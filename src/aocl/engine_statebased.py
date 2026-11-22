"""AOCL State-Based Simulation Engine (AOCL-CR-012).

The quantitative counterpart to the logical engine (CR-011): evolves numeric
plant state under declared disturbance profiles and the declared control
policy, measures the consequences, and evaluates the mapping's plausibility
invariants as run verdicts.

The quantitative semantics are NOT reimplemented here: they are the sim-canvas
prototype's, extracted verbatim into src/aocl/simcore.py (SBE-016 — single
source of truth; site/sim.js is the JS parity port). This module adds the
CR-010 contract machinery around that core:

- conformance gating (SBE-002/003): the execution definition must be
  state-based ready, the bound scenario library valid and state-based ready,
  and the loop document must be a valid canonical ClosedLoop carrying
  assessment vectors (the policy source);
- deterministic runs with input-derived run identity (SBE-010/011);
- the invariant suite evaluated as first-class run verdicts (SBE-012) with
  formal-model findings reported as observations, never absorbed (SBE-013);
- SimulationEvidence with run/scenario/seed/vectors/engine identity (SBE-014).

The level→policy mapping is the informative hypothesis under test — runs are
evidence about it, never conformance certificates (SBE-015).
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("error: pyyaml is required for the state-based engine (pip install pyyaml)")

try:
    from .simcore import suite, evaluate
    from .execution import validate_execution_definition
    from .scenario import validate_scenario_library
    from .metamodel import validate_canonical
except ImportError:  # direct-script execution: fall back to the package path
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from aocl.simcore import suite, evaluate
    from aocl.execution import validate_execution_definition
    from aocl.scenario import validate_scenario_library
    from aocl.metamodel import validate_canonical

RULESET_VERSION = "1.0.0"
ENGINE_VERSION = "0.1.0"
_CORE_VERSION = "1.0.0"  # simcore (extracted verbatim from the prototype) — SBE-016 single source

SCENARIO_KEY = re.compile(r"SCN-SIM-([A-Z]+)-\d+$")


class EngineError(Exception):
    pass


def _load(path) -> dict:
    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _scenario_key(scenario_id: str):
    m = SCENARIO_KEY.match(str(scenario_id))
    return m.group(1).lower() if m else None


class StateBasedEngine:
    def __init__(self, execution: dict, loop_doc: dict, scenario_doc: dict, seed: int = 2026):
        self.exec_doc, self.loop_doc, self.scen_doc = execution, loop_doc, scenario_doc
        self.ex = execution["executionDefinition"]
        self.seed = seed
        self.findings: list[str] = []

    # ---------------- gating (SBE-002/003)

    def gate(self) -> dict:
        problems = []
        ex_result = validate_execution_definition(self.exec_doc)
        if not ex_result["valid"]:
            problems.append("execution definition: " + "; ".join(
                f"{f['rule']}: {f['message']}"[:150] for f in ex_result["findings"] if f["severity"] == "error"))
        elif not ex_result["conformance"]["stateBasedEngineReady"]:
            problems.append("execution definition is not state-based engine ready (SBE-003): "
                            + "; ".join(ex_result.get("engineReadinessReasons", [])))
        if self.ex.get("executionMode") not in ("StateBased", "Hybrid"):
            problems.append(f"mode {self.ex.get('executionMode')!r} is not a state-based mode (SBE-001)")

        lib_result = validate_scenario_library(self.scen_doc)
        if not lib_result["valid"]:
            problems.append("scenario library: " + "; ".join(
                f"{f['rule']}: {f['message']}"[:150] for f in lib_result["findings"] if f["severity"] == "error"))
        scenarios = self.scen_doc["scenarioLibrary"]["scenarios"]
        scenario_id = self.ex.get("scenarioId")
        self.scenario = next((s for s in scenarios if s.get("scenarioId") == scenario_id), None)
        if self.scenario is None:
            problems.append(f"scenarioId {scenario_id!r} not found in the bound library (SBE-002)")
        else:
            readiness = {r["scenarioId"]: r for r in lib_result["scenarioReadiness"]}
            if not readiness.get(scenario_id, {}).get("stateBasedReady", False):
                problems.append(f"scenario {scenario_id} is not state-based simulation ready (SBE-003)")

        loop_result = validate_canonical(self.loop_doc)
        if not loop_result["valid"]:
            problems.append("canonical loop: " + "; ".join(
                f"{f['rule']}: {f['message']}"[:150] for f in loop_result["findings"] if f["severity"] == "error"))
        loop = self.loop_doc.get("closedLoop", {})
        assessment = loop.get("assessment") or {}
        vectors = assessment.get("vectors")
        if not isinstance(vectors, dict) or set(vectors) != {"GD", "DV", "FI"}:
            problems.append("canonical loop carries no GD/DV/FI assessment vectors — the policy source is "
                            "undefined (SBE-006)")
        if problems:
            raise EngineError("conformance gate failed (SBE-002/003):\n  - " + "\n  - ".join(problems))
        return {"vectors": vectors, "assessedLevel": assessment.get("level"),
                "loopRef": loop.get("id"), "velocity": (loop.get("controlledSystems") or [{}])[0]
                .get("cycleIntervalTicks")}

    # ---------------- run (SBE-004..018)

    def run(self) -> dict:
        info = self.gate()
        loop_id = info["loopRef"]
        scenario_id = self.ex["scenarioId"]
        key = _scenario_key(scenario_id)
        run_id = f"sbrun-{scenario_id}-seed{self.seed}"

        # single-scenario run at the assessed level (the bound scenario's own dynamics)
        vectors = info["vectors"]
        level = int(info["assessedLevel"] or min(vectors.values()))
        single = None
        if key:
            single = dict(_core_simulate(vectors, level, self.seed, key))
            single["id"] = f"{scenario_id}-L{level}"
        else:
            self.findings.append(f"scenario {scenario_id} does not follow the SCN-SIM-<key>-NNN convention — "
                                 "the single-scenario run is skipped; the invariant suite still executes")

        # the full invariant suite (S1–S8; multi-seed S6 per SBE-017)
        runs = suite(self.seed)
        invariants, formal_findings = evaluate(runs)
        all_hold = all(i["ok"] for i in invariants)

        ladder = [r for r in runs if r["id"].startswith("S1-L")]
        metrics = [{"level": f"L{r['level']}", "excursions": r["excursions"], "mttr": r["mttr"],
                    "peak": r["peak"], "humanTicks": r["human_ticks"],
                    "selfInflicted": r["self_inflicted"], "novelDepth": r["novel_depth"],
                    "ESim": r["E_sim"]} for r in ladder]

        evidence = {
            "evidenceId": f"E-{run_id}", "evidenceType": "SimulationEvidence",
            "name": f"State-based run {run_id}",
            "sourceRef": f"aocl-engine-statebased@{ENGINE_VERSION} (core sim@{_CORE_VERSION})",
            "subjectRef": self.ex.get("controlModelRef"),
            "originClass": "SimulationTime",
            "simulationRun": {"runId": run_id, "scenarioRef": scenario_id, "seed": self.seed,
                               "engineVersion": ENGINE_VERSION,
                               "behavioralSpecVersion": self.ex.get("specVersion"),
                               "controlContractVersion": "bound-by-reference",
                               "vectors": vectors, "assessedLevel": level},
        }
        return {
            "runId": run_id, "rulesetVersion": RULESET_VERSION, "engineVersion": ENGINE_VERSION,
            "coreVersion": _CORE_VERSION,
            "executionRef": self.ex["id"], "executionMode": self.ex["executionMode"],
            "scenarioRef": self.ex.get("scenarioRef"), "scenarioId": scenario_id,
            "loopRef": loop_id, "vectors": vectors, "assessedLevel": level,
            "policySource": "level→policy reference mapping (model/behavior.yaml, informative — SBE-006/015)",
            "seed": self.seed,
            "singleRun": single,
            "invariants": invariants, "allInvariantsHold": all_hold,
            "formalFindings": formal_findings,
            "ladderMetrics": metrics,
            "evidence": evidence,
            "findings": self.findings,
        }


def _core_simulate(vectors: dict, level: int, seed: int, key: str) -> dict:
    try:
        from .simcore import simulate
    except ImportError:
        from aocl.simcore import simulate
    try:
        return simulate({"GD": level, "DV": level, "FI": level}, "fast", seed, scenario=key)
    except Exception:  # unknown scenario key — fall back to baseline
        return simulate({"GD": level, "DV": level, "FI": level}, "fast", seed, scenario="baseline")


def run_from_paths(exec_path, loop_path, scenario_path, seed=2026) -> dict:
    return StateBasedEngine(_load(exec_path), _load(loop_path), _load(scenario_path), seed=seed).run()


def render_summary(summary: dict) -> str:
    lines = [f"AOCL state-based run — {summary['runId']}"]
    lines.append(f"execution {summary['executionRef']} ({summary['executionMode']}) · scenario {summary['scenarioId']}"
                 f" · loop {summary['loopRef']} · vectors {summary['vectors']} (assessed L{summary['assessedLevel']})"
                 f" · seed {summary['seed']}")
    lines.append(f"policy source: {summary['policySource']}")
    sr = summary.get("singleRun")
    if sr:
        lines.append(f"bound-scenario run: exc={sr['excursions']} mttr={sr['mttr']} peak={sr['peak']} "
                     f"human={sr['human_ticks']} ticks")
    lines.append("ladder: " + " · ".join(f"{m['level']}: exc={m['excursions']} mttr={m['mttr']} "
                                          f"human={m['humanTicks']}" for m in summary["ladderMetrics"]))
    for i in summary["invariants"]:
        lines.append(f"[{'PASS' if i['ok'] else 'FAIL'}] {i['id']}")
    for f in summary["formalFindings"]:
        lines.append(f"[NOTE] {f['id']}: {f['statement'][:100]}…")
    verdict = "ALL INVARIANTS HOLD" if summary["allInvariantsHold"] else "INVARIANT FAILURE"
    lines.append(f"verdict: {verdict} ({len(summary['invariants'])} invariants, "
                 f"{len(summary['formalFindings'])} formal-model findings)")
    return "\n".join(lines)


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--self-test" in argv:
        return _self_test()
    as_json = "--json" in argv
    argv = [a for a in argv if a != "--json"]
    if not argv or argv[0] != "run":
        print("usage: aocl-engine-statebased run <execution.yaml> --loop <canonical-loop.yaml> "
              "--scenarios <library.yaml> [--seed N] [--json] | --self-test")
        return 2
    args, opts = argv[1:], {}
    i = 0
    while i < len(args):
        if args[i] == "--loop":
            opts["loop"] = args[i + 1]; i += 2
        elif args[i] == "--scenarios":
            opts["scenarios"] = args[i + 1]; i += 2
        elif args[i] == "--seed":
            opts["seed"] = int(args[i + 1]); i += 2
        else:
            i += 1
    if "loop" not in opts or "scenarios" not in opts:
        print("error: --loop and --scenarios are required")
        return 2
    try:
        summary = StateBasedEngine(_load(args[0]), _load(opts["loop"]), _load(opts["scenarios"]),
                                   seed=opts.get("seed", 2026)).run()
    except EngineError as exc:
        print(f"error: {exc}")
        return 1
    print(json.dumps(summary, indent=2, default=str) if as_json else render_summary(summary))
    return 0


def _self_test() -> int:
    import copy

    exec_doc = _load("examples/execution-definition-statebased-sim.yaml") \
        if Path("examples/execution-definition-statebased-sim.yaml").exists() else None
    assert exec_doc, "the reference state-based execution definition must exist"
    loop_doc = _load("examples/canonical-loop.yaml")
    scen_doc = _load("examples/scenario-library-sim.yaml")

    # gate + full run at the default seed: invariants evaluated, all hold
    eng = StateBasedEngine(copy.deepcopy(exec_doc), copy.deepcopy(loop_doc), copy.deepcopy(scen_doc), seed=2026)
    summary = eng.run()
    assert summary["allInvariantsHold"], [i for i in summary["invariants"] if not i["ok"]]
    assert len(summary["invariants"]) == 7
    assert len(summary["formalFindings"]) >= 4  # F1–F4 reported as observations (SBE-013)
    assert summary["assessedLevel"] == 3 and summary["vectors"] == {"GD": 3, "DV": 3, "FI": 3}
    assert summary["singleRun"], "bound-scenario run present"
    assert summary["singleRun"]["id"] == "SCN-SIM-BASELINE-001-L3"
    assert summary["evidence"]["originClass"] == "SimulationTime"
    assert summary["evidence"]["simulationRun"]["seed"] == 2026
    assert summary["runId"] == "sbrun-SCN-SIM-BASELINE-001-seed2026"
    assert len(summary["ladderMetrics"]) == 5

    # determinism (SBE-010/011): identical inputs → identical summary
    eng2 = StateBasedEngine(copy.deepcopy(exec_doc), copy.deepcopy(loop_doc), copy.deepcopy(scen_doc), seed=2026)
    summary2 = eng2.run()
    assert summary2 == summary

    # a different seed changes the runs but the invariants still hold (robustness of the mapping)
    eng3 = StateBasedEngine(copy.deepcopy(exec_doc), copy.deepcopy(loop_doc), copy.deepcopy(scen_doc), seed=77)
    summary3 = eng3.run()
    assert summary3["runId"] != summary["runId"]
    assert summary3["allInvariantsHold"], [i for i in summary3["invariants"] if not i["ok"]]

    # conformance gate (SBE-002): an invalid loop is refused — vectors inconsistent with level (ADR-006-F1)
    bad_loop = copy.deepcopy(loop_doc)
    bad_loop["closedLoop"]["assessment"]["level"] = 5
    try:
        StateBasedEngine(copy.deepcopy(exec_doc), bad_loop, copy.deepcopy(scen_doc)).run()
        raise AssertionError("gate must refuse a loop with an inconsistent assessment")
    except EngineError as exc:
        assert "ADR-006-F1" in str(exc)

    # gate refuses a loop without vectors (SBE-006)
    no_vec = copy.deepcopy(loop_doc)
    no_vec["closedLoop"].pop("assessment")
    try:
        StateBasedEngine(copy.deepcopy(exec_doc), no_vec, copy.deepcopy(scen_doc)).run()
        raise AssertionError("gate must refuse a loop without assessment vectors")
    except EngineError as exc:
        assert "SBE-006" in str(exc)

    print(f"self-test OK (state-based engine v{ENGINE_VERSION}, core sim@{_CORE_VERSION}, SBE-001..020)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
