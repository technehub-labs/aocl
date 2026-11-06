# AOCL-CR-004 — Establish the Canonical Control Architecture Metamodel

> **Status:** Proposed · **Queued:** 2026-11-07 (fourth deliverable of the foundation tranche, after CR-003). Drafted from the architectural review; carries the review's five pre-approval considerations (Plant as semantic role, Observation first-class, Controller as authority, actuator feedback ≠ outcome verification, multi-controller authority boundaries).

---

CR-003 defined the behavioral responsibilities of a closed loop. CR-004 now defines the structural elements that realize those responsibilities: the controlled system, sensing mechanisms, observations, controller, actuators and knowledge resources.

The critical distinction is that the behavioral lifecycle describes what the loop does; the control architecture describes the components and relationships through which it does it. A controller may realize several behavioral stages, and a behavioral stage may involve several architectural components.

# AOCL-CR-004 — Establish the Canonical Control Architecture Metamodel

| Field           | Value                                                                        |
| --------------- | ---------------------------------------------------------------------------- |
| Change ID       | AOCL-CR-004                                                                  |
| Title           | Establish the Canonical Control Architecture Metamodel                       |
| Status          | Proposed                                                                     |
| Change Type     | Foundational / Metamodel                                                     |
| Priority        | Critical                                                                     |
| Target          | AOCL Domain Model                                                            |
| Depends On      | AOCL-CR-001, AOCL-CR-002, AOCL-CR-003                                        |
| Related Changes | AOCL-CR-005, AOCL-CR-006, AOCL-CR-007, AOCL-CR-008, AOCL-CR-009, AOCL-CR-010 |

---

## 1. Executive Summary

This Change Request establishes the canonical structural control architecture for AOCL.

The AOCL conceptual foundation requires a closed loop to represent a governed feedback system in which observations of a controlled environment inform decisions and interventions that influence subsequent states. The resulting effects are evaluated against intent and constraints.

The behavioral lifecycle established by AOCL-CR-003 describes the responsibilities through which this occurs. However, those responsibilities require an architectural representation of the systems and mechanisms that observe, interpret, control and influence the operational environment.

This CR establishes the following canonical control architecture elements:

1. **Plant** — the system or operational domain whose state or behavior is subject to control.
2. **Sensor** — a mechanism that acquires information about the Plant or its environment.
3. **Observation** — a representation of acquired information about an observed condition or event.
4. **Controller** — the logical or physical control authority that interprets conditions, evaluates policies and selects control responses.
5. **Actuator** — a mechanism through which an authorized intervention is applied.
6. **Knowledge** — governed information and models used to inform control behavior and improve its effectiveness.

The architecture also recognizes supporting concepts, including control signals, feedback signals, disturbances, operating environments, control variables and architectural bindings.

The metamodel SHALL support physical, digital, software-defined, organizational and hybrid controlled systems. It SHALL NOT assume that every Plant is a physical machine or that every Sensor and Actuator is a hardware device.

The canonical architecture must support distributed, hierarchical, centralized, decentralized and multi-controller configurations.

## 2. Problem Statement

The behavioral lifecycle establishes the responsibilities of a closed loop but does not yet define the architectural entities through which those responsibilities are realized.

Without a canonical control architecture:

- The controlled system may be confused with the controller.
- Observations may be confused with sensors or raw telemetry.
- Decisions may be confused with control signals.
- Actuators may be modeled as arbitrary activities rather than intervention mechanisms.
- Knowledge may be treated as an undifferentiated data store.
- Feedback may be confused with the mere availability of monitoring data.
- The architecture may become tied to physical control systems, excluding enterprise and digital operating environments.
- The visual model, simulation engine and canonical metamodel may adopt incompatible interpretations of the same components.

AOCL therefore requires a technology-independent control architecture metamodel with explicit component semantics and relationships.

## 3. Objectives

This CR SHALL:

1. Establish the canonical control architecture vocabulary.
2. Define the semantic responsibility of each architectural element.
3. Distinguish the Plant from the Controller and the environment.
4. Distinguish Sensors, Observations and Knowledge.
5. Define the Controller's architectural responsibility.
6. Distinguish Actuators from decisions and execution activities.
7. Establish the conceptual role of control and feedback signals.
8. Support disturbances and environmental influences.
9. Support multiple Sensors, Actuators and Controllers.
10. Support distributed and hierarchical control architectures.
11. Establish the relationship between architectural components and behavioral stages.
12. Establish structural validation requirements.
13. Provide the architectural foundation for subsequent control contracts and simulation semantics.

## 4. Scope

### 4.1 In scope

