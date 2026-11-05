# Loop Ledger Format (schema 1)

**Status:** draft (v0.1.0) · **Schema:** `schema/loop-ledger.schema.json` · **CLI:** `aocl-ledger`

The ledger is the **registry of managed closed loops** — what is deployed, on what entity, at what maturity, owned by whom, and when it was last reviewed. It mirrors the autonomy-ledger pattern from the lowercase `mama` method (related but distinct — see [naming.md](naming.md)) and is the operational counterpart of the [modeler's design-time model](loop-modeler.md).

## File

```yaml
schema: 1                      # format version; top-level and required
loops:
  - id: loop-anomaly-detect-v1 # required, unique lowercase slug; version (-v2) rather than mutate
    entity: proc-anomaly-detect
    entity_kind: process       # process | capability | system | function
    velocity: fast             # fast | tactical | slow
    level: 3                   # 1..5; if vector_levels present, level must equal min(GD, DV, FI)
    vector_levels: {GD: 3, DV: 3, FI: 3}   # optional
    decision_model: MAPE       # OODA | MAPE | CUSTOM (CUSTOM = CLAM pass-through)
    hitl: HOTL                 # optional; default by level; overrides recorded as warnings
    state: active              # CLAM lifecycle: designed|validated|published|active|paused|error|retired
    owner: assurance-lead      # required, non-empty
    guardrails:                # mandatory in practice at L3+ (error if empty there)
      - policy bounds enforced by orchestrator
      - rollback tested monthly
    budget_end_to_end: "< 100 ms"   # optional; fast loops without one draw a warning
    last_review: 2026-11-01    # ISO date
    review_cadence_days: 90    # default 90
    notes: >
      Predictive signals trigger pre-emptive scaling.
```

## Health report (`aocl-ledger <file> [--today YYYY-MM-DD] [--json]`)

- **Validity** — required fields, enums, id slugs, level ranges, `level` vs `vector_levels` weakest-link consistency, unknown-field rejection
- **Guardrail hygiene** — L3+ loops with empty guardrails are **errors** (assumption 4: safety envelopes are not optional); HITL overrides are recorded warnings
- **Staleness** — active loops whose `last_review` is older than their cadence
- **Coverage** — fraction of loops with all required fields plus guardrails where required
- **Portfolio shape** — counts by level and by velocity

Exit codes: 0 healthy · 1 findings (errors, stale, or unhygienic) · 2 unreadable/invalid. The `--today` flag makes runs deterministic for CI. Schema-version gates mirror the upstream pattern: missing `schema:` warns (pre-versioning), older schemas warn, **newer schemas fail closed**.

## Example

`examples/loops.yaml` ships a reference ledger with three synthetic loops (fast L3 process loop, slow L4 system loop, fast L2 function loop) validated in CI with a pinned `--today`.

## Design-time vs deployed

The [modeler](loop-modeler.md) produces the design-time model; the ledger is the deployed record. Promote a model loop to the ledger when its CLAM lifecycle reaches `active` — same id, same decision-model kind, now with owner, guardrails, and review cadence. A loop in the ledger whose level drifts from its last assessment is exactly what the review cadence exists to catch.
