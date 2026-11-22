"""AOCL Logical Simulation Engine (AOCL-CR-011).

A deterministic, stdlib-only interpreter that executes a BehavioralSpecification
(CR-006) under a SimulationScenario (CR-009) through an ExecutionDefinition
(CR-010), per the engine-conformance rules LSE-001..022 of AOCL-CR-011.

Conformance-gated: the engine refuses to run any bound artifact that fails its
native validator (LSE-002) and verifies the execution definition's logical
readiness (LSE-003). It executes the LOGICAL dimension — graph-faithful
activation, channel-routed condition evaluation, event scheduling, the dispatch
chain, approval suspension, exception resolution, safe states — and declares
minimal numeric semantics (CR-011 §7), explicitly non-normative pending the
state-based engine's quantitative fidelity (LSE-018).

The load-bearing rule is runtime visibility enforcement (EXE-036/LSE-006):
condition evaluation contexts route to a channel; controller-facing contexts
resolve on the observed view only. A disturbance declared unknown to the
Controller never reaches the observed channel until an observation copies it —
the simulated Controller never reads the scenario's hidden ground truth.
"""

from __future__ import annotations

import json
import math
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("error: pyyaml is required for the logical engine (pip install pyyaml)")

try:
    from .behavior_spec import validate_behavioral_spec
    from .scenario import validate_scenario_library
    from .execution import validate_execution_definition
    from .control_contract import validate_control_model
    from .evidence_model import validate_evidence_model
except ImportError:  # direct-script execution: fall back to the package path
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from aocl.behavior_spec import validate_behavioral_spec
    from aocl.scenario import validate_scenario_library
    from aocl.execution import validate_execution_definition
    from aocl.control_contract import validate_control_model
    from aocl.evidence_model import validate_evidence_model

RULESET_VERSION = "1.0.0"
ENGINE_VERSION = "0.1.0"

TRACE_CLASSES = ("Activation", "ConditionEvaluation", "TransitionEvaluation", "Dispatch",
                 "ApprovalResolution", "ExceptionDisposition", "SafeStateTransition")
CHAIN = ("Command", "Acknowledgement", "ExecutionStatus", "Effect", "Outcome")
DEFAULT_ACTIVATION_BOUND = 8
DEFAULT_MAX_TICKS = 100
DEFAULT_APPROVAL_WINDOW_TICKS = 3

_SECONDS = re.compile(r"(\d+(?:\.\d+)?)\s*s", re.I)
_ISO = re.compile(r"^PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+(?:\.\d+)?)S)?$", re.I)


class EngineError(Exception):
    pass


def _load(path) -> dict:
    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _tick_seconds(basis: dict) -> float:
    m = _SECONDS.search(str((basis or {}).get("tickUnit", "")))
    return float(m.group(1)) if m else 1.0


def _iso_seconds(text: str):
    m = _ISO.match(str(text).strip())
    if not m:
        return None
    h, mi, s = (float(x) if x else 0.0 for x in m.groups())
    return h * 3600 + mi * 60 + s


class LCG:
    """Deterministic seeded source (same construction as the site engine)."""

    def __init__(self, seed: int):
        self.state = seed & 0xFFFFFFFF or 1

    def next_u32(self) -> int:
        x = self.state
        x ^= (x << 13) & 0xFFFFFFFF
        x ^= x >> 17
        x ^= (x << 5) & 0xFFFFFFFF
        self.state = x
        return x


def _route_channel(cond: dict) -> str:
    """EXE-036/LSE-007: route the evaluation channel from the declared context.
    Default is controller-facing (observed) — conservative by design."""
    ctx = str(cond.get("evaluationContext", "")).lower()
    if "ground truth" in ctx or "actual" in ctx:
        return "actual"
    if "estimate" in ctx or "estimator" in ctx:
        return "estimated"
    return "observed"


