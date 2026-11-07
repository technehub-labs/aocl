> **Status:** Proposed · **Queued:** 2026-11-07 — the behavioral lifecycle becomes machine-readable — typed behavioral elements over a directed graph, stage coverage, conditions/guards, exception and safe-state paths, human participation (P19–P26) · Carries forward the review's pre-approval observations (kept in-document as review checks).

---

# AOCL-CR-006 — Establish the Canonical Behavioral Specification Schema

**Change Request ID:** AOCL-CR-006\
**Title:** Establish the Canonical Behavioral Specification Schema\
**Status:** Proposed\
**Priority:** Critical\
**Change Type:** Metamodel / Schema / Behavioral Modeling\
**Depends On:**

- AOCL-CR-001 — Establish Canonical Conceptual Foundation and Normative Engineering Principles
- AOCL-CR-002 — Establish the Canonical Closed-Loop Metamodel
- AOCL-CR-003 — Establish the Canonical Seven-Stage Behavioral Lifecycle Metamodel
- AOCL-CR-004 — Establish the Canonical Control Architecture Metamodel
- AOCL-CR-005 — Establish the Canonical Relationship, Constraint and Loop Composition Model

**Affected Areas:** Behavioral Model, Canonical Domain Model, Schema Registry, Model Validation, Behavioral Conformance, Model Serialization, Visual Modeling Studio, Simulation Readiness.

---

## 1. Purpose

Establish a canonical, machine-readable Behavioral Specification Schema for AOCL.

The preceding foundation CRs define the conceptual identity of a closed loop, its principal entities, its behavioral lifecycle, its control architecture and its relationship and composition semantics.

This CR defines how the behavior of an individual closed loop is formally specified.

A behavioral specification describes:

- What behavioral responsibilities the loop must fulfil.
- Which behavioral elements realize those responsibilities.
- How those elements are related.
- What conditions govern transitions between them.
- What inputs and outputs are expected.
- Which policies and constraints apply.
- How exceptional and alternative behavior is represented.
- How behavior can be traced to intent, control architecture and verification requirements.

The schema must be suitable for authoring, validation, exchange, versioning and subsequent interpretation by AOCL engineering and simulation capabilities.

It must be technology-independent and must not assume a particular workflow engine, programming language, control algorithm or simulation implementation.

## 2. Problem Statement

The seven-stage behavioral lifecycle establishes the responsibilities that a closed loop must account for. However, a list of stages is insufficient to describe actual operational behavior.

A realistic closed loop may:

- Execute behavioral responsibilities in different orders.
- Repeat analysis after receiving new observations.
- Branch according to operating conditions.
- Perform multiple activities concurrently.
- Wait for an asynchronous event.
- Request human approval.
- Retry an unsuccessful intervention.
- Escalate when a constraint or threshold is breached.
- Enter a safe state following a failure.
- Verify an outcome through an independent observation path.
- Learn from verified evidence without automatically changing its authority or policy.

A fixed sequence cannot adequately express these conditions.

AOCL therefore requires a formal behavioral specification that can represent both the canonical responsibilities and the actual behavioral structure of a particular loop.

Without such a specification, the modeling canvas risks becoming a diagramming tool whose connections cannot be reliably validated or interpreted by downstream engineering capabilities.

## 3. Objectives

This CR shall:

1. Establish the BehavioralSpecification as a first-class model artifact.
2. Define the structure of a behavioral specification.
3. Define canonical behavioral element types.
4. Associate behavioral elements with the seven canonical responsibilities.
5. Establish graph-based behavioral representation.
6. Define transition, branching, synchronization and exception constructs.
7. Define behavioral inputs, outputs and information dependencies.
8. Define condition and policy references.
9. Establish behavioral element traceability to intent and control architecture.
10. Define behavioral specification validation and conformance.
11. Establish versioning and serialization requirements.
12. Provide a machine-readable foundation for subsequent control contracts and execution semantics.

## 4. Normative Design Principles

