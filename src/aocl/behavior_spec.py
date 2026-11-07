"""AOCL canonical behavioral specification (AOCL-CR-006): load, validate, migrate.

Implements validation rules BSS-001..036 natively (stdlib + pyyaml) and the four
conformance levels of CR-006 §17 — schema, structural, behavioral and simulation
readiness are reported separately (BSS-035/036): a specification can be
schema-conformant without being behaviorally complete, and behaviorally complete
without being simulation-ready (control contracts CR-007 and scenario bindings
CR-009 are readiness prerequisites, not conformance prerequisites).

Carries the ADR-007 decision-3 measurement anchors: human participation
declarations are the E anchor (manual touch per stage); control-architecture
component and fusion/dependency declarations are the C anchors (structural,
dynamic, semantic, coupling); observation-quality declarations are the V_d
anchor. Dangling anchor references are errors (rule ADR-007-ANCHOR).

Also migrates existing loop registrations + model/behavior.yaml policy semantics
into Draft specification skeletons (CR-006 §20): decision-model selections are
preserved as decisionArchitectureRef; stage mappings stay unresolved (Required,
never Realized); no conditions, inputs, outputs or exception paths are
fabricated — gaps are inventoried as findings.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("error: pyyaml is required for the behavioral spec (pip install pyyaml)")

RULESET_VERSION = "1.0.0"
SCHEMA_VERSION = "0.1"

LIFECYCLE = ("Draft", "InReview", "Approved", "Deprecated", "Retired")
STAGES = ("Intent", "Observe", "Analyze", "Decide", "Execute", "Verify", "Learn")
SUBSTANTIVE_TYPES = {"IntentReference", "Observation", "Analysis", "Assessment", "Decision",
                     "Approval", "Action", "Verification", "Learning", "Escalation",
                     "ExceptionHandler", "SafeState", "SubSpecification"}
ELEMENT_TYPES = set(SUBSTANTIVE_TYPES) | {"Event", "Condition", "Wait", "Synchronization"}
RELATIONSHIP_TYPES = {"FlowsTo", "BranchesTo", "Triggers", "DependsOn", "ExecutesInParallelWith",
                      "SynchronizesWith", "RepeatsTo", "ReturnsTo", "EscalatesTo", "HandlesException",
                      "TerminatesWith", "Invokes"}
TERMINATION_OUTCOMES = {"SuccessfulCompletion", "VerifiedCompletion", "ControlledTermination",
                        "Cancellation", "Escalation", "SafeStateTransition", "Failure", "Suspended"}
SYNC_PATTERNS = {"WaitForAll", "WaitForAny", "WaitForSubset", "Conditional", "Timeout"}
EXCEPTION_CATEGORIES = {"ObservationFailure", "DataQualityFailure", "AnalysisFailure", "DecisionFailure",
                        "AuthorizationFailure", "ExecutionFailure", "VerificationFailure", "Timeout",
                        "DependencyFailure", "ConstraintViolation", "UnexpectedState",
                        "ExternalServiceFailure", "HumanInterventionRequired"}

SEMVER = re.compile(r"^\d+\.\d+\.\d+$")
SPEC_URN = re.compile(r"^urn:aocl:spec:[a-z0-9][a-z0-9-]*$")
LOOP_URN = re.compile(r"^urn:aocl:loop:[a-z0-9][a-z0-9-]*$")

# Conformance rule grouping (CR-006 §17): schema-level structure first, then
# referential integrity (structural), then behavioral adequacy.
SCHEMA_RULES = {"BSS-001", "BSS-002", "BSS-003", "BSS-006", "BSS-008", "BSS-011", "BSS-013",
                "BSS-033", "BSS-034", "BSS-035"}
STRUCTURAL_RULES = {"BSS-005", "BSS-012", "BSS-019", "BSS-020", "BSS-021", "BSS-033"}
BEHAVIORAL_RULES = {"BSS-004", "BSS-007", "BSS-009", "BSS-010", "BSS-014", "BSS-015", "BSS-016",
                    "BSS-017", "BSS-018", "BSS-022", "BSS-023", "BSS-024", "BSS-025", "BSS-026",
                    "BSS-027", "BSS-028", "BSS-029", "BSS-030", "BSS-031", "BSS-032", "ADR-007-ANCHOR"}


def _f(findings: list, rule: str, severity: str, message: str) -> None:
    findings.append({"rule": rule, "severity": severity, "message": message})


def validate_behavioral_spec(data: dict) -> dict:
    """Validate a canonical BehavioralSpecification document against BSS-001..036
    plus the ADR-007 anchor-integrity rule. Returns findings and the four
    conformance flags (schema / structural / behavioral / simulation readiness)."""
    findings: list[dict] = []

    if not isinstance(data, dict):
        _f(findings, "BSS-035", "error", "document must be a mapping")
        return _result(findings)
    if data.get("schemaVersion") != SCHEMA_VERSION:
        _f(findings, "BSS-035", "error",
           f"schemaVersion must be '{SCHEMA_VERSION}' (this validator's contract), got {data.get('schemaVersion')!r}")
    if not SEMVER.match(str(data.get("specVersion", ""))):
        _f(findings, "BSS-003", "error", f"specVersion must be semver (independent version, BSS-003), got {data.get('specVersion')!r}")

    known_root = {"schemaVersion", "specVersion", "behavioralSpecification"}
    unknown_root = set(data) - known_root
    if unknown_root:
        _f(findings, "BSS-035", "error", f"unknown document attributes: {sorted(unknown_root)}")

    spec = data.get("behavioralSpecification")
    if not isinstance(spec, dict):
        _f(findings, "BSS-001", "error", "behavioralSpecification missing")
        return _result(findings)

    # ---- BSS-001 identity / BSS-002 context binding / BSS-034 lifecycle
    if not SPEC_URN.match(str(spec.get("id", ""))):
        _f(findings, "BSS-001", "error",
           "behavioralSpecification.id must match urn:aocl:spec:<slug> (stable, opaque; BSS-001)")
    if spec.get("type") != "BehavioralSpecification":
        _f(findings, "BSS-001", "error", "behavioralSpecification.type must be 'BehavioralSpecification'")
    if not str(spec.get("name", "")).strip():
        _f(findings, "BSS-001", "error", "behavioralSpecification.name is mandatory")
    if not str(spec.get("definition", "")).strip():
        _f(findings, "BSS-001", "error", "behavioralSpecification.definition is mandatory")

    clr = spec.get("closedLoopRef")
    if not isinstance(clr, dict) or not LOOP_URN.match(str(clr.get("loopId", ""))) \
            or not str(clr.get("sourceSystem", "")).strip():
        _f(findings, "BSS-002", "error",
           "closedLoopRef must identify the associated ClosedLoop (urn:aocl:loop:<slug>) and its source system (BSS-002)")

    status = spec.get("lifecycleStatus")
    if status not in LIFECYCLE:
        _f(findings, "BSS-034", "error", f"lifecycleStatus must be one of {LIFECYCLE}, got {status!r} (specification lifecycle, not runtime — §15)")
    gov = spec.get("governance")
    if not isinstance(gov, dict) or "approvalRequired" not in gov:
        _f(findings, "BSS-034", "error", "governance must be present with approvalRequired (BSS-034)")
    elif status == "Approved" and (not str(gov.get("approvedBy", "")).strip() or not str(gov.get("approvalDate", "")).strip()):
        _f(findings, "BSS-034", "error", "an Approved specification must carry approvedBy and approvalDate (BSS-034)")
    dar = spec.get("decisionArchitectureRef")
    if dar is not None and (dar.get("kind") not in ("OODA", "MAPE", "CUSTOM") or not str(dar.get("source", "")).strip()):
        _f(findings, "BSS-035", "error", "decisionArchitectureRef must carry a governed kind (OODA/MAPE/CUSTOM) and its source (§20)")

    known_spec = {"id", "type", "name", "definition", "description", "lifecycleStatus", "closedLoopRef",
                  "decisionArchitectureRef", "objectives", "stageCoverage", "entry", "termination",
                  "elements", "relationships", "conditions", "informationDependencies", "policyRefs",
                  "humanParticipation", "exceptions", "safeStates", "verificationRefs", "learningBoundaries",
                  "measurementAnchors", "traceability", "controlContractBindings", "scenarioBindings",
                  "governance", "migrationNotes"}
    unknown_spec = set(spec) - known_spec
    if unknown_spec:
        _f(findings, "BSS-035", "error", f"behavioralSpecification: unknown attributes {sorted(unknown_spec)}")

    # ---- BSS-004 objectives
    objectives = spec.get("objectives")
    if not isinstance(objectives, list) or not objectives:
        _f(findings, "BSS-004", "error", "behavioral objectives must be declared (BSS-004)")
        objectives = []
    objective_ids = []
    for i, obj in enumerate(objectives):
        if not isinstance(obj, dict):
            _f(findings, "BSS-004", "error", f"objectives[{i}] must be a mapping")
            continue
        oid = obj.get("objectiveId", f"objectives[{i}]")
        objective_ids.append(oid)
        if not str(obj.get("objectiveId", "")).strip() or not str(obj.get("description", "")).strip():
            _f(findings, "BSS-004", "error", f"objective {oid}: id and description are mandatory (BSS-004)")
        if not str(obj.get("goalRef", "")).strip():
            _f(findings, "BSS-032", "error", f"objective {oid}: goalRef missing — objectives must trace to intent/goals (BSS-032)")
    if len(objective_ids) != len(set(objective_ids)):
        _f(findings, "BSS-005", "error", "duplicate objectiveIds")

    # ---- BSS-008/009 stage coverage
    coverage = spec.get("stageCoverage")
    by_stage: dict = {}
    if not isinstance(coverage, list):
        _f(findings, "BSS-008", "error", "stageCoverage must be an array over the seven canonical responsibilities")
        coverage = []
    for i, sc in enumerate(coverage):
        if not isinstance(sc, dict) or sc.get("stage") not in STAGES:
            _f(findings, "BSS-008", "error", f"stageCoverage[{i}]: stage must be one of {STAGES}")
            continue
        st = sc.get("status")
        if st not in ("Required", "Realized", "PartiallyRealized", "NotApplicable", "Deferred"):
            _f(findings, "BSS-008", "error", f"stageCoverage[{sc['stage']}]: invalid status {st!r}")
        if st == "NotApplicable" and not str(sc.get("justification", "")).strip():
            _f(findings, "BSS-009", "error", f"stageCoverage[{sc['stage']}]: NotApplicable requires justification (BSS-009)")
        by_stage[sc["stage"]] = st
    missing_stages = [s for s in STAGES if s not in by_stage]
    if missing_stages:
        _f(findings, "BSS-008", "error", f"stageCoverage must declare all seven responsibilities; missing: {missing_stages}")

    # ---- BSS-010/011 entry + termination
    entry = spec.get("entry")
    entry_conditions = entry.get("conditions") if isinstance(entry, dict) else None
    if not isinstance(entry_conditions, list) or not entry_conditions:
        _f(findings, "BSS-010", "error", "entry conditions must be identified (BSS-010)")
    term = spec.get("termination")
    outcomes = term.get("outcomes") if isinstance(term, dict) else None
    if not isinstance(outcomes, list) or not outcomes:
        _f(findings, "BSS-011", "error", "termination outcomes must be identified (BSS-011)")
    else:
        bad = [o for o in outcomes if o not in TERMINATION_OUTCOMES]
        if bad:
            _f(findings, "BSS-011", "error", f"termination outcomes invalid: {bad}")

    # ---- elements (BSS-005/006/007) + referential index
    elements = spec.get("elements")
    element_ids: list = []
    elements_by_id: dict = {}
    produced: set = set()
    declared_info: set = set()
    condition_ids: set = set()
    participation_ids: set = set()
    architecture_refs: set = set()
    multi_output: dict = {}
    if not isinstance(elements, list) or not elements:
        _f(findings, "BSS-005", "error", "at least one behavioral element is required (BSS-005)")
        elements = []
    for el in elements:
        if not isinstance(el, dict):
            _f(findings, "BSS-005", "error", f"elements entry must be a mapping, got {type(el).__name__}")
            continue
        eid = el.get("id", "<missing>")
        element_ids.append(eid)
        elements_by_id[eid] = el
        if not str(el.get("id", "")).strip() or len(str(eid)) < 3:
            _f(findings, "BSS-005", "error", f"element id missing or too short (BSS-005): {eid!r}")
        etype = el.get("type")
        if etype not in ELEMENT_TYPES:
            _f(findings, "BSS-006", "error",
               f"element {eid}: type {etype!r} is not in the canonical vocabulary (BSS-006); "
               "extensions must be governed and must not redefine canonical semantics")
        if etype in SUBSTANTIVE_TYPES:
            stages = el.get("stages")
            if not isinstance(stages, list) or not stages:
                _f(findings, "BSS-007", "error", f"element {eid}: substantive elements must map to canonical stages (BSS-007)")
            else:
                bad = [s for s in stages if s not in STAGES]
                if bad:
                    _f(findings, "BSS-007", "error", f"element {eid}: invalid stage(s) {bad}")
        if "grantsAuthority" in el or "autoAuthorize" in el:
            _f(findings, "BSS-023", "error",
               f"element {eid}: carries a self-granted authority attribute — authority is a property of the "
               "governed control architecture and authorization model, never of an element's existence (BSS-023)")
        for out in el.get("outputs", []) or []:
            produced.add(out)
            multi_output.setdefault(out, []).append(eid)
        car = el.get("controlArchitectureRef") or {}
        for v in car.values():
            architecture_refs.add(v)
        if etype == "Wait":
            if not str(el.get("resumeEventRef", "")).strip() and not str(el.get("resumeConditionRef", "")).strip():
                _f(findings, "BSS-018", "error",
                   f"element {eid}: Wait must identify the event or condition that resumes the suspended path (BSS-018, §8.7)")
        if etype == "Synchronization":
            if el.get("syncPattern") not in SYNC_PATTERNS:
                _f(findings, "BSS-017", "error", f"element {eid}: Synchronization must declare its coordination pattern (BSS-017)")
            elif el.get("syncPattern") == "WaitForSubset" and not el.get("syncSubsetSize"):
                _f(findings, "BSS-017", "error", f"element {eid}: WaitForSubset requires syncSubsetSize (BSS-017)")
            elif el.get("syncPattern") == "Timeout" and not str(el.get("syncTimeoutConditionRef", "")).strip():
                _f(findings, "BSS-017", "error", f"element {eid}: Timeout synchronization requires syncTimeoutConditionRef (BSS-017)")
        if etype == "SubSpecification" and not str(el.get("invokedSpecRef", "")).strip():
            _f(findings, "BSS-006", "error", f"element {eid}: SubSpecification must reference a separately governed specification (§7.2)")
    if len(element_ids) != len(set(element_ids)):
        _f(findings, "BSS-005", "error", "duplicate element ids (BSS-005)")
    for out, producers in multi_output.items():
        if len(producers) > 1:
            findings.append({"rule": "BSS-019", "severity": "warning",
                             "message": f"information {out!r} is produced by multiple elements ({producers}) — "
                                        "outputs must be traceable to their producing element (§10.2)"})

    # ---- conditions (BSS-021)
    conditions = spec.get("conditions") or []
    if not isinstance(conditions, list):
        _f(findings, "BSS-021", "error", "conditions must be an array")
        conditions = []
    for c in conditions:
        cid = c.get("conditionId", "<missing>") if isinstance(c, dict) else "<missing>"
        if not isinstance(c, dict):
            _f(findings, "BSS-021", "error", f"condition {cid} must be a mapping")
            continue
        condition_ids.add(cid)
        if not str(c.get("conditionId", "")).strip() or len(str(cid)) < 3:
            _f(findings, "BSS-021", "error", f"condition: stable identifier missing (BSS-021/§9.1)")
        if not str(c.get("evaluationContext", "")).strip():
            _f(findings, "BSS-021", "error",
               f"condition {cid}: explicit definition and evaluation context are mandatory (BSS-021)")
        if c.get("category") == "Composite" and not c.get("memberConditionRefs"):
            _f(findings, "BSS-021", "error", f"condition {cid}: composite conditions must reference member conditions (§9.3)")
    dangling_entry = [c for c in (entry_conditions or []) if c not in condition_ids]
    if dangling_entry:
        _f(findings, "BSS-012", "error", f"entry conditions do not resolve: {dangling_entry}")

    # ---- information dependencies (BSS-019/020)
    info_deps = spec.get("informationDependencies") or []
    if not isinstance(info_deps, list):
        _f(findings, "BSS-020", "error", "informationDependencies must be an array")
        info_deps = []
    dep_ids = []
    for d in info_deps:
        if not isinstance(d, dict):
            _f(findings, "BSS-020", "error", "information dependency entries must be mappings")
            continue
        did = d.get("informationId", "<missing>")
        dep_ids.append(did)
        declared_info.add(did)
        if not str(d.get("informationId", "")).strip() or len(str(did)) < 3:
            _f(findings, "BSS-020", "error", "information dependency: stable id missing (BSS-020)")
        if d.get("kind") not in ("Required", "Optional", "Conditional", "PotentiallyStale", "Derived", "IndependentlyVerified"):
            _f(findings, "BSS-020", "error", f"information dependency {did}: kind {d.get('kind')!r} invalid (§10.3)")
        if d.get("kind") in ("PotentiallyStale", "IndependentlyVerified") and not isinstance(d.get("quality"), dict):
            _f(findings, "BSS-020", "error",
               f"information dependency {did}: kind {d.get('kind')} requires a quality declaration "
               "(freshness/staleness/independent verification — §10.3, the V_d anchor)")
    if len(dep_ids) != len(set(dep_ids)):
        _f(findings, "BSS-020", "error", "duplicate informationDependency ids")
    undeclared_outputs = sorted(produced - declared_info)
    if undeclared_outputs:
        _f(findings, "BSS-020", "error",
           f"element outputs not declared as information dependencies: {undeclared_outputs} (BSS-020)")

    # element input resolution (structural, BSS-019)
    for eid, el in elements_by_id.items():
        for inp in el.get("inputs", []) or []:
            if inp not in produced and inp not in declared_info:
                _f(findings, "BSS-019", "error",
                   f"element {eid}: input {inp!r} resolves to no element output nor declared dependency (BSS-019)")

    # ---- relationships (BSS-012/013/014/015/016/017/033)
    rels = spec.get("relationships")
    rel_ids = []
    if not isinstance(rels, list) or not rels:
        _f(findings, "BSS-012", "error", "behavioral relationships (the directed graph) are mandatory")
        rels = []
    for r in rels:
        if not isinstance(r, dict):
            _f(findings, "BSS-012", "error", "relationship entries must be mappings")
            continue
        rid = r.get("relationshipId", "<missing>")
        rel_ids.append(rid)
        rtype = r.get("type")
        if not str(r.get("relationshipId", "")).strip():
            _f(findings, "BSS-033", "error", f"relationship {rid}: relationshipId missing (BSS-033)")
        if rid in element_ids:
            _f(findings, "BSS-033", "error", f"relationship id {rid!r} collides with an element id — structural and behavioral namespaces must remain distinguishable (BSS-033)")
        if rtype not in RELATIONSHIP_TYPES:
            _f(findings, "BSS-013", "error", f"relationship {rid}: type {rtype!r} has no defined behavioral semantics (BSS-013)")
        for end_name in ("source", "target"):
            if r.get(end_name) not in elements_by_id:
                _f(findings, "BSS-012", "error", f"relationship {rid}: {end_name} {r.get(end_name)!r} is not a behavioral element (BSS-012)")
        if rtype == "BranchesTo" and not str(r.get("conditionRef", "")).strip():
            _f(findings, "BSS-014", "error", f"relationship {rid}: BranchesTo requires an explicit governing condition (BSS-014)")
        if r.get("conditionRef") and r["conditionRef"] not in condition_ids:
            _f(findings, "BSS-012", "error", f"relationship {rid}: conditionRef {r['conditionRef']!r} does not resolve")
        if rtype == "RepeatsTo" and not str(r.get("conditionRef", "")).strip():
            _f(findings, "BSS-015", "error",
               f"relationship {rid}: RepeatsTo must identify its governing condition or termination criterion (BSS-015, §8.5)")
        if rtype == "ExecutesInParallelWith" and not str(r.get("parallelGroup", "")).strip():
            _f(findings, "BSS-016", "error", f"relationship {rid}: ExecutesInParallelWith requires a parallelGroup (BSS-016)")
        if rtype == "SynchronizesWith":
            if r.get("syncPattern") not in SYNC_PATTERNS:
                _f(findings, "BSS-017", "error", f"relationship {rid}: SynchronizesWith must declare its coordination requirement (BSS-017)")
            elif r.get("syncPattern") == "WaitForSubset" and not r.get("syncSubsetSize"):
                _f(findings, "BSS-017", "error", f"relationship {rid}: WaitForSubset requires syncSubsetSize (BSS-017)")
        if rtype == "TerminatesWith" and r.get("terminationOutcome") not in TERMINATION_OUTCOMES:
            _f(findings, "BSS-011", "error", f"relationship {rid}: TerminatesWith requires a canonical termination outcome (§8.3)")
        if rtype == "Invokes":
            src = elements_by_id.get(r.get("source"), {})
            if src.get("type") != "SubSpecification":
                _f(findings, "BSS-012", "error", f"relationship {rid}: Invokes must originate from a SubSpecification element (§7.2)")
    if len(rel_ids) != len(set(rel_ids)):
        _f(findings, "BSS-033", "error", "duplicate relationshipIds")

    # ---- policy references (BSS-022/023)
    policy_refs = spec.get("policyRefs") or []
    if not isinstance(policy_refs, list):
        _f(findings, "BSS-022", "error", "policyRefs must be an array")
        policy_refs = []
    authorized_by_targets: set = set()
    for p in policy_refs:
        if not isinstance(p, dict):
            _f(findings, "BSS-022", "error", "policyRef entries must be mappings")
            continue
        pid = p.get("policyRefId", "<missing>")
        if not str(p.get("policyRefId", "")).strip() or not str(p.get("targetRef", "")).strip():
            _f(findings, "BSS-022", "error", f"policyRef {pid}: stable id and governed targetRef are mandatory (BSS-022/§11)")
        if p.get("relationship") not in ("SubjectTo", "AuthorizedBy", "ConstrainedBy", "Informs"):
            _f(findings, "BSS-022", "error", f"policyRef {pid}: relationship {p.get('relationship')!r} invalid (§11)")
        if p.get("relationship") == "AuthorizedBy":
            for t in p.get("appliesToRefs", []) or []:
                authorized_by_targets.add(t)
        if p.get("resolved") is False and not str(p.get("resolutionNote", "")).strip():
            _f(findings, "BSS-022", "error",
               f"policyRef {pid}: unresolved references must be explicitly marked with a resolutionNote (BSS-022)")
    for eid, el in elements_by_id.items():
        if el.get("type") == "Action" and eid not in authorized_by_targets:
            _f(findings, "BSS-023", "error",
               f"element {eid}: Action is not covered by an AuthorizedBy policy reference — an Action element's "
               "existence grants no authority; authority must be explicit in the governed authorization model (BSS-023, §11)")

    # ---- human participation (BSS-024) + E anchor material
    hp = spec.get("humanParticipation") or []
    if not isinstance(hp, list):
        _f(findings, "BSS-024", "error", "humanParticipation must be an array")
        hp = []
    for h in hp:
        if not isinstance(h, dict):
            _f(findings, "BSS-024", "error", "humanParticipation entries must be mappings")
            continue
        hid = h.get("participationId", "<missing>")
        participation_ids.add(hid)
        if not str(h.get("participationId", "")).strip():
            _f(findings, "BSS-024", "error", "humanParticipation: stable id missing")
        kind = h.get("participationKind")
        if kind not in ("Approval", "Notification", "Intervention", "Verification"):
            _f(findings, "BSS-024", "error", f"human participation {hid}: participationKind {kind!r} invalid (BSS-024)")
        if kind == "Approval":
            if h.get("role") not in ("Approver", "DecisionMaker", "Supervisor", "VerificationAuthority"):
                _f(findings, "BSS-024", "error",
                   f"human participation {hid}: an Approval requires an authorization-bearing role, got {h.get('role')!r} (BSS-024)")
            if not str(h.get("timeoutConditionRef", "")).strip() and not str(h.get("fallbackRef", "")).strip():
                _f(findings, "BSS-024", "error",
                   f"human participation {hid}: approvals require timeout/escalation/fallback behavior when no response arrives (§12)")
        if kind == "Notification" and h.get("role") == "Approver":
            _f(findings, "BSS-024", "error",
               f"human participation {hid}: an Approver cannot be a mere Notification — approval and "
               "notification must be distinguishable (BSS-024)")
    for eid, el in elements_by_id.items():
        if el.get("type") == "Approval" and not (el.get("participationRefs") or []):
            _f(findings, "BSS-024", "error",
               f"element {eid}: Approval elements must link their humanParticipation entry (BSS-024)")
        for pref in el.get("participationRefs", []) or []:
            if pref not in participation_ids:
                _f(findings, "BSS-012", "error", f"element {eid}: participationRef {pref!r} does not resolve")

    # ---- exceptions (BSS-025/026) and safe states (BSS-027)
    exceptions = spec.get("exceptions") or []
    if not isinstance(exceptions, list):
        _f(findings, "BSS-025", "error", "exceptions must be an array")
        exceptions = []
    has_actions = any(isinstance(el, dict) and el.get("type") == "Action" for el in elements)
    if has_actions and not exceptions:
        _f(findings, "BSS-025", "error",
           "a specification with Actions must account for exceptional conditions (BSS-025, §13.1)")
    unresolved_critical = []
    for e in exceptions:
        if not isinstance(e, dict):
            _f(findings, "BSS-025", "error", "exception entries must be mappings")
            continue
        xid = e.get("exceptionId", "<missing>")
        if not str(e.get("exceptionId", "")).strip():
            _f(findings, "BSS-025", "error", "exception: stable id missing")
        if e.get("category") not in EXCEPTION_CATEGORIES:
            _f(findings, "BSS-025", "error", f"exception {xid}: category {e.get('category')!r} invalid (§13.2)")
        if e.get("affectedElementRef") not in elements_by_id:
            _f(findings, "BSS-012", "error", f"exception {xid}: affectedElementRef {e.get('affectedElementRef')!r} does not resolve")
        if not str(e.get("handlingResponsibility", "")).strip():
            _f(findings, "BSS-025", "error", f"exception {xid}: handling responsibility must be identified (§13.3)")
        if e.get("pathRef") and e["pathRef"] not in elements_by_id:
            _f(findings, "BSS-012", "error", f"exception {xid}: pathRef {e['pathRef']!r} does not resolve")
        if e.get("recoveryOrEscalation") == "Unresolved" and e.get("criticality") == "Critical":
            unresolved_critical.append(xid)
    if unresolved_critical:
        _f(findings, "BSS-026", "error",
           f"critical unresolved exception paths prevent behavioral conformance: {unresolved_critical} (BSS-026)")

    safe_states = spec.get("safeStates") or []
    needs_safe_state = "SafeStateTransition" in set(outcomes or []) or \
        any(isinstance(e, dict) and e.get("recoveryOrEscalation") == "SafeState" for e in exceptions)
    if needs_safe_state and not safe_states:
        _f(findings, "BSS-027", "error",
           "safe-state behavior must be identifiable: a SafeStateTransition outcome or SafeState recovery "
           "path is declared but no safeStates are defined (BSS-027, §13.4)")
    if not isinstance(safe_states, list):
        _f(findings, "BSS-027", "error", "safeStates must be an array")
        safe_states = []
    for s in safe_states:
        if not isinstance(s, dict):
            _f(findings, "BSS-027", "error", "safeState entries must be mappings")
            continue
        sid = s.get("safeStateId", "<missing>")
        for field in ("scopeRef", "entryConditionRef", "expectedOutcome", "responsibleAuthorityRef", "verificationRef"):
            if not str(s.get(field, "")).strip():
                _f(findings, "BSS-027", "error", f"safe state {sid}: {field} missing (§13.4)")
        if s.get("entryConditionRef") not in condition_ids:
            _f(findings, "BSS-012", "error", f"safe state {sid}: entryConditionRef {s.get('entryConditionRef')!r} does not resolve")

    # ---- verification (BSS-028/029) + governed learning (BSS-030)
    vrefs = spec.get("verificationRefs")
    verify_realized = by_stage.get("Verify") in ("Required", "Realized", "PartiallyRealized")
    if not isinstance(vrefs, list) or not vrefs:
        _f(findings, "BSS-028", "error",
           "verification responsibilities must be explicitly representable — verificationRefs are mandatory (BSS-028)")
        vrefs = []
    verify_elements = {eid for eid, el in elements_by_id.items() if isinstance(el, dict) and el.get("type") == "Verification"}
    for v in vrefs:
        if not isinstance(v, dict):
            _f(findings, "BSS-028", "error", "verificationRef entries must be mappings")
            continue
        vid = v.get("verificationId", "<missing>")
        if v.get("elementRef") not in verify_elements:
            _f(findings, "BSS-028", "error",
               f"verification {vid}: elementRef {v.get('elementRef')!r} is not a Verification-typed element (BSS-028)")
        indep = v.get("independence")
        if indep not in ("Independent", "Delegated", "SamePath"):
            _f(findings, "BSS-029", "error", f"verification {vid}: independence {indep!r} invalid (BSS-029)")
        elif indep == "SamePath":
            _f(findings, "BSS-029", "error",
               f"verification {vid}: SamePath verification is rejected — successful Action execution is never "
               "proof that the intended outcome was achieved (BSS-029, §7.4)")
        elif indep == "Delegated" and not str(v.get("resultContractRef", "")).strip():
            _f(findings, "BSS-029", "error", f"verification {vid}: Delegated evaluation requires resultContractRef (§9.4)")
    if verify_realized and not verify_elements:
        _f(findings, "BSS-028", "error", "stage Verify is declared realized/required but no Verification element exists (BSS-028)")

    learning_elements = [eid for eid, el in elements_by_id.items()
                         if isinstance(el, dict) and el.get("type") == "Learning"]
    lb = spec.get("learningBoundaries")
    if learning_elements:
        if not isinstance(lb, dict):
            _f(findings, "BSS-030", "error",
               f"Learning elements ({learning_elements}) require declared learning boundaries (BSS-030)")
        elif lb.get("authorizationRequiredForPolicyChange") is not True:
            _f(findings, "BSS-030", "error",
               "learningBoundaries.authorizationRequiredForPolicyChange must be true — learning must never "
               "implicitly change authority, constraints or approved policy (BSS-030, AOCL-P26)")
        elif not lb.get("authorizationPolicyRef") and not lb.get("boundaries"):
            _f(findings, "BSS-030", "error", "learningBoundaries must name the authorization policy ref or explicit boundaries (BSS-030)")

    # ---- traceability (BSS-031/032)
    for eid, el in elements_by_id.items():
        etype = el.get("type") if isinstance(el, dict) else None
        car = el.get("controlArchitectureRef") or {}
        if etype == "Observation" and not car.get("sensorRef"):
            _f(findings, "BSS-031", "error", f"element {eid}: Observation must trace to its sensor/information source (BSS-031, §14)")
        if etype == "Action" and not car.get("actuatorRef"):
            _f(findings, "BSS-031", "error", f"element {eid}: Action must trace to its actuator responsibility (BSS-031, §14)")
        if etype == "IntentReference" and not (el.get("goalRefs") or []):
            _f(findings, "BSS-032", "error", f"element {eid}: IntentReference must trace to intent/goals (BSS-032)")

    # ---- ADR-007 decision 3: E/C/V_d anchor integrity
    anchors = spec.get("measurementAnchors")
    if anchors is not None and isinstance(anchors, dict):
        eff = anchors.get("effort") or {}
        for ref in eff.get("humanParticipationRefs", []) or []:
            if ref not in participation_ids:
                _f(findings, "ADR-007-ANCHOR", "error", f"E anchor: humanParticipationRef {ref!r} does not resolve")
        cx = anchors.get("complexity") or {}
        for ref in cx.get("architectureRefs", []) or []:
            if ref not in architecture_refs:
                _f(findings, "ADR-007-ANCHOR", "error",
                   f"C anchor: architectureRef {ref!r} is not referenced by any element's controlArchitectureRef")
        for ref in cx.get("fusionDependencies", []) or []:
            if ref not in declared_info:
                _f(findings, "ADR-007-ANCHOR", "error", f"C anchor: fusionDependency {ref!r} is not a declared information dependency")
        vd = anchors.get("veracity") or {}
        for ref in vd.get("informationIds", []) or []:
            if ref not in declared_info:
                _f(findings, "ADR-007-ANCHOR", "error", f"V_d anchor: informationId {ref!r} does not resolve")
    elif hp and anchors is None:
        findings.append({"rule": "ADR-007-ANCHOR", "severity": "warning",
                         "message": "human participation is declared but measurementAnchors is absent — "
                                    "declare the E/C/V_d anchors (ADR-007 decision 3) so the specification "
                                    "is measurable by construction"})

    return _result(findings)


def _result(findings: list) -> dict:
    errors = [f for f in findings if f["severity"] == "error"]
    hit = lambda rules: any(f["rule"] in rules for f in errors)
    schema_valid = not hit(SCHEMA_RULES | {"BSS-035"})
    structurally_valid = schema_valid and not hit(STRUCTURAL_RULES)
    behaviorally_conformant = structurally_valid and not hit(BEHAVIORAL_RULES)
    return {
        "valid": not errors,
        "findings": findings,
        "conformance": {
            "schemaValid": schema_valid,
            "structurallyValid": structurally_valid,
            "behaviorallyConformant": behaviorally_conformant,
            "simulationReady": False,  # set by simulate_readiness()
        },
    }


def simulate_readiness(result: dict, spec: dict) -> dict:
    """BSS-036: simulation readiness is distinct from behavioral conformance.
    Requires control-contract bindings (CR-007) and scenario bindings (CR-009)."""
    reasons = []
    if not result["conformance"]["behaviorallyConformant"]:
        reasons.append("not behaviorally conformant")
    if not spec.get("controlContractBindings"):
        reasons.append("no controlContractBindings (CR-007 contracts must bind actions and state transitions)")
    if not spec.get("scenarioBindings"):
        reasons.append("no scenarioBindings (CR-009 scenarios must bind disturbances and initial conditions)")
    result["conformance"]["simulationReady"] = not reasons
    result["simulationReadinessReasons"] = reasons
    return result


def load_and_validate(path: str | Path) -> dict:
    with open(path, encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    result = validate_behavioral_spec(data)
    if isinstance(data, dict):
        result = simulate_readiness(result, data.get("behavioralSpecification") or {})
    result["source"] = str(path)
    return result


def migrate_to_spec(loop: dict, behavior_policy: dict | None = None) -> dict:
    """Migrate one loop registration into a Draft BehavioralSpecification skeleton
    (CR-006 §20). Preserves identifiers, goals and the decision-model selection;
    stage coverage is declared Required (unresolved mapping — never presumed
    Realized); no conditions, inputs, outputs or exception paths are fabricated;
    every gap is inventoried in migrationNotes + MIG findings."""
    findings: list[dict] = []
    lid = str(loop.get("id", "unknown"))
    missing = [
        "entry conditions (BSS-010)",
        "termination outcomes (BSS-011)",
        "behavioral elements and graph (BSS-005..007)",
        "conditions and guards (BSS-021)",
        "information dependencies (BSS-019/020)",
        "exception and safe-state paths (BSS-025..027)",
        "verification references (BSS-028/029)",
        "human participation declarations (BSS-024)",
    ]
    stage_coverage = [{"stage": s, "status": "Required"} for s in STAGES]
    if behavior_policy:
        stage_coverage.append({"stage": "Learn", "status": "Required"})
    dm = loop.get("decision_model") or {}
    kind = dm.get("kind")
    if kind not in ("OODA", "MAPE", "CUSTOM", None):
        _f(findings, "MIG-003", "warning",
           f"loop {lid}: decision-model kind {kind!r} is not a governed selection — inventoried, not mapped")
        kind = None
    spec = {
        "schemaVersion": SCHEMA_VERSION,
        "specVersion": "0.1.0",
        "behavioralSpecification": {
            "id": f"urn:aocl:spec:{lid}",
            "type": "BehavioralSpecification",
            "name": f"Migrated behavioral specification for {lid}",
            "definition": loop.get("notes") or f"Skeleton migrated from loop registration {lid}; behavior not yet modeled.",
            "lifecycleStatus": "Draft",
            "closedLoopRef": {"loopId": f"urn:aocl:loop:{lid}", "sourceSystem": "aocl-loop-model"},
            "decisionArchitectureRef": {"kind": kind, "source": f"preserved selection from loop {lid}"} if kind else None,
            "objectives": [{
                "objectiveId": f"obj-{lid}-g{i}",
                "goalRef": f"urn:aocl:loop:{lid}#goal-{g.get('name', 'unnamed')}",
                "description": f"Carried from loop goal '{g.get('name', 'unnamed')}' (BSS-032 traceability preserved).",
            } for i, g in enumerate(loop.get("goals", []) or [])],
            "stageCoverage": stage_coverage,
            "entry": {"conditions": [], "description": None},
            "termination": {"outcomes": [], "description": None},
            "elements": [],           # never fabricated (§20)
            "relationships": [],
            "conditions": [],
            "informationDependencies": [],
            "policyRefs": [],
            "humanParticipation": [],
            "exceptions": [],
            "safeStates": [],
            "verificationRefs": [],
            "traceability": {"intentRefs": [], "architectureRefs": [], "requirementRefs": []},
            "governance": {"approvalRequired": True},
            "migrationNotes": {"missingAttributes": missing,
                               "unresolvedStageMappings": [f"{s}: mapping from "
                                                           f"{(dm.get('kind') or 'unspecified')} decision model not inferred (§20)"
                                                           for s in STAGES]},
        },
    }
    _f(findings, "MIG-004", "warning",
       f"loop {lid}: migrated to Draft with {len(missing)} missing behavioral attributes inventoried — "
       "never fabricated (CR-006 §20)")
    result = validate_behavioral_spec(spec)
    # The skeleton is intentionally incomplete: its gaps are the point of the migration.
    result["skeletonConformance"] = result["conformance"]
    result["spec"] = spec
    result["findings"] = findings + result["findings"]
    return result


def render(result: dict) -> str:
    lines = [f"AOCL behavioral specification — {result.get('source', 'validation')}"]
    conf = result.get("conformance", {})
    lines.append("Schema: {} · Structural: {} · Behavioral: {} · Simulation-ready: {}".format(
        conf.get("schemaValid"), conf.get("structurallyValid"),
        conf.get("behaviorallyConformant"), conf.get("simulationReady")))
    for r in result.get("simulationReadinessReasons", []) or []:
        lines.append(f"  readiness: {r}")
    for f in result.get("findings", []):
        lines.append(f"[{f['severity'].upper()}] {f['rule']}: {f['message']}")
    if not result.get("findings"):
        lines.append("No findings — BSS-001..036 and the ADR-007 anchor rule satisfied.")
    return "\n".join(lines)


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--self-test" in argv:
        return _self_test()
    as_json = "--json" in argv
    argv = [a for a in argv if a != "--json"]
    if "--migrate" in argv:
        i = argv.index("--migrate")
        path = argv[i + 1]
        with open(path, encoding="utf-8") as fh:
            model = yaml.safe_load(fh)
        migrated = [migrate_to_spec(loop) for loop in (model.get("loops") or [])]
        ok = bool(migrated)  # migration succeeds when loops are processed; skeleton gaps are the diagnostics
        out = {"valid": ok, "specifications": [{"spec": m["spec"], "findings": m["findings"]} for m in migrated]}
        print(json.dumps(out, indent=2, default=str) if as_json else
              "\n\n".join(render_migrated(m) for m in migrated))
        return 0 if ok else 1
    if not argv:
        print("usage: aocl-behavior-spec <spec.yaml> [--json] | --migrate <loop-model.yaml> | --self-test")
        return 2
    try:
        result = load_and_validate(argv[0])
    except (OSError, ValueError) as exc:
        print(f"error: {exc}")
        return 2
    print(json.dumps(result, indent=2, default=str) if as_json else render(result))
    return 0 if result["valid"] else 1


def render_migrated(m: dict) -> str:
    spec = m["spec"]["behavioralSpecification"]
    lines = [f"AOCL behavioral specification — migrated {spec['id']} (Draft skeleton, CR-006 §20)"]
    for f in m["findings"]:
        lines.append(f"[{f['severity'].upper()}] {f['rule']}: {f['message']}")
    return "\n".join(lines)


def _self_test() -> int:
    import copy

    valid = {
        "schemaVersion": "0.1", "specVersion": "1.0.0",
        "behavioralSpecification": {
            "id": "urn:aocl:spec:service-assurance-001", "type": "BehavioralSpecification",
            "name": "Network Service Assurance Behavior",
            "definition": "Observes latency, decides remediation, executes within authorization, verifies independently, records governed learning.",
            "lifecycleStatus": "Draft",
            "closedLoopRef": {"loopId": "urn:aocl:loop:service-assurance-001", "sourceSystem": "AOCL"},
            "objectives": [{"objectiveId": "obj-latency", "goalRef": "goal-service-latency",
                            "description": "Maintain latency within threshold."}],
            "stageCoverage": [{"stage": s, "status": "Realized"} for s in STAGES],
            "entry": {"conditions": ["cond-cycle"]},
            "termination": {"outcomes": ["VerifiedCompletion", "Escalation"]},
            "elements": [
                {"id": "obs-lat", "type": "Observation", "name": "Observe latency", "stages": ["Observe"],
                 "outputs": ["latency-obs"], "controlArchitectureRef": {"sensorRef": "sensor-lat"}},
                {"id": "analyze", "type": "Analysis", "name": "Analyze congestion", "stages": ["Analyze"],
                 "inputs": ["latency-obs"], "outputs": ["assessment"]},
                {"id": "decide", "type": "Decision", "name": "Decide remediation", "stages": ["Decide"],
                 "inputs": ["assessment"], "outputs": ["decision"]},
                {"id": "approve", "type": "Approval", "name": "Approve reroute", "stages": ["Decide", "Execute"],
                 "inputs": ["decision"], "outputs": ["authorization"], "participationRefs": ["hp-approve"]},
                {"id": "execute", "type": "Action", "name": "Reroute traffic", "stages": ["Execute"],
                 "inputs": ["authorization"], "outputs": ["action-result"],
                 "controlArchitectureRef": {"actuatorRef": "actuator-te"}},
                {"id": "verify", "type": "Verification", "name": "Verify latency", "stages": ["Verify"],
                 "inputs": ["action-result"], "outputs": ["verification-result"]},
                {"id": "learn", "type": "Learning", "name": "Record experience", "stages": ["Learn"],
                 "inputs": ["verification-result"]},
            ],
            "relationships": [
                {"relationshipId": "rel-1", "type": "FlowsTo", "source": "obs-lat", "target": "analyze"},
                {"relationshipId": "rel-2", "type": "FlowsTo", "source": "analyze", "target": "decide"},
                {"relationshipId": "rel-3", "type": "FlowsTo", "source": "decide", "target": "approve"},
                {"relationshipId": "rel-4", "type": "FlowsTo", "source": "approve", "target": "execute"},
                {"relationshipId": "rel-5", "type": "FlowsTo", "source": "execute", "target": "verify"},
                {"relationshipId": "rel-6", "type": "FlowsTo", "source": "verify", "target": "learn"},
                {"relationshipId": "rel-7", "type": "RepeatsTo", "source": "learn", "target": "obs-lat", "conditionRef": "cond-cycle"},
            ],
            "conditions": [
                {"conditionId": "cond-cycle", "category": "Temporal", "subject": "monitoring cycle",
                 "evaluationContext": "scheduler tick"},
            ],
            "informationDependencies": [
                {"informationId": "latency-obs", "kind": "Required", "sourceRef": "obs-lat"},
                {"informationId": "assessment", "kind": "Derived"},
                {"informationId": "decision", "kind": "Derived"},
                {"informationId": "authorization", "kind": "Conditional"},
                {"informationId": "action-result", "kind": "Required"},
                {"informationId": "verification-result", "kind": "Derived"},
            ],
            "policyRefs": [
                {"policyRefId": "pol-te-auth", "targetRef": "auth-routing-changes",
                 "relationship": "AuthorizedBy", "appliesToRefs": ["execute"], "resolved": True},
            ],
            "humanParticipation": [
                {"participationId": "hp-approve", "role": "Approver", "participationKind": "Approval",
                 "stages": ["Decide", "Execute"], "requiredInput": "decision", "expectedResponse": "grant or reject",
                 "timeoutConditionRef": "cond-cycle",
                 "effortAnchor": {"measure": "manual approvals per remediation invocation", "perStage": True}},
            ],
            "exceptions": [
                {"exceptionId": "exc-exec", "category": "ExecutionFailure", "affectedElementRef": "execute",
                 "handlingResponsibility": "retry once then escalate", "pathRef": "approve",
                 "recoveryOrEscalation": "Escalation", "criticality": "Major"},
            ],
            "safeStates": [],
            "verificationRefs": [
                {"verificationId": "vr-lat", "elementRef": "verify", "independence": "Independent",
                 "expectedOutcomeRef": "goal-service-latency", "evidenceTarget": "p95 latency records"},
            ],
            "learningBoundaries": {"knowledgeRefs": ["kb-playbooks"], "boundaries": ["record playbooks only"],
                                    "authorizationRequiredForPolicyChange": True,
                                    "authorizationPolicyRef": "pol-te-auth"},
            "measurementAnchors": {
                "effort": {"humanParticipationRefs": ["hp-approve"], "measure": "approvals per invocation"},
                "complexity": {"architectureRefs": ["sensor-lat", "actuator-te"],
                               "fusionDependencies": ["latency-obs"],
                               "dimensions": ["structural", "dynamic", "semantic", "coupling"]},
                "veracity": {"informationIds": ["latency-obs"], "qualityAttributes": ["freshness"]},
            },
            "traceability": {"intentRefs": ["goal-service-latency"], "architectureRefs": ["sensor-lat", "actuator-te"]},
            "governance": {"approvalRequired": True,
                           "changeHistory": [{"version": "1.0.0", "date": "2026-11-07", "rationale": "initial"}]},
        },
    }

    base = validate_behavioral_spec(copy.deepcopy(valid))
    assert base["valid"], base["findings"]
    assert base["conformance"]["schemaValid"] and base["conformance"]["structurallyValid"], base
    assert base["conformance"]["behaviorallyConformant"], base["findings"]
    base = simulate_readiness(base, valid["behavioralSpecification"])
    assert base["conformance"]["simulationReady"] is False and base["simulationReadinessReasons"], "BSS-036 distinction"

    def broken(mutator):
        d = copy.deepcopy(valid)
        mutator(d["behavioralSpecification"])
        return validate_behavioral_spec(d)

    # BSS-003 mutates the document root (specVersion lives beside schemaVersion)
    r = validate_behavioral_spec({**copy.deepcopy(valid), "specVersion": "one"})
    assert any(f["rule"] == "BSS-003" for f in r["findings"])

    rules_hit = {
        "BSS-001": lambda s: s.__setitem__("id", "spec-1"),
        "BSS-002": lambda s: s.pop("closedLoopRef"),
        "BSS-004": lambda s: s.__setitem__("objectives", []),
        "BSS-005": lambda s: s["elements"].append(copy.deepcopy(s["elements"][0])),
        "BSS-006": lambda s: s["elements"][0].__setitem__("type", "MagicStep"),
        "BSS-007": lambda s: s["elements"][1].pop("stages"),
        "BSS-008": lambda s: s["stageCoverage"].pop(),
        "BSS-009": lambda s: s["stageCoverage"][6].__setitem__("status", "NotApplicable"),
        "BSS-010": lambda s: s.__setitem__("entry", {"conditions": []}),
        "BSS-011": lambda s: s.__setitem__("termination", {"outcomes": []}),
        "BSS-012": lambda s: s["relationships"][0].__setitem__("target", "no-such-element"),
        "BSS-013": lambda s: s["relationships"][0].__setitem__("type", "MaybeFlows"),
        "BSS-014": lambda s: s["relationships"][0].__setitem__("type", "BranchesTo"),
        "BSS-016": lambda s: s["relationships"][0].__setitem__("type", "ExecutesInParallelWith"),
        "BSS-017": lambda s: s["relationships"][0].__setitem__("type", "SynchronizesWith"),
        "BSS-018": lambda s: s["elements"].append({"id": "wait-1", "type": "Wait", "name": "Hold"}),
        "BSS-019": lambda s: s["elements"][1].__setitem__("inputs", ["phantom-input"]),
        "BSS-020": lambda s: s["informationDependencies"].append(s["informationDependencies"][0]),
        "BSS-021": lambda s: s["conditions"][0].pop("evaluationContext"),
        "BSS-022": lambda s: s["policyRefs"][0].__setitem__("resolved", False),
        "BSS-023": lambda s: s["elements"][4].__setitem__("grantsAuthority", True),
        "BSS-024": lambda s: s["humanParticipation"][0].__setitem__("participationKind", "Notification"),
        "BSS-025": lambda s: s.__setitem__("exceptions", []),
        "BSS-027": lambda s: s["termination"]["outcomes"].append("SafeStateTransition"),
        "BSS-028": lambda s: s.__setitem__("verificationRefs", []),
        "BSS-029": lambda s: s["verificationRefs"][0].__setitem__("independence", "SamePath"),
        "BSS-030": lambda s: s.pop("learningBoundaries"),
        "BSS-031": lambda s: s["elements"][4].pop("controlArchitectureRef"),
        "BSS-032": lambda s: s["objectives"][0].pop("goalRef"),
        "BSS-033": lambda s: s["relationships"][0].pop("relationshipId"),
        "BSS-034": lambda s: s.__setitem__("lifecycleStatus", "Approved"),
        "ADR-007-ANCHOR": lambda s: s["measurementAnchors"]["effort"]["humanParticipationRefs"].append("hp-ghost"),
    }
    for rule, mutator in rules_hit.items():
        r = broken(mutator)
        assert any(f["rule"] == rule for f in r["findings"]), (rule, r["findings"])

    # BSS-026: critical unresolved exception blocks behavioral conformance only
    def unresolved_critical(s):
        s["exceptions"][0]["recoveryOrEscalation"] = "Unresolved"
        s["exceptions"][0]["criticality"] = "Critical"
    r = broken(unresolved_critical)
    assert any(f["rule"] == "BSS-026" for f in r["findings"])
    assert not r["conformance"]["behaviorallyConformant"] and r["conformance"]["structurallyValid"], r["conformance"]

    # BSS-035: schema vs behavioral distinction
    r = broken(lambda s: s.__setitem__("unknownKey", 1))
    assert any(f["rule"] == "BSS-035" for f in r["findings"]) and r["conformance"]["schemaValid"] is False

    # migration: skeleton is Draft, stages Required, decision model preserved, gaps inventoried
    loop = {"id": "loop-9", "notes": "legacy loop", "decision_model": {"kind": "MAPE"},
            "goals": [{"name": "latency", "target": {"metric": "e2e_ms", "value": 100, "direction": "AT_MOST"}}]}
    m = migrate_to_spec(loop)
    bs = m["spec"]["behavioralSpecification"]
    assert bs["lifecycleStatus"] == "Draft" and bs["decisionArchitectureRef"]["kind"] == "MAPE"
    assert all(sc["status"] == "Required" for sc in bs["stageCoverage"]) and not bs["elements"]
    assert any("never fabricated" in f["message"] for f in m["findings"])
    print(f"self-test OK (behavior-spec v{RULESET_VERSION}, schema {SCHEMA_VERSION}, BSS-001..036 + migration)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
