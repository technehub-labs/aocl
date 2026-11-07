> **Status:** Proposed · **Queued:** 2026-11-07 — simulation scenarios and disturbances — SimulationScenario, initial conditions, disturbance profiles, event schedules, variants, reproducibility (SCN-001..057); completes the Modeling stage · Carries forward the review's pre-approval observations (kept in-document as review checks).

---

# AOCL-CR-009 — Establish the Canonical Simulation Scenario and Disturbance Model

**CR ID:** AOCL-CR-009\
**Title:** Establish the Canonical Simulation Scenario and Disturbance Model\
**Programme:** AOCL Conceptual and Modeling Foundation\
**Status:** Proposed\
**Priority:** Critical\
**Type:** Metamodel and Normative Semantics\
**Depends on:** AOCL-CR-001 through AOCL-CR-008

---

## 1. Executive Summary

This Change Request establishes the canonical simulation scenario and disturbance model for AOCL.

AOCL requires a simulation capability that can evaluate closed-loop behavior under defined operating conditions, changing system states, environmental influences, disturbances and exceptional events.

A simulation cannot be considered meaningful merely because a behavioral specification can be executed. It must establish the conditions under which that behavior is evaluated and provide a reproducible description of the environment in which the loop operates.

CR-009 introduces the canonical model for:

1. SimulationScenario.
2. ScenarioContext.
3. InitialConditions.
4. InitialState.
5. ScenarioParameter.
6. OperatingCondition.
7. EnvironmentalCondition.
8. Disturbance.
9. ScenarioEvent.
10. EventSchedule.
11. ScenarioVariant.
12. ScenarioAssumption.
13. ScenarioConstraint.
14. ExpectedObservation.
15. ScenarioVerificationTarget.
16. ScenarioCompatibility.
17. ScenarioReproducibility.

The model SHALL support deterministic and stochastic scenarios, time-based and event-driven disturbances, single-loop and multi-loop scenarios, and logical and state-based simulation.

It SHALL provide a technology-independent scenario representation that can be consumed by different simulation engines without embedding engine-specific execution semantics into the domain model.

CR-009 also establishes the relationship between scenarios and the verification model from CR-008, enabling scenario outcomes to be evaluated against explicit verification claims and criteria.

## 2. Problem Statement

A closed loop must be evaluated under conditions that reveal how it responds to both expected and unexpected changes in its operating environment.

A scenario must therefore represent more than a sequence of inputs.

It must describe:

- The operating context.
- The initial state of the controlled system.
- The initial state of relevant control components.
- The conditions under which the loop begins.
- The disturbances that may affect the Plant.
- The events that occur during simulation.
- The parameters that influence system behavior.
- The expected observations and state changes.
- The verification targets used to evaluate results.
- The assumptions and limitations of the scenario.

Without a canonical scenario model, simulation behavior risks becoming embedded in engine-specific scripts, manually configured canvas elements or undocumented test fixtures.

That would undermine AOCL's objectives of model-first engineering, interoperability and reproducibility.

### 2.1 The distinction between a scenario and a behavioral specification

A BehavioralSpecification defines how a closed loop is expected to behave.

A SimulationScenario defines the conditions under which that behavior is evaluated.

For example:

| Concern          | BehavioralSpecification                      | SimulationScenario                                             |
| ---------------- | -------------------------------------------- | -------------------------------------------------------------- |
| Desired outcome  | Defines the intended goal                    | References the goal being evaluated                            |
| Observation      | Defines how observations are used            | Defines the initial and subsequent observation conditions      |
| Decision         | Defines decision behavior                    | Defines the conditions influencing decisions                   |
| Action           | Defines permitted interventions              | Defines the circumstances requiring intervention               |
| State transition | Defines permitted transitions                | Defines initial states and events that may trigger transitions |
| Disturbance      | Defines behavioral responses to disturbances | Defines disturbance characteristics and occurrence             |
| Verification     | Defines verification behavior                | Defines the verification targets and evaluation context        |

These artifacts SHALL remain separate but explicitly related.

### 2.2 The distinction between a disturbance and an event

A disturbance represents an influence that changes, or attempts to change, the condition of a Plant or its operating environment.

An event represents an occurrence that may trigger or influence behavioral execution.

A disturbance may therefore be represented through one or more events, but not every event is a disturbance.

For example:

- A sudden increase in network traffic is a disturbance.
- A telemetry threshold-crossing notification is an event.
- An approval request is an event.
- An actuator failure is a disturbance affecting the control architecture.
- A scheduled simulation start is an event, not a Plant disturbance.

This distinction SHALL be preserved throughout the model.

## 3. Objectives

CR-009 SHALL:

1. Establish SimulationScenario as a first-class AOCL model concept.
2. Define the relationship between scenarios and closed-loop models.
3. Define initial conditions and initial state representations.
4. Establish operating and environmental conditions.
5. Define disturbances and their characteristics.
6. Define scenario events and event schedules.
7. Support time-driven and event-driven scenarios.
8. Support deterministic and stochastic scenario behavior.
9. Support scenario variants and comparative evaluation.
10. Define scenario assumptions and limitations.
11. Define expected observations and verification targets.
12. Establish scenario compatibility and validation.
13. Support single-loop and composed multi-loop simulation.
14. Establish scenario reproducibility requirements.
15. Preserve separation between scenario definition and simulation execution.

## 4. Scope

### 4.1 In scope

- SimulationScenario.
- ScenarioContext.
- ScenarioIdentity.
- ScenarioParameter.
- InitialConditions.
- InitialState.
- OperatingCondition.
- EnvironmentalCondition.
- Disturbance.
- DisturbanceProfile.
- ScenarioEvent.
- EventSchedule.
- ScenarioTrigger.
- ScenarioVariant.
- ScenarioAssumption.
- ScenarioConstraint.
- ExpectedObservation.
- ScenarioVerificationTarget.
- ScenarioCompatibility.
- ScenarioReproducibility.
- Scenario applicability and validation.
- Scenario composition and dependencies.
- Scenario versioning and provenance.

### 4.2 Out of scope

| Concern                                    | Owning CR   |
| ------------------------------------------ | ----------- |
| Closed-loop identity, intent and goals     | AOCL-CR-002 |
| Behavioral lifecycle and graph             | AOCL-CR-003 |
| Control architecture                       | AOCL-CR-004 |
| Relationships and composition              | AOCL-CR-005 |
| Behavioral specification schema            | AOCL-CR-006 |
| Control contracts and state transitions    | AOCL-CR-007 |
| Verification and evidence model            | AOCL-CR-008 |
| Execution scheduling and runtime semantics | AOCL-CR-010 |
| Logical simulation engine                  | AOCL-CR-011 |
| State-based simulation engine              | AOCL-CR-012 |
| Simulation trace and replay                | AOCL-CR-013 |
| Visual scenario management                 | AOCL-CR-016 |

