# AOCL Architecture Baseline

| Document | Status | Establishes |
|---|---|---|
| [Review input (Rev. 1)](AOCL-ARCH-REVIEW-INPUT.md) | reference | The comprehensive architectural review preceding the baseline |
| [AOCL-ARCH-001](AOCL-ARCH-001.md) | Proposed | Conceptual architecture and normative foundation: 7-stage behavioral lifecycle, structural/behavioral distinction, hybrid simulation, three layers, P01–P12 |
| [AOCL-CR-001](AOCL-CR-001.md) | Proposed | Adopts the foundation: identity, canonical definition, normative requirements REQ-001..018, principles |
| [AOCL-CR-002](AOCL-CR-002.md) | Queued | Canonical Closed-Loop Metamodel: the ClosedLoop aggregate, intent/goals/constraints, bindings, validation rules MM-001..018 |
| [AOCL-CR-003](AOCL-CR-003.md) | Queued | Behavioral Lifecycle Metamodel: stage semantics S1–S7, behavioral graph, progression, governance |
| [AOCL-CR-004](AOCL-CR-004.md) | Queued | Control Architecture Metamodel: Plant, Sensor, Observation, Controller, Actuator, Knowledge; configurations and invariants |

Implementation status: CR-002's machine-readable tranche is **implemented and validated** — `schema/canonical-loop.schema.json`, `src/aocl/metamodel.py` (MM-001..018 + migration + ADR-006 binding rule), `examples/canonical-loop.yaml` (acceptance criterion 12). CR-003 and CR-004 are queued for behavioral-lifecycle and control-architecture implementation. Simulation evidence and dispositions: [ADR-006](../decisions/adr-006-simulation-evidence-and-architecture-alignment.md).