- Canonical control architecture.
- Plant and controlled-system semantics.
- Sensor and observation-source semantics.
- Observation representation.
- Controller semantics.
- Actuator semantics.
- Knowledge-resource semantics.
- Control and feedback signal concepts.
- Disturbance and environment concepts.
- Architectural composition and topology.
- Component-to-behavioral-stage mapping.
- Structural validation requirements.
- Architectural conformance.

### 4.2 Out of scope

| Change      | Responsibility                                                               |
| ----------- | ---------------------------------------------------------------------------- |
| AOCL-CR-005 | Canonical relationships, constraints and loop composition                    |
| AOCL-CR-006 | Machine-readable metamodel and behavioral schemas                            |
| AOCL-CR-007 | Control contracts, control variables, state transitions and action semantics |
| AOCL-CR-008 | Verification, evidence and outcome evaluation                                |
| AOCL-CR-009 | Simulation scenarios, disturbances and initial-state configuration           |
| AOCL-CR-010 | Canonical execution semantics                                                |
| AOCL-CR-011 | Logical simulation engine                                                    |
| AOCL-CR-012 | State-based simulation engine                                                |

This CR establishes architectural semantics. It does not prescribe a specific controller algorithm, communication protocol, sensor technology, actuator implementation or simulation engine.

## 5. Canonical Control Architecture

### 5.1 Architectural overview

The canonical control architecture comprises six primary elements.

| Element     | Canonical ID   | Primary responsibility                                      |
| ----------- | -------------- | ----------------------------------------------------------- |
| Plant       | CA-PLANT       | Represents the controlled system                            |
| Sensor      | CA-SENSOR      | Acquires information about the Plant or environment         |
| Observation | CA-OBSERVATION | Represents acquired information                             |
| Controller  | CA-CONTROLLER  | Evaluates conditions and determines control responses       |
| Actuator    | CA-ACTUATOR    | Applies authorized interventions                            |
| Knowledge   | CA-KNOWLEDGE   | Supplies governed information and models supporting control |

These elements are conceptually distinct even where one implementation component performs multiple responsibilities.

For example, a software platform may combine monitoring, analysis and control logic. Its AOCL representation should nevertheless preserve the distinction between the information acquisition, analytical, decision and intervention responsibilities.

### 5.2 Reference architecture

The following conceptual relationship is illustrative:

```
flowchart LR
    E["Operating Environment"] --> P["Plant"]
    D["Disturbances"] --> P

    P --> S["Sensors"]
    E --> S

    S --> O["Observations"]
    O --> C["Controller"]

    K["Knowledge"] <--> C
    C --> CS["Control Signal"]
    CS --> A["Actuators"]
    A --> P

    P -. "Subsequent state" .-> S

    C -. "Behavioral decisions" .-> B["Decision and Behavioral Logic"]
    B -. "Intent and constraints" .-> C
```

This is a conceptual topology rather than a mandatory deployment architecture. It does not prescribe communication direction, protocol, physical connectivity or execution sequence.

## 6. Canonical Architectural Elements

### 6.1 Plant

**Definition:** The Plant is the system, entity or operational domain whose state, behavior or outcomes are subject to control by a closed loop.

The Plant represents the controlled subject, not the control mechanism.

A Plant may be:

- A physical asset or machine.
- A network or infrastructure domain.
- A software application or service.
- A business process or operational capability.
- An organizational function.
- An enterprise operating environment.
- A digital twin or simulated system.
- A composite of interacting physical and digital systems.

Responsibilities:

- Represent the controlled system boundary.
- Identify the relevant operational context.
- Expose or make accessible the state and behavior relevant to control.
- Receive interventions through applicable mechanisms.
- Produce state changes and outcomes that can be observed.
- Identify dependencies on external systems and environmental conditions.

A Plant may contain or represent multiple internal subsystems. Those subsystems need not all be independently modeled as Plants.

A composite Plant may be decomposed into subordinate controlled systems when the control architecture requires that distinction.

**Important distinction:** A system that is monitored but cannot be influenced by the closed loop is not necessarily a Plant. It may instead be an observation source, environmental system or external dependency.

### 6.2 Sensor

**Definition:** A Sensor is a mechanism that acquires information about the state, behavior, events or conditions of a Plant or its operating environment.

A Sensor may be:

- A physical sensor.
- A software monitoring component.
- A telemetry collector.
- An application programming interface.
- An event subscription.
- A human observation mechanism.
- An analytical or derived measurement mechanism.
- An external information service.

Responsibilities:

- Acquire information from an identifiable source.
- Identify the observed subject or variable.
- Provide information to an observation mechanism.
- Preserve source and acquisition provenance.
- Support the identification of measurement quality and freshness.
- Identify unavailable, invalid or conflicting information where detectable.

