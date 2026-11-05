# Changelog — aocl

Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); semver. The release workflow publishes the tagged version's section verbatim as release notes — write it for users. Ruleset and model-format changes follow [docs/versioning.md](docs/versioning.md).

## [Unreleased]

## [0.1.0] — 2026-11-05

### Added (initial release)

- **Loop maturity assessment**: L1–L5 ladder across three vectors (Goal Decisioning, Data Veracity, Feedback Intelligence), weakest-link aggregation, frontier + barrier guidance, decision-model (OODA/MAPE) and HITL recommendations — `aocl-score`.
- **Realization model (informative heuristic)**: R = √(E² + (C·V_d)²) with four-vector E/C decompositions, effort e^R, sensitivity partials, inverse solvers, Table 1.1 reference points, and the logarithmic/exponential value models — `aocl-realization`.
- **Loop ledger** (schema 1): registry of managed closed loops with validity checks, guardrail hygiene (L3+ requires guardrails), review staleness, and portfolio shape — `aocl-ledger`.
- **Loop modeler model**: entities (process/capability/system/function) + loops specified in the CLAM-aligned format (Closed-Loop-Management data model 1.0), with `aocl-clam-export` provisioning payloads — `aocl-model --clam`.
- **Interactive site** (offline-first, no build step): assessment quiz + scorecard + vector radar; realization sliders driving the E–C plane, realization sigmoid, and effort curve; **Loop Modeler** (visual lanes for processes/capabilities/systems/functions, loop chips, full CLAM-shaped loop editor, live portfolio scatter); portfolio + latency-budget views. Parity-tested against the Python engine via the golden corpus.
- **Golden corpus**: 16 exact-output cases (7 assessment, 9 realization incl. the source document's worked examples) run against both engines in CI; cross-grepped RULESET_VERSION parity; drift blocks release.
- **Framework documentation**: 14 docs formalizing the TechNE Hub guide (v1.2.0) — framework, maturity model, assessment, realization model, loop velocity, decision models, loop modeler, CLAM alignment, value streams, use cases, AO-ready assumptions, AOMM mapping, ledger format, versioning, naming, limitations.
- **Figures**: 12 recreated SVG figures + the 17 originals archived with provenance (incl. the Fig. 7 toolbar-artifact note).
- **Pipelines**: CI (Python self-tests + corpus + JS self-test + corpus + schema validation + docs link check), GitHub Pages (gated on site self-test), release (wheel + sdist smoke, PyInstaller binaries for macOS arm64 / Linux x86_64 / Windows x86_64, changelog-extracted notes, SHA256SUMS), manual PyPI trusted publishing.

[0.1.0]: https://github.com/technehub-labs/aocl/releases/tag/v0.1.0
