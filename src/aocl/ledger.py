"""AOCL loop ledger: the registry of managed closed loops (schema 1).

Validates a loop-ledger YAML file and reports organizational health:
validity, guardrail hygiene (L3+ loops need guardrails), review staleness,
and vector/level consistency. Modeled on the autonomy-ledger pattern:
the file declares its format with a top-level `schema:` integer.
"""

from __future__ import annotations

import datetime as _dt
import json
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("error: pyyaml is required for aocl-ledger (pip install pyyaml)")

RULESET_VERSION = "1.0.0"
SUPPORTED_SCHEMA_VERSION = 1

STATES = ("designed", "validated", "published", "active", "paused", "error", "retired")
VELOCITIES = ("fast", "tactical", "slow")
ENTITY_KINDS = ("process", "capability", "system", "function")
DECISION_MODELS = ("OODA", "MAPE", "CUSTOM")  # CUSTOM passes through for CLAM compatibility
HITL_MODELS = ("HITL", "HOTL", "HOOTL")
HITL_BY_LEVEL = {1: "HITL", 2: "HITL", 3: "HOTL", 4: "HOTL", 5: "HOOTL"}

REQUIRED_FIELDS = (
    "id", "entity", "entity_kind", "velocity", "level",
    "decision_model", "owner", "state",
)
OPTIONAL_FIELDS = (
    "vector_levels", "hitl", "guardrails", "budget_end_to_end",
    "last_review", "review_cadence_days", "notes",
)

_BUDGETS = {
    "fast": "< 100 ms",
    "tactical": "< 10 min",
    "slow": "< 7 days",
}


def _isodate(value) -> _dt.date | None:
    if isinstance(value, _dt.date):
        return value
    if isinstance(value, str):
        try:
            return _dt.date.fromisoformat(value)
        except ValueError:
            return None
    return None


def _validate_loop(raw, index: int) -> tuple[dict, list[str], list[str]]:
    """Returns (loop, errors, warnings)."""
    problems: list[str] = []
    warnings: list[str] = []
    if not isinstance(raw, dict):
        return {}, [f"loops[{index}] is not a mapping"], []
    lid = raw.get("id")
    label = f"loop {lid!r}" if isinstance(lid, str) and lid else f"loops[{index}]"

    for name in REQUIRED_FIELDS:
        if name not in raw:
            problems.append(f"{label}: missing required field {name!r}")
    if problems:
        return raw, problems, warnings

    if not re.match(r"^[a-z0-9][a-z0-9-]*$", str(lid)):
        problems.append(f"{label}: id must be a lowercase slug")
    if raw["entity_kind"] not in ENTITY_KINDS:
        problems.append(f"{label}: entity_kind must be one of {ENTITY_KINDS}")
    if raw["velocity"] not in VELOCITIES:
        problems.append(f"{label}: velocity must be one of {VELOCITIES}")
    if raw["decision_model"] not in DECISION_MODELS:
        problems.append(f"{label}: decision_model must be one of {DECISION_MODELS}")
    if raw["state"] not in STATES:
        problems.append(f"{label}: state must be one of {STATES}")
    if not isinstance(raw["owner"], str) or not raw["owner"].strip():
        problems.append(f"{label}: owner must be a non-empty string")

    level = raw["level"]
    if not isinstance(level, int) or isinstance(level, bool) or not 1 <= level <= 5:
        problems.append(f"{label}: level must be an integer 1..5, got {level!r}")
        level = None

    vlevels = raw.get("vector_levels")
    if vlevels is not None:
        if not isinstance(vlevels, dict) or set(vlevels) != {"GD", "DV", "FI"}:
            problems.append(f"{label}: vector_levels must be a mapping with exactly GD, DV, FI")
        else:
            for code, val in vlevels.items():
                if not isinstance(val, int) or isinstance(val, bool) or not 1 <= val <= 5:
                    problems.append(f"{label}: vector_levels.{code} must be an integer 1..5")
            if all(isinstance(v, int) and not isinstance(v, bool) and 1 <= v <= 5 for v in vlevels.values()):
                weakest = min(vlevels.values())
                if level is not None and level != weakest:
                    problems.append(
                        f"{label}: level {level} inconsistent with weakest vector level {weakest} "
                        "(overall level = min of GD/DV/FI)"
                    )

    hitl = raw.get("hitl")
    if hitl is not None:
        if hitl not in HITL_MODELS:
            problems.append(f"{label}: hitl must be one of {HITL_MODELS}")
        elif level is not None and hitl != HITL_BY_LEVEL[level]:
            warnings.append(
                f"{label}: hitl {hitl} differs from the level-{level} default "
                f"{HITL_BY_LEVEL[level]} (permitted; recorded)"
            )

    guardrails = raw.get("guardrails", [])
    if guardrails is None:
        guardrails = []
    if not isinstance(guardrails, list) or not all(isinstance(g, str) and g.strip() for g in guardrails):
        problems.append(f"{label}: guardrails must be a list of non-empty strings")
    elif level is not None and level >= 3 and not guardrails:
        problems.append(
            f"{label}: a loop at L{level} without guardrails is not AO-ready "
            "(safety-envelope integrity, assumption 4)"
        )

    if raw["velocity"] == "fast" and not raw.get("budget_end_to_end"):
        warnings.append(f"{label}: fast loop without a recorded end-to-end latency budget")
    if raw.get("budget_end_to_end") and raw.get("budget_end_to_end") != _BUDGETS.get(raw["velocity"]) and raw.get("budget_end_to_end") != "custom":
        warnings.append(
            f"{label}: budget {raw['budget_end_to_end']!r} differs from the {raw['velocity']} "
            f"reference budget {_BUDGETS[raw['velocity']]!r} (permitted; recorded)"
        )

    horizon_ok = True
    if "last_review" in raw and raw["last_review"] is not None:
        parsed = _isodate(raw["last_review"])
        if parsed is None:
            problems.append(f"{label}: last_review must be an ISO date, got {raw['last_review']!r}")
            horizon_ok = False
    cadence = raw.get("review_cadence_days", 90)
    if not isinstance(cadence, int) or isinstance(cadence, bool) or cadence <= 0:
        problems.append(f"{label}: review_cadence_days must be a positive integer")

    unknown = set(raw) - set(REQUIRED_FIELDS) - set(OPTIONAL_FIELDS)
    if unknown:
        problems.append(f"{label}: unknown fields {sorted(unknown)} — ledger schema 1 does not define them")

    _ = horizon_ok  # staleness handled in health_report against --today
    return raw, problems, warnings


