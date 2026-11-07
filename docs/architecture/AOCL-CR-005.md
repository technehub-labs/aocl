> **Status:** Proposed · **Queued:** 2026-11-07 — pivotal: makes CR-002/003/004 coherent as one model — relationship taxonomy, constraint attachment/propagation, composition patterns, shared control scopes, authority integrity (P13–P18) · Carries forward the review's pre-approval observations (kept in-document as review checks).

---

# AOCL-CR-005 — Establish the Canonical Relationship, Constraint and Loop Composition Model

**Change Request ID:** AOCL-CR-005\
**Title:** Establish the Canonical Relationship, Constraint and Loop Composition Model\
**Status:** Proposed\
**Priority:** Critical\
**Change Type:** Metamodel / Architecture / Governance\
**Depends On:**

- AOCL-CR-001 — Establish Canonical Conceptual Foundation and Normative Engineering Principles
- AOCL-CR-002 — Establish the Canonical Closed-Loop Metamodel
- AOCL-CR-003 — Establish the Canonical Seven-Stage Behavioral Lifecycle Metamodel
- AOCL-CR-004 — Establish the Canonical Control Architecture Metamodel

**Affected Areas:** Domain Model, Relationship Model, Control Architecture, Behavioral Model, Model Validation, Composition, Simulation Readiness, Model Serialization.

---

## 1. Purpose

Establish a canonical relationship, constraint and composition model that defines how AOCL engineering entities relate to one another, how those relationships are governed, and how individual closed loops can be composed into larger control systems.

CR-002, CR-003 and CR-004 establish the principal entities and architectural concepts. However, entity definitions alone do not establish a coherent metamodel. AOCL must also define the semantics of connections between those entities.

This CR introduces a common relationship model across:

1. Closed-loop domain entities.
2. Behavioral lifecycle elements.
3. Control architecture components.
4. Intent, goals and constraints.
5. Enterprise references.
6. Multiple interacting closed loops.
7. Model composition and containment.

The resulting model must support both structural representation and behavioral interpretation without conflating them.

The objective is to ensure that a connection in AOCL has a defined meaning, valid endpoints, applicable constraints, traceable provenance and an explicit role in the engineering model.

## 2. Problem Statement

Without a canonical relationship and composition model, AOCL risks developing inconsistent interpretations of the same model.

Examples include:

- A relationship between a Sensor and a Plant being interpreted differently by the modeling interface and simulation engine.
- A Controller being connected to an Actuator without a defined authority or delivery path.
- A behavioral stage being connected to a component in a way that incorrectly implies a one-to-one relationship.
- Multiple loops controlling the same Plant without a defined coordination or conflict-resolution mechanism.
- A loop referencing another loop without distinguishing dependency, delegation, coordination and composition.
- A relationship being visually represented but lacking machine-verifiable semantics.
- A model being structurally connected while remaining behaviorally incomplete.
- Constraints being attached to entities without defining their applicability or enforcement implications.

These are not merely diagramming problems. They affect model validity, simulation fidelity, safety, interoperability and the ability to prepare a closed loop for operational realization.

AOCL therefore requires a normative relationship and composition foundation before defining executable behavior and simulation semantics.

## 3. Objectives

This CR shall:

1. Establish a canonical relationship vocabulary.
2. Define relationship endpoint and direction semantics.
3. Distinguish containment, reference, dependency, interaction and realization.
4. Define relationship ownership and lifecycle.
5. Establish constraint attachment and propagation principles.
6. Define closed-loop composition and boundary semantics.
7. Support multiple Plants, Sensors, Controllers, Actuators and Knowledge resources.
8. Support distributed, hierarchical, cooperative and human-supervised control architectures.
9. Support relationships across the seven behavioral stages.
10. Define the structural conditions for valid loop composition.
11. Establish cross-loop coordination and conflict-detection requirements.
12. Provide a common foundation for validation, serialization and future simulation.