| ID       | Principle                 | Normative implication                                                                         |
| -------- | ------------------------- | --------------------------------------------------------------------------------------------- |
| AOCL-P19 | Behavioral Explicitness   | Required behavior must be explicitly represented.                                             |
| AOCL-P20 | Graph-Based Behavior      | Behavior must support branching, repetition, parallelism and asynchronous transitions.        |
| AOCL-P21 | Stage Traceability        | Behavioral elements must map to canonical behavioral responsibilities.                        |
| AOCL-P22 | Contractual Clarity       | Behavioral inputs, outputs and expected conditions must be identifiable.                      |
| AOCL-P23 | Exception Awareness       | Exceptional behavior must be modeled rather than left implicit.                               |
| AOCL-P24 | Execution Independence    | Behavioral specification must remain independent of a particular execution engine.            |
| AOCL-P25 | Verification Traceability | Behavior must identify what requires verification and where evidence is expected.             |
| AOCL-P26 | Governed Adaptation       | Learning and adaptation must not implicitly change authority, constraints or approved policy. |

These principles supplement the principles established by CR-001 through CR-005.

## 5. Scope

### 5.1 In scope

- BehavioralSpecification structure.
- Behavioral element taxonomy.
- Canonical stage mapping.
- Behavioral graph representation.
- Transition and routing constructs.
- Conditions and guards.
- Parallel and synchronization constructs.
- Event and asynchronous behavior.
- Exception and recovery representation.
- Inputs, outputs and information dependencies.
- Human participation and approval.
- Behavioral references to control architecture.
- Traceability and conformance requirements.
- Schema versioning and serialization.

### 5.2 Out of scope

| Concern                                          | Assigned CR |
| ------------------------------------------------ | ----------- |
| Detailed control variables and control contracts | CR-007      |
| Formal state-transition and actuation semantics  | CR-007      |
| Verification evidence structures                 | CR-008      |
| Scenario and disturbance definitions             | CR-009      |
| Runtime interpretation and scheduling            | CR-010      |
| Logical simulation engine                        | CR-011      |
| State-based simulation engine                    | CR-012      |
| Trace recording and deterministic replay         | CR-013      |
| Visual modeling interface                        | CR-014      |
| Simulation controls and runtime visualization    | CR-015      |

CR-006 defines what behavior is specified and how it is represented. It does not define the complete runtime meaning of executing that behavior.

## 6. Canonical BehavioralSpecification

### 6.1 Definition

A **BehavioralSpecification** is a governed, versioned model artifact that defines the behavioral responsibilities, elements, relationships, conditions, information dependencies and expected outcomes through which a closed loop realizes its intended operation.

It provides the behavioral representation of a closed loop independently of the specific technology used to implement or execute it.

### 6.2 Ownership and association

A BehavioralSpecification shall be associated with a ClosedLoop through the binding mechanism established by CR-002.

The specification must have its own identity and version.

The model must support:

- One primary approved BehavioralSpecification per ClosedLoop at a given model baseline.
- Draft and alternative specifications during engineering.
- Versioned specifications associated with different model baselines.
- Explicit references to reusable behavioral specifications where appropriate.

Alternative specifications must not be treated as simultaneously authoritative unless their applicability and selection conditions are explicitly defined.

### 6.3 Top-level structure

A BehavioralSpecification shall contain the following logical sections:

| Section                          | Responsibility                                                 |
| -------------------------------- | -------------------------------------------------------------- |
| Specification Identity           | Stable identity, name, definition and version.                 |
| Context Binding                  | Associated ClosedLoop and applicable operational context.      |
| Behavioral Objectives            | Behavioral outcomes and responsibilities to be realized.       |
| Stage Coverage                   | Mapping to the seven canonical responsibilities.               |
| Behavioral Elements              | Nodes representing behavioral responsibilities and constructs. |
| Behavioral Relationships         | Directed relationships between elements.                       |
| Conditions                       | Guards, predicates and routing conditions.                     |
| Information Dependencies         | Inputs, outputs and information references.                    |
| Policy and Constraint References | Applicable policies, goals and constraints.                    |
| Exception Model                  | Failure, escalation, recovery and safe-state paths.            |
| Verification References          | Expected verification responsibilities and evidence targets.   |
| Traceability                     | Links to intent, architecture and model requirements.          |
| Governance                       | Lifecycle, provenance and approval information.                |

This is a logical schema organization, not a requirement to store every section in a separate file.

## 7. Canonical Behavioral Element Model

### 7.1 BehavioralElement

A BehavioralElement is a first-class node within a BehavioralSpecification.

It shall have:

- Stable identifier.
- Element type.
- Name.
- Definition.
- Behavioral stage association.
- Lifecycle status.
- Input references where applicable.
- Output references where applicable.
- Applicable conditions.
- Applicable constraints.
- Traceability references.
- Provenance.

