"""AOCL realization model (INFORMATIVE planning heuristic).

R = sqrt(E^2 + (C*V_d)^2) — the Euclidean norm of the Experience-Complexity vector
with data veracity scaling the complexity term. Harvested from
Autonomous_Operations_and_Closed_Loops v1.2.0 section 4; that section is informative:
planning aid only, never a contractual or certification metric.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys

RULESET_VERSION = "1.0.0"

E_RANGE = (0.0, 1.0)
VD_RANGE = (0.0, 1.0)

# Table 1.1 reference points (theoretical illustrations, not measured benchmarks).
# Note: the published effort column was computed from R rounded to 2 dp (e.g. e^3.63
# = 37.71); this engine computes effort from the unrounded R (e^3.62665... = 37.59).
REFERENCE_POINTS = (
    {"level": "L1", "name": "Static", "E": 0.10, "C": 0.10, "R": 0.14},
    {"level": "L2", "name": "Reactive", "E": 0.30, "C": 0.40, "R": 0.50},
    {"level": "L3", "name": "Proactive", "E": 0.60, "C": 0.80, "R": 1.00},
    {"level": "L4", "name": "Predictive", "E": 0.80, "C": 1.50, "R": 1.70},
    {"level": "L5", "name": "Pre-emptive", "E": 0.95, "C": 3.50, "R": 3.63},
)


def _check_range(value: float, name: str, lo: float, hi: float) -> float:
    if not lo <= value <= hi:
        raise SystemExit(f"error: {name} must be in [{lo}, {hi}], got {value}")
    return value


def realize(E: float, C: float, Vd: float = 1.0) -> float:
    """R = sqrt(E^2 + (C*Vd)^2)."""
    _check_range(E, "E", *E_RANGE)
    _check_range(Vd, "Vd", *VD_RANGE)
    if C < 0:
        raise SystemExit(f"error: C must be >= 0, got {C}")
    return math.sqrt(E**2 + (C * Vd) ** 2)


def effort(R: float) -> float:
    """Illustrative effort factor e^R (alpha = 1 per the source document)."""
    return math.exp(R)


def experience_from_components(Ed: float, Em: float, Eo: float, Ex: float) -> float:
    """E = sqrt(Ed^2 + Em^2 + Eo^2 + Ex^2), clamped to [0, 1]."""
    raw = math.sqrt(Ed**2 + Em**2 + Eo**2 + Ex**2)
    return min(raw, 1.0)


def complexity_from_components(Cs: float, Cd: float, Cm: float, Cc: float) -> float:
    """C = sqrt(Cs^2 + Cd^2 + Cm^2 + Cc^2)."""
    return math.sqrt(Cs**2 + Cd**2 + Cm**2 + Cc**2)


def sensitivity(E: float, C: float, Vd: float = 1.0) -> dict:
    """Partial derivatives of R at (E, C, Vd). Undefined (all zero) at R = 0."""
    R = realize(E, C, Vd)
    if R == 0:
        return {"dR_dE": 0.0, "dR_dC": 0.0, "dR_dVd": 0.0, "R": 0.0}
    return {
        "dR_dE": E / R,
        "dR_dC": C * Vd**2 / R,
        "dR_dVd": C**2 * Vd / R,
        "R": R,
    }


def required_complexity(E: float, target_R: float, Vd: float = 1.0) -> float:
    """The C needed to reach target_R at experience E: C = sqrt(R^2 - E^2)/Vd."""
    if target_R < E:
        raise SystemExit(
            f"error: target R ({target_R}) is below current experience E ({E}) — "
            "R >= E always, so no complexity can reach it"
        )
    return math.sqrt(target_R**2 - E**2) / Vd


def required_experience(C: float, target_R: float, Vd: float = 1.0) -> float:
    """The E needed to reach target_R at complexity C."""
    inner = target_R**2 - (C * Vd) ** 2
    if inner < 0:
        raise SystemExit(
            f"error: target R ({target_R}) is below the complexity term C*Vd "
            f"({C * Vd}) — R >= C*Vd always, so no experience can reach it"
        )
    return min(math.sqrt(inner), 1.0)


def value_logarithmic(level: float, v_max: float = 1.0, alpha: float = 1.0) -> float:
    """Value(L) = V_max * ln(1 + alpha*L) / ln(1 + alpha*5) — the L1-L3 model."""
    return v_max * math.log(1 + alpha * level) / math.log(1 + alpha * 5)


def value_exponential(level: float, v0: float = 1.0, beta: float = 1.0) -> float:
    """Value(L) = V_0 * exp(beta*(L-3)) — the L>=3 model."""
    return v0 * math.exp(beta * (level - 3))


def nearest_reference(R: float) -> dict:
    """The Table 1.1 reference point with the smallest |R - R_ref|."""
    return min(REFERENCE_POINTS, key=lambda p: abs(p["R"] - R))


def decision_table(E: float, C: float, Vd: float = 1.0,
                   alpha: float = 1.0, beta: float = 1.0) -> dict:
    """The cost-benefit decision table: marginal effort vs marginal value for each
    level transition L(n)→L(n+1), evaluated at the caller's position.

    Effort deltas use the Table 1.1 reference points (or caller-supplied calibrated
    values via --calibrate); value deltas use the research corpus's two value models
    (logarithmic through L3, exponential from L3). The L3→L4 transition is flagged
    as the inflection gate. Informative: the recommendation is only as good as the
    calibration — uncalibrated runs use the corpus reference points and carry the
    'uncalibrated' label.
    """
    _check_range(E, "E", *E_RANGE)
    _check_range(Vd, "Vd", *VD_RANGE)
    if C < 0:
        raise SystemExit(f"error: C must be >= 0, got {C}")
    transitions = []
    for i in range(len(REFERENCE_POINTS) - 1):
        lo, hi = REFERENCE_POINTS[i], REFERENCE_POINTS[i + 1]
        eff_lo, eff_hi = effort(lo["R"]), effort(hi["R"])
        effort_delta = eff_hi / eff_lo  # multiplicative: "how many times more effort"
        if hi["level"] == "L3":
            value_delta = value_exponential(3, 1.0, beta) / max(value_logarithmic(3, 1.0, alpha), 1e-12)
        else:
            hi_l = int(hi["level"][1])
            lo_l = int(lo["level"][1])
            if lo_l < 3 <= hi_l:
                v_lo = value_logarithmic(lo_l, 1.0, alpha)
                v_hi = value_exponential(hi_l, 1.0, beta)
            elif lo_l >= 3:
                v_lo = value_exponential(lo_l, 1.0, beta)
                v_hi = value_exponential(hi_l, 1.0, beta)
            else:
                v_lo = value_logarithmic(lo_l, 1.0, alpha)
                v_hi = value_logarithmic(hi_l, 1.0, alpha)
            value_delta = (v_hi / max(v_lo, 1e-12))
        ratio = value_delta / max(effort_delta, 1e-12)
        transitions.append({
            "transition": f'{lo["level"]}→{hi["level"]}',
            "from": lo["name"], "to": hi["name"],
            "effort_factor_at": {"from": round(eff_lo, 2), "to": round(eff_hi, 2)},
            "effort_multiple": round(effort_delta, 2),
            "value_multiple": round(value_delta, 2),
            "benefit_per_effort": round(ratio, 3),
            "inflection_gate": lo["level"] == "L3",
        })
    r_now = realize(E, C, Vd)
    nearest = nearest_reference(r_now)
    # where the caller stands relative to the ladder
    standing = {
        "realization": round(r_now, 3),
        "nearest_reference": nearest["level"],
        "position_note": "informative — the value side is modeled; the cost side must be calibrated with your own engineering data before investment decisions",
    }
    return {"ruleset_version": RULESET_VERSION,
            "position": standing,
            "transitions": transitions,
            "gate": "L3→L4 is the value-model inflection: logarithmic gains through L1–L3, "
                    "compounding only after. Cross it only with calibration and evidence.",
            "status": "informative decision support — not a contractual or certification metric"}


def _least_squares(xs, ys):
    """Simple least-squares fit y = a + b*x over one variable. Returns (a, b, r2)."""
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sxx = sum((x - mx) ** 2 for x in xs)
    b = sxy / sxx if sxx else 0.0
    a = my - b * mx
    ss_tot = sum((y - my) ** 2 for y in ys)
    ss_res = sum((y - (a + b * x)) ** 2 for x, y in zip(xs, ys))
    r2 = 1 - ss_res / ss_tot if ss_tot else 1.0
    return a, b, r2


def fit_curve_shape(points) -> dict:
    """Classify the cost-curve shape from cumulative cost-to-reach-level points.

    points: list of {"level": int, "cost": number} (cost = cumulative cost to reach level).
    Fits linear (c = a + b·L), logarithmic (c = a + b·ln L) and exponential
    (c = a·e^(b·L)) shapes; returns the best-supported shape by R² with a
    simplicity tie-break (linear preferred when fits are near-equal).
    """
    pts = sorted((int(p["level"]), float(p["cost"])) for p in points)
    if len(pts) < 3:
        raise SystemExit("error: at least 3 calibrated cost points are required to classify a curve shape")
    xs = [float(l) for l, _c in pts]
    ys = [c for _l, c in pts]

    def r2_of(pred):
        mean_y = sum(ys) / len(ys)
        ss_tot = sum((y - mean_y) ** 2 for y in ys)
        ss_res = sum((y - pred(x)) ** 2 for x, y in zip(xs, ys))
        return 1 - ss_res / ss_tot if ss_tot else 1.0

    a_lin, b_lin, r2_lin = _least_squares(xs, ys)
    lxs = [math.log(x) for x in xs]
    a_log, b_log, r2_log = _least_squares(lxs, ys)
    if all(y > 0 for y in ys):
        lys = [math.log(y) for y in ys]
        a_e, b_e, r2_exp_t = _least_squares(xs, lys)
        a_exp, b_exp = math.exp(a_e), b_e
        r2_exp = r2_of(lambda x: a_exp * math.exp(b_exp * x))
    else:
        a_exp, b_exp, r2_exp = None, None, -1.0

    candidates = [
        {"shape": "linear", "r2": r2_lin, "params": {"a": round(a_lin, 6), "b": round(b_lin, 6)},
         "project": lambda lvl: max(a_lin + b_lin * lvl, 0.0)},
        {"shape": "logarithmic", "r2": r2_log, "params": {"a": round(a_log, 6), "b": round(b_log, 6)},
         "project": lambda lvl: max(a_log + b_log * math.log(lvl), 0.0)},
    ]
    if a_exp is not None:
        candidates.append({"shape": "exponential", "r2": r2_exp,
                           "params": {"a": round(a_exp, 6), "b": round(b_exp, 6)},
                           "project": lambda lvl: max(a_exp * math.exp(b_exp * lvl), 0.0)})
    # simplicity tie-break: prefer the simpler model when R² is within 0.01
    order = ["linear", "logarithmic", "exponential"]
    candidates.sort(key=lambda c: (-round(c["r2"], 4), order.index(c["shape"])))
    best = candidates[0]
    within = abs(candidates[0]["r2"] - candidates[-1]["r2"]) < 0.01 and order.index(candidates[0]["shape"]) > order.index(candidates[-1]["shape"])
    if within and candidates[-1]["r2"] >= candidates[0]["r2"] - 0.01:
        best = candidates[-1] if order.index(candidates[-1]["shape"]) < order.index(candidates[0]["shape"]) else best
    projections = [{"level": f"L{lvl}", "projected_cost": round(best["project"](lvl), 4)}
                   for lvl in range(1, 6)]
    return {"shape": best["shape"], "r2": round(best["r2"], 4), "params": best["params"],
            "supported_shapes": sorted(candidates, key=lambda c: -c["r2"]),
            "projections": projections}


def plan_investment(E, C, Vd, budget, cost_points=None, value_points=None,
                    alpha: float = 1.0, beta: float = 1.0) -> dict:
    """Project the L1-L5 cost/benefit curve against a budget.

    Cost side: the calibrated curve when cost_points are supplied, otherwise the
    research reference points (explicitly labeled uncalibrated).
    Value side: calibrated value points fitted the same way, otherwise the
    research value models (log through L3, exponential from L3), labeled uncalibrated.
    """
    if budget is None or budget < 0:
        raise SystemExit("error: --budget must be a non-negative number")

    if cost_points:
        cost_fit = fit_curve_shape(cost_points)
        cum_cost = {int(p["level"]): float(p["cost"]) for p in cost_points}
        cost_source = "calibrated"
    else:
        cost_fit = {"shape": "reference-illustration", "r2": None,
                    "params": {p["level"]: p["C"] for p in REFERENCE_POINTS}}
        # reference cumulative effort per level from Table 1.1 effort column
        cum_cost = {int(p["level"][1]): effort(p["R"]) for p in REFERENCE_POINTS}
        cost_source = "uncalibrated reference illustration (Table 1.1)"

    if value_points:
        vfit = fit_curve_shape([{"level": p["level"], "cost": p["value"]} for p in value_points])
        cum_value = {int(p["level"]): float(p["value"]) for p in value_points}
        value_source = f"calibrated ({vfit['shape']}, R2={vfit['r2']})"
        project_value = lambda lvl: max(vfit["project"](lvl), 0.0)
    else:
        value_source = "uncalibrated research value models (log through L3, exponential from L3)"
        project_value = lambda lvl: (value_logarithmic(lvl, 1.0, alpha) if lvl <= 3
                                     else value_exponential(lvl, 1.0, beta) / value_exponential(3, 1.0, beta)
                                     * value_logarithmic(3, 1.0, alpha))
        cum_value = {lvl: round(project_value(lvl), 4) for lvl in range(1, 6)}

    rows = []
    for lvl in range(1, 6):
        cost = cum_cost.get(lvl, cum_cost.get(max(cum_cost)))
        value = cum_value.get(lvl, max(cum_value.values()))
        within = cost <= budget
        rows.append({"level": f"L{lvl}", "cumulative_cost": round(cost, 3),
                     "projected_value": round(value, 3),
                     "within_budget": within,
                     "benefit_per_cost": round(value / cost, 3) if cost else None})
    reachable = [r for r in rows if r["within_budget"]]
    max_level = max(int(r["level"][1:]) for r in reachable) if reachable else 0
    marginal = []
    keys = sorted(cum_cost)
    for a, b in zip(keys, keys[1:]):
        dc = cum_cost[b] - cum_cost[a]
        dv = cum_value.get(b, 0) - cum_value.get(a, 0)
        marginal.append({"transition": f"L{a}→L{b}",
                          "marginal_cost": round(dc, 3),
                          "marginal_value": round(dv, 3),
                          "value_per_cost": round(dv / dc, 3) if dc else None})

    position = None
    if E is not None:
        position = {"E": round(E, 3), "C": round(C, 3) if C is not None else None,
                    "Vd": round(Vd, 3), "realization": round(realize(E, C, Vd), 3)}

    return {
        "ruleset_version": RULESET_VERSION,
        "budget": budget,
        "cost_source": cost_source, "cost_shape": cost_fit.get("shape"),
        "cost_fit_r2": cost_fit.get("r2"),
        "value_source": value_source,
        "position": position,
        "rows": rows,
        "max_level_within_budget": f"L{max_level}",
        "marginal_analysis": marginal,
        "status": "informative planning support — calibrate before investment decisions",
    }


def value_band(level: int) -> str:
    """Which value model governs at this maturity level."""
    return "logarithmic" if level <= 3 else "exponential"


def assess_position(E: float, C: float, Vd: float = 1.0, level: int | None = None) -> dict:
    """Full position report: R, effort, sensitivity, nearest reference, band."""
    R = realize(E, C, Vd)
    out = {
        "ruleset_version": RULESET_VERSION,
        "E": round(E, 6),
        "C": round(C, 6),
        "Vd": round(Vd, 6),
        "R": round(R, 4),
        "effort": round(effort(R), 4),
        "sensitivity": {k: round(v, 4) for k, v in sensitivity(E, C, Vd).items()},
        "nearest_reference": {k: nearest_reference(R)[k] for k in ("level", "name", "R")},
        "value_band": value_band(level) if level else None,
        "status": "informative heuristic — not a normative measurement",
    }
    return out


def render(out: dict) -> str:
    lines = [
        "AOCL Realization (informative heuristic)",
        f"Ruleset version: {out['ruleset_version']}",
        f"  E={out['E']}  C={out['C']}  Vd={out['Vd']}",
        f"  R = {out['R']}   effort e^R = {out['effort']}",
        f"  nearest Table 1.1 reference: {out['nearest_reference']['level']} {out['nearest_reference']['name']} (R={out['nearest_reference']['R']})",
        f"  sensitivity: dR/dE={out['sensitivity']['dR_dE']}  dR/dC={out['sensitivity']['dR_dC']}  dR/dVd={out['sensitivity']['dR_dVd']}",
    ]
    if out.get("value_band"):
        lines.append(f"  value band at level: {out['value_band']}")
    lines.append(f"  {out['status']}")
    return "\n".join(lines)


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--self-test" in argv:
        return _self_test()
    parser = argparse.ArgumentParser(prog="aocl-realization")
    parser.add_argument("--E", type=float, default=None, help="Experience index 0..1 (or omit when --Ed..--Ex given)")
    parser.add_argument("--C", type=float, help="Complexity index >= 0 (or omit when --Cs..--Cc given)")
    parser.add_argument("--Vd", type=float, default=1.0, help="Data Veracity Index 0..1 (default 1.0)")
    parser.add_argument("--Ed", "--Em", "--Eo", "--Ex", dest="ecomps", type=float, action="append", default=None, help="Experience components (all four required together)")
    parser.add_argument("--Cs", "--Cd", "--Cm", "--Cc", dest="ccomps", type=float, action="append", default=None, help="Complexity components (all four required together)")
    parser.add_argument("--level", type=int, choices=range(1, 6), default=None, help="Maturity level for the value-band note")
    parser.add_argument("--target", type=float, default=None, help="Solve for required C (given --E) or E (given --C)")
    parser.add_argument("--decide", action="store_true", help="Emit the investment decision table (marginal effort vs value per level transition)")
    parser.add_argument("--plan", action="store_true", help="Project the L1-L5 cost/benefit curve against --budget (calibrated when --cost-points/--value-points are given)")
    parser.add_argument("--budget", type=float, default=None, help="Available cost budget for the planning projection")
    parser.add_argument("--cost-points", default=None, help="JSON file with cumulative cost-to-reach-level points: {\"costs\": [{\"level\": 1, \"cost\": 1.2}, ...]}")
    parser.add_argument("--value-points", default=None, help="JSON file with calibrated cumulative value points (optional)")
    parser.add_argument("--chart", default=None, help="Write the projected cost/benefit chart as an SVG to this path")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    E, C, Vd = args.E, args.C, args.Vd
    if args.ecomps:
        if len(args.ecomps) != 4:
            raise SystemExit("error: --Ed --Em --Eo --Ex (all four) required for component aggregation")
        E = experience_from_components(*args.ecomps)
    if args.ccomps:
        if len(args.ccomps) != 4:
            raise SystemExit("error: --Cs --Cd --Cm --Cc (all four) required for component aggregation")
        C = complexity_from_components(*args.ccomps)
    if getattr(args, "decide", False):
        if E is None:
            raise SystemExit("error: --decide requires --E (your measured experience) and --C (your platform complexity)")
        table = decision_table(E, C, Vd)
        if args.json:
            print(json.dumps(table, indent=2))
        else:
            print("AOCL investment decision table (informative decision support)")
            print(f"  your position: E={E} C={C} Vd={Vd} → R={table['position']['realization']} "
                  f"(nearest reference: {table['position']['nearest_reference']})")
            print("  transition   effort_multiple   value_multiple   benefit/effort")
            for tr in table["transitions"]:
                gate = "  ← INFLECTION GATE" if tr["inflection_gate"] else ""
                print(f"  {tr['transition']:<10}   {tr['effort_multiple']:>6}x          {tr['value_multiple']:>6}x        "
                      f"{tr['benefit_per_effort']:>6}{gate}")
            print(f"  {table['gate']}")
            print(f"  {table['status']}")
        return 0

    if args.plan:
        cost_points = value_points = None
        if args.cost_points:
            cost_points = json.loads(open(args.cost_points, encoding="utf-8").read()).get("costs")
        if args.value_points:
            value_points = json.loads(open(args.value_points, encoding="utf-8").read()).get("values")
        plan = plan_investment(E, C, Vd, args.budget, cost_points, value_points)
        if args.chart:
            from aocl.planchart import plan_chart
            svg = plan_chart(plan)
            with open(args.chart, "w", encoding="utf-8") as fh:
                fh.write(svg)
            plan["chart"] = args.chart
        if args.json:
            print(json.dumps(plan, indent=2))
        else:
            print(f"AOCL investment plan (budget: {args.budget})")
            print(f"  cost side:  {plan['cost_source']}" + (f" — shape: {plan['cost_shape']} (R2={plan['cost_fit_r2']})" if plan.get("cost_shape") else ""))
            print(f"  value side: {plan['value_source']}")
            print(f"  {'level':<6}{'cum.cost':>10}{'proj.value':>12}{'in budget':>11}{'benefit/cost':>14}")
            for row in plan["rows"]:
                print(f"  {row['level']:<6}{row['cumulative_cost']:>10}{row['projected_value']:>12}"
                      f"{str(row['within_budget']):>11}{str(row['benefit_per_cost']):>14}")
            print(f"  → max level within budget: {plan['max_level_within_budget']}")
            print(f"  {plan['status']}")
        return 0

    if args.target is not None:
        c_given = args.C is not None or args.ccomps is not None
        if c_given:
            solved = {"solve": "required_E", "value": round(required_experience(C, args.target, Vd), 4)}
        else:
            solved = {"solve": "required_C", "value": round(required_complexity(E, args.target, Vd), 4)}
        if args.json:
            print(json.dumps(solved, indent=2))
        else:
            print(f"{solved['solve']} = {solved['value']}")
        return 0

    if E is None or C is None:
        raise SystemExit("error: --E and --C are required (use component flags to aggregate first)")

    out = assess_position(E, C, Vd, args.level)
    print(json.dumps(out, indent=2) if args.json else render(out))
    return 0


def _self_test() -> int:
    # Worked example from the source document, section 4.1.3:
    assert round(realize(0.6, 0.8, 0.9), 4) == round(math.sqrt(0.36 + 0.5184), 4)
    assert round(realize(0.6, 0.8, 0.9), 2) == 0.94
    assert round(realize(0.6, 0.8, 0.5), 2) == 0.72
    # Table 1.1 reference rows reproduce from E and C:
    for p in REFERENCE_POINTS:
        assert abs(realize(p["E"], p["C"]) - p["R"]) < 0.01, p
    # Zero limits:
    assert abs(realize(0.8, 0.0) - 0.8) < 1e-12
    assert abs(realize(0.0, 1.2, 1.0) - 1.2) < 1e-12
    # Components aggregate:
    assert abs(experience_from_components(0.3, 0.3, 0.3, 0.3) - 0.6) < 1e-12
    assert abs(complexity_from_components(1.0, 1.0, 1.0, 1.0) - 2.0) < 1e-12
    # Sensitivity at R=1 (E=0.6, C=0.8): dR/dE = 0.6, dR/dC = 0.8
    s = sensitivity(0.6, 0.8)
    assert abs(s["dR_dE"] - 0.6) < 1e-12 and abs(s["dR_dC"] - 0.8) < 1e-12
    # Inverse solver:
    assert abs(required_complexity(0.6, 1.0) - 0.8) < 1e-12
    assert abs(required_experience(0.8, 1.0) - 0.6) < 1e-12
    for bad_target in (0.5,):
        try:
            required_complexity(0.6, bad_target)
            raise AssertionError("expected rejection of infeasible target")
        except SystemExit:
            pass
    # Curve-shape classification: exponential series classified exponential; linear series linear
    fit = fit_curve_shape([{"level": l, "cost": 2 ** (l - 1)} for l in range(1, 6)])
    assert fit["shape"] == "exponential", fit
    fit = fit_curve_shape([{"level": l, "cost": float(l)} for l in range(1, 6)])
    assert fit["shape"] == "linear", fit
    # Planner: budget crossing respects the cumulative curve
    plan = plan_investment(None, None, 1.0, 10.0,
                           cost_points=[{"level": l, "cost": 2 ** (l - 1)} for l in range(1, 6)],
                           value_points=[{"level": l, "value": 0.2 * l} for l in range(1, 6)])
    assert plan["max_level_within_budget"] == "L4", plan["max_level_within_budget"]  # cum 1,3,7,15 → L4 = 15 <= 10? no; cum L3 = 7 <= 10, L4 = 15 > 10
    # Decision table: the L4→L5 effort multiple ≈ 7x (the research corpus's core claim)
    table = decision_table(0.6, 0.8, 0.9)
    t45 = [x for x in table["transitions"] if x["transition"] == "L4→L5"][0]
    assert 6.0 < t45["effort_multiple"] < 8.0, t45
    assert t45["inflection_gate"] is False
    gate = [x for x in table["transitions"] if x["inflection_gate"]]
    assert len(gate) == 1 and gate[0]["transition"] == "L3→L4"
    # Value bands:
    assert value_band(3) == "logarithmic" and value_band(4) == "exponential"
    assert value_band(5) == "exponential"
    for out_of_range in ((1.5, 0.8), (0.6, -1.0)):
        try:
            realize(*out_of_range)
            raise AssertionError("expected rejection of out-of-range input")
        except SystemExit:
            pass
    # Cross-engine version parity with site/scoring.js:
    try:
        import os

        js = os.path.join(os.path.dirname(__file__), "..", "..", "site", "scoring.js")
        with open(js, encoding="utf-8") as fh:
            src = fh.read()
        match = re.search(r'RULESET_VERSION\s*=\s*"([^"]+)"', src)
        assert match and match.group(1) == RULESET_VERSION, "site/scoring.js RULESET_VERSION drift"
    except FileNotFoundError:
        pass
    print(f"self-test OK (ruleset {RULESET_VERSION})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
