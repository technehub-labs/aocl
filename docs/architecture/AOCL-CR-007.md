> **Status:** Proposed · **Queued:** 2026-11-07 — control contracts and the state-transition model — actual/observed/estimated/desired/commanded/verified state distinctions, transition guards, authority, invariants, safe states (CTM-001..040) · Carries forward the review's pre-approval observations (kept in-document as review checks).

---

# AOCL-CR-007 — Establish the Canonical Control Contracts and State-Transition Model

**CR ID:** AOCL-CR-007\
**Title:** Establish the Canonical Control Contracts and State-Transition Model\
**Programme:** AOCL Conceptual and Modeling Foundation\
**Status:** Proposed\
**Priority:** Critical\
**Type:** Metamodel and Normative Semantics\
**Depends on:** AOCL-CR-001, AOCL-CR-002, AOCL-CR-004, AOCL-CR-005, AOCL-CR-006

---

## 1. Executive Summary

This Change Request establishes the canonical control-contract and state-transition model for AOCL.

The preceding modeling CRs establish the closed-loop aggregate, behavioral lifecycle, control architecture, relationships, constraints and behavioral specification. They provide the structural and behavioral representation of a closed loop.

What remains is a formal representation of the conditions under which a control intervention is permitted, the state it is intended to influence, and how the resulting state transition is evaluated.

AOCL must distinguish between:

- The actual state of a controlled system.
- The state inferred or estimated from observations.
- The desired or reference state.
- The state requested through a command.
- The execution status reported by an actuator.
- The resulting state established through subsequent observation.
- The outcome independently verified against the original intent.

Without these distinctions, AOCL cannot reliably determine whether an intervention was valid, whether a system transitioned as expected, or whether the intended outcome was achieved.

This CR introduces:

1. A canonical control-variable model.
2. A typed state and state-variable model.
3. A state-transition representation.
4. Control contracts for decisions and interventions.
5. Explicit authorization and constraint evaluation.
6. Transition invariants and safe-state definitions.
7. Multi-variable and multi-controller coordination semantics.
8. A technology-independent foundation for logical, state-based and hybrid simulation.

The result is a formal model that can support subsequent execution, verification and simulation engineering.

## 2. Problem Statement

AOCL needs to represent more than the presence of a Controller, Plant, Sensor and Actuator.

It must be able to answer:

- What property of the Plant is being controlled?
- What is its current state?
- How is that state established?
- What state is desired?
- Which variables may a Controller influence?
- Under what conditions is an intervention permitted?
- What must be true before an action can occur?
- What must be true after it occurs?
- Which transitions are valid?
- Which transitions are prohibited?
- What happens when a transition fails or produces an unexpected result?
- How is a safe state established and verified?
- How are competing interventions coordinated?

The existing conceptual model provides the elements needed to describe a loop, but these questions require explicit semantics.

A control command is not proof of a state transition. An actuator acknowledgement is not proof of an operational effect. A successful transition is not necessarily proof that the intended goal has been achieved.

AOCL therefore requires a canonical distinction between **control intent, authorization, intervention, state transition and verified outcome**.

## 3. Objectives

This CR SHALL:

1. Define the canonical control-variable taxonomy.
2. Establish a technology-independent state model.
3. Define state-transition semantics and guards.
4. Introduce explicit control contracts.
5. Formalize preconditions and postconditions.
6. Establish control authority and authorization requirements.
7. Define state invariants and safe-state semantics.
8. Support continuous, discrete and hybrid controlled systems.
9. Support coupled variables and multiple actuators.
10. Support multiple Controllers operating over shared or overlapping control scopes.
11. Establish traceability from Intent and behavioral specifications to state changes and expected outcomes.
12. Define conformance and simulation-readiness requirements.

## 4. Scope

### 4.1 In scope

- ControlVariable and its specializations.
- StateVariable and StateSpace.
- Desired, actual, observed, estimated and commanded state distinctions.
- Reference values, setpoints, bounds and operating modes.
- StateTransition and TransitionGuard.
- ControlContract.
- Preconditions and postconditions.
- Authorization and authority scope.
- Transition invariants.
- SafeState and safe-state transition requirements.
- ControlSignal, Command, Acknowledgement and execution-status distinctions.
- Multi-variable and multi-actuator relationships.
- Shared-variable and competing-controller constraints.
- Abstract support for continuous, discrete and hybrid state models.
- Model validation and conformance requirements.

### 4.2 Out of scope

The following are addressed by subsequent CRs:

| Concern                                                   | Owning CR   |
| --------------------------------------------------------- | ----------- |
| Verification evidence and evidence provenance             | AOCL-CR-008 |
| Simulation scenarios, disturbances and initial conditions | AOCL-CR-009 |
| Runtime execution, scheduling and orchestration semantics | AOCL-CR-010 |
| Logical simulation engine                                 | AOCL-CR-011 |
| State-based simulation engine                             | AOCL-CR-012 |
| Simulation trace, replay and deterministic run management | AOCL-CR-013 |

