# Autonomous Operations & Closed Loops - aocl

**Status:** `draft` (v0.1.0) · **License:** Apache-2.0 · **Model ruleset:** 1.0.0

> The interlock in one line: **Autonomous Operations cannot exist without Closed Loops** — loops translate intent into action, action into observation, and observation into learning. Without formally specified, rigorously governed loops, autonomy degenerates into uncontrolled automation: efficient but brittle, capable but unaccountable, powerful but unsafe.

This toolkit formalizes the TechNE Hub introductory guide *Autonomous Operations and Closed Loops* (v1.2.0) as a **versioned computational model** with three capabilities:

1. **Assess** — score a closed loop across three vectors (Goal Decisioning, Data Veracity, Feedback Intelligence) onto the L1–L5 maturity ladder; get the weakest-link overall level, the next frontier, and the suggested decision model (OODA / MAPE) and human-interaction model (HITL/HOTL/HOOTL).
2. **Model** — an interactive visual modeler (browser, fully local) where closed loops are placed on **Processes, Capabilities, Systems, or Functions**, specified in the [Closed-Loop-Management (CLAM)](https://github.com/emmanuel-a-otchere/Closed-Loop-Management) aligned format, and exported as provisioning payloads.
3. **Realize** — the informative realization heuristic `R = √(E² + (C·V_d)²)` with four-vector decompositions, sensitivity, inverse solvers, and graphed analytics.

## Install

```bash
pip install aocl            # runtime dep: pyyaml only
# or zero-install from a checkout:
python3 tools/aocl_score.py --self-test
```

## CLI

```bash
aocl-score 3 4 2 --velocity slow        # assess vectors GD DV FI (1..5 each)
aocl-score 3 3 3 --current 3 --json     # with operating-level comparison
aocl-realization --E 0.6 --C 0.8 --Vd 0.9 --json     # R ≈ 0.94 (doc §4.1.3 worked example)
aocl-realization --E 0.6 --target 1.0   # required complexity to reach a target R
aocl-ledger examples/loops.yaml         # loop registry health (staleness, guardrails, budgets)
aocl-model examples/loops.yaml --clam   # model → CLAM provisioning export
```

## Interactive site

Open [`site/index.html`](https://github.com/technehub-labs/aocl/blob/main/site/index.html) in a browser — or on GitHub Pages. Tabs: **Assess** (questionnaire + scorecard + vector radar), **Realization** (sliders driving the E–C plane, realization curve, effort curve), **Loop Modeler** (place loops on processes/capabilities/systems/functions; specify each loop CLAM-style; export model YAML / CLAM payloads / ledger), **Portfolio** (velocity × maturity scatter, latency budgets). No telemetry, no CDN, no accounts — everything runs locally.

## Naming: three different "MAMA"s — and this repo is none of them

| Identity | What it is | Home |
|---|---|---|
| TechNE Hub **MAMA** project | The industry project (GB1040 family) that produced the source document | TechNE Hub |
| **`mama`** (lowercase) | The *measuring and managing autonomy* method — decision-rights grants; a **related but distinct** instrument | [`emmanuel-a-otchere/measuring-and-managing-autonomy`](https://github.com/emmanuel-a-otchere/measuring-and-managing-autonomy) |
| **MAMA** umbrella org | Measuring Automation & Measuring Autonomy — the umbrella framework org | [Measuring-Automation-Managing-Autonomy](https://github.com/Measuring-Automation-Managing-Autonomy) |
| **AOCL** (this repo) | Closed-loop automation maturity: loop levels, vectors, realization, modeler | here |

A loop's maturity level is **not** an autonomy grant level; the concepts interlock but the scores are never merged. See [docs/naming.md](https://github.com/technehub-labs/aocl/blob/main/docs/naming.md).

## Repository map

| Path | Contents |
|---|---|
| `model/` | The harvested + improved framework as versioned YAML (levels, vectors, realization, velocity, decision models, assessment items, loop-model format) — the code of record |
| `schema/` | JSON Schemas (draft 2020-12) for the loop model, ledger, scorecard export, and CLAM export |
| `src/aocl/` | Python engines: `assess.py`, `realization.py`, `ledger.py`, `model.py` |
| `tools/` | Zero-install shims + golden-corpus runners (Python & JS) + site self-test |
| `site/` | Static interactive app (no build step, offline-first) |
| `docs/` | The formalized framework, with section-level citation of the source document |
| `assets/figures/original/` | The 17 figures as embedded in the source document (provenance) |
| `docs/img/` | Recreated clean SVG figures |
| `tests/corpus.json` | Golden corpus — 16 exact-output cases run against **both** engines; drift blocks release |

## Documentation

[Framework](https://github.com/technehub-labs/aocl/blob/main/docs/framework.md) · [Maturity model](https://github.com/technehub-labs/aocl/blob/main/docs/maturity-model.md) · [Assessment](https://github.com/technehub-labs/aocl/blob/main/docs/assessment.md) · [Realization model](https://github.com/technehub-labs/aocl/blob/main/docs/realization-model.md) · [Loop velocity](https://github.com/technehub-labs/aocl/blob/main/docs/loop-velocity.md) · [Decision models](https://github.com/technehub-labs/aocl/blob/main/docs/decision-models.md) · [Loop modeler](https://github.com/technehub-labs/aocl/blob/main/docs/loop-modeler.md) · [CLAM alignment](https://github.com/technehub-labs/aocl/blob/main/docs/clm-alignment.md) · [Value streams](https://github.com/technehub-labs/aocl/blob/main/docs/value-streams.md) · [Use cases](https://github.com/technehub-labs/aocl/blob/main/docs/use-cases.md) · [AO-ready assumptions](https://github.com/technehub-labs/aocl/blob/main/docs/assumptions.md) · [AOMM mapping](https://github.com/technehub-labs/aocl/blob/main/docs/aomm-mapping.md) · [Ledger format](https://github.com/technehub-labs/aocl/blob/main/docs/ledger-format.md) · [Versioning](https://github.com/technehub-labs/aocl/blob/main/docs/versioning.md) · [Naming](https://github.com/technehub-labs/aocl/blob/main/docs/naming.md) · [Limitations](https://github.com/technehub-labs/aocl/blob/main/docs/limitations.md)

## License

Apache-2.0. The source document is a TechNE Hub asset; this repository holds the formalization with attribution — see [NOTICE](NOTICE) and [docs/limitations.md](https://github.com/technehub-labs/aocl/blob/main/docs/limitations.md).