## 4. Normative Design Principles

| ID       | Principle               | Normative implication                                                                       |
| -------- | ----------------------- | ------------------------------------------------------------------------------------------- |
| AOCL-P13 | Relationship Semantics  | Every canonical relationship must have an explicit meaning.                                 |
| AOCL-P14 | Explicit Boundaries     | Ownership, containment and control scope must be distinguishable.                           |
| AOCL-P15 | Constraint Integrity    | Constraints must remain traceable to their source and applicable scope.                     |
| AOCL-P16 | Composition Integrity   | Composed loops must preserve their individual identity and governance.                      |
| AOCL-P17 | Authority Integrity     | Relationships must never imply control authority that has not been explicitly granted.      |
| AOCL-P18 | Behavioral Traceability | Structural relationships must be traceable to the behavioral responsibilities they support. |

These principles supplement the normative principles established by CR-001.

## 5. Scope

### 5.1 In scope

- Canonical relationship taxonomy.
- Relationship definitions and endpoint semantics.
- Relationship metadata and identity.
- Ownership and containment rules.
- Constraint attachment and applicability.
- Loop composition and decomposition.
- Cross-loop relationships.
- Shared and overlapping controlled-system boundaries.
- Relationship validation and conformance requirements.
- Migration and compatibility requirements.

### 5.2 Out of scope

The following remain separate change requests:

| CR     | Responsibility                                                      |
| ------ | ------------------------------------------------------------------- |
| CR-006 | Detailed behavioral specification schema                            |
| CR-007 | Control contracts, control variables and state-transition semantics |
| CR-008 | Verification and evidence model                                     |
| CR-009 | Simulation scenarios and disturbance model                          |
| CR-010 | Canonical execution semantics                                       |
| CR-011 | Logical simulation engine                                           |
| CR-012 | State-based simulation engine                                       |

CR-005 defines the relationships and composition structures those later models will use. It does not prescribe their complete execution semantics.

## 6. Canonical Relationship Model

### 6.1 Relationship as a first-class modeling construct

A relationship shall be a first-class metamodel construct rather than an untyped connection between two visual nodes.

Every canonical relationship must have:

- Stable relationship identifier.
- Relationship type.
- Source entity reference.
- Target entity reference.
- Direction.
- Definition or semantic description.
- Lifecycle status.
- Provenance.
- Version information where applicable.

Optional relationship attributes may include:

- Role.
- Cardinality.
- Validity period.
- Applicable context.
- Conditions.
- Priority.
- Ownership.
- Evidence reference.
- Extension attributes.

The model must distinguish the identity of a relationship from the identity of its source and target entities.

### 6.2 Relationship categories

AOCL shall organize canonical relationships into six semantic categories.

| Category           | Purpose                                                    | Examples                                |
| ------------------ | ---------------------------------------------------------- | --------------------------------------- |
| Structural         | Expresses model organization and ownership                 | Contains, ComposedOf                    |
| Referential        | Connects an AOCL entity to another governed entity         | References, BindsTo                     |
| Functional         | Expresses a responsibility or operational role             | Controls, Monitors, Realizes            |
| Informational      | Expresses information production and consumption           | Produces, Informs, Uses                 |
| Causal / Influence | Expresses an effect or influence                           | Influences, Affects                     |
| Coordinative       | Expresses interaction between loops or control authorities | CoordinatesWith, DependsOn, DelegatesTo |

The categories organize semantics; they do not imply that every relationship is interchangeable or belongs to only one implementation layer.

### 6.3 Canonical relationship vocabulary

The following relationships establish the initial normative vocabulary.

#### A. Structural relationships

| Relationship | Source                 | Target             | Meaning                                                  |
| ------------ | ---------------------- | ------------------ | -------------------------------------------------------- |
| Contains     | Aggregate or container | Owned entity       | The source owns the target within its model boundary.    |
| ComposedOf   | Composite entity       | Constituent entity | The target contributes to the composition of the source. |
| PartOf       | Entity                 | Composite entity   | Inverse expression of composition where appropriate.     |

