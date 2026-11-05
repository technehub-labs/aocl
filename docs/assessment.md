# Assessment: scoring a loop's maturity

**Status:** draft (v0.1.0) · **Instrument:** `model/questions.yaml` · **Engine:** `src/aocl/assess.py` (+ site *Assess* tab)

## What you score

Three vectors, each on the L1–L5 ladder:

| Vector | Focus areas | What it establishes |
|---|---|---|
| **GD** Goal Decisioning | Intent Management · Analytics & Decisioning | How well the loop makes complex, intelligent decisions aligned with desired outcomes |
| **DV** Data Veracity | Observation · Governance & Assurance | The quality and reliability of the data feeding decisions |
| **FI** Feedback Intelligence | Action Execution · Knowledge & Learning | The loop's capacity to learn from outcomes and refine behaviour |

## The instrument

For each vector, five statements (L1→L5) derived from the source document's per-level vector characteristics (§3.2). The instrument is **derived content** — the document defines the characteristics but ships no questionnaire; `model/questions.yaml` carries the provenance.

- **GD**: fixed goals/rigid rules → post-event goal adjustment → scenario anticipation + self-optimization in policy bounds → AI/ML-optimized anticipatory goals → self-set goals with experimental learning.
- **DV**: static, low-trust data → real-time, unquantified accuracy → context-aware, high consistency → multi-source, cleansed → self-curated adaptive data ecosystem.
- **FI**: basic, non-integrated feedback → delayed corrections → predictive risk mitigation → prescriptive insights, continuous learning → autonomous refinement and innovation.

**Scoring rule (ladder):** a vector's level is the **highest rung whose item — and all items below it — hold**. Tick only what demonstrably holds; at **L3 and above, recorded evidence is required** — an unevidenced claim drops the vector one level.

## Aggregation

```
overall_level = min(GD, DV, FI)     # weakest link
```

**This rule is AOCL-derived** — the document characterizes each level with per-vector attributes and warns that *"advancement in loop maturity without corresponding advancement in Data and Culture dimensions is a common failure mode"*. The conservative, honest reading: **a loop is as mature as its least mature vector.** A loop cannot be "L4 with weak data" — it is an L2 loop with an advanced controller, and the ledger says so.

## What the engine returns

```bash
aocl-score 3 4 2 --velocity slow --current 3
```

- `vector_levels` — the three scores as issued (pass-through; never re-scored)
- `level` — the weakest-link overall
- `notes` — weakest-vector callouts, the **next frontier** with its barrier, operating-level comparison (headroom / over-assessment)
- `recommended_decision_model` — OODA or MAPE per the level × velocity mapping
- `hitl` — HITL / HOTL / HOOTL default for the level
- `recommended_move` — the stable, corpus-pinned guidance string per level

The site's *Assess* tab renders the same assessment as a scorecard + vector radar, entirely locally.

## Protocol (adapted from the upstream `mama` assessor discipline)

1. **Score per loop, not per platform** — a platform hosts many loops at different levels.
2. **Independent scoring, then reconcile** — two assessors score separately; disagreements are recorded, not averaged away.
3. **Evidence at L3+** — forecasts, model cards, training pipelines, data-quality dashboards.
4. **Velocity matters** — score with the loop's velocity in mind (a "predictive" fast loop with non-deterministic AI inference is a red flag; see [loop-velocity.md](loop-velocity.md)).
5. **Re-assess on cadence** — the ledger tracks `last_review` and cadence; stale loops surface in `aocl-ledger` health.

## Boundary

An assessment result is a **maturity classification**, not a safety case, not a certification, and not an autonomy grant. Boundary risks (autonomy ≠ safety, composite prohibition) are stated in [limitations.md](limitations.md) and [naming.md](naming.md).