CR-009 does not define numerical integration methods, simulation solvers, execution scheduling algorithms, runtime event queues or engine-specific APIs.

## 5. Normative Design Principles

### P01 — Scenario Grounding

Every scenario SHALL reference the model elements and context it intends to evaluate.

### P02 — Initial-State Explicitness

The initial state of relevant Plants and components SHALL be explicitly defined or derived through a declared initialization method.

### P03 — Environmental Separation

The Plant, its operating environment and disturbances affecting it SHALL remain distinguishable.

### P04 — Disturbance Explicitness

Disturbances SHALL be represented as identifiable model elements with defined characteristics and applicable effects.

### P05 — Temporal and Event Flexibility

Scenarios SHALL support time-based, event-based, condition-based and combined triggering.

### P06 — Reproducibility

A scenario SHALL preserve the configuration and parameters necessary to reproduce its intended conditions.

### P07 — Controlled Variability

Stochastic behavior and parameter variation SHALL be explicit and governed.

### P08 — Scenario Independence

A scenario SHALL remain independent of a particular simulation engine wherever possible.

### P09 — Verification Grounding

Scenario evaluation SHALL reference explicit verification targets and criteria.

### P10 — Composability

Scenarios SHALL support composed loops, shared Plants, coordinated controllers and interdependent disturbances.

### P11 — Assumption Transparency

Scenario assumptions, simplifications and limitations SHALL be explicit.

### P12 — Simulation Fidelity

The scenario SHALL describe conditions that affect modeled behavior, not merely visual changes to the modeling canvas.

## 6. Canonical SimulationScenario Model

### 6.1 SimulationScenario

A `SimulationScenario` represents a governed and versioned specification of operating conditions, initial states, events, disturbances and evaluation targets for examining the behavior of one or more closed loops.

A SimulationScenario SHALL reference the model baseline it is intended to evaluate.

Proposed attributes:

| Attribute                   | Description                            |
| --------------------------- | -------------------------------------- |
| scenarioId                  | Stable identifier                      |
| scenarioType                | Governed scenario classification       |
| name                        | Human-readable scenario name           |
| definition                  | Purpose and intended evaluation        |
| description                 | Scenario detail                        |
| version                     | Scenario version                       |
| lifecycleStatus             | Scenario lifecycle state               |
| contextRef                  | Scenario context                       |
| modelRefs                   | Closed-loop model references           |
| modelVersionRefs            | Exact model versions being evaluated   |
| behavioralSpecificationRefs | Relevant behavioral specifications     |
| controlArchitectureRefs     | Relevant control architecture versions |
| initialConditionsRef        | Initial condition definition           |
| parameterRefs               | Scenario parameter definitions         |
| operatingConditionRefs      | Operating conditions                   |
| disturbanceRefs             | Disturbance definitions                |
| eventScheduleRefs           | Scenario event definitions             |
| variantRefs                 | Related scenario variants              |
| assumptionRefs              | Declared assumptions                   |
| constraintRefs              | Applicable scenario constraints        |
| verificationTargetRefs      | Expected verification targets          |
| reproducibilityRef          | Reproducibility configuration          |
| provenanceRef               | Scenario provenance                    |

The scenario SHALL be independently identifiable and versioned.

### 6.2 Scenario identity and lifecycle

Scenario identity SHALL be independent of its display name.

Scenario versions SHALL distinguish changes to:

- Initial conditions.
- Disturbance profiles.
- Event schedules.
- Scenario parameters.
- Operating conditions.
- Assumptions.
- Verification targets.
- Model compatibility.

Proposed lifecycle:

- Draft.
- InReview.
- Approved.
- Deprecated.
- Retired.

Scenario lifecycle SHALL remain distinct from simulation-run status.

An approved scenario does not imply that it has been executed or that its expected outcomes have been achieved.

## 7. ScenarioContext

A `ScenarioContext` defines the context within which a scenario is intended to be evaluated.

It MAY reference:

- Operational domain.
- Operating environment.
- Controlled system.
- Plant.
- Organizational or service context.
- Relevant enterprise entities.
- Applicable operating mode.
- Geographic or physical context, where relevant.
- Relevant time context.
- External dependencies.

ScenarioContext SHALL reference governed entities where available rather than duplicate their definitions.

It SHALL establish sufficient context to interpret the scenario's initial conditions, disturbances and verification targets.

A scenario MAY cover multiple operating contexts when their relationships and applicability are explicit.

## 8. Initial Conditions and Initial State

### 8.1 InitialConditions

`InitialConditions` defines the conditions that must hold at the beginning of a simulation scenario.

It SHALL identify the initialization method and the initial state of relevant model elements.

Initial conditions MAY include:

- Plant state.
- Controlled variable values.
- Observed variable values.
- Estimated state.
- Controller state.
- Actuator state.
- Knowledge state.
- Operating mode.
- Resource availability.
- Environmental conditions.
- Active constraints.
- Pending events.
- Initial disturbance conditions.

InitialConditions SHALL reference the relevant model elements and state definitions established by CR-007.

### 8.2 InitialState

An `InitialState` defines the starting value or condition of a state variable or modeled entity.

Proposed attributes:

| Attribute            | Description                               |
| -------------------- | ----------------------------------------- |
| initialStateId       | Stable identifier                         |
| subjectRef           | Plant, component or state variable        |
| stateVariableRef     | State variable being initialized          |
| value                | Initial value or state                    |
| valueType            | Data type or state representation         |
| unit                 | Applicable unit                           |
| validityContext      | Context in which the value applies        |
| initializationMethod | How the value is established              |
| provenanceRef        | Source or derivation                      |
| uncertainty          | Uncertainty information, where applicable |

InitialState SHALL distinguish actual Plant state from observed or estimated state.

For example, a scenario may initialize the Plant at 72 ms latency while the Controller receives an older observation indicating 48 ms.

This distinction is essential for evaluating delayed or inaccurate telemetry.

### 8.3 Initialization methods

AOCL SHALL support the following initialization methods:

| Method     | Description                                                |
| ---------- | ---------------------------------------------------------- |
| Explicit   | Initial value supplied directly                            |
| Derived    | Initial value calculated from other defined conditions     |
| Referenced | Initial value obtained from an external model or dataset   |
| Sampled    | Initial value selected from a declared distribution        |
| Inherited  | Initial value inherited from a parent or composed scenario |
| Defaulted  | Initial value supplied by an explicitly governed default   |

A default SHALL NOT silently replace a missing mandatory initial condition.

Where initialization is incomplete, scenario validation SHALL identify the missing information.

### 8.4 Initial-state consistency

Initial conditions SHALL be evaluated for consistency against:

- State-variable definitions.
- Type and unit requirements.
- State-space boundaries.
- Control constraints.
- Plant invariants.
- Operating modes.
- Component dependencies.
- Scenario assumptions.