**Rules:**

- Containment establishes ownership and lifecycle implications.
- Composition establishes a meaningful constituent relationship.
- A reference does not imply ownership.
- The model must avoid defining both directions as independently authoritative relationships where one can be derived.
- A contained entity must not be silently treated as an externally governed entity.

#### B. Referential relationships

| Relationship | Source                  | Target                         | Meaning                                                          |
| ------------ | ----------------------- | ------------------------------ | ---------------------------------------------------------------- |
| References   | AOCL entity             | External or internal entity    | Identifies a governed entity without copying its definition.     |
| BindsTo      | AOCL binding            | Referenced entity              | Establishes an explicit association with a governed target.      |
| Implements   | Implementation artifact | Specification or model element | Identifies the implementation of a defined model responsibility. |

A reference must preserve source-system identity and target identity.

A reference must not be interpreted as ownership, execution authority or operational dependency unless additional semantics explicitly establish those properties.

#### C. Control architecture relationships

| Relationship | Source                         | Target                            | Meaning                                                                          |
| ------------ | ------------------------------ | --------------------------------- | -------------------------------------------------------------------------------- |
| ObservedBy   | Plant                          | Sensor or observation mechanism   | Identifies an observation path for the Plant.                                    |
| Monitors     | Sensor or monitoring mechanism | Plant or monitored entity         | Identifies the subject being monitored.                                          |
| Controls     | Controller                     | Plant or control scope            | Identifies the controlled subject and declared control responsibility.           |
| Actuates     | Actuator                       | Plant or controlled interface     | Identifies the target of an intervention mechanism.                              |
| Influences   | Entity                         | Entity                            | Expresses an influence relationship without necessarily implying direct control. |
| AffectedBy   | Entity                         | Disturbance or influencing entity | Identifies an influence on the entity.                                           |

These relationships must not be used to infer authority beyond the explicitly defined controller and actuator responsibilities.

A Plant may have multiple Sensors, Controllers and Actuators. A Controller may control multiple Plants or defined control scopes.

The metamodel must also permit shared monitoring and distributed control.

#### D. Information relationships

| Relationship       | Source                           | Target                              | Meaning                                                         |
| ------------------ | -------------------------------- | ----------------------------------- | --------------------------------------------------------------- |
| Produces           | Information-producing entity     | Information artifact                | Identifies the origin of information.                           |
| Informs            | Information artifact             | Consumer or decision responsibility | Identifies information used by a consumer.                      |
| Uses               | Controller or behavioral element | Knowledge resource                  | Identifies a governed resource used in decisioning or analysis. |
| ProvidesFeedbackTo | Feedback-producing entity        | Controller or coordinating element  | Identifies a feedback information path.                         |

A Sensor may directly produce an Observation, or may produce raw measurements that are subsequently transformed into an Observation.

The model must preserve this distinction.

An Observation must retain provenance indicating whether it is directly measured, derived, inferred, aggregated or externally reported.

An Actuator status message must not automatically be treated as independent evidence that the intended Plant outcome was achieved.

#### E. Behavioral relationships

| Relationship | Source                       | Target                    | Meaning                                                 |
| ------------ | ---------------------------- | ------------------------- | ------------------------------------------------------- |
| Supports     | Structural or control entity | Behavioral stage          | Identifies support for a behavioral responsibility.     |
| Realizes     | Entity or model element      | Behavioral responsibility | Identifies the realization of a defined responsibility. |
| Precedes     | Behavioral element           | Behavioral element        | Establishes an ordering constraint where applicable.    |
| Enables      | Behavioral element           | Behavioral element        | Establishes a necessary enabling relationship.          |
| DependsOn    | Behavioral element           | Behavioral element        | Identifies a dependency.                                |
| Triggers     | Event or condition           | Behavioral element        | Identifies a behavioral activation condition.           |