A Sensor may acquire multiple variables. Multiple Sensors may observe the same variable through independent sources.

A Sensor does not inherently interpret the operational meaning of the information it acquires.

**Semantic boundary:** A Sensor is the acquisition mechanism; an Observation is the information acquired or represented through that mechanism.

### 6.3 Observation

**Definition:** An Observation is a representation of information acquired about a condition, state, variable or event associated with a Plant or its environment.

An Observation is an information artifact, not an acquisition mechanism.

Responsibilities:

- Represent the observed value, condition or event.
- Identify the observed subject.
- Identify the source or acquisition mechanism.
- Record the observation time.
- Represent units and relevant measurement context.
- Identify provenance and quality information.
- Support subsequent interpretation and verification.

An Observation may represent:

- A direct sensor reading.
- An event notification.
- A human-reported condition.
- A calculated or derived measurement.
- An aggregate of multiple observations.
- A state estimate produced by an analytical model.

Observation quality should distinguish at least:

- Validity.
- Accuracy or confidence, where known.
- Completeness.
- Freshness.
- Provenance.
- Consistency.

An Observation SHALL NOT automatically be treated as the actual state of the Plant. It is evidence about that state.

### 6.4 Controller

**Definition:** A Controller is the logical or physical control authority responsible for determining and coordinating control responses in accordance with the closed loop's intent, policies and constraints.

The Controller is the central control decision authority in the conceptual architecture. This does not imply that it must be implemented as one centralized software component.

Responsibilities:

- Consume relevant observations.
- Interpret operational conditions.
- Evaluate deviations against reference conditions.
- Use applicable knowledge and analytical models.
- Evaluate control policies and constraints.
- Select appropriate control responses.
- Establish authorization requirements.
- Coordinate control actions through Actuators.
- Evaluate control feedback.
- Support governed learning and adaptation.

A Controller may be:

- A conventional control algorithm.
- A rule-based decision engine.
- A model-predictive controller.
- An AI-enabled decision system.
- An agent or collection of agents.
- A human operator.
- A hybrid human-machine control arrangement.

A Controller may be decomposed into multiple cooperating control functions.

The architectural representation SHALL permit:

- Single-controller configurations.
- Hierarchical controllers.
- Distributed controllers.
- Peer or cooperative controllers.
- Supervisory control.
- Human-supervised autonomous control.
- Multiple controllers operating on shared or overlapping Plants.

A Controller SHALL remain subject to the applicable authority model and control constraints.

**Semantic boundary:** A Controller selects and coordinates control responses. It does not itself represent the controlled system or necessarily perform the physical or digital intervention.

### 6.5 Actuator

**Definition:** An Actuator is a mechanism through which an authorized control intervention is applied to a Plant or its operating environment.

An Actuator may be:

- A physical actuator.
- A network configuration interface.
- A software command interface.
- A service-management API.
- A workflow or process invocation.
- An automated operational agent.
- A human operator acting under defined authority.

Responsibilities:

- Receive an authorized intervention.
- Validate applicable execution conditions.
- Apply the requested intervention through the relevant interface.
- Record execution status.
- Report success, failure or partial completion where available.
- Make resulting effects observable through the control architecture.

An Actuator may support multiple action types. Multiple Actuators may cooperate to apply a composite intervention.

**Semantic boundary:** An Actuator applies an intervention. The Controller selects the response, and the Plant is the subject whose state or behavior may be changed.

An actuator's report that a command was accepted or completed is not sufficient evidence that the intended Plant outcome was achieved.

### 6.6 Knowledge

**Definition:** Knowledge is a governed collection of information, models, rules, policies and historical experience used to inform the operation and improvement of a closed loop.

Knowledge may include:

- Control policies.
- Operational rules.
- System models.
- Analytical models.
- Decision models.
- Historical observations.
- Historical decisions and actions.
- Performance baselines.
- Causal models.
- Learned patterns.
- Approved operating procedures.
- Domain and enterprise semantics.

Responsibilities:

- Provide contextual information to control functions.
- Support interpretation of observations.
- Inform decision selection.
- Support prediction and evaluation.
- Preserve historical evidence.
- Support learning and controlled model improvement.
- Maintain provenance, version and governance information.

Knowledge may be held in repositories, models, databases, knowledge graphs or distributed services.

It is a cross-cutting architectural resource, not necessarily a sequential behavioral stage or a single centralized component.

Knowledge updates SHALL be governed. The availability of new information does not automatically authorize a change to control policy or operational authority.

## 7. Supporting Architectural Concepts

The following concepts support the six primary elements. They are included to establish a complete architectural vocabulary without prematurely defining detailed execution semantics.

### 7.1 Operating Environment