This CR defines what constitutes a valid control contract and state transition. It does not define the software runtime that evaluates or executes them.

## 5. Normative Design Principles

### P01 — Explicit Control Variables

Every controlled property SHALL be represented through an explicitly typed control variable or a governed reference to one.

### P02 — State Distinction

Actual, observed, estimated, desired and commanded states SHALL remain distinguishable.

### P03 — Contract-Bounded Intervention

Every modeled intervention SHALL be governed by an explicit contract defining its permitted scope and conditions.

### P04 — Explicit Authority

A Controller SHALL NOT acquire authority merely because it is related to, connected to or capable of influencing a Plant.

### P05 — Transition Integrity

A command or actuator acknowledgement SHALL NOT, by itself, establish that a Plant state transition occurred.

### P06 — Invariant Preservation

State transitions SHALL be evaluated against applicable invariants and constraints.

### P07 — Outcome Independence

The evaluation of an intervention's operational effect SHALL remain distinguishable from the evaluation of the intervention's execution status.

### P08 — Safe-State Governance

Safe states and the conditions for entering them SHALL be explicitly defined where applicable.

### P09 — Model Fidelity

State and contract representations SHALL preserve the distinctions necessary for meaningful simulation and verification.

### P10 — Technology Independence

The metamodel SHALL not prescribe a particular control algorithm, programming language, simulation solver or execution platform.

## 6. Canonical Control-Variable Model

### 6.1 ControlVariable

A `ControlVariable` represents a typed property relevant to the control of a Plant or operational domain.

It provides the semantic identity of a property whose value can be observed, estimated, targeted, constrained or influenced.

Proposed attributes:

| Attribute        | Description                                 |
| ---------------- | ------------------------------------------- |
| variableId       | Stable identifier                           |
| name             | Human-readable name                         |
| definition       | Semantic definition                         |
| dataType         | Value type                                  |
| unit             | Unit of measurement, where applicable       |
| valueDomain      | Permitted values or range                   |
| precision        | Relevant precision                          |
| operatingContext | Context in which the variable is meaningful |
| provenance       | Source of the variable definition           |
| lifecycleStatus  | Governed lifecycle state                    |

A variable's semantic identity SHALL be independent of the mechanism used to measure or manipulate it.

### 6.2 Canonical variable classifications

| Variable type       | Definition                                                                            | Example                       |
| ------------------- | ------------------------------------------------------------------------------------- | ----------------------------- |
| ControlledVariable  | Property whose behavior or value the loop seeks to regulate                           | Service latency               |
| ObservedVariable    | Property acquired through a Sensor or external observation source                     | Measured latency              |
| EstimatedVariable   | Property inferred from observations or a model                                        | Estimated congestion          |
| ManipulatedVariable | Property that a Controller is authorized to influence through an intervention         | Traffic allocation            |
| StateVariable       | Property representing the state of a Plant or component                               | Network operating mode        |
| DisturbanceVariable | Property representing an influence not directly controlled by the relevant Controller | External traffic demand       |
| ReferenceVariable   | Desired or target value used to evaluate control behavior                             | Target latency                |
| ConstraintVariable  | Property or value used to define a control boundary                                   | Maximum permitted utilization |

These classifications describe semantic roles. They are not mutually exclusive in all contexts. A variable may have multiple roles, provided each role is explicitly declared and its relationships are unambiguous.

### 6.3 Variable relationships

A variable MAY be:

- Observed by one or more Sensors.
- Derived from other variables.
- Estimated by a model or Controller.
- Controlled by one or more Controllers under explicit authority.
- Influenced by one or more ManipulatedVariables.
- Constrained by one or more ControlConstraints.
- Referenced by one or more Goals or ReferenceConditions.

A variable SHALL have a defined type and value domain appropriate to its use.

Where units are applicable, compatible units SHALL be required for comparisons, calculations and constraints.

### 6.4 Reference values and setpoints

AOCL SHALL distinguish:

- **ReferenceCondition:** the desired condition or outcome established by Intent.
- **Setpoint:** a target value assigned to a control variable for a particular control context.
- **OperatingBound:** a permitted value range or limit.
- **Tolerance:** an accepted deviation from a reference or target.
- **ControlRange:** the range within which a Controller may operate.
- **RateLimit:** the maximum permitted rate of change.
- **Deadband:** a range in which no corrective intervention is required or permitted by the applicable control policy.

A setpoint is not automatically equivalent to a Goal. It is a control parameter that may contribute to achieving one or more Goals.

A Controller SHALL NOT modify an authoritative reference value merely because it cannot achieve that value. Any authorized adaptation of a setpoint must remain traceable to its governing policy and authority.

## 7. Canonical State Model

### 7.1 State

A `State` represents the condition of a Plant, component or governed operational entity at a particular point or interval in time.

A state is established through one or more state variables and their values.

