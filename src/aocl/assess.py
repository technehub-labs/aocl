"""AOCL loop maturity assessment engine (OODA/MAPE decision-model guidance).

Three vectors — Goal Decisioning (GD), Data Veracity (DV), Feedback Intelligence (FI) —
each scored L1..L5. The loop's overall level is the WEAKEST of the three vectors.
See model/levels.yaml and model/vectors.yaml for the harvested definitions.
"""

from __future__ import annotations

import re
import sys

RULESET_VERSION = "1.0.0"

VECTORS = (("GD", "Goal Decisioning"), ("DV", "Data Veracity"), ("FI", "Feedback Intelligence"))
LEVEL_MIN, LEVEL_MAX = 1, 5

LEVEL_NAMES = {1: "Static", 2: "Reactive", 3: "Proactive", 4: "Predictive", 5: "Pre-emptive"}

# Frontier to the next level (doc §3.3); barrier notes in parentheses.
FRONTIERS = {
    1: ("Automation Frontier", "instrumentation, orchestration, rule engines — barrier: organizational trust"),
    2: ("Prediction Frontier", "data science capability, forecast models — barrier: data quality and feature engineering"),
    3: ("Cognition Frontier", "AI/ML infrastructure, model governance, MLOps, explainability — barriers: AI talent scarcity, non-stationary environments"),
    4: ("Autonomy Frontier", "experimentation infrastructure, digital twins, causal inference — barrier: delegating goal-setting to machines"),
}

DECISION_MODELS = ("OODA", "MAPE")  # CUSTOM passes through for CLAM compatibility but is not advised here
VELOCITIES = ("fast", "tactical", "slow")

HITL = {1: "HITL", 2: "HITL", 3: "HOTL", 4: "HOTL", 5: "HOOTL"}


def parse_vector_scores(values) -> dict:
    """Parse 3 integers (GD, DV, FI), each 1..5."""
    if len(values) != len(VECTORS):
        raise SystemExit(
            f"error: expected exactly {len(VECTORS)} vector scores (GD DV FI), got {len(values)}\n"
            "usage: aocl-score GD DV FI   (each 1..5)"
        )
    scores = {}
    for (code, _name), raw in zip(VECTORS, values):
        if isinstance(raw, bool) or not isinstance(raw, (int, str)):
            raise SystemExit(f"error: score for {code} must be an integer, got {raw!r}")
        try:
            score = int(raw)
        except ValueError:
            raise SystemExit(f"error: score for {code} must be an integer, got {raw!r}")
        if not LEVEL_MIN <= score <= LEVEL_MAX:
            raise SystemExit(f"error: score for {code} must be in {LEVEL_MIN}..{LEVEL_MAX}, got {score}")
        scores[code] = score
    return scores


def overall_level(vector_scores: dict) -> int:
    """Weakest link across the three vectors."""
    return min(vector_scores[v] for v, _ in VECTORS)


def frontier(level: int) -> tuple[str, str] | None:
    """(name, barrier note) for the frontier to the next level; None at L5."""
    return FRONTIERS.get(level)


def recommended_model(level: int, velocity: str = "tactical") -> str:
    """(level x velocity) -> suggested decision model. L4-L5 fast loops keep the
    deterministic MAPE skeleton; learning lives in the Slow Loops that parametrize them."""
    if velocity not in VELOCITIES:
        raise SystemExit(f"error: velocity must be one of {VELOCITIES}, got {velocity!r}")
    if level <= 3:
        return "MAPE"
    return "OODA" if velocity in ("tactical", "slow") else "MAPE"


def recommended_hitl(level: int) -> str:
    return HITL[level]


def _recommended_move(level: int) -> str:
    return {
        1: "stabilize: automate thresholds to reach the Automation Frontier (reactive control)",
        2: "predict: add trend analysis and forecasting to cross the Prediction Frontier",
        3: "learn: introduce AI/ML strategy generation to cross the Cognition Frontier",
        4: "delegate: extend autonomy toward goal-setting across the Autonomy Frontier",
        5: "hold: govern at the strategic level; re-review on cadence",
    }[level]


def gap_notes(vector_scores: dict, current: int | None) -> list[str]:
    """Weakest-vector, frontier, and positioning notes."""
    notes: list[str] = []
    level = overall_level(vector_scores)
    weakest_code, weakest_name = min(
        ((v, n) for v, n in VECTORS if vector_scores[v] == level),
        key=lambda t: t[0],
    )
    laggards = [v for v, _ in VECTORS if vector_scores[v] == level]
    if len(laggards) < len(VECTORS):
        names = ", ".join(n for v, n in VECTORS if v in laggards)
        notes.append(f"weakest link: {names} at L{level} — advance the lagging vector(s) before raising the overall level")
    if level < LEVEL_MAX:
        name, barrier = FRONTIERS[level]
        notes.append(f"next: {name} — {barrier}")
    if current is not None:
        if current == 0:
            notes.append("no formal loop in operation: nothing is delegated to the loop yet")
        headroom = level - current
        if headroom > 0:
            notes.append(f"headroom: assessed level exceeds current operation by {headroom}; raise after clean review cycles")
        elif headroom < 0:
            notes.append(f"over-assessment: operating level exceeds assessed level by {-headroom}; reassess the vectors or step the operation down")
        else:
            notes.append("operating level matches assessment: hold and review")
    return notes


