"""AOCL Studio bundle export (AOCL-CR-014).

Exports a deterministic, read-only bundle (studio-data.json) that renders the
canonical artifacts in the Studio view: the behavioral specification's staged
graph, the scenario library with visibility-declared disturbances, the control
model's contracts and authority, and the reference run's verdict.

Conformance-gated (STU-001): every artifact in the bundle must pass its native
validator — the Studio renders nothing that the validators reject. The bundle
carries ids and versions (STU-002), is deterministically ordered (STU-006),
and never carries model semantics of its own (STU-007): it is a rendering
projection, not a source of truth.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("error: pyyaml is required for the studio export (pip install pyyaml)")

try:
    from .behavior_spec import validate_behavioral_spec
    from .scenario import validate_scenario_library
    from .control_contract import validate_control_model
    from .trace import validate_trace
except ImportError:  # direct-script execution
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from aocl.behavior_spec import validate_behavioral_spec
    from aocl.scenario import validate_scenario_library
    from aocl.control_contract import validate_control_model
    from aocl.trace import validate_trace

RULESET_VERSION = "1.0.0"
BUNDLE_VERSION = "1.0.0"

STAGES = ("Intent", "Observe", "Analyze", "Decide", "Execute", "Verify", "Learn")


class StudioError(Exception):
    pass


def _load(path) -> dict:
    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh) if str(path).endswith((".yaml", ".yml")) else json.load(fh)


def export_bundle(spec_path, scenario_path, control_path=None, trace_path=None) -> dict:
    """Build the Studio bundle from validated artifacts (STU-001..006)."""
    problems = []
    spec_doc = _load(spec_path)
    spec_result = validate_behavioral_spec(spec_doc)
    if not spec_result["conformance"]["behaviorallyConformant"]:
        problems.append("behavioral specification: not behaviorally conformant — "
                        + "; ".join(f["rule"] for f in spec_result["findings"] if f["severity"] == "error"))
    scen_doc = _load(scenario_path)
    scen_result = validate_scenario_library(scen_doc)
    if not scen_result["valid"]:
        problems.append("scenario library: " + "; ".join(
            f"{f['rule']}" for f in scen_result["findings"] if f["severity"] == "error"))
    control_doc = _load(control_path) if control_path else None
    if control_doc:
        ctrl_result = validate_control_model(control_doc)
        if not ctrl_result["valid"]:
            problems.append("control model: " + "; ".join(
                f"{f['rule']}" for f in ctrl_result["findings"] if f["severity"] == "error"))
    trace_doc = _load(trace_path) if trace_path else None
    if trace_doc:
        trace_result = validate_trace(trace_doc)
        if not trace_result["valid"]:
            problems.append("trace: " + "; ".join(
                f"{f['rule']}" for f in trace_result["findings"] if f["severity"] == "error"))
    if problems:
        raise StudioError("studio gate failed (STU-001):\n  - " + "\n  - ".join(problems))

    spec = spec_doc["behavioralSpecification"]
    lib = scen_doc["scenarioLibrary"]

    # graph projection (STU-003/004): exactly the declared elements/relationships,
    # staged by their declared associations — nothing implied
    elements = []
    for el in sorted(spec.get("elements", []), key=lambda e: e.get("id", "")):
        elements.append({
            "id": el.get("id"), "type": el.get("type"), "name": el.get("name"),
            "stages": el.get("stages", []),
            "inputs": el.get("inputs", []), "outputs": el.get("outputs", []),
            "participationRefs": el.get("participationRefs", []),
            "goalRefs": el.get("goalRefs", []),
            "conditionRefs": el.get("conditionRefs", []),
            "controlArchitectureRef": el.get("controlArchitectureRef", {}),
            "resumeEventRef": el.get("resumeEventRef"),
            "syncPattern": el.get("syncPattern"),
        })
    relationships = sorted([
        {k: r.get(k) for k in ("relationshipId", "type", "source", "target",
                                "conditionRef", "terminationOutcome") if r.get(k) is not None}
        for r in spec.get("relationships", [])], key=lambda r: r.get("relationshipId", ""))
    conditions = sorted([{"conditionId": c.get("conditionId"), "category": c.get("category"),
                           "subject": c.get("subject"), "operator": c.get("operator"),
                           "valueRef": c.get("valueRef"), "evaluationContext": c.get("evaluationContext")}
                          for c in spec.get("conditions", [])], key=lambda c: c.get("conditionId", ""))
    participation = sorted([{"participationId": h.get("participationId"), "role": h.get("role"),
                              "participationKind": h.get("participationKind"),
                              "expectedResponse": h.get("expectedResponse")}
                             for h in spec.get("humanParticipation", [])],
                            key=lambda h: h.get("participationId", ""))
    exceptions = sorted([{"exceptionId": e.get("exceptionId"), "category": e.get("category"),
                           "affectedElementRef": e.get("affectedElementRef"),
                           "criticality": e.get("criticality"),
                           "recoveryOrEscalation": e.get("recoveryOrEscalation")}
                          for e in spec.get("exceptions", [])], key=lambda e: e.get("exceptionId", ""))
    safe_states = sorted([{"safeStateId": s.get("safeStateId"), "scopeRef": s.get("scopeRef"),
                            "expectedOutcome": s.get("expectedOutcome")}
                           for s in spec.get("safeStates", [])], key=lambda s: s.get("safeStateId", ""))
    verifications = sorted([{"verificationId": v.get("verificationId"), "elementRef": v.get("elementRef"),
                              "independence": v.get("independence"), "claim": v.get("claim")}
                             for v in spec.get("verificationRefs", [])],
                            key=lambda v: v.get("verificationId", ""))

    scenarios = []
    for sc in sorted(lib.get("scenarios", []), key=lambda s: s.get("scenarioId", "")):
        scenarios.append({
            "scenarioId": sc.get("scenarioId"), "name": sc.get("name"), "type": sc.get("scenarioType"),
            "version": sc.get("version"), "lifecycleStatus": sc.get("lifecycleStatus"),
            "extends": sc.get("extends"), "differences": sc.get("differences", []),
            "disturbances": [{
                "disturbanceId": d.get("disturbanceId"), "type": d.get("disturbanceType"),
                "name": d.get("name"), "magnitude": d.get("magnitude"),
                "magnitudeUnit": d.get("magnitudeUnit"),
                "profile": (d.get("profile") or {}).get("kind"),
                "knownToController": d.get("knownToController"),  # STU-005: rendered explicitly
            } for d in sorted(sc.get("disturbances", []), key=lambda d: d.get("disturbanceId", ""))],
            "verificationTargets": [{"targetId": t.get("targetId"), "claimRef": t.get("claimRef")}
                                     for t in sc.get("verificationTargets", [])],
            "initialStates": [{"stateVariableRef": s.get("stateVariableRef"), "stateClass": s.get("stateClass"),
                                "value": s.get("value"), "unit": s.get("unit")}
                               for s in sc.get("initialConditions", {}).get("states", [])],
        })

    control = None
    if control_doc:
        cm = control_doc["controlModel"]
        control = {
            "ref": cm.get("id"), "version": cm.get("modelVersion"),
            "variables": [{"variableId": v.get("variableId"), "roles": v.get("roles", []),
                            "unit": v.get("unit")} for v in cm.get("controlVariables", [])],
            "contracts": [{"contractId": c.get("contractId"), "contractType": c.get("contractType"),
                            "subjectRef": c.get("subjectRef")} for c in cm.get("contracts", [])],
            "authority": [{"authorityId": a.get("authorityId"), "subjectRef": a.get("subjectRef"),
                            "authorityClass": a.get("authorityClass")} for a in cm.get("authority", [])],
            "invariants": [{"invariantId": i.get("invariantId"), "priorityClass": i.get("priorityClass"),
                             "statement": i.get("statement")} for i in cm.get("invariants", [])],
        }

    trace = None
    if trace_doc:
        t = trace_doc["executionTrace"]
        trace = {"runId": t.get("runId"), "engineName": t.get("engineName"),
                  "engineVersion": t.get("engineVersion"), "termination": t.get("termination"),
                  "recordCount": len(t.get("records", []))}

    return {
        "bundleVersion": BUNDLE_VERSION, "rulesetVersion": RULESET_VERSION,
        "generatedBy": "aocl-studio",
        "spec": {"ref": spec.get("id"), "name": spec.get("name"), "version": spec_doc.get("specVersion"),
                  "lifecycleStatus": spec.get("lifecycleStatus"),
                  "entry": spec.get("entry", {}).get("conditions", []),
                  "terminationOutcomes": spec.get("termination", {}).get("outcomes", []),
                  "elements": elements, "relationships": relationships, "conditions": conditions,
                  "humanParticipation": participation, "exceptions": exceptions,
                  "safeStates": safe_states, "verificationRefs": verifications},
        "scenarios": {"ref": lib.get("id"), "name": lib.get("name"), "scenarios": scenarios},
        "control": control,
        "trace": trace,
    }


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--self-test" in argv:
        return _self_test()
    as_json = "--json" in argv
    argv = [a for a in argv if a != "--json"]
    if not argv or argv[0] != "export":
        print("usage: aocl-studio export <spec.yaml> --scenarios <library.yaml> [--control <yaml>] "
              "[--trace <trace.json>] [--out <file.json>] [--json] | --self-test")
        return 2
    args, opts = argv[1:], {}
    i = 0
    while i < len(args):
        if args[i] == "--scenarios":
            opts["scenarios"] = args[i + 1]; i += 2
        elif args[i] == "--control":
            opts["control"] = args[i + 1]; i += 2
        elif args[i] == "--trace":
            opts["trace"] = args[i + 1]; i += 2
        elif args[i] == "--out":
            opts["out"] = args[i + 1]; i += 2
        else:
            i += 1
    if "scenarios" not in opts:
        print("error: --scenarios is required")
        return 2
    try:
        bundle = export_bundle(args[0], opts["scenarios"], opts.get("control"), opts.get("trace"))
    except StudioError as exc:
        print(f"error: {exc}")
        return 1
    text = json.dumps(bundle, indent=2)
    if opts.get("out"):
        Path(opts["out"]).write_text(text)
        print(f"studio bundle written: {opts['out']} "
              f"({len(bundle['spec']['elements'])} elements, {len(bundle['scenarios']['scenarios'])} scenarios)")
    else:
        print(text if as_json else f"studio bundle: {len(bundle['spec']['elements'])} elements, "
                                    f"{len(bundle['spec']['relationships'])} relationships, "
                                    f"{len(bundle['scenarios']['scenarios'])} scenarios"
                                    + (f", trace {bundle['trace']['runId']}" if bundle.get("trace") else ""))
    return 0


def _self_test() -> int:
    import copy

    bundle = export_bundle("examples/behavioral-spec.yaml", "examples/scenario-library.yaml",
                            "examples/control-contract.yaml", "examples/trace-logical-run.json")
    # provenance (STU-002)
    assert bundle["spec"]["ref"] == "urn:aocl:spec:network-assurance-001"
    assert bundle["spec"]["version"] and bundle["scenarios"]["ref"]
    # graph fidelity (STU-003): every declared relationship is in the bundle, nothing added
    spec = _load("examples/behavioral-spec.yaml")["behavioralSpecification"]
    declared = {(r["relationshipId"], r["type"], r["source"], r["target"]) for r in spec["relationships"]}
    rendered = {(r["relationshipId"], r["type"], r["source"], r["target"]) for r in bundle["spec"]["relationships"]}
    assert declared == rendered
    # visibility rendering (STU-005): knownToController carried on every disturbance
    for sc in bundle["scenarios"]["scenarios"]:
        for d in sc["disturbances"]:
            assert isinstance(d["knownToController"], bool)
    # determinism (STU-006): two exports are byte-identical
    again = export_bundle("examples/behavioral-spec.yaml", "examples/scenario-library.yaml",
                           "examples/control-contract.yaml", "examples/trace-logical-run.json")
    assert json.dumps(again, sort_keys=True) == json.dumps(bundle, sort_keys=True)
    # verdict honesty (STU-008): the trace's termination verdict is carried
    assert bundle["trace"]["termination"]["outcome"] == "VerifiedCompletion"
    # gate (STU-001): an invalid spec is refused
    bad = copy.deepcopy(_load("examples/behavioral-spec.yaml"))
    bad["behavioralSpecification"]["lifecycleStatus"] = "Running"
    Path("/tmp/bad-spec.yaml").write_text(yaml.dump(bad))
    try:
        export_bundle("/tmp/bad-spec.yaml", "examples/scenario-library.yaml")
        raise AssertionError("gate must refuse an invalid spec")
    except StudioError as exc:
        assert "STU-001" in str(exc)

    print(f"self-test OK (studio export v{BUNDLE_VERSION}, ruleset {RULESET_VERSION}, STU-001..008)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