Proposed attributes:

| Attribute           | Description                                                       |
| ------------------- | ----------------------------------------------------------------- |
| stateId             | Stable identifier                                                 |
| subjectRef          | Plant or component whose state is represented                     |
| stateVariables      | Variables and corresponding values                                |
| stateSpaceRef       | Applicable state-space definition                                 |
| temporalReference   | Time or interval represented                                      |
| stateClassification | Actual, observed, estimated, desired or other declared state type |
| provenance          | How the state was established                                     |
| confidence          | Confidence or uncertainty where applicable                        |
| operatingMode       | Applicable operating mode                                         |
| validity            | Whether the state is current and valid for its intended use       |

### 7.2 State distinctions

AOCL SHALL represent the following separately:

| State representation | Meaning                                                                      |
| -------------------- | ---------------------------------------------------------------------------- |
| ActualState          | The actual condition of the controlled system, whether directly known or not |
| ObservedState        | State established from acquired observations                                 |
| EstimatedState       | State inferred through a model, estimator or analytical process              |
| DesiredState         | State required by Intent or an applicable reference condition                |
| CommandedState       | State requested through an authorized command or intervention                |
| VerifiedState        | State or outcome established through an applicable verification process      |

These representations SHALL NOT be treated as interchangeable.

For example, a Controller may command a network service to use an alternative route. The command may be acknowledged, but the actual network state may not change. Even if it changes, the resulting latency may remain outside the desired range.

### 7.3 StateSpace

A `StateSpace` defines the permitted or modeled states of a Plant or component.

It SHALL specify:

- State variables.
- Variable types and domains.
- Valid value ranges.
- Applicable operating modes.
- Permitted combinations of variable values.
- Relevant invariants.
- Initial-state requirements where known.
- Safe-state definitions where applicable.

A state space MAY be finite, discrete, continuous, hybrid or abstract.

A state space need not enumerate every possible state where the domain is continuous or too large to enumerate. In such cases, it SHALL define the relevant variables, domains, constraints and transition semantics.

### 7.4 Operating modes

An `OperatingMode` represents a governed mode of operation that may alter applicable control behavior.

Examples include:

- Normal.
- Degraded.
- Maintenance.
- Recovery.
- Emergency.
- Restricted.

Operating modes SHALL be defined by the domain model rather than assumed to be universal AOCL states.

Mode transitions SHALL be governed by explicit conditions, authority and constraints.

## 8. State-Transition Model

### 8.1 StateTransition

A `StateTransition` represents a permitted or modeled change from one state condition to another.

Proposed attributes:

| Attribute             | Description                              |
| --------------------- | ---------------------------------------- |
| transitionId          | Stable identifier                        |
| name                  | Transition name                          |
| definition            | Transition semantics                     |
| sourceState           | Source state or state predicate          |
| targetState           | Target state or state predicate          |
| transitionGuard       | Conditions required for transition       |
| transitionEffects     | Expected changes to state variables      |
| applicableConstraints | Constraints governing transition         |
| authorityRef          | Required authority                       |
| transitionType        | Discrete, continuous, hybrid or abstract |
| failureOutcomes       | Defined failure or alternative outcomes  |
| provenance            | Source of transition definition          |

A transition MAY be triggered by:

- An authorized intervention.
- A Plant-generated event.
- A disturbance.
- An external event.
- A human action.
- A scheduled or policy-governed condition.

Not every state transition is a Controller-initiated transition. AOCL must also represent spontaneous and disturbance-driven state changes.

### 8.2 TransitionGuard

A `TransitionGuard` defines the conditions that must hold before a transition is permitted.

It may reference:

- Current state.
- Observed or estimated values.
- Operating mode.
- Control constraints.
- Authorization status.
- Required approvals.
- Temporal conditions.
- Data quality and freshness.
- Environmental conditions.
- Resource availability.

A guard SHALL identify the subject, evaluation context and applicable condition semantics.

A transition SHALL NOT be considered valid solely because its guard evaluates successfully if the required authority or other mandatory controls are absent.

### 8.3 Transition outcomes

A transition SHALL support explicit outcome classification.

| Outcome     | Meaning                                                    |
| ----------- | ---------------------------------------------------------- |
| Completed   | Transition is established as completed                     |
| Rejected    | Transition was not permitted                               |
| Blocked     | A required condition or dependency was not satisfied       |
| Failed      | Transition did not achieve its defined transition result   |
| Partial     | Only part of the expected transition occurred              |
| Interrupted | Transition was interrupted before completion               |
| Unknown     | Available evidence is insufficient to establish the result |
| Superseded  | Transition was replaced by another authorized transition   |

The outcome of a transition SHALL remain distinct from the outcome of the overall control objective.

### 8.4 Transition types

AOCL SHALL support three abstract transition classes:

**Discrete transition**

A state changes between identifiable states or modes.

Example: `Normal` to `Degraded`.

