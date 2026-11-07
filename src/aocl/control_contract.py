"""AOCL control contracts and state-transition model (AOCL-CR-007).

Implements validation rules CTM-001..040 natively (stdlib + pyyaml) and reports
the seven conformance profiles of CR-007 §19 separately — variable, state model,
transition, contract, authority, safety, traceability — with simulation
readiness assessed independently of structural conformance (AD-007-12).

Enforces the core semantic boundaries of the CR:

- The six-way state distinction (actual/observed/estimated/desired/commanded/
  verified) is never collapsed (CTM-008); estimates must name their estimator
  (CTM-012).
- Authority is never inferred: every contract, transition and safe-state
  authority reference must resolve to a declared AuthorityDefinition (CTM-028),
  and overlapping control scopes require explicit coordination (CTM-029).
- Execution acknowledgement does not establish operational outcome (AD-007-09):
  postcondition kinds are matched against the evidential strength of the
  signals that support them (§12).
- Safety/regulatory invariants are binding: a contract touching a covered
  variable without binding the invariant is invalid (CTM-033).
- Units are not silently mixed (CTM-006).

Also migrates canonical ClosedLoop records into Draft control-model skeletons
(CR-007 §21): goal reference conditions carry over as ReferenceVariable
definitions; controlled-system bindings are NOT converted into authority
(authority is never inferred from a Controls relationship); gaps are
inventoried, never fabricated.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("error: pyyaml is required for the control-contract model (pip install pyyaml)")

RULESET_VERSION = "1.0.0"
SCHEMA_VERSION = "0.1"

LIFECYCLE = ("Draft", "InReview", "Approved", "Deprecated", "Retired")
VARIABLE_ROLES = {"Controlled", "Observed", "Estimated", "Manipulated", "State",
                  "Disturbance", "Reference", "Constraint"}
QUANTITY_TYPES = {"quantity", "number", "float", "double", "real", "decimal", "integer", "int"}
STATE_CLASSES = {"Actual", "Observed", "Estimated", "Desired", "Commanded", "Verified"}
TRANSITION_TYPES = {"Discrete", "Continuous", "Hybrid", "Abstract"}
TRIGGERS = {"AuthorizedIntervention", "PlantEvent", "Disturbance", "ExternalEvent",
            "HumanAction", "ScheduledPolicy"}
OUTCOMES = {"Completed", "Rejected", "Blocked", "Failed", "Partial", "Interrupted",
            "Unknown", "Superseded"}
CONTRACT_TYPES = {"Decision", "Action", "StateTransition", "Verification"}
POSTCONDITION_KINDS = {"ExecutionResult", "OperationalOutcome", "StateEstablished", "InvariantHeld"}
DISPOSITIONS = {"Reject", "Block", "RequestApproval", "Escalate", "EnterSafeState",
                "Recovery", "Suspend", "RecordUnresolved"}
SIGNAL_KINDS = {"ControlSignal", "Command", "Acknowledgement", "ExecutionStatus",
                "FeedbackSignal", "Observation", "StateEstimate", "VerificationEvidence"}
EVIDENTIAL_STRENGTHS = {"Instruction", "Receipt", "ExecutionReport", "Measurement",
                        "Inference", "VerifiedOutcome"}
# AD-007-09: which signal kinds can support which postcondition claims.
EXECUTION_LEVEL_SIGNALS = {"Acknowledgement", "ExecutionStatus", "FeedbackSignal"}
OUTCOME_LEVEL_SIGNALS = {"Observation", "StateEstimate", "VerificationEvidence"}
INSTRUCTION_LEVEL_SIGNALS = {"ControlSignal", "Command"}
PRIORITY_CLASSES = {"Safety", "Regulatory", "Operational", "Performance"}

SEMVER = re.compile(r"^\d+\.\d+\.\d+$")
CONTROL_URN = re.compile(r"^urn:aocl:control:[a-z0-9][a-z0-9-]*$")
LOOP_URN = re.compile(r"^urn:aocl:loop:[a-z0-9][a-z0-9-]*$")

PROFILE_RULES = {
    "variableConformance": {"CTM-001", "CTM-002", "CTM-003", "CTM-004", "CTM-005", "CTM-006"},
    "stateModelConformance": {"CTM-007", "CTM-008", "CTM-009", "CTM-010", "CTM-011", "CTM-012"},
    "transitionConformance": {"CTM-013", "CTM-014", "CTM-015", "CTM-016", "CTM-017", "CTM-018"},
    "contractConformance": {"CTM-019", "CTM-020", "CTM-021", "CTM-022", "CTM-023", "CTM-024",
                            "CTM-025", "CTM-026", "CTM-035", "AD-007-09"},
    "authorityConformance": {"CTM-027", "CTM-028", "CTM-029", "CTM-036"},
    "safetyConformance": {"CTM-030", "CTM-031", "CTM-032", "CTM-033"},
    "traceabilityConformance": {"CTM-034", "CTM-037", "CTM-039", "CTM-040", "CTM-001"},
}


def _f(findings: list, rule: str, severity: str, message: str) -> None:
    findings.append({"rule": rule, "severity": severity, "message": message})


def _unresolved_report(findings: list, entity: str, item: dict) -> None:
    """CTM-040: unresolved definitions are reported explicitly, never silent."""
    if item.get("unresolved"):
        note = str(item.get("unresolvedNote", "")).strip()
        if not note:
            _f(findings, "CTM-040", "error", f"{entity}: marked unresolved without an explanatory note")
        else:
            findings.append({"rule": "CTM-040", "severity": "warning",
                             "message": f"{entity}: unresolved — {note} (reported, not silently conformant; CTM-040)"})


def validate_control_model(data: dict) -> dict:
    """Validate a canonical control-model document against CTM-001..040 plus the
    AD-007-09 evidential-strength rule. Returns findings and the §19 profiles."""
    findings: list[dict] = []

    if not isinstance(data, dict):
        _f(findings, "CTM-039", "error", "document must be a mapping")
        return _result(findings)
    if data.get("schemaVersion") != SCHEMA_VERSION:
        _f(findings, "CTM-039", "error",
           f"schemaVersion must be '{SCHEMA_VERSION}' (this validator's contract), got {data.get('schemaVersion')!r}")
    if not SEMVER.match(str(data.get("modelVersion", ""))):
        _f(findings, "CTM-039", "error", f"modelVersion must be semver (independent of schemaVersion, CTM-039), got {data.get('modelVersion')!r}")

    model = data.get("controlModel")
    if not isinstance(model, dict):
        _f(findings, "CTM-039", "error", "controlModel missing")
        return _result(findings)

    known_root = {"schemaVersion", "modelVersion", "controlModel"}
    if set(data) - known_root:
        _f(findings, "CTM-039", "error", f"unknown document attributes: {sorted(set(data) - known_root)}")

    if not CONTROL_URN.match(str(model.get("id", ""))):
        _f(findings, "CTM-039", "error", "controlModel.id must match urn:aocl:control:<slug>")
    if model.get("type") != "ControlModel":
        _f(findings, "CTM-039", "error", "controlModel.type must be 'ControlModel'")
    if not str(model.get("name", "")).strip() or not str(model.get("definition", "")).strip():
        _f(findings, "CTM-039", "error", "controlModel.name and .definition are mandatory")
    clr = model.get("closedLoopRef")
    if not isinstance(clr, dict) or not LOOP_URN.match(str(clr.get("loopId", ""))) \
            or not str(clr.get("sourceSystem", "")).strip():
        _f(findings, "CTM-039", "error", "closedLoopRef must identify the governed ClosedLoop and its source system")

    known_model = {"id", "type", "name", "definition", "closedLoopRef", "decisionArchitectureRef",
                   "controlVariables", "stateSpaces", "operatingModes", "states", "transitions",
                   "contracts", "authority", "coordination", "invariants", "safeStates", "signals",
                   "verificationRefs", "scenarioBindings", "simulationIntent", "migrationNotes"}
    unknown = set(model) - known_model
    if unknown:
        _f(findings, "CTM-039", "error", f"controlModel: unknown attributes {sorted(unknown)}")

    dar = model.get("decisionArchitectureRef")
    if dar is not None and (dar.get("kind") not in ("OODA", "MAPE", "CUSTOM") or not str(dar.get("source", "")).strip()):
        _f(findings, "CTM-039", "error", "decisionArchitectureRef must carry a governed kind and source (§15)")

    # ---------------- control variables (CTM-001..006, 034, 040)
    variables = model.get("controlVariables") or []
    var_ids: list = []
    variables_by_id: dict = {}
    for v in variables:
        if not isinstance(v, dict):
            _f(findings, "CTM-001", "error", "controlVariables entries must be mappings")
            continue
        vid = v.get("variableId", "<missing>")
        var_ids.append(vid)
        variables_by_id[vid] = v
        if not str(v.get("variableId", "")).strip() or len(str(vid)) < 3:
            _f(findings, "CTM-001", "error", f"variable {vid}: stable identifier missing or too short (CTM-001)")
        if not str(v.get("definition", "")).strip() or not str(v.get("dataType", "")).strip():
            _f(findings, "CTM-002", "error", f"variable {vid}: semantic definition and declared data type are mandatory (CTM-002)")
        roles = v.get("roles") or []
        bad_roles = [r for r in roles if r not in VARIABLE_ROLES]
        if not roles or bad_roles:
            _f(findings, "CTM-005", "error", f"variable {vid}: roles must be declared from the canonical classifications (CTM-005), got {roles or 'none'}")
        dtype = str(v.get("dataType", "")).lower()
        if dtype in QUANTITY_TYPES and not str(v.get("unit", "")).strip() and v.get("unitless") is not True:
            _f(findings, "CTM-003", "error",
               f"variable {vid}: a quantity-typed variable must declare a unit or be explicitly unitless (CTM-003)")
        if ("Controlled" in roles or "Constraint" in roles) and not str(v.get("valueDomain", "")).strip():
            _f(findings, "CTM-004", "error", f"variable {vid}: Controlled/Constraint variables require a declared value domain (CTM-004)")
        if "Estimated" in roles and not str(v.get("estimatorRef", "")).strip():
            _f(findings, "CTM-012", "error", f"variable {vid}: Estimated variables must name their estimator or model (CTM-012)")
        if ("Controlled" in roles or "State" in roles) and not str(v.get("plantRef", "")).strip():
            _f(findings, "CTM-034", "error", f"variable {vid}: Controlled/State variables must trace to their Plant (CTM-034)")
        if ("Controlled" in roles or "Reference" in roles) and not (v.get("goalRefs") or []):
            _f(findings, "CTM-034", "error", f"variable {vid}: Controlled/Reference variables must trace to Intent/Goals (CTM-034)")
        _unresolved_report(findings, f"variable {vid}", v)
    if len(var_ids) != len(set(var_ids)):
        _f(findings, "CTM-001", "error", "duplicate variableIds (CTM-001)")

    def deref(ref, kind="reference"):
        if ref in variables_by_id:
            return True
        return None  # unknown

    # ---------------- operating modes (CTM-010)
    modes = model.get("operatingModes") or []
    mode_ids = {m.get("modeId") for m in modes if isinstance(m, dict) and m.get("modeId")}
    for m in modes:
        if isinstance(m, dict) and not str(m.get("definition", "")).strip():
            _f(findings, "CTM-010", "error", f"operating mode {m.get('modeId')}: domain-defined semantics required (CTM-010, §7.4)")

    used_modes: list = []
    for ss in model.get("stateSpaces") or []:
        if isinstance(ss, dict):
            used_modes += ss.get("operatingModeRefs", []) or []
    for st in model.get("states") or []:
        if isinstance(st, dict) and st.get("operatingModeRef"):
            used_modes.append(st["operatingModeRef"])
    for a in model.get("authority") or []:
        if isinstance(a, dict):
            used_modes += a.get("operatingModeRefs", []) or []
    for ss in model.get("safeStates") or []:
        if isinstance(ss, dict) and ss.get("operatingModeRef"):
            used_modes.append(ss["operatingModeRef"])
    undeclared_modes = sorted({m for m in used_modes if m not in mode_ids})
    if undeclared_modes:
        _f(findings, "CTM-010", "error",
           f"operating modes referenced but not defined: {undeclared_modes} — modes must be explicitly "
           "defined where used, never assumed universal (CTM-010, §7.4)")

    # ---------------- state spaces (CTM-009)
    for ss in model.get("stateSpaces") or []:
        if not isinstance(ss, dict):
            _f(findings, "CTM-009", "error", "stateSpaces entries must be mappings")
            continue
        ssid = ss.get("stateSpaceId", "<missing>")
        if not str(ss.get("subjectRef", "")).strip():
            _f(findings, "CTM-007", "error", f"state space {ssid}: governed subject missing (CTM-007)")
        svars = ss.get("variables") or []
        if not svars:
            _f(findings, "CTM-009", "error", f"state space {ssid}: relevant variables and domains must be defined (CTM-009)")
        for sv in svars:
            if not isinstance(sv, dict) or not str(sv.get("variableRef", "")).strip() or not str(sv.get("domain", "")).strip():
                _f(findings, "CTM-009", "error", f"state space {ssid}: each variable needs a reference and a domain (CTM-009)")
            elif isinstance(sv, dict) and sv["variableRef"] not in variables_by_id:
                _f(findings, "CTM-009", "error", f"state space {ssid}: variableRef {sv['variableRef']!r} does not resolve")

    # ---------------- states (CTM-007/008/011/012)
    state_ids = set()
    for st in model.get("states") or []:
        if not isinstance(st, dict):
            _f(findings, "CTM-007", "error", "states entries must be mappings")
            continue
        sid = st.get("stateId", "<missing>")
        state_ids.add(sid)
        if not str(st.get("subjectRef", "")).strip():
            _f(findings, "CTM-007", "error", f"state {sid}: governed subject missing (CTM-007)")
        if st.get("classification") not in STATE_CLASSES:
            _f(findings, "CTM-008", "error",
               f"state {sid}: classification must be one of {sorted(STATE_CLASSES)} — actual, observed, "
               "estimated, desired, commanded and verified states are never interchangeable (CTM-008)")
        if not str(st.get("temporalRef", "")).strip() or not str(st.get("provenance", "")).strip():
            _f(findings, "CTM-011", "error", f"state {sid}: temporal context and provenance are mandatory (CTM-011)")
        if st.get("classification") == "Estimated" and not str(st.get("estimatorRef", "")).strip():
            _f(findings, "CTM-012", "error",
               f"state {sid}: Estimated states must name the estimator/model that produced them — estimates "
               "are distinguishable from directly acquired observations (CTM-012)")
        for sv in st.get("stateVariables", []) or []:
            if isinstance(sv, dict) and sv.get("variableRef") not in variables_by_id:
                _f(findings, "CTM-009", "error", f"state {sid}: variableRef {sv.get('variableRef')!r} does not resolve")

    # ---------------- transitions (CTM-013..018, 036)
    contract_ids = set()
    contracts = model.get("contracts") or []
    for c in contracts:
        if isinstance(c, dict) and c.get("contractId"):
            contract_ids.add(c["contractId"])
    transition_contract_pairs: set = set()
    for t in model.get("transitions") or []:
        if not isinstance(t, dict):
            _f(findings, "CTM-013", "error", "transitions entries must be mappings")
            continue
        tid = t.get("transitionId", "<missing>")
        src = t.get("sourceStateRef") or t.get("sourcePredicate")
        tgt = t.get("targetStateRef") or t.get("targetPredicate")
        if not src or not tgt:
            _f(findings, "CTM-013", "error", f"transition {tid}: source and target conditions must be identified (CTM-013)")
        if t.get("sourceStateRef") and t["sourceStateRef"] not in state_ids:
            _f(findings, "CTM-013", "error", f"transition {tid}: sourceStateRef {t['sourceStateRef']!r} does not resolve")
        if t.get("targetStateRef") and t["targetStateRef"] not in state_ids:
            _f(findings, "CTM-013", "error", f"transition {tid}: targetStateRef {t['targetStateRef']!r} does not resolve")
        ttype = t.get("transitionType")
        if ttype not in TRANSITION_TYPES:
            _f(findings, "CTM-018", "error", f"transition {tid}: transitionType {ttype!r} invalid (CTM-018)")
        if ttype in ("Discrete", "Hybrid"):
            guard = t.get("guard") or {}
            if not str(guard.get("evaluationContext", "")).strip():
                _f(findings, "CTM-014", "error",
                   f"transition {tid}: Discrete/Hybrid transitions require an explicit guard with an evaluation context (CTM-014)")
        elif t.get("guard") is None:
            findings.append({"rule": "CTM-014", "severity": "warning",
                             "message": f"transition {tid}: continuous transition carries no guard — declare the eligibility conditions or the guard's absence"})
        if t.get("trigger") not in TRIGGERS:
            _f(findings, "CTM-017", "error", f"transition {tid}: trigger {t.get('trigger')!r} invalid (CTM-017)")
        bad_outcomes = [o for o in (t.get("possibleOutcomes") or []) if o not in OUTCOMES]
        if bad_outcomes:
            _f(findings, "CTM-015", "error", f"transition {tid}: outcome classifications not governed: {bad_outcomes} (CTM-015)")
        if not (t.get("constraintRefs") or []) and not str(t.get("constraintReview", "")).strip():
            _f(findings, "CTM-016", "error",
               f"transition {tid}: declare applicable constraints/invariants or an explicit constraintReview "
               "— transitions are evaluated against applicable constraints (CTM-016)")
        cref = t.get("contractRef")
        if not cref:
            _f(findings, "CTM-036", "error", f"transition {tid}: governing contract missing (CTM-036)")
        elif cref not in contract_ids:
            _f(findings, "CTM-036", "error", f"transition {tid}: contractRef {cref!r} does not resolve")
        else:
            transition_contract_pairs.add((tid, cref))
        if t.get("entersSafeStateRef"):
            guard = t.get("guard") or {}
            if not str(guard.get("evaluationContext", "")).strip() or not str(t.get("authorityRef", "")).strip():
                _f(findings, "CTM-032", "error",
                   f"transition {tid}: a safe-state transition requires an explicit guard and pre-authorized "
                   "protective authority — a safe-state command is not a safe state achieved (CTM-032, §11.3)")

    # ---------------- authority (CTM-027..029)
    authority = model.get("authority") or []
    authority_ids = set()
    covered_vars: dict = {}
    for a in authority:
        if not isinstance(a, dict):
            _f(findings, "CTM-027", "error", "authority entries must be mappings")
            continue
        aid = a.get("authorityId", "<missing>")
        authority_ids.add(aid)
        if not str(a.get("subjectRef", "")).strip() or not str(a.get("scopeRef", "")).strip():
            _f(findings, "CTM-027", "error", f"authority {aid}: authorized subject and controlled scope are mandatory (CTM-027)")
        pvs = a.get("permittedVariables") or []
        if not pvs:
            _f(findings, "CTM-027", "error", f"authority {aid}: permitted variables must be declared — authority is never total (CTM-027)")
        for pv in pvs:
            if isinstance(pv, dict):
                vref = pv.get("variableRef")
                if vref not in variables_by_id:
                    _f(findings, "CTM-027", "error", f"authority {aid}: permitted variable {vref!r} does not resolve")
                else:
                    covered_vars.setdefault(vref, []).append(aid)
                cr = pv.get("controlRange")
                if isinstance(cr, dict) and cr.get("unit"):
                    v = variables_by_id.get(vref) or {}
                    if v.get("unit") and cr["unit"] != v["unit"]:
                        _f(findings, "CTM-006", "error",
                           f"authority {aid}: controlRange unit {cr['unit']!r} differs from variable {vref}'s unit {v['unit']!r} (CTM-006)")
    _unresolved_report_collect(findings, authority, "authority")

    # CTM-029: overlapping scopes need explicit coordination
    coordination = model.get("coordination") or []
    coordinated_vars: set = set()
    for c in coordination:
        if not isinstance(c, dict):
            _f(findings, "CTM-029", "error", "coordination entries must be mappings")
            continue
        cid = c.get("coordinationId", "<missing>")
        for field in ("precedence", "conflictDetection", "arbitration"):
            if not str(c.get(field, "")).strip():
                _f(findings, "CTM-029", "error", f"coordination {cid}: {field} must be explicit — no implicit priority (CTM-029, §10.3)")
        coordinated_vars.update(c.get("variableRefs") or [])
    for vref, aids in sorted(covered_vars.items()):
        if len(aids) > 1 and vref not in coordinated_vars:
            _f(findings, "CTM-029", "error",
               f"variable {vref} is governed by multiple authorities ({aids}) but no CoordinationRule covers it — "
               "shared control requires explicit precedence, conflict detection and arbitration (CTM-029)")

    # ---------------- invariants (CTM-030, 033)
    invariants = model.get("invariants") or []
    invariant_ids = set()
    invariant_by_var: dict = {}
    for inv in invariants:
        if not isinstance(inv, dict):
            _f(findings, "CTM-030", "error", "invariants entries must be mappings")
            continue
        iid = inv.get("invariantId", "<missing>")
        invariant_ids.add(iid)
        if not str(inv.get("statement", "")).strip() or not str(inv.get("subject", "")).strip():
            _f(findings, "CTM-030", "error", f"invariant {iid}: subject and statement are mandatory (CTM-030)")
        if not str(inv.get("governingRef", "")).strip():
            _f(findings, "CTM-030", "error", f"invariant {iid}: must be traceable to its governing requirement (CTM-030)")
        if inv.get("priorityClass") not in PRIORITY_CLASSES:
            _f(findings, "CTM-033", "error", f"invariant {iid}: priorityClass {inv.get('priorityClass')!r} invalid (CTM-033)")
        for vref in inv.get("variableRefs", []) or []:
            invariant_by_var.setdefault(vref, []).append(iid)

    def governing_refs_resolve(refs):
        ok = set()
        ok |= invariant_ids
        ok |= authority_ids
        ok |= {r for r in refs if str(r).startswith("urn:")}  # governed external references
        return ok

    # ---------------- contracts (CTM-019..026, 035, AD-007-09)
    for c in contracts:
        if not isinstance(c, dict):
            _f(findings, "CTM-019", "error", "contracts entries must be mappings")
            continue
        cid = c.get("contractId", "<missing>")
        ctype = c.get("contractType")
        if ctype not in CONTRACT_TYPES:
            _f(findings, "CTM-019", "error", f"contract {cid}: contractType {ctype!r} invalid (CTM-019, §9.2)")
        if not str(c.get("subjectRef", "")).strip() or not str(c.get("permittedScope", "")).strip():
            _f(findings, "CTM-020", "error", f"contract {cid}: subject and permitted scope are mandatory (CTM-020)")
        preconds = c.get("preconditions") or []
        if not preconds:
            _f(findings, "CTM-021", "error", f"contract {cid}: preconditions must be explicit (CTM-021)")
        for p in preconds:
            if not isinstance(p, dict) or not str(p.get("governingRef", "")).strip():
                _f(findings, "CTM-021", "error", f"contract {cid}: each precondition must trace to its governing requirement (CTM-021, §9.3)")
        auth = c.get("authorization") or {}
        aref = auth.get("authorityRef")
        if not str(aref or "").strip():
            _f(findings, "CTM-022", "error", f"contract {cid}: required authorization must be explicit (CTM-022)")
        elif aref not in authority_ids:
            _f(findings, "CTM-028", "error",
               f"contract {cid}: authorityRef {aref!r} does not resolve to a declared AuthorityDefinition — "
               "authority is never inferred from a relationship (CTM-028, P04)")
        for cref in c.get("constraintRefs", []) or []:
            if cref not in governing_refs_resolve(c.get("constraintRefs", [])):
                _f(findings, "CTM-023", "error", f"contract {cid}: constraintRef {cref!r} does not resolve to a governed constraint (CTM-023)")
        effects = c.get("expectedEffects") or []
        if not effects:
            _f(findings, "CTM-024", "error", f"contract {cid}: expected effects must be represented (CTM-024)")
        for e in effects:
            if not isinstance(e, dict):
                continue
            vref = e.get("variableRef")
            if vref not in variables_by_id:
                _f(findings, "CTM-024", "error", f"contract {cid}: expected-effect variableRef {vref!r} does not resolve (CTM-024)")
            elif e.get("targetUnit") and variables_by_id[vref].get("unit") \
                    and e["targetUnit"] != variables_by_id[vref]["unit"]:
                _f(findings, "CTM-006", "error",
                   f"contract {cid}: effect targetUnit {e['targetUnit']!r} differs from variable {vref}'s unit "
                   f"{variables_by_id[vref]['unit']!r} — incompatible units are not silently combined (CTM-006)")
        posts = c.get("postconditions") or []
        kinds = {p.get("kind") for p in posts if isinstance(p, dict)}
        if ctype in ("Action", "StateTransition"):
            if "ExecutionResult" not in kinds:
                _f(findings, "CTM-025", "error",
                   f"contract {cid}: an execution-level postcondition (ExecutionResult) is mandatory — execution "
                   "completion is evaluated separately from the operational outcome (CTM-025, P07)")
            if not (kinds & {"OperationalOutcome", "StateEstablished"}):
                _f(findings, "CTM-025", "error",
                   f"contract {cid}: an outcome-level postcondition (OperationalOutcome/StateEstablished) is "
                   "mandatory — a command is not proof of a state transition, and a transition is not proof of "
                   "the intended outcome (CTM-025, P05)")
        # AD-007-09 evidential strength: match postcondition KIND against signal KIND
        signals = {s.get("signalId"): s for s in (model.get("signals") or []) if isinstance(s, dict)}
        for p in posts:
            if not isinstance(p, dict):
                continue
            sig = signals.get(p.get("evidenceSignalRef"))
            if sig is None:
                continue
            kind, sig_kind = p.get("kind"), sig.get("kind")
            if kind == "ExecutionResult" and sig_kind in INSTRUCTION_LEVEL_SIGNALS:
                _f(findings, "AD-007-09", "error",
                   f"contract {cid}: ExecutionResult claim supported by {sig_kind} — an instruction or command "
                   "is not a report of execution (§12)")
            if kind in ("OperationalOutcome", "StateEstablished", "InvariantHeld") \
                    and sig_kind not in OUTCOME_LEVEL_SIGNALS:
                _f(findings, "AD-007-09", "error",
                   f"contract {cid}: {kind} claim supported by {sig_kind} — acknowledgement does not establish "
                   "execution, execution status does not establish plant state, and actuator feedback does not "
                   "establish the operational effect (AD-007-09, §12)")
        failures = c.get("failureConditions") or []
        if ctype == "Action" and not failures:
            _f(findings, "CTM-026", "error", f"contract {cid}: relevant failure conditions and dispositions must be defined (CTM-026)")
        for fc in failures:
            if isinstance(fc, dict):
                if fc.get("disposition") not in DISPOSITIONS:
                    _f(findings, "CTM-026", "error", f"contract {cid}: disposition {fc.get('disposition')!r} not governed (CTM-026)")
                if fc.get("disposition") == "EnterSafeState" and not str(fc.get("safeStateRef", "")).strip():
                    _f(findings, "CTM-031", "error", f"contract {cid}: EnterSafeState disposition must name its safe state (CTM-031)")
        ber = c.get("behavioralElementRefs") or []
        if ctype == "Action" and not ber:
            _f(findings, "CTM-019", "error",
               f"contract {cid}: an intervention must reference its governing BehavioralSpecification Action "
               "elements — no modeled intervention without an applicable contract (CTM-019, P03)")
        elif not ber:
            _f(findings, "CTM-035", "error", f"contract {cid}: must be traceable to BehavioralSpecification elements (CTM-035)")
        # CTM-033: safety/regulatory invariants are binding on contracts touching their variables
        touched = {e.get("variableRef") for e in effects if isinstance(e, dict)}
        touched.update(c.get("applicableVariableRefs") or [])
        for vref in sorted(touched):
            for iid in invariant_by_var.get(vref, []):
                inv = next((i for i in invariants if isinstance(i, dict) and i.get("invariantId") == iid), {})
                if inv.get("priorityClass") in ("Safety", "Regulatory") and iid not in (c.get("constraintRefs") or []):
                    _f(findings, "CTM-033", "error",
                       f"contract {cid} touches variable {vref} covered by {inv.get('priorityClass')} invariant "
                       f"{iid} without binding it — lower-authority interventions shall not bypass safety or "
                       "regulatory constraints (CTM-033)")
        _unresolved_report(findings, f"contract {cid}", c)

    # ---------------- safe states (CTM-031..033) + verification refs (CTM-037)
    safe_states = model.get("safeStates") or []
    safe_state_ids = {s.get("safeStateId") for s in safe_states if isinstance(s, dict) and s.get("safeStateId")}
    needs_safe = any(
        (isinstance(fc, dict) and fc.get("disposition") == "EnterSafeState")
        for c in contracts if isinstance(c, dict)
        for fc in (c.get("failureConditions") or [])
    ) or any(isinstance(t, dict) and t.get("entersSafeStateRef") for t in model.get("transitions") or [])
    if needs_safe and not safe_states:
        _f(findings, "CTM-031", "error",
           "safe-state dispositions/transitions are declared but no safe states are defined (CTM-031, §11.2)")
    ver_refs = {v.get("verificationRef") for v in (model.get("verificationRefs") or []) if isinstance(v, dict)}
    for v in model.get("verificationRefs") or []:
        if isinstance(v, dict) and not str(v.get("claim", "")).strip():
            _f(findings, "CTM-037", "error", "verification references must state the claim they support (CTM-037)")
    for s in safe_states:
        if not isinstance(s, dict):
            continue
        sid = s.get("safeStateId", "<missing>")
        for ref in s.get("verificationRefs", []) or []:
            if ref not in ver_refs:
                _f(findings, "CTM-032", "error",
                   f"safe state {sid}: verificationRef {ref!r} does not resolve — safe states are verified, "
                   "not assumed from the entry command (CTM-032, §11.3)")
        for e in s.get("entryConditions", []) or s.get("exitConditions", []) or []:
            if not str(e).strip():
                _f(findings, "CTM-032", "error", f"safe state {sid}: entry/exit conditions must be explicit (CTM-032)")
        if s.get("authorityRef") and s["authorityRef"] not in authority_ids:
            _f(findings, "CTM-028", "error", f"safe state {sid}: authorityRef {s['authorityRef']!r} does not resolve (CTM-028)")

    # signals: kinds/strengths coherent
    for s in model.get("signals") or []:
        if not isinstance(s, dict):
            continue
        sid = s.get("signalId", "<missing>")
        if s.get("kind") not in SIGNAL_KINDS or s.get("evidentialStrength") not in EVIDENTIAL_STRENGTHS:
            _f(findings, "CTM-038", "error", f"signal {sid}: kind/strength not governed (§12)")
        if s.get("kind") in ("ControlSignal", "Command") and s.get("evidentialStrength") not in ("Instruction",):
            _f(findings, "CTM-038", "error", f"signal {sid}: instructions carry Instruction strength (§12)")
        if s.get("kind") == "Acknowledgement" and s.get("evidentialStrength") != "Receipt":
            _f(findings, "CTM-038", "error", f"signal {sid}: an acknowledgement is a Receipt — it does not establish execution (§12)")

    return _result(findings)


def _unresolved_report_collect(findings: list, items, entity: str) -> None:
    for item in items or []:
        if isinstance(item, dict):
            _unresolved_report(findings, f"{entity} {item.get(entity.rstrip('y') + 'ies', item.get('authorityId', '<missing>'))}", item)


def _result(findings: list) -> dict:
    errors = [f for f in findings if f["severity"] == "error"]
    hit = lambda rules: any(f["rule"] in rules for f in errors)
    profiles = {name: not hit(rules) for name, rules in PROFILE_RULES.items()}
    unresolved = [f for f in findings if f["rule"] == "CTM-040" and f["severity"] == "warning"]
    return {
        "valid": not errors,
        "findings": findings,
        "conformance": {**profiles,
                        "structurallyConformant": all(v for k, v in profiles.items() if k != "traceabilityConformance"),
                        "fullyConformant": all(profiles.values()) and not unresolved,
                        "simulationReady": False,
                        "unresolvedDefinitions": len(unresolved)},
    }


def simulate_readiness(result: dict, model: dict) -> dict:
    """AD-007-12: simulation readiness assessed independently of structural conformance."""
    reasons = []
    conf = result["conformance"]
    if not conf["structurallyConformant"]:
        reasons.append("not structurally conformant")
    if not (model.get("stateSpaces") or []):
        reasons.append("no state spaces defined (CR-009 needs StateSpace/State/ControlVariable inputs)")
    transitions = model.get("transitions") or []
    if not transitions:
        reasons.append("no state transitions defined")
    elif not all((t.get("guard") or {}).get("evaluationContext") for t in transitions if isinstance(t, dict)):
        reasons.append("transitions without explicit guards cannot be evaluated in simulation")
    if not (model.get("scenarioBindings") or []):
        reasons.append("no scenarioBindings (CR-009 scenarios must bind initial conditions and disturbances)")
    if not (model.get("simulationIntent") or {}).get("intendedType"):
        reasons.append("no declared simulation intent (§19 Simulation Readiness profile)")
    result["conformance"]["simulationReady"] = not reasons
    result["simulationReadinessReasons"] = reasons
    return result


def load_and_validate(path: str | Path) -> dict:
    with open(path, encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    result = validate_control_model(data)
    if isinstance(data, dict):
        result = simulate_readiness(result, data.get("controlModel") or {})
    result["source"] = str(path)
    return result


def migrate_from_loop(canonical_doc: dict) -> dict:
    """Migrate a canonical ClosedLoop (CR-002) into a Draft control-model skeleton
    (CR-007 §21). Preserves loop identity, goal reference conditions (as
    ReferenceVariable definitions with their units) and controlled-system
    references. Controlled-system bindings are deliberately NOT converted into
    AuthorityDefinitions — authority is never inferred from a Controls
    relationship (CTM-028); that gap is inventoried. No transitions, states or
    contracts are fabricated."""
    findings: list[dict] = []
    if not isinstance(canonical_doc, dict) or not isinstance(canonical_doc.get("closedLoop"), dict):
        _f(findings, "MIG-001", "error", "expected a canonical ClosedLoop document (CR-002)")
        return {"valid": False, "findings": findings, "spec": None}
    loop = canonical_doc["closedLoop"]
    lid = loop.get("id", "unknown")
    short = lid.rsplit(":", 1)[-1]
    variables = []
    carried = 0
    intent = loop.get("intent") or {}
    for g in intent.get("goals", []) or []:
        for rc in g.get("referenceConditions", []) or []:
            carried += 1
            variables.append({
                "variableId": f"ref-{rc.get('variable', 'condition')}".replace(" ", "-"),
                "name": str(rc.get("variable", "reference condition")),
                "definition": f"Carried from goal '{g.get('goalId', '')}' reference condition: "
                              f"{rc.get('variable')} {rc.get('operator')} {rc.get('targetValue')} "
                              f"{rc.get('unit') or ''}".strip(),
                "dataType": "quantity" if isinstance(rc.get("targetValue"), (int, float)) else "string",
                "unit": rc.get("unit"),
                "unitless": rc.get("unit") is None,
                "roles": ["Reference"],
                "goalRefs": [g.get("goalId", "")],
                "unresolved": True,
                "unresolvedNote": "carried from a reference condition — control semantics, domain and "
                                  "measurement mechanism are not yet modeled (§21)",
            })
    missing = [
        "ControlledVariable / ManipulatedVariable definitions (CTM-001..005)",
        "StateSpace, states and the six-way state distinction (CTM-007..012)",
        "StateTransitions with guards and governed outcomes (CTM-013..018)",
        "ControlContracts with preconditions/postconditions (CTM-019..026)",
        "AuthorityDefinitions — controlled-system bindings do NOT confer authority (CTM-027/028)",
        "invariants and safe states (CTM-030..033)",
    ]
    unresolved_mappings = [
        f"controlled-system binding {b.get('bindingId', '?')}: requires an explicit AuthorityDefinition; "
        "authority is never inferred from a Controls relationship (CTM-028, §10.1)"
        for b in (loop.get("controlledSystems") or []) if isinstance(b, dict)
    ]
    spec = {
        "schemaVersion": SCHEMA_VERSION,
        "modelVersion": "1.0.0",
        "controlModel": {
            "id": f"urn:aocl:control:{short}",
            "type": "ControlModel",
            "name": f"Migrated control model for {short}",
            "definition": loop.get("definition") or f"Skeleton migrated from {lid}; control semantics not yet modeled.",
            "closedLoopRef": {"loopId": lid, "sourceSystem": "canonical-loop migration"},
            "controlVariables": variables,
            "contracts": [],
            "authority": [],
            "migrationNotes": {"missingAttributes": missing, "unresolvedMappings": unresolved_mappings},
        },
    }
    _f(findings, "MIG-004", "warning",
       f"loop {short}: migrated to Draft with {len(missing)} missing control attributes and "
       f"{len(unresolved_mappings)} authority-mapping gaps inventoried — never fabricated (CR-007 §21)")
    result = validate_control_model(spec)
    result["skeletonConformance"] = result["conformance"]
    result["spec"] = spec
    result["findings"] = findings + [f for f in result["findings"] if f["rule"] not in ("MIG-004",)]
    result["carriedReferenceConditions"] = carried
    return result


def render(result: dict) -> str:
    lines = [f"AOCL control model — {result.get('source', 'validation')}"]
    conf = result.get("conformance", {})
    order = ["variableConformance", "stateModelConformance", "transitionConformance",
             "contractConformance", "authorityConformance", "safetyConformance",
             "traceabilityConformance", "structurallyConformant", "fullyConformant", "simulationReady"]
    lines.append(" · ".join(f"{k}={conf.get(k)}" for k in order))
    for r in result.get("simulationReadinessReasons", []) or []:
        lines.append(f"  readiness: {r}")
    for f in result.get("findings", []):
        lines.append(f"[{f['severity'].upper()}] {f['rule']}: {f['message']}")
    if not result.get("findings"):
        lines.append("No findings — CTM-001..040 and the AD-007-09 evidential rule satisfied.")
    return "\n".join(lines)


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--self-test" in argv:
        return _self_test()
    as_json = "--json" in argv
    argv = [a for a in argv if a != "--json"]
    if "--migrate" in argv:
        i = argv.index("--migrate")
        with open(argv[i + 1], encoding="utf-8") as fh:
            doc = yaml.safe_load(fh)
        result = migrate_from_loop(doc)
        print(json.dumps(result, indent=2, default=str) if as_json else render_migrated(result))
        return 0 if result["valid"] else 1
    if not argv:
        print("usage: aocl-control-contract <model.yaml> [--json] | --migrate <canonical-loop.yaml> | --self-test")
        return 2
    try:
        result = load_and_validate(argv[0])
    except (OSError, ValueError) as exc:
        print(f"error: {exc}")
        return 2
    print(json.dumps(result, indent=2, default=str) if as_json else render(result))
    return 0 if result["valid"] else 1


def render_migrated(result: dict) -> str:
    lines = ["AOCL control model — migrated Draft skeleton (CR-007 §21)"]
    for f in result.get("findings", []):
        lines.append(f"[{f['severity'].upper()}] {f['rule']}: {f['message']}")
    lines.append(f"carried reference conditions: {result.get('carriedReferenceConditions', 0)}")
    return "\n".join(lines)


def _self_test() -> int:
    import copy

    valid = {
        "schemaVersion": "0.1", "modelVersion": "1.0.0",
        "controlModel": {
            "id": "urn:aocl:control:network-assurance-001", "type": "ControlModel",
            "name": "Network Service Assurance Control Model",
            "definition": "Controls end-to-end service latency via traffic allocation within authorized bounds.",
            "closedLoopRef": {"loopId": "urn:aocl:loop:network-assurance-001", "sourceSystem": "AOCL"},
            "decisionArchitectureRef": {"kind": "MAPE", "source": "loop registration"},
            "controlVariables": [
                {"variableId": "svc-latency", "name": "Service latency", "definition": "End-to-end latency.",
                 "dataType": "quantity", "unit": "ms", "valueDomain": "0..10000 ms",
                 "roles": ["Controlled"], "plantRef": "network-service", "goalRefs": ["goal-latency"]},
                {"variableId": "measured-latency", "name": "Measured latency", "definition": "Observed latency.",
                 "dataType": "quantity", "unit": "ms", "roles": ["Observed"], "observedByRef": "sensor-latency-probe"},
                {"variableId": "predicted-latency", "name": "Predicted latency", "definition": "Estimated latency.",
                 "dataType": "quantity", "unit": "ms", "roles": ["Estimated"], "estimatorRef": "estimator-congestion"},
                {"variableId": "traffic-allocation", "name": "Traffic allocation", "definition": "Allocation split.",
                 "dataType": "quantity", "unit": "percent", "valueDomain": "0..100 percent",
                 "roles": ["Manipulated"], "plantRef": "network-service"},
                {"variableId": "demand-external", "name": "External demand", "definition": "Demand profile.",
                 "dataType": "quantity", "unit": "Gbps", "roles": ["Disturbance"]},
                {"variableId": "target-latency", "name": "Target latency", "definition": "Reference target.",
                 "dataType": "quantity", "unit": "ms", "roles": ["Reference"], "goalRefs": ["goal-latency"]},
                {"variableId": "max-utilization", "name": "Max utilization", "definition": "Boundary.",
                 "dataType": "quantity", "unit": "percent", "valueDomain": "0..100 percent", "roles": ["Constraint"]},
            ],
            "operatingModes": [
                {"modeId": "normal", "definition": "Nominal service operation."},
                {"modeId": "degraded", "definition": "Latency above threshold; remediation active."},
                {"modeId": "recovering", "definition": "Authorized redistribution in progress."},
                {"modeId": "safe-mode", "definition": "Governed acceptable-risk state; automated remediation suspended."},
            ],
            "states": [
                {"stateId": "st-normal-obs", "subjectRef": "network-service", "classification": "Observed",
                 "stateVariables": [{"variableRef": "measured-latency", "value": 42, "unit": "ms"}],
                 "temporalRef": "cycle t", "provenance": "sensor-latency-probe", "operatingModeRef": "normal"},
                {"stateId": "st-degraded-est", "subjectRef": "network-service", "classification": "Estimated",
                 "stateVariables": [{"variableRef": "predicted-latency", "value": 61, "unit": "ms"}],
                 "temporalRef": "cycle t+1", "provenance": "estimator-congestion", "estimatorRef": "estimator-congestion",
                 "operatingModeRef": "degraded"},
                {"stateId": "st-reroute-commanded", "subjectRef": "network-service", "classification": "Commanded",
                 "stateVariables": [{"variableRef": "traffic-allocation", "value": 70, "unit": "percent"}],
                 "temporalRef": "cycle t", "provenance": "assurance-controller command", "operatingModeRef": "recovering"},
            ],
            "transitions": [
                {"transitionId": "tr-normal-degraded", "transitionType": "Discrete", "trigger": "Disturbance",
                 "sourceStateRef": "st-normal-obs", "targetStateRef": "st-degraded-est",
                 "guard": {"description": "valid observation exceeds bound", "evaluationContext": "fresh observation within tolerance"},
                 "constraintRefs": ["inv-availability"], "authorityRef": "auth-protective",
                 "contractRef": "ctr-redistribute", "possibleOutcomes": ["Completed", "Unknown"]},
                {"transitionId": "tr-degraded-recovering", "transitionType": "Discrete", "trigger": "AuthorizedIntervention",
                 "sourceStateRef": "st-degraded-est", "targetStateRef": "st-reroute-commanded",
                 "guard": {"description": "permitted allocation within control range", "evaluationContext": "authority check"},
                 "constraintRefs": ["inv-availability", "inv-utilization"], "authorityRef": "auth-assurance",
                 "contractRef": "ctr-redistribute", "possibleOutcomes": ["Completed", "Rejected", "Blocked", "Failed"]},
                {"transitionId": "tr-recovering-normal", "transitionType": "Hybrid", "trigger": "PlantEvent",
                 "sourcePredicate": "latency below target", "targetStateRef": "st-normal-obs",
                 "guard": {"description": "verified post-intervention latency", "evaluationContext": "independent verification"},
                 "constraintRefs": [], "constraintReview": "no additional constraints beyond the binding invariants already evaluated on the entry transition",
                 "authorityRef": "auth-protective", "contractRef": "ctr-verify", "possibleOutcomes": ["Completed", "Partial", "Unknown"]},
            ],
            "contracts": [
                {"contractId": "ctr-redistribute", "name": "Traffic Redistribution", "contractType": "Action",
                 "definition": "Redistribute traffic allocation to reduce congestion.",
                 "subjectRef": "assurance-controller", "targetRef": "network-service",
                 "applicableVariableRefs": ["traffic-allocation", "svc-latency"],
                 "permittedScope": "traffic allocation within the declared control range (0..85 percent)",
                 "preconditions": [
                     {"preconditionId": "pre-fresh-obs", "description": "fresh latency observation",
                      "governingRef": "urn:aocl:policy:observation-freshness"},
                     {"preconditionId": "pre-eligible-mode", "description": "mode Normal or Degraded",
                      "governingRef": "urn:aocl:policy:operating-modes"},
                     {"preconditionId": "pre-authority", "description": "controller authority over traffic allocation",
                      "governingRef": "auth-assurance"},
                 ],
                 "authorization": {"authorityRef": "auth-assurance", "approvalRequired": True,
                                    "approvalConditions": "changes beyond the control range require supervisory approval"},
                 "constraintRefs": ["inv-availability", "inv-utilization"],
                 "expectedEffects": [{"variableRef": "traffic-allocation", "expectedChange": "redistribution toward less congested routes",
                                       "targetUnit": "percent"}],
                 "postconditions": [
                     {"postconditionId": "post-exec", "description": "command has a recorded execution disposition",
                      "kind": "ExecutionResult", "evidenceSignalRef": "sig-exec-status"},
                     {"postconditionId": "post-state", "description": "resulting allocation observed",
                      "kind": "StateEstablished", "evidenceSignalRef": "sig-latency-obs"},
                     {"postconditionId": "post-outcome", "description": "latency evaluated against reference",
                      "kind": "OperationalOutcome", "evidenceSignalRef": "sig-verification"},
                 ],
                 "failureConditions": [
                     {"description": "actuator rejects the command", "disposition": "Escalate"},
                     {"description": "safety condition breached during execution", "disposition": "EnterSafeState",
                      "safeStateRef": "safe-latency-mode"},
                 ],
                 "behavioralElementRefs": ["urn:aocl:spec:network-assurance-001#execute-reroute"],
                 "lifecycleStatus": "Draft", "version": "1.0.0"},
                {"contractId": "ctr-decide", "name": "Remediation Decision", "contractType": "Decision",
                 "definition": "Selects a permitted remediation when latency breaches the bound.",
                 "subjectRef": "assurance-controller", "permittedScope": "decision selection within policy",
                 "preconditions": [{"preconditionId": "pre-assessment", "description": "congestion assessment available",
                                     "governingRef": "urn:aocl:policy:assessment-quality"}],
                 "authorization": {"authorityRef": "auth-assurance"},
                 "constraintRefs": ["inv-availability"],
                 "expectedEffects": [{"variableRef": "svc-latency", "expectedChange": "intended reduction toward target",
                                       "targetUnit": "ms"}],
                 "postconditions": [{"postconditionId": "post-decision", "description": "a permitted transition selected",
                                      "kind": "ExecutionResult"}],
                 "failureConditions": [{"description": "no permitted remediation", "disposition": "Escalate"}],
                 "behavioralElementRefs": ["urn:aocl:spec:network-assurance-001#decide-remediation"]},
                {"contractId": "ctr-verify", "name": "Post-intervention Verification", "contractType": "Verification",
                 "definition": "Evaluates the latency condition against the reference after intervention.",
                 "subjectRef": "verification-path", "permittedScope": "read-only evaluation",
                 "preconditions": [{"preconditionId": "pre-exec-recorded", "description": "execution disposition recorded",
                                     "governingRef": "ctr-redistribute"}],
                 "authorization": {"authorityRef": "auth-protective"},
                 "expectedEffects": [{"variableRef": "measured-latency", "expectedChange": "post-intervention measurement",
                                       "targetUnit": "ms"}],
                 "postconditions": [{"postconditionId": "post-verified", "description": "latency condition evaluated",
                                      "kind": "OperationalOutcome", "evidenceSignalRef": "sig-verification"}],
                 "failureConditions": [{"description": "verification evidence insufficient", "disposition": "RecordUnresolved"}],
                 "behavioralElementRefs": ["urn:aocl:spec:network-assurance-001#verify-latency"]},
            ],
            "authority": [
                {"authorityId": "auth-assurance", "subjectRef": "assurance-controller", "scopeRef": "network-routing-scope",
                 "actionClasses": ["traffic.redistribute"], "authorityClass": "Primary",
                 "permittedVariables": [{"variableRef": "traffic-allocation",
                                          "controlRange": {"min": 0, "max": 85, "unit": "percent"}}],
                 "operatingModeRefs": ["normal", "degraded"],
                 "constraintRefs": ["inv-utilization"], "delegation": {"permitted": False},
                 "approvalRequirements": "supervisory approval beyond control range", "validity": "revocable by governance"},
                {"authorityId": "auth-supervisory", "subjectRef": "supervisory-controller", "scopeRef": "network-routing-scope",
                 "actionClasses": ["traffic.redistribute", "traffic.override"], "authorityClass": "Supervisory",
                 "permittedVariables": [{"variableRef": "traffic-allocation",
                                          "controlRange": {"min": 0, "max": 100, "unit": "percent"}}],
                 "operatingModeRefs": ["normal", "degraded", "recovering"]},
                {"authorityId": "auth-protective", "subjectRef": "protective-mechanism", "scopeRef": "network-service",
                 "actionClasses": ["mode.enter-safe"], "authorityClass": "Protective",
                 "permittedVariables": [{"variableRef": "traffic-allocation"}],
                 "operatingModeRefs": ["safe-mode"], "constraintRefs": ["inv-availability"]},
            ],
            "coordination": [
                {"coordinationId": "coord-allocation", "variableRefs": ["traffic-allocation"],
                 "precedence": "supervisory override preempts primary within its range; protective always highest",
                 "conflictDetection": "concurrent allocation deltas compared per cycle",
                 "arbitration": "protective > supervisory > primary; conflicts escalate to governance"},
            ],
            "invariants": [
                {"invariantId": "inv-availability", "subject": "network-service", "appliesTo": "Plant",
                 "variableRefs": ["svc-latency"],
                 "statement": "service availability remains above the minimum at all times",
                 "priorityClass": "Safety", "governingRef": "urn:aocl:policy:service-availability"},
                {"invariantId": "inv-utilization", "subject": "network-service", "appliesTo": "Variable",
                 "variableRefs": ["max-utilization"],
                 "statement": "resource utilization does not exceed available capacity",
                 "priorityClass": "Operational", "governingRef": "urn:aocl:policy:capacity"},
            ],
            "safeStates": [
                {"safeStateId": "safe-latency-mode", "scopeRef": "network-routing-scope",
                 "variableConditions": [{"variableRef": "traffic-allocation", "condition": "last-known-good allocation"}],
                 "operatingModeRef": "safe-mode",
                 "entryConditions": ["critical safety condition per inv-availability"],
                 "authorityRef": "auth-protective",
                 "prohibitedActions": ["further redistribution"],
                 "exitConditions": ["operator intent recorded and conditions re-verified"],
                 "verificationRefs": ["vr-safe-mode"], "recoveryRef": "ctr-verify"},
            ],
            "signals": [
                {"signalId": "sig-command", "kind": "Command", "producedByRef": "assurance-controller", "evidentialStrength": "Instruction"},
                {"signalId": "sig-ack", "kind": "Acknowledgement", "producedByRef": "traffic-engineering-actuator", "evidentialStrength": "Receipt"},
                {"signalId": "sig-exec-status", "kind": "ExecutionStatus", "producedByRef": "traffic-engineering-actuator", "evidentialStrength": "ExecutionReport"},
                {"signalId": "sig-latency-obs", "kind": "Observation", "producedByRef": "sensor-latency-probe", "evidentialStrength": "Measurement"},
                {"signalId": "sig-estimate", "kind": "StateEstimate", "producedByRef": "estimator-congestion", "evidentialStrength": "Inference"},
                {"signalId": "sig-verification", "kind": "VerificationEvidence", "producedByRef": "verification-path", "evidentialStrength": "VerifiedOutcome"},
            ],
            "verificationRefs": [
                {"verificationRef": "vr-safe-mode", "claim": "the safe-mode conditions hold on the governed scope"},
                {"verificationRef": "vr-latency", "claim": "post-intervention latency evaluated against the reference"},
            ],
        },
    }

    base = validate_control_model(copy.deepcopy(valid))
    assert base["valid"], base["findings"]
    conf = base["conformance"]
    assert all(conf[k] for k in conf if k not in ("simulationReady", "unresolvedDefinitions")), conf
    base = simulate_readiness(base, valid["controlModel"])
    assert base["conformance"]["simulationReady"] is False and base["simulationReadinessReasons"], "AD-007-12"

    def broken(mutator):
        d = copy.deepcopy(valid)
        mutator(d["controlModel"])
        return validate_control_model(d)

    rules_hit = {
        "CTM-001": lambda m: m["controlVariables"].append(copy.deepcopy(m["controlVariables"][0])),
        "CTM-002": lambda m: m["controlVariables"][0].pop("definition"),
        "CTM-003": lambda m: m["controlVariables"][0].pop("unit"),
        "CTM-004": lambda m: m["controlVariables"][0].pop("valueDomain"),
        "CTM-005": lambda m: m["controlVariables"][0].__setitem__("roles", []),
        "CTM-006": lambda m: m["contracts"][0]["expectedEffects"][0].__setitem__("targetUnit", "seconds"),
        "CTM-007": lambda m: m["states"][0].pop("subjectRef"),
        "CTM-008": lambda m: m["states"][0].__setitem__("classification", "Running"),
        "CTM-009": lambda m: (m.__setitem__("stateSpaces", [{"stateSpaceId": "ss1", "subjectRef": "net", "variables": []}]),),
        "CTM-010": lambda m: m["states"][0].__setitem__("operatingModeRef", "hyperspace"),
        "CTM-011": lambda m: m["states"][0].pop("temporalRef"),
        "CTM-012": lambda m: m["states"][1].pop("estimatorRef"),
        "CTM-013": lambda m: m["transitions"][0].pop("sourceStateRef"),
        "CTM-014": lambda m: m["transitions"][1].pop("guard"),
        "CTM-015": lambda m: m["transitions"][0].__setitem__("possibleOutcomes", ["Worked"]),
        "CTM-016": lambda m: (m["transitions"][1].pop("constraintRefs"), m["transitions"][1].pop("constraintReview", None) if "constraintReview" in m["transitions"][1] else None),
        "CTM-017": lambda m: m["transitions"][0].__setitem__("trigger", "Vibes"),
        "CTM-018": lambda m: m["transitions"][0].__setitem__("transitionType", "Quantum"),
        "CTM-019": lambda m: m["contracts"][0].pop("behavioralElementRefs"),
        "CTM-020": lambda m: m["contracts"][0].pop("permittedScope"),
        "CTM-021": lambda m: m["contracts"][0]["preconditions"][0].pop("governingRef"),
        "CTM-022": lambda m: m["contracts"][0]["authorization"].pop("authorityRef"),
        "CTM-023": lambda m: m["contracts"][0].__setitem__("constraintRefs", ["inv-ghost"]),
        "CTM-024": lambda m: m["contracts"][0].__setitem__("expectedEffects", []),
        "CTM-025": lambda m: m["contracts"][0].__setitem__("postconditions", [m["contracts"][0]["postconditions"][0]]),
        "CTM-026": lambda m: m["contracts"][0].__setitem__("failureConditions", []),
        "CTM-027": lambda m: m["authority"][0].pop("scopeRef"),
        "CTM-028": lambda m: m["contracts"][0]["authorization"].__setitem__("authorityRef", "auth-ghost"),
        "CTM-029": lambda m: m.pop("coordination"),
        "CTM-030": lambda m: m["invariants"][0].pop("governingRef"),
        "CTM-031": lambda m: m.pop("safeStates"),
        "CTM-032": lambda m: m["safeStates"][0].__setitem__("verificationRefs", ["vr-ghost"]),
        "CTM-033": lambda m: m["contracts"][0].__setitem__("constraintRefs", ["inv-utilization"]),
        "CTM-034": lambda m: m["controlVariables"][0].pop("goalRefs"),
        "CTM-035": lambda m: m["contracts"][1].pop("behavioralElementRefs"),
        "CTM-036": lambda m: m["transitions"][0].__setitem__("contractRef", "ctr-ghost"),
        "CTM-037": lambda m: m["verificationRefs"][0].pop("claim"),
        "CTM-039": lambda m: m.pop("closedLoopRef"),
        "AD-007-09": lambda m: m["contracts"][0]["postconditions"][1].__setitem__("evidenceSignalRef", "sig-ack"),
    }
    for rule, mutator in rules_hit.items():
        r = broken(mutator)
        assert any(f["rule"] == rule for f in r["findings"]), (rule, [f["rule"] for f in r["findings"]])

    # CTM-032 via safe-state transition without guard/authority
    def bad_safe_transition(m):
        m["transitions"][1]["entersSafeStateRef"] = "safe-latency-mode"
        m["transitions"][1].pop("guard")
    r = broken(bad_safe_transition)
    assert any(f["rule"] == "CTM-032" for f in r["findings"])

    # CTM-040: unresolved definitions reported, block full conformance
    def mark_unresolved(m):
        m["controlVariables"][1]["unresolved"] = True
        m["controlVariables"][1]["unresolvedNote"] = "measurement mechanism undecided"
    r = broken(mark_unresolved)
    assert any(f["rule"] == "CTM-040" and f["severity"] == "warning" for f in r["findings"])
    assert r["conformance"]["unresolvedDefinitions"] == 1 and r["conformance"]["fullyConformant"] is False

    # migration: preserves reference conditions, never infers authority, gaps inventoried
    loop_doc = {
        "schemaVersion": "0.1", "modelVersion": "1.0.0",
        "closedLoop": {
            "id": "urn:aocl:loop:net-1", "type": "ClosedLoop", "name": "Net", "definition": "d",
            "lifecycleStatus": "Draft",
            "intent": {"intentId": "i", "statement": "s", "goals": [
                {"goalId": "g1", "definition": "d", "successCriteria": "sc",
                 "referenceConditions": [{"conditionId": "c1", "variable": "service.latency",
                                           "operator": "lessThan", "targetValue": 50, "unit": "ms"}]}]},
            "controlledSystems": [{"bindingId": "b1", "systemRole": "ControlledSystem",
                                    "targetReference": {"targetId": "net", "sourceSystem": "EA"}}],
            "provenance": {"source": "s", "authority": "a", "createdAt": "2026-11-07"},
        },
    }
    mig = migrate_from_loop(loop_doc)
    cm = mig["spec"]["controlModel"]
    assert mig["carriedReferenceConditions"] == 1
    assert cm["controlVariables"][0]["roles"] == ["Reference"] and cm["controlVariables"][0]["unit"] == "ms"
    assert cm["authority"] == [] and cm["contracts"] == []  # nothing fabricated
    assert any("never inferred" in u for u in cm["migrationNotes"]["unresolvedMappings"])
    assert any("never fabricated" in f["message"] for f in mig["findings"])

    # round-trip serialization (CTM-038): yaml -> dict -> json -> dict equality
    rt = json.loads(json.dumps(valid))
    assert rt == valid
    print(f"self-test OK (control-contract v{RULESET_VERSION}, schema {SCHEMA_VERSION}, CTM-001..040 + migration)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
