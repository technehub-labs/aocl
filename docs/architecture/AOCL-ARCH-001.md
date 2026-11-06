# AOCL-ARCH-001 — Conceptual Architecture and Normative Foundation

> Committed verbatim from the proposed baseline (v0.1, status: Proposed). Disposition and adoption record: [ADR-006](../decisions/adr-006-simulation-evidence-and-architecture-alignment.md). Review input: the comprehensive architectural review (Rev. 1) that preceded this baseline.


The immediate objective is to establish a normative foundation that can support both a rigorous engineering model and a usable software product.

The key architectural rule will be:

AOCL models the structure, intent, behavior, governance and evidence of a closed loop independently of the simulation technology used to execute it.

This prevents the model from becoming coupled to a particular canvas, simulation engine, decision framework or runtime.

# AOCL Conceptual Architecture and Normative Foundation

**Document ID:** AOCL-ARCH-001\
**Version:** 0.1\
**Status:** Proposed\
**Classification:** Architecture Foundation\
**Applies to:** AOCL domain model, assessment engine, modeling environment, simulation engine and integrations.

---

## 1. Purpose

This document establishes the conceptual and architectural foundation for the Autonomous Operations Closed Loop (AOCL) engineering framework.

It defines the concepts, principles, architectural boundaries and behavioral semantics necessary to model, assess, simulate, verify and prepare closed-loop systems for operational realization.

AOCL is positioned as a closed-loop engineering and realization framework. It is not merely a maturity assessment instrument, workflow designer or visualization tool.

Its purpose is to provide a consistent engineering foundation for specifying how an operational system should behave, how its behavior is controlled, how its outcomes are verified and how its control mechanisms can be improved.

## 2. Architectural decisions

The following decisions are normative for the proposed architecture.

| Decision                | Adopted position                                              |
| ----------------------- | ------------------------------------------------------------- |
| Framework identity      | Closed-loop engineering and realization framework             |
| Simulation approach     | Hybrid logical and state-based simulation                     |
| Behavioral lifecycle    | Seven canonical behavioral stages                             |
| Decision frameworks     | OODA, MAPE-K and extensible custom models                     |
| Modeling approach       | Model-first, schema-governed and technology-independent       |
| Visual environment      | Interactive graph-based engineering canvas                    |
| Simulation authority    | Canonical model and execution semantics                       |
| Operational integration | Interoperability with CLAM and enterprise architecture models |

### 2.1 Seven canonical behavioral stages

1. Intent
2. Observe
3. Analyze
4. Decide
5. Execute
6. Verify
7. Learn

These stages define the canonical behavioral vocabulary. They do not prescribe a rigid sequential execution algorithm.

Implementations may combine, repeat, parallelize or bypass stages where justified by their control architecture, provided the required behavioral responsibilities and conformance rules are satisfied.

## 3. AOCL conceptual definition

**Autonomous Operations Closed Loop (AOCL)** is an engineering framework for specifying, assessing, modeling, simulating and preparing closed-loop operational systems that regulate their behavior against declared intent, operate within governed constraints, verify resulting outcomes and improve through controlled feedback and learning.

A closed loop is a governed feedback system in which observations of a controlled environment inform decisions and interventions that influence subsequent states of that environment, with resulting effects evaluated against declared intent and constraints.

A closed loop is characterized by:

- A defined controlled system or operational environment.
- An explicit intent and reference condition.
- An observable operational state.
- A mechanism for interpreting observations.
- A decision mechanism operating within declared authority.
- An execution mechanism capable of influencing the controlled system.
- A feedback path that exposes the resulting state.
- A verification mechanism for evaluating achieved outcomes.
- A governed mechanism for learning and adaptation.

The existence of automation, an AI agent, a workflow or a sequence of conditional activities is not sufficient to establish a closed loop.

## 4. Conceptual architecture

AOCL is organized into three architectural layers.

### 4.1 Domain Model Layer

