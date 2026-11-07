# AOCL Architecture Baseline

## Foundation tranche

| Document | Status | Establishes |
|---|---|---|
| [Review input (Rev. 1)](AOCL-ARCH-REVIEW-INPUT.md) | reference | The comprehensive architectural review preceding the baseline |
| [AOCL-ARCH-001](AOCL-ARCH-001.md) | Proposed | Conceptual architecture and normative foundation: 7-stage behavioral lifecycle, structural/behavioral distinction, hybrid simulation, three layers, P01–P12 |
| [AOCL-CR-001](AOCL-CR-001.md) | Proposed | Adopts the foundation: identity, canonical definition, normative requirements REQ-001..018, principles |
| [AOCL-CR-002](AOCL-CR-002.md) | Queued | Canonical Closed-Loop Metamodel: the ClosedLoop aggregate, intent/goals/constraints, bindings, validation rules MM-001..018 |

## Modeling tranche

| Document | Status | Establishes |
|---|---|---|
| [AOCL-CR-003](AOCL-CR-003.md) | Queued | Behavioral Lifecycle Metamodel: stage semantics S1–S7, behavioral graph, progression, governance (BLM-001..030) |
| [AOCL-CR-004](AOCL-CR-004.md) | Queued | Control Architecture Metamodel: Plant, Sensor, Observation, Controller, Actuator, Knowledge; configurations and invariants (CAM-001..030) |
| [AOCL-CR-005](AOCL-CR-005.md) | Queued | Relationship, Constraint and Composition Model: relationship taxonomy, constraint attachment/propagation, composition patterns, shared control scopes, authority integrity (P13–P18, RCM-001..032) |
| [AOCL-CR-006](AOCL-CR-006.md) | Queued | Behavioral Specification Schema: typed behavioral elements over a directed graph, stage coverage, conditions/guards, exceptions, safe states, human participation (P19–P26, BSS-001..036) |
| [AOCL-CR-007](AOCL-CR-007.md) | Queued | Control Contracts and State-Transition Model: control variables and roles, state distinctions (actual/observed/estimated/desired/commanded/verified), transition guards and outcomes, contracts, authority, invariants, safe states (CTM-001..040) |
| [AOCL-CR-008](AOCL-CR-008.md) | Queued | Verification and Evidence Model: Evidence/Verification as first-class, claims/criteria/methods/results, independence classes, simulation-vs-operational evidence (VER-001..050) |
| [AOCL-CR-009](AOCL-CR-009.md) | Queued | Simulation Scenario and Disturbance Model: SimulationScenario, initial conditions, disturbance profiles, event schedules, variants, reproducibility (SCN-001..057) — completes the Modeling stage |

## Engine tranche (next after Modeling approval)

| CR | Deliverable |
|---|---|
| AOCL-CR-010 | Canonical Execution Semantics |
| AOCL-CR-011 | Logical Simulation Engine |
| AOCL-CR-012 | State-Based Simulation Engine |
| AOCL-CR-013 | Simulation Trace and Replay |
| AOCL-CR-014+ | Studio, scenario management, CLAM and enterprise integration |

## Implementation status

- **CR-002's machine-readable tranche is implemented and validated** — `schema/canonical-loop.schema.json`, `src/aocl/metamodel.py` (MM-001..018 + migration + ADR-006 binding rule), `examples/canonical-loop.yaml` (acceptance criterion 12), `examples/loop-modeler-model.yaml` (migration source).
- **Simulation evidence** ([ADR-006](../decisions/adr-006-simulation-evidence-and-architecture-alignment.md)): 7/7 plausibility invariants hold; findings F1–F4 are disposed against this CR sequence (F1 aggregation-binding → CR-002/CR-003 implementation; F2 burden-shift → CR-003; F3 sandbox containment → CR-004/CR-007; F4 velocity fit → CR-002 (done: binding fields) + CR-007).
- **Hybrid simulation** is realized: logical mode (`site/simulation.html`) + state-based mode (`tools/sim_check.py`, `site/sim.js`), parity pinned in `tests/sim-parity.json`.

**Cost-benefit thesis as programme policy** ([ADR-007](../decisions/adr-007-realization-cost-benefit-instrument.md)): realization is the core decision instrument; E/C/V_d measurement anchors bind into CR-006; the L3 investment gate governs L4–L5 tooling and investment (exception-driven, evidence-driven).

Next per the review's sequence: **AOCL-CR-010 (canonical execution semantics)** should be baselined before either simulation engine is formalized, with CR-006 (behavioral specification schema) as the first implementation tranche of the Modeling stack — it is where the current `model/behavior.yaml` semantics graduate into the canonical specification the engines execute, now carrying the E/C/V_d measurement anchors.
