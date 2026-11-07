"""SVG chart generation for the AOCL investment planner (stdlib only).

Renders the projected L1-L5 cumulative cost vs projected value curve with the
budget line and the reachable-level marker. Mirrors the hand-rolled SVG style
of site/charts.js so CLI output and site visualization look consistent.
"""

from __future__ import annotations


def _esc(s: str) -> str:
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def plan_chart(plan: dict, width: int = 860, height: int = 380) -> str:
    rows = plan.get("rows", [])
    if not rows:
        return '<svg xmlns="http://www.w3.org/2000/svg"></svg>'
    budget = float(plan.get("budget") or 0)
    pad_l, pad_r, pad_t, pad_b = 64, 18, 34, 44
    levels = [r["level"] for r in rows]
    costs = [r["cumulative_cost"] for r in rows]
    values = [r["projected_value"] for r in rows]
    y_max = max(max(costs, default=1), max(values, default=1), budget or 0) * 1.12 or 1.0

    def X(i: int) -> float:
        return pad_l + (i / max(len(rows) - 1, 1)) * (width - pad_l - pad_r)

    def Y(v: float) -> float:
        return pad_t + (1 - v / y_max) * (height - pad_t - pad_b)

    s = [f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" '
         f'role="img" style="max-width:100%;height:auto;font-family:ui-monospace,Menlo,monospace">']
    s.append(f'<rect x="{pad_l}" y="{pad_t}" width="{width - pad_l - pad_r}" '
             f'height="{height - pad_t - pad_b}" fill="#fafafa" stroke="#e2e8f0"/>')

    # budget line
    if budget > 0:
        yb = Y(budget)
        s.append(f'<line x1="{pad_l}" y1="{yb:.1f}" x2="{width - pad_r}" y2="{yb:.1f}" '
                 f'stroke="#16a34a" stroke-width="1.6" stroke-dasharray="6 3"/>')
        s.append(f'<text x="{pad_l + 6}" y="{yb - 5:.1f}" font-size="10" fill="#166534">'
                 f'budget {budget:g}</text>')

    # projected value line
    s.append('<polyline points="')
    s.append(" ".join(f"{X(i):.1f},{Y(v):.1f}" for i, v in enumerate(values)))
    s.append('" fill="none" stroke="#2563eb" stroke-width="2"/>')
    # cost line
    s.append('<polyline points="')
    s.append(" ".join(f"{X(i):.1f},{Y(c):.1f}" for i, c in enumerate(costs)))
    s.append('" fill="none" stroke="#dc2626" stroke-width="2"/>')

    # markers + reachable flag
    for i, row in enumerate(rows):
        color = "#16a34a" if row["within_budget"] else "#b91c1c"
        s.append(f'<circle cx="{X(i):.1f}" cy="{Y(costs[i]):.1f}" r="4.5" fill="{color}" stroke="#fff"/>')
        s.append(f'<text x="{X(i):.1f}" y="{height - pad_b + 16:.1f}" text-anchor="middle" '
                 f'font-size="11" fill="#64748b">{row["level"]}</text>')
        cross = " ✓" if row["within_budget"] else " ✗"
        s.append(f'<text x="{X(i):.1f}" y="{Y(costs[i]) - 8:.1f}" text-anchor="middle" '
                 f'font-size="9" fill="{color}">{costs[i]:g}{cross}</text>')

    # legend + caption
    s.append(f'<text x="{pad_l}" y="{pad_t - 12}" font-size="12" fill="#4c1d95" font-weight="bold">'
             f'AOCL investment plan — cumulative cost vs projected value per level</text>')
    s.append(f'<text x="{width - pad_r}" y="{height - pad_b + 16:.1f}" text-anchor="end" font-size="9.5" '
             f'fill="#64748b">cost shape: {_esc(plan.get("cost_shape") or plan.get("cost_source", ""))} · '
             f'reachable: {plan.get("max_level_within_budget", "?")}</text>')
    s.append(f'<text x="{pad_l}" y="{height - 6}" font-size="9.5" fill="#64748b">'
             f'red = cumulative cost · blue = projected value · green dots within budget, red dots beyond · '
             f'{_esc(plan.get("status", ""))}</text>')
    s.append("</svg>")
    return "\n".join(s)
