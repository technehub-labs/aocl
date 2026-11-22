# ADR-008: Formal-Model Finding Decisions (F1–F4) — OPEN

**Status:** OPEN — awaiting decisions (2026-11-23) · **Supersedes:** none · **Context:** [ADR-006](adr-006-simulation-evidence-and-architecture-alignment.md) (disposition of the findings against the CR sequence), [docs/simulation.md](../simulation.md) (the findings), the engines (CR-011/012) that reproduce them on every run

The simulation's four formal-model findings survived every bug fix — they are properties of the model, not the code. ADR-006 disposed them against the CR sequence (F1 → CR-002 binding; F2 → framing; F3 → sandbox attribute; F4 → velocity fit); the machine-readable tranche is now complete, so the decisions can be made against implemented, tested structures. Each decision below lists the finding, the options, and the engineering recommendation. **Nothing here is adopted until decided**; the engines currently implement the vector-gated reading of F1 (informative), and all findings are reported as observations (SBE-013/SMC-009), never silently resolved.

---

## D1 (from F1) — How capabilities gate: vectors vs level

**Finding.** Under min-aggregation, `(GD5, DV1, FI5)` behaves nearly identically to pure L1 — the model cannot express *sophisticated but blind*. Conversely `(GD5, DV2, FI5)` — also min-L2 — behaves *better* than pure L2, because FI4+ gain adaptation and GD5 goals are vector-gated, not level-gated. The aggregation gates some capabilities and leaks others: inconsistent in both directions. The engines implement the vector-gated reading.

**Options.**
- **(a) Vectors-first** *(recommended)*: `(GD, DV, FI)` is the behavioral profile; capabilities gate on individual vectors; `level = min(GD, DV, FI)` remains a derived **reporting** label only (the CR-002 binding rule becomes reporting consistency, not behavioral gating). Most expressive — sophisticated-but-blind becomes expressible and behaves badly, as it should. Matches the engines. Cost: the *meaning* of "a loop is at L4" changes everywhere → ledger/modeler/exports carry an explicit note; assessment outputs label level as derived.
- **(b) Strict level-gating**: every capability keys off the derived level; pure L2 ≡ (GD5, DV2, FI5). Consistent, less expressive; the blind-savant loop stays inexpressible; the engines' current behavior would be reined in.
- **(c) Hybrid**: safety-critical capabilities (containment, escalation) level-gated; adaptive/learning capabilities (FI, GD) vector-gated. Middle ground with a second classification rule to maintain.

**Impact if (a):** `aocl-score` labels level as derived; ledger/modeler/exports annotate; CR-002 binding rule re-labeled as reporting consistency (no schema change — the rule already binds level = min(vectors)); sim engines unchanged (already vector-gated); docs updated.

## D2 (from F2) — The L5 burden claim

**Finding.** With humans out of the loop (HOOTL), routine recovery is the loop's alone — L5's MTTR can exceed L4's human-assisted recovery. Novelty still summons people. Higher autonomy ≠ better restoration.

**Options.**
- **(a) Reframe to routine burden** *(recommended)*: the model claims **"L5 eliminates routine human burden"** (HOOTL novelty-only, E → ~0) — not monotone burden reduction. Levels/README/behavior.yaml/docs updated. Metrics already exist (`human_ticks` + `mttr`); low risk.
- **(b) Reframe + dual metric**: as (a), plus ledger/modeler/exports show human burden and loop-owned recovery as separate columns at every level.
- **(c) Keep monotone framing**: contradicted by the simulation; would require changing the invariant suite to hide the effect.

## D3 (from F3) — Sandboxing as a requirement

**Finding.** The first L5 semantics experimented in production: human burden rose above L4's, breaking plausibility. Assumption 7 (sandboxing) is load-bearing for L5's HOOTL semantics.

**Options.**
- **(a) Normative requirement** *(recommended)*: any L4+ loop claiming exploration/adaptation must **declare its containment mechanism** (behavioral-spec constraint / control-model attribute — the migrated scenario skeletons already carry `sc-*-sandbox` constraints). An un-sandboxed exploration claim is non-conformant; the validators enforce the declaration.
- **(b) Documented assumption**: assumption 7 stays a caveat with warning notes; no validator enforcement.

## D4 (from F4) — Velocity fit before high maturity

**Finding.** Level policy parameters (gain, thresholds, lead times) are velocity-independent; a high-gain L5 policy on a slow cycle accumulates silent unbounded drift under HOOTL (mttr 2860 vs L1's 87 in the mismatch scenario). Escalation windows are engagement policy and must stay level-independent (already the mapping's behavior).

**Options.**
- **(a) Precondition + warning** *(recommended)*: L3+ maturity claims require a **declared velocity fit** (loop cycle vs disturbance dynamics — the CR-002 binding fields `cycleIntervalTicks`/`actuationAuthorityPerCycle` already exist); `aocl-score` warns when high maturity is claimed on a mismatched velocity without a declared fit.
- **(b) Hard gate**: `aocl-score` refuses L3+ without a declared fit — strongest, but blocks informative use on loops that haven't measured cycle dynamics.
- **(c) Informative caveat only**: documented in the docs and levels.yaml policy notes; no tooling enforcement.

---

## Decision record

| Decision | Choice | Date | Consequence notes |
|---|---|---|---|
| D1 (F1) | *pending* | — | — |
| D2 (F2) | *pending* | — | — |
| D3 (F3) | *pending* | — | — |
| D4 (F4) | *pending* | — | — |

**F5 needs no decision**: the L3/L4 known/novel discriminator reproduced cleanly (L3 pre-empts known modes ~84%, novel depth ≈ L2; L4 halves novel depth) — the mapping's sharpest claim holds.

Once decided, this ADR moves to Accepted with the table filled, and the implementation tranche follows (docs + validators + assessment tooling per the chosen options).