**Continuous transition**

A state variable changes over time within a defined domain.

Example: network latency changes from 35 ms to 72 ms.

**Hybrid transition**

The system combines continuous variable evolution with discrete state changes.

Example: utilization increases continuously until a threshold causes a discrete operating-mode change.

The metamodel SHALL represent these classes without requiring a specific numerical solver or simulation technology.

## 9. Control Contract Model

### 9.1 ControlContract

A `ControlContract` defines the conditions and obligations governing a control decision or intervention.

It formalizes the relationship between an intended control effect, the authority to initiate it, the conditions under which it may occur and the expected result.

A contract SHALL be associated with the relevant ClosedLoop and linked to the applicable Controller, Plant, BehavioralSpecification and control variables.

Proposed attributes:

| Attribute             | Description                                |
| --------------------- | ------------------------------------------ |
| contractId            | Stable identifier                          |
| name                  | Contract name                              |
| definition            | Contract purpose and semantics             |
| subjectRef            | Controller, action or controlled scope     |
| targetRef             | Plant or target component                  |
| applicableVariables   | Variables governed by the contract         |
| preconditions         | Conditions required before intervention    |
| authorization         | Required authority and approval            |
| permittedScope        | Scope within which intervention is allowed |
| constraints           | Applicable control constraints             |
| expectedEffects       | Expected state changes                     |
| postconditions        | Conditions evaluated after intervention    |
| failureConditions     | Conditions indicating failure              |
| compensationPolicyRef | Optional recovery or compensation policy   |
| lifecycleStatus       | Contract lifecycle state                   |
| version               | Contract version                           |

### 9.2 Contract types

AOCL SHALL support at least the following contract classifications:

| Contract type           | Purpose                                                                          |
| ----------------------- | -------------------------------------------------------------------------------- |
| DecisionContract        | Governs the conditions and authority under which a decision may be selected      |
| ActionContract          | Governs the conditions and authority under which an intervention may be executed |
| StateTransitionContract | Defines the permitted transition and its expected effects                        |
| VerificationContract    | Defines the conditions against which a transition or outcome is evaluated        |

These classifications MAY be represented through a common ControlContract structure with typed specializations.

### 9.3 Preconditions

A precondition defines what must be true before the governed decision or action is permitted.

Examples:

- The observed variable is sufficiently fresh.
- The Plant is in an eligible operating mode.
- The Controller has authority over the target variable.
- The required human approval has been granted.
- The target value is within permitted operating bounds.
- Required resources are available.
- No higher-priority safety interlock is active.

Preconditions SHALL be explicit and traceable to their governing requirements, constraints or policies.

### 9.4 Postconditions

A postcondition defines what must be evaluated after a decision, action or transition.

Postconditions may establish:

- Whether the intervention was accepted.
- Whether the actuator reported execution.
- Whether the Plant changed state.
- Whether the intended variable reached its target range.
- Whether the desired outcome was achieved.
- Whether applicable invariants remained satisfied.

Postconditions SHALL distinguish execution completion from operational outcome achievement.

### 9.5 Contract failure semantics

A contract SHALL define relevant failure conditions and the required disposition.

Possible dispositions include:

- Reject the intervention.
- Block execution.
- Request human approval.
- Escalate to a supervisory Controller.
- Enter a defined safe state.
- Initiate an authorized recovery action.
- Suspend further intervention.
- Record an unresolved outcome for verification.

The exact runtime response and scheduling behavior are deferred to AOCL-CR-010.

## 10. Authority and Authorization Model

### 10.1 Explicit authority

A Controller SHALL have an explicit authority definition.

Authority SHALL specify:

- Authorized subject.
- Authorized action classes.
- Controlled Plant or scope.
- Permitted variables.
- Permitted value ranges.
- Operating modes in which authority applies.
- Applicable constraints.
- Delegation permissions.
- Approval requirements.
- Validity period or revocation conditions, where applicable.

Authority SHALL NOT be inferred from a `Controls`, `Influences`, `Uses` or similar relationship.

### 10.2 Authorization evaluation

An intervention SHALL be authorized only when all applicable requirements are satisfied.

These may include:

1. Controller identity and authority.
2. Target scope.
3. Action type.
4. Variable permissions.
5. Operating mode.
6. Control constraints.
7. Human approval.
8. Delegation rules.
9. Validity and revocation status.

A decision can be logically valid but unauthorized. AOCL SHALL represent that distinction.

### 10.3 Multiple Controllers

Where multiple Controllers influence the same Plant or variable, the model SHALL define:

- Authority boundaries.
- Priority or precedence.
- Coordination requirements.
- Shared-variable ownership or governance.
- Conflict detection conditions.
- Arbitration or escalation policy.
- Supervisory authority, where applicable.

No implicit priority SHALL be assumed based on component hierarchy, relationship order or model placement.

## 11. Invariants and Safe-State Model

### 11.1 StateInvariant