Defines the canonical concepts and their relationships.

Responsibilities:

- Closed-loop identity and context.
- Intent, goals and constraints.
- Controlled systems and operational state.
- Control components and interfaces.
- Behavioral stages and activities.
- Decision models and policies.
- State transitions and feedback relationships.
- Verification and evidence.
- Learning and adaptation.
- Maturity and realization attributes.

This layer is authoritative for the meaning of AOCL models.

### 4.2 Engineering Engine Layer

Provides the computational services that interpret and operate on the domain model.

Responsibilities:

- Schema validation.
- Semantic conformance validation.
- Relationship and dependency validation.
- Maturity assessment.
- Realization analysis.
- Behavioral interpretation.
- Logical simulation.
- State-based simulation.
- Scenario execution.
- Execution trace generation.
- Evidence evaluation.
- Simulation comparison and replay.

The engineering engine must operate independently of the visual interface.

### 4.3 Studio and Integration Layer

Provides the interfaces through which engineers interact with AOCL.

Responsibilities:

- Visual modeling canvas.
- Object properties and configuration.
- Behavioral graph editing.
- Simulation controls.
- Scenario management.
- Runtime visualization.
- Assessment dashboards.
- Model import and export.
- CLAM integration.
- Enterprise architecture references.

The Studio is a client of the domain model and engineering engine. It must not independently redefine their semantics.

## 5. Core conceptual model

The canonical model comprises the following conceptual aspects.

### 5.1 ClosedLoop

The primary modeled entity.

Represents a bounded operational feedback system with a declared purpose, scope, control architecture, behavioral specification and verification obligations.

Required attributes include:

- Stable identifier.
- Name.
- Definition.
- Description.
- Lifecycle status.
- Operational scope.
- Owner or accountable authority.
- Version.
- Intent reference.
- Controlled-system reference.
- Behavioral specification reference.

### 5.2 Intent

Defines the desired condition or outcome that the loop is expected to establish or maintain.

Includes:

- Goal.
- Desired state.
- Reference values.
- Performance targets.
- Constraints.
- Invariants.
- Operating boundaries.
- Priority and conflict-resolution rules.

Intent must be distinguishable from the actions used to achieve it.

### 5.3 Plant

Represents the controlled system or operational environment.

Includes:

- State variables.
- State-transition rules.
- External inputs.
- Environmental conditions.
- Disturbances.
- Observable properties.
- Controllable properties.
- Operational boundaries.

The plant is the object of control, not the controller itself.

### 5.4 Sensor and Observation

A Sensor represents a mechanism for acquiring information about the plant.

An Observation represents the resulting information.

Observations must support attributes such as:

- Observed variable.
- Value.
- Measurement unit.
- Timestamp.
- Source.
- Quality.
- Confidence.
- Freshness.
- Provenance.

Actual plant state must remain distinguishable from observed state.

### 5.5 Controller

Represents the mechanism responsible for interpreting operational information and determining appropriate control responses.

Includes:

- Decision architecture.
- Decision model.
- Policies.
- Knowledge dependencies.
- Authority boundaries.
- Decision rules.
- Control objectives.

A controller may be implemented through deterministic logic, optimization, an AI agent, a human decision-maker or a combination.

### 5.6 Actuator

Represents the mechanism through which a controller influences the plant.

Includes:

- Supported operations.
- Interface and contract.
- Input requirements.
- Preconditions.
- Authorization.
- Expected effects.
- Postconditions.
- Failure modes.

### 5.7 BehavioralSpecification

Defines the stages, activities, conditions, decisions and transitions that describe the operational behavior of a closed loop.

It must support branching, parallelism, repetition, asynchronous events, escalation and exception handling.

### 5.8 Verification

Defines how expected outcomes are evaluated against observed results.

Includes:

- Verification objectives.
- Expected conditions.
- Evaluation rules.
- Evidence requirements.
- Acceptance criteria.
- Failure and inconclusive outcomes.