An element may also contain type-specific attributes.

### 7.2 Canonical behavioral element types

The initial canonical vocabulary shall include the following.

| Element type     | Purpose                                                        | Typical stage association |
| ---------------- | -------------------------------------------------------------- | ------------------------- |
| IntentReference  | Identifies the governing intent and desired outcomes           | Intent                    |
| Observation      | Represents the receipt or acquisition of information           | Observe                   |
| Analysis         | Represents interpretation of observations and context          | Analyze                   |
| Assessment       | Represents an evaluated situation or condition                 | Analyze                   |
| Decision         | Represents selection of a response                             | Decide                    |
| Approval         | Represents an authorization or human approval requirement      | Decide / Execute          |
| Action           | Represents an intended intervention                            | Execute                   |
| Verification     | Represents evaluation of an expected outcome                   | Verify                    |
| Learning         | Represents evaluation and recording of experience              | Learn                     |
| Event            | Represents an occurrence that may trigger behavior             | Any                       |
| Condition        | Represents a condition used to govern behavior                 | Any                       |
| Wait             | Represents suspension pending an event or condition            | Any                       |
| Synchronization  | Represents coordination of concurrent behavioral paths         | Any                       |
| Escalation       | Represents transfer to a higher authority or intervention path | Any                       |
| ExceptionHandler | Represents defined handling of an exceptional condition        | Any                       |
| SafeState        | Represents a defined safe or controlled fallback behavior      | Execute / Verify          |
| SubSpecification | References a separately governed behavioral specification      | Any                       |

The canonical element vocabulary is intentionally extensible, but extensions must not redefine the semantics of canonical types.

### 7.3 Stage association

Every substantive behavioral element must map to at least one canonical behavioral responsibility.

The seven responsibilities are:

1. Intent.
2. Observe.
3. Analyze.
4. Decide.
5. Execute.
6. Verify.
7. Learn.

The mapping must support many-to-many associations where necessary.

An element may support multiple responsibilities, and a responsibility may be realized by multiple elements.

An Event, Condition or Synchronization element may participate across multiple stages.

A technical element type must not be mistaken for a behavioral stage. For example, an Observation is a behavioral element, whereas Observe is the responsibility it supports.

### 7.4 Stage coverage

A BehavioralSpecification must declare which canonical stages are:

- Required.
- Realized.
- Partially realized.
- Not applicable.
- Deferred or unresolved.

A stage may only be declared NotApplicable where the specification provides a justified rationale.

The absence of a modeled stage must not automatically be interpreted as evidence that the responsibility is unnecessary.

In particular, Verify must remain an explicit consideration. Successful execution of an Action must not be treated as successful verification of the intended outcome.

## 8. Behavioral Graph Model

### 8.1 Graph representation

A BehavioralSpecification shall represent its behavior as a directed graph.

The graph comprises:

- Behavioral elements as nodes.
- Behavioral relationships as directed edges.
- Conditions associated with applicable edges or nodes.
- Explicit entry and termination semantics.
- References to external events, information and constraints.

The graph must support multiple valid paths.

It must not assume that all elements execute sequentially or exactly once.

### 8.2 Behavioral relationship types

The initial canonical behavioral relationship vocabulary shall include:

| Relationship           | Meaning                                                          |
| ---------------------- | ---------------------------------------------------------------- |
| FlowsTo                | Establishes a possible progression from one element to another.  |
| BranchesTo             | Establishes an alternative path.                                 |
| Triggers               | Identifies an event or condition that activates another element. |
| DependsOn              | Identifies a required dependency.                                |
| ExecutesInParallelWith | Identifies concurrent behavioral execution.                      |
| SynchronizesWith       | Establishes a synchronization dependency.                        |
| RepeatsTo              | Represents a repetition or feedback path.                        |
| ReturnsTo              | Represents a return to an earlier behavioral responsibility.     |
| EscalatesTo            | Transfers behavior to an escalation path.                        |
| HandlesException       | Connects an element to its exception-handling path.              |
| TerminatesWith         | Identifies a defined termination outcome.                        |
| Invokes                | Invokes a referenced behavioral specification.                   |

These relationships extend the general relationship foundation of CR-005 with behavioral-specific semantics.

Their execution interpretation will be defined by CR-010.

### 8.3 Entry and termination

A BehavioralSpecification must declare its entry conditions.

It must also identify applicable termination outcomes.