An inconsistent initial state SHALL prevent the scenario from being considered valid for execution under the relevant validation profile.

## 9. Scenario Parameters

A `ScenarioParameter` defines a configurable value that influences scenario conditions or modeled behavior.

Parameters MAY represent:

- Traffic volume.
- Network capacity.
- Service latency.
- Resource availability.
- Sensor sampling interval.
- Observation delay.
- Actuator response time.
- Failure probability.
- Recovery duration.
- Environmental conditions.
- Policy thresholds.
- Control limits.

Proposed attributes:

| Attribute       | Description                                           |
| --------------- | ----------------------------------------------------- |
| parameterId     | Stable identifier                                     |
| name            | Parameter name                                        |
| definition      | Parameter meaning                                     |
| valueType       | Numeric, Boolean, categorical, temporal or structured |
| defaultValue    | Optional declared default                             |
| allowedRange    | Permitted value or range                              |
| unit            | Applicable unit                                       |
| variationMode   | Fixed, ranged, sampled or externally supplied         |
| distributionRef | Distribution definition, where applicable             |
| sensitivityRole | Whether parameter is used in sensitivity evaluation   |
| provenanceRef   | Source or derivation                                  |

Parameter definitions SHALL distinguish a parameter's type and unit from the values assigned in a particular scenario.

Parameters SHALL be typed and validated against the model elements that consume them.

A scenario parameter SHALL NOT silently override a normative control constraint or authority boundary.

## 10. Operating Conditions

An `OperatingCondition` represents a condition under which the closed loop or Plant is expected to operate.

Examples include:

- Normal operating load.
- Peak traffic.
- Reduced capacity.
- Maintenance mode.
- Degraded operation.
- Recovery mode.
- Emergency operating mode.
- Restricted resource availability.

Operating conditions MAY be:

- Static.
- Time-dependent.
- Event-triggered.
- Condition-triggered.
- Derived from other state variables.

An OperatingCondition SHALL identify its applicable scope and the conditions that establish its validity.

### 10.1 Operating modes

A scenario MAY define multiple operating modes and transitions between them.

Operating modes SHALL reference the state model established by CR-007.

They SHALL NOT introduce conflicting or duplicate definitions of Plant states.

### 10.2 EnvironmentalCondition

An `EnvironmentalCondition` represents a condition external to the controlled Plant that may influence its behavior.

Examples include:

- Ambient temperature.
- Weather.
- External network congestion.
- Power availability.
- External service availability.
- Regulatory or operational restrictions.
- External demand patterns.

Environmental conditions SHALL be distinguished from internal Plant state.

An environmental condition MAY influence a disturbance profile or the Plant's state-transition behavior.

## 11. Disturbance Model

### 11.1 Disturbance

A `Disturbance` represents an influence that changes, or attempts to change, the state or operating conditions of a Plant or relevant component.

A disturbance may be:

- Internal or external.
- Known or unknown.
- Transient or persistent.
- Gradual or sudden.
- Deterministic or stochastic.
- Continuous or discrete.
- Single or compound.

Proposed attributes:

| Attribute          | Description                              |
| ------------------ | ---------------------------------------- |
| disturbanceId      | Stable identifier                        |
| disturbanceType    | Governed disturbance classification      |
| name               | Human-readable name                      |
| definition         | Nature of the disturbance                |
| description        | Detailed characteristics                 |
| targetRefs         | Affected Plants, variables or components |
| sourceRef          | Origin, where known                      |
| magnitude          | Magnitude or severity                    |
| magnitudeUnit      | Unit of measurement                      |
| direction          | Direction of influence, where applicable |
| onsetCondition     | Condition initiating the disturbance     |
| duration           | Expected duration or persistence         |
| temporalProfileRef | Disturbance evolution                    |
| effectRef          | Declared effect on the model             |
| uncertainty        | Uncertainty or variability               |
| provenanceRef      | Source or derivation                     |

A disturbance SHALL reference its affected model elements.

A disturbance SHALL NOT be represented merely as a label or annotation on the simulation canvas.

### 11.2 Disturbance classification

AOCL SHOULD support the following classifications:

| Category         | Description                                      | Example                      |
| ---------------- | ------------------------------------------------ | ---------------------------- |
| Demand           | Changes in workload or demand                    | Sudden traffic increase      |
| Capacity         | Changes in available capacity                    | Reduced network bandwidth    |
| Resource         | Changes in resource availability                 | Compute resource exhaustion  |
| Environmental    | External environmental influence                 | Power instability            |
| ComponentFailure | Failure of a modeled component                   | Sensor or actuator failure   |
| DataQuality      | Degradation of observation quality               | Stale or corrupted telemetry |
| Timing           | Changes in timing behavior                       | Increased observation delay  |
| Security         | Security-related influence                       | Unauthorized control attempt |
| Dependency       | Failure or degradation of an external dependency | External service outage      |
| Policy           | Change in governing policy or restriction        | New operating restriction    |
| Coordination     | Conflict or interference between loops           | Competing control actions    |

The classification SHALL remain extensible through governed extensions.

### 11.3 Disturbance profiles

A `DisturbanceProfile` defines how a disturbance changes over time or in response to conditions.

It MAY represent:

- Step changes.
- Ramps.
- Pulses.
- Periodic variation.
- Gradual degradation.
- Sudden failure.
- Intermittent failure.
- Recovery.
- Compound disturbances.
- Random variation.
- Condition-dependent variation.

The profile SHALL specify its applicable variable, unit, temporal characteristics and boundary conditions.

### 11.4 Disturbance effects

A disturbance SHALL identify the effect it is intended to have on the modeled environment.

Effects MAY include:

- Changing a Plant state variable.
- Altering an environmental condition.
- Reducing resource availability.
- Delaying an observation.
- Increasing measurement error.
- Preventing actuator execution.
- Triggering a component failure state.
- Introducing competing control influences.

The effect definition SHALL reference CR-007 state variables and transitions.

CR-009 SHALL describe the disturbance and its modeled effect without defining the numerical execution algorithm used by a simulation engine.

### 11.5 Unknown disturbances

AOCL SHALL support scenarios in which a disturbance is not known to the Controller before it occurs.

This is important for testing whether the loop can detect and respond to unanticipated conditions.

The scenario may define the disturbance for simulation purposes while withholding its identity or parameters from the simulated Controller.

The simulation model SHALL distinguish:

- Information available to the scenario.
- Information available to the Plant.
- Information available to Sensors.
- Information available to the Controller.
- Information available to the verification mechanism.

A Controller SHALL NOT automatically receive complete scenario configuration information.

This prevents the simulation from unintentionally giving the Controller knowledge unavailable in the intended operating environment.

## 12. Scenario Events and Event Schedules

### 12.1 ScenarioEvent

