# AOCL-CR-001 — Establish Canonical Conceptual Foundation and Normative Engineering Principles

> Committed verbatim from the proposed change record (status: Proposed). Adoption record and simulation evidence: [ADR-006](../decisions/adr-006-simulation-evidence-and-architecture-alignment.md).

# Change Request: AOCL-CR-001 — Establish Canonical Conceptual Foundation and Normative Engineering Principles
: Conceptual Foundation and Normative Principles



Proposed change record

Foundation tranche



# AOCL-CR-001 — Establish Canonical Conceptual Foundation and Normative Engineering Principles

**Change ID:** AOCL-CR-001\
**Title:** Establish Canonical Conceptual Foundation and Normative Engineering Principles\
**Repository:** technehub-labs/aocl\
**Change Type:** Foundational / Architectural\
**Priority:** Critical\
**Status:** Proposed\
**Target Baseline:** Next approved AOCL baseline\
**Dependencies:** Existing AOCL conceptual framework, assessment model, domain model and CLAM integration contracts.

---

## 1. Executive Summary

This change establishes the canonical conceptual and engineering foundation of AOCL as a closed-loop engineering and realization framework.

The existing AOCL implementation provides a foundation for closed-loop assessment, registration, decision-model selection, realization analysis and interoperability.

However, the framework requires a more comprehensive and normative conceptual foundation to support executable behavioral models, hybrid simulation and operationally meaningful engineering.

This change formalizes:

1. The canonical definition and boundaries of a closed loop.
2. The distinction between control architecture and behavioral lifecycle.
3. Seven canonical behavioral stages.
4. The structural components of a closed-loop control system.
5. The distinction between decision architectures and canonical behavioral semantics.
6. The normative principles governing model construction and interpretation.
7. The separation of maturity, realization, performance and simulation.
8. The architectural boundaries between AOCL, CLAM and enterprise architecture models.

The resulting foundation will govern subsequent changes to the AOCL metamodel, schemas, validators, simulation engine and visual engineering environment.

## 2. Problem Statement

AOCL must evolve from a framework primarily oriented around loop assessment and registration into a coherent engineering environment.

The existing conceptual foundation recognizes classical feedback control and incorporates decision architectures such as OODA and MAPE.

However, several distinctions require formalization:

- A closed loop versus a workflow or automated sequence.
- Structural control components versus behavioral execution stages.
- Decision-making versus execution.
- Action execution versus outcome verification.
- Runtime state changes versus governed learning.
- Maturity versus operational performance.
- Engineering simulation versus visual animation.
- Engineering representation versus operational lifecycle management.

Without these distinctions, subsequent enhancements risk introducing inconsistent terminology, incomplete behavioral models and simulation implementations that do not faithfully represent closed-loop behavior.

## 3. Change Objectives

### OBJ-001: Establish AOCL identity

Normatively position AOCL as a closed-loop engineering and realization framework.

### OBJ-002: Establish the canonical closed-loop definition

Define the essential properties that distinguish a genuine closed-loop system from automation, workflows and conditional execution.

### OBJ-003: Establish canonical behavioral stages

Adopt the seven-stage behavioral lifecycle:

- Intent.
- Observe.
- Analyze.
- Decide.
- Execute.
- Verify.
- Learn.

### OBJ-004: Separate control architecture from behavioral lifecycle

Establish independent structural and behavioral representations.

### OBJ-005: Formalize control components

Establish the conceptual roles of Plant, Sensor, Observation, Controller, Actuator, Verification and Knowledge.

### OBJ-006: Preserve decision-model extensibility

Retain OODA and MAPE-K while introducing explicit mapping to canonical AOCL behavioral responsibilities.

### OBJ-007: Establish engineering boundaries

Separate AOCL domain semantics, engineering execution, visual interfaces and operational integration.

### OBJ-008: Establish simulation integrity

Make the canonical model the authoritative source of simulation behavior.

## 4. Proposed Normative Requirements

### REQ-001 — Closed-Loop Identity