A `StateInvariant` defines a condition that must remain true across a defined state space or transition scope.

Examples:

- Temperature SHALL remain within a permitted safety range.
- A resource allocation SHALL NOT exceed its available capacity.
- A critical service SHALL retain minimum availability.
- A safety interlock SHALL NOT be bypassed by a lower-authority Controller.

Invariants MAY apply to:

- A variable.
- A Plant.
- A component.
- A transition.
- A control scope.
- A composite loop.

Where multiple invariants apply, their precedence and conflict semantics SHALL be explicit.

### 11.2 SafeState

A `SafeState` defines a governed condition in which the controlled system is considered to be in an acceptable risk state under specified circumstances.

A SafeState definition SHALL include:

- State identity.
- Applicable Plant or scope.
- Required variable conditions.
- Applicable operating mode.
- Entry conditions.
- Required authority.
- Permitted or prohibited actions.
- Exit conditions.
- Verification requirements.
- Recovery or escalation reference.

A SafeState is domain-dependent. AOCL SHALL not assume that stopping all activity, disabling all actuators or reverting to a previous state is universally safe.

### 11.3 Safe-state transitions

Where a safe-state transition is required, the model SHALL define:

- Triggering conditions.
- Required authority or pre-authorized protective mechanism.
- Transition path.
- Constraints that remain binding.
- Expected target state.
- Verification conditions.
- Failure disposition if the safe state cannot be established.

A model SHALL NOT claim that a safe state was achieved merely because a safe-state command was issued.

## 12. Control and Feedback Information Semantics

AOCL SHALL distinguish the following information artifacts:

| Artifact             | Meaning                                                   |
| -------------------- | --------------------------------------------------------- |
| ControlSignal        | Signal conveying a control instruction or value           |
| Command              | An actionable request to an actuator or intermediary      |
| Acknowledgement      | Confirmation that a command was received or accepted      |
| ExecutionStatus      | Report of the command's execution progress or disposition |
| FeedbackSignal       | Information returned from an actuator or control path     |
| Observation          | Information acquired about the Plant or environment       |
| StateEstimate        | Inferred representation of the Plant's state              |
| VerificationEvidence | Evidence used to evaluate a postcondition or outcome      |

These artifacts have different evidential strength.

In particular:

- Acknowledgement does not establish execution.
- Execution status does not establish Plant state.
- Feedback from an actuator does not automatically establish the resulting operational effect.
- Observation does not automatically establish an independently verified outcome.
- VerificationEvidence must identify the claim it supports and its provenance.

Detailed evidence semantics are owned by AOCL-CR-008.

## 13. Multi-Variable and Composite Control

AOCL SHALL support control contracts that govern multiple variables and transitions.

The model SHALL accommodate:

- One Controller influencing multiple variables.
- Multiple Controllers influencing different variables of one Plant.
- Multiple Actuators implementing one intervention.
- Multiple Actuators influencing a shared variable.
- Coupled variables where changing one affects another.
- Constraints spanning multiple variables.
- Composite transitions requiring several coordinated state changes.

Where variables are coupled, the model SHALL identify relevant dependencies or constraints.

A transition SHALL NOT be evaluated in isolation where doing so could violate a cross-variable invariant.

For example, reducing service latency by increasing resource allocation may be unacceptable if it breaches a resource or cost constraint.

## 14. Relationship to the Seven Behavioral Stages

The control-contract and state-transition model SHALL support the seven canonical behavioral stages without redefining them.

| Behavioral stage | CR-007 contribution                                                  |
| ---------------- | -------------------------------------------------------------------- |
| Intent           | Desired state, reference values, target ranges and constraints       |
| Observe          | Observed variables and state provenance                              |
| Analyze          | State estimation, deviation and transition eligibility               |
| Decide           | Decision contracts and authority evaluation                          |
| Execute          | Action contracts, commands and permitted interventions               |
| Verify           | Postconditions, transition results and state comparisons             |
| Learn            | Evidence-based updates to governed knowledge and control definitions |

The mapping remains many-to-many.

A ControlContract may span multiple stages. A stage may use multiple contracts. No one-to-one component-to-stage assumption is introduced.

Learning SHALL NOT automatically modify an approved contract, authority definition, invariant or safety constraint. Such changes require the applicable governance and approval process.

## 15. Relationship to OODA and MAPE-K

OODA, MAPE-K and custom decision architectures remain alternative decision architectures.

CR-007 does not replace these models.

Instead, each decision architecture SHALL be capable of referencing the same canonical control variables, contracts, state transitions and authority constraints.

For example:

- MAPE-K Monitor may acquire ObservedState.
- MAPE-K Analyze may construct EstimatedState.
- MAPE-K Plan may select an authorized StateTransition.
- MAPE-K Execute may invoke an ActionContract.
- OODA Orient may interpret observations and knowledge.
- OODA Decide may select a permitted intervention.
- OODA Act may initiate an authorized action.