### 5.9 Knowledge and Learning

Knowledge represents the information used by the controller or learning mechanism.

Learning represents a governed process for changing knowledge, models, policies or control strategies.

Learning must distinguish between:

- Runtime state updates.
- Knowledge updates.
- Model recalibration.
- Policy changes.
- Controller changes.
- Authorized changes to operating constraints.

A learning event does not automatically authorize a policy or controller modification.

## 6. Seven-stage behavioral lifecycle

### S1 — Intent

Establish what the loop must achieve.

Inputs:

- Goals.
- Reference states.
- Constraints.
- Operating policies.

Outputs:

- Declared intent.
- Reference conditions.
- Control objectives.

### S2 — Observe

Establish what is happening in the controlled environment.

Inputs:

- Sensor measurements.
- Events.
- External signals.
- Historical observations.

Outputs:

- Observation set.
- State estimates.
- Data quality indicators.

### S3 — Analyze

Interpret observations and determine the operational situation.

Inputs:

- Observations.
- Reference conditions.
- Context.
- Knowledge.

Outputs:

- Situation assessment.
- Deviation analysis.
- Diagnosed conditions.
- Risk indicators.

### S4 — Decide

Determine an appropriate response.

Inputs:

- Situation assessment.
- Policies.
- Authority boundaries.
- Constraints.
- Available actions.

Outputs:

- Decision.
- Selected action or plan.
- Authorization requirement.
- Expected effects.

### S5 — Execute

Apply the approved intervention.

Inputs:

- Decision.
- Action specification.
- Authorization.
- Execution preconditions.

Outputs:

- Execution result.
- Action record.
- Resulting plant state or state-change request.

### S6 — Verify

Determine whether the intervention achieved its intended outcome.

Inputs:

- Expected effects.
- Post-action observations.
- Acceptance criteria.

Outputs:

- Verification result.
- Outcome evidence.
- Residual deviation.
- Remediation requirement.

### S7 — Learn

Improve the loop using operational and verification evidence.

Inputs:

- Execution history.
- Verification results.
- Historical performance.
- Knowledge and model context.

Outputs:

- Learning record.
- Proposed knowledge updates.
- Model improvement recommendations.
- Authorized policy or controller changes.

### 6.1 Stage execution semantics

The seven stages are canonical behavioral responsibilities, not mandatory software modules.

An implementation may combine stages or distribute them across components.

However, each closed-loop model must identify how the responsibilities are fulfilled.

For example, an implementation that combines Observe and Analyze must still demonstrate how observations are acquired and how their operational meaning is determined.

### 6.2 Loop continuation

The lifecycle is iterative.

Verification and learning results influence subsequent observations, decisions, policies and control behavior.

A failed verification may trigger:

- Re-analysis.
- A different decision.
- A corrective action.
- Human escalation.
- Safe-state transition.
- Loop suspension.

A successful verification does not necessarily terminate the loop. The loop may continue monitoring to maintain the desired operating condition.

## 7. Structural control architecture

The behavioral lifecycle must be distinguishable from the physical or logical control architecture.

The reference architecture comprises:

1. Intent and reference specification.
2. Controlled system or plant.
3. Observation mechanisms.
4. Controller.
5. Actuation mechanisms.
6. Feedback mechanisms.
7. Verification mechanisms.
8. Knowledge and learning mechanisms.

These elements are related through typed relationships rather than implicit workflow ordering.

The architecture must support multiple sensors, controllers, actuators and verification mechanisms within a single closed loop.

It must also support nested and coordinated closed loops.

## 8. Decision architecture

AOCL supports alternative decision architectures.

### OODA

Observe, Orient, Decide, Act.

### MAPE-K

Monitor, Analyze, Plan, Execute, with shared Knowledge.

### CUSTOM

A declared decision architecture with explicit mapping to the AOCL behavioral responsibilities.

Decision architectures must be independently versioned and must not redefine the canonical meaning of AOCL stages.

