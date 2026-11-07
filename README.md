# Autonomous Operations & Closed Loops - aocl

**Status:** `draft` (v0.1.0) · **License:** Apache-2.0 · **Model ruleset:** 1.0.0

> The interlock in one line: **Autonomous Operations cannot exist without Closed Loops** — loops translate intent into action, action into observation, and observation into learning. Without formally specified, rigorously governed loops, autonomy degenerates into uncontrolled automation: efficient but brittle, capable but unaccountable, powerful but unsafe.

**The core premise:** organizations invest in automating the adaptability, self-governance and decisioning of operational processes and systems — pursuing the Self-X mode with humans out of the loop except *on-the-loop* (policy setting, observability, intent provisioning). The research corpus's central postulate is a **cost-benefit law**: the engineering cost of realizing higher loop maturity rises steeply with sophistication (data-fusion requirements, decisioning models, interwoven loops) — *exponentially in the reference research scenario*, with the actual shape (exponential, logarithmic or linear) depending on domain, scope and environment — while incremental gains diminish until the L3–L4 boundary, where value inflects from logarithmic to compounding. The shape is not assumed: it is **calibrated from your own cost and value data**, and AOCL exists to make that investment decision evidence-based, per loop.

This toolkit formalizes the AOCL foundational research corpus on *Autonomous Operations and Closed Loops* (v1.2.0) as a **versioned computational model** with three capabilities:

> **Research basis:** Closed Loop Automation and Autonomous Operations are established as first-class concepts through the AOCL foundational research — conceived, developed and validated as this programme's own work, not adapted from external standards.