The underlying control contract remains authoritative regardless of the decision architecture used.

## 16. Canonical Metamodel Components

CR-007 introduces the following principal concepts.

| Concept                 | Responsibility                                      |
| ----------------------- | --------------------------------------------------- |
| ControlVariable         | Defines a typed property relevant to control        |
| VariableRole            | Declares the variable's control or observation role |
| State                   | Represents a condition of a governed subject        |
| StateVariable           | Defines a variable participating in a state         |
| StateSpace              | Defines valid or modeled state conditions           |
| OperatingMode           | Defines a governed mode of operation                |
| StateTransition         | Represents a permitted or modeled state change      |
| TransitionGuard         | Defines conditions for a transition                 |
| TransitionOutcome       | Classifies the result of a transition               |
| ControlContract         | Governs a decision or intervention                  |
| DecisionContract        | Defines decision conditions and authority           |
| ActionContract          | Defines intervention conditions and authority       |
| StateTransitionContract | Defines transition obligations                      |
| VerificationContract    | Defines postcondition evaluation                    |
| AuthorityDefinition     | Defines permitted control authority                 |
| StateInvariant          | Defines conditions that must remain true            |
| SafeState               | Defines a governed acceptable risk state            |
| Setpoint                | Defines a target value for a control variable       |
| OperatingBound          | Defines a permitted value boundary                  |
| ControlRange            | Defines the range of permitted control              |
| RateLimit               | Defines permitted rate of change                    |

The implementation schema SHALL preserve these semantic distinctions even if some concepts are represented through shared structures or reusable types.

## 17. Illustrative Example — Network Service Assurance

### 17.1 Control context

A network service assurance loop seeks to maintain service latency within an agreed operating threshold.

| Element             | Example                       |
| ------------------- | ----------------------------- |
| Plant               | Network service               |
| ControlledVariable  | End-to-end service latency    |
| ObservedVariable    | Measured service latency      |
| EstimatedVariable   | Predicted service latency     |
| ManipulatedVariable | Traffic allocation            |
| DisturbanceVariable | External traffic demand       |
| ReferenceCondition  | Latency below 50 ms           |
| Setpoint            | 45 ms                         |
| OperatingBound      | 50 ms maximum                 |
| Controller          | Service assurance Controller  |
| Actuator            | Traffic engineering interface |

### 17.2 Example control contract

**Contract:** Traffic Redistribution Contract

**Preconditions**

- Current latency observation is valid and sufficiently fresh.
- The service is in Normal or Degraded operating mode.
- The Controller has authority over the relevant traffic allocation.
- Alternative route capacity is available.
- No active constraint prohibits redistribution.

**Authorization**

- Controller may modify traffic allocation within its declared control range.
- Changes beyond the approved range require supervisory approval.
- Safety and regulatory constraints remain binding.

**Expected effects**

- Traffic allocation changes to reduce congestion.
- The affected service transitions toward the target latency range.
- Resource constraints remain satisfied.

**Postconditions**

- The command has a recorded execution disposition.
- The resulting traffic allocation is observed or otherwise established.
- Service latency is measured after the intervention.
- The latency condition is evaluated against the reference.
- Resource and service constraints remain satisfied.

### 17.3 Illustrative state transition

| From                | Trigger                     | To         | Evaluation                         |
| ------------------- | --------------------------- | ---------- | ---------------------------------- |
| Normal              | Latency exceeds 50 ms       | Degraded   | Confirm valid observation          |
| Degraded            | Authorized redistribution   | Recovering | Confirm permitted allocation       |
| Recovering          | Latency returns below 50 ms | Normal     | Verify post-intervention latency   |
| Recovering          | Latency remains above 50 ms | Degraded   | Reassess and determine next action |
| Any applicable mode | Critical safety condition   | Safe mode  | Evaluate safe-state conditions     |

This example illustrates the distinction between a commanded transition and an established operational transition. A successful redistribution command does not prove that the service returned to Normal.

## 18. Conformance Requirements

A conforming AOCL model SHALL satisfy the applicable requirements below.

### 18.1 Control-variable conformance

**CTM-001:** Every modeled control variable SHALL have a stable identifier.

**CTM-002:** Every control variable SHALL have a semantic definition and declared data type.

**CTM-003:** Units SHALL be specified where the variable requires a unit of measurement.

**CTM-004:** Variable domains and permitted ranges SHALL be represented where applicable.

**CTM-005:** Variable roles SHALL be explicitly declared.

**CTM-006:** Incompatible units or value domains SHALL NOT be silently combined.

### 18.2 State-model conformance

**CTM-007:** Every State SHALL identify its governed subject.

**CTM-008:** State representations SHALL distinguish actual, observed, estimated, desired, commanded and verified states.

**CTM-009:** Every StateSpace SHALL define its relevant variables and domains.

**CTM-010:** Operating modes SHALL be explicitly defined where used.