## 9. Maturity and realization boundaries

AOCL preserves three maturity vectors:

- Goal Decisioning (GD).
- Data Veracity (DV).
- Feedback Intelligence (FI).

The overall maturity remains constrained by the weakest dimension, subject to the normative assessment rules.

Maturity must be distinguished from:

- Simulation performance.
- Operational effectiveness.
- Stability.
- Reliability.
- Safety.
- Realization feasibility.

The existing realization heuristic remains informative and must not be treated as an operational performance prediction or maturity score.

## 10. Simulation architecture

AOCL adopts hybrid simulation.

### 10.1 Logical simulation

Supports:

- Behavioral stage execution.
- Conditions and decisions.
- State transitions.
- Branching.
- Retries.
- Exceptions.
- Human approval.
- Execution traces.

### 10.2 State-based simulation

Supports:

- Plant state.
- Sensor observations.
- Measurement errors.
- Time delays.
- Disturbances.
- Control actions.
- Dynamic state changes.
- Thresholds.
- Outcome verification.

### 10.3 Advanced simulation extension

The architecture must permit future integration of:

- Multiple interacting loops.
- Stochastic behavior.
- Predictive control.
- Optimization.
- Dynamic digital twins.
- External simulation engines.

These capabilities are extensions, not prerequisites for the initial implementation.

### 10.4 Simulation integrity

Simulation must execute against the canonical behavioral specification.

It must not rely on canvas animation or presentation-layer logic.

Every run must identify:

- Model version.
- Scenario version.
- Simulation configuration.
- Initial state.
- Random seed where applicable.
- Execution trace.
- Outcome metrics.
- Verification results.

A simulation must be reproducible within its declared execution fidelity.

## 11. Governance and safety

Every control action must be subject to declared authority and operating constraints.

The architecture must distinguish:

- Autonomous execution.
- Human-authorized execution.
- Human-supervised execution.
- Escalation.
- Prohibited execution.

It must support preconditions, postconditions, authorization checks, safe-state behavior and auditable decisions.

Learning must not silently expand the authority of a controller.

## 12. Interoperability

AOCL maintains separation between engineering and operational management.

AOCL owns the engineering representation, assessment and simulation semantics.

CLAM remains the operational management and service-lifecycle integration boundary.

AOCL must also support references to governed enterprise entities, including capabilities, processes, systems, functions, information, resources, goals and outcomes.

External references must preserve source identity and provenance.

## 13. Normative architecture principles

- P01: Closed loops are first-class engineering entities.
- P02: Every loop is grounded in declared intent.
- P03: Actual system state is distinguishable from observed state.
- P04: Feedback relationships are explicit.
- P05: Behavioral responsibilities are identifiable and complete.
- P06: Autonomous actions are bounded by declared authority.
- P07: Outcomes are independently verifiable.
- P08: Learning and adaptation are governed.
- P09: Simulation derives from canonical model semantics.
- P10: Models are schema-governed and interoperable.
- P11: Closed loops are composable.
- P12: Simulation and evidence are reproducible.

## 14. Architectural acceptance criteria

The architecture is considered sufficiently established when:

1. A closed loop can be defined independently of any visual tool.
2. The canonical behavioral stages have unambiguous semantics.
3. Structural control components can be modeled independently.
4. Typed relationships can express the feedback architecture.
5. The model can represent alternative decision architectures.
6. The model supports branching, retries and exceptions.
7. Verification and evidence are first-class concepts.
8. Learning is distinguishable from ordinary state updates.
9. Simulation can operate against a versioned model.
10. The model can support both logical and state-based simulation.
11. Maturity, performance, realization and safety remain distinct.
12. The architecture supports CLAM and enterprise-model integration without coupling the domain model to either.

---

**End of AOCL-ARCH-001**

**Architectural disposition:** Proposed baseline for formalization through AOCL-CR-001. No implementation or existing repository baseline is superseded until the change is approved and accepted.
