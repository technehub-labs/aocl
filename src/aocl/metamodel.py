"""AOCL canonical metamodel (AOCL-CR-002): load, validate and migrate.

Implements structural and semantic validation rules MM-001..018 natively
(stdlib + pyyaml only) and carries the ADR-006 F1 disposition: maturity
vectors are first-class behavioral attributes of the ClosedLoop aggregate;
the overall level is derived reporting and must equal min(GD, DV, FI).

Also provides the migration path from the modeler's `aocl-loop-model`
format to canonical ClosedLoop records (CR-002 §11): existing identifiers,
names, goals and decision-model selections are preserved; missing required
attributes are inventoried as findings — never fabricated.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("error: pyyaml is required for the metamodel (pip install pyyaml)")

RULESET_VERSION = "1.0.0"
SCHEMA_VERSION = "0.1"

LIFECYCLE = ("Draft", "InReview", "Approved", "Deprecated", "Retired")
RUNTIME_STATUSES = {"running", "suspended", "failed", "active", "paused", "deployed", "operational"}
OPERATORS = ("lessThan", "lessThanOrEqual", "greaterThan", "greaterThanOrEqual",
             "equals", "within", "outside", "present")
CONSTRAINT_TYPES = ("Safety", "Operational", "Regulatory", "Financial",
                    "Resource", "Temporal", "Authorization", "Technical")
ENTERPRISE_TYPES = ("Capability", "Process", "Activity", "System", "Function", "Service",
                    "Resource", "InformationEntity", "DataEntity", "Goal", "Outcome", "Metric")
SYSTEM_ROLES = ("ControlledSystem", "MonitoredSystem", "SupportingSystem", "IndirectlyAffectedSystem")
RELATIONSHIP_ROLES = ("Realizes", "DependsOn", "Monitors", "Controls", "ContributesTo")

SEMVER = re.compile(r"^\d+\.\d+\.\d+$")
URN = re.compile(r"^urn:aocl:loop:[a-z0-9][a-z0-9-]*$")
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _findings_add(findings: list, rule: str, severity: str, message: str) -> None:
    findings.append({"rule": rule, "severity": severity, "message": message})


def _check_id(findings: list, entity: str, value, rule: str = "MM-001") -> bool:
    if not isinstance(value, str) or len(value) < 3:
        _findings_add(findings, rule, "error", f"{entity}: stable identifier missing or too short")
        return False
    return True


def validate_canonical(data: dict) -> dict:
    """Validate a canonical ClosedLoop document against MM-001..018 plus the
    ADR-006 aggregation-binding rule. Returns findings and conformance flags."""
    findings: list[dict] = []
    warnings: list[dict] = []

    if not isinstance(data, dict):
        _findings_add(findings, "MM-001", "error", "document must be a mapping")
        return {"valid": False, "findings": findings, "warnings": warnings,
                "conformance": {"structurallyValid": False, "semanticallyValid": False}}

    # MM-014: independent model and schema versions
    if data.get("schemaVersion") != SCHEMA_VERSION:
        _findings_add(findings, "MM-014", "error",
                      f"schemaVersion must be '{SCHEMA_VERSION}' (this validator's contract), got {data.get('schemaVersion')!r}")
    if not SEMVER.match(str(data.get("modelVersion", ""))):
        _findings_add(findings, "MM-014", "error", f"modelVersion must be semver, got {data.get('modelVersion')!r}")

    loop = data.get("closedLoop")
    if not isinstance(loop, dict):
        _findings_add(findings, "MM-002", "error", "closedLoop aggregate missing")
        return {"valid": False, "findings": findings, "warnings": warnings,
                "conformance": {"structurallyValid": False, "semanticallyValid": False}}

    # MM-017: unknown attributes cannot override canonical semantics
    known_root = {"schemaVersion", "modelVersion", "closedLoop"}
    unknown_root = set(data) - known_root
    if unknown_root:
        _findings_add(findings, "MM-017", "error", f"unknown document attributes: {sorted(unknown_root)}")

    known_loop = {"id", "type", "name", "definition", "description", "modelVersion", "schemaVersion",
                  "lifecycleStatus", "context", "scope", "intent", "controlledSystems",
                  "enterpriseReferences", "architectureBindings", "behavioralBindings",
                  "assessment", "provenance", "changeHistory"}
    unknown_loop = set(loop) - known_loop
    if unknown_loop:
        _findings_add(findings, "MM-017", "error", f"closedLoop: unknown attributes {sorted(unknown_loop)}")

    # MM-001 / MM-002: stable, unique identity
    if not _check_id(findings, "closedLoop.id", loop.get("id"), "MM-002"):
        pass
    elif not URN.match(loop["id"]):
        _findings_add(findings, "MM-002", "error",
                      "closedLoop.id must match urn:aocl:loop:<slug> (stable, opaque; not derived from names)")

    if loop.get("type") != "ClosedLoop":
        _findings_add(findings, "MM-013", "error", "closedLoop.type must be 'ClosedLoop'")
    if not str(loop.get("name", "")).strip():
        _findings_add(findings, "MM-001", "error", "closedLoop.name is mandatory")
    if not str(loop.get("definition", "")).strip():
        _findings_add(findings, "MM-001", "error", "closedLoop.definition is mandatory")

    # MM-016: lifecycle status is not runtime status
    status = loop.get("lifecycleStatus")
    if status not in LIFECYCLE:
        hint = " — runtime statuses belong to execution representations, not the model lifecycle (MM-016)" \
            if str(status).lower() in RUNTIME_STATUSES else ""
        _findings_add(findings, "MM-016", "error",
                      f"lifecycleStatus must be one of {LIFECYCLE}, got {status!r}{hint}")

    # MM-003 context
    ctx = loop.get("context")
    if not isinstance(ctx, dict) or not str(ctx.get("domain", "")).strip():
        _findings_add(findings, "MM-003", "error", "context must be present with an operational domain")
    elif not str(ctx.get("contextId", "")).strip():
        _findings_add(findings, "MM-001", "error", "context.contextId missing")

    # MM-004 scope
    scope = loop.get("scope")
    if not isinstance(scope, dict) or not str(scope.get("boundaryDefinition", "")).strip():
        _findings_add(findings, "MM-004", "error", "scope must be present with an explicit boundary definition")
    elif not str(scope.get("scopeId", "")).strip():
        _findings_add(findings, "MM-001", "error", "scope.scopeId missing")

    # MM-005..MM-009 intent
    intent = loop.get("intent")
    if not isinstance(intent, dict) or not str(intent.get("statement", "")).strip():
        _findings_add(findings, "MM-005", "error", "intent specification missing or without a statement")
        goals = []
    else:
        if not str(intent.get("intentId", "")).strip():
            _findings_add(findings, "MM-001", "error", "intent.intentId missing")
        goals = intent.get("goals")
        if not isinstance(goals, list) or not goals:
            _findings_add(findings, "MM-006", "error", "intent must contain at least one goal")
            goals = []
        for i, goal in enumerate(goals):
            gid = goal.get("goalId", f"goals[{i}]") if isinstance(goal, dict) else f"goals[{i}]"
            if not isinstance(goal, dict) or not str(goal.get("definition", "")).strip():
                _findings_add(findings, "MM-007", "error", f"goal {gid}: definition missing")
            if not isinstance(goal, dict) or not str(goal.get("successCriteria", "")).strip():
                _findings_add(findings, "MM-007", "error", f"goal {gid}: identifiable success criteria missing")
            if isinstance(goal, dict):
                gids = [g.get("goalId") for g in goals if isinstance(g, dict)]
                if gids.count(goal.get("goalId")) > 1:
                    _findings_add(findings, "MM-011", "error", f"duplicate goalId: {goal.get('goalId')!r}")
                for j, rc in enumerate(goal.get("referenceConditions", []) or []):
                    rid = rc.get("conditionId", f"[{j}]") if isinstance(rc, dict) else f"[{j}]"
                    if not isinstance(rc, dict):
                        _findings_add(findings, "MM-008", "error", f"reference condition {rid} must be a mapping")
                        continue
                    if not str(rc.get("variable", "")).strip():
                        _findings_add(findings, "MM-008", "error", f"reference condition {rid}: variable missing")
                    if rc.get("operator") not in OPERATORS:
                        _findings_add(findings, "MM-008", "error",
                                      f"reference condition {rid}: operator {rc.get('operator')!r} invalid")
                    if "targetValue" not in rc and rc.get("operator") != "present":
                        _findings_add(findings, "MM-008", "error", f"reference condition {rid}: targetValue missing")
        for j, con in enumerate(intent.get("constraints", []) or []):
            cid = con.get("constraintId", f"[{j}]") if isinstance(con, dict) else f"[{j}]"
            if not isinstance(con, dict):
                _findings_add(findings, "MM-009", "error", f"constraint {cid} must be a mapping")
                continue
            if con.get("constraintType") not in CONSTRAINT_TYPES:
                _findings_add(findings, "MM-009", "error",
                              f"constraint {cid}: constraintType {con.get('constraintType')!r} invalid")
            if not str(con.get("expression", "")).strip():
                _findings_add(findings, "MM-009", "error", f"constraint {cid}: expression missing")

    # MM-010 controlled systems
    systems = loop.get("controlledSystems")
    if not isinstance(systems, list) or not systems:
        _findings_add(findings, "MM-010", "error", "at least one controlled-system binding is required")
        systems = []
    binding_ids = []
    for i, b in enumerate(systems):
        if not isinstance(b, dict):
            _findings_add(findings, "MM-010", "error", f"controlledSystems[{i}] must be a mapping")
            continue
        bid = b.get("bindingId", f"[{i}]")
        binding_ids.append(bid)
        if not str(b.get("bindingId", "")).strip():
            _findings_add(findings, "MM-001", "error", f"controlledSystems[{i}]: bindingId missing")
        tr = b.get("targetReference")
        if not isinstance(tr, dict) or not str(tr.get("sourceSystem", "")).strip():
            # MM-012 for controlled-system references: source-qualified
            _findings_add(findings, "MM-012", "error",
                          f"controlled system {bid}: targetReference must be source-qualified (sourceSystem)")
        if b.get("systemRole") not in SYSTEM_ROLES:
            _findings_add(findings, "MM-013", "error",
                          f"controlled system {bid}: systemRole {b.get('systemRole')!r} invalid "
                          f"(controlled vs monitored vs supporting must be distinguished)")
    if len(binding_ids) != len(set(binding_ids)):
        _findings_add(findings, "MM-011", "error", "duplicate controlled-system bindingIds")

    # MM-012 / MM-013 enterprise references
    for i, ref in enumerate(loop.get("enterpriseReferences", []) or []):
        rid = ref.get("referenceId", f"[{i}]") if isinstance(ref, dict) else f"[{i}]"
        if not isinstance(ref, dict):
            _findings_add(findings, "MM-012", "error", f"enterpriseReferences[{i}] must be a mapping")
            continue
        if not str(ref.get("sourceSystem", "")).strip():
            _findings_add(findings, "MM-012", "error",
                          f"enterprise reference {rid}: sourceSystem missing — references must preserve authoritative source identity")
        if ref.get("targetType") not in ENTERPRISE_TYPES:
            _findings_add(findings, "MM-013", "error",
                          f"enterprise reference {rid}: targetType {ref.get('targetType')!r} invalid")
        if ref.get("relationshipRole") not in RELATIONSHIP_ROLES:
            _findings_add(findings, "MM-013", "error",
                          f"enterprise reference {rid}: relationshipRole {ref.get('relationshipRole')!r} invalid "
                          "(no unqualified relatedTo relationships)")

    # MM-018 provenance
    prov = loop.get("provenance")
    if not isinstance(prov, dict) or not str(prov.get("source", "")).strip() or not str(prov.get("authority", "")).strip():
        _findings_add(findings, "MM-018", "error",
                      "provenance must identify the authoritative source and authority of the definition")
    elif not DATE.match(str(prov.get("createdAt", ""))):
        _findings_add(findings, "MM-018", "error", "provenance.createdAt must be an ISO date")

    # ADR-006 F1 disposition: vectors are the first-class behavioral attributes;
    # level is derived reporting and must equal the weakest vector.
    assessment = loop.get("assessment")
    if assessment is not None:
        if not isinstance(assessment, dict) or not str(assessment.get("method", "")).strip():
            _findings_add(findings, "MM-018", "error", "assessment: method missing (assessment provenance)")
        else:
            vectors = assessment.get("vectors")
            if not isinstance(vectors, dict) or set(vectors) != {"GD", "DV", "FI"}:
                _findings_add(findings, "ADR-006-F1", "error",
                              "assessment.vectors must carry exactly GD, DV, FI (vectors are the first-class behavioral attributes)")
            else:
                weakest = min(vectors.values())
                declared = assessment.get("level")
                if declared != weakest:
                    _findings_add(findings, "ADR-006-F1", "error",
                                  f"assessment.level {declared} inconsistent with weakest vector {weakest} — "
                                  "level is derived reporting: level = min(GD, DV, FI)")

    errors = [f for f in findings if f["severity"] == "error"]
    structurally_valid = not any(f["rule"] in ("MM-001", "MM-002", "MM-003", "MM-004", "MM-005",
                                               "MM-006", "MM-008", "MM-009", "MM-010", "MM-013",
                                               "MM-014", "MM-016", "MM-017") for f in errors)
    semantically_valid = structurally_valid and not any(f["rule"] in ("MM-007", "MM-011", "MM-012",
                                                                     "MM-018", "ADR-006-F1") for f in errors)
    return {
        "valid": not errors,
        "findings": findings,
        "warnings": warnings,
        "conformance": {"structurallyValid": structurally_valid, "semanticallyValid": semantically_valid},
    }


# ---------------------------------------------------------------- migration

def migrate_loop_model(model: dict) -> dict:
    """Migrate a modeler `aocl-loop-model` document into canonical ClosedLoop
    records (CR-002 §11). Preserves identifiers, names, goals and decision-model
    selections; inventories missing required attributes as findings — never
    fabricates them. Migrated loops are Draft status."""
    findings: list[dict] = []
    if not isinstance(model, dict) or model.get("format") != "aocl-loop-model":
        _findings_add(findings, "MIG-001", "error", "expected format: aocl-loop-model")
        return {"valid": False, "findings": findings, "closedLoops": []}

    entities = {e.get("id"): e for e in model.get("entities", []) if isinstance(e, dict) and e.get("id")}
    loops = model.get("loops", [])
    if not loops:
        _findings_add(findings, "MIG-002", "error", "no loops to migrate")

    closed_loops = []
    for loop in loops:
        lid = loop.get("id", "unknown")
        entity = entities.get(loop.get("entity"), {})
        missing = []
        if not loop.get("owner"):
            missing.append("owner (provenance.authority)")
        missing.append("operational context (context.domain)")
        missing.append("explicit boundary definition (scope)")
        missing.append("behavioral specification binding (CR-003)")
        missing.append("architecture binding (CR-004)")
        goals = []
        for gl in loop.get("goals", []) or []:
            target = gl.get("target", {}) or {}
            goals.append({
                "goalId": f"goal-{gl.get('name', 'unnamed')}",
                "name": gl.get("name", "unnamed"),
                "definition": f"Carried from the loop-model goal '{gl.get('name')}': "
                              f"target {target.get('metric')} {target.get('direction', 'AT_LEAST')} "
                              f"{target.get('value')} {target.get('unit') or ''}".strip(),
                "successCriteria": "",  # inventoried: absent in the loop-model format
                "referenceConditions": [{
                    "conditionId": f"cond-{target.get('metric', 'metric')}",
                    "variable": str(target.get("metric", "")),
                    "operator": {"AT_LEAST": "greaterThanOrEqual", "AT_MOST": "lessThanOrEqual",
                                 "EXACTLY": "equals"}.get(target.get("direction"), "greaterThanOrEqual"),
                    "targetValue": target.get("value"),
                    "unit": target.get("unit"),
                }],
            })
            if not str(gl.get("name", "")).strip() or "value" not in target:
                _findings_add(findings, "MIG-003", "error",
                              f"loop {lid}: goal '{gl.get('name')}' lacks a measurable target — inventoried, not fabricated")
        vectors = loop.get("vector_scores")
        assessment = None
        if vectors:
            assessment = {"vectors": vectors, "level": min(vectors.values()),
                          "method": "carried from aocl-loop-model", "assessedAt": None}
        record = {
            "schemaVersion": SCHEMA_VERSION,
            "modelVersion": "1.0.0",
            "closedLoop": {
                "id": f"urn:aocl:loop:{lid}",
                "type": "ClosedLoop",
                "name": entity.get("name", lid),
                "definition": entity.get("description") or loop.get("notes") or f"Migrated loop {lid}.",
                "modelVersion": "1.0.0",
                "lifecycleStatus": "Draft",
                "context": {"contextId": f"ctx-{loop.get('entity', 'unknown')}",
                            "domain": entity.get("domain") or "unspecified"},
                "scope": {"scopeId": f"scope-{loop.get('entity', 'unknown')}",
                          "boundaryDefinition": f"Entity {entity.get('name', loop['entity'])} "
                                                f"({entity.get('kind', 'unknown')})."},
                "intent": {"intentId": f"intent-{lid}", "statement": loop.get("notes") or "", "goals": goals},
                "controlledSystems": [{
                    "bindingId": f"binding-{loop.get('entity', 'unknown')}",
                    "targetReference": {"targetId": loop.get("entity", "unknown"),
                                        "targetType": "System", "sourceSystem": "aocl-loop-model"},
                    "systemRole": "ControlledSystem",
                }],
                "behavioralBindings": [],
                "architectureBindings": [],
                "enterpriseReferences": [],
                "assessment": assessment,
                "provenance": {"source": "aocl-loop-model migration", "authority": loop.get("owner") or "unassigned",
                               "createdAt": None},
                "migrationNotes": {"missingAttributes": missing,
                                    "decisionModel": (loop.get("decision_model") or {}).get("kind"),
                                    "velocity": loop.get("velocity"),
                                    "maturityLevel": loop.get("level")},
            },
        }
        if missing:
            _findings_add(findings, "MIG-004", "warning",
                          f"loop {lid}: migrated to Draft with missing attributes inventoried ({len(missing)}) — "
                          "never fabricated (CR-002 §11)")
        closed_loops.append(record)
    return {"valid": not any(f["severity"] == "error" for f in findings),
            "findings": findings, "closedLoops": closed_loops}


def load_and_validate(path: str | Path) -> dict:
    with open(path, encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    result = validate_canonical(data)
    result["source"] = str(path)
    return result


def render(result: dict) -> str:
    lines = [f"AOCL canonical metamodel — {result.get('source', 'validation')}"]
    conf = result.get("conformance", {})
    lines.append(f"Structurally valid: {conf.get('structurallyValid')} · Semantically valid: {conf.get('semanticallyValid')}")
    for f in result.get("findings", []):
        lines.append(f"[{f['severity'].upper()}] {f['rule']}: {f['message']}")
    if not result.get("findings"):
        lines.append("No findings — MM-001..018 and the ADR-006 binding rule satisfied.")
    for w in result.get("warnings", []):
        lines.append(f"[WARNING] {w}")
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
        result = migrate_loop_model(model)
        print(json.dumps(result, indent=2, default=str) if as_json else render(result))
        return 0 if result["valid"] else 1
    if not argv:
        print("usage: aocl-metamodel <canonical.yaml> [--json] | --migrate <loop-model.yaml> | --self-test")
        return 2
    try:
        result = load_and_validate(argv[0])
    except (OSError, ValueError) as exc:
        print(f"error: {exc}")
        return 2
    print(json.dumps(result, indent=2, default=str) if as_json else render(result))
    return 0 if result["valid"] else 1


def _self_test() -> int:
    valid = {
        "schemaVersion": "0.1", "modelVersion": "1.0.0",
        "closedLoop": {
            "id": "urn:aocl:loop:service-assurance-001", "type": "ClosedLoop",
            "name": "Network Service Assurance",
            "definition": "Maintains network service performance within declared thresholds.",
            "modelVersion": "1.0.0",
            "lifecycleStatus": "Draft",
            "context": {"contextId": "ctx-1", "domain": "Network Operations"},
            "scope": {"scopeId": "scope-1", "boundaryDefinition": "Service latency and traffic management."},
            "intent": {"intentId": "intent-1", "statement": "Maintain latency below threshold.",
                       "goals": [{"goalId": "g1", "name": "Latency", "definition": "Hold latency.",
                                  "successCriteria": "p95 below target.",
                                  "referenceConditions": [{"conditionId": "c1", "variable": "service.latency",
                                                           "operator": "lessThan", "targetValue": 50, "unit": "ms"}]}],
                       "constraints": [{"constraintId": "k1", "name": "Routing safety",
                                        "constraintType": "Safety", "expression": "No unsafe reroute."}]},
            "controlledSystems": [{"bindingId": "b1",
                                    "targetReference": {"targetId": "network-service-001", "targetType": "System",
                                                        "sourceSystem": "Enterprise Architecture"},
                                    "systemRole": "ControlledSystem",
                                    "cycleIntervalTicks": 1, "actuationAuthorityPerCycle": 10}],
            "enterpriseReferences": [{"referenceId": "r1", "targetId": "cap-1", "targetType": "Capability",
                                       "sourceSystem": "Enterprise Architecture", "relationshipRole": "Realizes"}],
            "assessment": {"vectors": {"GD": 3, "DV": 3, "FI": 3}, "level": 3,
                            "method": "aocl-assessment", "assessedAt": "2026-11-07"},
            "provenance": {"source": "AOCL Engineering Model", "authority": "Model Owner",
                            "createdAt": "2026-11-07"},
        },
    }
    result = validate_canonical(json.loads(json.dumps(valid)))
    assert result["valid"] and result["conformance"]["semanticallyValid"], result

    def broken(mutator):
        d = json.loads(json.dumps(valid))
        mutator(d)
        return validate_canonical(d)

    r = broken(lambda d: d["closedLoop"].__setitem__("lifecycleStatus", "Running"))
    assert any(f["rule"] == "MM-016" for f in r["findings"])
    r = broken(lambda d: d["closedLoop"]["intent"].__setitem__("goals", []))
    assert any(f["rule"] == "MM-006" for f in r["findings"])
    r = broken(lambda d: d["closedLoop"]["intent"]["goals"][0]["referenceConditions"][0].__setitem__("operator", "about"))
    assert any(f["rule"] == "MM-008" for f in r["findings"])
    r = broken(lambda d: d["closedLoop"].__setitem__("assessment", {"vectors": {"GD": 5, "DV": 5, "FI": 2},
                                                                    "level": 5, "method": "x"}))
    assert any(f["rule"] == "ADR-006-F1" for f in r["findings"]), r["findings"]
    r = broken(lambda d: d["closedLoop"].__setitem__("extraKey", 1))
    assert any(f["rule"] == "MM-017" for f in r["findings"])
    r = broken(lambda d: d["closedLoop"].pop("provenance"))
    assert any(f["rule"] == "MM-018" for f in r["findings"])
    r = broken(lambda d: d["closedLoop"].__setitem__("controlledSystems", []))
    assert any(f["rule"] == "MM-010" for f in r["findings"])

    # migration: preserves ids/goals, inventories gaps, never fabricates
    model = {
        "format": "aocl-loop-model", "model_version": "1.0.0", "ruleset_version": "1.0.0",
        "entities": [{"id": "proc-1", "kind": "process", "name": "Detect Anomaly", "domain": "assurance"}],
        "loops": [{"id": "loop-1", "entity": "proc-1", "velocity": "fast", "level": 2,
                    "decision_model": {"kind": "MAPE"}, "owner": "op-lead",
                    "goals": [{"name": "latency", "target": {"metric": "e2e_ms", "value": 100, "direction": "AT_MOST"}}]}],
        "links": [],
    }
    m = migrate_loop_model(model)
    assert m["valid"] and len(m["closedLoops"]) == 1
    cl = m["closedLoops"][0]["closedLoop"]
    assert cl["id"] == "urn:aocl:loop:loop-1" and cl["lifecycleStatus"] == "Draft"
    assert cl["intent"]["goals"][0]["referenceConditions"][0]["operator"] == "lessThanOrEqual"
    assert any("missing" in f["message"] for f in m["findings"])  # gaps inventoried
    bad = migrate_loop_model({"format": "wrong"})
    assert not bad["valid"]
    print(f"self-test OK (metamodel v{RULESET_VERSION}, schema {SCHEMA_VERSION}, MM-001..018 + migration)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