**CTM-011:** State values SHALL retain their temporal context and provenance.

**CTM-012:** State estimates SHALL be distinguishable from directly acquired observations.

### 18.3 Transition conformance

**CTM-013:** Every StateTransition SHALL identify its source and target conditions.

**CTM-014:** Transition guards SHALL be explicitly represented where required.

**CTM-015:** Transition outcomes SHALL use governed classifications.

**CTM-016:** Transitions SHALL be evaluated against applicable constraints and invariants.

**CTM-017:** Disturbance-driven and externally initiated transitions SHALL be representable.

**CTM-018:** Continuous, discrete and hybrid transition models SHALL be distinguishable.

### 18.4 Contract conformance

**CTM-019:** Every modeled intervention SHALL reference an applicable ActionContract or equivalent governed contract.

**CTM-020:** Contracts SHALL identify their subject and permitted scope.

**CTM-021:** Preconditions SHALL be explicit.

**CTM-022:** Required authorization SHALL be explicit.

**CTM-023:** Applicable constraints SHALL be traceable.

**CTM-024:** Expected effects SHALL be represented.

**CTM-025:** Postconditions SHALL distinguish execution results from operational outcomes.

**CTM-026:** Relevant failure conditions and dispositions SHALL be defined.

### 18.5 Authority and safety conformance

**CTM-027:** Controller authority SHALL be explicit and scoped.

**CTM-028:** Authority SHALL NOT be inferred from structural relationships.

**CTM-029:** Shared or overlapping control scopes SHALL have explicit coordination semantics.

**CTM-030:** Applicable invariants SHALL be represented and traceable.

**CTM-031:** Safe states SHALL have explicit definitions where required.

**CTM-032:** Safe-state transitions SHALL have explicit entry and verification conditions.

**CTM-033:** Lower-authority interventions SHALL NOT override higher-priority safety or regulatory constraints.

### 18.6 Traceability and interoperability

**CTM-034:** Control variables SHALL be traceable to relevant Plant, Intent and Goal references.

**CTM-035:** Contracts SHALL be traceable to their BehavioralSpecification elements.

**CTM-036:** Transitions SHALL be traceable to their governing contracts and applicable constraints.

**CTM-037:** Verification references SHALL be supported without duplicating the evidence model owned by CR-008.

**CTM-038:** Control contracts and state models SHALL be serializable in the canonical AOCL representation.

**CTM-039:** Model and schema versions SHALL remain independently identifiable.

**CTM-040:** Incomplete or unresolved control definitions SHALL be reported explicitly rather than silently treated as conformant.

## 19. Conformance Profiles

AOCL SHALL distinguish the following profiles.

| Profile                 | Purpose                                                                                                             |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------- |
| Variable Conformance    | Validates control-variable definitions and types                                                                    |
| State Model Conformance | Validates state spaces, state distinctions and operating modes                                                      |
| Transition Conformance  | Validates transition definitions, guards and outcomes                                                               |
| Contract Conformance    | Validates preconditions, authorization, expected effects and postconditions                                         |
| Authority Conformance   | Validates explicit authority and scope boundaries                                                                   |
| Safety Conformance      | Validates invariants and safe-state definitions                                                                     |
| Simulation Readiness    | Determines whether the model contains sufficient state and transition information for a declared simulation purpose |

Passing structural conformance SHALL NOT automatically imply simulation readiness.

Simulation readiness SHALL be assessed against the requirements of the intended simulation type and fidelity.

## 20. Canonical Representation and Validation

The implementation SHALL provide:

1. A canonical machine-readable representation.
2. JSON Schema validation for structural correctness.
3. Semantic validation for references, units, ranges and relationships.
4. Contract validation for preconditions, postconditions and authority.
5. State-transition validation for source and target conditions.
6. Invariant validation for applicable state and transition constraints.
7. Version-aware import and export.
8. Round-trip serialization tests.
9. Reference examples covering discrete, continuous and hybrid models.

The representation SHALL support YAML as a human-readable serialization where consistent with the existing AOCL model conventions.

Schema validation alone SHALL NOT be treated as sufficient semantic validation.

## 21. Migration and Compatibility

Existing AOCL models and assessments SHALL be reviewed for information that can be mapped into the new control-contract and state-transition model.

Migration SHALL:

- Preserve existing loop identifiers.
- Preserve existing Plant, Controller, Sensor and Actuator references where valid.
- Preserve existing Goal, Reference and Constraint information.
- Preserve existing decision-model selections.
- Preserve existing maturity and realization records.
- Preserve existing CLAM integration references.
- Identify variables whose semantics are unclear.
- Avoid fabricating state transitions or control authority.
- Avoid interpreting actuator acknowledgements as verified state changes.
- Retain unresolved mappings as explicit migration findings.

Legacy models that lack sufficient information SHALL remain representable as incomplete or Draft models. They SHALL NOT be silently promoted to fully conformant control models.

## 22. Acceptance Criteria