These relationships must preserve the distinction between behavioral ordering and structural architecture.

In particular:

- A Controller may support Analyze, Decide and other responsibilities.
- A Sensor may support Observe and Verify.
- An Actuator may support Execute.
- Knowledge may support Analyze, Decide and Learn.
- A behavioral stage may be supported by multiple components.
- A component may support multiple behavioral stages.

The model must not impose a one-to-one mapping between components and behavioral stages.

#### F. Coordination relationships

| Relationship       | Source                          | Target                          | Meaning                                                       |
| ------------------ | ------------------------------- | ------------------------------- | ------------------------------------------------------------- |
| CoordinatesWith    | ClosedLoop                      | ClosedLoop                      | Establishes an explicit coordination relationship.            |
| DependsOn          | ClosedLoop                      | ClosedLoop                      | Identifies a dependency between loops.                        |
| DelegatesTo        | ClosedLoop or controller        | ClosedLoop or controller        | Transfers an explicitly bounded responsibility.               |
| Supervises         | Supervisory controller or loop  | Controlled loop or controller   | Establishes supervisory responsibility.                       |
| SharesResourceWith | ClosedLoop                      | ClosedLoop                      | Identifies a shared resource or control dependency.           |
| ConflictsWith      | ClosedLoop or control authority | ClosedLoop or control authority | Identifies an incompatible or competing control relationship. |

These relationships must not be treated as interchangeable.

For example, a loop that depends on another loop is not necessarily coordinated by it. A supervisory relationship does not automatically transfer operational control authority.

## 7. Relationship Semantics and Integrity

### 7.1 Endpoint validity

Every relationship must identify valid source and target entities.

The metamodel shall define:

- Permitted source entity types.
- Permitted target entity types.
- Directionality.
- Required attributes.
- Cardinality constraints.
- Applicable lifecycle states.
- Whether the relationship is internal or external.

An invalid endpoint combination must fail semantic validation.

### 7.2 Relationship identity

Relationships must have stable identifiers independent of entity names.

Renaming an entity must not change the identity of an existing relationship.

Relationship identity must support:

- Versioning.
- Provenance.
- Change tracking.
- Model comparison.
- Migration.
- Traceability.

### 7.3 Relationship lifecycle

Relationships shall support lifecycle states appropriate to their use:

- Draft
- Active
- Deprecated
- Retired

The model must distinguish relationship lifecycle from the runtime state of the entities involved.

### 7.4 Derived relationships

Where one relationship is logically derivable from another, AOCL should avoid maintaining two independent sources of truth.

For example, if an entity is explicitly contained by a composite, its inverse PartOf relationship may be derived.

Derived relationships must be distinguishable from explicitly asserted relationships.

### 7.5 Relationship provenance

A relationship must be identifiable as one of:

- Explicitly modeled.
- Imported from an external source.
- Derived by a defined rule.
- Inferred by an analysis process.

Inferred relationships must never silently become authoritative relationships.

## 8. Constraint Model

### 8.1 Purpose

Constraints establish the boundaries within which a closed loop, controller, actuator or behavioral responsibility may operate.

CR-002 establishes ControlConstraint as a core entity. CR-005 defines how constraints apply across model boundaries and relationships.

### 8.2 Constraint attachment

A constraint may apply to:

- ClosedLoop.
- IntentSpecification.
- Goal.
- Plant.
- Controller.
- Actuator.
- BehavioralSpecification.
- Relationship.
- Control scope.
- Composed group of loops.

The metamodel must support both direct attachment and scoped applicability.

A constraint attached to a composite loop must not automatically be copied into every constituent loop. Its applicability and propagation must be explicit.

### 8.3 Constraint categories

The initial categories established by CR-002 remain:

1. Safety.
2. Operational.
3. Regulatory.
4. Financial.
5. Resource.
6. Temporal.
7. Authorization.
8. Technical.