def _num(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _operators_ok(op: str, a: float, b: float):
    return {
        "lessThan": a < b, "lessThanOrEqual": a <= b,
        "greaterThan": a > b, "greaterThanOrEqual": a >= b,
        "equals": a == b, "present": True,
    }.get(op)


class LogicalEngine:
    def __init__(self, execution: dict, spec: dict, scenario_doc: dict,
                 control: dict | None = None, evidence: dict | None = None,
                 seed: int = 2026, run_inputs: dict | None = None):
        self.exec_doc, self.spec_doc, self.scen_doc = execution, spec, scenario_doc
        self.control_doc, self.evidence_doc = control, evidence
        self.seed, self.run_inputs = seed, dict(run_inputs or {})
        self.ex = execution["executionDefinition"]
        self.spec = spec["behavioralSpecification"]
        self.findings: list[str] = []
        self.trace: list[dict] = []
        self.rng = LCG(seed)

    # ---------------- gating (LSE-002/003)

    def gate(self) -> None:
        problems = []
        checks = [(validate_execution_definition(self.exec_doc), "execution definition")]
        if self.control_doc:
            checks.append((validate_control_model(self.control_doc), "control model"))
        if self.evidence_doc:
            checks.append((validate_evidence_model(self.evidence_doc), "evidence model"))
        for result, name in checks:
            if not result["valid"]:
                problems.append(f"{name}: " + "; ".join(f"{f['rule']}: {f['message']}"[:160]
                                                        for f in result["findings"] if f["severity"] == "error"))
        spec_result = validate_behavioral_spec(self.spec_doc)
        if not spec_result["conformance"]["behaviorallyConformant"]:
            problems.append("behavioral specification: not behaviorally conformant — "
                            + "; ".join(f"{f['rule']}: {f['message']}"[:160]
                                        for f in spec_result["findings"] if f["severity"] == "error"))
        lib_result = validate_scenario_library(self.scen_doc)
        if not lib_result["valid"]:
            problems.append("scenario library: " + "; ".join(f"{f['rule']}: {f['message']}"[:160]
                                                             for f in lib_result["findings"] if f["severity"] == "error"))
        if problems:
            raise EngineError("conformance gate failed (LSE-002):\n  - " + "\n  - ".join(problems))
        if not spec_result["conformance"].get("simulationReady", False) and \
                not self.spec.get("controlContractBindings"):
            self.findings.append("behavioral specification declares no controlContractBindings — "
                                 "contracts are matched by reference only (BSS-036 readiness not claimed)")
        if self.ex["executionMode"] not in ("Logical", "Hybrid"):
            raise EngineError(f"mode {self.ex['executionMode']} is not a logical mode (LSE-003)")
        # re-derive readiness from the validator's own flags
        fresh = validate_execution_definition(self.exec_doc)
        if not fresh["conformance"]["logicalEngineReady"]:
            raise EngineError("execution definition is not logical-engine ready (LSE-003): "
                              + "; ".join(fresh.get("engineReadinessReasons", [])))
        scenario_id = self.ex.get("scenarioId")
        scenarios = self.scen_doc["scenarioLibrary"]["scenarios"]
        self.scenario = next((s for s in scenarios if s["scenarioId"] == scenario_id), None)
        if self.scenario is None:
            if len(scenarios) == 1:
                self.scenario = scenarios[0]
            else:
                raise EngineError(f"scenarioId {scenario_id!r} not found in the bound library (LSE-002)")
        readiness = {r["scenarioId"]: r for r in lib_result["scenarioReadiness"]}
        if not readiness.get(self.scenario["scenarioId"], {}).get("logicalReady", False):
            raise EngineError(f"scenario {self.scenario['scenarioId']} is not logical-simulation ready (LSE-003)")

    # ---------------- setup

    def setup(self) -> None:
        # channels by state class (LSE-005)
        self.actual: dict = {}
        self.observed: dict = {}
        self.estimated: dict = {}
        self.params = {p["parameterId"]: p.get("value") for p in self.scenario.get("parameters", [])
                       if isinstance(p, dict)}
        self.param_names = {}
        for p in self.scenario.get("parameters", []):
            if isinstance(p, dict):
                self.param_names[p.get("name", "").lower()] = p.get("value")
        for st in self.scenario.get("initialConditions", {}).get("states", []):
            var = st.get("stateVariableRef")
            cls, val = st.get("stateClass"), st.get("value")
            if cls == "Actual":
                self.actual[var] = val
            elif cls == "Observed":
                self.observed[var] = val
            elif cls == "Estimated":
                self.estimated[var] = val
        for var, val in self.actual.items():
            self.observed.setdefault(var, val)  # observed defaults to t0 copy of actual
        self.goal_var, self.reference = self._goal_and_reference()

        # conditions by id; elements by id
        self.conditions = {c["conditionId"]: c for c in self.spec.get("conditions", []) if isinstance(c, dict)}
        self.elements = {e["id"]: e for e in self.spec.get("elements", []) if isinstance(e, dict)}
        self.relationships = sorted([r for r in self.spec.get("relationships", []) if isinstance(r, dict)],
                                    key=lambda r: r.get("relationshipId", ""))
        # control model references (authority ids, contracts by behavioral element)
        self.authority_ids = set()
        self.contract_for_element: dict = {}
        if self.control_doc:
            cm = self.control_doc["controlModel"]
            self.authority_ids = {a.get("authorityId") for a in cm.get("authority", []) if isinstance(a, dict)}
            for c in cm.get("contracts", []):
                for ber in c.get("behavioralElementRefs", []) or []:
                    element = str(ber).split("#")[-1]
                    self.contract_for_element[element] = c
        # scenario events schedule (LSE time semantics)
        self.tick_s = _tick_seconds(self.ex.get("timeBasis"))
        self.scheduled: list[tuple[int, str, dict]] = []
        natural: dict = {}
        for ev in self.scenario.get("events", []):
            if not isinstance(ev, dict):
                continue
            trig = ev.get("trigger") or {}
            basis, at = trig.get("basis"), trig.get("at")
            tick = None
            if basis == "RelativeTime":
                secs = _num(at)
                if secs is None:
                    m = _SECONDS.search(str(at))
                    secs = float(m.group(1)) if m else 0.0
                tick = int(math.ceil(secs / self.tick_s)) if secs else 0
            elif basis == "AbsoluteTime":
                tick = int(_num(at) or 0)
            elif basis == "Periodic":
                every = trig.get("every")
                self.scheduled.append((0, ev["eventId"], {**ev, "_periodic": _num(every)}))
                continue
            if tick is None:
                self.findings.append(f"scenario event {ev.get('eventId')}: basis {basis!r} has no computed tick "
                                     "in the reference interpretation — tied to its dependency")
                natural[ev["eventId"]] = None
            else:
                natural[ev["eventId"]] = tick
        for ev in self.scenario.get("events", []):
            if not isinstance(ev, dict) or "_periodic" in ev:
                continue
            tick = natural.get(ev["eventId"])
            if tick is None:
                continue  # dependency-tied events are handled when their dependency fires
            dep = (ev.get("trigger") or {}).get("afterEventRef") or (ev.get("dependsOnRefs") or [None])[0]
            if dep and dep in natural and natural[dep] is not None:
                tick = max(tick, natural[dep] + 1)
            self.scheduled.append((tick, ev["eventId"], ev))
        self.scheduled.sort(key=lambda x: (x[0], x[1]))
        # fired disturbances with pre-values (remediation revert semantics)
        self.disturbance_schedule: list[tuple[int, dict]] = []
        for d in self.scenario.get("disturbances", []):
            onset = d.get("onset") or {}
            secs = _num(onset.get("at"))
            if onset.get("basis") in ("RelativeTime", "AbsoluteTime") and secs is not None:
                self.disturbance_schedule.append((int(math.ceil(secs / self.tick_s)) if secs else 0, d))
            elif onset.get("basis") == "Periodic":
                self.disturbance_schedule.append((0, {**d, "_periodic": _num((onset or {}).get("every"))}))
        self.disturbance_schedule.sort(key=lambda x: (x[0], x[1].get("disturbanceId", "")))
        self.fired: dict = {}     # var -> pre-disturbance actual value
        self.fired_active: set = set()
        # approvals from declared run inputs (LSE-021)
        self.approvals = {k: dict(v) for k, v in (self.run_inputs.get("approvals") or {}).items()}
        self.failures = set(self.run_inputs.get("failures") or [])
        self.max_ticks = int(self.run_inputs.get("max_ticks")
                             or self._horizon_param() or DEFAULT_MAX_TICKS)
        self.activation_bound = int(self.run_inputs.get("activation_bound") or DEFAULT_ACTIVATION_BOUND)
        self.activations: dict = {}
        self.pending_approval: dict | None = None
        self.verification_succeeded = False
        self.deviation_detected = False
        self.terminated: dict | None = None

    def _horizon_param(self):
        for name, val in self.param_names.items():
            if "horizon" in name:
                return _num(val)
        return None

    def _goal_and_reference(self):
        """Goal variable + reference value: control model's Controlled variable;
        reference from a scenario target parameter or a Reference-role variable."""
        goal_var, reference = None, None
        if self.control_doc:
            cm = self.control_doc["controlModel"]
            for v in cm.get("controlVariables", []):
                if isinstance(v, dict) and "Controlled" in (v.get("roles") or []):
                    goal_var = v["variableId"]
                if isinstance(v, dict) and "Reference" in (v.get("roles") or []) and v.get("value") is not None:
                    reference = v.get("value")
        for name, val in self.param_names.items():
            if reference is None and ("target" in name or "reference" in name):
                reference = _num(val)
        if goal_var is None:
            # no control model bound: fall back to the scenario's tracked variables
            state_vars = [st.get("stateVariableRef") for st in self.scenario.get("initialConditions", {}).get("states", [])
                          if isinstance(st, dict) and st.get("stateVariableRef")]
            if state_vars:
                goal_var = state_vars[0]
        return goal_var, reference

    # ---------------- trace helpers

    def _record(self, cls: str, t: int, ref: str, detail: str, **extra) -> None:
        rec = {"class": cls, "t": t, "ref": ref, "detail": detail}
        rec.update(extra)
        self.trace.append(rec)

    # ---------------- condition evaluation (LSE-007)

    def eval_condition(self, cond_id: str, t: int) -> bool | None:
        cond = self.conditions.get(cond_id)
        if cond is None:
            self._record("ConditionEvaluation", t, cond_id, "condition not declared — unresolved", outcome="Unresolved")
            return None
        channel = _route_channel(cond)
        subject = str(cond.get("subject", ""))
        var = subject.split(".")[0].strip()
        op = cond.get("operator")
        val_ref = cond.get("valueRef")
        value = {"actual": self.actual, "observed": self.observed, "estimated": self.estimated}[channel].get(var)
        if value is None and isinstance(val_ref, str) and val_ref in self.params:
            # subject names a parameter domain, not a channel variable
            value = self.params[val_ref]
            val_ref = None
        target = _num(val_ref) if val_ref is not None else None
        if target is None and isinstance(val_ref, str):
            target = _num(self.params.get(val_ref, _num(self.param_names.get(val_ref.lower()))))
        a, b = _num(value), _num(target)
        if a is None or b is None or _operators_ok(op, 0, 1) is None:
            self._record("ConditionEvaluation", t, cond_id,
                         f"unresolved: subject {subject!r} on channel {channel} is not numerically evaluable "
                         "(recorded, never defaulted — LSE-007)", outcome="Unresolved", channel=channel)
            return None
        outcome = bool(_operators_ok(op, a, b))
        if channel == "observed" and var == self.goal_var:
            goal_ref = _num(self.reference)
            if goal_ref is not None and a > goal_ref:
                self.deviation_detected = True
        self._record("ConditionEvaluation", t, cond_id,
                     f"{subject} {op} {target} on {channel}: {a} → {outcome}",
                     outcome="Satisfied" if outcome else "NotSatisfied", channel=channel)
        return outcome

    # ---------------- events (LSE time/visibility semantics)

    def _apply_disturbance(self, d: dict, t: int) -> None:
        var = (d.get("effect") or {}).get("variableRef")
        mag, unit = _num(d.get("magnitude")), str(d.get("magnitudeUnit", "")).lower()
        if var is None or mag is None:
            self.findings.append(f"disturbance {d.get('disturbanceId')}: not applied — effect/magnitude not numeric")
            return
        if var not in self.fired:
            self.fired[var] = self.actual.get(var)
        cur = _num(self.actual.get(var)) or 0.0
        if "percent" in unit:
            self.actual[var] = cur * (1 + mag / 100.0)
        else:
            self.actual[var] = cur + mag
        self.fired_active.add(var)
        known = d.get("knownToController")
        if known is True:
            self.observed[var] = self.actual[var]  # controller-known disturbance is visible immediately
        self._record("TransitionEvaluation", t, d.get("disturbanceId", "?"),
                     f"disturbance applied to {var} (actual → {self.actual[var]}); "
                     f"controller-visible: {'yes' if known else 'NO — hidden until observed (EXE-036)'}",
                     outcome="Applied")

    def _observe(self, t: int, source: str) -> None:
        for var in self.actual:
            self.observed[var] = self.actual[var]
        self._record("TransitionEvaluation", t, source, "observation: actual → controller-visible view copied",
                     outcome="Observed")

    # ---------------- activation (LSE-008)

    def _entry_elements(self) -> list[str]:
        # Progression edges (FlowsTo/BranchesTo/Triggers/Invokes) disqualify a target from entry;
        # RepeatsTo/ReturnsTo targets are loop heads and remain legitimate entries.
        targets = {r.get("target") for r in self.relationships
                   if r.get("type") in ("FlowsTo", "BranchesTo", "Triggers", "Invokes")}
        entries = [eid for eid, e in sorted(self.elements.items())
                   if eid not in targets and "Observe" in (e.get("stages") or [])]
        if not entries:
            entries = sorted(self.elements)
        return entries

    def _outgoing(self, eid: str, rtype: str) -> list[dict]:
        return [r for r in self.relationships if r.get("source") == eid and r.get("type") == rtype]

    def activate(self, eid: str, t: int, cause: str) -> None:
        if self.terminated:
            return
        if self.pending_approval:
            self.findings.append(f"element {eid}: activation blocked — approval gate open "
                                 f"({self.pending_approval['element']}); the path is suspended")
            return
        if self.activations.get(eid, 0) >= self.activation_bound:
            self.findings.append(f"element {eid}: activation bound reached — not re-activated (LSE-017)")
            return
        self.activations[eid] = self.activations.get(eid, 0) + 1
        el = self.elements.get(eid, {})
        self._record("Activation", t, eid, f"activated ({cause}); type={el.get('type')}, stages={el.get('stages')}")
        etype = el.get("type")

        # Verification: the independent probe reports the plant (VER-036 independence), then evaluates
        if etype == "Verification":
            self._observe(t, eid + ":independent-probe")
            self._verify(t, eid)
        # Approval suspension (LSE-009)
        if etype == "Approval":
            self._suspend_for_approval(eid, t)
            return
        # Action dispatch (LSE-010); a Failed execution does not progress its success path —
        # the declared exception path owns continuation (P32/EXE-030)
        if etype == "Action":
            if self._dispatch(eid, t):
                return

        # conditional branches first (Pattern B): the decision point evaluates its alternatives;
        # an unsatisfied branch falls through to the default progression
        for rel in self._outgoing(eid, "BranchesTo"):
            cref = rel.get("conditionRef")
            result = self.eval_condition(cref, t) if cref else None
            if result is True:
                self.activate(rel["target"], t, f"BranchesTo {rel.get('relationshipId')} satisfied")
                return
        # progress along FlowsTo (Synchronization targets gate on their declared pattern)
        for rel in self._outgoing(eid, "FlowsTo"):
            target = rel["target"]
            if not self._sync_ready(target):
                self._record("TransitionEvaluation", t, target,
                             f"synchronization {target}: waiting for parallel inputs (WaitForAll)",
                             outcome="Waiting")
                continue
            self.activate(target, t, f"FlowsTo {rel.get('relationshipId')}")
            if self.terminated or self.pending_approval:
                return
        # escalation progression (exception paths)
        for rel in self._outgoing(eid, "EscalatesTo"):
            self.activate(rel["target"], t, f"EscalatesTo {rel.get('relationshipId')}")
            if self.terminated or self.pending_approval:
                return
        # repetition (guarded)
        for rel in self._outgoing(eid, "RepeatsTo") + self._outgoing(eid, "ReturnsTo"):
            cref = rel.get("conditionRef")
            result = self.eval_condition(cref, t) if cref else False
            if result is True:
                self.activate(rel["target"], t, f"{rel.get('type')} {rel.get('relationshipId')}")
                return
        # termination edges
        for rel in self._outgoing(eid, "TerminatesWith"):
            outcome = rel.get("terminationOutcome", "ControlledTermination")
            target = rel.get("target")
            if target and target in self.elements:
                self.activate(target, t, f"TerminatesWith {rel.get('relationshipId')}")
            self._terminate(t, outcome, f"via {rel.get('relationshipId')}")

    def _sync_ready(self, target: str) -> bool:
        el = self.elements.get(target, {})
        if el.get("type") != "Synchronization" or el.get("syncPattern") != "WaitForAll":
            return True
        sources = {r["source"] for r in self.relationships
                   if r.get("target") == target and r.get("type") == "FlowsTo"}
        return all(self.activations.get(src, 0) > 0 for src in sources) or not sources

    def _dispatch(self, eid: str, t: int) -> bool:
        contract = self.contract_for_element.get(eid, {})
        failed = eid in self.failures
        chain_detail = {
            "Command": f"command issued to {contract.get('subjectRef', 'actuator')}",
            "Acknowledgement": "acknowledgement received (Receipt — NOT execution)",
            "ExecutionStatus": "execution reported complete" if not failed else "execution reported FAILED",
            "Effect": self._effect_detail(eid, t),
            "Outcome": "action outcome recorded (distinct from execution status)",
        }
        for stage in CHAIN:
            outcome = "Failed" if (failed and stage == "ExecutionStatus") else \
                      ("Applied" if stage == "Effect" and not failed else
                       ("Recorded" if stage != "Effect" else "NotApplied"))
            if failed and stage in ("Effect", "Outcome"):
                outcome = "NotApplied"
            self._record("Dispatch", t, eid, f"{stage}: {chain_detail[stage]}", outcome=outcome)
        # authority check (EXE-016)
        auth = (contract.get("authorization") or {}).get("authorityRef")
        self._record("TransitionEvaluation", t, eid,
                     f"authority {auth!r} checked against declared AuthorityDefinition: "
                     f"{'valid' if auth in self.authority_ids else 'NOT DECLARED'}",
                     outcome="Valid" if auth in self.authority_ids else "Invalid")
        if failed:
            self._handle_exception(eid, t, "ExecutionFailure")
        elif self.fired_active:
            # remediation restores pre-disturbance values (CR-011 §7.7, LSE-018)
            for var, pre in self.fired.items():
                if var in self.fired_active:
                    self.actual[var] = pre
                    self.fired_active.discard(var)
            self._record("TransitionEvaluation", t, eid,
                         "remediation effect: disturbed variables restored to pre-disturbance actual values "
                         "(declared logical-mode interpretation, LSE-018)", outcome="Restored")
        return failed

    def _effect_detail(self, eid: str, t: int) -> str:
        contract = self.contract_for_element.get(eid, {})
        effects = contract.get("expectedEffects") or []
        if effects:
            e0 = effects[0]
            return f"declared effect on {e0.get('variableRef')}: {e0.get('expectedChange')}"
        return "no control contract bound — effect recorded without declared delta"

    def _handle_exception(self, eid: str, t: int, category: str) -> None:
        handlers = self._outgoing(eid, "HandlesException")
        unhandled = (self.ex.get("exceptionHandling") or {}).get("unhandledPolicy", "Escalate")
        if not handlers:
            self._record("ExceptionDisposition", t, eid,
                         f"{category} unhandled — policy {unhandled}", outcome=unhandled)
            if unhandled == "Escalate":
                self._terminate(t, "Failed", f"unhandled {category}")
            return
        for rel in handlers:
            self._record("ExceptionDisposition", t, eid,
                         f"{category} → handler {rel['target']} ({rel.get('relationshipId')})",
                         outcome="Handled")
            self.activate(rel["target"], t, f"HandlesException {rel.get('relationshipId')}")

    def _suspend_for_approval(self, eid: str, t: int) -> None:
        window = self._approval_window(eid)
        self.pending_approval = {"element": eid, "since": t, "timeout": t + window}
        self._record("ApprovalResolution", t, eid,
                     f"suspended into WaitingApproval (declared window {window} ticks)",
                     outcome="WaitingApproval")

    def _approval_window(self, eid: str) -> int:
        for pref in self.elements.get(eid, {}).get("participationRefs", []) or []:
            for h in self.spec.get("humanParticipation", []):
                if isinstance(h, dict) and h.get("participationId") == pref:
                    cond = self.conditions.get(h.get("timeoutConditionRef") or "", {})
                    secs = _iso_seconds(cond.get("valueRef"))
                    if secs is not None:
                        return max(1, int(math.ceil(secs / self.tick_s)))
        return DEFAULT_APPROVAL_WINDOW_TICKS

    def _resolve_approval(self, resolution: str, t: int, source: str) -> None:
        eid = self.pending_approval["element"]
        self._record("ApprovalResolution", t, eid, f"{resolution} ({source})", outcome=resolution)
        self.pending_approval = None  # gate open for the resolution's own activations
        if resolution == "granted":
            branches = [r for r in self._outgoing(eid, "BranchesTo")
                        if (self.conditions.get(r.get("conditionRef"), {}) or {}).get("category") == "Authorization"]
            if branches:
                self.activate(branches[0]["target"], t, f"approval grant → {branches[0]['conditionRef']}")
                return
            flows = self._outgoing(eid, "FlowsTo")
            if flows:
                self.activate(flows[0]["target"], t, "approval grant → resumed path")
                return
            self.findings.append(f"approval {eid}: grant resolved but no authorization branch or progression")
        else:
            target = self._escalation_target(eid)
            if target:
                self.activate(target, t, f"approval {resolution} → escalation")
            else:
                self._terminate(t, "Failed", f"approval {resolution} without escalation path")

    def _escalation_target(self, eid: str):
        escalations = self._outgoing(eid, "EscalatesTo")
        if escalations:
            return escalations[0]["target"]
        for exc in self.spec.get("exceptions", []):
            if isinstance(exc, dict) and exc.get("affectedElementRef") == eid \
                    and exc.get("recoveryOrEscalation") in ("Escalation", "SafeState"):
                return exc.get("pathRef")
        return None

    def _verify(self, t: int, eid: str) -> None:
        """LSE verification semantics: goal variable's observed value vs declared reference."""
        if self.reference is None or self.goal_var is None:
            self._record("ConditionEvaluation", t, eid,
                         "verification unresolved: no goal variable/reference derivable", outcome="Unresolved")
            return
        value = _num(self.observed.get(self.goal_var))
        ok = value is not None and value < float(self.reference)
        self.verification_succeeded = self.verification_succeeded or ok
        self._record("ConditionEvaluation", t, eid,
                     f"verification: observed {self.goal_var}={value} vs reference {self.reference} → "
                     f"{'achieved' if ok else 'not achieved'} (evaluated-by-reference; textual conditions "
                     "recorded separately)", outcome="Achieved" if ok else "NotAchieved")

    def _terminate(self, t: int, outcome: str, why: str) -> None:
        if self.terminated:
            return
        if outcome == "SafeStateTransition":
            self._record("SafeStateTransition", t, why, "safe state entered — verification status recorded, "
                         "never implicit (LSE-012)", outcome="EnteredVerificationPending")
        self.terminated = {"t": t, "outcome": outcome, "why": why}

    # ---------------- main loop (deterministic; LSE-014)

    def run(self) -> dict:
        self.gate()
        self.setup()
        run_id = f"run-{self.scenario['scenarioId']}-seed{self.seed}"
        self._record("Activation", 0, "<run>",
                     f"execution {self.ex['id']} v{self.ex['version']}; mode {self.ex['executionMode']}; "
                     f"scenario {self.scenario['scenarioId']}; seed {self.seed}; runId {run_id}")
        queue = list(self._entry_elements())
        scheduled = list(self.scheduled)
        disturbances = list(self.disturbance_schedule)
        periodic_events = [s for s in scheduled if "_periodic" in s[2]]
        for _, _, ev in periodic_events:
            pass  # periodic events beyond t0 are recorded once at t0 in the reference interpretation
        for eid in queue:
            self.activate(eid, 0, "declared entry")
        tick = 0
        while not self.terminated and tick <= self.max_ticks:
            mark = len(self.trace)
            # scheduled events + disturbances fire before the tick's activations
            due_events = [s for s in scheduled if s[0] == tick]
            for _, ev_id, ev in due_events:
                self._record("Activation", tick, ev_id, f"scenario event {ev.get('eventType')} fired")
                if ev.get("eventType") == "ObservationReceived":
                    self._observe(tick, ev_id)
            scheduled = [s for s in scheduled if s[0] > tick]
            due_dist = [d for d in disturbances if d[0] == tick]
            for _, d in due_dist:
                self._apply_disturbance(d, tick)
            disturbances = [d for d in disturbances if d[0] > tick]
            # approval timeout / declared grant
            if self.pending_approval:
                pa = self.pending_approval
                declared = self.approvals.get(pa["element"])
                if declared and _num(declared.get("atTick")) == tick:
                    self._resolve_approval(str(declared.get("resolution", "granted")), tick, "declared run input")
                elif tick >= pa["timeout"]:
                    self._record("ExceptionDisposition", tick, pa["element"],
                                 "approval timeout — escalating per declared participation timeout",
                                 outcome="Timeout")
                    self.pending_approval = None  # the gate opens for the escalation itself
                    target = self._escalation_target(pa["element"])
                    if target:
                        self._record("ExceptionDisposition", tick, pa["element"],
                                     f"timeout → {target}", outcome="Escalated")
                        self.activate(target, tick, "approval timeout escalation")
                    else:
                        self._terminate(tick, "Failed", "approval timeout without escalation path")
            # idle break: nothing happened this tick, nothing scheduled, no gate open (declared bounds)
            if (len(self.trace) == mark and not scheduled and not disturbances
                    and not self.pending_approval):
                break
            tick += 1
        if not self.terminated:
            if self.verification_succeeded:
                self.terminated = {"t": tick - 1, "outcome": "VerifiedCompletion",
                                   "why": "declared verification succeeded (LSE-013)"}
            else:
                self.terminated = {"t": self.max_ticks, "outcome": "Terminated",
                                   "why": "maximum tick bound reached without declared verification success "
                                          "(declared bounds, LSE-013/017)"}
        return self._summary(run_id)

    def _summary(self, run_id: str) -> dict:
        activated = set(self.activations)
        unactivated = sorted(set(self.elements) - activated)
        if unactivated:
            self.findings.append(f"elements not activated: {unactivated}")
        unevaluated = sum(1 for r in self.trace if r["class"] == "ConditionEvaluation"
                          and r.get("outcome") == "Unresolved")
        targets = []
        for vt in self.scenario.get("verificationTargets", []):
            achieved = self.verification_succeeded and "outcome" in vt.get("targetId", "").lower()
            targets.append({"targetId": vt.get("targetId"), "claimRef": vt.get("claimRef"),
                            "evaluation": "Achieved" if achieved else
                            ("Detected" if vt.get("targetId", "").startswith("vt-detection") and self.deviation_detected
                             else "NotEvaluated")})
        counts = {c: sum(1 for r in self.trace if r["class"] == c) for c in TRACE_CLASSES}
        records_valid = all(isinstance(r.get("t"), int) and r.get("class") in TRACE_CLASSES
                             and str(r.get("ref", "")).strip() for r in self.trace)
        evidence = {
            "evidenceId": f"E-{run_id}", "evidenceType": "SimulationEvidence",
            "name": f"Logical run {run_id}",
            "sourceRef": f"aocl-engine-logical@{ENGINE_VERSION}",
            "subjectRef": self.ex.get("controlModelRef"),
            "originClass": "SimulationTime",
            "simulationRun": {"runId": run_id, "scenarioRef": self.scenario["scenarioId"],
                               "seed": self.seed, "engineVersion": ENGINE_VERSION,
                               "behavioralSpecVersion": self.ex.get("specVersion"),
                               "controlContractVersion": "bound-by-reference"},
        }
        if self.terminated["outcome"] == "SafeStateTransition":
            self.findings.append("safe state entered; its declared verification did not run — "
                                 "verification status is pending, never implicit (LSE-012)")
        return {
            "runId": run_id,
            "rulesetVersion": RULESET_VERSION, "engineVersion": ENGINE_VERSION,
            "executionRef": self.ex["id"], "executionMode": self.ex["executionMode"],
            "scenarioRef": self.ex.get("scenarioRef"), "scenarioId": self.scenario["scenarioId"],
            "seed": self.seed,
            "runInputs": {"approvals": self.approvals, "failures": sorted(self.failures)},
            "ticks": self.terminated["t"], "terminationOutcome": self.terminated["outcome"],
            "terminationWhy": self.terminated["why"],
            "verificationSucceeded": self.verification_succeeded,
            "deviationDetected": self.deviation_detected,
            "verificationTargets": targets,
            "traceCounts": counts, "traceRecordsValid": records_valid,
            "channels": {"actual": self.actual, "observed": self.observed, "estimated": self.estimated},
            "evidence": evidence,
            "findings": self.findings,
        }


def run_from_paths(exec_path, spec_path, scenario_path, control_path=None, evidence_path=None,
                   seed=2026, run_inputs=None) -> dict:
    execution = _load(exec_path)
    spec = _load(spec_path)
    scenario_doc = _load(scenario_path)
    control = _load(control_path) if control_path else None
    evidence = _load(evidence_path) if evidence_path else None
    engine = LogicalEngine(execution, spec, scenario_doc, control, evidence, seed=seed,
                           run_inputs=run_inputs)
    return engine.run()


def render_summary(summary: dict) -> str:
    lines = [f"AOCL logical run — {summary['runId']}"]
    lines.append(f"execution {summary['executionRef']} ({summary['executionMode']}) · scenario {summary['scenarioId']} · "
                 f"seed {summary['seed']} · ticks {summary['ticks']}")
    lines.append(f"termination: {summary['terminationOutcome']} — {summary['terminationWhy']}")
    lines.append(f"verification: {'achieved' if summary['verificationSucceeded'] else 'not achieved'} · "
                 f"deviation detected: {summary['deviationDetected']}")
    lines.append("trace: " + " · ".join(f"{k}={v}" for k, v in summary["traceCounts"].items()))
    for vt in summary.get("verificationTargets", []):
        lines.append(f"  target {vt['targetId']}: {vt['evaluation']}")
    for f in summary.get("findings", []):
        lines.append(f"  finding: {f}")
    return "\n".join(lines)


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--self-test" in argv:
        return _self_test()
    as_json = "--json" in argv
    argv = [a for a in argv if a != "--json"]
    if not argv or argv[0] != "run":
        print("usage: aocl-engine-logical run <execution.yaml> --spec <spec.yaml> --scenarios <library.yaml> "
              "[--control <yaml>] [--evidence <yaml>] [--scenario-id ID] [--seed N] "
              "[--approve element=resolution@tick] [--fail element] [--json] | --self-test")
        return 2
    args, run_inputs = argv[1:], {"approvals": {}, "failures": []}
    opts = {}
    i = 0
    while i < len(args):
        a = args[i]
        if a == "--spec":
            opts["spec"] = args[i + 1]; i += 2
        elif a == "--scenarios":
            opts["scenarios"] = args[i + 1]; i += 2
        elif a == "--control":
            opts["control"] = args[i + 1]; i += 2
        elif a == "--evidence":
            opts["evidence"] = args[i + 1]; i += 2
        elif a == "--scenario-id":
            opts["scenario_id"] = args[i + 1]; i += 2
        elif a == "--seed":
            opts["seed"] = int(args[i + 1]); i += 2
        elif a == "--approve":
            element, rest = args[i + 1].split("=", 1)
            resolution, at = rest.split("@", 1)
            run_inputs["approvals"][element] = {"resolution": resolution, "atTick": int(at)}
            i += 2
        elif a == "--fail":
            run_inputs["failures"].append(args[i + 1]); i += 2
        elif a == "--max-ticks":
            run_inputs["max_ticks"] = int(args[i + 1]); i += 2
        else:
            i += 1
    if "spec" not in opts or "scenarios" not in opts:
        print("error: --spec and --scenarios are required")
        return 2
    execution = _load(args[0])
    if opts.get("scenario_id"):
        execution = json.loads(json.dumps(execution))
        execution["executionDefinition"]["scenarioId"] = opts["scenario_id"]
    try:
        summary = LogicalEngine(execution, _load(opts["spec"]), _load(opts["scenarios"]),
                                _load(opts["control"]) if opts.get("control") else None,
                                _load(opts["evidence"]) if opts.get("evidence") else None,
                                seed=opts.get("seed", 2026), run_inputs=run_inputs).run()
    except EngineError as exc:
        print(f"error: {exc}")
        return 1
    print(json.dumps(summary, indent=2, default=str) if as_json else render_summary(summary))
    return 0


def _self_test() -> int:
    import copy

    # ---------- synthetic specification exercising the machinery
    def element(eid, etype, stages, **kw):
        return {"id": eid, "type": etype, "name": eid, "stages": stages, **kw}

    spec = {
        "schemaVersion": "0.1", "specVersion": "1.0.0",
        "behavioralSpecification": {
            "id": "urn:aocl:spec:synth-001", "type": "BehavioralSpecification",
            "name": "Synthetic", "definition": "Engine self-test specification.",
            "lifecycleStatus": "Draft",
            "closedLoopRef": {"loopId": "urn:aocl:loop:synth-001", "sourceSystem": "test"},
            "objectives": [{"objectiveId": "obj-1", "goalRef": "g1", "description": "d"}],
            "stageCoverage": [{"stage": s, "status": "Realized"}
                              for s in ("Intent", "Observe", "Analyze", "Decide", "Execute", "Verify", "Learn")],
            "entry": {"conditions": ["c-monitor"]},
            "termination": {"outcomes": ["VerifiedCompletion", "SafeStateTransition"]},
            "elements": [
                element("obs", "Observation", ["Observe"], outputs=["sig-o"],
                        controlArchitectureRef={"sensorRef": "sensor-1"}),
                element("analyze", "Analysis", ["Analyze"], inputs=["sig-o"], outputs=["sig-a"]),
                element("decide", "Decision", ["Decide"], inputs=["sig-a"], outputs=["sig-d"],
                        conditionRefs=["c-hot", "c-cool"]),
                element("approve", "Approval", ["Decide", "Execute"], inputs=["sig-d"],
                        outputs=["sig-auth"], participationRefs=["hp-1"]),
                element("act", "Action", ["Execute"], inputs=["sig-auth"], outputs=["sig-r"],
                        controlArchitectureRef={"actuatorRef": "act-1"}),
                element("handler", "ExceptionHandler", ["Execute"], inputs=["sig-r"]),
                element("esc", "Escalation", ["Decide"], inputs=["sig-r"]),
                element("safe", "SafeState", ["Execute", "Verify"]),
                element("verify", "Verification", ["Verify"], inputs=["sig-r"], outputs=["sig-v"]),
                element("learn", "Learning", ["Learn"], inputs=["sig-v"]),
            ],
            "relationships": [
                {"relationshipId": "f1", "type": "FlowsTo", "source": "obs", "target": "analyze"},
                {"relationshipId": "f2", "type": "FlowsTo", "source": "analyze", "target": "decide"},
                {"relationshipId": "f3", "type": "FlowsTo", "source": "decide", "target": "approve"},
                {"relationshipId": "f4", "type": "FlowsTo", "source": "approve", "target": "act"},
                {"relationshipId": "b-hot", "type": "BranchesTo", "source": "decide", "target": "act",
                 "conditionRef": "c-hot"},
                {"relationshipId": "x1", "type": "HandlesException", "source": "act", "target": "handler"},
                {"relationshipId": "e1", "type": "EscalatesTo", "source": "handler", "target": "esc"},
                {"relationshipId": "t1", "type": "TerminatesWith", "source": "esc", "target": "safe",
                 "terminationOutcome": "SafeStateTransition"},
                {"relationshipId": "f5", "type": "FlowsTo", "source": "act", "target": "verify"},
                {"relationshipId": "f6", "type": "FlowsTo", "source": "verify", "target": "learn"},
                {"relationshipId": "rep1", "type": "RepeatsTo", "source": "learn", "target": "obs",
                 "conditionRef": "c-monitor"},
            ],
            "conditions": [
                {"conditionId": "c-hot", "category": "Threshold", "subject": "latency",
                 "operator": "greaterThan", "valueRef": 50,
                 "evaluationContext": "controller observation of the service"},
                {"conditionId": "c-cool", "category": "Threshold", "subject": "latency",
                 "operator": "lessThanOrEqual", "valueRef": 50,
                 "evaluationContext": "controller observation of the service"},
                {"conditionId": "c-monitor", "category": "Temporal", "subject": "monitoring cycle",
                 "evaluationContext": "scheduler"},
                {"conditionId": "c-timeout", "category": "Temporal", "subject": "approval age",
                 "operator": "greaterThan", "valueRef": "PT1M", "evaluationContext": "approval clock"},
            ],
            "informationDependencies": [{"informationId": "sig-o", "kind": "Required"},
                                          {"informationId": "sig-a", "kind": "Derived"},
                                          {"informationId": "sig-d", "kind": "Derived"},
                                          {"informationId": "sig-auth", "kind": "Conditional"},
                                          {"informationId": "sig-r", "kind": "Required"},
                                          {"informationId": "sig-v", "kind": "Derived"}],
            "policyRefs": [{"policyRefId": "p-auth", "targetRef": "auth-1", "relationship": "AuthorizedBy",
                            "appliesToRefs": ["act"], "resolved": True}],
            "humanParticipation": [{"participationId": "hp-1", "role": "Approver", "participationKind": "Approval",
                                     "stages": ["Decide"], "timeoutConditionRef": "c-timeout",
                                     "expectedResponse": "grant or reject"}],
            "exceptions": [{"exceptionId": "x-exec", "category": "ExecutionFailure", "affectedElementRef": "act",
                             "handlingResponsibility": "escalate", "pathRef": "handler",
                             "recoveryOrEscalation": "Escalation", "criticality": "Major"},
                            {"exceptionId": "x-approval", "category": "Timeout", "affectedElementRef": "approve",
                             "handlingResponsibility": "escalate on approval timeout", "pathRef": "esc",
                             "recoveryOrEscalation": "Escalation", "criticality": "Major"}],
            "safeStates": [{"safeStateId": "safe-1", "scopeRef": "plant",
                             "entryConditionRef": "c-monitor", "expectedOutcome": "controlled stop",
                             "responsibleAuthorityRef": "auth-1", "verificationRef": "v-1"}],
            "verificationRefs": [{"verificationId": "v-1", "elementRef": "verify", "independence": "Independent",
                                   "expectedOutcomeRef": "g1"}],
            "learningBoundaries": {"authorizationRequiredForPolicyChange": True,
                                    "authorizationPolicyRef": "p-auth"},
            "measurementAnchors": {
                "effort": {"humanParticipationRefs": ["hp-1"], "measure": "approvals"},
                "complexity": {"architectureRefs": ["act-1"], "dimensions": ["structural"]},
                "veracity": {"informationIds": ["sig-o"]}},
            "traceability": {},
            "governance": {"approvalRequired": True},
        },
    }

    def scenario_lib(init_actual, init_observed, sid="SCN-SYNTH-001"):
        return {
            "schemaVersion": "0.1", "modelVersion": "1.0.0",
            "scenarioLibrary": {
                "id": "urn:aocl:scenarios:synth", "type": "ScenarioLibrary",
                "name": "Synthetic", "definition": "Engine self-test scenarios.",
                "closedLoopRef": {"loopId": "urn:aocl:loop:synth-001", "sourceSystem": "test"},
                "contexts": [{"contextId": "ctx-1", "domain": "test"}],
                "scenarios": [{
                    "scenarioId": sid, "scenarioType": "Normal", "name": "Synthetic",
                    "definition": "Exercises activation, visibility, dispatch, approvals, exceptions.",
                    "version": "1.0.0", "lifecycleStatus": "Draft", "contextRef": "ctx-1",
                    "modelRefs": {"closedLoopRefs": ["urn:aocl:loop:synth-001"]},
                    "modelVersionRefs": ["test"],
                    "initialConditions": {"method": "Explicit", "states": [
                        {"initialStateId": "is-actual", "subjectRef": "plant", "stateVariableRef": "latency",
                         "value": init_actual, "valueType": "numeric", "unit": "ms", "stateClass": "Actual",
                         "initializationMethod": "Explicit"},
                        {"initialStateId": "is-observed", "subjectRef": "plant", "stateVariableRef": "latency",
                         "value": init_observed, "valueType": "numeric", "unit": "ms", "stateClass": "Observed",
                         "initializationMethod": "Explicit"},
                    ]},
                    "parameters": [{"parameterId": "p-target", "name": "latency target", "definition": "goal",
                                     "valueType": "numeric", "value": 50, "unit": "ms", "variationMode": "Fixed"}],
                    "disturbances": [{
                        "disturbanceId": "d-hidden", "disturbanceType": "Demand", "name": "hidden spike",
                        "definition": "hidden demand spike", "targetRefs": ["plant"], "magnitude": 10,
                        "magnitudeUnit": "ms", "onset": {"basis": "RelativeTime", "at": "60 s"},
                        "duration": "persistent", "profile": {"kind": "Step"},
                        "effect": {"variableRef": "latency", "effect": "raises latency"},
                        "knownToController": False,
                    }],
                    "events": [
                        {"eventId": "ev-start", "eventType": "ScenarioStart",
                         "trigger": {"basis": "RelativeTime", "at": "0 s"}, "subjectRef": "plant",
                         "ordering": "Independent"},
                        {"eventId": "ev-obs", "eventType": "ObservationReceived",
                         "trigger": {"basis": "RelativeTime", "at": "120 s"}, "subjectRef": "plant",
                         "ordering": "Ordered", "dependsOnRefs": ["ev-start"]},
                    ],
                    "assumptions": [{"assumptionId": "a-1", "description": "test", "basis": "test"}],
                    "verificationTargets": [{"targetId": "vt-outcome", "claimRef": "claim-1",
                                              "criterionRef": "crit-1", "conditions": "post-run"}],
                    "reproducibility": {"seed": 2026, "seedOrPolicyDeclared": True},
                    "compatibility": {"outcome": "Compatible", "modelBaselineRef": "test"},
                }],
            },
        }

    scenario_stale = scenario_lib(60, 40, "SCN-SYNTH-001")   # plant hot, controller sees stale 40
    scenario_clean = scenario_lib(40, 40, "SCN-SYNTH-002")   # plant healthy; hidden spike at t1

    execution = {
        "schemaVersion": "0.1", "modelVersion": "1.0.0",
        "executionDefinition": {
            "id": "urn:aocl:execution:synth-001", "type": "ExecutionDefinition",
            "name": "Synthetic", "definition": "Engine self-test execution.",
            "version": "1.0.0", "lifecycleStatus": "Draft", "executionMode": "Logical",
            "behavioralSpecRef": "urn:aocl:spec:synth-001", "specVersion": "1.0.0",
            "scenarioRef": "urn:aocl:scenarios:synth", "scenarioVersion": "1.0.0",
            "scenarioId": "SCN-SYNTH-001",
            "controlModelRef": "urn:aocl:control:synth-001",
            "evidenceModelRef": "urn:aocl:evidence:synth-001",
            "timeBasis": {"basis": "Tick", "tickUnit": "60 s test interval"},
            "activation": {"entryPolicy": "DeclaredEntry", "graphWalkOnly": True},
            "conditionEvaluation": {"contextPolicy": "DeclaredContext", "freshnessPolicy": "BlockOnStale"},
            "transitionEvaluation": {"guardOrder": "GuardsBeforeEffects", "authorityCheck": "AlwaysDeclared",
                                      "effectApplication": "DeclaredDeltas", "outcomeClassification": "Governed"},
            "eventHandling": {"orderingResolution": "PerScenarioDeclaration", "tieBreak": "DeclaredDeterministic",
                               "dependenciesBlock": True},
            "scheduling": {"cyclePolicy": "PerVelocityDeclaration"},
            "actionDispatch": {"chain": list(CHAIN), "distinctRecords": True, "resultClassification": "Governed",
                                "retryPolicy": {"permitted": False}},
            "humanParticipation": {"approvalGate": "Suspend", "timeoutPolicy": "c-timeout",
                                    "fallbackPolicy": "escalate"},
            "exceptionHandling": {"handlerResolution": "DeclaredPaths", "unhandledPolicy": "Escalate",
                                   "criticalUnresolvedBlock": True},
            "safeStateHandling": {"authorityRequired": True, "verificationRequired": True},
            "determinism": {"seedPolicy": "Declared", "sameInputsSameTrace": True},
            "informationVisibility": {"channelPolicy": "SeparatedChannels",
                                       "controllerVisiblePolicy": "PerScenarioDeclaration",
                                       "enforcement": "Runtime"},
            "trace": {"records": sorted(TRACE_CLASSES), "temporalRefs": True},
            "evidence": {"originClass": "SimulationTime", "runIdentity": "Declared"},
            "executionLifecycle": {"states": ["Initialized", "Ready", "Running", "WaitingApproval",
                                               "Terminated", "Failed"],
                                    "distinctFromModelLifecycle": True, "temporalRecording": True},
        },
    }

    # ---------- visibility proof (SCN-SYNTH-001, stale view): no grant → timeout → escalation
    eng = LogicalEngine(copy.deepcopy(execution), copy.deepcopy(spec), copy.deepcopy(scenario_stale), seed=7)
    summary = eng.run()
    assert summary["terminationOutcome"] == "SafeStateTransition", summary["terminationWhy"]
    hot = [r for r in eng.trace if r["class"] == "ConditionEvaluation" and r["ref"] == "c-hot"]
    assert hot and hot[0]["channel"] == "observed" and hot[0]["outcome"] == "NotSatisfied", hot[:1]
    assert eng.actual["latency"] == 60 and eng.observed["latency"] == 40  # channels never merged
    timeouts = [r for r in eng.trace if r["class"] == "ExceptionDisposition" and r["outcome"] == "Timeout"]
    assert timeouts, "approval timeout must be recorded"
    pa = [r for r in eng.trace if r["class"] == "ApprovalResolution" and r["outcome"] == "WaitingApproval"]
    assert pa and pa[0]["t"] + 1 == timeouts[0]["t"], (pa, timeouts)  # PT1M at 60 s/tick → 1-tick window
    assert any("pending" in f for f in summary["findings"])  # safe-state verification never implicit

    # ---------- happy path (SCN-SYNTH-002, clean): grant at t1 → dispatch → remediation → VerifiedCompletion
    exec2 = copy.deepcopy(execution)
    exec2["executionDefinition"]["scenarioId"] = "SCN-SYNTH-002"
    eng = LogicalEngine(copy.deepcopy(exec2), copy.deepcopy(spec), copy.deepcopy(scenario_clean), seed=2026,
                        run_inputs={"approvals": {"approve": {"resolution": "granted", "atTick": 1}}})
    summary = eng.run()
    assert summary["terminationOutcome"] == "VerifiedCompletion", (summary["terminationWhy"], summary["findings"])
    assert summary["verificationSucceeded"] is True
    dispatch = [r for r in eng.trace if r["class"] == "Dispatch" and r["ref"] == "act"]
    assert [r["detail"].split(":")[0] for r in dispatch] == list(CHAIN), [r["detail"] for r in dispatch]
    approvals = [r for r in eng.trace if r["class"] == "ApprovalResolution"]
    assert any(r["outcome"] == "WaitingApproval" for r in approvals)
    assert any(r["outcome"] == "granted" for r in approvals)
    # hidden disturbance touched actual (then remediation restored it) but the controller view never saw it
    assert eng.actual["latency"] == 40, eng.actual
    assert eng.observed["latency"] == 40
    assert summary["traceRecordsValid"] and summary["traceCounts"]["Dispatch"] == 5
    assert summary["evidence"]["originClass"] == "SimulationTime"
    assert summary["evidence"]["simulationRun"]["seed"] == 2026
    assert summary["runId"] == "run-SCN-SYNTH-002-seed2026"
    unresolved = [r for r in eng.trace if r["class"] == "ConditionEvaluation" and r["outcome"] == "Unresolved"]
    assert any(r["ref"] == "c-monitor" for r in unresolved), "unresolved conditions recorded, never defaulted"

    # determinism (LSE-014): identical inputs → identical trace
    eng2 = LogicalEngine(copy.deepcopy(exec2), copy.deepcopy(spec), copy.deepcopy(scenario_clean), seed=2026,
                         run_inputs={"approvals": {"approve": {"resolution": "granted", "atTick": 1}}})
    summary2 = eng2.run()
    assert eng2.trace == eng.trace

    # ---------- declared failure → exception path → escalation (LSE-011)
    eng4 = LogicalEngine(copy.deepcopy(exec2), copy.deepcopy(spec), copy.deepcopy(scenario_clean), seed=2026,
                         run_inputs={"approvals": {"approve": {"resolution": "granted", "atTick": 1}},
                                      "failures": ["act"]})
    summary4 = eng4.run()
    assert summary4["terminationOutcome"] == "SafeStateTransition", summary4["terminationWhy"]
    assert any(r["class"] == "ExceptionDisposition" and r["outcome"] == "Handled" for r in eng4.trace)

    # ---------- conformance gate (LSE-002): an invalid spec is refused
    bad_spec = copy.deepcopy(spec)
    bad_spec["behavioralSpecification"]["lifecycleStatus"] = "Running"  # runtime status → BSS-034
    try:
        LogicalEngine(copy.deepcopy(execution), bad_spec, copy.deepcopy(scenario_stale)).run()
        raise AssertionError("conformance gate must refuse an invalid specification")
    except EngineError as exc:
        assert "BSS-034" in str(exc)

    print(f"self-test OK (logical engine v{ENGINE_VERSION}, ruleset {RULESET_VERSION}, LSE-001..022)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
