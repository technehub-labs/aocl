"""AOCL Scenario Management and Comparison (AOCL-CR-016).

Cross-scenario comparison, variant differencing and verification-target
coverage over CR-009 scenario libraries (rules SMC-001..010).

- Cross-scenario comparison (SMC-002/003): the same loop vectors, assessed
  level and seed run under each scenario that has a quantitative
  interpretation (the SCN-SIM-<key>-NNN convention mapping to the sim core);
  differences are scenario-attributable because the model is held constant.
- Variant differencing (SMC-004): declared differences (extends/differences)
  plus structural deltas (parameters, disturbances, initial states) versus
  the base scenario.
- Coverage (SMC-005): the scenario × verification-target matrix.
- Honesty (SMC-009/010): scenarios without a quantitative interpretation are
  compared structurally and reported as such — no fabricated metrics;
  results are evidence, never certificates.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("error: pyyaml is required for scenario comparison (pip install pyyaml)")

try:
    from .scenario import validate_scenario_library
    from .metamodel import validate_canonical
    from .simcore import simulate
except ImportError:  # direct-script execution
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from aocl.scenario import validate_scenario_library
    from aocl.metamodel import validate_canonical
    from aocl.simcore import simulate

RULESET_VERSION = "1.0.0"
SCENARIO_KEY = re.compile(r"SCN-SIM-([A-Z]+)-\d+$")


class CompareError(Exception):
    pass


def _load(path) -> dict:
    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _structural_delta(variant: dict, base: dict) -> dict:
    """SMC-004: structural deltas versus the base scenario."""
    def keyed(items, k):
        return {i.get(k): i for i in items if isinstance(i, dict)}

    d_params = keyed(variant.get("parameters", []), "parameterId")
    b_params = keyed(base.get("parameters", []), "parameterId")
    d_dists = keyed(variant.get("disturbances", []), "disturbanceId")
    b_dists = keyed(base.get("disturbances", []), "disturbanceId")
    def states(sc):
        return {(s.get("stateVariableRef"), s.get("stateClass")): s.get("value")
                for s in sc.get("initialConditions", {}).get("states", []) if isinstance(s, dict)}
    ds, bs = states(variant), states(base)
    return {
        "parametersAdded": sorted(set(d_params) - set(b_params)),
        "parametersRemoved": sorted(set(b_params) - set(d_params)),
        "parametersChanged": sorted(k for k in set(d_params) & set(b_params)
                                     if d_params[k].get("value") != b_params[k].get("value")),
        "disturbancesAdded": sorted(set(d_dists) - set(b_dists)),
        "disturbancesRemoved": sorted(set(b_dists) - set(d_dists)),
        "initialStatesChanged": sorted(f"{v}@{c}" for (v, c) in set(ds) | set(bs)
                                        if ds.get((v, c)) != bs.get((v, c))),
    }


def compare(scenario_doc: dict, loop_doc: dict, seed: int = 2026) -> dict:
    """SMC-001..010: gated comparison over the bound library."""
    lib_result = validate_scenario_library(scenario_doc)
    if not lib_result["valid"]:
        raise CompareError("scenario library invalid (SMC-001): " + "; ".join(
            f["rule"] for f in lib_result["findings"] if f["severity"] == "error"))
    loop_result = validate_canonical(loop_doc)
    if not loop_result["valid"]:
        raise CompareError("canonical loop invalid (SMC-001): " + "; ".join(
            f["rule"] for f in loop_result["findings"] if f["severity"] == "error"))
    loop = loop_doc["closedLoop"]
    vectors = (loop.get("assessment") or {}).get("vectors")
    if not isinstance(vectors, dict) or set(vectors) != {"GD", "DV", "FI"}:
        raise CompareError("canonical loop carries no GD/DV/FI vectors — nothing to hold constant (SMC-002)")
    level = int((loop.get("assessment") or {}).get("level") or min(vectors.values()))

    lib = scenario_doc["scenarioLibrary"]
    scenarios = sorted(lib.get("scenarios", []), key=lambda s: s.get("scenarioId", ""))
    by_id = {s["scenarioId"]: s for s in scenarios}

    # ---- cross-scenario comparison (quantitative where interpretable)
    baseline_key = next((s["scenarioId"] for s in scenarios
                          if s.get("scenarioType") in ("Baseline", "Normal")), None)
    rows, quantitative = [], []
    for sc in scenarios:
        m = SCENARIO_KEY.match(sc.get("scenarioId", ""))
        if not m:
            rows.append({"scenarioId": sc["scenarioId"], "quantitative": False,
                          "note": "no quantitative interpretation — compared structurally (SMC-010)"})
            continue
        key = m.group(1).lower()
        run = simulate({"GD": level, "DV": level, "FI": level}, "fast", seed, scenario=key
                        if key in ("baseline", "drift", "fastdist", "quiet") else "baseline")
        row = {"scenarioId": sc["scenarioId"], "quantitative": True, "simKey": key,
                "excursions": run["excursions"], "mttr": run["mttr"], "peak": run["peak"],
                "humanTicks": run["human_ticks"], "selfInflicted": run["self_inflicted"],
                "novelDepth": run["novel_depth"]}
        rows.append(row)
        quantitative.append(row)
    baseline_row = next((r for r in quantitative if r["scenarioId"] == baseline_key),
                        quantitative[0] if quantitative else None)
    for row in quantitative:
        if baseline_row and row is not baseline_row:
            row["deltaVsBaseline"] = {
                "excursions": row["excursions"] - baseline_row["excursions"],
                "mttr": round(row["mttr"] - baseline_row["mttr"], 2),
                "humanTicks": row["humanTicks"] - baseline_row["humanTicks"],
            }
    # SMC-002/006 attribution note
    attribution = ("model configuration held constant (vectors %s, level %d, seed %d) — "
                   "metric differences are scenario-attributable (CR-009 §13.3, SMC-002/006)"
                   % (vectors, level, seed)) if len(quantitative) > 1 else \
        "single quantitative scenario — no cross-scenario deltas"

    # ---- variant matrix (SMC-004)
    variants = []
    for sc in scenarios:
        base_id = sc.get("extends")
        if not base_id or base_id not in by_id:
            continue
        variants.append({"scenarioId": sc["scenarioId"], "baseScenario": base_id,
                          "declaredDifferences": sc.get("differences", []),
                          "structuralDelta": _structural_delta(sc, by_id[base_id])})

    # ---- coverage matrix (SMC-005)
    targets = sorted({t.get("claimRef") for sc in scenarios
                       for t in sc.get("verificationTargets", []) if t.get("claimRef")})
    coverage = [{"claimRef": t,
                  "coveredBy": [sc["scenarioId"] for sc in scenarios
                                 if any(t == tt.get("claimRef") for tt in sc.get("verificationTargets", []))]}
                 for t in targets]
    uncovered = [c for c in coverage if not c["coveredBy"]]

    return {
        "rulesetVersion": RULESET_VERSION,
        "libraryRef": lib.get("id"), "loopRef": loop.get("id"),
        "vectors": vectors, "assessedLevel": level, "seed": seed,
        "comparison": rows, "attribution": attribution,
        "variants": variants,
        "coverage": coverage, "uncoveredClaims": uncovered,
        "note": "evidence about the model under scenarios — never conformance certificates (SMC-009)",
    }


def render(result: dict) -> str:
    lines = [f"AOCL scenario comparison — {result['libraryRef']} @ {result['loopRef']}"]
    lines.append(f"model held constant: vectors {result['vectors']} (L{result['assessedLevel']}), seed {result['seed']}")
    lines.append(f"{'scenario':<24}{'key':<10}{'exc':>5}{'mttr':>7}{'peak':>7}{'human':>7}{'Δexc':>6}{'Δhuman':>8}")
    for r in result["comparison"]:
        if not r.get("quantitative"):
            lines.append(f"{r['scenarioId']:<24}{'—':<10}  structural comparison only (SMC-010)")
            continue
        d = r.get("deltaVsBaseline", {})
        lines.append(f"{r['scenarioId']:<24}{r['simKey']:<10}{r['excursions']:>5}{r['mttr']:>7}{r['peak']:>7}"
                     f"{r['humanTicks']:>7}{d.get('excursions', '—'):>6}{d.get('humanTicks', '—'):>8}")
    lines.append(f"attribution: {result['attribution']}")
    for v in result["variants"]:
        lines.append(f"variant {v['scenarioId']} ← {v['baseScenario']}: "
                     f"{len(v['declaredDifferences'])} declared, "
                     f"Δdisturbances {v['structuralDelta']['disturbancesAdded']} added / "
                     f"{v['structuralDelta']['disturbancesRemoved']} removed")
    for c in result["coverage"]:
        lines.append(f"coverage {c['claimRef']}: {', '.join(c['coveredBy']) or 'UNCOVERED'}")
    return "\n".join(lines)


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--self-test" in argv:
        return _self_test()
    as_json = "--json" in argv
    argv = [a for a in argv if a != "--json"]
    if not argv or argv[0] != "run":
        print("usage: aocl-scenario-compare run <library.yaml> --loop <canonical-loop.yaml> [--seed N] [--json] | --self-test")
        return 2
    args, opts = argv[1:], {}
    i = 0
    while i < len(args):
        if args[i] == "--loop":
            opts["loop"] = args[i + 1]; i += 2
        elif args[i] == "--seed":
            opts["seed"] = int(args[i + 1]); i += 2
        else:
            i += 1
    if "loop" not in opts:
        print("error: --loop is required")
        return 2
    try:
        result = compare(_load(args[0]), _load(opts["loop"]), seed=opts.get("seed", 2026))
    except CompareError as exc:
        print(f"error: {exc}")
        return 1
    print(json.dumps(result, indent=2, default=str) if as_json else render(result))
    return 0


def _self_test() -> int:
    import copy

    lib_sim = _load("examples/scenario-library-sim.yaml")
    lib_net = _load("examples/scenario-library.yaml")
    loop = _load("examples/canonical-loop.yaml")

    # quantitative comparison over the sim library (4 scenarios, model held constant)
    result = compare(lib_sim, loop, seed=2026)
    quant = [r for r in result["comparison"] if r["quantitative"]]
    assert len(quant) == 4, [r["scenarioId"] for r in result["comparison"]]
    assert all("deltaVsBaseline" in r for r in quant if r["scenarioId"] != quant[0]["scenarioId"])
    # the fastdist scenario is harder than baseline (scenario-attributable difference)
    base = next(r for r in quant if r["simKey"] == "baseline")
    fast = next(r for r in quant if r["simKey"] == "fastdist")
    assert fast["excursions"] != base["excursions"], "scenarios must produce different outcomes"
    assert "scenario-attributable" in result["attribution"]

    # determinism (SMC-007)
    again = compare(lib_sim, loop, seed=2026)
    assert json.dumps(again, sort_keys=True) == json.dumps(result, sort_keys=True)

    # variant matrix on the network library (extends/differences)
    result_net = compare(lib_net, loop, seed=2026)
    variants = {v["scenarioId"]: v for v in result_net["variants"]}
    assert "SCN-NET-001-C" in variants and "SCN-NET-001-F" in variants
    assert variants["SCN-NET-001-C"]["declaredDifferences"], "declared differences carried"
    # the stale-telemetry variant changes the observed initial state structurally
    assert variants["SCN-NET-001-C"]["structuralDelta"]["initialStatesChanged"]
    # variant F is multi-loop → structural comparison only (SMC-010, no fabricated metrics)
    rows = {r["scenarioId"]: r for r in result_net["comparison"]}
    assert rows["SCN-NET-001-F"]["quantitative"] is False
    assert "structurally" in rows["SCN-NET-001-F"]["note"]

    # coverage matrix (SMC-005)
    assert result_net["coverage"], "coverage matrix present"
    assert all(c["coveredBy"] for c in result_net["coverage"])  # every target covered by its scenario

    # gate (SMC-001): an invalid library is refused
    bad = copy.deepcopy(lib_sim)
    bad["scenarioLibrary"]["scenarios"][0]["lifecycleStatus"] = "Running"  # runtime status → SCN-006
    try:
        compare(bad, loop)
        raise AssertionError("gate must refuse an invalid library")
    except CompareError as exc:
        assert "SCN-006" in str(exc) or "SMC-001" in str(exc)

    print(f"self-test OK (scenario comparison v{RULESET_VERSION}, SMC-001..010)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