The categories may be extended through governed extension mechanisms.

### 8.4 Constraint properties

A constraint should be capable of expressing:

- Stable identifier.
- Category.
- Definition.
- Scope.
- Subject.
- Condition or expression.
- Severity.
- Applicability.
- Enforcement responsibility.
- Source and provenance.
- Effective period.
- Evidence or verification requirement.

Detailed executable expression syntax is deferred to CR-006 and CR-007.

### 8.5 Constraint propagation

Constraints may be inherited, referenced or explicitly propagated through composition.

The model must distinguish:

- **Inherited constraint:** applies to a constituent because of a defined containment or governance rule.
- **Referenced constraint:** points to a constraint owned elsewhere.
- **Propagated constraint:** explicitly applied to a target scope.
- **Local constraint:** applies only to the entity on which it is defined.

Propagation must be deterministic and traceable.

Where constraints conflict, AOCL must identify the conflict rather than silently selecting one.

A precedence policy must be explicit and must not allow a lower-authority constraint to override a higher-authority safety or regulatory constraint.

## 9. Closed-Loop Composition Model

### 9.1 Composition principle

AOCL must support the composition of multiple closed loops into a larger operational control arrangement.

Composition allows an engineering model to represent:

- Multiple loops working towards a shared outcome.
- Hierarchical control.
- Supervisory control.
- Distributed control.
- Cooperative control.
- Interdependent loops.
- Shared controlled systems.
- Nested or coordinated control scopes.

Composition must not erase the identity, intent, maturity or governance of constituent loops.

### 9.2 Composite ClosedLoop

A composite ClosedLoop shall represent an aggregate control arrangement comprising two or more constituent loops.

The composite must have:

- Its own stable identity.
- Defined operational context.
- Defined scope.
- Explicit composition membership.
- Declared aggregate intent or contribution to a higher-level intent.
- Applicable constraints.
- Defined coordination relationships.
- Traceable references to constituent loops.

A composite loop must not automatically inherit the maturity or realization status of its constituents.

Its maturity and realization must be assessed according to its own defined criteria.

### 9.3 Composition patterns

AOCL shall support at least the following patterns.

**A. Hierarchical composition**

A supervisory loop coordinates subordinate loops.

Examples include policy-level supervision of multiple operational control loops.

**B. Cooperative composition**

Multiple loops coordinate to achieve a shared outcome.

No single constituent necessarily owns the entire outcome.

**C. Dependency composition**

One loop depends on the outcome, state or service of another loop.

Dependency does not imply shared control authority.

**D. Shared-Plant composition**

Multiple loops interact with the same Plant or overlapping control scopes.

This pattern requires explicit control-scope and conflict analysis.

**E. Federated composition**

Independently governed loops cooperate through explicit interfaces and agreements without being merged into a single ownership boundary.

### 9.4 Composition boundaries

A constituent loop retains its own:

- Identity.
- Intent.
- Goals.
- Constraints.
- Behavioral specification.
- Control architecture.
- Assessment references.
- Simulation references.
- Lifecycle status.

The composite may reference these properties, but must not silently redefine them.

Changes to a constituent loop must be traceable and must trigger re-evaluation of affected composite models where relevant.

### 9.5 Nested composition

AOCL must permit nested composition, subject to validation of:

- Circular dependencies.
- Recursive containment.
- Conflicting control scopes.
- Inconsistent constraints.
- Unresolvable references.
- Ambiguous ownership.
- Unbounded delegation.

The model must distinguish containment hierarchy from operational dependency graphs. A dependency cycle is not necessarily a containment cycle.

## 10. Shared Control Scope and Multiple Authorities

A particularly important composition concern is the possibility that more than one loop influences the same Plant.

AOCL must not assume that each Plant has exactly one Controller or that each Controller has exclusive control over a Plant.

However, shared control introduces potential conflicts.

The model must therefore support explicit declarations of:

- Control scope.
- Control variables or controlled properties.
- Authority level.
- Operating context.
- Priority.
- Coordination mechanism.
- Delegation boundaries.
- Conflict-resolution policy.
- Supervisory authority.

Detailed control-variable typing and state-transition semantics remain in CR-007.

### 10.1 Control authority rules

The following rules are normative:

1. A Controls relationship identifies a declared control responsibility; it does not independently grant authority.
2. Authority must be explicitly defined and governed.
3. An Actuates relationship identifies an intervention path, not proof of successful outcome.
4. A supervisory relationship must define the limits of supervision.
5. Delegation must identify the delegated responsibility and its boundaries.
6. Conflicting authority must be detected and surfaced.
7. Safety and authorization constraints must remain effective across composed loops.

### 10.2 Advisory and monitor-only arrangements

AOCL may represent advisory, monitoring-only and human-mediated arrangements.

These arrangements must be explicitly classified.

A monitoring-only model must not automatically qualify as a fully realized closed-loop control system.

An advisory controller may recommend interventions without possessing authority to execute them.

A human operator may serve as the decision-maker, controller, approver or actuator role where the modeled responsibilities support that interpretation.

## 11. Relationship to the Behavioral Lifecycle

CR-003 establishes the seven canonical behavioral responsibilities:

1. Intent.
2. Observe.
3. Analyze.
4. Decide.
5. Execute.
6. Verify.
7. Learn.

CR-005 establishes how structural entities and relationships support those responsibilities.

The following mapping is the reference model, not a mandatory execution sequence.

| Behavioral responsibility | Relevant structural relationships       |
| ------------------------- | --------------------------------------- |
| Intent                    | Defines, ConstrainedBy, References      |
| Observe                   | Monitors, ObservedBy, Produces, Informs |
| Analyze                   | Uses, Informs, DependsOn                |
| Decide                    | Uses, ConstrainedBy, Supports           |
| Execute                   | Controls, Actuates, DelegatesTo         |
| Verify                    | ObservedBy, Produces, Informs, Supports |
| Learn                     | Uses, Produces, References, Supports    |

The same structural component may support multiple responsibilities.

A component's participation in a stage must be explicitly modeled or derived through a governed mapping rule.

The relationship model must not force a sequential workflow or prohibit parallel and asynchronous behavior.

## 12. Model Validation Requirements

The following requirements are normative.

| ID      | Requirement                                                                                           |
| ------- | ----------------------------------------------------------------------------------------------------- |
| RCM-001 | Every canonical relationship must have a defined relationship type.                                   |
| RCM-002 | Every relationship must have valid source and target references.                                      |
| RCM-003 | Every relationship type must define permitted endpoint types.                                         |
| RCM-004 | Relationship direction must be explicit.                                                              |
| RCM-005 | Relationship identity must be stable and independent of entity names.                                 |
| RCM-006 | Relationship provenance must be recorded.                                                             |
| RCM-007 | Derived relationships must be distinguishable from asserted relationships.                            |
| RCM-008 | Containment and reference semantics must remain distinct.                                             |
| RCM-009 | Composition must preserve constituent identity.                                                       |
| RCM-010 | Constraint applicability must be explicit.                                                            |
| RCM-011 | Constraint propagation must be deterministic and traceable.                                           |
| RCM-012 | Conflicting constraints must be identified.                                                           |
| RCM-013 | Control relationships must not imply ungranted authority.                                             |
| RCM-014 | Multiple Sensors and Observations must be supported.                                                  |
| RCM-015 | Multiple Controllers and Actuators must be supported.                                                 |
| RCM-016 | Multiple loops may reference or coordinate with the same Plant.                                       |
| RCM-017 | Shared control scopes must be identifiable.                                                           |
| RCM-018 | Conflicting control responsibilities must be detectable.                                              |
| RCM-019 | Hierarchical composition must be supported.                                                           |
| RCM-020 | Cooperative composition must be supported.                                                            |
| RCM-021 | Dependency composition must be supported.                                                             |
| RCM-022 | Federated composition must be supported.                                                              |
| RCM-023 | Nested composition must be supported subject to cycle validation.                                     |
| RCM-024 | Containment cycles must be rejected.                                                                  |
| RCM-025 | Dependency cycles must be identified and classified, not automatically treated as containment errors. |
| RCM-026 | Behavioral and structural relationships must remain distinguishable.                                  |
| RCM-027 | Stage-to-component mappings must support many-to-many relationships.                                  |
| RCM-028 | Advisory and monitor-only arrangements must be explicitly classified.                                 |
| RCM-029 | External references must preserve source-system identity.                                             |
| RCM-030 | Relationship changes must be traceable through model versioning.                                      |
| RCM-031 | Model validation must distinguish structural validity from behavioral completeness.                   |
| RCM-032 | Model validation must distinguish conformance from simulation readiness.                              |

