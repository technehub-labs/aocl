# Changelog — aocl

Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); semver. The release workflow publishes the tagged version's section verbatim as release notes — write it for users. Ruleset and model-format changes follow [docs/versioning.md](docs/versioning.md).

## [Unreleased]

### Added

- **Architecture baseline committed** ([ADR-006](docs/decisions/adr-006-simulation-evidence-and-architecture-alignment.md)): AOCL-ARCH-001 (normative foundation — 7-stage behavioral lifecycle, hybrid simulation, P01–P12), AOCL-CR-001 (adoption CR), and the preceding architectural review, under `docs/architecture/`. The simulation is designated the prototype of ARCH-001's state-based simulation mode; findings F1–F4 are disposed against the CR sequence (F1 aggregation-binding → must-resolve in CR-002).
- **Simulation canvas** (`site/simulation.html`, `site/sim.js`): deterministic discrete-event simulation testing the level→policy mapping — vector-driven semantics (GD goals, DV observation quality incl. wrong-direction actions, FI learning), playbook pre-emption, novel containment, sandboxed experimentation, humans by HITL/HOTL/HOOTL, governance (exception upflow → playbook conversion). Parity-verified against the Python engine.
- **Batch invariant runner** (`tools/sim_check.py`): 7 plausibility invariants (restoration monotonicity, burden collapse, novel-mode discriminator, velocity orthogonality, sandboxing, policy downflow, veracity multiplier) + 4 formal-model findings — all 7 hold at the default seed; run in CI.
- **`model/behavior.yaml`** — the behavioral semantics under test (informative), and **`docs/simulation.md`** — the findings report.

## [0.1.1] — 2026-11-06

### Fixed

- README links are absolute GitHub URLs — PyPI renders the README in isolation, so relative links were dead on the project page (description refreshes only on a new upload, hence the version bump).

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
