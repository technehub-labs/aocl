# AOCL-CR-002 — Canonical Closed-Loop Metamodel

> **Status:** Proposed · **Queued:** 2026-11-07 (second deliverable of the AOCL foundation tranche, after CR-001). Drafted from the architectural review; normalized for the repository (diagram restored to Mermaid source, slide-draft artifacts removed) and carrying the [ADR-006](../decisions/adr-006-simulation-evidence-and-architecture-alignment.md) dispositions (§4a).

---

# AOCL-CR-002 — Canonical Closed-Loop Metamodel



Proposed change record

Foundation tranche

Objective: Translate the conceptual foundation established by AOCL-CR-001 into a canonical, technology-independent metamodel that can serve as the authoritative basis for modeling, validation, simulation and engineering.

The most important design decision for this CR is to establish the ClosedLoop as a first-class model aggregate, while keeping its behavioral specification, control architecture and execution implementation independently identifiable.

This avoids two undesirable extremes:

- A flat loop record containing loosely structured attributes.
- An excessively coupled metamodel in which every stage, sensor, controller, action and simulation detail is embedded in one large object.

The resulting metamodel must be sufficiently expressive for real engineering, but modular enough to evolve through CR-003 onward.

## 1. Scope and modeling boundaries

The CR sequence should preserve the separation established in the original improvement programme: CR-002 defines the canonical metamodel; CR-003 elaborates behavioral lifecycle semantics; CR-004 defines control architecture and component semantics; CR-005 establishes relationships, constraints and composition.&#x20;

Accordingly, CR-002 establishes the foundational object model without prematurely absorbing the detailed responsibilities of its successors.

CR-002 metamodel boundary

Core Closed-Loop Model

Identity · Context · Scope · Intent · Goals · Constraints · Governance · References

CR-003

Behavioral specification and seven-stage lifecycle

CR-004

Plant, sensors, controllers, actuators and knowledge

CR-005

Typed relationships, dependencies, composition and constraints

CR-006 onward translates these constructs into machine-readable specifications and executable engineering.

## 2. Proposed metamodel structure

The following is the proposed canonical structure.

### 2.1 Core metamodel entities

| Entity                         | Responsibility                             | Classification |
| ------------------------------ | ------------------------------------------ | -------------- |
| ClosedLoop                     | Primary aggregate and engineering identity | Core           |
| OperationalContext             | Environment and circumstances of operation | Core           |
| OperationalScope               | Defines the boundary of the loop           | Core           |
| IntentSpecification            | Declares what the loop must achieve        | Core           |
| Goal                           | Defines intended outcomes                  | Core           |
| ReferenceCondition             | Defines target or desired conditions       | Core           |
| ControlConstraint              | Defines limits and operating restrictions  | Core           |
| ControlledSystemBinding        | References the system being controlled     | Core           |
| EnterpriseReference            | Links governed enterprise entities         | Core           |
| ArchitectureBinding            | References control architecture            | Extension      |
| BehavioralSpecificationBinding | References behavioral specification        | Extension      |
| AssessmentReference            | Links independent maturity assessments     | Extension      |
| SimulationReference            | Links simulation artifacts                 | Extension      |

The distinction between an entity and a binding is important.

For example, AOCL should not create a second definition of an enterprise system merely because that system participates in a closed loop. It should create a `ControlledSystemBinding` that references the authoritative system definition.

## 3. Proposed conceptual class model

The following diagram establishes the core aggregate and its foundational associations. It deliberately leaves the internal structures of the behavioral and control architecture models to their respective successor CRs.


Important: These cardinalities are proposed normative requirements for review. The precise semantics of each relationship, including composition and dependency behavior, will be formalized in CR-005.

## 4. Canonical entity specifications

### 4.1 ClosedLoop

The aggregate root.

A ClosedLoop must have one stable identity throughout its existence, even when its name, implementation, control architecture or behavioral specification changes.

Required attributes:

| Attribute            | Type                | Requirement                        |
| -------------------- | ------------------- | ---------------------------------- |
| id                   | Identifier          | Mandatory, immutable               |
| name                 | String              | Mandatory                          |
| definition           | String              | Mandatory                          |
| description          | String              | Recommended                        |
| modelVersion         | Version             | Mandatory                          |
| schemaVersion        | Version             | Mandatory                          |
| lifecycleStatus      | Enumeration         | Mandatory                          |
| context              | OperationalContext  | Mandatory                          |
| scope                | OperationalScope    | Mandatory                          |
| intent               | IntentSpecification | Mandatory                          |
| controlledSystems    | Collection          | At least one                       |
| architectureBindings | Collection          | Optional during initial definition |
| behavioralBindings   | Collection          | Optional during initial definition |
| provenance           | Provenance          | Mandatory                          |

A model may be incomplete while in Draft status. It must not be represented as conformant or ready for simulation merely because its root entity exists.

### 4.2 OperationalContext

Defines the context within which the closed loop operates.

It should identify:

- Operational domain.
- Business or service context.
- Operating environment.
- Relevant stakeholders.
- Environmental dependencies.
- Contextual assumptions.

It should not become a free-form container for all other model aspects.

### 4.3 OperationalScope

Defines the boundary of responsibility and control.

It should explicitly identify:

- Included systems and operational elements.
- Excluded systems and responsibilities.
- Boundary conditions.
- Interfaces with external systems.
- Scope assumptions.

This prevents an AOCL model from claiming control over systems it can only observe or influence indirectly.

### 4.4 IntentSpecification

Defines the intended operational purpose of the loop.

It contains:

- One or more goals.
- Reference conditions.
- Control constraints.
- Goal priorities.
- Success criteria.

Intent must remain independent of implementation.

For example, maintaining latency below an agreed threshold is an intent. Rerouting traffic is a possible intervention, not the intent itself.

### 4.5 Goal

A Goal represents an intended outcome.

It should support:

- Unique identity.
- Definition.
- Outcome classification.
- Priority.
- Success criteria.
- Related reference conditions.

A Goal should not be reduced to a KPI. A KPI is a measurement mechanism that may provide evidence of goal achievement.

### 4.6 ReferenceCondition

A ReferenceCondition represents a measurable or evaluable desired condition.

It should support:

- Variable or property.
- Comparison operator.
- Target value or range.
- Measurement unit.
- Applicable operating context.
- Tolerance.
- Evaluation method reference.

Examples include:

- Latency below 50 ms.
- Service availability above 99.95%.
- Queue depth below 100 requests.

The metamodel must permit qualitative reference conditions where quantitative measurements are unsuitable.

### 4.7 ControlConstraint

A ControlConstraint defines a restriction on the operation of the loop.

Constraint categories should include:

- Safety.
- Operational.
- Regulatory.
- Financial.
- Resource.
- Temporal.
- Authorization.
- Technical.

A constraint is not simply another goal. A goal defines what should be achieved; a constraint defines what must or must not happen while pursuing it.

### 4.8 ControlledSystemBinding

References the actual controlled system or operational environment.

It must distinguish:

- The system being controlled.
- Systems being monitored.
- Systems providing supporting services.
- Systems receiving indirect effects.

The detailed Plant, Sensor, Controller and Actuator semantics belong to CR-004.

### 4.9 EnterpriseReference

Allows AOCL to link to governed enterprise entities.

Supported reference categories should accommodate:

- Capability.
- Process.
- Activity.
- System.
- Function.
- Service.
- Resource.
- Information entity.
- Data entity.
- Goal.
- Outcome.
- Metric.

These references must preserve the authoritative identity and source of the referenced entity.

## 5. Common identity and metadata model

All canonical AOCL entities should inherit a common identity and metadata contract.

| Field           | Description                                 |
| --------------- | ------------------------------------------- |
| id              | Stable globally unique identifier           |
| type            | Canonical metamodel type                    |
| name            | Human-readable name where applicable        |
| definition      | Formal semantic definition where applicable |
| description     | Additional explanatory information          |
| version         | Entity or model version                     |
| provenance      | Origin and source information               |
| lifecycleStatus | Governed lifecycle status                   |
| createdAt       | Creation timestamp                          |
| updatedAt       | Last modification timestamp                 |

Two distinct version concepts must be maintained:

1. Model version: The version of the particular closed-loop definition.
2. Schema version: The version of the metamodel contract used to interpret that definition.

A model must not silently change meaning because its schema evolves.

Stable identifiers should be opaque rather than derived from mutable names or descriptions. Identifier generation and namespace rules should be standardized across the repository.