def load_ledger(path) -> dict:
    path = Path(path)
    with path.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    if not isinstance(data, dict):
        raise ValueError(f"{path}: ledger must be a YAML mapping with 'schema' and 'loops'")

    schema = data.get("schema")
    warnings: list[str] = []
    if schema is None:
        warnings.append("pre-versioning ledger: no 'schema' field — re-save with 'schema: 1'")
        schema = None
    elif not isinstance(schema, int) or isinstance(schema, bool):
        raise ValueError(f"{path}: 'schema' must be an integer, got {schema!r}")
    elif schema > SUPPORTED_SCHEMA_VERSION:
        raise ValueError(
            f"{path}: ledger schema {schema} is newer than supported schema "
            f"{SUPPORTED_SCHEMA_VERSION} — fail-closed; update the tool"
        )
    elif schema < SUPPORTED_SCHEMA_VERSION:
        warnings.append(f"ledger schema {schema} is older than supported {SUPPORTED_SCHEMA_VERSION}")

    loops_raw = data.get("loops")
    if not isinstance(loops_raw, list):
        raise ValueError(f"{path}: top-level 'loops' must be a list")

    loops, errors, loop_warnings = [], [], []
    for i, raw in enumerate(loops_raw):
        loop, problems, warns = _validate_loop(raw, i)
        loops.append(loop)
        errors.extend(problems)
        loop_warnings.extend(warns)

    ids = [l.get("id") for l in loops if isinstance(l, dict) and l.get("id")]
    duplicates = sorted({i for i in ids if ids.count(i) > 1})
    if duplicates:
        errors.append(f"duplicate loop ids: {duplicates}")

    return {
        "schema_version": schema,
        "loops": loops,
        "errors": errors,
        "warnings": warnings + loop_warnings,
        "source": str(path),
    }


def health_report(ledger: dict, today: _dt.date | None = None) -> dict:
    today = today or _dt.date.today()
    loops = ledger["loops"]
    active = [l for l in loops if l.get("state") == "active"]
    by_level: dict[int, int] = {}
    by_velocity: dict[str, int] = {}
    for l in loops:
        lv = l.get("level")
        if isinstance(lv, int):
            by_level[lv] = by_level.get(lv, 0) + 1
        v = l.get("velocity")
        if isinstance(v, str):
            by_velocity[v] = by_velocity.get(v, 0) + 1

    stale, unhygienic = [], 0
    for l in loops:
        problems = 0
        cadence = l.get("review_cadence_days", 90)
        last = _isodate(l.get("last_review")) if l.get("last_review") else None
        if l.get("state") == "active":
            if last is None:
                stale.append({"id": l["id"], "reason": "active loop has never been reviewed"})
                problems += 1
            elif (today - last).days > cadence:
                stale.append({
                    "id": l["id"],
                    "reason": f"last review {last} is {(today - last).days} days old (cadence {cadence})",
                })
                problems += 1
        if l.get("level", 0) >= 3 and not l.get("guardrails"):
            problems += 1
        unhygienic += problems

    coverage = 0.0
    if loops:
        complete = sum(
            1 for l in loops
            if all(l.get(f) not in (None, "") for f in REQUIRED_FIELDS)
            and (l.get("level", 5) < 3 or bool(l.get("guardrails")))
        )
        coverage = complete / len(loops)

    return {
        "ruleset_version": RULESET_VERSION,
        "schema_version": ledger["schema_version"],
        "schema_warnings": ledger["warnings"],
        "total_loops": len(loops),
        "active": len(active),
        "by_level": {f"L{k}": v for k, v in sorted(by_level.items())},
        "by_velocity": {k: v for k, v in sorted(by_velocity.items())},
        "validity_errors": ledger["errors"],
        "stale_reviews": stale,
        "unhygienic_count": unhygienic,
        "coverage": round(coverage, 4),
        "today": today.isoformat(),
    }