**Definition:** The Operating Environment is the external or surrounding context within which a Plant operates and which may influence its behavior or conditions.

It may include:

- External systems.
- Physical conditions.
- Network conditions.
- Market conditions.
- Organizational conditions.
- Regulatory conditions.
- Other operational actors.

The environment is distinct from the Plant, although a model may define a composite controlled boundary that includes selected environmental subsystems.

### 7.2 Disturbance

**Definition:** A Disturbance is an external or internal influence that changes, or may change, the state or behavior of the Plant independently of the controller's intended intervention.

Examples:

- Unexpected traffic demand.
- Equipment degradation.
- Environmental changes.
- External system failures.
- Workload variation.
- Unplanned operational events.
- Adverse market or supply conditions.

A disturbance may be observed, estimated or unknown.

Disturbances are relevant to simulation, robustness analysis and control effectiveness.

Detailed disturbance modeling is reserved for AOCL-CR-009.

### 7.3 Control Signal

**Definition:** A Control Signal is a representation of an instruction, command, setpoint or control input issued by a Controller to an Actuator or control interface.

A Control Signal communicates the selected intervention. It is not itself proof that the intervention was applied or that the Plant changed as intended.

### 7.4 Feedback Signal

**Definition:** A Feedback Signal is information returned from the Plant, Actuator or associated observation mechanism that informs the Controller about the resulting condition or response.

Feedback may include:

- Observed Plant state.
- Measured performance.
- Actuator execution status.
- Command acceptance or rejection.
- Operational events.
- Verification findings.

Feedback must retain sufficient provenance to distinguish actuator-reported status from independently observed Plant outcomes.

### 7.5 Control Variable

**Definition:** A Control Variable is a variable whose value or behavior is relevant to controlling the Plant.

Control variables may be:

- Measured variables.
- Estimated state variables.
- Setpoints.
- Manipulated variables.
- Disturbance variables.
- Performance variables.

Detailed classification, typing, units and state-transition semantics are reserved for AOCL-CR-007.

### 7.6 Reference Condition

**Definition:** A Reference Condition is a defined desired, acceptable or expected condition against which an observed or estimated condition may be evaluated.

Reference Conditions are grounded in the IntentSpecification established by AOCL-CR-002.

They may represent:

- Target values.
- Acceptable ranges.
- Thresholds.
- Qualitative conditions.
- Operating envelopes.
- State-dependent conditions.

A Reference Condition is not necessarily a control signal or an action.

## 8. Structural and Behavioral Separation

The control architecture and behavioral lifecycle SHALL remain distinct.

The following table establishes the principal relationship.

| Architectural element | Principal behavioral responsibilities                           |
| --------------------- | --------------------------------------------------------------- |
| Plant                 | Subject of Observe, Execute and Verify                          |
| Sensor                | Supports Observe                                                |
| Observation           | Input to Observe, Analyze and Verify                            |
| Controller            | Supports Analyze, Decide and coordination of Execute and Verify |
| Actuator              | Supports Execute                                                |
| Knowledge             | Cross-cutting support for Analyze, Decide and Learn             |
| Operating Environment | Context for Observe, Analyze and Execute                        |
| Disturbance           | Influences Plant behavior and simulation scenarios              |
| Control Signal        | Carries a selected intervention toward an Actuator              |
| Feedback Signal       | Carries information about execution or resulting conditions     |

This mapping is many-to-many.

For example:

- A Controller may contain analytical, decision and supervisory responsibilities.
- A Sensor may provide information to several controllers.
- An Observation may be consumed by multiple behavioral activities.
- A behavioral Execute stage may coordinate several Actuators.
- Knowledge may support several Controllers and behavioral stages.
- One Plant may be controlled by multiple cooperating or hierarchical Controllers.

No architectural element SHALL be treated as equivalent to a behavioral stage merely because it commonly realizes that stage.

## 9. Control Architecture Configurations

The metamodel SHALL support different architectural topologies.

### 9.1 Single-controller configuration

A single Controller coordinates the control behavior for one Plant or controlled-system boundary.

Typical characteristics:

- One principal decision authority.
- Multiple Sensors.
- Multiple Actuators.
- Shared Knowledge.
- One or more control objectives.

### 9.2 Hierarchical control

Multiple Controllers operate at different control levels.

A higher-level Controller may establish goals, constraints or setpoints for subordinate Controllers.

Subordinate Controllers may perform more immediate operational control.

The model must distinguish:

- Supervisory authority.
- Local control authority.
- Delegated responsibilities.
- Constraints imposed by higher-level controllers.
- Feedback between control levels.

### 9.3 Distributed control

Multiple Controllers operate across different components, services or operational boundaries.

The model must permit:

- Distributed observations.
- Independent decision responsibilities.
- Coordinated actions.
- Shared Knowledge.
- Explicit control dependencies.
- Conflict detection and resolution.

### 9.4 Cooperative control

Multiple Controllers may coordinate toward shared or interdependent goals.

The model must support explicit responsibility and authority boundaries.

A cooperative relationship must not imply unrestricted authority to intervene in another controller's Plant.

### 9.5 Supervisory human-machine control

Human operators may participate as Controllers, approval authorities, supervisors or escalation recipients.

The architecture must represent the human role explicitly rather than treating all human intervention as an unstructured exception.

### 9.6 Hybrid control

A closed loop may combine conventional controllers, software agents, human decision-makers and physical control mechanisms.

The architecture must remain independent of the technology or actor type used to implement each responsibility.

## 10. Architectural Relationships

The following relationships establish the intended semantic connections. Detailed cardinalities, formal relationship types, composition rules and constraints will be standardized under AOCL-CR-005.

| Source               | Relationship            | Target         | Meaning                                                     |
| -------------------- | ----------------------- | -------------- | ----------------------------------------------------------- |
| Plant                | ObservedBy              | Sensor         | A Sensor acquires information about a Plant                 |
| Sensor               | Produces                | Observation    | A Sensor provides information represented as an Observation |
| Observation          | Informs                 | Controller     | An Observation informs control reasoning                    |
| Controller           | Uses                    | Knowledge      | A Controller consumes governed Knowledge                    |
| Controller           | Issues                  | ControlSignal  | A Controller issues a control instruction                   |
| ControlSignal        | DeliveredTo             | Actuator       | An Actuator receives the intervention instruction           |
| Actuator             | Influences              | Plant          | An Actuator applies an intervention to the Plant            |
| Plant                | AffectedBy              | Disturbance    | A Disturbance influences Plant behavior                     |
| OperatingEnvironment | Influences              | Plant          | The environment affects Plant conditions                    |
| Plant                | ProvidesFeedbackThrough | Sensor         | Plant conditions are made observable                        |
| Actuator             | Reports                 | FeedbackSignal | An Actuator reports execution-related feedback              |
| FeedbackSignal       | Informs                 | Controller     | Feedback informs subsequent control reasoning               |

These relationships are semantic declarations, not mandatory implementation interfaces.

## 11. Control Architecture Invariants

The following invariants SHALL apply to conformant AOCL models.

### 11.1 Plant and Controller distinction

The Plant and Controller are conceptually distinct.

An implementation may host both on the same infrastructure, but their responsibilities must remain distinguishable.

### 11.2 Observation provenance

Every Observation used as material control evidence must have an identifiable source or explicitly declared derivation mechanism.

### 11.3 Sensor and Observation distinction

A Sensor is an acquisition mechanism. An Observation is the resulting information artifact.

### 11.4 Decision and intervention distinction

A control decision is distinct from the Control Signal used to communicate it and the Actuator that applies it.

### 11.5 Intervention traceability

An intervention must be traceable to an originating control decision and its applicable authorization.

### 11.6 Feedback integrity

Feedback must identify whether it represents:

- Command or actuator status.
- Direct Plant observation.
- Derived state estimation.
- Independent outcome verification.

These categories must not be silently treated as interchangeable.

### 11.7 Knowledge governance

Knowledge resources must have identifiable provenance and applicable version or governance information.

### 11.8 Environment distinction

The Plant and Operating Environment must have identifiable boundaries, even where the modeled controlled domain includes selected external subsystems.

### 11.9 Constraint preservation

The existence of an architectural connection does not grant authority to issue or apply an intervention.

### 11.10 Technology independence

The architecture must not require a particular physical, software, organizational or agent technology.

## 12. Illustrative Control Architecture Model

The following YAML is illustrative and not the normative schema.

```
controlArchitecture:
  id: aocl:architecture/network-service-assurance
  name: Network Service Assurance Control Architecture
  version: 1.0.0
  lifecycleStatus: Draft

  plant:
    id: plant:network-service
    name: Network Service
    description: Controlled network service and its operational state

  operatingEnvironment:
    id: environment:network-operations
    name: Network Operating Environment

  sensors:
    - id: sensor:latency-monitor
      name: Service Latency Monitor
      observes:
        - plant:network-service

    - id: sensor:traffic-monitor
      name: Network Traffic Monitor
      observes:
        - plant:network-service
        - environment:network-operations

  observations:
    - id: observation:service-latency
      name: Service Latency Observation
      source: sensor:latency-monitor
      observedSubject: plant:network-service
      variable: service-latency

    - id: observation:traffic-load
      name: Traffic Load Observation
      source: sensor:traffic-monitor
      observedSubject: plant:network-service
      variable: traffic-load

  controller:
    id: controller:service-assurance
    name: Service Assurance Controller
    consumes:
      - observation:service-latency
      - observation:traffic-load
    usesKnowledge:
      - knowledge:service-policy
      - knowledge:network-model

  knowledge:
    - id: knowledge:service-policy
      name: Service Assurance Policy

    - id: knowledge:network-model
      name: Network Operational Model

  actuators:
    - id: actuator:traffic-engineering
      name: Traffic Engineering Interface
      influences:
        - plant:network-service

  controlSignals:
    - id: signal:traffic-redistribution
      issuedBy: controller:service-assurance
      deliveredTo: actuator:traffic-engineering

  disturbances:
    - id: disturbance:traffic-spike
      name: Unexpected Traffic Spike
      affects:
        - plant:network-service
```