Termination outcomes may include:

- Successful completion.
- Verified completion.
- Controlled termination.
- Cancellation.
- Escalation.
- Safe-state transition.
- Failure.
- Suspended or awaiting an external event.

A closed loop may continue operating indefinitely. Consequently, the specification must distinguish termination of an individual behavioral invocation from termination of the closed loop itself.

### 8.4 Branching

A specification must support conditional branching.

A branch must identify:

- The source element.
- The target element.
- The governing condition.
- The condition evaluation context.
- The applicable fallback behavior where required.

The schema must support mutually exclusive and non-exclusive branch conditions.

Where multiple branches may be selected, the specification must explicitly identify whether the behavior is concurrent, prioritized or otherwise coordinated.

### 8.5 Repetition and feedback

The graph must support repetition, including:

- Retry.
- Re-analysis.
- Re-observation.
- Re-verification.
- Continuous monitoring.
- Periodic execution.
- Return to a prior behavioral stage.

Repetition must be represented explicitly.

A repeated path should identify its governing condition or termination criterion where applicable.

The schema must not impose arbitrary iteration limits. Where a limit is required for safe or bounded behavior, it must be explicitly declared.

### 8.6 Parallelism and synchronization

The schema must support multiple behavioral paths executing concurrently.

A Synchronization element or equivalent construct must identify the coordination requirement.

Supported synchronization patterns should include:

- Wait for all.
- Wait for any.
- Wait for a specified subset.
- Conditional synchronization.
- Timeout-based synchronization.

The schema defines these as behavioral requirements, not as a mandate for a specific runtime scheduling mechanism.

### 8.7 Asynchronous behavior

Behavioral specifications must support asynchronous events.

Examples include:

- A delayed sensor observation.
- An external approval.
- A Plant state change.
- An actuator completion notification.
- An external service response.
- A scheduled observation.
- A timeout.

The specification must identify the event or condition that resumes the suspended behavioral path.

## 9. Conditions and Guards

### 9.1 Condition model

A Condition represents a predicate or evaluated circumstance that influences behavioral progression.

Conditions may be associated with:

- Behavioral elements.
- Behavioral transitions.
- Branches.
- Exception handlers.
- Entry conditions.
- Termination conditions.
- Approval requirements.

A condition must have a stable identifier and an explicit semantic definition.

### 9.2 Condition properties

The initial logical condition model shall support:

- Subject or referenced variable.
- Operator.
- Comparison value or expression reference.
- Unit or type where applicable.
- Evaluation context.
- Applicable time or freshness requirement.
- Result interpretation.
- Provenance.

### 9.3 Condition categories

The schema should distinguish:

- State conditions.
- Threshold conditions.
- Temporal conditions.
- Event conditions.
- Authorization conditions.
- Policy conditions.
- Data-quality conditions.
- Composite conditions.

Detailed type systems, variable definitions and executable expressions are deferred to CR-007.

### 9.4 Condition evaluation

The schema must not assume that a condition is always a simple Boolean comparison.

Conditions may require:

- Evaluation against multiple observations.
- Temporal windows.
- Aggregation.
- Contextual interpretation.
- External policy evaluation.
- Human judgment.

Where evaluation is delegated to an external mechanism, the specification must identify the responsible reference and the expected result contract.

## 10. Behavioral Inputs and Outputs

### 10.1 Input model

A behavioral element may consume:

- Observations.
- Assessments.
- Decisions.
- Events.
- Knowledge resources.
- Policies.
- Goals and constraints.
- External information.
- Results from preceding elements.

Inputs must be explicitly identifiable.

### 10.2 Output model

A behavioral element may produce:

- Observations.
- Assessments.
- Decisions.
- Approval requests or results.
- Actions.
- Verification results.
- Learning records.
- Events.
- Status information.
- Exception information.

Outputs must be traceable to their producing element.

### 10.3 Information dependencies

Information dependencies must use the canonical relationships established by CR-005.

The behavioral specification must distinguish:

- Information that is required.
- Information that is optional.
- Information that is conditional.
- Information that may be stale or incomplete.
- Information that is derived or inferred.
- Information that must be independently verified.

A behavioral element must not be considered adequately specified merely because an input or output is named.

Its expected meaning and relationship to the behavioral responsibility must be clear.

## 11. Policy, Constraint and Authority References

Behavioral elements must be able to reference applicable:

- Goals.
- Control constraints.
- Policies.
- Authorization requirements.
- Control architecture components.
- Control scopes.
- Enterprise entities.

These must use governed references rather than duplicated definitions.

The specification must identify the relationship between a behavioral element and its applicable constraint.

For example:

- An Action may be subject to authorization and safety constraints.
- A Decision may be constrained by policy and operating context.
- A Verification may be required to establish that a goal has been achieved.
- A Learning element may be prohibited from changing an approved policy without authorization.

A behavioral specification must not grant authority through the existence of an Action element or an Actuates relationship.

Authority remains an explicit property of the governed control architecture and applicable authorization model.

## 12. Human Participation

The schema must support human participation as a first-class behavioral concern.

A human may participate as:

- Decision-maker.
- Approver.
- Operator.
- Observer.
- Supervisor.
- Exception handler.
- Verification authority.

The specification must identify the human responsibility, required input, expected response and applicable authorization context.

Human participation must not be represented merely as an untyped external task.

A human approval requirement must be distinguishable from a notification or informational event.

The schema must also permit timeout, escalation and fallback behavior when a required human response is unavailable.

## 13. Exception and Recovery Model

### 13.1 Purpose

A valid behavioral specification must account for relevant exceptional conditions.

Exception handling must not be treated as an informal annotation.

### 13.2 Exception categories

The initial categories shall include:

- Observation failure.
- Data-quality failure.
- Analysis failure.
- Decision failure.
- Authorization failure.
- Execution failure.
- Verification failure.
- Timeout.
- Dependency failure.
- Constraint violation.
- Unexpected state.
- External service failure.
- Human intervention required.

### 13.3 Exception handling requirements

An exception path should identify:

- Triggering condition.
- Affected behavioral element.
- Exception category.
- Handling responsibility.
- Recovery or escalation path.
- Applicable constraints.
- Expected termination or resumption condition.

A specification may identify an exception as unresolved during early engineering, but unresolved critical exceptions must prevent the specification from being classified as fully behaviorally conformant.

### 13.4 Safe-state behavior

Where applicable, the specification must identify safe-state behavior.

A safe-state reference must identify:

- The relevant controlled scope.
- The conditions requiring transition.
- The expected safe-state outcome.
- The responsible authority or mechanism.
- The verification responsibility.

CR-006 defines the behavioral representation. Detailed state-transition and safety-control semantics remain in CR-007.

## 14. Behavioral Traceability

A BehavioralSpecification must support traceability across the AOCL model.

At minimum, traceability must be possible between:

| From                     | To                                                     |
| ------------------------ | ------------------------------------------------------ |
| Intent and goals         | Behavioral objectives                                  |
| Goals                    | Verification responsibilities                          |
| Constraints              | Decisions and Actions                                  |
| Behavioral elements      | Canonical behavioral stages                            |
| Behavioral elements      | Control architecture components                        |
| Observations             | Sensor and information sources                         |
| Actions                  | Controller and Actuator responsibilities               |
| Verification elements    | Expected outcomes and evidence requirements            |
| Learning elements        | Knowledge resources and approved adaptation boundaries |
| Behavioral specification | ClosedLoop identity and version                        |

Traceability must support impact analysis.

For example, a change to a control constraint should make it possible to identify affected Decisions, Actions and behavioral paths.

A change to the control architecture should make it possible to identify the behavioral elements that depend on the changed component.

## 15. Behavioral Specification Lifecycle

The BehavioralSpecification shall have a lifecycle distinct from runtime execution.

The proposed lifecycle is:

- Draft.
- InReview.
- Approved.
- Deprecated.
- Retired.

The lifecycle must support:

- Review and approval.
- Version history.
- Change rationale.
- Provenance.
- Model baseline association.
- Supersession references.

Approval of a specification does not imply deployment, operational realization or successful simulation.

Alternative specifications must remain distinguishable from the approved specification.

## 16. Validation and Conformance Requirements

The following requirements are normative.