def render(report: dict) -> str:
    lines = [
        "AOCL Loop Ledger Health",
        f"Ruleset version: {report['ruleset_version']}",
        f"Loops: {report['total_loops']} total, {report['active']} active",
    ]
    if report["by_level"]:
        lines.append("By level: " + ", ".join(f"{k}: {v}" for k, v in report["by_level"].items()))
    if report["by_velocity"]:
        lines.append("By velocity: " + ", ".join(f"{k}: {v}" for k, v in report["by_velocity"].items()))
    lines.append(f"Coverage (complete loops): {report['coverage']:.0%}")
    for w in report["schema_warnings"]:
        lines.append(f"warning: {w}")
    for e in report["validity_errors"]:
        lines.append(f"error: {e}")
    for s in report["stale_reviews"]:
        lines.append(f"stale: {s['id']} — {s['reason']}")
    if report["unhygienic_count"]:
        lines.append(f"hygiene findings: {report['unhygienic_count']}")
    lines.append(f"(as of {report['today']})")
    return "\n".join(lines)


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--self-test" in argv:
        return _self_test()
    as_json = "--json" in argv
    argv = [a for a in argv if a != "--json"]
    today = None
    if "--today" in argv:
        i = argv.index("--today")
        today = _dt.date.fromisoformat(argv[i + 1])
        del argv[i : i + 2]
    if not argv:
        print("usage: aocl-ledger <ledger.yaml> [--today YYYY-MM-DD] [--json] | --self-test")
        return 2
    try:
        ledger = load_ledger(argv[0])
    except (OSError, ValueError) as exc:
        print(f"error: {exc}")
        return 2
    report = health_report(ledger, today)
    print(json.dumps(report, indent=2) if as_json else render(report))
    return 1 if (report["validity_errors"] or report["unhygienic_count"] or report["stale_reviews"]) else 0


def _self_test() -> int:
    good = {
        "id": "loop-a", "entity": "proc-1", "entity_kind": "process", "velocity": "fast",
        "level": 3, "decision_model": "MAPE", "owner": "op-lead", "state": "active",
        "guardrails": ["policy bounds enforced"], "budget_end_to_end": "< 100 ms",
        "last_review": "2026-11-01", "review_cadence_days": 90,
    }
    loop, errors, warnings = _validate_loop(dict(good), 0)
    assert not errors and not warnings, (errors, warnings)
    # vector/level consistency:
    bad = dict(good, level=5, vector_levels={"GD": 5, "DV": 5, "FI": 3})
    _, errors, _ = _validate_loop(bad, 0)
    assert any("inconsistent" in e for e in errors)
    # L3 without guardrails is an error:
    _, errors, _ = _validate_loop({k: v for k, v in good.items() if k != "guardrails"}, 0)
    assert any("not AO-ready" in e for e in errors)
    # hitl mismatch is a recorded warning, not an error:
    _, errors, warnings = _validate_loop(dict(good, hitl="HOOTL"), 0)
    assert not errors and any("differs from the level-3 default" in w for w in warnings)
    # L1 without guardrails is fine:
    l1 = dict(good, level=1, velocity="slow")
    _, errors, _ = _validate_loop(l1, 0)
    assert not errors
    # unknown field rejected:
    _, errors, _ = _validate_loop(dict(good, blended_score=9), 0)
    assert any("unknown fields" in e for e in errors)
    # report math with deterministic today:
    ledger = {"schema_version": 1, "loops": [good], "errors": [], "warnings": [], "source": "t"}
    report = health_report(ledger, today=_dt.date(2026, 12, 5))  # 34 days after review
    assert report["stale_reviews"] == [] and report["coverage"] == 1.0
    report = health_report(ledger, today=_dt.date(2027, 2, 1))  # 92 days after
    assert len(report["stale_reviews"]) == 1
    print(f"self-test OK (ruleset {RULESET_VERSION}, ledger schema {SUPPORTED_SCHEMA_VERSION})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