The example illustrates the distinction between:

- The controlled system.
- The mechanisms used to observe it.
- The observations obtained.
- The controller that reasons over those observations.
- The knowledge used to inform decisions.
- The intervention mechanism.
- The disturbance that may affect the Plant.

It does not prescribe a particular control algorithm or guarantee that the selected intervention will achieve the intended result.

## 13. Metamodel Validation Requirements

| ID      | Requirement                                                                                                  |
| ------- | ------------------------------------------------------------------------------------------------------------ |
| CAM-001 | Every ControlArchitecture SHALL have a stable identifier, name and version.                                  |
| CAM-002 | Every ControlArchitecture SHALL be associated with a valid ClosedLoop.                                       |
| CAM-003 | Every modeled Plant SHALL have a stable identifier and defined controlled-system identity.                   |
| CAM-004 | Plant and Controller responsibilities SHALL remain semantically distinguishable.                             |
| CAM-005 | Every Sensor SHALL have an identifiable acquisition responsibility.                                          |
| CAM-006 | Every Observation used as control evidence SHALL identify its source or derivation mechanism.                |
| CAM-007 | Every Observation SHALL identify its observed subject or declared observation scope.                         |
| CAM-008 | Observation provenance SHALL be representable.                                                               |
| CAM-009 | Observation time and relevant freshness information SHALL be representable.                                  |
| CAM-010 | Every Controller SHALL have an identifiable control responsibility and authority context.                    |
| CAM-011 | Controller-to-Knowledge relationships SHALL be representable.                                                |
| CAM-012 | Every Actuator SHALL have an identifiable intervention mechanism and applicable Plant or operational target. |
| CAM-013 | Control decisions SHALL be distinguishable from Control Signals and Actuator execution.                      |
| CAM-014 | Control Signals SHALL identify their originating Controller and intended recipient or destination.           |
| CAM-015 | Feedback information SHALL distinguish actuator status from observed Plant conditions.                       |
| CAM-016 | Knowledge resources SHALL support provenance and version identification.                                     |
| CAM-017 | The architecture SHALL support multiple Sensors and Actuators.                                               |
| CAM-018 | The architecture SHALL support multiple Controllers.                                                         |
| CAM-019 | The architecture SHALL support hierarchical and distributed control configurations.                          |
| CAM-020 | The architecture SHALL support cooperative control where authority boundaries are explicit.                  |
| CAM-021 | Operating Environment SHALL be distinguishable from Plant.                                                   |
| CAM-022 | Disturbances SHALL be representable as influences on Plant behavior.                                         |
| CAM-023 | The architecture SHALL support physical, digital, organizational and hybrid Plants.                          |
| CAM-024 | Architectural components SHALL be traceable to applicable behavioral responsibilities.                       |
| CAM-025 | The model SHALL not imply authorization solely from the existence of an architectural relationship.          |
| CAM-026 | The architecture SHALL preserve references to relevant Intent, Goals and Control Constraints.                |
| CAM-027 | Architectural elements SHALL have stable identifiers independent of mutable display names.                   |
| CAM-028 | The architecture SHALL be representable independently of a particular visual editor or runtime.              |
| CAM-029 | An architecture SHALL identify unresolved or invalid component references.                                   |
| CAM-030 | An architecture SHALL support structural conformance evaluation independently of simulation readiness.       |

## 14. Architectural Conformance

AOCL SHALL distinguish three architectural validation outcomes.

### 14.1 Structural conformance

An architecture is structurally conformant when:

- Required architectural entities are valid.
- Identifiers are stable and unique within their defined scope.
- Relationships reference valid entities.
- Component types are valid.
- Required provenance and version information are represented.
- The model satisfies the applicable architectural integrity rules.

### 14.2 Control architecture completeness

An architecture is control-complete when it demonstrates the necessary sensing, decision and intervention relationships for its declared closed-loop purpose.

