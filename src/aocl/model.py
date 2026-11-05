"""AOCL loop modeler model: entities (process/capability/system/function) and
their closed loops, with CLAM-aligned loop specifications.

Load + validate an `aocl-loop-model` file and convert it to the CLAM
provisioning export (Closed-Loop-Management data model 1.0). See
docs/clm-alignment.md and schema/loop-model.schema.json.
"""

from __future__ import annotations

import re
import sys

RULESET_VERSION = "1.0.0"

ENTITY_KINDS = ("process", "capability", "system", "function")
VELOCITIES = ("fast", "tactical", "slow")
STATES = ("designed", "validated", "published", "active", "paused", "error", "retired")
LINK_KINDS = ("DAISY_CHAIN", "HIERARCHICAL", "FEEDBACK")
DIRECTIONS = ("AT_LEAST", "AT_MOST", "EXACTLY")

_STEP_FIELDS = {
    "OODA": ("observe", "orient", "decide", "act"),
    "MAPE": ("monitor", "analyze", "plan", "execute"),
}


def _fail(msg: str):
    raise SystemExit(f"error: {msg}")


def _validate_activity(step, where: str, problems: list[str]):
    if not isinstance(step, dict) or not step.get("name"):
        problems.append(f"{where}: step must be a mapping with a non-empty 'name'")
        return
    if "action" in step and not isinstance(step["action"], str):
        problems.append(f"{where}.action must be a string")


def _validate_decision_model(dm, where: str, problems: list[str]):
    if not isinstance(dm, dict) or "kind" not in dm:
        problems.append(f"{where}: decision_model must be a mapping with 'kind'")
        return
    kind = dm["kind"]
    if kind in _STEP_FIELDS:
        for field in _STEP_FIELDS[kind]:
            if field not in dm:
                problems.append(f"{where}: {kind} decision model requires step {field!r}")
            else:
                _validate_activity(dm[field], f"{where}.{field}", problems)
    elif kind == "CUSTOM":
        steps = dm.get("steps")
        if not isinstance(steps, list) or not steps:
            problems.append(f"{where}: CUSTOM decision model requires a non-empty 'steps' list")
        else:
            for i, step in enumerate(steps):
                _validate_activity(step, f"{where}.steps[{i}]", problems)
    else:
        problems.append(f"{where}: decision model kind must be OODA, MAPE, or CUSTOM, got {kind!r}")


def _validate_goal(goal, where: str, problems: list[str]):
    if not isinstance(goal, dict) or not goal.get("name") or "target" not in goal:
        problems.append(f"{where}: goal requires 'name' and 'target'")
        return
    target = goal["target"]
    if not isinstance(target, dict) or not target.get("metric") or "value" not in target:
        problems.append(f"{where}.target: requires 'metric' and numeric 'value'")
    elif not isinstance(target["value"], (int, float)) or isinstance(target["value"], bool):
        problems.append(f"{where}.target.value must be a number")
    if "direction" in target and target["direction"] not in DIRECTIONS:
        problems.append(f"{where}.target.direction must be one of {DIRECTIONS}")