A `ScenarioEvent` represents an identifiable occurrence within a scenario that may affect the Plant, environment or behavioral execution.

Examples include:

- Scenario start.
- Disturbance onset.
- Threshold crossing.
- Observation received.
- Approval requested.
- Approval granted.
- Actuator failure.
- Recovery condition reached.
- Timeout.
- External dependency restored.
- Verification completed.

Proposed attributes:

| Attribute         | Description                   |
| ----------------- | ----------------------------- |
| eventId           | Stable identifier             |
| eventType         | Governed event classification |
| name              | Event name                    |
| definition        | Event meaning                 |
| triggerRef        | Trigger condition             |
| subjectRef        | Affected entity               |
| temporalReference | Scheduled or relative time    |
| payload           | Typed event information       |
| effectRefs        | Relevant effects              |
| provenanceRef     | Event origin                  |
| correlationRef    | Related event or event group  |

An event SHALL identify its triggering condition or scheduling basis.

### 12.2 EventSchedule

An `EventSchedule` defines when or under what conditions scenario events are expected to occur.

AOCL SHALL support:

- Absolute-time schedules.
- Relative-time schedules.
- Periodic schedules.
- Event-triggered schedules.
- Condition-triggered schedules.
- Randomized schedules.
- Compound schedules.

For example:

- At simulation time 60 seconds, increase traffic demand.
- When latency exceeds 70 ms, introduce a congestion event.
- After actuator execution, delay the next observation by 10 seconds.
- If resource utilization exceeds 90%, trigger a capacity restriction.

The schedule SHALL preserve its time basis and triggering semantics.

### 12.3 Event ordering and concurrency

Scenarios MAY contain simultaneous or concurrent events.

Where event ordering affects behavior, the scenario SHALL define the applicable ordering or coordination requirement.

Where multiple events occur at the same simulation time, the scenario SHALL identify whether they are:

- Independent.
- Ordered.
- Concurrent.
- Mutually exclusive.
- Conditional.
- Coordinated.

The resolution of event execution order belongs to CR-010.

### 12.4 Event dependency

Events MAY depend on:

- Other events.
- State transitions.
- Threshold crossings.
- Time conditions.
- External responses.
- Verification results.
- Human approvals.

Event dependencies SHALL be explicit and validated for unresolved references and invalid dependency cycles.

## 13. Scenario Variants and Comparative Evaluation

### 13.1 ScenarioVariant

A `ScenarioVariant` represents a controlled variation of a base scenario.

Variants allow AOCL to compare loop behavior under different operating conditions without duplicating the entire scenario definition.

A variant MAY modify:

- Initial conditions.
- Scenario parameters.
- Operating conditions.
- Disturbance magnitude.
- Disturbance timing.
- Event schedules.
- Environmental conditions.
- Selected assumptions.
- Verification thresholds, where permitted by the governing model.

A variant SHALL identify its base scenario and the exact differences it introduces.

### 13.2 Variant types

AOCL SHOULD support:

| Variant     | Purpose                                                         |
| ----------- | --------------------------------------------------------------- |
| Baseline    | Reference operating conditions                                  |
| Normal      | Expected operating conditions                                   |
| Stress      | Elevated demand or constrained resources                        |
| Degraded    | Reduced component or system performance                         |
| Failure     | One or more component or dependency failures                    |
| Recovery    | Evaluation of recovery behavior                                 |
| Boundary    | Evaluation near operating or safety limits                      |
| Adversarial | Evaluation under hostile or intentionally disruptive conditions |
| Sensitivity | Evaluation under controlled parameter variation                 |
| Comparative | Comparison of alternative policies or control configurations    |

These are scenario classifications, not mandatory execution modes.

### 13.3 Scenario comparison

AOCL SHALL support comparison of scenarios that share a compatible model baseline.

Comparison SHOULD evaluate:

- Goal achievement.
- Response time.
- State-transition behavior.
- Constraint violations.
- Stability.
- Recovery behavior.
- Resource consumption.
- Verification outcomes.
- Evidence quality.
- Uncertainty.

Scenario comparison SHALL distinguish changes attributable to scenario inputs from changes attributable to the model or controller configuration.

A comparison between incompatible model versions SHALL require an explicit compatibility assessment.

## 14. Scenario Assumptions and Constraints

### 14.1 ScenarioAssumption

A `ScenarioAssumption` records an assumption made about the operating environment, Plant, data, disturbance or model.

Examples include:

- Network topology remains unchanged during the scenario.
- The external service responds within a declared interval.
- Sensor measurement error follows a defined distribution.
- Resource capacity remains constant except where explicitly disturbed.
- A particular dependency is available at scenario initialization.

Assumptions SHALL identify:

- Assumption identity.
- Description.
- Applicable scope.
- Basis or rationale.
- Validation status.
- Known limitations.
- Provenance, where available.

Assumptions SHALL be visible in scenario results and reproducibility records.

### 14.2 ScenarioConstraint

A `ScenarioConstraint` defines a condition that applies to the scenario itself.

Examples include:

- Maximum simulation duration.
- Permitted parameter ranges.
- Required initial conditions.
- Maximum disturbance magnitude.
- Mandatory verification targets.
- Required scenario coverage.
- Prohibited scenario configurations.

ScenarioConstraint SHALL remain distinct from operational ControlConstraints.

A scenario may be designed to test a control constraint boundary, but it SHALL NOT override that constraint in the underlying model.

### 14.3 Assumption and constraint handling

A scenario SHALL be invalidated or marked incomplete where a mandatory assumption or constraint cannot be established.

A scenario MAY be approved with declared limitations where those limitations do not invalidate its intended evaluation purpose.

The validation result SHALL preserve the applicable rationale.

## 15. Expected Observations and Verification Targets

### 15.1 ExpectedObservation

An `ExpectedObservation` defines an observation or measurement that is expected to occur under a scenario condition.

Examples include:

- Latency rises above a threshold after a demand disturbance.
- A Sensor reports a delayed measurement.
- A Controller receives an incomplete observation.
- A recovery event is detected.
- A component failure is observed.

ExpectedObservation SHALL reference the relevant Sensor, Observation type, variable or event where applicable.

It SHALL distinguish:

- Expected Plant condition.
- Expected Sensor output.
- Expected Controller-visible information.
- Expected verification evidence.

This is essential because the actual Plant state may differ from what the Controller observes.

### 15.2 ScenarioVerificationTarget

A `ScenarioVerificationTarget` defines a claim or outcome that the scenario is intended to evaluate.

It SHALL reference the verification model from CR-008.

Possible targets include:

- Goal achievement.
- Control contract compliance.
- State-transition validity.
- Constraint preservation.
- Disturbance detection.
- Recovery behavior.
- Response time.
- Stability.
- Reliability.
- Safety behavior.
- Exception handling.
- Learning behavior.

