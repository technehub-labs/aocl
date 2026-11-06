# Architectural Review Input (Rev. 1) — Comprehensive Review of Concept, Principles and Engineering Foundation

> Reference input preceding AOCL-ARCH-001. Committed for provenance of the architectural decisions; image placeholders removed. Simulation corroboration of this review's expectations: [docs/simulation.md](../simulation.md) and [ADR-006](../decisions/adr-006-simulation-evidence-and-architecture-alignment.md).

# AOCL Comprehensive Review: Concept, Principles and Engineering Foundation

Repository: [technehub-labs/aocl](https://github.com/technehub-labs/aocl?utm_source=chatgpt.com)\
Review objective: Establish version update to improve sound conceptual and engineering foundation for modeling, governing, realizing and simulating autonomous operations through closed-loop systems.

This as an architectural review before treating the software enhancement exercise.

The distinction is important: a visual modeler, scoring engine and simulation canvas will only be valuable if the underlying closed-loop ontology, behavioral model and execution semantics are sufficiently rigorous. Otherwise, we risk building a visually attractive tool that cannot faithfully represent real operational behavior.

## 1. Initial assessment

The repository already establishes foundation. Its scope brings together three capabilities:

1. Assess: Evaluate closed-loop maturity across Goal Decisioning, Data Veracity and Feedback Intelligence, using L1–L5.
2. Model: Define closed loops in relation to processes, capabilities, systems and functions, with CLAM-aligned exports.
3. Realize: Apply an informative realization heuristic to examine the relationship between effort, complexity and realization.

It also has a Python implementation, versioned YAML models, JSON Schemas, a browser-based modeler, a ledger, and cross-language golden tests.&#x20;


GitHub

Promising foundation

However, my initial architectural concern is that these three capabilities are not yet necessarily three parts of one coherent engineering lifecycle.

They need to become connected stages of a single system:

Conceptual definition → Structural modeling → Behavioral specification → Simulation → Verification → Operational realization → Continuous improvement.

That should become the organizing principle for the next evolution of AOCL.

## 2. Review of the underlying concept

### 2.1 The central premise is correct, but needs stronger formalization

The framework document defines a closed loop as a self-regulating control system in which measured outputs feed back to influence subsequent inputs. It identifies five classical elements:

- Plant
- Sensor
- Controller
- Actuator
- Reference

It then extends the control problem into stabilization, optimization and adaptation.&#x20;


GitHub

Important distinction to formalize.

A closed loop is not simply a sequence of activities that eventually returns to its starting point. It is a governed feedback mechanism that uses observations of an operating system to determine and influence subsequent system behavior.

That distinction should be normative throughout AOCL.

Consider three different situations:

| Pattern                | What happens                                                                                                          | Is it a closed loop? |
| ---------------------- | --------------------------------------------------------------------------------------------------------------------- | -------------------- |
| Sequential automation  | A predefined sequence executes                                                                                        | No                   |
| Conditional automation | An action is selected using a condition                                                                               | Not necessarily      |
| Feedback control       | An observed state is evaluated against an intended state, and the resulting decision influences the controlled system | Yes                  |

A workflow can contain a closed loop, but a workflow is not inherently a closed loop.

Similarly, an autonomous agent can participate in a closed loop, but the presence of an AI agent does not establish closed-loop control.

### 2.2 The missing distinction: control architecture versus behavioral lifecycle

I would formalize AOCL around two complementary views.

View A — Structural control architecture

WHAT CONSTITUTES THE LOOP

Controlled System / Plant

Operational environment and state

Observation

Sensor / Monitor

Control

Analyze / Decide / Plan

Execution / Actuation

Changes to the controlled environment

New System State

Observed again to close the feedback path

View B — Behavioral lifecycle

HOW THE LOOP OPERATES

1. Intent and Reference — establish desired outcomes and operating constraints.
2. Observe and Monitor — establish the actual state.
3. Orient and Analyze — interpret observations and identify deviations.
4. Decide and Plan — determine the appropriate response.
5. Act and Execute — implement the selected intervention.
6. Verify and Evaluate — establish whether the intended effect occurred.
7. Learn and Adapt — update knowledge, policies or control strategies where authorized.

These views should not be confused or forced into one sequence.

The structural view defines the components and relationships that make feedback possible. The behavioral view defines the stages through which a loop progresses.

The distinction also allows us to model loops using different control architectures without forcing every implementation into one fixed workflow.

### 2.3 A proposed canonical behavioral model

I recommend formalizing seven behavioral stages as the default AOCL reference lifecycle.

| Stage       | Primary responsibility                                   | Principal output        |
| ----------- | -------------------------------------------------------- | ----------------------- |
| S1. Intent  | Define desired state, goals and constraints              | Reference specification |
| S2. Observe | Collect actual state and signals                         | Observation set         |
| S3. Analyze | Interpret state, context and deviation                   | Situation assessment    |
| S4. Decide  | Select a response under policies and constraints         | Decision record         |
| S5. Execute | Apply the selected intervention                          | Action record           |
| S6. Verify  | Evaluate actual results against expected results         | Verification evidence   |
| S7. Learn   | Improve knowledge and, where permitted, control behavior | Learning update         |

Recommended conceptual baseline

There are two important qualifications:

1. These are logical stages, not necessarily seven sequential software components. For example, analysis and decisioning can be combined in one controller.
2. Learning is not necessarily executed on every control cycle. It can operate on a slower supervisory loop.

The model should support branching, retries, escalation, exception handling, asynchronous execution and nested loops.

In particular, verification must not be treated as an optional reporting activity. An action being successfully executed does not mean its intended operational outcome was achieved.

This is one of the most important improvements I would make.

## 3. The maturity model: what should L1–L5 actually measure?

AOCL currently uses three maturity vectors:

- Goal Decisioning (GD)
- Data Veracity (DV)
- Feedback Intelligence (FI)

It applies a weakest-link rule to derive overall loop maturity.&#x20;


GitHub+1

I support the multidimensional approach. A single autonomy score would obscure important weaknesses.

However, we should be precise about what is being assessed.

Maturity is a property of a particular closed-loop implementation, not an inherent property of an enterprise, system or AI agent.

For example, a network might have highly automated resource optimization loops but relatively immature customer-experience loops.

### My proposed interpretation of the three vectors

| Vector | What it measures                 | Important question                                                    |
| ------ | -------------------------------- | --------------------------------------------------------------------- |
| GD     | Decision-making capability       | Can the loop determine an appropriate action within its authority?    |
| DV     | Observational integrity          | Can it reliably establish what is happening?                          |
| FI     | Feedback and learning capability | Can it establish the effects of its actions and improve its behavior? |

The three vectors should be independent assessment dimensions.

A loop with excellent decisioning but unreliable observations should not be classified as highly mature.

Likewise, a loop with excellent data and sophisticated decisioning but no outcome verification is not a genuinely mature closed loop.

### A critical refinement

I would distinguish three separate maturity concerns:

1. Control maturity: The ability to regulate the controlled system.
2. Decision maturity: The ability to select appropriate actions.
3. Learning maturity: The ability to improve control and decision behavior through evidence.

These can remain represented through the existing three vectors if their definitions and assessment criteria are tightened.

I would not introduce additional vectors until we establish that the existing three cannot adequately represent these concerns.

## 4. Decision models: OODA and MAPE-K need a clearer relationship to the lifecycle

The repository supports OODA, MAPE and CUSTOM decision models. It correctly recognizes that OODA and MAPE are complementary rather than competing approaches.&#x20;


GitHub

This is a good decision, but I see a modeling issue.

OODA and MAPE-K describe decision and control structures. They do not, by themselves, provide the entire operational lifecycle we need to simulate.

For example:

- MAPE has Monitor, Analyze, Plan and Execute.
- OODA has Observe, Orient, Decide and Act.
- Neither explicitly makes outcome verification a mandatory, separately identifiable stage.
- MAPE-K incorporates Knowledge as a shared resource, rather than simply another sequential execution step.

I recommend retaining both as supported decision models and introducing a separate behavioral lifecycle abstraction.

### Proposed mapping

| AOCL behavioral stage | OODA                                   | MAPE-K                                   |
| --------------------- | -------------------------------------- | ---------------------------------------- |
| Intent                | Reference / mission                    | Goals / policies                         |
| Observe               | Observe                                | Monitor                                  |
| Analyze               | Orient                                 | Analyze                                  |
| Decide                | Decide                                 | Plan                                     |
| Execute               | Act                                    | Execute                                  |
| Verify                | Post-action observation and evaluation | Post-execution monitoring and evaluation |
| Learn                 | Updated orientation and experience     | Knowledge updates                        |

This gives us a common behavioral foundation while allowing different controller architectures.

It also makes CUSTOM more meaningful: users can define alternative decision structures without losing the ability to map them to the canonical behavioral stages.

Recommendation: Decision models should be plug-in behavioral implementations of an AOCL control specification, not the definition of the closed loop itself.

## 5. What is missing from the current loop model?

The existing modeler supports registering processes, capabilities, systems and functions, assigning maturity and velocity, specifying decision models, defining goals and linking loops.&#x20;


GitHub

That is useful for loop inventory and architectural organization.

But there is a considerable difference between a loop registry and an executable behavioral model.

I would introduce the following conceptual model.

Proposed AOCL Closed-Loop Model

1\. Loop Identity and Context

Identity, description, owner, scope, controlled entity, operational context, related capabilities and processes.

2\. Intent and Reference Model

Goals, target states, KPIs, constraints, policies, invariants and acceptable operating boundaries.

3\. Control Architecture

Plant, sensors, controller, actuators, knowledge resources and external dependencies.

4\. Behavioral Specification

Stages, activities, decisions, conditions, transitions, branches, retries, exceptions and feedback paths.

5\. Execution and Governance

Decision rights, human intervention, authorization, action execution, safety guards and lifecycle state.

6\. Verification and Evidence

Expected versus actual outcomes, verification rules, provenance, audit records and evidence quality.

7\. Learning and Adaptation

Knowledge updates, policy evolution, controller improvement, model recalibration and change authorization.

These are proposed model aspects, not seven new maturity dimensions.

A particularly important point: these aspects should be independently modeled and related through explicit references.

For example, an actuator should not simply be a text field containing an API endpoint. It should be a modeled component with:

- An identity and type.
- An operational interface.
- Permitted actions.
- Input and output contracts.
- Preconditions and postconditions.
- Failure behavior.
- Authorization requirements.
- Expected effects on the plant.

The same principle applies to sensors, decision mechanisms, verification rules and knowledge resources.

This is what will make the model useful beyond documentation.

## 6. The realization model needs a carefully controlled role

AOCL includes the heuristic:

\\[ R=\sqrt{E^2+(C\cdot V_d)^2} \\]

Where:

- \\(E\\) = Experience
- \\(C\\) = Complexity
- \\(V_d\\) = Data Veracity

The repository appropriately labels this model informative rather than normative and explicitly excludes its use for contractual commitments or certification.&#x20;


GitHub

I recommend preserving that distinction.

There are, however, three things to address.

First: realization is not behavioral performance.

A loop can have high estimated realization potential but still exhibit poor operational performance.

Second: realization is not maturity.

A high realization score should not automatically elevate a loop's L1–L5 classification.

Third: realization is not simulation.

The heuristic cannot predict how a loop will behave under disturbances, delayed observations, actuator failures, conflicting goals or unstable feedback.

I would therefore separate the following outputs:

| Concern       | Measurement                                          |
| ------------- | ---------------------------------------------------- |
| Maturity      | GD, DV and FI assessment                             |
| Realization   | Informative realization heuristic                    |
| Performance   | Actual operational KPI results                       |
| Stability     | Control-system response and convergence              |
| Reliability   | Successful operation under failures and disturbances |
| Safety        | Constraint compliance and risk exposure              |
| Effectiveness | Verified achievement of intended outcomes            |

This separation is essential to avoid creating a misleading composite score.

## 7. The most important engineering evolution: a real behavioral simulation model

This is where I think AOCL has the opportunity to become substantially more valuable.

The current documentation describes a visual modeler that places loops on entities, edits their attributes, links loops and updates portfolio analytics. Its existing export formats support YAML, CLAM payloads and a ledger.&#x20;


GitHub+1

That is a good modeling foundation, but the next evolution should be a proper simulation environment.

### 7.1 What I would expect the canvas to support

9

The canvas should support the actual engineering objects, not merely visual representations of loop records.

I would divide the workspace into four interacting areas:

## AOCL Model & Simulation Studio

Modeling palette

Components

Plant

Sensor

Controller

Actuator

Goal

Policy

Decision

Verification

Knowledge

Behavior canvas

Model

Reference / Intent

Observe

Analyze

Decide → Execute

Verify → Learn

Conceptual workspace only. The production canvas should allow free arrangement, connections, branching and feedback routing.

Properties inspector

Selected object, configuration, contracts and constraints

Simulation monitor

State, events, metrics, execution traces and failures

Simulation controls

Run · Pause · Step · Reset · Scenario selection · Speed control

### 7.2 Simulation must operate on a real state model

A simulation engine should not simply animate nodes and connections.

It must maintain an internal representation of the operating environment.

At minimum:

| Simulation concern | Required behavior                                       |
| ------------------ | ------------------------------------------------------- |
| Plant state        | Maintain the current state of the controlled system     |
| Observations       | Generate sensor measurements from plant state           |
| Disturbances       | Introduce external events and environmental changes     |
| Controller         | Evaluate observations against goals and constraints     |
| Decisioning        | Select an appropriate control action                    |
| Actuation          | Apply changes to the simulated plant                    |
| Feedback           | Return the resulting state to the observation mechanism |
| Verification       | Compare expected and actual results                     |
| Learning           | Update permitted knowledge or model parameters          |
| History            | Record events, state transitions and execution traces   |

The distinction between actual plant state and observed sensor state is especially important.

For example, a controller may receive delayed or inaccurate telemetry. If the simulation simply passes the current plant state directly into the controller, it will conceal one of the most important sources of operational failure.

### 7.3 Simulation needs multiple levels of fidelity

I would not start by building a sophisticated physics or network simulator.

Instead, establish three simulation modes.

L1

Logical simulation

Discrete stages, conditions, branches, transitions, retries and exception handling.

First implementation target.

L2

State-based simulation

Plant state, sensor readings, control actions, disturbances, time delays, thresholds and measurable outcomes.

The foundation for realistic control behavior.

L3

Advanced simulation

Multiple interacting loops, dynamic system behavior, stochastic events, predictive control, optimization and digital-twin integration.

An advanced extension, not a prerequisite for usability.

This approach avoids making the initial implementation unnecessarily complex while creating a credible path towards more sophisticated simulation.

## 8. Engineering principles that should govern AOCL

I recommend establishing the following as normative design principles before expanding the codebase.

| ID       | Principle                   | Engineering implication                                                          |
| -------- | --------------------------- | -------------------------------------------------------------------------------- |
| AOCL-P01 | Loop Primacy                | Closed loops are first-class modeled entities, not merely workflow attributes.   |
| AOCL-P02 | Intent Grounding            | Every loop must have explicit intent, goals and operating constraints.           |
| AOCL-P03 | Observable State            | The controlled system and its observable state must be distinguishable.          |
| AOCL-P04 | Explicit Feedback           | Feedback paths must be explicitly modeled and validated.                         |
| AOCL-P05 | Behavioral Completeness     | Decisions, actions, transitions and verification must be specified.              |
| AOCL-P06 | Bounded Autonomy            | Every autonomous action must operate within declared authority and constraints.  |
| AOCL-P07 | Evidence-Based Verification | Operational outcomes must be verified using defined evidence.                    |
| AOCL-P08 | Controlled Adaptation       | Learning must be governed, traceable and reversible where appropriate.           |
| AOCL-P09 | Simulation Fidelity         | Simulation behavior must derive from the model, not from visual animation.       |
| AOCL-P10 | Interoperability            | Models must have stable identifiers, schemas and explicit integration contracts. |
| AOCL-P11 | Composability               | Loops must support hierarchical, coordinated and interdependent arrangements.    |
| AOCL-P12 | Reproducibility             | Simulation scenarios and results must be reproducible from versioned inputs.     |

These principles should govern the metamodel, schema, validation engine, visual modeler, simulation engine and exports.

## 9. Important architectural decisions

There are several decisions I would make now rather than allowing them to emerge accidentally during implementation.

### 9.1 AOCL versus CLAM

The repository describes AOCL as consuming CLAM's format and exporting provisioning payloads. CLAM remains responsible for the managed closed-loop service and lifecycle.&#x20;


GitHub

I would preserve this separation.

| Responsibility                   | AOCL                 | CLAM                             |
| -------------------------------- | -------------------- | -------------------------------- |
| Conceptual closed-loop framework | Primary              | Consumer                         |
| Maturity assessment              | Primary              | Not primary                      |
| Behavioral modeling              | Primary              | Managed representation           |
| Simulation                       | Primary              | Execution/management integration |
| Provisioning                     | Export               | Primary                          |
| Operational lifecycle management | Model and assess     | Primary                          |
| Operational evidence             | Analyze and evaluate | Collect/manage as supported      |

AOCL should become the engineering environment for designing and evaluating closed loops, while CLAM manages their operational lifecycle.

We should not duplicate CLAM's service implementation inside AOCL.

### 9.2 AOCL versus the wider OpenDEA ecosystem

There is also an opportunity to strengthen alignment with the enterprise architecture foundations.

AOCL should be capable of referencing:

- Business and operational capabilities.
- Business processes and activities.
- Systems and functions.
- Information and data entities.
- Resources and services.
- Goals, outcomes and metrics.

These should be references to governed enterprise entities where available, not duplicated definitions.

This is particularly important because a closed loop usually operates across multiple architectural entities.

For example, a loop might realize an operational capability, execute through a process, monitor several systems and contribute to a business outcome.

### 9.3 Separate the model from its execution implementation

I recommend three distinct layers:

AOCL Domain Model

Canonical concepts, metamodel, behavioral stages, relationships, constraints and schemas.

AOCL Engineering Engine

Model validation, assessment, execution semantics, simulation, scenario management and evidence generation.

AOCL Studio and Integrations

Visual modeling, simulation canvas, analytics, CLI, YAML/JSON interchange and CLAM integration.

This architecture also allows future alternative interfaces without changing the underlying domain model.

## 10. What a realistic AOCL use case should look like

Before building anything, we should test the proposed conceptual model against a realistic operational example.

I suggest starting with a network service assurance loop.


[ciena.com](https://www.ciena.com/insights/articles/Network-heal-thyself-with-analytics-and-AI.html?utm_source=chatgpt.com)

Scenario: Network Service Assurance

Desired outcome: Maintain network service latency within an agreed operational threshold.

| Component      | Example                                       |
| -------------- | --------------------------------------------- |
| Plant          | Network service                               |
| Reference      | Latency below 50 ms                           |
| Sensor         | Network telemetry                             |
| Controller     | Service assurance controller                  |
| Decision model | MAPE-K                                        |
| Actuator       | Traffic engineering API                       |
| Verification   | Post-remediation latency measurement          |
| Knowledge      | Historical incidents and remediation outcomes |

A simulation should be able to demonstrate:

1. Normal operating conditions.
2. A sudden increase in network latency.
3. Telemetry reporting the deviation.
4. Analysis identifying congestion.
5. A decision to reroute traffic.
6. Execution of the traffic-engineering action.
7. Verification that latency returns below the threshold.
8. A learning update recording the effectiveness of the intervention.

But we should also simulate failure cases:

- Sensor data is stale.
- The controller selects an inappropriate action.
- The actuator fails.
- The action succeeds but the target outcome is not achieved.
- Two loops issue conflicting actions.
- The system oscillates between two operating states.
- A human approval is required.
- A safety constraint prevents execution.

This is where the quality of the AOCL model will become apparent.

A simulation that only demonstrates the successful path is not sufficient.

## 11. Recommended repository improvement programme

I would organize the work into the following change-request sequence.

This is a proposed programme, not an assertion that these CRs already exist.

| Stage       | Proposed CR | Deliverable                                     |
| ----------- | ----------- | ----------------------------------------------- |
| Foundation  | AOCL-CR-001 | Conceptual framework and normative principles   |
| Foundation  | AOCL-CR-002 | Canonical closed-loop metamodel                 |
| Foundation  | AOCL-CR-003 | Behavioral lifecycle and stage definitions      |
| Foundation  | AOCL-CR-004 | Control architecture and component semantics    |
| Foundation  | AOCL-CR-005 | Relationships, constraints and loop composition |
| Modeling    | AOCL-CR-006 | Behavioral specification schema                 |
| Modeling    | AOCL-CR-007 | Control contracts and state-transition model    |
| Modeling    | AOCL-CR-008 | Verification and evidence model                 |
| Modeling    | AOCL-CR-009 | Scenario and disturbance model                  |
| Engine      | AOCL-CR-010 | Canonical execution semantics                   |
| Engine      | AOCL-CR-011 | Logical simulation engine                       |
| Engine      | AOCL-CR-012 | State-based simulation engine                   |
| Engine      | AOCL-CR-013 | Simulation trace and replay                     |
| Studio      | AOCL-CR-014 | Graph-based visual modeling canvas              |
| Studio      | AOCL-CR-015 | Simulation controls and runtime visualization   |
| Studio      | AOCL-CR-016 | Scenario management and comparison              |
| Integration | AOCL-CR-017 | CLAM integration enhancement                    |
| Integration | AOCL-CR-018 | OpenDEA entity references and interoperability  |

The existing assessment and realization capabilities should be preserved, but reviewed against the new conceptual foundation rather than unnecessarily rewritten.

### Proposed delivery gates

- Gate 1: Conceptual and semantic correctness.
- Gate 2: Complete machine-readable modeling.
- Gate 3: Executable behavioral semantics.
- Gate 4: Reproducible simulation.
- Gate 5: Usable visual engineering studio.
- Gate 6: Operational interoperability.

Each gate should have acceptance criteria, schemas, reference examples and automated tests.

## 12. My overall verdict

# AOCL has a worthwhile foundation, but needs to evolve beyond loop assessment and registration.

The most important opportunity is to establish AOCL as a genuine closed-loop engineering environment.

| Existing strength        | Required evolution                                       |
| ------------------------ | -------------------------------------------------------- |
| Maturity assessment      | Evidence-backed maturity assessment                      |
| Loop registry            | Canonical behavioral metamodel                           |
| Decision-model selection | Explicit behavioral semantics                            |
| CLAM-aligned exports     | Complete model lifecycle interoperability                |
| Visual loop placement    | Graph-based engineering canvas                           |
| Portfolio analytics      | Executable simulation and performance analysis           |
| Realization heuristic    | Separate realization, performance and stability analysis |

Recommended strategic positioning

AOCL should be the engineering framework and environment through which closed loops are specified, assessed, composed, simulated, verified and prepared for operational realization.

## 13. What I would settle before drafting the first CR

There are three architectural decisions worth establishing explicitly.

Decision 1 — AOCL's primary identity

Closed-loop assessment and management framework

Closed-loop engineering and realization framework

End-to-end closed-loop engineering platform

Decision 2 — Simulation ambition

Logical process and transition simulation only

Logical and state-based simulation, extensible to advanced models

Full digital-twin-oriented simulation from the outset

Decision 3 — Behavioral lifecycle

Seven canonical stages, with flexible execution and mapping to OODA/MAPE-K

Use OODA and MAPE-K as the primary stage definitions

Fully configurable stages without a canonical lifecycle

Confirm architectural direction

My recommendation: Choose engineering framework, hybrid simulation and seven canonical behavioral stages.

That gives AOCL a sufficiently ambitious purpose without turning its first implementation into an unmanageable digital-twin project.

The next deliverable should be the AOCL Conceptual Architecture and Normative Foundation, resolving the ontology, control architecture, behavioral lifecycle, maturity boundaries, simulation semantics and CLAM relationship before we draft AOCL-CR-001.

I would treat that as an investigation and architecture-baselining exercise first, with no repository changes until the conceptual decisions are settled.