## 6. Relationship and reference model

The metamodel must distinguish between containment and reference.

| Relationship  | Meaning                                                     |
| ------------- | ----------------------------------------------------------- |
| Contains      | Structural ownership within a model                         |
| References    | Points to an independently governed entity                  |
| Defines       | Establishes a semantic specification                        |
| ConstrainedBy | Subject to a defined restriction                            |
| Controls      | Indicates a control responsibility                          |
| Monitors      | Indicates observation responsibility                        |
| Realizes      | Indicates contribution to an intended capability or outcome |
| DependsOn     | Expresses a dependency                                      |

CR-002 establishes the relationship vocabulary and reference requirements. CR-004 and CR-005 will define the precise semantics and applicable cardinalities for control and composition relationships.

Unqualified generic relationships such as `relatedTo` must not be used as substitutes for typed semantic relationships.

## 7. Model lifecycle and conformance

The model lifecycle must be distinguished from operational execution status.

Proposed model lifecycle:

| Status     | Meaning                               |
| ---------- | ------------------------------------- |
| Draft      | Being defined                         |
| InReview   | Submitted for review                  |
| Approved   | Accepted as an engineering definition |
| Deprecated | Superseded by a newer definition      |
| Retired    | No longer maintained for use          |

Approval does not mean the loop is deployed or operational.

Likewise, operational states such as Running, Suspended and Failed belong to execution or runtime representations, not the canonical model lifecycle.

Conformance should be calculated independently using validation results.

Suggested conformance classifications:

- Structurally valid.
- Semantically valid.
- Behaviorally complete.
- Simulation-ready.
- Operationally approved.

Their detailed rules will be specified by subsequent CRs.

## 8. Illustrative canonical model instance

The following YAML demonstrates how a network service assurance loop could be represented using the proposed metamodel.

It is illustrative, not the final normative schema.

```

schemaVersion: "0.1"
modelVersion: "1.0.0"

closedLoop:
  id: "urn:aocl:loop:service-assurance-001"
  type: "ClosedLoop"
  name: "Network Service Assurance"
  definition: >
    Maintains network service performance within
    declared operational thresholds through
    observation, decision and controlled intervention.

  lifecycleStatus: "Draft"

  context:
    contextId: "service-assurance-context"
    domain: "Network Operations"
    operatingEnvironment: "Telecommunications"

  scope:
    scopeId: "network-service-scope"
    boundaryDefinition: >
      Network service latency and traffic management
      within the defined service boundary.
    inclusions:
      - "Service latency"
      - "Traffic routing"
    exclusions:
      - "Physical infrastructure replacement"

  intent:
    intentId: "service-assurance-intent"
    statement: >
      Maintain service latency within the
      agreed operational threshold.

    goals:
      - goalId: "latency-goal"
        name: "Maintain Service Latency"
        definition: >
          Maintain measured service latency
          below the operational threshold.
        priority: 1

        referenceConditions:
          - conditionId: "latency-reference"
            variable: "service.latency"
            operator: "lessThan"
            targetValue: 50
            unit: "ms"

    constraints:
      - constraintId: "routing-safety"
        name: "Routing Safety Constraint"
        constraintType: "Operational"
        expression: >
          Do not execute a routing change
          that violates the declared
          network safety policy.

  controlledSystems:
    - bindingId: "network-service-binding"
      targetReference:
        targetId: "network-service-001"
        targetType: "System"
        sourceSystem: "Enterprise Architecture"
      systemRole: "ControlledSystem"

  enterpriseReferences:
    - referenceId: "network-operations-capability"
      targetId: "network-operations-capability"
      targetType: "Capability"
      relationshipRole: "Realizes"

  architectureBindings: []
  behavioralBindings: []

  provenance:
    source: "AOCL Engineering Model"
    authority: "Model Owner"

```

This example deliberately does not embed MAPE-K stages, sensor contracts, actuator interfaces or simulation parameters. Those will be defined by the relevant successor models.

## 9. Metamodel validation requirements

The metamodel must support automated validation.