Each target SHALL identify:

- Verification claim.
- Applicable criterion.
- Scenario conditions.
- Required evidence.
- Applicable evaluation interval.
- Required assurance level, where applicable.

A scenario may have multiple verification targets.

A scenario that executes successfully but does not evaluate its declared targets SHALL not be considered complete for the intended verification purpose.

### 15.3 Expected behavior versus expected outcome

AOCL SHALL distinguish:

- Expected behavior: what the behavioral specification says the loop should do.
- Expected state: what the Plant or component should become.
- Expected outcome: what the loop is intended to achieve.
- Verification target: what must be established to determine whether the expected result occurred.

A scenario SHALL NOT assume that the intended outcome will necessarily be achieved.

Failure to achieve an expected outcome is a valid and important simulation result.

## 16. Scenario Composition and Multi-Loop Evaluation

### 16.1 Composed scenarios

A SimulationScenario MAY evaluate:

- A single ClosedLoop.
- Multiple coordinated ClosedLoops.
- Hierarchical loops.
- Cooperative loops.
- Dependent loops.
- Loops sharing a Plant.
- Loops operating across interconnected Plants.

Composition SHALL reuse the relationships and composition semantics established by CR-005.

### 16.2 Shared operating environments

Where multiple loops share a Plant or operating environment, the scenario SHALL identify:

- Shared state variables.
- Shared resources.
- Shared constraints.
- Inter-loop dependencies.
- Competing interventions.
- Coordination requirements.
- Relevant authority boundaries.

### 16.3 Competing and conflicting disturbances

A scenario MAY introduce multiple simultaneous disturbances.

It SHALL support cases in which:

- Disturbances affect the same state variable.
- Disturbances affect different but coupled variables.
- One disturbance changes the effect of another.
- A disturbance affects multiple Plants.
- Multiple loops respond to the same disturbance.
- Loop interventions create secondary effects on other loops.

### 16.4 Cross-loop evaluation

A scenario MAY evaluate:

- Coordination effectiveness.
- Resource contention.
- Control conflicts.
- Cascading effects.
- Dependency failures.
- Propagation of disturbances.
- Recovery coordination.

A composed scenario SHALL preserve the identity and version of each constituent loop and relevant model artifact.

## 17. Scenario Reproducibility

### 17.1 Reproducibility model

A `ScenarioReproducibility` definition identifies the information necessary to reproduce the intended scenario conditions.

It SHALL include or reference:

- Scenario ID and version.
- Model IDs and versions.
- Behavioral specification versions.
- Control architecture versions.
- Control contract versions.
- Initial conditions.
- Scenario parameters.
- Disturbance definitions and profiles.
- Event schedules.
- Assumptions.
- Scenario variants.
- Random seed, where applicable.
- External dataset references.
- Relevant model dependencies.

Simulation engine and engine version SHALL be recorded by the simulation execution model in CR-010 and subsequent engine CRs.

### 17.2 Deterministic scenarios

A deterministic scenario SHALL produce the same scenario inputs and event conditions when initialized with the same configuration.

This does not imply that every simulation engine must produce identical numerical outputs under all execution conditions. Numerical and engine-level reproducibility requirements belong to the relevant execution and engine specifications.

### 17.3 Stochastic scenarios

A stochastic scenario SHALL declare:

- The variable or event subject to randomness.
- The distribution or sampling method.
- Applicable parameters.
- Random seed or seed policy.
- Sampling scope.
- Relevant assumptions.

Where multiple stochastic processes are present, the scenario SHALL identify their separate definitions and dependencies.

### 17.4 External data dependencies

Where a scenario references external datasets, it SHALL preserve:

- Dataset identity.
- Dataset version or snapshot.
- Source.
- Retrieval or acquisition time.
- Relevant transformations.
- Access or integrity references, where applicable.

A moving external dataset reference SHALL NOT be treated as sufficient for reproducibility.

### 17.5 Reproducibility limitations

Where exact reproduction is not possible, AOCL SHALL preserve the reason.

Examples include:

- Unavailable external datasets.
- Non-deterministic external services.
- Uncontrolled environmental inputs.
- Unavailable model versions.
- Unrecorded randomization parameters.

A reproducibility limitation SHALL be reported rather than concealed.

## 18. Scenario Validation and Compatibility

### 18.1 Scenario validation

AOCL SHALL validate scenarios before they are accepted for simulation.

Validation SHALL include:

- Scenario identity and version.
- Model references.
- Model version compatibility.
- Initial-state completeness.
- Initial-state consistency.
- Parameter typing and ranges.
- Disturbance target validity.
- Disturbance profile validity.
- Event dependency validity.
- Scenario assumption completeness.
- Scenario constraint compliance.
- Verification target validity.
- Reproducibility information.
- Multi-loop composition consistency.

### 18.2 ScenarioCompatibility

A `ScenarioCompatibility` assessment determines whether a scenario is applicable to a particular model baseline and its constituent artifacts.

Compatibility SHALL consider:

- ClosedLoop identity and version.
- BehavioralSpecification version.
- ControlArchitecture version.
- ControlContract version.
- State-variable definitions.
- Relationship and composition versions.
- Referenced constraints.
- Verification definitions.
- Required model extensions.

A scenario SHALL NOT be silently executed against a materially different model version.

### 18.3 Compatibility outcomes

AOCL SHOULD support:

| Outcome                | Meaning                                                                     |
| ---------------------- | --------------------------------------------------------------------------- |
| Compatible             | Scenario applies to the specified model baseline                            |
| CompatibleWithWarnings | Applicable with declared limitations                                        |
| Incompatible           | Scenario cannot validly apply to the model baseline                         |
| RequiresMigration      | Scenario references an older model structure requiring controlled migration |
| Unresolved             | Compatibility cannot yet be established                                     |

### 18.4 Validation profiles

AOCL SHOULD distinguish:

| Profile                    | Purpose                                                                                |
| -------------------------- | -------------------------------------------------------------------------------------- |
| Structural Validation      | Checks scenario structure and references                                               |
| Initial-State Validation   | Checks initial condition completeness and consistency                                  |
| Parameter Validation       | Checks parameter types, values and ranges                                              |
| Disturbance Validation     | Checks disturbance definitions and effects                                             |
| Event Validation           | Checks event triggers and dependencies                                                 |
| Verification Readiness     | Checks verification target definitions                                                 |
| Composition Validation     | Checks multi-loop scenario consistency                                                 |
| Reproducibility Validation | Checks scenario reproducibility information                                            |
| Simulation Readiness       | Determines whether the scenario is sufficiently defined for a declared simulation mode |

Passing Structural Validation SHALL NOT automatically imply Simulation Readiness.

## 19. Canonical Metamodel Components

CR-009 introduces the following principal concepts.