1. **Assess** — score a closed loop across three vectors (Goal Decisioning, Data Veracity, Feedback Intelligence) onto the L1–L5 maturity ladder; get the weakest-link overall level, the next frontier, and the suggested decision model (OODA / MAPE) and human-interaction model (HITL/HOTL/HOOTL).
2. **Model** — an interactive visual modeler (browser, fully local) where closed loops are placed on **Processes, Capabilities, Systems, or Functions**, specified in the [Closed-Loop-Management (CLAM)](https://github.com/emmanuel-a-otchere/Closed-Loop-Management) aligned format, and exported as provisioning payloads.
3. **Decide** — the cost-benefit instrument: the realization model `R = √(E² + (C·V_d)²)` with four-vector decompositions, sensitivity, inverse solvers, marginal effort-vs-value analysis per level transition, and the L3–L4 investment gate (`aocl-realization --decide`).

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

## Simulation canvas

The level→policy mapping is tested, not just asserted: a deterministic discrete-event simulation runs a loop at a chosen (GD, DV, FI) against a live plant (noise, drift, learnable known modes, novel one-shots, humans with response times). Seven plausibility invariants are checked in CI — monotone restoration, burden collapse, the L3/L4 novel-mode discriminator, velocity orthogonality, sandboxed experimentation, policy downflow (exception upflow → playbook conversion, 50% excursion cut), and the veracity multiplier. Findings and formal-model change candidates: [docs/simulation.md](https://github.com/technehub-labs/aocl/blob/main/docs/simulation.md).

```bash
python3 tools/sim_check.py   # batch + invariants
```

## Interactive site

Open [`site/index.html`](https://github.com/technehub-labs/aocl/blob/main/site/index.html) in a browser — or on GitHub Pages. Tabs: **Assess** (questionnaire + scorecard + vector radar), **Realization** (sliders driving the E–C plane, realization curve, effort curve), **Loop Modeler** (place loops on processes/capabilities/systems/functions; specify each loop CLAM-style; export model YAML / CLAM payloads / ledger), **Portfolio** (velocity × maturity scatter, latency budgets). No telemetry, no CDN, no accounts — everything runs locally.

## Canonical metamodel (CR-002, implemented)

The canonical ClosedLoop aggregate is machine-readable and validated: [schema/canonical-loop.schema.json](https://github.com/technehub-labs/aocl/blob/main/schema/canonical-loop.schema.json) (contract) + [src/aocl/metamodel.py](https://github.com/technehub-labs/aocl/blob/main/src/aocl/metamodel.py) (native validator for rules MM-001..018, referential integrity, lifecycle-vs-runtime separation, and the ADR-006 binding rule — vectors first-class, level derived). Migration from the modeler format preserves identifiers and inventories gaps without fabricating them (CR-002 §11).

```bash
aocl-metamodel examples/canonical-loop.yaml          # validate
aocl-metamodel --migrate examples/loop-modeler-model.yaml   # modeler → canonical (Draft)
```

## Behavioral specification (CR-006, implemented)

A loop's behavior is a machine-readable artifact: [schema/behavioral-spec.schema.json](https://github.com/technehub-labs/aocl/blob/main/schema/behavioral-spec.schema.json) (contract) + [src/aocl/behavior_spec.py](https://github.com/technehub-labs/aocl/blob/main/src/aocl/behavior_spec.py) (native validator for rules BSS-001..036). Typed behavioral elements over a directed graph (branching, repetition, parallelism, async waits), stage coverage over the seven canonical responsibilities, exception/safe-state paths, human participation, and governed learning boundaries. Four conformance levels are reported separately (§17): schema / structural / behavioral / **simulation readiness** — a spec can be behaviorally complete and still not simulation-ready until CR-007 contracts and CR-009 scenarios bind (BSS-036). The [reference instance](https://github.com/technehub-labs/aocl/blob/main/examples/behavioral-spec.yaml) demonstrates the eight behavioral patterns (A–H). E/C/V_d measurement anchors (ADR-007) are validated parts of the spec, so it is measurable by construction.

```bash
aocl-behavior-spec examples/behavioral-spec.yaml     # validate (all four conformance levels)
aocl-behavior-spec --migrate examples/loop-modeler-model.yaml   # loop registration → Draft skeleton (§20)
```

## Control contracts and state transitions (CR-007, implemented)

What a loop is *permitted* to control, under what conditions, and how a transition is evaluated: [schema/control-contract.schema.json](https://github.com/technehub-labs/aocl/blob/main/schema/control-contract.schema.json) (contract) + [src/aocl/control_contract.py](https://github.com/technehub-labs/aocl/blob/main/src/aocl/control_contract.py) (native validator for rules CTM-001..040). Typed control variables with explicit roles; the six-way state distinction (actual / observed / estimated / desired / commanded / verified); transitions with guards and governed outcomes; contracts with preconditions, explicit authority, expected effects and postconditions that separate **execution completion from operational outcome** (an acknowledgement is not execution, an execution report is not plant state); scoped authority that is never inferred from relationships, with explicit coordination where scopes overlap; binding safety invariants and verified safe states. Seven conformance profiles (§19) are reported separately, with simulation readiness assessed independently (AD-007-12). The [reference model](https://github.com/technehub-labs/aocl/blob/main/examples/control-contract.yaml) is the §17 network-assurance example.

```bash
aocl-control-contract examples/control-contract.yaml     # validate (all seven profiles)
aocl-control-contract --migrate examples/canonical-loop.yaml   # canonical loop → Draft skeleton (§21)
```

## Verification and evidence (CR-008, implemented)

What can actually be *demonstrated* — not just executed: [schema/evidence-model.schema.json](https://github.com/technehub-labs/aocl/blob/main/schema/evidence-model.schema.json) (contract) + [src/aocl/evidence_model.py](https://github.com/technehub-labs/aocl/blob/main/src/aocl/evidence_model.py) (native validator for rules VER-001..050). Evidence as a first-class concept with governed types, origin classes (design / test / **simulation** / deployment / **operational** / audit) and explicit claim relationships; verifications over specific claims, criteria and methods; results whose governed outcomes keep **failure distinct from insufficient evidence** (Failed / Inconclusive / Conflicting are never collapsed into success). Enforced: execution evidence never establishes an outcome; a commanded state is not an established state; conflicts are preserved, never silently resolved; self-verification is honestly labeled; safety-critical claims need independent assurance; simulation evidence carries its run identity and never substitutes for operational evidence. The [reference model](https://github.com/technehub-labs/aocl/blob/main/examples/evidence-model.yaml) is the §21 network-assurance chain.

```bash
aocl-evidence examples/evidence-model.yaml     # validate (all nine profiles)
aocl-evidence --migrate examples/control-contract.yaml   # control model → Draft skeleton (§22)
```

## Simulation scenarios (CR-009, implemented)

The conditions under which loop behavior is evaluated: [schema/scenario.schema.json](https://github.com/technehub-labs/aocl/blob/main/schema/scenario.schema.json) (contract) + [src/aocl/scenario.py](https://github.com/technehub-labs/aocl/blob/main/src/aocl/scenario.py) (native validator for rules SCN-001..057). Governed, versioned scenarios with explicit initial conditions (actual plant state kept distinct from what the controller observes), typed range-checked parameters, first-class disturbances with governed classifications and an explicit controller-visibility declaration (a simulated controller never sees the scenario's hidden ground truth), event schedules with cycle-checked dependencies, controlled variants, recorded assumptions, and reproducibility with seeds and stable dataset snapshots. **Mode-specific readiness** (§21): a scenario can be logical-simulation-ready while incomplete for state-based simulation. The [reference library](https://github.com/technehub-labs/aocl/blob/main/examples/scenario-library.yaml) carries the §23 congestion-and-recovery scenario and its variants.

```bash
aocl-scenario examples/scenario-library.yaml     # validate (all ten profiles + readiness)
aocl-scenario --migrate model/behavior.yaml      # sim-canvas config → Draft skeletons (§24)
```

## Architecture baseline

[AOCL-ARCH-001](https://github.com/technehub-labs/aocl/blob/main/docs/architecture/AOCL-ARCH-001.md) (Proposed) establishes the normative foundation: a closed-loop **engineering and realization framework** with a seven-stage behavioral lifecycle (Intent, Observe, Analyze, Decide, Execute, **Verify**, **Learn**), structural control architecture distinct from behavioral lifecycle, hybrid logical + state-based simulation, three layers (domain model / engineering engine / studio), and principles P01–P12. [AOCL-CR-001](https://github.com/technehub-labs/aocl/blob/main/docs/architecture/AOCL-CR-001.md) proposes its adoption. The simulation canvas ([findings](https://github.com/technehub-labs/aocl/blob/main/docs/simulation.md), [ADR-006](https://github.com/technehub-labs/aocl/blob/main/docs/decisions/adr-006-simulation-evidence-and-architecture-alignment.md)) is the prototype of ARCH-001's state-based simulation mode and the evidence instrument for the mapping's plausibility. The full CR sequence (CR-001..009 modeling foundation, CR-010..013 engines) is tracked in the [architecture index](https://github.com/technehub-labs/aocl/blob/main/docs/architecture/README.md).

## Naming: three different "MAMA"s — and this repo is none of them

| Identity | What it is | Home |
|---|---|---|
| **AOCL research corpus** | Autonomous Operations & Closed Loops (v1.2.0) | The foundational research that established Closed Loop Automation and Autonomous Operations as first-class concepts — the basis of this toolkit | this repository |
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

[Framework](https://github.com/technehub-labs/aocl/blob/main/docs/framework.md) · [Maturity model](https://github.com/technehub-labs/aocl/blob/main/docs/maturity-model.md) · [Assessment](https://github.com/technehub-labs/aocl/blob/main/docs/assessment.md) · [Realization model](https://github.com/technehub-labs/aocl/blob/main/docs/realization-model.md) · [Loop velocity](https://github.com/technehub-labs/aocl/blob/main/docs/loop-velocity.md) · [Decision models](https://github.com/technehub-labs/aocl/blob/main/docs/decision-models.md) · [Loop modeler](https://github.com/technehub-labs/aocl/blob/main/docs/loop-modeler.md) · [CLAM alignment](https://github.com/technehub-labs/aocl/blob/main/docs/clm-alignment.md) · [Value streams](https://github.com/technehub-labs/aocl/blob/main/docs/value-streams.md) · [Use cases](https://github.com/technehub-labs/aocl/blob/main/docs/use-cases.md) · [Simulation](https://github.com/technehub-labs/aocl/blob/main/docs/simulation.md) · [AO-ready assumptions](https://github.com/technehub-labs/aocl/blob/main/docs/assumptions.md) · [AOMM mapping](https://github.com/technehub-labs/aocl/blob/main/docs/aomm-mapping.md) · [Ledger format](https://github.com/technehub-labs/aocl/blob/main/docs/ledger-format.md) · [Versioning](https://github.com/technehub-labs/aocl/blob/main/docs/versioning.md) · [Naming](https://github.com/technehub-labs/aocl/blob/main/docs/naming.md) · [Limitations](https://github.com/technehub-labs/aocl/blob/main/docs/limitations.md)

## License

Apache-2.0. The concepts of Closed Loop Automation and Autonomous Operations are established as first-class work through the AOCL foundational research corpus; this repository holds their formalization — see [NOTICE](NOTICE) and [docs/limitations.md](https://github.com/technehub-labs/aocl/blob/main/docs/limitations.md).