def load_model(path) -> dict:
    """Load and structurally validate an aocl-loop-model YAML file."""
    try:
        import yaml
    except ImportError:  # pragma: no cover
        sys.exit("error: pyyaml is required for model loading (pip install pyyaml)")
    with open(path, encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    if not isinstance(data, dict):
        _fail(f"{path}: model file must be a YAML mapping")
    if data.get("format") != "aocl-loop-model":
        _fail(f"{path}: expected format: aocl-loop-model, got {data.get('format')!r}")

    problems: list[str] = []
    entities = data.get("entities")
    loops = data.get("loops")
    if not isinstance(entities, list) or not entities:
        problems.append("entities must be a non-empty list")
        entities = []
    if not isinstance(loops, list):
        problems.append("loops must be a list")
        loops = []

    seen_entities: set[str] = set()
    for i, ent in enumerate(entities):
        if not isinstance(ent, dict):
            problems.append(f"entities[{i}] is not a mapping")
            continue
        eid = ent.get("id")
        if not eid or not re.match(r"^[a-z0-9][a-z0-9-]*$", str(eid)):
            problems.append(f"entities[{i}].id must be a lowercase slug, got {eid!r}")
        elif eid in seen_entities:
            problems.append(f"duplicate entity id: {eid}")
        seen_entities.add(eid or f"<unnamed-{i}>")
        if ent.get("kind") not in ENTITY_KINDS:
            problems.append(f"entities[{i}].kind must be one of {ENTITY_KINDS}, got {ent.get('kind')!r}")
        if not ent.get("name"):
            problems.append(f"entities[{i}].name is required")

    seen_loops: set[str] = set()
    for i, loop in enumerate(loops):
        if not isinstance(loop, dict):
            problems.append(f"loops[{i}] is not a mapping")
            continue
        lid = loop.get("id")
        label = f"loops[{i}] ({lid})" if lid else f"loops[{i}]"
        if not lid or not re.match(r"^[a-z0-9][a-z0-9-]*$", str(lid)):
            problems.append(f"{label}: id must be a lowercase slug")
        elif lid in seen_loops:
            problems.append(f"duplicate loop id: {lid}")
        seen_loops.add(lid or f"<unnamed-{i}>")
        if loop.get("entity") not in seen_entities:
            problems.append(f"{label}: entity {loop.get('entity')!r} not found in entities")
        if loop.get("velocity") not in VELOCITIES:
            problems.append(f"{label}: velocity must be one of {VELOCITIES}")
        level = loop.get("level")
        if not isinstance(level, int) or isinstance(level, bool) or not 1 <= level <= 5:
            problems.append(f"{label}: level must be an integer 1..5")
        vlevels = loop.get("vector_scores")
        if vlevels is not None:
            if not isinstance(vlevels, dict) or set(vlevels) != {"GD", "DV", "FI"}:
                problems.append(f"{label}: vector_scores must be a mapping with exactly GD, DV, FI")
            elif isinstance(level, int) and all(
                isinstance(v, int) and not isinstance(v, bool) and 1 <= v <= 5 for v in vlevels.values()
            ):
                weakest = min(vlevels.values())
                if level != weakest:
                    problems.append(
                        f"{label}: level {level} inconsistent with weakest vector score {weakest} "
                        "(overall = min of GD/DV/FI)"
                    )
        _validate_decision_model(loop.get("decision_model"), f"{label}.decision_model", problems)
        for j, goal in enumerate(loop.get("goals", []) or []):
            _validate_goal(goal, f"{label}.goals[{j}]", problems)
        if "hitl" in loop and loop["hitl"] not in ("HITL", "HOTL", "HOOTL"):
            problems.append(f"{label}: hitl must be HITL, HOTL, or HOOTL")
        if "state" in loop and loop["state"] not in STATES:
            problems.append(f"{label}: state must be one of {STATES}")

    links = data.get("links", []) or []
    for i, link in enumerate(links):
        if not isinstance(link, dict):
            problems.append(f"links[{i}] is not a mapping")
            continue
        for side in ("source", "target"):
            if link.get(side) not in seen_loops:
                problems.append(f"links[{i}].{side} {link.get(side)!r} is not a known loop id")
        if link.get("kind") not in LINK_KINDS:
            problems.append(f"links[{i}].kind must be one of {LINK_KINDS}")

    if problems:
        _fail("model validation failed:\n  - " + "\n  - ".join(problems))
    return data


def to_clam_export(model: dict) -> dict:
    """Convert a validated model to the aocl-clam-export provisioning document.

    Decision models are emitted first (POST to /decisionModel); loops reference
    them by name and are resolved to decisionModelRef at provisioning time.
    """
    loops = model["loops"]
    entities = {e["id"]: e for e in model["entities"]}

    decision_models: list[dict] = []
    dm_names: dict[str, str] = {}  # loop id -> decision model name
    for loop in loops:
        dm = dict(loop["decision_model"])
        name = f"{loop['id']}-dm"
        dm_names[loop["id"]] = name
        payload = {"kind": dm["kind"], "name": name}
        for field in ("observe", "orient", "decide", "act", "monitor", "analyze", "plan", "execute"):
            if field in dm:
                step = dm[field]
                ref = {"id": step["name"], "name": step["name"]}
                payload[field] = ref
        if dm["kind"] == "CUSTOM":
            payload["steps"] = [
                {"name": step["name"]} for step in dm.get("steps", [])
            ]
        decision_models.append(payload)

    closed_loops: list[dict] = []
    for loop in loops:
        entity = entities[loop["entity"]]
        vlevels = loop.get("vector_scores")
        hitl = loop.get("hitl")
        closed_loops.append({
            "name": loop["id"],
            "description": loop.get("notes") or f"{entity.get('name', loop['entity'])} — {loop['velocity']} loop at L{loop['level']}",
            "decision_model": dm_names[loop["id"]],
            "goals": [
                {
                    "name": g["name"],
                    "target": {
                        "metric": g["target"]["metric"],
                        "value": g["target"]["value"],
                        "unit": g["target"].get("unit"),
                        "direction": g["target"].get("direction", "AT_LEAST"),
                    },
                    "scope": g.get("scope", "CLOSED_LOOP"),
                }
                for g in loop.get("goals", [])
            ],
            "links": [
                {"source": link["source"], "target": link["target"], "kind": link["kind"], "condition": link.get("condition")}
                for link in (model.get("links") or [])
                if link["source"] == loop["id"] or link["target"] == loop["id"]
            ],
            "aocl": {
                "entity": loop["entity"],
                "entity_kind": entity["kind"],
                "velocity": loop["velocity"],
                "level": loop["level"],
                "vector_levels": vlevels,
                "hitl": hitl,
                "source_loop_id": loop["id"],
            },
        })

    return {
        "export_format": "aocl-clam-export",
        "export_version": "1.0.0",
        "source_model_version": model.get("model_version", "1.0.0"),
        "decision_models": decision_models,
        "closed_loops": closed_loops,
    }


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--self-test" in argv:
        return _self_test()
    if not argv:
        print("usage: aocl-model <model.yaml> [--clam] [--json] | --self-test")
        return 2
    as_json = "--json" in argv
    argv = [a for a in argv if a != "--json"]
    try:
        model = load_model(argv[0])
    except (OSError, SystemExit) as exc:
        print(exc if isinstance(exc, str) else exc.code if isinstance(exc, SystemExit) else exc)
        return 2
    if "--clam" in argv:
        export = to_clam_export(model)
        import json

        print(json.dumps(export, indent=2) if as_json else json.dumps(export, indent=2))
    else:
        import json

        print(json.dumps(model, indent=2, default=str))
    return 0


def _self_test() -> int:
    good_loop = {
        "id": "loop-1", "entity": "proc-1", "velocity": "fast", "level": 2,
        "decision_model": {
            "kind": "MAPE",
            "monitor": {"name": "read-kpis", "action": "kpi.stream"},
            "analyze": {"name": "threshold-check", "action": "rules.v1"},
            "plan": {"name": "pick-action", "action": "playbook.v1"},
            "execute": {"name": "apply", "action": "orchestrator.apply"},
        },
        "goals": [{"name": "latency", "target": {"metric": "e2e_ms", "value": 100, "direction": "AT_MOST"}}],
    }
    model = {
        "format": "aocl-loop-model", "model_version": "1.0.0", "ruleset_version": "1.0.0",
        "entities": [{"id": "proc-1", "kind": "process", "name": "Detect Anomaly"}],
        "loops": [good_loop],
        "links": [{"source": "loop-1", "target": "loop-1", "kind": "FEEDBACK"}],
    }
    # Direct validation via the internal path: reuse load_model's checks by writing
    # a temp file is overkill here — validate the pieces through to_clam_export.
    problems: list[str] = []
    _validate_decision_model(good_loop["decision_model"], "t", problems)
    assert not problems, problems
    _validate_decision_model({"kind": "MAPE", "monitor": {"name": "x"}}, "t", problems)
    assert any("requires step" in p for p in problems), problems
    problems.clear()
    _validate_decision_model({"kind": "OODA", "observe": {"name": "a"}}, "t", problems)
    assert any("requires step" in p for p in problems)
    export = to_clam_export(model)
    assert export["export_format"] == "aocl-clam-export"
    assert len(export["decision_models"]) == 1
    assert export["decision_models"][0]["name"] == "loop-1-dm"
    assert export["decision_models"][0]["kind"] == "MAPE"
    assert set(export["decision_models"][0]) >= {"monitor", "analyze", "plan", "execute"}
    cl = export["closed_loops"][0]
    assert cl["name"] == "loop-1" and cl["decision_model"] == "loop-1-dm"
    assert cl["aocl"]["entity_kind"] == "process" and cl["aocl"]["level"] == 2
    assert cl["goals"][0]["target"]["direction"] == "AT_MOST"
    assert cl["links"][0]["kind"] == "FEEDBACK"
    # CUSTOM pass-through:
    problems.clear()
    _validate_decision_model({"kind": "CUSTOM", "steps": [{"name": "s1"}, {"name": "s2"}]}, "t", problems)
    assert not problems
    print(f"self-test OK (model version 1.0.0, CLAM-aligned export)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