| Concept                    | Responsibility                                        |
| -------------------------- | ----------------------------------------------------- |
| SimulationScenario         | Governed specification of simulation conditions       |
| ScenarioContext            | Context within which the scenario applies             |
| InitialConditions          | Definition of scenario initialization                 |
| InitialState               | Initial state of a modeled subject or variable        |
| ScenarioParameter          | Configurable scenario input                           |
| OperatingCondition         | Condition governing Plant operation                   |
| EnvironmentalCondition     | External environmental condition                      |
| Disturbance                | Influence on Plant or operating conditions            |
| DisturbanceProfile         | Temporal or conditional disturbance behavior          |
| ScenarioEvent              | Identifiable scenario occurrence                      |
| EventSchedule              | Timing and triggering definition                      |
| ScenarioTrigger            | Condition that initiates an event or disturbance      |
| ScenarioVariant            | Controlled variation of a base scenario               |
| ScenarioAssumption         | Explicit scenario assumption                          |
| ScenarioConstraint         | Constraint on scenario configuration                  |
| ExpectedObservation        | Expected observation or measurement                   |
| ScenarioVerificationTarget | Verification claim or outcome evaluated by a scenario |
| ScenarioCompatibility      | Applicability of scenario to a model baseline         |
| ScenarioReproducibility    | Information required to reproduce scenario conditions |

These concepts SHALL be independently identifiable where they represent separately governed artifacts.

The implementation MAY use shared structural types where appropriate, provided semantic distinctions are preserved.

## 20. Conformance Requirements

### 20.1 Scenario identity and context

**SCN-001:** Every SimulationScenario SHALL have a stable identifier.

**SCN-002:** Every SimulationScenario SHALL have a declared version.

**SCN-003:** Every SimulationScenario SHALL identify its intended ClosedLoop model or composed model scope.

**SCN-004:** Every SimulationScenario SHALL reference the exact model versions it is intended to evaluate.

**SCN-005:** Every SimulationScenario SHALL identify its applicable context.

**SCN-006:** Scenario lifecycle SHALL be distinct from simulation-run status.

### 20.2 Initial conditions and parameters

**SCN-007:** Every executable scenario SHALL define or reference its required InitialConditions.

**SCN-008:** InitialState SHALL reference a valid model subject or state variable.

**SCN-009:** InitialState SHALL preserve applicable type and unit information.

**SCN-010:** Initial conditions SHALL be validated against applicable state spaces and constraints.

**SCN-011:** Actual Plant state SHALL remain distinguishable from observed and estimated state.

**SCN-012:** Initialization methods SHALL be explicit.

**SCN-013:** Mandatory missing initial values SHALL not be silently replaced by defaults.

**SCN-014:** Scenario parameters SHALL have declared types.

**SCN-015:** Parameter values SHALL be validated against applicable ranges and constraints.

### 20.3 Operating and environmental conditions

**SCN-016:** Operating conditions SHALL identify their applicable scope.

**SCN-017:** Operating modes SHALL reference the canonical state model.

**SCN-018:** Environmental conditions SHALL remain distinguishable from Plant state.

**SCN-019:** Time-dependent operating conditions SHALL declare their temporal basis.

### 20.4 Disturbance conformance

**SCN-020:** Every Disturbance SHALL have a stable identifier.

**SCN-021:** Every Disturbance SHALL identify its affected subject or scope.

**SCN-022:** Disturbance classification SHALL use governed types.

**SCN-023:** Disturbance magnitude and units SHALL be represented where applicable.

**SCN-024:** Disturbance onset and duration SHALL be defined or explicitly declared as unknown.

**SCN-025:** Time-dependent disturbances SHALL reference a valid DisturbanceProfile.

**SCN-026:** Disturbance effects SHALL reference applicable state variables or modeled effects.

**SCN-027:** Unknown disturbances SHALL be supported without automatically exposing their full definition to the Controller.

**SCN-028:** Multiple and compound disturbances SHALL be representable.

### 20.5 Event conformance

**SCN-029:** Every ScenarioEvent SHALL have an identifiable event type.

**SCN-030:** Every ScenarioEvent SHALL identify its trigger or scheduling basis.

**SCN-031:** Event schedules SHALL declare their time basis.

**SCN-032:** Event dependencies SHALL reference valid events or conditions.

**SCN-033:** Concurrent and ordered events SHALL be distinguishable.

**SCN-034:** Invalid or unresolved event dependencies SHALL be reported.

### 20.6 Variants and assumptions

**SCN-035:** Every ScenarioVariant SHALL identify its base scenario.

**SCN-036:** Variant differences SHALL be explicit.

**SCN-037:** Scenario assumptions SHALL be recorded.

**SCN-038:** Scenario constraints SHALL remain distinct from operational ControlConstraints.

**SCN-039:** Scenario limitations SHALL be preserved in validation and result references.

### 20.7 Verification targets

**SCN-040:** Scenarios intended for verification SHALL define or reference verification targets.

**SCN-041:** Verification targets SHALL reference valid claims and criteria from CR-008.

**SCN-042:** Expected observations SHALL distinguish Plant state from Controller-visible information.

**SCN-043:** Scenario completion SHALL not imply successful achievement of its verification targets.

**SCN-044:** Failed and inconclusive verification outcomes SHALL remain valid scenario results.

### 20.8 Composition and reproducibility

**SCN-045:** Composed scenarios SHALL preserve constituent loop identities and versions.

**SCN-046:** Shared Plant and shared resource conditions SHALL be explicit.

**SCN-047:** Inter-loop dependencies and competing disturbances SHALL be representable.

**SCN-048:** Reproducibility information SHALL identify the scenario configuration and model versions.

**SCN-049:** Stochastic scenarios SHALL declare their randomization basis.

**SCN-050:** External data dependencies SHALL identify stable versions or snapshots where available.

**SCN-051:** Reproducibility limitations SHALL be explicitly recorded.

### 20.9 Compatibility and simulation readiness

**SCN-052:** Scenario compatibility SHALL be evaluated against the target model baseline.

**SCN-053:** Material model-version incompatibilities SHALL prevent silent scenario execution.

**SCN-054:** Structural validation SHALL be distinct from simulation readiness.

**SCN-055:** Simulation readiness SHALL be evaluated against the intended simulation mode.

**SCN-056:** Scenario serialization SHALL preserve semantic relationships and references.

**SCN-057:** Scenario import and export SHALL support version-aware validation.

## 21. Conformance Profiles

AOCL SHALL support the following scenario conformance profiles:

| Profile                          | Purpose                                               |
| -------------------------------- | ----------------------------------------------------- |
| Scenario Structural Conformance  | Validates scenario identity, structure and references |
| Initial-State Conformance        | Validates initialization and state consistency        |
| Parameter Conformance            | Validates parameter definitions and values            |
| Disturbance Conformance          | Validates disturbance semantics and profiles          |
| Event Conformance                | Validates event definitions and dependencies          |
| Scenario Variant Conformance     | Validates controlled scenario variations              |
| Verification Target Conformance  | Validates links to claims and criteria                |
| Composition Conformance          | Validates multi-loop scenario composition             |
| Reproducibility Conformance      | Validates reproducibility information                 |
| Logical Simulation Readiness     | Establishes suitability for logical simulation        |
| State-Based Simulation Readiness | Establishes suitability for state-based simulation    |

Advanced simulation readiness MAY be introduced through future governed extensions.

A scenario MAY be ready for logical simulation while remaining incomplete for state-based simulation.

Simulation readiness SHALL therefore be mode-specific.

## 22. Canonical Representation and Validation

The implementation SHALL provide:

1. A canonical machine-readable SimulationScenario representation.
2. A canonical InitialConditions representation.
3. A canonical Disturbance representation.
4. A canonical ScenarioEvent and EventSchedule representation.
5. A canonical ScenarioVariant representation.
6. JSON Schema validation for structural correctness.
7. Semantic validation of model references.
8. State and parameter validation.
9. Disturbance and event validation.
10. Scenario compatibility validation.
11. Reproducibility validation.
12. Version-aware import and export.
13. Round-trip serialization tests.
14. Reference scenarios covering normal, degraded, failure and recovery conditions.

The model SHOULD support human-readable YAML serialization consistent with existing AOCL conventions.

The canonical scenario model SHALL remain independent of the simulation engine implementation.

## 23. Illustrative Example — Network Service Assurance

### 23.1 Scenario definition

**Scenario ID:** `SCN-NET-001`\
**Name:** Network Service Congestion and Recovery\
**Purpose:** Evaluate whether a network service assurance loop can detect congestion, select an authorized remediation action, restore service latency and verify the resulting outcome.

**Desired outcome:** Maintain network service latency below 50 ms.

### 23.2 Model references

| Model element            | Reference                                      |
| ------------------------ | ---------------------------------------------- |
| ClosedLoop               | Network Service Assurance Loop                 |
| Plant                    | Network service                                |
| Sensor                   | Network telemetry                              |
| Controller               | Service assurance Controller                   |
| Decision architecture    | MAPE-K                                         |
| Actuator                 | Traffic engineering interface                  |
| Knowledge                | Historical incidents and remediation outcomes  |
| Behavioral specification | Seven-stage service assurance specification    |
| Verification model       | Service latency and resource constraint claims |

### 23.3 Initial conditions

| Variable                   | Initial value | Meaning                       |
| -------------------------- | ------------- | ----------------------------- |
| Plant latency              | 42 ms         | Actual service latency        |
| Controller-visible latency | 42 ms         | Initial telemetry observation |
| Traffic utilization        | 65%           | Initial traffic load          |
| Available route capacity   | 100%          | Available capacity baseline   |
| Controller state           | Monitoring    | Normal operation              |
| Actuator state             | Available     | Ready to execute              |
| Service mode               | Normal        | Initial operating mode        |

### 23.4 Scenario parameters

| Parameter                     | Value | Unit    |
| ----------------------------- | ----- | ------- |
| Latency target                | 50    | ms      |
| Congestion threshold          | 70    | ms      |
| Traffic increase              | 35    | %       |
| Observation delay             | 5     | seconds |
| Actuator execution delay      | 3     | seconds |
| Evaluation interval           | 30    | seconds |
| Maximum permitted utilization | 90    | %       |

These are illustrative scenario values and not universal network engineering thresholds.

### 23.5 Disturbance definition

**Disturbance:** Sudden Traffic Demand Increase

- Classification: Demand.
- Target: Network service Plant.
- Onset: 60 seconds after scenario start.
- Magnitude: 35% traffic increase.
- Profile: Step increase.
- Duration: Persistent until remediation or scenario termination.
- Expected effect: Increased resource utilization and service latency.

### 23.6 Scenario event schedule

| Time or condition           | Event                           | Expected effect                            |
| --------------------------- | ------------------------------- | ------------------------------------------ |
| 0 seconds                   | Scenario starts                 | Initial conditions established             |
| 60 seconds                  | Traffic demand increases        | Plant experiences increased load           |
| After telemetry delay       | Congestion observation received | Controller receives delayed information    |
| After analysis              | Remediation decision            | Controller selects an appropriate response |
| After authorization         | Traffic redistribution command  | Actuator receives intervention             |
| After execution             | Network state changes           | Traffic allocation changes                 |
| After verification interval | Post-remediation observation    | Outcome can be evaluated                   |

### 23.7 Verification targets

| Target                 | Expected condition                                    |
| ---------------------- | ----------------------------------------------------- |
| Congestion detection   | Latency deviation is detected                         |
| Decision authorization | Intervention is within permitted authority            |
| Actuator execution     | Authorized command is executed                        |
| State transition       | Traffic allocation changes as expected                |
| Outcome achievement    | Latency returns below 50 ms                           |
| Resource constraint    | Utilization remains within the permitted limit        |
| Feedback integrity     | Post-intervention observation is sufficiently current |
| Learning evidence      | Remediation effectiveness is recorded                 |

### 23.8 Required scenario variants

The base scenario SHALL be extended with the following variants.

| Variant       | Change                                  | Intended evaluation                    |
| ------------- | --------------------------------------- | -------------------------------------- |
| SCN-NET-001-A | Normal demand                           | Baseline behavior                      |
| SCN-NET-001-B | Sudden congestion                       | Detection and remediation              |
| SCN-NET-001-C | Stale telemetry                         | Data veracity and decision quality     |
| SCN-NET-001-D | Actuator failure                        | Exception handling and recovery        |
| SCN-NET-001-E | Successful action, unsuccessful outcome | Outcome verification                   |
| SCN-NET-001-F | Conflicting loop interventions          | Multi-loop coordination                |
| SCN-NET-001-G | Oscillating operating conditions        | Stability and convergence              |
| SCN-NET-001-H | Human approval required                 | Human participation and escalation     |
| SCN-NET-001-I | Safety constraint blocks action         | Authority and constraint enforcement   |
| SCN-NET-001-J | Random demand variation                 | Robustness under stochastic conditions |

### 23.9 Important failure case — Successful execution without recovery

Assume the Controller issues an authorized redistribution command and the Actuator reports successful execution.

However, the resulting Plant latency remains at 65 ms.

The scenario SHALL establish separate results for:

- Decision validity.
- Authorization.
- Actuator execution.
- State transition.
- Goal achievement.

The scenario is not successful merely because the actuator completed its task.

The latency Goal remains unachieved.

### 23.10 Important observability case — Hidden disturbance

Assume traffic demand increases, but the Controller receives delayed telemetry.

The scenario SHALL preserve the actual Plant state and the Controller-visible observation as separate values.