| ID     | Validation rule                                                                  |
| ------ | -------------------------------------------------------------------------------- |
| MM-001 | Every canonical entity has a stable identifier.                                  |
| MM-002 | Every ClosedLoop has a unique identity.                                          |
| MM-003 | Every ClosedLoop has an operational context.                                     |
| MM-004 | Every ClosedLoop has an explicitly defined scope.                                |
| MM-005 | Every ClosedLoop has an intent specification.                                    |
| MM-006 | Every intent has at least one goal.                                              |
| MM-007 | Every goal has a definition and identifiable success criteria.                   |
| MM-008 | Reference conditions specify valid operators, values and units where applicable. |
| MM-009 | Constraints have identifiable categories and definitions.                        |
| MM-010 | Every ClosedLoop references at least one controlled system.                      |
| MM-011 | Internal references resolve to valid model entities.                             |
| MM-012 | External references preserve source identity and provenance.                     |
| MM-013 | Entity references use valid canonical types.                                     |
| MM-014 | Model version and schema version are independently represented.                  |
| MM-015 | Deprecated or retired definitions cannot silently become active.                 |
| MM-016 | Model lifecycle status is not confused with runtime execution status.            |
| MM-017 | Unsupported arbitrary attributes cannot override canonical semantics.            |
| MM-018 | Models identify the provenance of their authoritative definitions.               |

## 10. Engineering implementation requirements

The metamodel must be implemented as a technology-independent conceptual contract first.

Subsequent schema implementation must support:

- Canonical JSON representation.
- YAML serialization.
- JSON Schema validation.
- Referential integrity validation.
- Semantic validation.
- Stable identifiers.
- Model versioning.
- Schema migration.
- Controlled extensions.
- Round-trip import and export.

The visual Studio must consume the same canonical model.

It must not maintain a separate, incompatible object model for its canvas nodes and connections.

## 11. Migration and compatibility

Existing AOCL loop records must be mapped into the canonical model without losing:

- Existing loop identifiers.
- Loop names and descriptions.
- Associated capabilities, processes, systems and functions.
- Existing goals.
- Decision-model selections.
- Maturity dimensions and scores.
- Realization information.
- CLAM integration references.

Where existing records lack required attributes, the migration must identify missing information rather than fabricate it.

Existing models may be migrated into Draft status pending completion of the new requirements.

Existing maturity and realization results must remain independently traceable to the model version against which they were produced.

## 12. Scope boundaries

### Included

- Canonical ClosedLoop aggregate.
- Identity and metadata.
- Operational context and scope.
- Intent specification.
- Goals.
- Reference conditions.
- Control constraints.
- Controlled-system bindings.
- Enterprise references.
- Foundational relationship vocabulary.
- Model lifecycle and validation requirements.
- Serialization and schema implementation guidance.
- Migration requirements.

### Excluded

- Seven-stage behavioral metamodel details: CR-003.
- Detailed plant, sensor, controller and actuator semantics: CR-004.
- Advanced relationship and composition semantics: CR-005.
- Full JSON Schema contract: CR-006.
- Detailed control contracts and state transitions: CR-007.
- Verification and evidence semantics: CR-008.
- Simulation scenarios and disturbances: CR-009.

## 13. Acceptance criteria

AOCL-CR-002 will be considered complete when:

1. The canonical ClosedLoop aggregate is formally defined.
2. All foundational entity types have stable identifiers and semantic definitions.
3. Identity and metadata contracts are standardized.
4. Operational context and scope are independently represented.
5. Intent, goals, reference conditions and constraints are distinguishable.
6. Controlled-system references are supported.
7. Enterprise references preserve authoritative source identity.
8. Containment and reference relationships are distinguishable.
9. Model lifecycle and runtime status are separate.
10. Model version and schema version are separate.
11. Canonical cardinalities and validation requirements are documented.
12. An illustrative model instance passes the implemented structural and semantic validation rules.
13. Existing AOCL models have a documented migration path.
14. The model is extensible without allowing arbitrary attributes to undermine its semantics.
15. The metamodel is suitable for behavioral and control architecture extensions.

## 14. Successor dependencies

| Change      | Deliverable                             | Dependency             |
| ----------- | --------------------------------------- | ---------------------- |
| AOCL-CR-003 | Behavioral Lifecycle Metamodel          | CR-001, CR-002         |
| AOCL-CR-004 | Control Architecture Metamodel          | CR-001, CR-002         |
| AOCL-CR-005 | Relationships and Loop Composition      | CR-002, CR-003, CR-004 |
| AOCL-CR-006 | Behavioral Specification Schema         | CR-003                 |
| AOCL-CR-007 | Control Contracts and State Transitions | CR-004, CR-006         |
| AOCL-CR-008 | Verification and Evidence Model         | CR-003, CR-006         |
| AOCL-CR-009 | Scenario and Disturbance Model          | CR-006, CR-007, CR-008 |

