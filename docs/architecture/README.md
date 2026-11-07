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
| [AOCL-CR-006](AOCL-CR-006.md) | Queued → **implemented** | Behavioral Specification Schema: typed behavioral elements over a directed graph, stage coverage, conditions/guards, exceptions, safe states, human participation (P19–P26, BSS-001..036) |
| [AOCL-CR-007](AOCL-CR-007.md) | Queued → **implemented** | Control Contracts and State-Transition Model: control variables and roles, state distinctions (actual/observed/estimated/desired/commanded/verified), transition guards and outcomes, contracts, authority, invariants, safe states (CTM-001..040) |
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
- **CR-006's machine-readable tranche is implemented and validated** — `schema/behavioral-spec.schema.json` (the BehavioralSpecification contract), `src/aocl/behavior_spec.py` + `aocl-behavior-spec` (BSS-001..036 native validation, four-level conformance §17 with simulation readiness reported separately per BSS-035/036, ADR-007 E/C/V_d anchor integrity, §20 migration), and `examples/behavioral-spec.yaml` (the eight reference patterns A–H, acceptance criterion 24). The pattern-H governed-learning boundary (BSS-030) and the BSS-023 authority rule (an Action's existence grants nothing without an AuthorizedBy reference) are enforced, not just representable.
- **CR-007's machine-readable tranche is implemented and validated** — `schema/control-contract.schema.json` (the control-model contract), `src/aocl/control_contract.py` + `aocl-control-contract` (CTM-001..040 native validation, the seven conformance profiles of §19 reported separately with simulation readiness assessed independently per AD-007-12), and `examples/control-contract.yaml` (the §17 network-assurance reference, acceptance criterion 21). Enforced, not just representable: the six-way state distinction (CTM-008), estimates name their estimator (CTM-012), authority never inferred — every authority reference must resolve to a declared AuthorityDefinition (CTM-028) and overlapping scopes require explicit coordination (CTM-029), execution ≠ outcome via evidential-strength matching of postcondition claims against their supporting signals (AD-007-09), safety/regulatory invariants binding on touching contracts (CTM-033), and units never silently mixed (CTM-006). The §21 migration carries goal reference conditions into Draft skeletons while deliberately NOT converting controlled-system bindings into authority.
- **Simulation evidence** ([ADR-006](../decisions/adr-006-simulation-evidence-and-architecture-alignment.md)): 7/7 plausibility invariants hold; findings F1–F4 are disposed against this CR sequence (F1 aggregation-binding → CR-002/CR-003 implementation; F2 burden-shift → CR-003; F3 sandbox containment → CR-004/CR-007; F4 velocity fit → CR-002 (done: binding fields) + CR-007).
- **Hybrid simulation** is realized: logical mode (`site/simulation.html`) + state-based mode (`tools/sim_check.py`, `site/sim.js`), parity pinned in `tests/sim-parity.json`.

**Cost-benefit thesis as programme policy** ([ADR-007](../decisions/adr-007-realization-cost-benefit-instrument.md)): realization is the core decision instrument; E/C/V_d measurement anchors bind into CR-006; the L3 investment gate governs L4–L5 tooling and investment (exception-driven, evidence-driven).

Next per the review's sequence: **AOCL-CR-008 (verification and evidence)** is the next implementation tranche — CR-007's postconditions, transition outcomes and verification references define exactly what claims the evidence model must support (state observations, execution dispositions, transition completion, postcondition evaluation, goal achievement, safe-state verification), and CR-010 (canonical execution semantics) should still be baselined before either simulation engine is formalized.
