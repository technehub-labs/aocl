# Versioning & Compatibility

**Status:** draft (v0.1.0) · Pattern adopted from the `mama` toolkit's versioning constitution

A maturity classification is only useful if scores are **comparable over time**. Two failure modes destroy that: silent drift (rules edited, old scorecards quietly incomparable) and version ambiguity (outputs that don't say which rules produced them). Both are prevented the same way: every instrument carries a version, every output records it, and changes follow a written compatibility policy.

## The versioned surfaces

| What | Constant | Where |
|---|---|---|
| Assessment + realization ruleset | `RULESET_VERSION` (currently `1.0.0`) | `src/aocl/assess.py`, `src/aocl/realization.py`, `site/scoring.js` — cross-grepped both ways in self-tests |
| Model data files | `model_version` | each `model/*.yaml` |
| Loop model format | `model_version` in the file | `schema/loop-model.schema.json` |
| Ledger format | top-level `schema:` integer (currently `1`) | `schema/loop-ledger.schema.json` |
| Exports | `export_version` | `schema/scorecard-export.schema.json`, `schema/clm-export.schema.json` |
| Golden corpus | `corpus_version` + `ruleset_version` gate | `tests/corpus.json` |

## Ruleset policy (semver)

| Change | Bump | Comparability |
|---|---|---|
| Fix that changes no scored output; wording; docs | PATCH | Fully comparable |
| Additive: new optional output fields, new non-scoring notes | MINOR | Fully comparable |
| Re-worded assessment items changing what evidence counts | MINOR + changelog *clarification* entry | Comparable with a footnote; re-run on next review cadence |
| Changed items, level definitions, vector set, aggregation rule, realization formula | **MAJOR** | **Not comparable** — re-baseline required; ships with migration note and (where feasible) an old→new mapping |

## Parity and drift (release blockers)

- `tests/corpus.json` is the single engine-agnostic fixture; **both** `tools/corpus_check.py` and `tools/corpus_check.js` hard-fail when the corpus `ruleset_version` differs from the engine's — a scoring change must bump the corpus in the same change.
- Each engine cross-greps the other's `RULESET_VERSION` literal (Python ↔ JS): version drift fails immediately, not downstream.
- The ledger gate: schema newer than supported → **fail closed**; missing/older → loud warnings.

## External compatibility

- **TechNE Hub source document**: pinned at v1.2.0 in file provenance headers. A new document version is a content review, not an automatic bump.
- **CLAM data model**: pinned at 1.0 (see [clm-alignment.md](clm-alignment.md)). A CLAM MAJOR bump requires a changelog ADR-note + schema updates + corpus cases.