A control-complete architecture must identify:

- The controlled system.
- The relevant observation mechanisms.
- The information supplied to control reasoning.
- The control decision authority.
- The intervention mechanism.
- The feedback path.
- The applicable knowledge and constraints.

The precise completeness rules may vary by loop type, but deviations from the canonical feedback structure must be explicit and justified.

### 14.3 Simulation readiness

An architecture is not automatically simulation-ready because its structure is valid.

Simulation readiness additionally requires adequate definitions of:

- Plant state and relevant variables.
- Observation generation or acquisition behavior.
- Controller behavior or decision rules.
- Actuator effects.
- Feedback behavior.
- Relevant environmental influences.
- Initial conditions and disturbance assumptions.

Detailed simulation configuration is reserved for AOCL-CR-009 through AOCL-CR-012.

## 15. Implementation Requirements

The implementation arising from this CR SHALL:

1. Introduce canonical architectural element types.
2. Introduce the ControlArchitecture aggregate or equivalent governed root.
3. Represent Plant, Sensor, Observation, Controller, Actuator and Knowledge independently.
4. Support the supporting architectural concepts defined in this CR.
5. Represent relationships between architectural elements.
6. Support multiple and composite Plants where required.
7. Support multiple Sensors, Observations, Controllers and Actuators.
8. Support hierarchical, distributed and cooperative configurations.
9. Preserve architectural references to the ClosedLoop and IntentSpecification.
10. Preserve traceability between architectural elements and behavioral responsibilities.
11. Validate component references and relationship integrity.
12. Support source-qualified external system and enterprise references.
13. Keep architectural definitions independent of visual canvas structures.
14. Provide machine-readable validation results.
15. Support controlled extension without changing canonical element semantics.

The implementation must not introduce a second, incompatible architecture representation for simulation.

## 16. Migration and Compatibility

Migration SHALL preserve existing AOCL information and avoid unsupported semantic inference.

The migration process must:

- Preserve existing closed-loop registrations.
- Preserve existing system and service references.
- Preserve existing sensors, monitoring and actuator references where present.
- Preserve existing decision-model selections.
- Map existing entities to canonical architectural types only where their semantics support the mapping.
- Avoid treating all monitored systems as controlled Plants.
- Avoid treating raw telemetry as a fully validated Observation.
- Avoid treating an operational command as proof of an achieved intervention.
- Avoid inferring a Controller merely from the existence of a decision-model reference.
- Preserve external references and their source systems.
- Mark incomplete architectures as Draft or otherwise identify missing architectural responsibilities.
- Preserve existing assessment and maturity records and their model-version references.

Legacy models SHALL NOT be automatically promoted to control-complete status solely because they contain system and monitoring references.

## 17. Acceptance Criteria

AOCL-CR-004 shall be accepted when:

1. The six canonical architectural elements are formally defined.
2. Plant and Controller are distinguishable.
3. Sensor and Observation are distinguishable.
4. Controller and Actuator are distinguishable.
5. Knowledge is established as a governed, cross-cutting resource.
6. Operating Environment and Disturbance are representable.
7. Control Signal and Feedback Signal are semantically distinct.
8. Control decisions are distinguishable from interventions.
9. Feedback distinguishes actuator status from observed Plant outcomes.
10. Multiple Sensors and Actuators can be represented.
11. Multiple Controllers can be represented.
12. Hierarchical and distributed control configurations can be modeled.
13. Cooperative control can be modeled with explicit authority boundaries.
14. Physical, digital, organizational and hybrid systems can be represented.
15. Architectural elements can be mapped to behavioral responsibilities.
16. Architectural relationships can be validated.
17. Structural conformance and control completeness are independently assessable.
18. Simulation readiness is distinguishable from architectural conformance.
19. A reference architecture can be validated against the canonical model.
20. An incomplete architecture produces identifiable validation findings.
21. Legacy references can be migrated without fabricating missing components.
22. The canonical architecture can be consumed by both logical and state-based simulation models.

## 18. Design Decisions and Open Questions

### D-001 — Six canonical architectural elements

**Recommendation:** Adopt Plant, Sensor, Observation, Controller, Actuator and Knowledge as the six canonical elements.

Rationale: These provide a technology-independent structural foundation for representing the essential sensing, decision and intervention responsibilities of a closed loop.

### D-002 — Plant as a technology-independent concept

**Recommendation:** Define Plant broadly enough to represent physical, digital, organizational and hybrid controlled systems.

Rationale: AOCL must not become restricted to conventional industrial control systems.

### D-003 — Observation as a first-class entity

**Recommendation:** Represent Observation independently of Sensor.

Rationale: The same information may be obtained through different mechanisms, and derived observations may have no single physical sensor.