AOCL SHALL represent a closed loop as a first-class engineering entity.

A closed loop SHALL have an identifiable operational purpose, controlled environment, intent, control mechanism, feedback relationship and outcome-verification mechanism.

### REQ-002 — Intent Grounding

Every closed loop SHALL reference an explicit intent specification.

The specification SHALL identify applicable goals, reference conditions and operating constraints.

### REQ-003 — Controlled System

Every closed loop SHALL identify its controlled system or operational environment.

The controlled system SHALL be distinguishable from its controller.

### REQ-004 — Observable State

The model SHALL distinguish actual controlled-system state from observations and state estimates.

### REQ-005 — Explicit Feedback

The model SHALL explicitly represent how resulting system behavior is observed and returned to the control mechanism.

A feedback relationship SHALL NOT be inferred solely from the existence of sequential activities.

### REQ-006 — Behavioral Lifecycle

AOCL SHALL establish the seven canonical behavioral stages.

Each behavioral specification SHALL identify how the responsibilities of these stages are fulfilled.

### REQ-007 — Flexible Execution

The behavioral model SHALL support:

- Sequential execution.
- Branching.
- Parallel activities.
- Repetition.
- Conditional transitions.
- Asynchronous events.
- Retries.
- Escalation.
- Exception handling.

The canonical stages SHALL NOT impose an inflexible execution sequence.

### REQ-008 — Decision Architecture

AOCL SHALL support OODA, MAPE-K and custom decision architectures.

Decision architectures SHALL map their responsibilities to the canonical AOCL behavioral stages.

### REQ-009 — Control Authority

Every executable control action SHALL be subject to declared authority, applicable constraints and authorization requirements.

### REQ-010 — Outcome Verification

The model SHALL explicitly define how the outcomes of executed actions are evaluated.

Execution success SHALL NOT be treated as proof of operational outcome achievement.

### REQ-011 — Governed Learning

Learning SHALL be represented independently of ordinary state transitions.

Changes to policies, control strategies or decision authority SHALL be subject to explicit governance.

### REQ-012 — Independent Maturity Assessment

AOCL SHALL preserve Goal Decisioning, Data Veracity and Feedback Intelligence as distinct maturity dimensions.

Maturity SHALL NOT be derived directly from simulation performance or realization estimates.

### REQ-013 — Independent Realization Analysis

Realization analysis SHALL remain distinct from maturity, operational effectiveness and simulation results.

The existing informative realization heuristic SHALL retain its non-normative status.

### REQ-014 — Model-First Engineering

The canonical AOCL model SHALL be independent of the visual modeling interface.

All interfaces SHALL consume and produce models conforming to the authoritative domain specification.

### REQ-015 — Simulation Semantics

Simulation behavior SHALL derive from the canonical behavioral and control specifications.

The visual representation SHALL NOT independently implement simulation semantics.

### REQ-016 — Interoperability

AOCL SHALL preserve a technology-independent domain representation and support interoperability with CLAM and governed enterprise architecture references.

### REQ-017 — Reproducibility

Simulation and assessment results SHALL identify the model version and applicable execution configuration.

### REQ-018 — Composability

The model SHALL permit multiple closed loops to be related, coordinated and composed without losing their individual identities and boundaries.

## 5. Normative Principles

This change establishes the following principles:

| Principle | Name                        | Normative statement                                                |
| --------- | --------------------------- | ------------------------------------------------------------------ |
| P01       | Loop Primacy                | Closed loops are first-class engineering entities.                 |
| P02       | Intent Grounding            | Every loop operates against declared intent.                       |
| P03       | Observable State            | Actual state and observed state are distinguishable.               |
| P04       | Explicit Feedback           | Feedback paths are explicitly represented.                         |
| P05       | Behavioral Completeness     | Control responsibilities and behavioral outcomes are identifiable. |
| P06       | Bounded Autonomy            | Autonomous actions operate within declared authority.              |
| P07       | Evidence-Based Verification | Outcomes are evaluated using defined evidence.                     |
| P08       | Controlled Adaptation       | Learning and adaptation are governed.                              |
| P09       | Simulation Fidelity         | Simulation derives from canonical model semantics.                 |
| P10       | Semantic Interoperability   | Models use stable identifiers and explicit contracts.              |
| P11       | Composability               | Closed loops can be composed and coordinated.                      |
| P12       | Reproducibility             | Engineering results can be reproduced from versioned inputs.       |