## 13. Conformance Model

CR-005 introduces three distinct conformance concerns.

### 13.1 Relationship Conformance

Determines whether relationships are correctly defined, typed, directed and connected to valid endpoints.

### 13.2 Composition Conformance

Determines whether constituent loops, control scopes, ownership boundaries and coordination relationships are valid.

### 13.3 Constraint Conformance

Determines whether constraints are properly attached, scoped, propagated and governed.

These conformance results must remain distinguishable.

A model may be structurally valid while containing unresolved constraint conflicts or insufficient information for simulation.

## 14. Implementation Requirements

The implementation should introduce a technology-independent canonical relationship model before selecting serialization details.

The implementation programme should include:

1. Canonical relationship type registry.
2. Relationship endpoint definitions.
3. Relationship metadata model.
4. Relationship validation rules.
5. Constraint attachment model.
6. Constraint propagation rules.
7. Composition membership model.
8. Control-scope declarations.
9. Cross-loop coordination model.
10. Cycle and conflict detection.
11. Model migration and compatibility tests.
12. Reference models demonstrating supported composition patterns.

JSON Schema may validate structural representation, but semantic validation will also be required for endpoint compatibility, constraint propagation, cycles and control conflicts.

YAML and JSON representations must serialize the same canonical semantics.

The visual modeling canvas must consume this same model. A visually connected graph must not be considered valid merely because its nodes and edges can be rendered.

## 15. Migration and Compatibility

The implementation must preserve existing AOCL model identities and references.

Migration must:

- Preserve existing loop identifiers.
- Preserve existing enterprise references.
- Preserve existing links and associations where their semantics can be established.
- Distinguish legacy associations from newly classified canonical relationships.
- Avoid inventing ownership or control authority.
- Avoid treating every legacy link as a canonical relationship.
- Record unresolved relationship semantics.
- Preserve assessment and realization references.
- Permit incomplete legacy models to remain in Draft status.
- Provide migration diagnostics for invalid or ambiguous relationships.

No existing assessment, realization or CLAM integration behavior should be silently removed or reinterpreted.

## 16. Acceptance Criteria

This CR is accepted when:

1. A canonical relationship taxonomy is documented.
2. Relationship semantics and endpoint rules are defined.
3. Relationship identity and provenance are specified.
4. Structural, referential, functional, informational, influence and coordination relationships are distinguishable.
5. Containment and reference semantics are unambiguous.
6. Constraint attachment and propagation rules are defined.
7. Constraint conflicts can be identified.
8. Composite ClosedLoop semantics are defined.
9. Constituent loop identity and governance are preserved.
10. Hierarchical composition is representable.
11. Cooperative composition is representable.
12. Dependency composition is representable.
13. Federated composition is representable.
14. Nested composition is representable subject to validation.
15. Shared Plant and control scopes are representable.
16. Multiple Controllers and Actuators are supported.
17. Conflicting control responsibilities can be detected.
18. Advisory and monitor-only arrangements can be classified.
19. Behavioral and structural relationships remain distinct.
20. Many-to-many component-to-stage mappings are supported.
21. Structural, composition and constraint conformance are distinguishable.
22. Migration rules preserve existing model identity and references.
23. Reference models demonstrate valid and invalid relationship structures.
24. Automated validation tests cover the normative requirements.