| ID      | Requirement                                                                          |
| ------- | ------------------------------------------------------------------------------------ |
| BSS-001 | A BehavioralSpecification must have a stable identifier.                             |
| BSS-002 | A BehavioralSpecification must identify its associated ClosedLoop.                   |
| BSS-003 | A BehavioralSpecification must have an independent version.                          |
| BSS-004 | The specification must declare its behavioral objectives.                            |
| BSS-005 | Behavioral elements must have unique identifiers within the specification.           |
| BSS-006 | Every behavioral element must have a valid canonical or governed extension type.     |
| BSS-007 | Substantive behavioral elements must map to canonical stage responsibilities.        |
| BSS-008 | Stage coverage must be explicitly declared.                                          |
| BSS-009 | NotApplicable stage declarations must include justification.                         |
| BSS-010 | The specification must identify its entry conditions.                                |
| BSS-011 | The specification must identify applicable termination outcomes.                     |
| BSS-012 | Behavioral relationships must have valid endpoints.                                  |
| BSS-013 | Behavioral relationship types must have defined semantics.                           |
| BSS-014 | Branching must support explicit conditions.                                          |
| BSS-015 | Repetition must be explicitly represented.                                           |
| BSS-016 | Parallel behavior must be representable.                                             |
| BSS-017 | Synchronization requirements must be identifiable.                                   |
| BSS-018 | Asynchronous event handling must be supported.                                       |
| BSS-019 | Inputs and outputs must be identifiable.                                             |
| BSS-020 | Information dependencies must be traceable.                                          |
| BSS-021 | Conditions must have explicit definitions and evaluation context.                    |
| BSS-022 | Policy and constraint references must resolve or be explicitly marked unresolved.    |
| BSS-023 | Behavioral elements must not independently grant control authority.                  |
| BSS-024 | Human approval and human notification must be distinguishable.                       |
| BSS-025 | Exception paths must be representable.                                               |
| BSS-026 | Critical unresolved exception paths must prevent full behavioral conformance.        |
| BSS-027 | Applicable safe-state behavior must be identifiable.                                 |
| BSS-028 | Verification responsibilities must be explicitly representable.                      |
| BSS-029 | Action completion must not be treated as proof of outcome verification.              |
| BSS-030 | Learning behavior must preserve governance and authorization boundaries.             |
| BSS-031 | Behavioral elements must support traceability to control architecture.               |
| BSS-032 | Behavioral elements must support traceability to intent and goals.                   |
| BSS-033 | Structural and behavioral relationships must remain distinguishable.                 |
| BSS-034 | The specification must support versioning and lifecycle governance.                  |
| BSS-035 | Schema validation must distinguish structural validity from behavioral completeness. |
| BSS-036 | Behavioral conformance must remain distinct from simulation readiness.               |

## 17. Conformance Model

AOCL shall distinguish four levels of BehavioralSpecification conformance.

### 17.1 Schema Conformance

Determines whether the specification conforms to the canonical data structure and type definitions.

### 17.2 Structural Conformance

Determines whether behavioral elements and relationships are correctly connected and referenced.

### 17.3 Behavioral Conformance

Determines whether the specification adequately represents its required behavioral responsibilities, paths, conditions, exceptions and traceability.

### 17.4 Simulation Readiness

Determines whether the specification has sufficient information to support the simulation capabilities intended for the model.

Simulation readiness may require additional control contracts, state definitions, scenario bindings and verification structures established by subsequent CRs.

A specification can therefore be schema-conformant and structurally valid without being behaviorally complete or simulation-ready.

## 18. Canonical Serialization Requirements

The canonical BehavioralSpecification must be representable in a machine-readable format.

The implementation should support:

- JSON as a canonical interchange representation.
- YAML as a human-readable serialization.
- JSON Schema for structural validation.
- Semantic validators for relationship and behavioral integrity.
- Explicit schema versioning.
- Controlled extension mechanisms.
- Round-trip serialization tests.

The serialization format must not become the source of behavioral semantics. The canonical metamodel defines those semantics.

### 18.1 Illustrative representation

The following is an illustrative structural example, not the final normative JSON Schema.