## 6. Scope

### In Scope

- Canonical definitions.
- Conceptual architecture.
- Normative engineering principles.
- Behavioral lifecycle.
- Structural control architecture.
- Decision architecture boundaries.
- Maturity and realization boundaries.
- Simulation architecture principles.
- CLAM and enterprise architecture boundaries.
- Architectural conformance requirements.

### Out of Scope

The following are intentionally deferred to subsequent changes:

- Complete machine-readable metamodel.
- JSON Schema and YAML schema implementation.
- Detailed behavioral execution semantics.
- Simulation engine implementation.
- Visual canvas implementation.
- Advanced dynamic system modeling.
- Digital twin integration.
- CLAM provisioning enhancements.
- New maturity dimensions.
- Replacement of the existing realization heuristic.

## 7. Architectural Decisions

### ADR-001: AOCL Engineering Identity

**Decision:** Adopt closed-loop engineering and realization framework as the primary identity.

**Rationale:** Assessment alone is insufficient to support behavioral modeling, simulation and realization.

### ADR-002: Hybrid Simulation

**Decision:** Establish logical and state-based simulation as complementary simulation modes.

**Rationale:** Logical simulation validates behavioral completeness, while state-based simulation evaluates control behavior against changing operational conditions.

### ADR-003: Seven-Stage Behavioral Lifecycle

**Decision:** Establish Intent, Observe, Analyze, Decide, Execute, Verify and Learn as canonical behavioral responsibilities.

**Rationale:** This establishes a common behavioral vocabulary without constraining implementations to one decision architecture.

### ADR-004: Model and Runtime Separation

**Decision:** Separate canonical domain semantics from simulation execution and visual presentation.

**Rationale:** This preserves portability, testability and interoperability.

### ADR-005: AOCL and CLAM Separation

**Decision:** AOCL remains the engineering and evaluation environment; CLAM remains the operational management and lifecycle integration boundary.

**Rationale:** Avoid duplicating operational management responsibilities within AOCL.

## 8. Conformance Requirements

An implementation conforms to AOCL-CR-001 when:

1. It recognizes the canonical definition of a closed loop.
2. It distinguishes a closed loop from ordinary workflow automation.
3. It recognizes the seven canonical behavioral stages.
4. It separates behavioral lifecycle from structural control architecture.
5. It distinguishes the plant, controller and actuator.
6. It recognizes explicit feedback relationships.
7. It supports alternative decision architectures.
8. It recognizes outcome verification as a distinct responsibility.
9. It distinguishes learning from ordinary execution.
10. It preserves the existing maturity dimensions.
11. It preserves the separation between maturity and realization.
12. It recognizes model-first simulation architecture.
13. It maintains AOCL and CLAM responsibility boundaries.

## 9. Acceptance Criteria

### AC-001: Conceptual completeness

The approved documentation defines all canonical concepts and their relationships without contradictory definitions.

### AC-002: Behavioral completeness

All seven stages have explicit responsibilities, inputs, outputs and relationships.

### AC-003: Architectural separation

The documentation clearly distinguishes domain model, engineering engine and Studio/integration layers.

### AC-004: Decision-model compatibility

OODA and MAPE-K can be mapped to AOCL behavioral responsibilities without redefining them.

### AC-005: Assessment compatibility

The existing GD, DV and FI assessment model remains conceptually compatible.

### AC-006: Simulation readiness

The conceptual foundation supports logical and state-based simulation without requiring either simulation engine to be implemented in this change.

### AC-007: Interoperability

The AOCL and CLAM boundaries are documented and do not introduce competing ownership of operational lifecycle management.

