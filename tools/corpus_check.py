#!/usr/bin/env python3
"""Corpus checker (Python engine): runs tests/corpus.json against the aocl engines.
Hard-fails if the corpus ruleset_version differs from the engine's, blocking release
on drift. Mirrors tools/corpus_check.js."""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "src"))

import importlib  # noqa: E402

assess_mod = importlib.import_module("aocl.assess")  # noqa: E402  (aocl.assess attribute is shadowed by the assess() re-export)
real_mod = importlib.import_module("aocl.realization")  # noqa: E402


def main() -> int:
    with open(os.path.join(HERE, "..", "tests", "corpus.json"), encoding="utf-8") as fh:
        corpus = json.load(fh)
    if corpus["ruleset_version"] != assess_mod.RULESET_VERSION:
        print(
            f"corpus (python): FAIL — corpus ruleset {corpus['ruleset_version']} != "
            f"engine ruleset {assess_mod.RULESET_VERSION}; bump the corpus with the engine"
        )
        return 2

    failures = 0
    for case in corpus["assessment_cases"]:
        result = assess_mod.assess(
            case["vector_scores"], current=case.get("current"), velocity=case.get("velocity", "tactical")
        )
        exp = case["expect"]
        checks = [
            ("level", result["level"], exp["level"]),
            ("frontier", result["frontier"], exp["frontier"]),
            ("recommended_decision_model", result["recommended_decision_model"], exp["recommended_decision_model"]),
            ("hitl", result["hitl"], exp["hitl"]),
            ("recommended_move", result["recommended_move"], exp["recommended_move"]),
        ]
        for field, actual, expected in checks:
            if actual != expected:
                print(f"corpus (python): FAIL {case['name']}.{field}: {actual!r} != {expected!r}")
                failures += 1
        for needle in exp["notes_contain"]:
            if not any(needle in n for n in result["notes"]):
                print(f"corpus (python): FAIL {case['name']}: notes missing {needle!r}")
                failures += 1

    for case in corpus["realization_cases"]:
        R = real_mod.realize(case["E"], case["C"], case.get("Vd", 1.0))
        eff = real_mod.effort(R)
        if round(R, 4) != case["expect"]["R"]:
            print(f"corpus (python): FAIL {case['name']}.R: {round(R, 4)} != {case['expect']['R']}")
            failures += 1
        if round(eff, 4) != case["expect"]["effort"]:
            print(f"corpus (python): FAIL {case['name']}.effort: {round(eff, 4)} != {case['expect']['effort']}")
            failures += 1

    invalid = corpus["invalid_inputs"]
    for scores in invalid["vector_scores_out_of_range"] + invalid["vector_scores_non_integer"] + invalid["wrong_vector_count"]:
        try:
            assess_mod.parse_vector_scores(scores)
            print(f"corpus (python): FAIL — accepted invalid vector scores {scores}")
            failures += 1
        except SystemExit:
            pass
    for args in invalid["realization_out_of_range"]:
        try:
            real_mod.realize(args["E"], args["C"], args.get("Vd", 1.0))
            print(f"corpus (python): FAIL — accepted invalid realization input {args}")
            failures += 1
        except SystemExit:
            pass
    try:
        assess_mod.recommended_model(3, invalid["velocity_invalid"])
        print("corpus (python): FAIL — accepted invalid velocity")
        failures += 1
    except SystemExit:
        pass
    try:
        real_mod.required_complexity(invalid["infeasible_target"]["E"], invalid["infeasible_target"]["target_R"])
        print("corpus (python): FAIL — accepted infeasible target")
        failures += 1
    except SystemExit:
        pass

    if failures:
        print(f"corpus (python): {failures} failure(s)")
        return 1
    n = len(corpus["assessment_cases"]) + len(corpus["realization_cases"])
    print(f"corpus (python): {n} cases OK against ruleset {assess_mod.RULESET_VERSION}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