### D-004 — Controller as a logical authority

**Recommendation:** Define Controller as a control responsibility and authority rather than a prescribed software component.

Rationale: This permits human, software, agentic, distributed and hybrid implementations.

### D-005 — Actuator as an intervention mechanism

**Recommendation:** Treat Actuator as the mechanism through which an intervention is applied, not as the action or decision itself.

Rationale: This preserves traceability between decision, command, intervention and actual outcome.

### D-006 — Knowledge as cross-cutting architecture

**Recommendation:** Treat Knowledge as a governed architectural resource available to multiple control functions.

Rationale: Knowledge is not a stage that must execute sequentially; it supports the control architecture and its learning responsibilities.

### D-007 — Environment and Disturbance as supporting concepts

**Recommendation:** Include both in the architectural vocabulary.

Rationale: A closed loop cannot be evaluated adequately without representing the context and influences affecting its controlled system.

### D-008 — Support multiple controllers

**Recommendation:** Support multiple, hierarchical, distributed and cooperative Controllers.

Rationale: Realistic enterprise and autonomous systems frequently have multiple control authorities with different scopes and responsibilities.

### D-009 — Preserve control architecture and behavioral lifecycle separation

**Recommendation:** Keep the architectural and behavioral models separately identifiable and explicitly related.

Rationale: This prevents the model from confusing what a system does with the components through which it does it.

## 19. Risks and Mitigations

| Risk                                                | Mitigation                                                                          |
| --------------------------------------------------- | ----------------------------------------------------------------------------------- |
| Plant is interpreted as physical hardware only      | Define Plant across physical, digital, organizational and hybrid domains            |
| Sensor and Observation are conflated                | Establish separate acquisition and information-artifact semantics                   |
| Controller becomes synonymous with software agent   | Define Controller by control responsibility and authority                           |
| Actuator is confused with action                    | Distinguish intervention mechanism, control signal and action contract              |
| Knowledge becomes an ungoverned data store          | Require provenance, versioning and governance                                       |
| Feedback is inferred from command acceptance        | Distinguish actuator-reported status from observed Plant outcome                    |
| Multiple Controllers produce conflicting actions    | Require explicit authority and coordination boundaries                              |
| Environment and Plant boundaries become ambiguous   | Require identifiable controlled-system and environmental scopes                     |
| Canvas dictates architecture                        | Establish the canonical architecture independently of the editor                    |
| Simulation assumes every component is deterministic | Keep implementation and simulation assumptions separate from architectural identity |

## 20. Proposed Resolution

Approve AOCL-CR-004 as the normative foundation for the AOCL control architecture metamodel.

Upon approval:

1. Plant, Sensor, Observation, Controller, Actuator and Knowledge become the canonical architectural elements.
2. Operating Environment and Disturbance become recognized supporting concepts.
3. Control Signal and Feedback Signal become distinct architectural concepts.
4. The architecture supports physical, digital, organizational and hybrid systems.
5. Multiple and distributed Controllers are permitted, subject to explicit authority boundaries.
6. Architectural elements remain distinct from behavioral stages.
7. Structural conformance and simulation readiness remain separate validation outcomes.
8. Subsequent AOCL metamodel, schema, execution and simulation changes must conform to this architecture.

**Next proposed change:** AOCL-CR-005 — Establish Canonical Relationships, Constraints and Closed-Loop Composition.

This will formalize how the foundational closed-loop entities, behavioral elements and control architecture components relate, how relationship cardinality and composition are governed, and how multiple loops can be connected into coordinated or hierarchical control structures.

## Review observations before approval

There are five important design considerations I would retain for the CR-004 review:

1\. Plant is a semantic role, not a system category. A business process, network service or physical machine can each be a Plant when it is the subject of control. This avoids creating separate physical, digital and business Plant metamodels.

2\. Observation should be first-class. This is important for data provenance, sensor fusion, derived measurements and simulation. A Sensor produces or supplies evidence; it does not define the truth of the observed state.

3\. Controller is a control authority, not necessarily an agent. This preserves compatibility with conventional control algorithms, human-supervised systems, distributed controllers and agentic architectures.

4\. Actuator feedback is not outcome verification. This is a fundamental integrity requirement. A successful API response, command acceptance or actuator status cannot independently establish that the Plant reached its intended state.

5\. The architecture must permit multiple controllers without implying unrestricted control authority. This is especially important for enterprise-scale systems, where operational, supervisory and policy control may coexist.

The next CR-005 should consolidate the relationships introduced across CR-002, CR-003 and CR-004 into one coherent relationship and composition model. It should resolve cardinalities, ownership, references, constraints, loop boundaries and multi-loop coordination rather than simply adding more relationship names.