```
behavioralSpecification:
  id: aocl-bs-network-assurance-001
  name: Network Service Assurance Behavior
  version: 0.1.0
  schemaVersion: 1.0.0
  status: Draft

  closedLoopRef:
    id: aocl-loop-network-assurance-001
    sourceSystem: AOCL

  objectives:
    - id: obj-maintain-latency
      goalRef: goal-service-latency
      description: Maintain service latency within the defined threshold

  stageCoverage:
    - stage: Intent
      status: Realized
    - stage: Observe
      status: Realized
    - stage: Analyze
      status: Realized
    - stage: Decide
      status: Realized
    - stage: Execute
      status: Realized
    - stage: Verify
      status: Realized
    - stage: Learn
      status: Realized

  elements:
    - id: observe-latency
      type: Observation
      stage: Observe
      outputs:
        - latency-observation

    - id: analyze-latency
      type: Analysis
      stage: Analyze
      inputs:
        - latency-observation
      outputs:
        - congestion-assessment

    - id: decide-remediation
      type: Decision
      stage: Decide
      inputs:
        - congestion-assessment
      outputs:
        - remediation-decision

    - id: execute-reroute
      type: Action
      stage: Execute
      inputs:
        - remediation-decision
      controlArchitectureRef:
        actuatorRef: traffic-engineering-actuator

    - id: verify-latency
      type: Verification
      stage: Verify
      inputs:
        - post-action-latency-observation

    - id: record-learning
      type: Learning
      stage: Learn
      inputs:
        - verification-result

  relationships:
    - id: rel-001
      type: FlowsTo
      source: observe-latency
      target: analyze-latency

    - id: rel-002
      type: FlowsTo
      source: analyze-latency
      target: decide-remediation

    - id: rel-003
      type: FlowsTo
      source: decide-remediation
      target: execute-reroute

    - id: rel-004
      type: FlowsTo
      source: execute-reroute
      target: verify-latency

    - id: rel-005
      type: FlowsTo
      source: verify-latency
      target: record-learning

  governance:
    approvalRequired: true
```

The example deliberately does not define executable control expressions, scheduling behavior, state-transition equations or simulation parameters. Those belong to later CRs.

## 19. Reference Behavioral Patterns

The schema must be capable of representing at least the following reference patterns.

### Pattern A — Standard feedback cycle

Observe → Analyze → Decide → Execute → Verify → Learn → Observe.

The pattern must support repeated operation and must not imply that the loop terminates after one pass.

### Pattern B — Conditional remediation

A decision leads to alternative actions based on operating conditions.

The schema must represent branch conditions and the alternative paths.

### Pattern C — Human approval

A decision creates an approval requirement. Execution proceeds only after the required authorization is received.

The schema must represent approval, timeout, rejection and escalation paths.

### Pattern D — Failed execution

An Action fails or returns an unsuccessful status. The behavior enters an exception path, which may retry, escalate or transition to a safe state.

### Pattern E — Unsuccessful outcome

An Action executes successfully, but independent verification establishes that the intended outcome was not achieved.

The specification must permit re-analysis or alternative remediation.

### Pattern F — Parallel observation

Multiple observation paths contribute to a shared analysis or assessment.

The schema must support parallel inputs and synchronization requirements.

### Pattern G — Asynchronous external dependency

A behavioral path waits for an external event or response before proceeding.

The specification must identify the event, wait condition, timeout and applicable exception path.

### Pattern H — Governed learning

A verification result updates a Knowledge resource or learning record.

The specification must distinguish recording learning from authorizing a policy or controller change.

## 20. Migration and Compatibility

The implementation must preserve existing AOCL model identities and behavioral references.

Migration must:

- Preserve existing decision-model selections.
- Preserve existing custom behavioral definitions where available.
- Preserve existing loop registrations and identifiers.
- Preserve existing maturity assessment references.
- Preserve existing realization information.
- Preserve CLAM integration references.
- Avoid interpreting existing workflow descriptions as complete BehavioralSpecifications without validation.
- Record unresolved mappings to the canonical seven stages.
- Allow incomplete specifications to remain Draft.
- Avoid fabricating conditions, inputs, outputs or exception paths.
- Provide migration diagnostics for missing or ambiguous behavioral definitions.

Existing OODA, MAPE and CUSTOM decision-model selections must remain supported.

They should be represented as decision architecture references or governed mappings, not as substitutes for the complete behavioral specification.

## 21. Acceptance Criteria

This CR is accepted when:

1. BehavioralSpecification is established as a first-class model artifact.
2. Specification identity, ownership and versioning are defined.
3. The seven canonical behavioral responsibilities are supported.
4. Stage coverage and applicability are explicitly represented.
5. Canonical behavioral element types are defined.
6. The model supports directed graph representation.
7. Branching and conditional paths are representable.
8. Repetition and feedback paths are representable.
9. Parallel execution and synchronization are representable.
10. Asynchronous events and waiting behavior are representable.
11. Entry and termination conditions are defined.
12. Inputs and outputs are identifiable.
13. Information dependencies are traceable.
14. Policy and constraint references are supported.
15. Human approval and participation are representable.
16. Exception and recovery paths are representable.
17. Safe-state behavior can be referenced.
18. Verification responsibilities are explicitly representable.
19. Learning and adaptation boundaries are governed.
20. Behavioral elements can be traced to control architecture components.
21. Behavioral elements can be traced to intent and goals.
22. Schema, structural, behavioral and simulation-readiness conformance are distinguishable.
23. JSON and YAML representations preserve the same canonical semantics.
24. Reference models demonstrate the eight required behavioral patterns.
25. Automated validation tests cover the normative requirements.
26. Existing model and decision-model compatibility is preserved.

## 22. Risks and Mitigations

| Risk                                                        | Consequence                                     | Mitigation                                                  |
| ----------------------------------------------------------- | ----------------------------------------------- | ----------------------------------------------------------- |
| Behavioral model becomes a workflow engine specification    | Premature coupling to implementation technology | Keep the schema technology-independent.                     |
| Seven stages are interpreted as a rigid sequence            | Inability to model realistic control behavior   | Use stage mapping over a directed behavioral graph.         |
| Behavioral elements are confused with structural components | Inconsistent architecture and behavior models   | Maintain separate metamodels and explicit bindings.         |
| Conditions are under-specified                              | Ambiguous behavioral interpretation             | Require explicit condition identity and evaluation context. |
| Exception behavior is optional in practice                  | Incomplete operational models                   | Make exception completeness part of behavioral conformance. |
| Learning implicitly changes policy                          | Ungoverned adaptation                           | Preserve explicit authorization and governance boundaries.  |
| Schema becomes excessively complex                          | Poor usability and adoption                     | Use a canonical core and controlled extensions.             |
| Simulation requirements are introduced prematurely          | Scope overlap with CR-010 to CR-012             | Keep execution and simulation semantics outside this CR.    |

## 23. Proposed Resolution

Adopt the canonical BehavioralSpecification model and schema requirements defined by this CR as the normative behavioral representation for AOCL.

The resolution shall establish:

- BehavioralSpecification as a governed, versioned artifact.
- Seven canonical behavioral responsibilities.
- Typed behavioral elements.
- Directed graph representation.
- Explicit transitions and conditions.
- Branching, repetition, parallelism and asynchronous behavior.
- Inputs, outputs and information dependencies.
- Human participation and approval.
- Exception, recovery and safe-state representation.
- Traceability to intent, control architecture and verification.
- Independent schema, structural, behavioral and simulation-readiness conformance.

Approval of this CR authorizes detailed control-contract and state-transition modeling to proceed against a common behavioral specification foundation.

## 24. Subsequent Change Requests

| CR          | Title                                                  | Dependency                                                                                  |
| ----------- | ------------------------------------------------------ | ------------------------------------------------------------------------------------------- |
| AOCL-CR-007 | Establish Control Contracts and State-Transition Model | Defines typed control variables, action contracts, state transitions and control semantics. |
| AOCL-CR-008 | Establish Verification and Evidence Model              | Defines verification criteria, evidence structures and outcome assessment.                  |
| AOCL-CR-009 | Establish Simulation Scenario and Disturbance Model    | Defines scenarios, initial conditions, disturbances and simulation parameters.              |
| AOCL-CR-010 | Establish Canonical Execution Semantics                | Defines how the behavioral specification is interpreted and executed.                       |
| AOCL-CR-011 | Establish Logical Simulation Engine                    | Implements logical behavioral simulation.                                                   |

**End of AOCL-CR-006**

## Architectural assessment

CR-006 establishes a useful boundary between three different things that AOCL must keep separate:

| Concern                  | What it defines                                  | Governing CR |
| ------------------------ | ------------------------------------------------ | ------------ |
| Behavioral specification | What the loop is supposed to do                  | CR-006       |
| Control contracts        | What actions and state transitions mean          | CR-007       |
| Execution semantics      | How specified behavior is interpreted at runtime | CR-010       |

This separation is important. It prevents the behavioral schema from becoming coupled to a particular simulation engine or workflow technology.

One design issue to carry forward: the canonical element taxonomy should be governed as a vocabulary, not treated as a closed list of all possible behavioral constructs. Domain-specific extensions will be necessary, but they must preserve the semantics and conformance requirements of the canonical elements.

The next change request is AOCL-CR-007 — Establish Control Contracts and State-Transition Model.