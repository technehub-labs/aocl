"""AOCL canonical execution semantics (AOCL-CR-010).

Implements validation rules EXE-001..040 natively (stdlib + pyyaml) and reports
the conformance profiles of CR-010 §17 separately, with mode-specific engine
readiness (logical vs state-based) distinct from structural conformance.

CR-010 is the architectural transition between the Modeling stage and the
engine tranche: an ExecutionDefinition binds one BehavioralSpecification, one
SimulationScenario and the control/evidence models into a runnable
interpretation with DECLARED policies for every semantic decision an engine
would otherwise make implicitly. The validator enforces the policies the CR
makes normative — several are single-valued on purpose:

- Activation is graph-faithful with a declared entry (EXE-008/010); no stage
  ordering is implied.
- Stale evidence blocks dependent evaluation (EXE-014); guards evaluate before
  effects (EXE-015); authority is always checked against the declared
  AuthorityDefinition (EXE-016); effects apply as declared deltas (EXE-017).
- Event ordering honors scenario declarations with deterministic tie-breaking
  (EXE-019/020); dependencies block (EXE-021).
- The dispatch chain preserves the CR-007 evidential distinctions as distinct
  records (EXE-024/AD-007-09); retries only within declared budgets (EXE-026).
- Approvals suspend execution (EXE-027); unhandled exceptions escalate, never
  absorb (EXE-030); critical unresolved exceptions block readiness (EXE-031);
  safe states require pre-authorized authority AND verification (EXE-032/033).
- Determinism flows from declared seeded sources (EXE-034/035).
- Controller visibility is enforced at RUNTIME from scenario declarations
  (EXE-036, P30) — the single most load-bearing rule: without it, a simulated
  Controller could read the scenario's hidden ground truth and every
  data-veracity experiment would be invalid. `controllerVisiblePolicy: Full`
  is structurally forbidden, and enforcement must be Runtime, not authorial.
- Trace obligations cover all seven record classes with temporal references
  (EXE-038); runtime evidence carries run identity and a governed origin class
  (EXE-039) — simulation modes produce SimulationEvidence, never operational.

Also migrates the simulation canvas's implicit execution policies
(model/behavior.yaml human model, plant model, escalation windows) into a
Draft ExecutionDefinition skeleton (CR-010 §19): carried policies are named as
carried, never silently promoted to Approved; engine-embedded level→policy
parameters remain engine-embedded pending CR-011/012.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("error: pyyaml is required for the execution model (pip install pyyaml)")

RULESET_VERSION = "1.0.0"
SCHEMA_VERSION = "0.1"

MODES = {"Logical", "StateBased", "Hybrid"}
LIFECYCLE = ("Draft", "InReview", "Approved", "Deprecated", "Retired")
EXEC_STATES = {"Initialized", "Ready", "Running", "Suspended", "WaitingApproval", "Terminated",
               "Failed", "Cancelled"}
TIME_BASES = {"Tick", "WallClock", "EventDriven"}
TRACE_RECORDS = {"Activation", "ConditionEvaluation", "TransitionEvaluation", "Dispatch",
                 "ApprovalResolution", "ExceptionDisposition", "SafeStateTransition"}
CHAIN = ["Command", "Acknowledgement", "ExecutionStatus", "Effect", "Outcome"]

SEMVER = re.compile(r"^\d+\.\d+\.\d+$")
EXEC_URN = re.compile(r"^urn:aocl:execution:[a-z0-9][a-z0-9-]*$")
SPEC_URN = re.compile(r"^urn:aocl:spec:[a-z0-9][a-z0-9-]*$")
SCEN_URN = re.compile(r"^urn:aocl:scenarios:[a-z0-9][a-z0-9-]*$")
CTRL_URN = re.compile(r"^urn:aocl:control:[a-z0-9][a-z0-9-]*$")
EVID_URN = re.compile(r"^urn:aocl:evidence:[a-z0-9][a-z0-9-]*$")

PROFILE_RULES = {
    "structuralConformance": {"EXE-001", "EXE-002", "EXE-003", "EXE-004", "EXE-005", "EXE-006",
                              "EXE-007", "EXE-022"},
    "semanticConformance": {"EXE-008", "EXE-009", "EXE-010", "EXE-011", "EXE-012", "EXE-013",
                            "EXE-014", "EXE-015", "EXE-017", "EXE-018", "EXE-019", "EXE-020",
                            "EXE-021", "EXE-023", "EXE-024", "EXE-025", "EXE-026", "EXE-027",
                            "EXE-028", "EXE-029", "EXE-030"},
    "determinismConformance": {"EXE-034", "EXE-035"},
    "safetyConformance": {"EXE-016", "EXE-031", "EXE-032", "EXE-033"},
    "visibilityConformance": {"EXE-036", "EXE-037"},
    "traceabilityConformance": {"EXE-038", "EXE-039", "EXE-040"},
}


def _f(findings: list, rule: str, severity: str, message: str) -> None:
    findings.append({"rule": rule, "severity": severity, "message": message})


def _require(findings: list, rule: str, cond: bool, ok_msg: str, bad_msg: str, severity: str = "error") -> bool:
    if not cond:
        _f(findings, rule, severity, bad_msg)
        return False
    return True


def validate_execution_definition(data: dict) -> dict:
    """Validate a canonical ExecutionDefinition against EXE-001..040.
    Returns findings, the §17 profiles, and mode-specific engine readiness."""
    findings: list[dict] = []

    if not isinstance(data, dict):
        _f(findings, "EXE-001", "error", "document must be a mapping")
        return _result(findings, {})
    if data.get("schemaVersion") != SCHEMA_VERSION:
        _f(findings, "EXE-001", "error",
           f"schemaVersion must be '{SCHEMA_VERSION}' (this validator's contract), got {data.get('schemaVersion')!r}")
    if not SEMVER.match(str(data.get("modelVersion", ""))):
        _f(findings, "EXE-001", "error", f"modelVersion must be semver, got {data.get('modelVersion')!r}")

    ex = data.get("executionDefinition")
    if not isinstance(ex, dict):
        _f(findings, "EXE-001", "error", "executionDefinition missing")
        return _result(findings, {})

    known_root = {"schemaVersion", "modelVersion", "executionDefinition"}
    if set(data) - known_root:
        _f(findings, "EXE-001", "error", f"unknown document attributes: {sorted(set(data) - known_root)}")

    # ---- identity + bindings (EXE-001..005)
    _require(findings, "EXE-001", bool(EXEC_URN.match(str(ex.get("id", "")))),
             "ok", "executionDefinition.id must match urn:aocl:execution:<slug> (EXE-001)")
    _require(findings, "EXE-001", ex.get("type") == "ExecutionDefinition",
             "ok", "executionDefinition.type must be 'ExecutionDefinition'")
    _require(findings, "EXE-001", bool(str(ex.get("name", "")).strip()) and bool(str(ex.get("definition", "")).strip()),
             "ok", "executionDefinition.name and .definition are mandatory")
    _require(findings, "EXE-001", bool(SEMVER.match(str(ex.get("version", "")))),
             "ok", "executionDefinition.version must be semver")
    _require(findings, "EXE-001", ex.get("lifecycleStatus") in LIFECYCLE,
             "ok", f"lifecycleStatus must be one of {LIFECYCLE}")
    mode = ex.get("executionMode")
    _require(findings, "EXE-005", mode in MODES,
             "ok", f"executionMode must be one of {sorted(MODES)} (EXE-005)")
    _require(findings, "EXE-002", bool(SPEC_URN.match(str(ex.get("behavioralSpecRef", "")))) and bool(str(ex.get("specVersion", "")).strip()),
             "ok", "behavioralSpecRef (urn:aocl:spec:...) and its exact specVersion are mandatory bindings (EXE-002)")
    _require(findings, "EXE-003", bool(SCEN_URN.match(str(ex.get("scenarioRef", "")))) and bool(str(ex.get("scenarioVersion", "")).strip()),
             "ok", "scenarioRef (urn:aocl:scenarios:...) and its exact scenarioVersion are mandatory bindings (EXE-003)")
    _require(findings, "EXE-004", bool(CTRL_URN.match(str(ex.get("controlModelRef", "")))) and bool(EVID_URN.match(str(ex.get("evidenceModelRef", "")))),
             "ok", "controlModelRef and evidenceModelRef are mandatory bindings (EXE-004)")

    known = {"id", "type", "name", "definition", "version", "lifecycleStatus", "executionMode",
             "behavioralSpecRef", "specVersion", "scenarioRef", "scenarioVersion", "scenarioId",
             "controlModelRef", "evidenceModelRef", "timeBasis", "activation", "conditionEvaluation",
             "transitionEvaluation", "eventHandling", "scheduling", "actionDispatch", "humanParticipation",
             "exceptionHandling", "safeStateHandling", "determinism", "informationVisibility", "trace",
             "evidence", "executionLifecycle", "migrationNotes"}
    if set(ex) - known:
        _f(findings, "EXE-040", "error", f"executionDefinition: unknown attributes {sorted(set(ex) - known)}")

    # ---- execution lifecycle (EXE-006/007)
    lc = ex.get("executionLifecycle") or {}
    states = lc.get("states") or []
    _require(findings, "EXE-006", bool(states) and all(s in EXEC_STATES for s in states),
             "ok", f"execution lifecycle states must be from {sorted(EXEC_STATES)} (EXE-006)")
    _require(findings, "EXE-006", lc.get("distinctFromModelLifecycle") is True,
             "ok", "execution lifecycle must be declared distinct from model/spec/scenario lifecycles and run status (EXE-006)")
    if lc.get("temporalRecording") is not True:
        _f(findings, "EXE-007", "error", "execution lifecycle transitions must be recorded with temporal references (EXE-007)")

    # ---- time basis (EXE-022) with mode coherence
    tb = ex.get("timeBasis") or {}
    _require(findings, "EXE-022", tb.get("basis") in TIME_BASES,
             "ok", f"timeBasis.basis must be one of {sorted(TIME_BASES)} (EXE-022)")
    if tb.get("basis") == "Tick" and not str(tb.get("tickUnit", "")).strip():
        _f(findings, "EXE-022", "error", "tick-based time basis must declare its tick unit (EXE-022)")
    if mode in ("StateBased", "Hybrid") and tb.get("basis") != "Tick":
        _f(findings, "EXE-022", "error",
           "StateBased/Hybrid execution requires a Tick time basis — state evolution is tick-quantified (EXE-022)")
    if mode == "Logical" and tb.get("basis") == "WallClock":
        _f(findings, "EXE-022", "error",
           "Logical simulation must not bind to wall-clock time — use EventDriven or Tick (EXE-022, P08)")

    # ---- activation (EXE-008..011)
    act = ex.get("activation") or {}
    _require(findings, "EXE-008", act.get("graphWalkOnly") is True,
             "ok", "activation must be graph-faithful (graphWalkOnly) — no stage ordering is implied (EXE-008, P28)")
    _require(findings, "EXE-010", act.get("entryPolicy") == "DeclaredEntry",
             "ok", "execution must begin at the specification's declared entry (DeclaredEntry, EXE-010)")

    # ---- condition evaluation (EXE-012..014)
    ce = ex.get("conditionEvaluation") or {}
    _require(findings, "EXE-012", ce.get("contextPolicy") == "DeclaredContext",
             "ok", "conditions must be evaluated in their declared evaluation context (EXE-012)")
    _require(findings, "EXE-014", ce.get("freshnessPolicy") == "BlockOnStale",
             "ok", "stale evidence must block dependent evaluation — ProceedOnStale silently violates VER-020 (EXE-014)")
    for d in ce.get("delegatedEvaluations") or []:
        if isinstance(d, dict) and (not str(d.get("responsibleRef", "")).strip() or not str(d.get("resultContract", "")).strip()):
            _f(findings, "EXE-013", "error", "delegated evaluations must name the responsible reference and result contract (EXE-013)")

    # ---- transition evaluation (EXE-015..018)
    te = ex.get("transitionEvaluation") or {}
    _require(findings, "EXE-015", te.get("guardOrder") == "GuardsBeforeEffects",
             "ok", "guards must be evaluated before effects are applied (EXE-015)")
    _require(findings, "EXE-016", te.get("authorityCheck") == "AlwaysDeclared",
             "ok", "authority must be checked against the declared AuthorityDefinition at dispatch — never inferred (EXE-016)")
    _require(findings, "EXE-017", te.get("effectApplication") == "DeclaredDeltas",
             "ok", "effects must be applied as declared deltas with postcondition kinds preserved (EXE-017)")
    _require(findings, "EXE-018", te.get("outcomeClassification") == "Governed",
             "ok", "transition outcomes must use governed classifications (EXE-018)")

    # ---- event handling (EXE-019..021)
    eh = ex.get("eventHandling") or {}
    _require(findings, "EXE-019", eh.get("orderingResolution") == "PerScenarioDeclaration",
             "ok", "event ordering must honor the scenario's ordering declarations (EXE-019)")
    _require(findings, "EXE-020", eh.get("tieBreak") == "DeclaredDeterministic",
             "ok", "simultaneous events must resolve by a declared deterministic tie-break, never arrival order (EXE-020, P29)")
    _require(findings, "EXE-021", eh.get("dependenciesBlock") is True,
             "ok", "event dependencies must block dependents until resolved (EXE-021)")

    # ---- scheduling (EXE-023)
    sch = ex.get("scheduling") or {}
    _require(findings, "EXE-023", sch.get("cyclePolicy") == "PerVelocityDeclaration",
             "ok", "cycle execution must follow the loop's velocity declaration (EXE-023)")

    # ---- action dispatch (EXE-024..026)
    ad = ex.get("actionDispatch") or {}
    _require(findings, "EXE-024", ad.get("chain") == CHAIN,
             "ok", f"dispatch must preserve the CR-007 chain in order: {CHAIN} (EXE-024)")
    _require(findings, "EXE-024", ad.get("distinctRecords") is True,
             "ok", "chain stages must be distinct runtime records — an acknowledgement never advances state as if execution occurred (EXE-024, P32)")
    _require(findings, "EXE-025", ad.get("resultClassification") == "Governed",
             "ok", "action results must use governed outcome classifications (EXE-025)")
    rp = ad.get("retryPolicy") or {}
    if rp.get("permitted") is True and rp.get("budgetsDeclared") is not True:
        _f(findings, "EXE-026", "error", "retries are permitted only within declared budgets — declare them (EXE-026); there is no implicit retry")

    # ---- human participation (EXE-027/028)
    hp = ex.get("humanParticipation") or {}
    _require(findings, "EXE-027", hp.get("approvalGate") == "Suspend",
             "ok", "approval elements must suspend execution into WaitingApproval (EXE-027)")
    _require(findings, "EXE-028", bool(str(hp.get("timeoutPolicy", "")).strip()) and bool(str(hp.get("fallbackPolicy", "")).strip()),
             "ok", "approval timeout and fallback policies must be declared per the participation declaration (EXE-028)")

    # ---- exception handling (EXE-029..031)
    xc = ex.get("exceptionHandling") or {}
    _require(findings, "EXE-029", xc.get("handlerResolution") == "DeclaredPaths",
             "ok", "exceptions must resolve through the specification's declared handler paths (EXE-029)")
    _require(findings, "EXE-030", xc.get("unhandledPolicy") == "Escalate",
             "ok", "unhandled exceptions must escalate per the CR-007 dispositions — Absorb silently hides failures (EXE-030)")
    _require(findings, "EXE-031", xc.get("criticalUnresolvedBlock") is True,
             "ok", "critical unresolved exceptions must block execution readiness (EXE-031, BSS-026)")

    # ---- safe states (EXE-032/033)
    ss = ex.get("safeStateHandling") or {}
    _require(findings, "EXE-032", ss.get("authorityRequired") is True,
             "ok", "safe-state entry must use the pre-authorized protective mechanism (EXE-032)")
    _require(findings, "EXE-033", ss.get("verificationRequired") is True,
             "ok", "a safe state must never be treated as established without its declared verification (EXE-033, CTM-032)")

    # ---- determinism (EXE-034/035)
    det = ex.get("determinism") or {}
    _require(findings, "EXE-034", det.get("seedPolicy") == "Declared",
             "ok", "all stochastic behavior must flow through declared seeded sources (EXE-034, P33)")
    for src in det.get("stochasticSources") or []:
        if isinstance(src, dict) and (not str(src.get("sourceId", "")).strip() or not str(src.get("distribution", "")).strip()):
            _f(findings, "EXE-034", "error", "each stochastic source must declare its id and distribution (EXE-034)")
    _require(findings, "EXE-035", det.get("sameInputsSameTrace") is True,
             "ok", "same declared inputs must yield the same trace within an engine version (EXE-035, P34)")

    # ---- information visibility (EXE-036/037) — the load-bearing rule
    iv = ex.get("informationVisibility") or {}
    _require(findings, "EXE-036", iv.get("controllerVisiblePolicy") == "PerScenarioDeclaration",
             "ok", "the simulated Controller must receive exactly what the scenario declares visible — "
                "controllerVisiblePolicy: Full would hand it the scenario's hidden ground truth and "
                "invalidate every data-veracity experiment (EXE-036, P30, SCN-027)")
    _require(findings, "EXE-036", iv.get("enforcement") == "Runtime",
             "ok", "visibility must be enforced by the interpreter at runtime, not left to authoring discipline (EXE-036)")
    _require(findings, "EXE-037", iv.get("channelPolicy") == "SeparatedChannels",
             "ok", "actual, observed and estimated state must remain separate runtime channels (EXE-037, P31)")

    # ---- trace (EXE-038)
    tr = ex.get("trace") or {}
    records = tr.get("records") or []
    missing_records = sorted(TRACE_RECORDS - set(records))
    _require(findings, "EXE-038", not missing_records,
             "ok", f"trace must declare all obligatory record classes; missing: {missing_records} (EXE-038 — format is CR-013's)")
    _require(findings, "EXE-038", tr.get("temporalRefs") is True,
             "ok", "every trace record must carry its temporal reference (EXE-038)")

    # ---- evidence (EXE-039)
    ev = ex.get("evidence") or {}
    _require(findings, "EXE-039", ev.get("runIdentity") == "Declared",
             "ok", "runtime evidence must carry declared run identity (EXE-039, VER-039)")
    if ev.get("originClass") == "OperationalTime" and mode in MODES:
        _f(findings, "EXE-039", "error",
           "simulation execution produces SimulationEvidence — an ExecutionDefinition for a simulation mode "
           "cannot declare OperationalTime origin (EXE-039, AD-008-11)")
    elif ev.get("originClass") != "SimulationTime":
        _f(findings, "EXE-039", "error", f"evidence originClass {ev.get('originClass')!r} invalid (EXE-039)")

    return _result(findings, {"mode": mode, "timeBasis": (tb or {}).get("basis"),
                              "determinismDeclared": det.get("seedPolicy") == "Declared",
                              "visibilityRuntime": iv.get("enforcement") == "Runtime",
                              "traceComplete": not missing_records and tr.get("temporalRefs") is True,
                              "structuralOk": not [f for f in findings if f["severity"] == "error"
                                                   and f["rule"] in PROFILE_RULES["structuralConformance"]],
                              "semanticOk": not [f for f in findings if f["severity"] == "error"
                                                 and f["rule"] in PROFILE_RULES["semanticConformance"]],
                              "safetyOk": not [f for f in findings if f["severity"] == "error"
                                               and f["rule"] in PROFILE_RULES["safetyConformance"]],
                              "determinismOk": not [f for f in findings if f["severity"] == "error"
                                                    and f["rule"] in PROFILE_RULES["determinismConformance"]],
                              "visibilityOk": not [f for f in findings if f["severity"] == "error"
                                                   and f["rule"] in PROFILE_RULES["visibilityConformance"]]})


def _result(findings: list, ctx: dict) -> dict:
    errors = [f for f in findings if f["severity"] == "error"]
    hit = lambda rules: any(f["rule"] in rules for f in errors)
    profiles = {name: not hit(rules) for name, rules in PROFILE_RULES.items()}
    mode = ctx.get("mode")
    structural_ok = ctx.get("structuralOk", True)
    semantic_ok = ctx.get("semanticOk", True)
    safety_ok = ctx.get("safetyOk", True)
    visibility_ok = ctx.get("visibilityOk", True)
    det_ok = ctx.get("determinismOk", True)
    logical_ready = (structural_ok and semantic_ok and visibility_ok
                     and ctx.get("timeBasis") in ("Tick", "EventDriven")
                     and ctx.get("traceComplete"))
    state_ready = (logical_ready and safety_ok and det_ok
                   and ctx.get("timeBasis") == "Tick"
                   and ctx.get("determinismDeclared") and ctx.get("visibilityRuntime"))
    return {
        "valid": not errors,
        "findings": findings,
        "conformance": {**profiles,
                        "structurallyConformant": structural_ok,
                        "fullyConformant": not errors,
                        "logicalEngineReady": logical_ready and mode is not None,
                        "stateBasedEngineReady": state_ready and mode is not None},
        "engineReadinessReasons": ([] if logical_ready else ["not ready for a logical engine"])
        + ([] if state_ready else ([] if not logical_ready else ["not ready for a state-based engine"])),
    }


def load_and_validate(path: str | Path) -> dict:
    with open(path, encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    result = validate_execution_definition(data)
    result["source"] = str(path)
    return result


def migrate_behavior_model(behavior: dict) -> dict:
    """Migrate the simulation canvas's implicit execution policies (CR-010 §19)
    into a Draft ExecutionDefinition skeleton: human-response, escalation-window
    and plant policies are carried AS CARRIED (never promoted to Approved);
    the level→policy parameters stay engine-embedded pending CR-011/012 and are
    inventoried in migrationNotes."""
    findings: list[dict] = []
    if not isinstance(behavior, dict) or not isinstance(behavior.get("human"), dict):
        _f(findings, "MIG-001", "error", "expected the AOCL behavioral-parameters file (model/behavior.yaml)")
        return {"valid": False, "findings": findings, "spec": None}
    human = behavior["human"]
    plant = behavior.get("plant") or {}
    carried = [
        f"human response time ({human.get('response_time_ticks')} ticks) → timeoutPolicy",
        f"level-independent escalation windows ({human.get('hotl_escalation_window_ticks')} ticks; sim finding: "
        "the window is engagement policy, not maturity) → timeoutPolicy",
        f"HOOTL novelty-only engagement ({human.get('hootl_engagement')}) → fallbackPolicy",
        f"plant return rate and control lag ({plant}) → scheduling notes",
    ]
    spec = {
        "schemaVersion": SCHEMA_VERSION,
        "modelVersion": "1.0.0",
        "executionDefinition": {
            "id": "urn:aocl:execution:sim-canvas-statebased",
            "type": "ExecutionDefinition",
            "name": "Sim-canvas execution policies (carried)",
            "definition": "Draft execution definition carrying the simulation canvas's implicit policies as declared semantics (CR-010 §19).",
            "version": "0.1.0",
            "lifecycleStatus": "Draft",
            "executionMode": "StateBased",
            "behavioralSpecRef": "urn:aocl:spec:network-assurance-001",
            "specVersion": "carried-reference (spec under test is the informative level→policy mapping)",
            "scenarioRef": "urn:aocl:scenarios:sim-canvas",
            "scenarioVersion": "0.1.0",
            "controlModelRef": "urn:aocl:control:network-assurance-001",
            "evidenceModelRef": "urn:aocl:evidence:network-assurance-001",
            "timeBasis": {"basis": "Tick", "tickUnit": "simulation tick"},
            "activation": {"entryPolicy": "DeclaredEntry", "graphWalkOnly": True},
            "conditionEvaluation": {"contextPolicy": "DeclaredContext", "freshnessPolicy": "BlockOnStale"},
            "transitionEvaluation": {"guardOrder": "GuardsBeforeEffects", "authorityCheck": "AlwaysDeclared",
                                      "effectApplication": "DeclaredDeltas", "outcomeClassification": "Governed"},
            "eventHandling": {"orderingResolution": "PerScenarioDeclaration", "tieBreak": "DeclaredDeterministic",
                               "dependenciesBlock": True},
            "scheduling": {"cyclePolicy": "PerVelocityDeclaration", "timeoutPolicy": "escalation windows per behavior.yaml human model"},
            "actionDispatch": {"chain": CHAIN, "distinctRecords": True, "resultClassification": "Governed",
                                "retryPolicy": {"permitted": False}},
            "humanParticipation": {"approvalGate": "Suspend",
                                    "timeoutPolicy": f"escalation window {human.get('hotl_escalation_window_ticks')} ticks, "
                                                     f"human response {human.get('response_time_ticks')} ticks",
                                    "fallbackPolicy": f"HOOTL engagement: {human.get('hootl_engagement')}"},
            "exceptionHandling": {"handlerResolution": "DeclaredPaths", "unhandledPolicy": "Escalate",
                                   "criticalUnresolvedBlock": True},
            "safeStateHandling": {"authorityRequired": True, "verificationRequired": True},
            "determinism": {"seedPolicy": "Declared", "sameInputsSameTrace": True,
                             "stochasticSources": [{"sourceId": "canvas-lcg", "distribution": "xorshift-seeded uniform/normal (canvas default seed 2026, slider-overridable)"}]},
            "informationVisibility": {"channelPolicy": "SeparatedChannels",
                                       "controllerVisiblePolicy": "PerScenarioDeclaration",
                                       "enforcement": "Runtime"},
            "trace": {"records": sorted(TRACE_RECORDS), "temporalRefs": True},
            "evidence": {"originClass": "SimulationTime", "runIdentity": "Declared"},
            "executionLifecycle": {"states": ["Initialized", "Ready", "Running", "Suspended", "WaitingApproval",
                                               "Terminated", "Failed", "Cancelled"],
                                    "distinctFromModelLifecycle": True, "temporalRecording": True},
            "migrationNotes": {
                "carriedPolicies": carried,
                "missingAttributes": [
                    "the level→policy parameters (thresholds, gains, containment authority) remain engine-embedded "
                    "in behavior.yaml/tools — they become canonical only via CR-011/012 implementations",
                    "specVersion is a carried reference, not a bound canonical specification version",
                ],
            },
        },
    }
    _f(findings, "MIG-004", "warning",
       "sim-canvas policies carried as Declared Draft semantics — engine-embedded level→policy parameters "
       "inventoried, never promoted (CR-010 §19)")
    result = validate_execution_definition(spec)
    result["skeletonConformance"] = result["conformance"]
    result["spec"] = spec
    result["findings"] = findings + result["findings"]
    return result


def render(result: dict) -> str:
    lines = [f"AOCL execution definition — {result.get('source', 'validation')}"]
    conf = result.get("conformance", {})
    lines.append(" · ".join(f"{k}={conf.get(k)}" for k in conf))
    for r in result.get("engineReadinessReasons", []) or []:
        lines.append(f"  readiness: {r}")
    for f in result.get("findings", []):
        lines.append(f"[{f['severity'].upper()}] {f['rule']}: {f['message']}")
    if not result.get("findings"):
        lines.append("No findings — EXE-001..040 satisfied.")
    return "\n".join(lines)


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--self-test" in argv:
        return _self_test()
    as_json = "--json" in argv
    argv = [a for a in argv if a != "--json"]
    if "--migrate" in argv:
        with open(argv[argv.index("--migrate") + 1], encoding="utf-8") as fh:
            doc = yaml.safe_load(fh)
        result = migrate_behavior_model(doc)
        print(json.dumps(result, indent=2, default=str) if as_json else render_migrated(result))
        return 0 if result.get("spec") else 1
    if not argv:
        print("usage: aocl-execution <definition.yaml> [--json] | --migrate model/behavior.yaml | --self-test")
        return 2
    try:
        result = load_and_validate(argv[0])
    except (OSError, ValueError) as exc:
        print(f"error: {exc}")
        return 2
    print(json.dumps(result, indent=2, default=str) if as_json else render(result))
    return 0 if result["valid"] else 1


def render_migrated(result: dict) -> str:
    lines = ["AOCL execution definition — migrated Draft skeleton (CR-010 §19)"]
    for f in result.get("findings", []):
        lines.append(f"[{f['severity'].upper()}] {f['rule']}: {f['message']}")
    return "\n".join(lines)


def _self_test() -> int:
    import copy

    valid = {
        "schemaVersion": "0.1", "modelVersion": "1.0.0",
        "executionDefinition": {
            "id": "urn:aocl:execution:network-assurance-statebased", "type": "ExecutionDefinition",
            "name": "Network Assurance State-Based Execution",
            "definition": "State-based interpretation of the assurance specification under the congestion-recovery scenario.",
            "version": "1.0.0", "lifecycleStatus": "InReview",
            "executionMode": "StateBased",
            "behavioralSpecRef": "urn:aocl:spec:network-assurance-001", "specVersion": "1.0.0",
            "scenarioRef": "urn:aocl:scenarios:network-assurance", "scenarioVersion": "1.0.0",
            "scenarioId": "SCN-NET-001",
            "controlModelRef": "urn:aocl:control:network-assurance-001",
            "evidenceModelRef": "urn:aocl:evidence:network-assurance-001",
            "timeBasis": {"basis": "Tick", "tickUnit": "30 s service interval"},
            "activation": {"entryPolicy": "DeclaredEntry", "graphWalkOnly": True,
                            "notes": "entry per cond-continuous-monitoring; RepeatsTo learn→observe closes each cycle"},
            "conditionEvaluation": {"contextPolicy": "DeclaredContext", "freshnessPolicy": "BlockOnStale",
                                     "delegatedEvaluations": [{"conditionRef": "cond-approval-granted",
                                                                "responsibleRef": "policy-approval-service",
                                                                "resultContract": "authorization decision record"}]},
            "transitionEvaluation": {"guardOrder": "GuardsBeforeEffects", "authorityCheck": "AlwaysDeclared",
                                      "effectApplication": "DeclaredDeltas", "outcomeClassification": "Governed"},
            "eventHandling": {"orderingResolution": "PerScenarioDeclaration", "tieBreak": "DeclaredDeterministic",
                               "dependenciesBlock": True},
            "scheduling": {"cyclePolicy": "PerVelocityDeclaration", "timeoutPolicy": "approval window PT10M per cond-approval-timeout"},
            "actionDispatch": {"chain": CHAIN, "distinctRecords": True, "resultClassification": "Governed",
                                "retryPolicy": {"permitted": True, "budgetsDeclared": True,
                                                 "note": "retry budget 1 per invocation per pol-retry-budget"}},
            "humanParticipation": {"approvalGate": "Suspend", "timeoutPolicy": "cond-approval-timeout",
                                    "fallbackPolicy": "rejected → esc-ops branch per r11"},
            "exceptionHandling": {"handlerResolution": "DeclaredPaths", "unhandledPolicy": "Escalate",
                                   "criticalUnresolvedBlock": True},
            "safeStateHandling": {"authorityRequired": True, "verificationRequired": True},
            "determinism": {"seedPolicy": "Declared", "sameInputsSameTrace": True,
                             "stochasticSources": [{"sourceId": "demand-noise", "distribution": "declared scenario distribution"}]},
            "informationVisibility": {"channelPolicy": "SeparatedChannels",
                                       "controllerVisiblePolicy": "PerScenarioDeclaration",
                                       "enforcement": "Runtime"},
            "trace": {"records": sorted(TRACE_RECORDS), "temporalRefs": True},
            "evidence": {"originClass": "SimulationTime", "runIdentity": "Declared"},
            "executionLifecycle": {"states": ["Initialized", "Ready", "Running", "Suspended", "WaitingApproval",
                                               "Terminated", "Failed", "Cancelled"],
                                    "distinctFromModelLifecycle": True, "temporalRecording": True},
        },
    }

    base = validate_execution_definition(copy.deepcopy(valid))
    assert base["valid"], base["findings"]
    conf = base["conformance"]
    assert all(conf[k] for k in conf if "Ready" not in k and k != "fullyConformant"), conf
    assert conf["logicalEngineReady"] and conf["stateBasedEngineReady"], conf

    def broken(mutator):
        d = copy.deepcopy(valid)
        mutator(d["executionDefinition"])
        return validate_execution_definition(d)

    rules_hit = {
        "EXE-001": lambda e: e.__setitem__("id", "exec-1"),
        "EXE-002": lambda e: e.pop("specVersion"),
        "EXE-003": lambda e: e.pop("scenarioVersion"),
        "EXE-004": lambda e: e.pop("evidenceModelRef"),
        "EXE-005": lambda e: e.__setitem__("executionMode", "Quantum"),
        "EXE-006": lambda e: e["executionLifecycle"].__setitem__("distinctFromModelLifecycle", False),
        "EXE-007": lambda e: e["executionLifecycle"].pop("temporalRecording"),
        "EXE-008": lambda e: e["activation"].__setitem__("graphWalkOnly", False),
        "EXE-010": lambda e: e["activation"].__setitem__("entryPolicy", "FirstElement"),
        "EXE-012": lambda e: e["conditionEvaluation"].__setitem__("contextPolicy", "EngineDefault"),
        "EXE-013": lambda e: e["conditionEvaluation"]["delegatedEvaluations"][0].pop("resultContract"),
        "EXE-014": lambda e: e["conditionEvaluation"].__setitem__("freshnessPolicy", "ProceedOnStale"),
        "EXE-015": lambda e: e["transitionEvaluation"].__setitem__("guardOrder", "EffectsFirst"),
        "EXE-016": lambda e: e["transitionEvaluation"].__setitem__("authorityCheck", "OnDemand"),
        "EXE-017": lambda e: e["transitionEvaluation"].__setitem__("effectApplication", "EngineComputed"),
        "EXE-018": lambda e: e["transitionEvaluation"].__setitem__("outcomeClassification", "EngineSpecific"),
        "EXE-019": lambda e: e["eventHandling"].__setitem__("orderingResolution", "EngineDefault"),
        "EXE-020": lambda e: e["eventHandling"].__setitem__("tieBreak", "ArrivalOrder"),
        "EXE-021": lambda e: e["eventHandling"].__setitem__("dependenciesBlock", False),
        "EXE-022": lambda e: e["timeBasis"].pop("tickUnit"),
        "EXE-023": lambda e: e["scheduling"].__setitem__("cyclePolicy", "EngineDefault"),
        "EXE-024": lambda e: e["actionDispatch"].__setitem__("chain", ["Command", "Effect"]),
        "EXE-025": lambda e: e["actionDispatch"].__setitem__("resultClassification", "EngineSpecific"),
        "EXE-026": lambda e: e["actionDispatch"]["retryPolicy"].__setitem__("budgetsDeclared", False),
        "EXE-027": lambda e: e["humanParticipation"].__setitem__("approvalGate", "ContinueWithDefault"),
        "EXE-028": lambda e: e["humanParticipation"].pop("fallbackPolicy"),
        "EXE-029": lambda e: e["exceptionHandling"].__setitem__("handlerResolution", "EngineDefault"),
        "EXE-030": lambda e: e["exceptionHandling"].__setitem__("unhandledPolicy", "Absorb"),
        "EXE-031": lambda e: e["exceptionHandling"].__setitem__("criticalUnresolvedBlock", False),
        "EXE-032": lambda e: e["safeStateHandling"].__setitem__("authorityRequired", False),
        "EXE-033": lambda e: e["safeStateHandling"].__setitem__("verificationRequired", False),
        "EXE-034": lambda e: e["determinism"].__setitem__("seedPolicy", "Ungoverned"),
        "EXE-035": lambda e: e["determinism"].__setitem__("sameInputsSameTrace", False),
        "EXE-036": lambda e: e["informationVisibility"].__setitem__("controllerVisiblePolicy", "Full"),
        "EXE-037": lambda e: e["informationVisibility"].__setitem__("channelPolicy", "SingleChannel"),
        "EXE-038": lambda e: e["trace"].__setitem__("records", ["Activation"]),
        "EXE-039": lambda e: e["evidence"].__setitem__("originClass", "OperationalTime"),
    }
    for rule, mutator in rules_hit.items():
        r = broken(mutator)
        assert any(f["rule"] == rule for f in r["findings"]), (rule, sorted({f["rule"] for f in r["findings"]}))

    # EXE-022 mode coherence: StateBased with EventDriven basis
    def wrong_basis(e):
        e["timeBasis"] = {"basis": "EventDriven"}
    r = broken(wrong_basis)
    assert any(f["rule"] == "EXE-022" and "Tick" in f["message"] for f in r["findings"]), r["findings"]

    # EXE-036 enforcement discipline: Full visibility forbidden, Authorial enforcement insufficient
    r = broken(lambda e: e["informationVisibility"].__setitem__("enforcement", "Authorial"))
    assert any(f["rule"] == "EXE-036" for f in r["findings"])

    # EXE-055-style readiness distinction: Logical mode with EventDriven basis is logical-ready but not state-ready
    def logical_variant(e):
        e["executionMode"] = "Logical"
        e["timeBasis"] = {"basis": "EventDriven"}
    d = copy.deepcopy(valid)
    logical_variant(d["executionDefinition"])
    r = validate_execution_definition(d)
    assert r["valid"] and r["conformance"]["logicalEngineReady"] and not r["conformance"]["stateBasedEngineReady"], r

    # migration: carried policies named, engine-embedded parameters inventoried, never promoted
    behavior = {"status": "informative",
                "human": {"response_time_ticks": 30, "hotl_escalation_window_ticks": 10, "hootl_engagement": "novelty_only"},
                "plant": {"x_initial": 0.0, "plant_return_rate": 0.15}}
    mig = migrate_behavior_model(behavior)
    exd = mig["spec"]["executionDefinition"]
    assert exd["lifecycleStatus"] == "Draft" and exd["timeBasis"]["basis"] == "Tick"
    assert any("escalation windows (10 ticks" in p for p in exd["migrationNotes"]["carriedPolicies"])
    assert any("engine-embedded" in m for m in exd["migrationNotes"]["missingAttributes"])
    assert any("never promoted" in f["message"] for f in mig["findings"])
    bad = migrate_behavior_model({"wrong": 1})
    assert not bad["valid"]

    # round-trip (serialization)
    assert json.loads(json.dumps(valid)) == valid
    print(f"self-test OK (execution semantics v{RULESET_VERSION}, schema {SCHEMA_VERSION}, EXE-001..040 + migration)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