This CR is accepted when:

1. The canonical control-variable model is documented.
2. Variable roles and their semantic distinctions are defined.
3. Actual, observed, estimated, desired, commanded and verified states are distinguishable.
4. StateSpace and OperatingMode are defined.
5. StateTransition and TransitionGuard semantics are established.
6. Transition outcomes are governed.
7. Discrete, continuous and hybrid transitions are representable.
8. ControlContract is established as a first-class concept.
9. DecisionContract and ActionContract responsibilities are defined.
10. Preconditions and postconditions are explicitly represented.
11. Controller authority is explicit and scoped.
12. Authorization is distinguishable from decision validity.
13. StateInvariant is defined.
14. SafeState and safe-state transition semantics are established.
15. ControlSignal, Command, Acknowledgement, ExecutionStatus and FeedbackSignal are distinguishable.
16. Multiple variables and coupled-variable constraints are supported.
17. Multiple Actuators and Controllers are supported.
18. Shared-variable conflict and coordination requirements are defined.
19. The model is traceable to Intent, Goals, behavioral elements and Plant definitions.
20. Simulation readiness is distinguishable from structural conformance.
21. A representative reference example is validated.
22. JSON Schema and semantic validation requirements are documented.
23. Migration requirements preserve existing AOCL information.
24. No runtime execution or simulation-engine implementation is introduced prematurely.

## 23. Architectural Decisions

The following decisions are proposed for formal adoption:

| Decision  | Proposed resolution                                                              |
| --------- | -------------------------------------------------------------------------------- |
| AD-007-01 | Control variables are first-class, typed model elements                          |
| AD-007-02 | Variable roles are explicit and may be contextually multiple                     |
| AD-007-03 | Actual, observed, estimated, desired, commanded and verified states are distinct |
| AD-007-04 | State spaces support discrete, continuous and hybrid representations             |
| AD-007-05 | State transitions are explicit model elements                                    |
| AD-007-06 | Preconditions and postconditions are mandatory contract concepts                 |
| AD-007-07 | Controller authority is explicit and cannot be inferred                          |
| AD-007-08 | State invariants and safe states are first-class concepts                        |
| AD-007-09 | Execution acknowledgement does not establish operational outcome                 |
| AD-007-10 | Multi-controller and coupled-variable control are supported                      |
| AD-007-11 | Control contracts are independent of runtime implementation                      |
| AD-007-12 | Simulation readiness is assessed independently of structural conformance         |

## 24. Dependencies and Next Change Requests

CR-007 establishes the control semantics required by the next modeling deliverables.

| Next CR     | Title                                                             | Relationship                                                                         |
| ----------- | ----------------------------------------------------------------- | ------------------------------------------------------------------------------------ |
| AOCL-CR-008 | Establish the Canonical Verification and Evidence Model           | Defines evidence used to establish transition results and outcome achievement        |
| AOCL-CR-009 | Establish the Canonical Simulation Scenario and Disturbance Model | Defines initial conditions, disturbances, scenario parameters and simulation context |
| AOCL-CR-010 | Establish Canonical Execution Semantics                           | Defines how behavioral specifications, contracts and transitions are executed        |
| AOCL-CR-011 | Establish the Logical Simulation Engine                           | Evaluates logical behavior and transition conditions                                 |
| AOCL-CR-012 | Establish the State-Based Simulation Engine                       | Evaluates modeled state evolution                                                    |

### Specific dependency on CR-008

CR-008 SHALL use the distinctions established here to define evidence for:

- State observations.
- State estimates.
- Command and execution outcomes.
- Transition completion.
- Postcondition evaluation.
- Goal achievement.
- Safe-state verification.

It SHALL not collapse these into a single generic success or failure record.

### Specific dependency on CR-009

CR-009 SHALL use the StateSpace, State, ControlVariable and DisturbanceVariable concepts established here to define simulation initial conditions and scenario inputs.

### Specific dependency on CR-010

CR-010 SHALL define the runtime handling of contract evaluation, authorization, transition guards, action execution, retries, interruptions and failure dispositions.

CR-007 remains the normative source for the meaning of the contracts and transitions themselves.

## 25. Recommendation

Approve AOCL-CR-007 as the canonical control-contract and state-transition foundation.

This CR closes a significant semantic gap between describing a closed-loop architecture and representing its actual control obligations.

With CR-007, AOCL can describe not only which components participate in a loop and how its behavior is structured, but also what those components are permitted to control, which transitions are valid, what outcomes are expected and how state integrity is preserved.

The next priority is AOCL-CR-008, which will establish how AOCL proves that a transition occurred and that the intended operational outcome was actually achieved.

**End of AOCL-CR-007.**

The key architectural boundary is now explicit: CR-007 defines the validity and meaning of control interventions and state transitions; CR-008 will define the evidence required to establish their results.

Next in sequence: AOCL-CR-008 — Establish the Canonical Verification and Evidence Model.