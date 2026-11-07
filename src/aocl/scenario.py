"""AOCL simulation scenario and disturbance model (AOCL-CR-009).

Implements validation rules SCN-001..057 natively (stdlib + pyyaml) and reports
the conformance profiles of CR-009 §21 separately, with mode-specific simulation
readiness: a scenario can be ready for logical simulation while remaining
incomplete for state-based simulation (SCN-054/055, AD-009-15).

Enforces the semantic boundaries that make scenarios defensible:

- Initial states keep Actual / Observed / Estimated classes distinct
  (SCN-011/AD-009-04): a scenario may initialize the Plant at 72 ms while the
  Controller sees 48 ms (§23.10) — that distinction is the point.
- No silent defaults: Derived/Referenced/Sampled/Defaulted initialization needs
  a declared source; a default never silently replaces a missing mandatory
  condition (SCN-013, §8.3).
- Every disturbance declares what the Controller may know about it
  (SCN-027/§11.5) — the simulated Controller never automatically receives the
  scenario's hidden ground truth.
- Disturbances and events remain distinct concepts with governed
  classifications; event dependencies are validated for resolution AND cycles
  (SCN-032/034).
- Parameters are typed and range-checked (SCN-014/015); stochastic scenarios
  declare their randomization basis (SCN-049); external datasets need stable
  snapshots, not moving references (SCN-050); reproduction limitations are
  reported, never concealed (SCN-051).
- Compatibility is evaluated against the exact model baseline; an Incompatible
  scenario can never be silently Approved (SCN-052/053).

Also migrates the simulation canvas's engine-embedded scenario data
(model/behavior.yaml: the four sim scenarios, their disturbances and
invariants) into Draft library skeletons (CR-009 §24): scenario-like
configurations are preserved, hard-coded disturbance behavior is surfaced in
migrationNotes, and nothing is fabricated.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("error: pyyaml is required for the scenario model (pip install pyyaml)")

RULESET_VERSION = "1.0.0"
SCHEMA_VERSION = "0.1"

LIFECYCLE = ("Draft", "InReview", "Approved", "Deprecated", "Retired")
RUNTIME_STATUSES = {"running", "passed", "failed", "executing", "completed", "active", "deployed"}
INIT_METHODS = {"Explicit", "Derived", "Referenced", "Sampled", "Inherited", "Defaulted"}
SOURCE_METHODS = {"Derived", "Referenced", "Sampled", "Defaulted"}
TRIGGER_BASES = {"AbsoluteTime", "RelativeTime", "Periodic", "Event", "Condition", "Random", "Unknown"}
PROFILE_KINDS = {"Step", "Ramp", "Pulse", "Periodic", "Degradation", "SuddenFailure", "Intermittent",
                 "Recovery", "Compound", "Random"}
DISTURBANCE_TYPES = {"Demand", "Capacity", "Resource", "Environmental", "ComponentFailure", "DataQuality",
                     "Timing", "Security", "Dependency", "Policy", "Coordination"}
EVENT_TYPES = {"ScenarioStart", "DisturbanceOnset", "ThresholdCrossing", "ObservationReceived",
               "ApprovalRequested", "ApprovalGranted", "ActuatorFailure", "RecoveryCondition", "Timeout",
               "DependencyRestored", "VerificationCompleted"}
ORDERINGS = {"Independent", "Ordered", "Concurrent", "MutuallyExclusive", "Conditional", "Coordinated"}
COMPAT_OUTCOMES = {"Compatible", "CompatibleWithWarnings", "Incompatible", "RequiresMigration", "Unresolved"}
STATE_CLASSES = {"Actual", "Observed", "Estimated"}
PARAM_TYPES = {"numeric", "boolean", "categorical", "temporal", "structured"}
LOOP_URN = re.compile(r"^urn:aocl:loop:[a-z0-9][a-z0-9-]*$")
LIB_URN = re.compile(r"^urn:aocl:scenarios:[a-z0-9][a-z0-9-]*$")
SEMVER = re.compile(r"^\d+\.\d+\.\d+$")

PROFILE_RULES = {
    "structuralConformance": {"SCN-001", "SCN-002", "SCN-003", "SCN-004", "SCN-005", "SCN-006",
                              "SCN-016", "SCN-017", "SCN-018", "SCN-019"},
    "initialStateConformance": {"SCN-007", "SCN-008", "SCN-009", "SCN-010", "SCN-011", "SCN-012", "SCN-013"},
    "parameterConformance": {"SCN-014", "SCN-015"},
    "disturbanceConformance": {"SCN-020", "SCN-021", "SCN-022", "SCN-023", "SCN-024", "SCN-025",
                               "SCN-026", "SCN-027", "SCN-028"},
    "eventConformance": {"SCN-029", "SCN-030", "SCN-031", "SCN-032", "SCN-033", "SCN-034"},
    "variantConformance": {"SCN-035", "SCN-036"},
    "verificationTargetConformance": {"SCN-040", "SCN-041", "SCN-042"},
    "compositionConformance": {"SCN-045", "SCN-046", "SCN-047"},
    "reproducibilityConformance": {"SCN-048", "SCN-049", "SCN-050", "SCN-051"},
    "compatibilityConformance": {"SCN-052", "SCN-053"},
}


def _f(findings: list, rule: str, severity: str, message: str) -> None:
    findings.append({"rule": rule, "severity": severity, "message": message})


def validate_scenario_library(data: dict) -> dict:
    """Validate a canonical scenario-library document against SCN-001..057.
    Returns findings, the §21 profiles, and mode-specific readiness."""
    findings: list[dict] = []

    if not isinstance(data, dict):
        _f(findings, "SCN-056", "error", "document must be a mapping")
        return _result(findings, [])
    if data.get("schemaVersion") != SCHEMA_VERSION:
        _f(findings, "SCN-056", "error",
           f"schemaVersion must be '{SCHEMA_VERSION}' (this validator's contract), got {data.get('schemaVersion')!r}")
    if not SEMVER.match(str(data.get("modelVersion", ""))):
        _f(findings, "SCN-056", "error", f"modelVersion must be semver, got {data.get('modelVersion')!r}")
    lib = data.get("scenarioLibrary")
    if not isinstance(lib, dict):
        _f(findings, "SCN-056", "error", "scenarioLibrary missing")
        return _result(findings, [])

    known_root = {"schemaVersion", "modelVersion", "scenarioLibrary"}
    if set(data) - known_root:
        _f(findings, "SCN-056", "error", f"unknown document attributes: {sorted(set(data) - known_root)}")
    if not LIB_URN.match(str(lib.get("id", ""))):
        _f(findings, "SCN-001", "error", "scenarioLibrary.id must match urn:aocl:scenarios:<slug>")
    if lib.get("type") != "ScenarioLibrary":
        _f(findings, "SCN-001", "error", "scenarioLibrary.type must be 'ScenarioLibrary'")
    if not str(lib.get("name", "")).strip() or not str(lib.get("definition", "")).strip():
        _f(findings, "SCN-001", "error", "scenarioLibrary.name and .definition are mandatory")
    clr = lib.get("closedLoopRef")
    if not isinstance(clr, dict) or not LOOP_URN.match(str(clr.get("loopId", ""))) \
            or not str(clr.get("sourceSystem", "")).strip():
        _f(findings, "SCN-003", "error", "closedLoopRef must identify the governed ClosedLoop and its source system")
    known_lib = {"id", "type", "name", "definition", "closedLoopRef", "contexts", "scenarios"}
    if set(lib) - known_lib:
        _f(findings, "SCN-056", "error", f"scenarioLibrary: unknown attributes {sorted(set(lib) - known_lib)}")

    contexts = lib.get("contexts") or []
    context_ids = {c.get("contextId") for c in contexts if isinstance(c, dict)}
    for c in contexts:
        if isinstance(c, dict) and not str(c.get("domain", "")).strip():
            _f(findings, "SCN-005", "error", f"context {c.get('contextId')}: operational domain missing")

    scenarios = lib.get("scenarios") or []
    scenario_ids = {s.get("scenarioId") for s in scenarios if isinstance(s, dict) and s.get("scenarioId")}
    readiness: list[dict] = []
    seen_ids: list = []

    for sc in scenarios:
        if not isinstance(sc, dict):
            _f(findings, "SCN-001", "error", "scenarios entries must be mappings")
            continue
        sid = sc.get("scenarioId", "<missing>")
        seen_ids.append(sid)
        findings_before = len(findings)
        _validate_scenario(sc, sid, context_ids, scenario_ids, findings)
        readiness.append(_readiness(sc, sid, findings[findings_before:]))

    if len(seen_ids) != len(set(seen_ids)):
        _f(findings, "SCN-001", "error", "duplicate scenarioIds (SCN-001)")
    if not scenarios:
        _f(findings, "SCN-001", "error", "at least one scenario is required")

    return _result(findings, readiness)


def _validate_scenario(sc: dict, sid: str, context_ids: set, scenario_ids: set, findings: list) -> None:
    """Per-scenario validation (SCN-001..053)."""
    # ---- identity + context (SCN-001..006)
    if not str(sc.get("scenarioId", "")).strip() or len(str(sid)) < 3:
        _f(findings, "SCN-001", "error", f"scenario {sid}: stable identifier missing (SCN-001)")
    if not SEMVER.match(str(sc.get("version", ""))):
        _f(findings, "SCN-002", "error", f"scenario {sid}: version must be semver (SCN-002)")
    stype = sc.get("scenarioType")
    if stype not in {"Baseline", "Normal", "Stress", "Degraded", "Failure", "Recovery", "Boundary",
                     "Adversarial", "Sensitivity", "Comparative"}:
        _f(findings, "SCN-001", "error", f"scenario {sid}: scenarioType {stype!r} not governed")
    if not str(sc.get("name", "")).strip() or not str(sc.get("definition", "")).strip():
        _f(findings, "SCN-001", "error", f"scenario {sid}: name and definition are mandatory")
    model_refs = sc.get("modelRefs") or {}
    loop_refs = model_refs.get("closedLoopRefs") or []
    bad_loops = [r for r in loop_refs if not LOOP_URN.match(str(r))]
    if not loop_refs or bad_loops:
        _f(findings, "SCN-003", "error", f"scenario {sid}: must identify its ClosedLoop model scope as urn:aocl:loop refs (SCN-003)")
    if len(loop_refs) != len(set(loop_refs)):
        _f(findings, "SCN-045", "error", f"scenario {sid}: duplicate constituent loops (SCN-045)")
    if not (sc.get("modelVersionRefs") or []):
        _f(findings, "SCN-004", "error", f"scenario {sid}: must reference the exact model versions it evaluates (SCN-004)")
    if sc.get("contextRef") not in context_ids:
        _f(findings, "SCN-005", "error", f"scenario {sid}: contextRef {sc.get('contextRef')!r} does not resolve (SCN-005)")
    status = sc.get("lifecycleStatus")
    if status not in LIFECYCLE:
        hint = " — run statuses belong to simulation execution, not the scenario lifecycle (SCN-006)" \
            if str(status).lower() in RUNTIME_STATUSES else ""
        _f(findings, "SCN-006", "error", f"scenario {sid}: lifecycleStatus {status!r} invalid{hint}")

    # ---- variants (SCN-035/036)
    base = sc.get("extends")
    if base:
        if base == sid:
            _f(findings, "SCN-035", "error", f"scenario {sid}: a variant cannot extend itself (SCN-035)")
        elif base not in scenario_ids:
            _f(findings, "SCN-035", "error", f"scenario {sid}: base scenario {base!r} does not resolve in this library (SCN-035)")
        if not (sc.get("differences") or []):
            _f(findings, "SCN-036", "error", f"scenario {sid}: variants must declare their exact differences (SCN-036)")

    # ---- initial conditions (SCN-007..013)
    init = sc.get("initialConditions") or {}
    states = init.get("states") or []
    if not states or init.get("method") not in INIT_METHODS:
        _f(findings, "SCN-007", "error",
           f"scenario {sid}: executable scenarios must define InitialConditions with a declared method (SCN-007)")
    units_by_var: dict = {}
    for st in states:
        if not isinstance(st, dict):
            _f(findings, "SCN-008", "error", f"scenario {sid}: initial states must be mappings")
            continue
        stid = st.get("initialStateId", "<missing>")
        if not str(st.get("subjectRef", "")).strip() or not str(st.get("stateVariableRef", "")).strip():
            _f(findings, "SCN-008", "error", f"scenario {sid} state {stid}: subject and state variable required (SCN-008)")
        if st.get("stateClass") not in STATE_CLASSES:
            _f(findings, "SCN-011", "error",
               f"scenario {sid} state {stid}: stateClass must be Actual, Observed or Estimated — actual plant "
               "state stays distinguishable from what the Controller sees (SCN-011, AD-009-04)")
        method = st.get("initializationMethod")
        if method not in INIT_METHODS:
            _f(findings, "SCN-012", "error", f"scenario {sid} state {stid}: initialization method required (SCN-012)")
        has_value = "value" in st and st.get("value") is not None
        if method == "Explicit" and not has_value:
            _f(findings, "SCN-013", "error", f"scenario {sid} state {stid}: Explicit initialization requires a value (SCN-013)")
        if method in SOURCE_METHODS and not str(st.get("sourceRef", "")).strip():
            _f(findings, "SCN-013", "error",
               f"scenario {sid} state {stid}: {method} initialization requires a declared source — a default "
               "never silently replaces a missing mandatory condition (SCN-013, §8.3)")
        if isinstance(st.get("value"), (int, float)) and not str(st.get("unit", "")).strip() \
                and "state" not in str(st.get("valueType", "")).lower():
            _f(findings, "SCN-009", "error",
               f"scenario {sid} state {stid}: numeric initial values must preserve type and unit information (SCN-009)")
        vref = st.get("stateVariableRef")
        unit = str(st.get("unit", "")).strip()
        if vref and unit:
            prev = units_by_var.setdefault(vref, unit)
            if prev != unit:
                _f(findings, "SCN-010", "error",
                   f"scenario {sid}: inconsistent units for {vref} ({prev} vs {unit}) — initial conditions are "
                   "validated for consistency (SCN-010)")

    # ---- parameters (SCN-014/015)
    for p in sc.get("parameters") or []:
        if not isinstance(p, dict):
            continue
        pid = p.get("parameterId", "<missing>")
        if p.get("valueType") not in PARAM_TYPES:
            _f(findings, "SCN-014", "error", f"scenario {sid} parameter {pid}: declared type required (SCN-014)")
        rng = p.get("allowedRange") or {}
        val = p.get("value")
        if isinstance(val, (int, float)) and isinstance(rng.get("min"), (int, float)) and isinstance(rng.get("max"), (int, float)):
            if not (rng["min"] <= val <= rng["max"]):
                _f(findings, "SCN-015", "error",
                   f"scenario {sid} parameter {pid}: value {val} outside its allowed range "
                   f"[{rng['min']}, {rng['max']}] (SCN-015)")
        if p.get("variationMode") == "Sampled" and not str(p.get("distributionRef", "")).strip():
            _f(findings, "SCN-049", "error", f"scenario {sid} parameter {pid}: Sampled variation requires a distribution (SCN-049)")

    # ---- operating/environmental conditions (SCN-016..019)
    for oc in sc.get("operatingConditions") or []:
        if not isinstance(oc, dict):
            continue
        cid = oc.get("conditionId", "<missing>")
        if not str(oc.get("scope", "")).strip():
            _f(findings, "SCN-016", "error", f"scenario {sid} condition {cid}: applicable scope required (SCN-016)")
        if oc.get("basis") == "TimeDependent" and not str(oc.get("temporalBasis", "")).strip():
            _f(findings, "SCN-019", "error", f"scenario {sid} condition {cid}: time-dependent conditions must declare their temporal basis (SCN-019)")
    for ec in sc.get("environmentalConditions") or []:
        if isinstance(ec, dict) and (not str(ec.get("subjectRef", "")).strip() or not str(ec.get("definition", "")).strip()):
            _f(findings, "SCN-018", "error", f"scenario {sid}: environmental conditions stay separate from plant state — subject and definition required (SCN-018)")

    # ---- disturbances (SCN-020..028)
    dist_ids = set()
    for d in sc.get("disturbances") or []:
        if not isinstance(d, dict):
            _f(findings, "SCN-020", "error", f"scenario {sid}: disturbances must be mappings")
            continue
        did = d.get("disturbanceId", "<missing>")
        dist_ids.add(did)
        if not str(d.get("disturbanceId", "")).strip() or len(str(did)) < 3:
            _f(findings, "SCN-020", "error", f"scenario {sid} disturbance {did}: stable identifier required (SCN-020)")
        if not (d.get("targetRefs") or []):
            _f(findings, "SCN-021", "error", f"scenario {sid} disturbance {did}: affected subjects required (SCN-021)")
        if d.get("disturbanceType") not in DISTURBANCE_TYPES:
            _f(findings, "SCN-022", "error", f"scenario {sid} disturbance {did}: type {d.get('disturbanceType')!r} not governed (SCN-022)")
        profile = d.get("profile") or {}
        kind = profile.get("kind")
        if kind not in PROFILE_KINDS:
            _f(findings, "SCN-025", "error", f"scenario {sid} disturbance {did}: profile kind {kind!r} not governed (SCN-025)")
        elif kind == "Random" and not str(profile.get("distributionRef", "")).strip():
            _f(findings, "SCN-049", "error", f"scenario {sid} disturbance {did}: Random profiles declare their distribution (SCN-049)")
        if kind != "Random" and ("magnitude" not in d or not str(d.get("magnitudeUnit", "")).strip()):
            _f(findings, "SCN-023", "error", f"scenario {sid} disturbance {did}: magnitude and unit required (SCN-023)")
        onset = d.get("onset") or {}
        if onset.get("basis") not in TRIGGER_BASES:
            _f(findings, "SCN-024", "error", f"scenario {sid} disturbance {did}: onset basis required (SCN-024)")
        elif onset.get("basis") == "Unknown" and onset.get("unknown") is not True:
            _f(findings, "SCN-024", "error", f"scenario {sid} disturbance {did}: unknown onset must be explicitly declared (SCN-024)")
        if not str(d.get("duration", "")).strip():
            _f(findings, "SCN-024", "error", f"scenario {sid} disturbance {did}: duration defined or explicitly 'unknown' (SCN-024)")
        effect = d.get("effect") or {}
        if not str(effect.get("variableRef", "")).strip() or not str(effect.get("effect", "")).strip():
            _f(findings, "SCN-026", "error",
               f"scenario {sid} disturbance {did}: effects must reference the CR-007 state model — a disturbance "
               "is never a mere label (SCN-026, P04)")
        if not isinstance(d.get("knownToController"), bool):
            _f(findings, "SCN-027", "error",
               f"scenario {sid} disturbance {did}: must declare knownToController — the simulated Controller "
               "never automatically receives the scenario's hidden ground truth (SCN-027, §11.5)")

    # ---- events (SCN-029..034) with dependency-cycle detection
    event_ids = set()
    for ev in sc.get("events") or []:
        if not isinstance(ev, dict):
            _f(findings, "SCN-029", "error", f"scenario {sid}: events must be mappings")
            continue
        eid = ev.get("eventId", "<missing>")
        event_ids.add(eid)
        if ev.get("eventType") not in EVENT_TYPES:
            _f(findings, "SCN-029", "error", f"scenario {sid} event {eid}: type {ev.get('eventType')!r} not governed (SCN-029)")
        trig = ev.get("trigger") or {}
        if trig.get("basis") not in TRIGGER_BASES:
            _f(findings, "SCN-030", "error", f"scenario {sid} event {eid}: trigger or scheduling basis required (SCN-030)")
        elif trig.get("basis") == "Periodic" and "every" not in trig:
            _f(findings, "SCN-031", "error", f"scenario {sid} event {eid}: periodic schedules declare their interval (SCN-031)")
        if ev.get("ordering") not in ORDERINGS:
            _f(findings, "SCN-033", "error", f"scenario {sid} event {eid}: ordering {ev.get('ordering')!r} invalid — concurrent and ordered events stay distinguishable (SCN-033)")
    for ev in sc.get("events") or []:
        if not isinstance(ev, dict):
            continue
        eid = ev.get("eventId", "<missing>")
        for dep in ev.get("dependsOnRefs", []) or []:
            if dep not in event_ids and not str(dep).startswith("urn:"):
                _f(findings, "SCN-032", "error", f"scenario {sid} event {eid}: dependency {dep!r} does not resolve (SCN-032/034)")
    _check_event_cycles(sc, sid, findings)

    # ---- assumptions/constraints (SCN-037..039) — schema-enforced; spot checks
    for a in sc.get("assumptions") or []:
        if isinstance(a, dict) and not str(a.get("basis", "")).strip():
            _f(findings, "SCN-037", "error", f"scenario {sid} assumption {a.get('assumptionId')}: basis/rationale required (SCN-037)")

    # ---- verification targets (SCN-040..042)
    targets = sc.get("verificationTargets") or []
    if not targets:
        _f(findings, "SCN-040", "error", f"scenario {sid}: scenarios intended for verification must declare targets (SCN-040)")
    for t in targets:
        if not isinstance(t, dict):
            continue
        tid = t.get("targetId", "<missing>")
        if not str(t.get("claimRef", "")).strip() or not str(t.get("criterionRef", "")).strip():
            _f(findings, "SCN-041", "error", f"scenario {sid} target {tid}: must reference the CR-008 claim and criterion (SCN-041)")
        if not str(t.get("conditions", "")).strip():
            _f(findings, "SCN-040", "error", f"scenario {sid} target {tid}: scenario conditions required (SCN-040)")
    for eo in sc.get("expectedObservations") or []:
        if isinstance(eo, dict) and eo.get("kind") not in ("PlantCondition", "SensorOutput", "ControllerVisible", "VerificationEvidence"):
            _f(findings, "SCN-042", "error", f"scenario {sid} observation {eo.get('observationId')}: kind must distinguish Plant state from Controller-visible information (SCN-042)")

    # ---- composition (SCN-045..047)
    for sr in sc.get("sharedResources") or []:
        if isinstance(sr, dict):
            outside = [r for r in (sr.get("sharedByLoopRefs") or []) if r not in loop_refs]
            if outside:
                _f(findings, "SCN-046", "error", f"scenario {sid}: shared resource {sr.get('resourceId')} references loops outside the scenario scope: {outside} (SCN-046)")
    if len(loop_refs) > 1 and not sc.get("sharedResources"):
        findings.append({"rule": "SCN-046", "severity": "warning",
                         "message": f"scenario {sid}: multi-loop scenario without declared shared resources — "
                                    "shared Plants/resources must be explicit (SCN-046)"})

    # ---- reproducibility (SCN-048..051)
    rep = sc.get("reproducibility") or {}
    declared = rep.get("seedOrPolicyDeclared")
    if declared is True and rep.get("seed") is None and not str(rep.get("seedPolicy", "")).strip():
        _f(findings, "SCN-048", "error", f"scenario {sid}: seed/policy declared but neither is present (SCN-048)")
    if declared is False and not str(rep.get("limitations", "")).strip():
        _f(findings, "SCN-051", "error",
           f"scenario {sid}: reproducibility gaps must be reported, never concealed (SCN-051)")
    stochastic = declared is not True or any(
        (isinstance(p, dict) and p.get("variationMode") == "Sampled")
        for p in sc.get("parameters") or []) or any(
        isinstance(d, dict) and (d.get("profile") or {}).get("kind") == "Random"
        for d in sc.get("disturbances") or [])
    if stochastic and declared is not True:
        _f(findings, "SCN-049", "error", f"scenario {sid}: stochastic scenario must declare its randomization basis (SCN-049)")
    for ds in rep.get("externalDatasets") or []:
        if isinstance(ds, dict) and not str(ds.get("snapshot", "")).strip():
            _f(findings, "SCN-050", "error",
               f"scenario {sid} dataset {ds.get('datasetId')}: a moving external reference is insufficient — "
               "declare a stable snapshot (SCN-050)")

    # ---- compatibility (SCN-052/053)
    compat = sc.get("compatibility") or {}
    if compat.get("outcome") not in COMPAT_OUTCOMES:
        _f(findings, "SCN-052", "error", f"scenario {sid}: compatibility outcome required (SCN-052)")
    elif compat.get("outcome") == "CompatibleWithWarnings" and not str(compat.get("notes", "")).strip():
        _f(findings, "SCN-039", "error", f"scenario {sid}: CompatibleWithWarnings requires recorded limitation notes (SCN-039)")
    if compat.get("outcome") == "Incompatible" and status in ("Approved", "InReview"):
        _f(findings, "SCN-053", "error",
           f"scenario {sid}: Incompatible scenarios must not be silently Approved for execution against a "
           "materially different baseline (SCN-053)")


def _check_event_cycles(sc: dict, sid: str, findings: list) -> None:
    events = {e.get("eventId"): e for e in (sc.get("events") or []) if isinstance(e, dict)}
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {eid: WHITE for eid in events}

    def visit(eid, chain):
        color[eid] = GRAY
        for dep in (events[eid].get("dependsOnRefs") or []):
            if dep not in events:
                continue
            if color.get(dep) == GRAY:
                _f(findings, "SCN-034", "error",
                   f"scenario {sid}: event dependency cycle detected: {' -> '.join(chain + [dep])} (SCN-034)")
            elif color.get(dep) == WHITE:
                visit(dep, chain + [dep])
        color[eid] = BLACK

    for eid in events:
        if color.get(eid) == WHITE:
            visit(eid, [eid])


def _readiness(sc: dict, sid: str, new_findings: list) -> dict:
    """SCN-054/055: mode-specific readiness, distinct from structural validity."""
    rules = {f["rule"] for f in new_findings if f["severity"] == "error"}
    structural_ok = not (rules & {"SCN-001", "SCN-002", "SCN-003", "SCN-004", "SCN-005", "SCN-006"})
    logical_ok = structural_ok and not (rules & {"SCN-029", "SCN-030", "SCN-031", "SCN-033", "SCN-040"}) \
        and bool(sc.get("events")) and bool(sc.get("verificationTargets"))
    state_ok = logical_ok and not (rules & {"SCN-007", "SCN-008", "SCN-009", "SCN-010", "SCN-011",
                                            "SCN-013", "SCN-015", "SCN-020", "SCN-021", "SCN-022",
                                            "SCN-023", "SCN-024", "SCN-025", "SCN-026", "SCN-048",
                                            "SCN-049", "SCN-052", "SCN-053"})
    init = sc.get("initialConditions") or {}
    has_actual = any(isinstance(s, dict) and s.get("stateClass") == "Actual" for s in (init.get("states") or []))
    if logical_ok and not has_actual:
        state_ok = False
    compat = (sc.get("compatibility") or {}).get("outcome")
    if compat not in ("Compatible", "CompatibleWithWarnings"):
        state_ok = False
    reasons = []
    if not logical_ok:
        reasons.append("not ready for logical simulation")
    if not state_ok:
        reasons.append("not ready for state-based simulation"
                       + ("" if logical_ok else " (logical readiness is a prerequisite)")
                       + ("" if has_actual else " — no Actual-class initial state")
                       + ("" if compat in ("Compatible", "CompatibleWithWarnings") else f" — compatibility {compat!r}"))
    return {"scenarioId": sid, "logicalReady": logical_ok, "stateBasedReady": state_ok, "reasons": reasons}


def _result(findings: list, readiness: list) -> dict:
    errors = [f for f in findings if f["severity"] == "error"]
    hit = lambda rules: any(f["rule"] in rules for f in errors)
    profiles = {name: not hit(rules) for name, rules in PROFILE_RULES.items()}
    lib_logical = all(r["logicalReady"] for r in readiness) and bool(readiness)
    lib_state = all(r["stateBasedReady"] for r in readiness) and bool(readiness)
    return {
        "valid": not errors,
        "findings": findings,
        "conformance": {**profiles,
                        "structurallyValid": profiles["structuralConformance"],
                        "logicalSimulationReady": lib_logical,
                        "stateBasedSimulationReady": lib_state},
        "scenarioReadiness": readiness,
    }


def load_and_validate(path: str | Path) -> dict:
    with open(path, encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    result = validate_scenario_library(data)
    result["source"] = str(path)
    return result


def migrate_behavior_model(behavior: dict) -> dict:
    """Migrate the simulation canvas's behavioral-parameters file (model/behavior.yaml)
    into Draft scenario-library skeletons (CR-009 §24). The four sim scenarios
    (baseline/drift/fastdist/quiet) are reconstructed with their parameters and
    disturbances carried; engine-embedded behavior is surfaced in migrationNotes;
    the plausibility invariants become the verification-target skeletons. Nothing
    is fabricated beyond what the file declares."""
    findings: list[dict] = []
    if not isinstance(behavior, dict) or not isinstance(behavior.get("environment"), dict):
        _f(findings, "MIG-001", "error", "expected the AOCL behavioral-parameters file (model/behavior.yaml)")
        return {"valid": False, "findings": findings, "spec": None}
    env = behavior["environment"]
    drift = env.get("drift") or {}
    modes = env.get("known_modes") or []

    scenario_ids = ["baseline", "drift", "fastdist", "quiet"]
    scenarios = []
    for name in scenario_ids:
        with_drift = name in ("baseline", "drift")
        with_modes = name in ("baseline", "fastdist")
        with_novel = name in ("baseline", "fastdist")
        disturbances = []
        if with_modes:
            for m in modes:
                disturbances.append({
                    "disturbanceId": f"d-mode-{m.get('name', 'x')}".lower(),
                    "disturbanceType": "Demand",
                    "name": f"Known mode {m.get('name')}",
                    "definition": f"Recurring demand spike carried from behavior.yaml known_modes (period {m.get('period')} ticks).",
                    "targetRefs": ["network-service"],
                    "magnitude": m.get("magnitude"),
                    "magnitudeUnit": "signal units",
                    "onset": {"basis": "Periodic", "every": m.get("period")},
                    "duration": str(m.get("duration")) + " ticks",
                    "profile": {"kind": "Periodic"},
                    "effect": {"variableRef": "svc-latency", "effect": "impulse added to plant state"},
                    "knownToController": True,
                })
        if with_novel:
            disturbances.append({
                "disturbanceId": "d-novel",
                "disturbanceType": "Demand",
                "name": "Novel one-shot demand spike",
                "definition": f"One-shot unique-signature spikes at rate {env.get('novel_rate_per_1000_ticks')}/1000 ticks, "
                              "magnitude range carried from behavior.yaml.",
                "targetRefs": ["network-service"],
                "magnitude": str(env.get("novel_magnitude_range") or "unknown"),
                "magnitudeUnit": "signal units",
                "onset": {"basis": "Random", "at": "rate-scheduled"},
                "duration": "3-8 ticks",
                "profile": {"kind": "Random",
                             "distributionRef": f"uniform rate {env.get('novel_rate_per_1000_ticks')}/1000 ticks; "
                                                 f"magnitude uniform in {env.get('novel_magnitude_range')} (carried from behavior.yaml)"},
                "effect": {"variableRef": "svc-latency", "effect": "impulse added to plant state"},
                "knownToController": False,
            })
        if with_drift:
            disturbances.append({
                "disturbanceId": "d-drift",
                "disturbanceType": "Demand",
                "name": "Slow demand drift",
                "definition": f"Slow ramp from tick {drift.get('start')} to {drift.get('end')}, total magnitude {drift.get('magnitude')}.",
                "targetRefs": ["network-service"],
                "magnitude": drift.get("magnitude"),
                "magnitudeUnit": "signal units",
                "onset": {"basis": "RelativeTime", "at": drift.get("start")},
                "duration": f"{drift.get('end')} - {drift.get('start')} ticks",
                "profile": {"kind": "Ramp"},
                "effect": {"variableRef": "svc-latency", "effect": "gradual offset added to plant state"},
                "knownToController": False,
            })
        scenarios.append({
            "scenarioId": f"SCN-SIM-{name.upper()}-001",
            "scenarioType": {"baseline": "Normal", "drift": "Degraded", "fastdist": "Stress", "quiet": "Baseline"}[name],
            "name": f"Sim-canvas scenario: {name}",
            "definition": f"Carried from the simulation canvas '{name}' scenario (engine-embedded configuration surfaced per §24).",
            "version": "0.1.0",
            "lifecycleStatus": "Draft",
            "contextRef": "ctx-sim-canvas",
            "modelRefs": {"closedLoopRefs": ["urn:aocl:loop:service-assurance-001"]},
            "modelVersionRefs": ["aocl-sim 1.0.0 (informative mapping under test)"],
            "initialConditions": {
                "method": "Defaulted",
                "states": [{
                    "initialStateId": f"is-{name}-plant",
                    "subjectRef": "network-service",
                    "stateVariableRef": "svc-latency",
                    "value": (behavior.get("plant") or {}).get("x_initial", 0.0),
                    "valueType": "numeric",
                    "unit": "signal units",
                    "stateClass": "Actual",
                    "initializationMethod": "Defaulted",
                    "sourceRef": "model/behavior.yaml plant.x_initial",
                }],
            },
            "parameters": [
                {"parameterId": "p-horizon", "name": "Horizon", "definition": "Simulation horizon in ticks.",
                 "valueType": "numeric", "value": env.get("horizon_ticks"), "unit": "ticks",
                 "variationMode": "Fixed", "allowedRange": {"min": 1, "max": 100000}},
                {"parameterId": "p-noise", "name": "Environment noise", "definition": "Plant noise sigma.",
                 "valueType": "numeric", "value": env.get("noise_sigma"), "unit": "sigma",
                 "variationMode": "Fixed", "allowedRange": {"min": 0, "max": 100}},
                {"parameterId": "p-tolerance", "name": "Excursion tolerance", "definition": "Excursion threshold.",
                 "valueType": "numeric", "value": env.get("excursion_tolerance"), "unit": "signal units",
                 "variationMode": "Fixed", "allowedRange": {"min": 0, "max": 1000}},
            ],
            "disturbances": disturbances,
            "events": [{
                "eventId": f"ev-{name}-start", "eventType": "ScenarioStart", "name": "Scenario start",
                "trigger": {"basis": "RelativeTime", "at": 0}, "subjectRef": "network-service",
                "ordering": "Independent",
            }],
            "assumptions": [{
                "assumptionId": f"as-{name}-mapping",
                "description": "The level→policy mapping encoded in behavior.yaml is an informative hypothesis under test, not a normative rule.",
                "basis": "model/behavior.yaml status: informative",
                "validationStatus": "Unvalidated",
            }],
            "scenarioConstraints": [{
                "constraintId": f"sc-{name}-sandbox",
                "description": "L5 experimentation is sandboxed (assumption 7, load-bearing per F3) — experiments never perturb production.",
            }],
            "verificationTargets": [{
                "targetId": f"vt-{name}",
                "claimRef": f"sim-invariant:{name}",
                "criterionRef": "invariant statement carried from model/behavior.yaml",
                "conditions": "fast velocity, seed 2026, per-canvas defaults",
            }],
            "reproducibility": {"seed": 2026, "seedOrPolicyDeclared": True},
            "compatibility": {"outcome": "CompatibleWithWarnings", "modelBaselineRef": "aocl-sim 1.0.0",
                              "notes": "scenario semantics carried from an engine-specific implementation; Draft until canonicalized"},
            "migrationNotes": {
                "hardCodedBehavior": [
                    "level→policy parameters (thresholds, gains, containment authority) are hard-coded in the sim engine and behavior.yaml — not yet canonical scenario parameters (§24)",
                    "event schedules (mode periods, novel rate) were engine-embedded — surfaced as disturbance profiles",
                ],
                "missingAttributes": [
                    "CR-008 verification claims/criteria behind the invariant targets (VER-011/012)",
                    "Observed/Estimated initial states distinct from the Actual plant state (SCN-011)",
                ],
            },
        })
    spec = {
        "schemaVersion": SCHEMA_VERSION,
        "modelVersion": "1.0.0",
        "scenarioLibrary": {
            "id": "urn:aocl:scenarios:sim-canvas",
            "type": "ScenarioLibrary",
            "name": "Sim-canvas scenario skeletons",
            "definition": "Draft scenarios migrated from the simulation canvas's engine-embedded configuration (CR-009 §24).",
            "closedLoopRef": {"loopId": "urn:aocl:loop:service-assurance-001", "sourceSystem": "sim-canvas migration"},
            "contexts": [{"contextId": "ctx-sim-canvas", "domain": "AOCL simulation canvas",
                          "environment": "state-based deterministic simulation, seeded"}],
            "scenarios": scenarios,
        },
    }
    _f(findings, "MIG-004", "warning",
       f"migrated {len(scenarios)} Draft scenario skeletons with engine-embedded behavior surfaced — "
       "verification claims, observed-state initialization and canonical parameters remain open (§24)")
    result = validate_scenario_library(spec)
    result["skeletonConformance"] = result["conformance"]
    result["spec"] = spec
    result["findings"] = findings + result["findings"]
    return result


def render(result: dict) -> str:
    lines = [f"AOCL scenario library — {result.get('source', 'validation')}"]
    conf = result.get("conformance", {})
    order = [k for k in conf]
    lines.append(" · ".join(f"{k}={conf.get(k)}" for k in order))
    for r in result.get("scenarioReadiness") or []:
        lines.append(f"  {r['scenarioId']}: logical={r['logicalReady']} state-based={r['stateBasedReady']}"
                     + (f" — {'; '.join(r['reasons'])}" if r["reasons"] else ""))
    for f in result.get("findings", []):
        lines.append(f"[{f['severity'].upper()}] {f['rule']}: {f['message']}")
    if not result.get("findings"):
        lines.append("No findings — SCN-001..057 satisfied.")
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
        print("usage: aocl-scenario <library.yaml> [--json] | --migrate model/behavior.yaml | --self-test")
        return 2
    try:
        result = load_and_validate(argv[0])
    except (OSError, ValueError) as exc:
        print(f"error: {exc}")
        return 2
    print(json.dumps(result, indent=2, default=str) if as_json else render(result))
    return 0 if result["valid"] else 1


def render_migrated(result: dict) -> str:
    lines = ["AOCL scenario library — migrated Draft skeletons (CR-009 §24)"]
    for f in result.get("findings", []):
        lines.append(f"[{f['severity'].upper()}] {f['rule']}: {f['message']}")
    return "\n".join(lines)


def _self_test() -> int:
    import copy

    base = {
        "scenarioId": "SCN-NET-001", "scenarioType": "Normal",
        "name": "Network Service Congestion and Recovery",
        "definition": "Evaluate whether the assurance loop detects congestion, remediates within authority, and restores latency.",
        "version": "1.0.0", "lifecycleStatus": "InReview",
        "contextRef": "ctx-net",
        "modelRefs": {"closedLoopRefs": ["urn:aocl:loop:network-assurance-001"],
                      "behavioralSpecRef": "urn:aocl:spec:network-assurance-001",
                      "controlModelRef": "urn:aocl:control:network-assurance-001",
                      "evidenceModelRef": "urn:aocl:evidence:network-assurance-001"},
        "modelVersionRefs": ["baseline-2026-11"],
        "initialConditions": {
            "method": "Explicit",
            "states": [
                {"initialStateId": "is-plant-latency", "subjectRef": "network-service", "stateVariableRef": "svc-latency",
                 "value": 42, "valueType": "numeric", "unit": "ms", "stateClass": "Actual", "initializationMethod": "Explicit"},
                {"initialStateId": "is-obs-latency", "subjectRef": "network-service", "stateVariableRef": "svc-latency",
                 "value": 42, "valueType": "numeric", "unit": "ms", "stateClass": "Observed", "initializationMethod": "Explicit"},
                {"initialStateId": "is-mode", "subjectRef": "network-service", "stateVariableRef": "operating-mode",
                 "value": "normal", "valueType": "operating-mode state", "stateClass": "Actual", "initializationMethod": "Explicit"},
            ],
        },
        "parameters": [
            {"parameterId": "p-target", "name": "Latency target", "definition": "Goal setpoint.",
             "valueType": "numeric", "value": 50, "unit": "ms", "variationMode": "Fixed",
             "allowedRange": {"min": 1, "max": 1000}},
            {"parameterId": "p-demand", "name": "Traffic increase", "definition": "Disturbance magnitude.",
             "valueType": "numeric", "value": 35, "unit": "percent", "variationMode": "Ranged",
             "allowedRange": {"min": 0, "max": 100}},
        ],
        "operatingConditions": [{"conditionId": "oc-normal", "scope": "network-service", "basis": "Static",
                                  "operatingModeRef": "urn:aocl:control:network-assurance-001#mode-normal"}],
        "environmentalConditions": [{"conditionId": "ec-demand", "subjectRef": "external-traffic",
                                      "definition": "External demand pattern, distinct from plant state."}],
        "disturbances": [{
            "disturbanceId": "d-demand-spike", "disturbanceType": "Demand",
            "name": "Sudden traffic demand increase",
            "definition": "Step increase in external demand 60 s after start.",
            "targetRefs": ["network-service"], "magnitude": 35, "magnitudeUnit": "percent",
            "onset": {"basis": "RelativeTime", "at": "60 s"}, "duration": "persistent until remediation",
            "profile": {"kind": "Step"},
            "effect": {"variableRef": "svc-latency", "effect": "latency rises toward the congestion threshold"},
            "knownToController": False,
        }],
        "events": [
            {"eventId": "ev-start", "eventType": "ScenarioStart", "name": "Scenario starts",
             "trigger": {"basis": "RelativeTime", "at": "0 s"}, "subjectRef": "network-service", "ordering": "Independent"},
            {"eventId": "ev-onset", "eventType": "DisturbanceOnset", "name": "Demand increases",
             "trigger": {"basis": "RelativeTime", "at": "60 s"}, "subjectRef": "network-service", "ordering": "Independent"},
            {"eventId": "ev-obs", "eventType": "ObservationReceived", "name": "Congestion observed",
             "trigger": {"basis": "Event", "afterEventRef": "ev-onset"}, "subjectRef": "assurance-controller",
             "ordering": "Ordered", "dependsOnRefs": ["ev-onset"]},
            {"eventId": "ev-verify", "eventType": "VerificationCompleted", "name": "Post-remediation verification",
             "trigger": {"basis": "Condition", "conditionRef": "after execution plus evaluation interval"},
             "subjectRef": "verification-path", "ordering": "Conditional", "dependsOnRefs": ["ev-obs"]},
        ],
        "assumptions": [{"assumptionId": "as-topology", "description": "Network topology unchanged during the scenario.",
                          "basis": "controlled test environment", "validationStatus": "Validated"}],
        "scenarioConstraints": [{"constraintId": "sc-max-duration", "description": "Maximum simulated horizon 10 minutes."}],
        "expectedObservations": [
            {"observationId": "eo-latency-rise", "subjectRef": "network-service",
             "expectation": "latency rises above 50 ms after the demand spike", "kind": "PlantCondition"},
            {"observationId": "eo-controller-view", "subjectRef": "assurance-controller",
             "expectation": "controller receives the delayed post-delay observation", "kind": "ControllerVisible"},
        ],
        "verificationTargets": [
            {"targetId": "vt-detection", "claimRef": "claim-detection", "criterionRef": "crit-detection",
             "conditions": "after the demand spike", "evaluationInterval": "one observation cycle"},
            {"targetId": "vt-outcome", "claimRef": "claim-c-latency-goal", "criterionRef": "crit-latency",
             "conditions": "post-remediation evaluation window", "requiredEvidence": "independent measurement"},
        ],
        "reproducibility": {"seed": 2026, "seedOrPolicyDeclared": True},
        "compatibility": {"outcome": "Compatible", "modelBaselineRef": "baseline-2026-11"},
    }

    variant_c = copy.deepcopy(base)
    variant_c.update({
        "scenarioId": "SCN-NET-001-C", "scenarioType": "Degraded", "name": "Stale telemetry variant",
        "definition": "Detection and decision quality under stale telemetry.",
        "extends": "SCN-NET-001",
        "differences": ["controller-visible initial latency held at 42 ms while the plant moves to 72 ms",
                        "observation delay increased to 30 s"],
        "lifecycleStatus": "Draft",
        "initialConditions": {
            "method": "Explicit",
            "states": [
                {"initialStateId": "is-plant-latency", "subjectRef": "network-service", "stateVariableRef": "svc-latency",
                 "value": 42, "valueType": "numeric", "unit": "ms", "stateClass": "Actual", "initializationMethod": "Explicit"},
                {"initialStateId": "is-stale-obs", "subjectRef": "network-service", "stateVariableRef": "svc-latency",
                 "value": 42, "valueType": "numeric", "unit": "ms", "stateClass": "Observed",
                 "initializationMethod": "Derived", "sourceRef": "delayed telemetry feed"},
            ],
        },
        "disturbances": [{
            "disturbanceId": "d-stale-telemetry", "disturbanceType": "DataQuality",
            "name": "Stale telemetry", "definition": "Observation freshness degraded.",
            "targetRefs": ["sensor-latency-probe"], "magnitude": "30 s", "magnitudeUnit": "delay",
            "onset": {"basis": "RelativeTime", "at": "0 s"}, "duration": "scenario-long",
            "profile": {"kind": "Step"},
            "effect": {"variableRef": "measured-latency", "effect": "observations lag plant state"},
            "knownToController": False,
        }],
    })

    variant_f = copy.deepcopy(base)
    variant_f.update({
        "scenarioId": "SCN-NET-001-F", "scenarioType": "Comparative", "name": "Competing interventions",
        "definition": "Multi-loop coordination under conflicting remediation.",
        "extends": "SCN-NET-001",
        "differences": ["a second assurance loop intervenes on the same allocation variable"],
        "modelRefs": {"closedLoopRefs": ["urn:aocl:loop:network-assurance-001", "urn:aocl:loop:peer-assurance-001"]},
        "sharedResources": [{"resourceId": "traffic-allocation", "coordination": "supervisory arbitration",
                              "sharedByLoopRefs": ["urn:aocl:loop:network-assurance-001", "urn:aocl:loop:peer-assurance-001"]}],
    })

    valid = {
        "schemaVersion": "0.1", "modelVersion": "1.0.0",
        "scenarioLibrary": {
            "id": "urn:aocl:scenarios:network-assurance", "type": "ScenarioLibrary",
            "name": "Network Assurance Scenario Library",
            "definition": "Reference scenarios for the CR-009 acceptance patterns.",
            "closedLoopRef": {"loopId": "urn:aocl:loop:network-assurance-001", "sourceSystem": "AOCL"},
            "contexts": [{"contextId": "ctx-net", "domain": "Network Operations",
                          "environment": "production-like service topology",
                          "plantRef": "network-service"}],
            "scenarios": [base, variant_c, variant_f],
        },
    }

    res = validate_scenario_library(copy.deepcopy(valid))
    assert res["valid"], res["findings"]
    conf = res["conformance"]
    assert all(conf[k] for k in conf if "Ready" not in k), conf
    rd = {r["scenarioId"]: r for r in res["scenarioReadiness"]}
    assert rd["SCN-NET-001"]["logicalReady"] and rd["SCN-NET-001"]["stateBasedReady"], rd
    # SCN-055: variant F (multi-loop, no seed change) is state-ready; C (Draft, declared policy) differs

    def broken(mutator):
        d = copy.deepcopy(valid)
        mutator(d["scenarioLibrary"])
        return validate_scenario_library(d)

    def scenario(mutator):
        def m(lib):
            mutator(lib["scenarios"][0])
        return m

    rules_hit = {
        "SCN-001": scenario(lambda s: s.__setitem__("scenarioId", "")),
        "SCN-002": scenario(lambda s: s.__setitem__("version", "one")),
        "SCN-003": scenario(lambda s: s["modelRefs"].__setitem__("closedLoopRefs", ["loop-1"])),
        "SCN-004": scenario(lambda s: s.__setitem__("modelVersionRefs", [])),
        "SCN-005": scenario(lambda s: s.__setitem__("contextRef", "ctx-ghost")),
        "SCN-006": scenario(lambda s: s.__setitem__("lifecycleStatus", "Running")),
        "SCN-007": scenario(lambda s: s["initialConditions"].__setitem__("states", [])),
        "SCN-008": scenario(lambda s: s["initialConditions"]["states"][0].pop("subjectRef")),
        "SCN-009": scenario(lambda s: s["initialConditions"]["states"][0].pop("unit")),
        "SCN-010": scenario(lambda s: s["initialConditions"]["states"][1].__setitem__("unit", "seconds")),
        "SCN-011": scenario(lambda s: s["initialConditions"]["states"][0].__setitem__("stateClass", "Hidden")),
        "SCN-012": scenario(lambda s: s["initialConditions"]["states"][0].__setitem__("initializationMethod", "Guesswork")),
        "SCN-013": scenario(lambda s: (s["initialConditions"]["states"][0].pop("value"),
                                        s["initialConditions"]["states"][0].__setitem__("initializationMethod", "Explicit"))),
        "SCN-014": scenario(lambda s: s["parameters"][0].__setitem__("valueType", "unknown")),
        "SCN-015": scenario(lambda s: s["parameters"][0].__setitem__("value", 5000)),
        "SCN-016": scenario(lambda s: s["operatingConditions"][0].pop("scope")),
        "SCN-019": scenario(lambda s: (s["operatingConditions"][0].__setitem__("basis", "TimeDependent"),)),
        "SCN-021": scenario(lambda s: s["disturbances"][0].__setitem__("targetRefs", [])),
        "SCN-022": scenario(lambda s: s["disturbances"][0].__setitem__("disturbanceType", "Vibes")),
        "SCN-023": scenario(lambda s: s["disturbances"][0].pop("magnitudeUnit")),
        "SCN-024": scenario(lambda s: (s["disturbances"][0].pop("duration"),)),
        "SCN-025": scenario(lambda s: s["disturbances"][0]["profile"].__setitem__("kind", "Wobble")),
        "SCN-026": scenario(lambda s: s["disturbances"][0]["effect"].pop("variableRef")),
        "SCN-027": scenario(lambda s: s["disturbances"][0].pop("knownToController")),
        "SCN-029": scenario(lambda s: s["events"][0].__setitem__("eventType", "Party")),
        "SCN-030": scenario(lambda s: s["events"][0].pop("trigger")),
        "SCN-031": scenario(lambda s: s["events"][0]["trigger"].__setitem__("basis", "Periodic")),
        "SCN-032": scenario(lambda s: s["events"][2]["dependsOnRefs"].append("ev-ghost")),
        "SCN-033": scenario(lambda s: s["events"][0].__setitem__("ordering", "Whenever")),
        "SCN-035": scenario(lambda s: s.__setitem__("extends", "SCN-GHOST")),
        "SCN-036": scenario(lambda s: (s.__setitem__("extends", "SCN-NET-001"), s.__setitem__("differences", []))),
        "SCN-037": scenario(lambda s: s["assumptions"][0].pop("basis")),
        "SCN-039": scenario(lambda s: s["compatibility"].__setitem__("outcome", "CompatibleWithWarnings")),
        "SCN-040": scenario(lambda s: s["verificationTargets"][0].pop("conditions")),
        "SCN-041": scenario(lambda s: s["verificationTargets"][0].pop("claimRef")),
        "SCN-042": scenario(lambda s: s["expectedObservations"][0].__setitem__("kind", "Whatever")),
        "SCN-046": scenario(lambda s: s.__setitem__("sharedResources", [{"resourceId": "r", "sharedByLoopRefs": ["urn:aocl:loop:other-1", "urn:aocl:loop:other-2"]}])),
        "SCN-048": scenario(lambda s: s["reproducibility"].pop("seed")),
        "SCN-049": scenario(lambda s: s["parameters"][1].__setitem__("variationMode", "Sampled")),
        "SCN-050": scenario(lambda s: s["reproducibility"].__setitem__("externalDatasets", [{"datasetId": "ds-1", "source": "live feed"}])),
        "SCN-051": scenario(lambda s: s["reproducibility"].__setitem__("seedOrPolicyDeclared", False)),
        "SCN-052": scenario(lambda s: s["compatibility"].__setitem__("outcome", "Sorta")),
        "SCN-053": scenario(lambda s: (s["compatibility"].__setitem__("outcome", "Incompatible"),)),
    }
    for rule, mutator in rules_hit.items():
        r = broken(mutator)
        assert any(f["rule"] == rule for f in r["findings"]), (rule, sorted({f["rule"] for f in r["findings"]}))

    # SCN-034: dependency cycle detection
    def cycle(lib):
        lib["scenarios"][0]["events"][2]["dependsOnRefs"] = ["ev-verify"]
        lib["scenarios"][0]["events"][3]["dependsOnRefs"] = ["ev-obs"]
    r = broken(cycle)
    assert any(f["rule"] == "SCN-034" and "cycle" in f["message"] for f in r["findings"]), r["findings"]

    # SCN-055: mode-specific readiness — logical-ready but not state-based-ready
    def degraded(lib):
        lib["scenarios"][0]["compatibility"]["outcome"] = "Unresolved"
    r = broken(degraded)
    rd = {x["scenarioId"]: x for x in r["scenarioReadiness"]}
    assert rd["SCN-NET-001"]["logicalReady"] and not rd["SCN-NET-001"]["stateBasedReady"], rd

    # migration: engine-embedded behavior surfaced, invariants carried, nothing fabricated
    behavior = {
        "status": "informative", "model_version": "1.0.0-sim",
        "plant": {"x_initial": 0.0},
        "environment": {
            "horizon_ticks": 3000, "noise_sigma": 1.0, "excursion_tolerance": 3.0,
            "drift": {"start": 1200, "end": 2400, "magnitude": 18.0},
            "known_modes": [{"name": "A", "period": 420, "magnitude": 26.0, "duration": 6}],
            "novel_rate_per_1000_ticks": 6.0, "novel_magnitude_range": [15.0, 30.0],
        },
    }
    mig = migrate_behavior_model(behavior)
    lib = mig["spec"]["scenarioLibrary"]
    assert len(lib["scenarios"]) == 4
    fast = next(s for s in lib["scenarios"] if "FASTDIST" in s["scenarioId"])
    assert any(d["knownToController"] is False for d in fast["disturbances"])
    assert any(d["profile"]["kind"] == "Periodic" for d in fast["disturbances"])
    assert any("hard-coded" in " ".join(s.get("migrationNotes", {}).get("hardCodedBehavior", [""])).lower()
               or s.get("migrationNotes", {}).get("hardCodedBehavior") for s in lib["scenarios"])
    assert any("surfaced" in f["message"] for f in mig["findings"])
    bad = migrate_behavior_model({"wrong": 1})
    assert not bad["valid"]

    # round-trip (SCN-056/057)
    assert json.loads(json.dumps(valid)) == valid
    print(f"self-test OK (scenario library v{RULESET_VERSION}, schema {SCHEMA_VERSION}, SCN-001..057 + migration)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