### AC-008: Traceability

All normative requirements and principles have stable identifiers and are traceable to subsequent metamodel and implementation changes.

## 10. Deliverables

1. Approved AOCL conceptual architecture.
2. Canonical closed-loop definition.
3. Normative principles register.
4. Seven-stage behavioral lifecycle specification.
5. Structural control architecture specification.
6. Decision-model mapping.
7. Architectural boundaries and responsibility definitions.
8. Requirements and acceptance criteria register.
9. Updated architecture documentation and repository navigation.

## 11. Dependencies and Successors

This change establishes the foundation for:

| Successor   | Title                                   | Dependency             |
| ----------- | --------------------------------------- | ---------------------- |
| AOCL-CR-002 | Canonical Closed-Loop Metamodel         | CR-001                 |
| AOCL-CR-003 | Behavioral Lifecycle Metamodel          | CR-001, CR-002         |
| AOCL-CR-004 | Control Architecture Metamodel          | CR-001, CR-002         |
| AOCL-CR-005 | Loop Relationships and Composition      | CR-002, CR-003, CR-004 |
| AOCL-CR-006 | Behavioral Specification Schema         | CR-003                 |
| AOCL-CR-007 | Control Contracts and State Transitions | CR-004, CR-006         |
| AOCL-CR-008 | Verification and Evidence Model         | CR-003, CR-006         |
| AOCL-CR-009 | Simulation Scenario Model               | CR-006, CR-007, CR-008 |

## 12. Migration and Compatibility

This change must not silently invalidate existing AOCL models.

Existing loop registrations, maturity assessments, realization calculations, YAML structures, ledger records and CLAM export contracts must be inventoried before implementation.

Where existing concepts map to the new foundation, mappings should be documented.

Where existing representations are insufficient, extensions or explicit migration rules must be introduced through subsequent approved changes.

Existing functionality should remain operational during the transition unless a separately approved change establishes its replacement.

## 13. Implementation Guidance

Implementation should proceed in the following order:

1. Approve the conceptual foundation.
2. Establish canonical terminology and identifiers.
3. Define the canonical metamodel.
4. Define machine-readable schemas.
5. Implement semantic validation.
6. Establish behavioral execution semantics.
7. Implement logical simulation.
8. Extend to state-based simulation.
9. Introduce the visual engineering canvas.
10. Integrate operational and enterprise architecture references.

No simulation-specific implementation should precede agreement on the behavioral and control semantics it is intended to execute.

## 14. Change Completion Conditions

AOCL-CR-001 is complete when all acceptance criteria are satisfied, the architecture documentation is incorporated into the repository, and the normative baseline is approved.

Approval of this change establishes the conceptual authority for subsequent AOCL metamodel, engine and Studio changes.

---

**End of AOCL-CR-001**

**Disposition:** Proposed for architectural review and approval.

## 3. Important architectural implications for the next CRs

There are three matters I would ensure we do not lose when translating this foundation into implementation.

A. Stage and component cardinality

A closed loop must be able to contain multiple sensors, multiple controllers, several actuators and multiple verification mechanisms. The seven stages are not seven fixed nodes.

B. Verification must influence control

A failed verification must be capable of triggering another control cycle, escalation or safe-state transition. Otherwise, the model is not sufficiently closed.

C. Simulation must have a defined temporal model

The next metamodel should distinguish synchronous execution, asynchronous events, event ordering, processing delays and observation intervals. These are essential to meaningful state-based simulation.

## 4. Proposed next step

I recommend making AOCL-CR-002 the next deliverable: the Canonical Closed-Loop Metamodel.

It should define the actual entity types, attributes, identifiers, cardinalities, relationships, constraints and machine-readable representation. That is where we move from conceptual agreement to an implementable engineering specification.

Before proceeding, the CR-001 review should specifically challenge the seven-stage semantics, the distinction between structural and behavioral models, and the AOCL/CLAM boundary.

You can use this reminder to return to that review:

📐Review AOCL-CR-001 tomorrowTap to set up