The Controller must respond to the information available to it, not to the scenario's hidden ground truth.

This is necessary to evaluate the effects of observation delay and data veracity.

## 24. Migration and Compatibility

Existing AOCL simulation-related configurations, examples, fixtures and model data SHALL be reviewed for scenario information that can be mapped into the new model.

Migration SHALL:

- Preserve existing loop identifiers.
- Preserve existing scenario-like configurations where available.
- Preserve existing model references.
- Preserve available parameter definitions.
- Preserve relevant initial-state information.
- Preserve existing test and simulation fixture identities.
- Identify undocumented assumptions.
- Identify hard-coded disturbance behavior.
- Identify scenario data embedded in engine-specific implementations.
- Avoid fabricating missing initial conditions.
- Avoid interpreting test fixtures as complete SimulationScenarios without validation.
- Preserve historical simulation results and their original configuration references where available.

Where a legacy scenario cannot be mapped completely, it MAY be represented as Draft or Unresolved pending completion.

Existing assessment and realization capabilities SHALL remain unaffected by this change.

## 25. Architectural Decisions

The following decisions are proposed for formal adoption.

| Decision  | Proposed resolution                                              |
| --------- | ---------------------------------------------------------------- |
| AD-009-01 | SimulationScenario is a first-class governed model artifact      |
| AD-009-02 | Scenario and BehavioralSpecification remain separate artifacts   |
| AD-009-03 | Initial conditions are explicit and validated                    |
| AD-009-04 | Actual, observed and estimated states remain distinct            |
| AD-009-05 | Disturbances are first-class modeled influences                  |
| AD-009-06 | Disturbances and events have distinct semantics                  |
| AD-009-07 | Time-based and event-based scenarios are supported               |
| AD-009-08 | Deterministic and stochastic scenarios are supported             |
| AD-009-09 | Scenario variants inherit from a defined base scenario           |
| AD-009-10 | Scenario assumptions and limitations are explicit                |
| AD-009-11 | Verification targets reference the CR-008 model                  |
| AD-009-12 | Multi-loop scenarios use the CR-005 composition model            |
| AD-009-13 | Scenario reproducibility is a normative requirement              |
| AD-009-14 | Scenario compatibility is evaluated against exact model versions |
| AD-009-15 | Simulation readiness is mode-specific                            |
| AD-009-16 | Scenario definitions remain independent of engine implementation |

## 26. Acceptance Criteria

This CR is accepted when:

1. SimulationScenario is established as a first-class model concept.
2. Scenario identity and lifecycle are defined.
3. ScenarioContext is defined.
4. InitialConditions and InitialState are defined.
5. Initialization methods are governed.
6. Actual, observed and estimated state distinctions are preserved.
7. ScenarioParameter is defined with typing and validation.
8. OperatingCondition and EnvironmentalCondition are defined.
9. Disturbance is established as a first-class model concept.
10. Disturbance classifications are defined.
11. DisturbanceProfile is defined.
12. Disturbance effects reference the CR-007 state model.
13. Unknown disturbances are supported.
14. ScenarioEvent and EventSchedule are defined.
15. Time-based and event-based triggering are supported.
16. Event concurrency and ordering are representable.
17. ScenarioVariant is defined.
18. ScenarioAssumption and ScenarioConstraint are defined.
19. ExpectedObservation is defined.
20. ScenarioVerificationTarget references the CR-008 verification model.
21. Multi-loop scenario composition is supported.
22. Stochastic scenario definitions are supported.
23. Scenario reproducibility requirements are defined.
24. Scenario compatibility is defined.
25. Logical and state-based simulation readiness are distinguished.
26. Structural and semantic validation requirements are documented.
27. A network service assurance scenario is represented.
28. Normal, degraded, failure, recovery and conflicting-loop variants are specified.
29. Migration and compatibility requirements are documented.
30. No simulation-engine execution semantics are introduced prematurely.

## 27. Dependencies and Next Change Requests

CR-009 completes the proposed core Modeling stage.

The next deliverable is:

**AOCL-CR-010 — Establish Canonical Execution Semantics.**

CR-010 SHALL establish how a valid BehavioralSpecification and SimulationScenario are interpreted and executed by AOCL.

It should define:

- ExecutionInstance.
- ExecutionContext.
- ExecutionState.
- BehavioralElement activation.
- Transition evaluation.
- Event handling.
- Condition evaluation.
- Scheduling and synchronization.
- Execution state and lifecycle.
- Action dispatch and result handling.
- Timeout and retry semantics.
- Exception propagation.
- Cancellation and termination.
- Safe-state handling.
- Execution trace generation.
- Runtime evidence references.
- Deterministic execution requirements.
- Human participation and approval handling.

CR-010 SHALL consume the canonical models from CR-001 through CR-009 without redefining their domain semantics.

The subsequent sequence remains:

| CR          | Deliverable                                    |
| ----------- | ---------------------------------------------- |
| AOCL-CR-011 | Logical Simulation Engine                      |
| AOCL-CR-012 | State-Based Simulation Engine                  |
| AOCL-CR-013 | Simulation Trace and Replay                    |
| AOCL-CR-014 | Graph-Based Visual Modeling Canvas             |
| AOCL-CR-015 | Simulation Controls and Runtime Visualization  |
| AOCL-CR-016 | Scenario Management and Comparison             |
| AOCL-CR-017 | CLAM Integration Enhancement                   |
| AOCL-CR-018 | OpenDEA Entity References and Interoperability |

## 28. Recommendation

Approve AOCL-CR-009 as the canonical scenario and disturbance foundation.

This CR establishes the conditions under which AOCL can test whether a closed loop behaves plausibly, robustly and safely.

It also makes scenario design a governed engineering activity rather than an informal collection of test inputs.

The most important design principle is that a scenario must represent the conditions available to the modeled system, not simply expose all scenario information to the Controller.

Actual Plant state, observed state, environmental conditions, disturbances and Controller-visible information must remain distinct.

This is essential to testing the effects of data veracity, control decisions, feedback delays, competing interventions and unexpected operating conditions.

With CR-009, AOCL's core conceptual modeling sequence is complete. The next phase can establish how these canonical models are interpreted and executed without prematurely coupling the domain model to a particular simulation engine.

**End of AOCL-CR-009.**

## Modeling stage closure

The proposed Modeling sequence is now complete:

| CR     | Established model                               |
| ------ | ----------------------------------------------- |
| CR-006 | What the loop is specified to do                |
| CR-007 | What control actions and state transitions mean |
| CR-008 | How behavior and outcomes are verified          |
| CR-009 | Under what conditions behavior is evaluated     |

The next step, CR-010, is an important architectural transition. It must connect these four models into a coherent execution contract while preserving the separation between the canonical domain model and the simulation engines.

I recommend completing CR-010 before implementing either simulation engine.