## 17. Risks and Mitigations

| Risk                                                     | Consequence                                       | Mitigation                                                         |
| -------------------------------------------------------- | ------------------------------------------------- | ------------------------------------------------------------------ |
| Relationship vocabulary becomes excessively broad        | Inconsistent semantics and model complexity       | Govern a canonical vocabulary and controlled extensions.           |
| Visual connections are treated as semantic relationships | Invalid or misleading models                      | Require typed relationships and semantic validation.               |
| Composition erases constituent identity                  | Loss of governance and traceability               | Preserve constituent loop identity and lifecycle.                  |
| Constraint propagation is ambiguous                      | Unsafe or inconsistent control behavior           | Require explicit propagation and conflict detection.               |
| Shared control is under-specified                        | Conflicting interventions                         | Model control scope, authority and coordination explicitly.        |
| Structural and behavioral models are conflated           | Rigid or inaccurate simulations                   | Preserve distinct metamodels and explicit mappings.                |
| Dependency cycles are rejected indiscriminately          | Valid cooperative architectures become impossible | Distinguish dependency cycles from containment cycles.             |
| Legacy links are reinterpreted without evidence          | Migration errors                                  | Preserve unresolved semantics and require explicit classification. |

## 18. Proposed Resolution

Adopt the canonical relationship, constraint and composition model defined by this CR as the normative relationship foundation for AOCL.

The resolution shall establish:

- A governed relationship vocabulary.
- First-class relationship identity and provenance.
- Explicit containment, reference and composition semantics.
- Scoped and traceable constraints.
- Composite and federated closed-loop arrangements.
- Shared control-scope representation.
- Explicit authority and coordination boundaries.
- Structural-to-behavioral traceability.
- Independent relationship, composition and constraint conformance.

Approval of this CR authorizes the detailed behavioral specification and control-contract modeling work to proceed against a coherent relationship foundation.

## 19. Subsequent Change Requests

| CR          | Title                                                  | Dependency on CR-005                                             |
| ----------- | ------------------------------------------------------ | ---------------------------------------------------------------- |
| AOCL-CR-006 | Establish the Behavioral Specification Schema          | Uses canonical behavioral and structural relationships.          |
| AOCL-CR-007 | Establish Control Contracts and State-Transition Model | Uses control scopes, constraints and coordination relationships. |
| AOCL-CR-008 | Establish Verification and Evidence Model              | Uses observation, information and behavioral relationships.      |
| AOCL-CR-009 | Establish Simulation Scenario and Disturbance Model    | Uses composition, Plant and influence relationships.             |
| AOCL-CR-010 | Establish Canonical Execution Semantics                | Uses the complete relationship and composition foundation.       |

**End of AOCL-CR-005**

## Architectural observations before treating CR-005 as ready for approval

There are four decisions I would pay particular attention to during review:

1. Relationship ontology versus implementation graph. A visual edge is a representation of a relationship, not the relationship itself. The canonical relationship must remain valid independently of the canvas.
2. Control authority versus connectivity. Connecting a Controller to a Plant must not grant it authority to intervene. Authority is a separately governed property.
3. Composition versus containment. A composite loop can coordinate independently governed loops without owning them. This is particularly important for federated architectures.
4. Constraint propagation. A safety or regulatory constraint must not be weakened by composition, inheritance or local configuration.

The next step after this is AOCL-CR-006: Behavioral Specification Schema. That CR will translate the behavioral lifecycle and relationship foundation into a formal, machine-readable specification, while leaving execution semantics to CR-010.