def assess(vector_scores: dict, current: int | None = None, velocity: str = "tactical") -> dict:
    """Return the assessment record (the CLI --json shape). Pass-through: the vector
    scores are echoed exactly as issued; nothing here re-scores them."""
    level = overall_level(vector_scores)
    return {
        "ruleset_version": RULESET_VERSION,
        "vector_levels": {v: vector_scores[v] for v, _ in VECTORS},
        "level": level,
        "current_level": current,
        "velocity": velocity,
        "notes": gap_notes(vector_scores, current),
        "frontier": frontier(level)[0] if level < LEVEL_MAX else None,
        "recommended_decision_model": recommended_model(level, velocity),
        "hitl": recommended_hitl(level),
        "recommended_move": _recommended_move(level),
    }


def render(result: dict) -> str:
    lines = [
        "AOCL Loop Maturity Assessment",
        f"Ruleset version: {result['ruleset_version']}",
    ]
    levels = result["vector_levels"]
    for code, name in VECTORS:
        lines.append(f"  {code} {name}: L{levels[code]}")
    lines.append(f"Overall level: L{result['level']} — {LEVEL_NAMES[result['level']]}")
    if result["frontier"]:
        lines.append(f"Next frontier: {result['frontier']}")
    lines.append(f"Recommended decision model: {result['recommended_decision_model']}")
    lines.append(f"Human interaction model: {result['hitl']}")
    lines.append(f"Recommended move: {result['recommended_move']}")
    if result["notes"]:
        lines.append("Notes:")
        lines.extend(f"  - {n}" for n in result["notes"])
    return "\n".join(lines)


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--self-test" in argv:
        return _self_test()
    velocity = "tactical"
    if "--velocity" in argv:
        i = argv.index("--velocity")
        velocity = argv[i + 1]
        del argv[i : i + 2]
    as_json = "--json" in argv
    if as_json:
        argv.remove("--json")
    current = None
    if "--current" in argv:
        i = argv.index("--current")
        try:
            current = int(argv[i + 1])
        except (ValueError, IndexError):
            raise SystemExit("error: --current must be an integer 1..5 (0 = no formal loop)")
        if not 0 <= current <= 5:
            raise SystemExit("error: --current must be an integer 1..5 (0 = no formal loop)")
        del argv[i : i + 2]
    scores = parse_vector_scores(argv)
    result = assess(scores, current=current, velocity=velocity)
    if as_json:
        import json

        print(json.dumps(result, indent=2))
    else:
        print(render(result))
    return 0


def _self_test() -> int:
    assert overall_level({"GD": 3, "DV": 4, "FI": 2}) == 2
    assert overall_level({"GD": 5, "DV": 5, "FI": 5}) == 5
    assert recommended_model(2, "fast") == "MAPE"
    assert recommended_model(4, "slow") == "OODA"
    assert recommended_model(5, "fast") == "MAPE"
    assert recommended_hitl(3) == "HOTL"
    assert recommended_hitl(5) == "HOOTL"
    assert frontier(5) is None and frontier(1)[0] == "Automation Frontier"
    try:
        parse_vector_scores([6, 3, 3])
        raise AssertionError("expected rejection of out-of-range score")
    except SystemExit:
        pass
    try:
        recommended_model(3, "hyper")
        raise AssertionError("expected rejection of bad velocity")
    except SystemExit:
        pass
    r = assess({"GD": 3, "DV": 3, "FI": 3}, current=3)
    assert r["level"] == 3 and r["recommended_decision_model"] == "MAPE"
    # Cross-engine version parity: site/scoring.js must carry the same literal.
    try:
        import os

        js = os.path.join(os.path.dirname(__file__), "..", "..", "site", "scoring.js")
        with open(js, encoding="utf-8") as fh:
            src = fh.read()
        match = re.search(r'RULESET_VERSION\s*=\s*"([^"]+)"', src)
        assert match and match.group(1) == RULESET_VERSION, "site/scoring.js RULESET_VERSION drift"
    except FileNotFoundError:
        pass  # installed wheel/binary: JS not adjacent
    print(f"self-test OK (ruleset {RULESET_VERSION})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