## 15. Completion and approval conditions

AOCL-CR-002 is complete when its conceptual and machine-readable deliverables satisfy the acceptance criteria and the implementation is incorporated into the approved AOCL baseline.

Approval establishes the canonical metamodel authority for subsequent AOCL modeling, simulation and Studio development.

End of AOCL-CR-002

Disposition: Proposed for architectural and metamodel review.

## 4a. Dispositions carried from ADR-006 (simulation evidence)

The simulation campaign ([ADR-006](../decisions/adr-006-simulation-evidence-and-architecture-alignment.md)) imposes one must-resolve and two carry-forward obligations on this metamodel:

1. **MUST-RESOLVE (finding F1): the aggregation-binding rule.** The simulation showed that weakest-link aggregation is *inconsistent* as currently expressed: a loop with vectors (GD5, DV1, FI5) behaves like pure L1 (capabilities never activate), while (GD5, DV2, FI5) — also min-L2 — behaves *better* than pure L2 because FI4+ gain adaptation is vector-gated rather than level-gated. CR-002's metamodel must therefore make the binding explicit: either (a) `level` strictly gates all capabilities (vectors become assessment detail), or (b) the `(GD, DV, FI)` profile is the behavioral first-class and `level` is a derived reporting label. The metamodel representation chosen here must record the decision — the recommendation is (b): model vectors as first-class behavioral attributes of the ClosedLoop aggregate and treat the overall level as derived.
2. **Velocity-fit precondition (finding F4):** the metamodel's ControlledSystemBinding and AssessmentReference must be able to carry the observation/cycle interval and actuation authority so a velocity-fit precondition can be evaluated before L4+ maturity is claimed (detailed semantics: CR-004).
3. **Sandbox containment (finding F3):** the learning/knowledge aspects must support an experimentation-containment declaration (full semantics: CR-004; conformance: CR-008).

## 5. Architectural review: decisions to challenge before approval

There are five issues I would pay particular attention to. These are not reasons to delay the draft; they are design questions that should be resolved before the metamodel becomes normative.

| Issue                          | My recommendation                                                    |
| ------------------------------ | -------------------------------------------------------------------- |
| Multiple controlled systems    | Support multiple plant bindings per loop.                            |
| Multiple goals                 | Support multiple goals with explicit priority and conflict handling. |
| Intent versus KPI              | Keep goals, reference conditions and metrics distinct.               |
| External references            | Use source-qualified references, not copied entity definitions.      |
| Model lifecycle versus runtime | Keep them entirely separate.                                         |

One additional issue deserves attention: should an AOCL ClosedLoop always have exactly one IntentSpecification, or should it support multiple independently governed intents?

My recommendation is one primary IntentSpecification per ClosedLoop, containing multiple goals and constraints. This gives the loop one coherent control purpose while supporting multiple operational objectives.

## 6. Recommended next sequence

## AOCL foundation progression

1. Prepared

   CR-001 — Conceptual Foundation

   Establishes the engineering identity and normative principles.
2. Current draft

   CR-002 — Canonical Metamodel

   Establishes the core object model and foundational entity contracts.
3. CR-003 — Behavioral Lifecycle Metamodel

   Formalizes the seven stages, activities, decisions, transitions, branches and exceptions.
4. CR-004 — Control Architecture Metamodel

   Formalizes the plant, sensors, observations, controllers, actuators and knowledge structures.
5. CR-005 — Relationships and Composition

   Establishes loop coordination, dependencies, hierarchical composition and semantic constraints.

My recommendation: Review and approve CR-002 before drafting CR-003. The most important thing to settle is the canonical identity and aggregation boundary of a ClosedLoop. Once that is stable, the behavioral and control architecture models can evolve independently without destabilizing the root metamodel.

The next deliverable should be AOCL-CR-003, with particular emphasis on making the seven stages executable as a flexible behavioral graph rather than a fixed seven-step workflow.