# AOCL-CR-003 — Establish the Canonical Behavioral Lifecycle Metamodel

> **Status:** Proposed · **Queued:** 2026-11-07 (third deliverable of the foundation tranche, after CR-002). Drafted from the architectural review; carries the review's four pre-approval checks (stage cardinality, graph termination, event/time semantics, verification independence).

---

This establishes the behavioral semantics of a closed loop: what each of the seven canonical stages means, what it consumes and produces, how stages relate, and how execution can branch, repeat, run asynchronously or escalate.

The key architectural rule is that the seven stages define canonical behavioral responsibilities, not a mandatory seven-step workflow. OODA and MAPE-K remain alternative decision architectures that can be mapped to this common lifecycle.

# AOCL-CR-003 — Establish the Canonical Behavioral Lifecycle Metamodel

| Field           | Value                                                                        |
| --------------- | ---------------------------------------------------------------------------- |
| Change ID       | AOCL-CR-003                                                                  |
| Title           | Establish the Canonical Behavioral Lifecycle Metamodel                       |
| Status          | Proposed                                                                     |
| Change Type     | Foundational / Metamodel                                                     |
| Priority        | Critical                                                                     |
| Target          | AOCL Domain Model                                                            |
| Depends On      | AOCL-CR-001, AOCL-CR-002                                                     |
| Related Changes | AOCL-CR-004, AOCL-CR-005, AOCL-CR-006, AOCL-CR-007, AOCL-CR-008, AOCL-CR-010 |

---

## 1. Executive Summary

This Change Request establishes a canonical behavioral lifecycle for specifying how an AOCL closed loop operates.

AOCL-CR-001 establishes the conceptual and normative foundation of AOCL. AOCL-CR-002 establishes the canonical closed-loop metamodel and its foundational entities. This CR introduces the behavioral layer that connects a loop's intent to its observations, analysis, decisions, interventions, verification and learning.

The proposed lifecycle consists of seven canonical behavioral stages:

1. **Intent** — establish desired outcomes, reference conditions and operating constraints.
2. **Observe** — acquire observations about the controlled system and its environment.
3. **Analyze** — interpret observations, context and deviations to establish the current situation.
4. **Decide** — select an authorized response consistent with intent, policies and constraints.
5. **Execute** — apply the selected intervention through an authorized execution mechanism.
6. **Verify** — evaluate whether the intervention produced the intended and acceptable result.
7. **Learn** — update governed knowledge and improve future behavior where authorized.

These stages are canonical behavioral responsibilities. They are not prescribed as a rigid, linear sequence, nor must every stage execute synchronously or independently.

The behavioral model must support:

- Conditional transitions and branching.
- Parallel and concurrent activities.
- Repeated control cycles.
- Event-triggered and asynchronous execution.
- Timeouts, retries and compensation.
- Escalation and human intervention.
- Nested and coordinated closed loops.
- Alternative decision architectures, including OODA and MAPE-K.
- Explicit verification and governed learning paths.

The result is a technology-independent behavioral metamodel that can be consumed by AOCL's validation, assessment, simulation, visual modeling and eventual execution environments.

## 2. Problem Statement

The conceptual foundation identifies seven behavioral stages, but a list of stages alone is insufficient to support engineering.

Without explicit behavioral semantics, different AOCL implementations could interpret the same stage differently. A visual modeler could represent a sequence that the simulation engine interprets differently. An export could omit important control-flow behavior. A decision architecture could become conflated with the lifecycle itself.

Several specific gaps must therefore be resolved.

### 2.1 Stage semantics are not yet normative

Each stage needs a defined responsibility, entry conditions, required inputs, expected outputs, completion conditions and failure behavior.

### 2.2 Behavioral progression cannot be assumed to be sequential

Real closed-loop systems do not necessarily execute one stage after another in a fixed order. They can respond to events, execute activities in parallel, repeat observations, suspend pending external conditions or escalate when authority is insufficient.

### 2.3 Decision architecture and behavioral lifecycle are different concerns

OODA, MAPE-K and other decision architectures organize decision-making responsibilities. They should not replace or redefine the canonical AOCL behavioral lifecycle.

### 2.4 Verification must be an explicit behavioral responsibility

Execution success is not equivalent to outcome success. An actuator may successfully issue a command while the controlled system fails to reach the intended state.

AOCL must therefore distinguish action execution, observed system response and verified outcome.

### 2.5 Learning requires explicit governance

Learning can update knowledge, improve analytical models or propose policy changes. It must not automatically acquire authority to change control policies, decision rights or permitted actions.

### 2.6 Simulation requires executable behavioral definitions

The logical and state-based simulation engines need an unambiguous model of behavioral progression, conditions, events, transitions and completion semantics.

## 3. Objectives

This CR shall:

1. Establish the seven canonical AOCL behavioral stages.
2. Define stage responsibilities and semantic boundaries.
3. Define a common behavioral element and behavioral graph model.
4. Establish explicit inputs, outputs and completion semantics.
5. Support flexible control flow rather than fixed sequential execution.
6. Define transition, branching, concurrency and repetition semantics.
7. Establish exception, retry, timeout and escalation behavior.
8. Define how OODA, MAPE-K and custom decision architectures map to the lifecycle.
9. Establish the distinction between execution completion and verified outcome achievement.
10. Establish governed learning and adaptation boundaries.
11. Provide the behavioral foundation for logical and state-based simulation.
12. Establish validation and conformance requirements.

## 4. Scope

### 4.1 In scope

- Canonical behavioral lifecycle.
- Behavioral stage definitions.
- Behavioral elements and stage instances.
- Behavioral graph and transition model.
- Entry, execution and completion conditions.
- Conditional and event-driven progression.
- Parallel and repeated execution.
- Exception, retry, timeout and escalation semantics.
- Decision architecture mappings.
- Behavioral traceability.
- Behavioral model validation requirements.
- Compatibility requirements for AOCL model representations.

### 4.2 Out of scope

The following are reserved for subsequent CRs:

| Change      | Responsibility                                                |
| ----------- | ------------------------------------------------------------- |
| AOCL-CR-004 | Structural control architecture and component semantics       |
| AOCL-CR-005 | Relationships, constraints and loop composition               |
| AOCL-CR-006 | Detailed behavioral specification schema                      |
| AOCL-CR-007 | Control contracts, state transitions and action semantics     |
| AOCL-CR-008 | Verification rules, evidence and outcome evaluation           |
| AOCL-CR-009 | Simulation scenarios, disturbances and scenario configuration |
| AOCL-CR-010 | Canonical execution semantics                                 |
| AOCL-CR-011 | Logical simulation engine                                     |
| AOCL-CR-012 | State-based simulation engine                                 |

This CR defines the behavioral metamodel and its normative requirements. It does not prescribe a specific programming language, runtime engine, workflow product or visual editor.

## 5. Normative Behavioral Lifecycle

### 5.1 Canonical stages

The following seven stages SHALL be recognized by conformant AOCL behavioral models.

| Stage ID | Stage   | Primary responsibility                                               | Principal output                   |
| -------- | ------- | -------------------------------------------------------------------- | ---------------------------------- |
| S1       | Intent  | Establish desired outcomes and operating boundaries                  | Intent and reference specification |
| S2       | Observe | Acquire information about actual system and environmental conditions | Observation set                    |
| S3       | Analyze | Interpret observations and establish the current situation           | Situation assessment               |
| S4       | Decide  | Select an appropriate response within authority and constraints      | Decision record                    |
| S5       | Execute | Apply an authorized intervention                                     | Execution record                   |
| S6       | Verify  | Determine whether expected results were achieved                     | Verification result and evidence   |
| S7       | Learn   | Improve governed knowledge and future behavioral effectiveness       | Learning record or proposed update |

The stages are semantic classifications. An implementation may combine multiple stage responsibilities in one component, provided their responsibilities remain identifiable in the behavioral model and execution evidence.

Likewise, one stage may be implemented through multiple activities or components.

### 5.2 S1 — Intent

**Purpose:** Establish what the closed loop is intended to achieve and the conditions under which it must operate.

Intent provides the reference against which observations, decisions, interventions and outcomes are evaluated.

Responsibilities:

- Identify the intended operational outcome.
- Establish one or more goals.
- Define target or reference conditions.
- Establish operating constraints and policies.
- Identify priorities and acceptable trade-offs.
- Establish success criteria.
- Identify applicable authority and governance boundaries.

Inputs:

- Closed-loop identity and operational context.
- Intent specification.
- Goals and reference conditions.
- Control constraints and policies.
- Applicable enterprise references.

Outputs:

- Intent context.
- Goal and reference-condition set.
- Applicable constraints.
- Success criteria.
- Traceable intent version.

Completion conditions:

- The applicable intent is identifiable.
- Relevant goals and constraints are available.
- The behavioral cycle has sufficient reference information to proceed.

An intent may remain stable across many control cycles. It does not have to be reconstructed or re-executed for every observation.

**Semantic boundary:** Intent defines desired outcomes and constraints. It does not prescribe the detailed decision algorithm or the actions required to achieve the outcomes.

### 5.3 S2 — Observe

**Purpose:** Acquire information about the actual state of the controlled system and relevant environmental conditions.

Responsibilities:

- Acquire sensor readings and operational events.
- Collect internal and external observations.
- Establish observation timestamps and provenance.
- Identify data quality and freshness.
- Associate observations with relevant state variables.
- Detect missing, conflicting or anomalous observations.
- Make observations available to downstream analysis.

Inputs:

- Observation requirements.
- Sensor and monitoring definitions.
- Controlled-system bindings.
- Operational context.
- Relevant reference conditions.

Outputs:

- Observation records.
- Observation timestamps.
- Source and provenance information.
- Data-quality indicators.
- Observation status.

Completion conditions:

- Required observations have been acquired, or
- The observation activity has reached an explicitly modeled incomplete, failed or timeout condition.

An observation must not be assumed to represent the current actual state without considering its timestamp, freshness, accuracy and provenance.

**Semantic boundary:** Observe acquires evidence. It does not independently establish the meaning of that evidence or select a control response.

### 5.4 S3 — Analyze

**Purpose:** Interpret observations in relation to intent, context, system state and applicable knowledge.

Responsibilities:

- Assess current operational conditions.
- Interpret observation quality and relevance.
- Identify deviations from reference conditions.
- Detect anomalies and relevant patterns.
- Determine potential causes or contributing conditions.
- Evaluate risks and possible consequences.
- Identify uncertainty and confidence.
- Establish whether further observation or analysis is required.

Inputs:

- Observation set.
- Intent and reference conditions.
- Operational context.
- Relevant knowledge.
- Historical evidence.
- Applicable policies and analytical models.

Outputs:

- Situation assessment.
- Deviation and anomaly findings.
- Risk and uncertainty information.
- Potential causal explanations.
- Analytical recommendations.

Completion conditions:

- The situation is sufficiently characterized for the next permitted behavioral action, or
- The model identifies an explicit need for further observation, additional analysis, escalation or termination.

**Semantic boundary:** Analyze establishes an interpretation of the situation. It does not itself authorize or execute an intervention.

### 5.5 S4 — Decide

**Purpose:** Select an appropriate response based on the analyzed situation, intent, authority and constraints.

Responsibilities:

- Identify candidate responses.
- Evaluate candidate actions against goals and constraints.
- Consider operational risk and expected effects.
- Resolve or escalate competing objectives.
- Select an appropriate response.
- Establish decision rationale.
- Determine whether human approval is required.
- Establish the authorization status of the selected response.

Inputs:

- Situation assessment.
- Intent and goals.
- Policies and control constraints.
- Available action definitions.
- Decision architecture.
- Authority and approval requirements.

Outputs:

- Decision record.
- Selected response or action plan.
- Decision rationale.
- Authorization requirement and status.
- Expected outcomes.
- Applicable execution conditions.

Completion conditions:

- A permitted decision has been selected and appropriately authorized, or
- The decision has been explicitly deferred, rejected, escalated or terminated.

A decision must not be treated as executable merely because it has been selected.

**Semantic boundary:** Decide selects and authorizes a response according to the applicable authority model. It does not perform the intervention.

### 5.6 S5 — Execute

**Purpose:** Apply the selected intervention to the controlled system or relevant operational environment.

Responsibilities:

- Validate execution preconditions.
- Confirm authorization.
- Invoke the appropriate actuator or execution mechanism.
- Apply the selected action.
- Record execution events and results.
- Detect action failures and partial completion.
- Handle timeout and retry conditions.
- Record actual execution effects where observable.

Inputs:

- Authorized decision.
- Action definition.
- Execution contract.
- Preconditions.
- Actuator or execution mechanism.
- Applicable safety and operational constraints.

Outputs:

- Execution record.
- Action status.
- Execution timestamps.
- Resulting observations or state changes where available.
- Failure and exception information.

Completion conditions:

- The action has completed successfully.
- The action has partially completed with an explicit status.
- The action has failed.
- Execution has been suspended or escalated.

Successful execution SHALL NOT imply successful achievement of the intended outcome.

**Semantic boundary:** Execute applies an intervention. It does not independently determine whether the resulting operational state satisfies intent.

### 5.7 S6 — Verify

**Purpose:** Establish whether the intervention produced the expected result and whether the resulting system state is acceptable.

Responsibilities:

- Obtain post-intervention observations.
- Compare actual results with expected results.
- Evaluate applicable success criteria.
- Assess constraint compliance.
- Identify residual deviations.
- Determine whether the outcome is achieved, partially achieved, not achieved or indeterminate.
- Produce traceable verification evidence.

Inputs:

- Original intent and success criteria.
- Decision and expected outcomes.
- Execution records.
- Post-execution observations.
- Verification rules.
- Applicable constraints.

Outputs:

- Verification result.
- Evidence references.
- Actual-versus-expected comparison.
- Residual deviation findings.
- Recommended next behavioral action.

Completion conditions:

- The result has been evaluated against the applicable criteria, or
- Verification has reached an explicit incomplete, failed or indeterminate condition.

Verification outcomes SHALL distinguish at least:

| Outcome           | Meaning                                                     |
| ----------------- | ----------------------------------------------------------- |
| Achieved          | Applicable success criteria are satisfied                   |
| PartiallyAchieved | Some, but not all, applicable criteria are satisfied        |
| NotAchieved       | The expected outcome was not achieved                       |
| Indeterminate     | Available evidence is insufficient to determine achievement |
| Invalidated       | The verification basis or evidence is invalid               |

**Semantic boundary:** Verify evaluates outcomes. It does not automatically alter the intent or authorize a new policy.

A verified failure may cause the behavioral graph to return to Observe, Analyze or Decide, depending on the modeled response.

### 5.8 S7 — Learn

**Purpose:** Use operational and verification evidence to improve governed knowledge and future loop effectiveness.

Responsibilities:

- Capture operational experience.
- Record the effectiveness of decisions and actions.
- Identify recurring patterns and systemic weaknesses.
- Update permitted knowledge resources.
- Propose improvements to analytical models or decision strategies.
- Identify potential policy or control improvements.
- Record learning provenance and confidence.
- Submit changes for required review and authorization.

Inputs:

- Verification results.
- Execution history.
- Observation and analysis records.
- Historical performance.
- Relevant operational knowledge.
- Learning and adaptation policies.

Outputs:

- Learning record.
- Knowledge update.
- Improvement recommendation.
- Model or policy change proposal.
- Evidence supporting the proposed change.

Completion conditions:

- Learning findings have been recorded.
- Any permitted knowledge updates have been applied.
- Changes requiring additional authority have been submitted for approval or deferred.

**Semantic boundary:** Learn improves knowledge and proposes or applies only those adaptations that are explicitly permitted. It does not inherently possess authority to modify operational policy, decision rights, safety constraints or execution permissions.

Learning may operate on a slower supervisory cycle and need not execute after every operational control cycle.

## 6. Behavioral Metamodel

### 6.1 Core behavioral entities

The following entities establish the conceptual behavioral model.

| Entity                  | Definition                                                  | Responsibility                                                        |
| ----------------------- | ----------------------------------------------------------- | --------------------------------------------------------------------- |
| BehavioralSpecification | A formal description of the behavior of a closed loop       | Defines the behavioral model                                          |
| BehavioralElement       | A modeled unit of behavioral responsibility or control flow | Provides the common behavioral abstraction                            |
| BehavioralStage         | A behavioral element classified against a canonical stage   | Represents Intent, Observe, Analyze, Decide, Execute, Verify or Learn |
| BehavioralActivity      | A specific activity performed within a behavioral stage     | Defines an operational unit of work                                   |
| BehavioralTransition    | A directed progression between behavioral elements          | Defines possible behavioral progression                               |
| TransitionCondition     | A condition governing whether a transition is eligible      | Defines conditional progression                                       |
| BehavioralEvent         | An occurrence that may initiate or influence behavior       | Supports event-driven execution                                       |
| BehavioralBranch        | A modeled alternative path from a behavioral element        | Supports conditional alternatives                                     |
| BehavioralJoin          | A synchronization point for multiple behavioral paths       | Supports parallel execution                                           |
| BehavioralLoop          | A repeated behavioral path or cycle                         | Supports repetition and feedback                                      |
| BehavioralException     | A defined exceptional behavioral condition                  | Supports failure handling                                             |
| BehavioralRetryPolicy   | A policy governing permitted repeated attempts              | Controls retry behavior                                               |
| BehavioralEscalation    | A defined transfer of responsibility or authority           | Supports human or supervisory intervention                            |
| BehavioralTrace         | A record of behavioral progression and execution evidence   | Supports audit and replay                                             |

These entities are technology-independent conceptual constructs. Their detailed machine-readable representation is reserved for AOCL-CR-006.

### 6.2 Behavioral element identity

Every independently modeled behavioral element SHALL have:

- A stable identifier.
- A behavioral element type.
- A name.
- A definition.
- A stage classification where applicable.
- A reference to its containing BehavioralSpecification.
- Applicable inputs and outputs.
- Entry and completion conditions where relevant.
- Applicable constraints and authority requirements.
- Provenance and version information.

An implementation may support additional attributes through governed extension mechanisms.

Identifiers SHALL not be derived solely from mutable names or display labels.

### 6.3 Behavioral graph

A BehavioralSpecification SHALL be representable as a directed behavioral graph.

The graph consists of:

- Behavioral elements as nodes.
- Behavioral transitions as directed edges.
- Conditions governing eligible transitions.
- Events that may initiate or influence progression.
- Branch and join structures where required.
- Explicit repetition and exception paths.

The graph represents permissible behavioral progression. It does not necessarily prescribe one predetermined execution path.

The model SHALL distinguish:

1. **Behavioral topology:** which transitions and paths are permitted.
2. **Behavioral conditions:** under what circumstances transitions are eligible.
3. **Execution history:** which paths were actually traversed during a particular run.

A simulation or execution trace must not be confused with the canonical behavioral specification.

### 6.4 Canonical stages versus behavioral activities

A canonical stage may contain one or more activities.

For example:

- Analyze may contain data validation, anomaly detection and causal analysis.
- Decide may contain candidate generation, policy evaluation and decision selection.
- Execute may contain precondition validation, actuator invocation and result recording.
- Verify may contain post-action observation, threshold evaluation and evidence recording.

An activity may be implemented by software, an agent, a human operator or a combination of these.

The implementation mechanism does not change the semantic responsibility of the stage.

## 7. Behavioral Progression Semantics

### 7.1 No mandatory linear sequence

The canonical stages SHALL NOT be interpreted as a mandatory sequential workflow.

The default conceptual relationship is:

Intent establishes the reference basis; Observe, Analyze, Decide, Execute and Verify support operational control; Learn supports governed improvement.

However, actual progression is defined by the behavioral graph and its conditions.

Examples include:

- Observe → Observe when additional measurements are required.
- Analyze → Observe when the evidence is insufficient.
- Decide → Analyze when a candidate response cannot be justified.
- Decide → Escalation when additional authorization is required.
- Execute → Execute when a permitted retry is necessary.
- Execute → Verify when the intervention has completed.
- Verify → Observe when further measurements are needed.
- Verify → Analyze when the result is not as expected.
- Verify → Learn when evidence is sufficient for a learning activity.
- Learn → Intent or Analyze when an approved change requires a new reference or analytical context.

These are illustrative transition patterns, not mandatory transitions.

### 7.2 Branching

A BehavioralSpecification SHALL support multiple alternative transitions from a behavioral element.

A branch may be governed by:

- A Boolean condition.
- A comparison against a reference condition.
- An event.
- A policy evaluation.
- An authorization result.
- A timeout.
- An explicit human decision.

Branch conditions must be identifiable and testable in the applicable execution or simulation environment.

### 7.3 Parallel execution

A BehavioralSpecification SHALL support independent activities executing concurrently where their dependencies and constraints permit.

The model must distinguish:

- Parallel activities.
- Independent alternative branches.
- Synchronization requirements.
- Join conditions.
- Failure propagation between concurrent paths.

A join may require all branches, a defined subset, or an explicitly modeled condition to complete.

The model must not assume that parallel activities complete in the order in which they were defined.

### 7.4 Repetition and feedback

A BehavioralSpecification SHALL support repeated execution of activities and stages.

Repetition may be triggered by:

- A periodic control cycle.
- A new observation.
- A state change.
- An unsuccessful verification.
- An external event.
- An explicit retry policy.

Repeated execution must be distinguishable from a new independent closed-loop instance.

The model must also support bounded repetition, including maximum attempts, time limits and termination conditions.

### 7.5 Event-driven and asynchronous behavior

Behavioral progression may be initiated or interrupted by asynchronous events.

Examples include:

- An alarm or threshold breach.
- A sensor availability event.
- A system failure.
- An external command.
- A human approval.
- A timeout.
- A change in operational context.

The behavioral model must identify event types and their permitted effects on progression.

Events may trigger a new behavioral path, suspend an existing path or cause escalation. They must not implicitly bypass authorization or safety constraints.

### 7.6 Exception handling

Exceptional conditions SHALL be modeled explicitly where they materially affect behavioral correctness.

Examples include:

- Missing observations.
- Invalid or stale data.
- Analysis failure.
- Conflicting objectives.
- Decision authorization failure.
- Actuator failure.
- Partial execution.
- Verification failure.
- Learning update rejection.

An exception definition should identify its detection condition, applicable response, permitted recovery behavior and termination or escalation path.

### 7.7 Retry and compensation

Retries SHALL be governed by an explicit retry policy.

A retry policy should define:

- Eligible failure conditions.
- Maximum attempts or bounded retry conditions.
- Retry delay or scheduling rule where applicable.
- Whether the action is safe to repeat.
- Whether an action requires compensation before retry.
- Escalation behavior when retries are exhausted.

Compensation is not automatically equivalent to rollback. The model must permit domain-specific compensating actions where the original action cannot be reversed.

Detailed action contracts and compensation semantics are reserved for AOCL-CR-007.

### 7.8 Escalation and human intervention

A BehavioralSpecification SHALL support escalation to a human or supervisory authority.

Escalation may be required when:

- The selected action exceeds the controller's authority.
- A policy requires human approval.
- Confidence or evidence quality falls below an accepted threshold.
- Constraints conflict.
- A safety condition is breached.
- Repeated execution failures occur.
- The system enters an explicitly defined exceptional state.

The model should identify the escalation target or authority role, the reason, the information required for resolution and the conditions for resumption.

## 8. Decision Architecture Mapping

### 8.1 Separation of concerns

The AOCL behavioral lifecycle and a decision architecture are distinct model concerns.

The behavioral lifecycle defines the canonical responsibilities of a closed loop.

A decision architecture defines how a controller organizes and performs selected decision-making responsibilities.

Decision architectures SHALL be represented as mappings or implementations within the behavioral specification. They SHALL NOT redefine the canonical stage vocabulary.

### 8.2 OODA mapping

OODA SHALL be supported as an alternative decision architecture.

| AOCL stage | OODA responsibility                    | Mapping                              |
| ---------- | -------------------------------------- | ------------------------------------ |
| Intent     | Mission and reference                  | Context and desired outcomes         |
| Observe    | Observe                                | Direct mapping                       |
| Analyze    | Orient                                 | Interpretation and contextualization |
| Decide     | Decide                                 | Direct mapping                       |
| Execute    | Act                                    | Direct mapping                       |
| Verify     | Post-action observation and evaluation | Explicit AOCL extension              |
| Learn      | Experience and updated orientation     | Explicit AOCL extension              |

OODA may combine or internalize responsibilities that AOCL represents separately. The mapping must preserve those responsibilities without requiring the OODA implementation to expose seven separate software components.

### 8.3 MAPE-K mapping

MAPE-K SHALL be supported as an alternative decision architecture.

| AOCL stage | MAPE-K responsibility                    | Mapping                                        |
| ---------- | ---------------------------------------- | ---------------------------------------------- |
| Intent     | Goals and policies                       | Context and desired outcomes                   |
| Observe    | Monitor                                  | Direct mapping                                 |
| Analyze    | Analyze                                  | Direct mapping                                 |
| Decide     | Plan                                     | Direct mapping                                 |
| Execute    | Execute                                  | Direct mapping                                 |
| Verify     | Post-execution monitoring and evaluation | Explicit AOCL responsibility                   |
| Learn      | Knowledge updates                        | Shared knowledge and adaptation responsibility |

Knowledge in MAPE-K is a shared resource supporting the Monitor, Analyze, Plan and Execute functions. It should not be treated as a mandatory sequential stage.

### 8.4 Custom decision architectures

Custom decision architectures SHALL be supported.

A custom architecture must:

- Identify its decision-making components.
- Define their responsibilities.
- Map relevant responsibilities to canonical AOCL stages.
- Identify inputs and outputs.
- Define applicable control-flow relationships.
- Preserve authority and constraint requirements.
- Provide sufficient mapping for validation and simulation.

A custom architecture may combine multiple canonical responsibilities, but it must not silently omit required behavioral responsibilities.

### 8.5 Decision architecture conformance

A decision architecture mapping does not automatically establish behavioral completeness.

A model must still demonstrate how it handles:

- Intent and reference conditions.
- Observation.
- Situation interpretation.
- Decision selection.
- Authorized execution.
- Outcome verification.
- Governed learning where applicable.

The absence of a dedicated component for a stage is not necessarily a conformance failure if the responsibility is explicitly realized elsewhere.

## 9. Behavioral State and Execution Status

The behavioral specification defines possible progression. A particular execution instance records its actual state.

The model SHALL distinguish specification lifecycle from execution status.

### 9.1 Behavioral specification lifecycle

Proposed lifecycle values:

- Draft
- InReview
- Approved
- Deprecated
- Retired

These describe the governance status of the behavioral specification.

### 9.2 Behavioral execution status

Proposed execution statuses:

- NotStarted
- Ready
- Active
- Waiting
- Suspended
- Completed
- Failed
- Aborted
- Escalated

These describe a particular behavioral execution instance.

### 9.3 Stage execution status

A behavioral stage instance may use:

- Pending
- Ready
- Active
- Waiting
- Completed
- Failed
- Skipped
- Cancelled
- Suspended

A skipped stage must have an explicit reason and must not imply that its responsibility has been fulfilled.

The status model must permit multiple stage instances to be active or waiting concurrently.

### 9.4 Execution history

Every execution instance SHALL maintain a trace sufficient to identify:

- Behavioral specification and version.
- Execution instance identifier.
- Stage and activity instances.
- Triggering events.
- Transition decisions.
- Evaluated conditions.
- Timestamps.
- Decisions and authorization outcomes.
- Execution results.
- Verification outcomes.
- Exceptions and escalations.
- Relevant evidence references.

Detailed trace serialization and replay requirements are reserved for AOCL-CR-013.

## 10. Behavioral Governance and Safety Requirements

The behavioral model SHALL preserve the following principles.

### 10.1 Authority is explicit

No transition into an action execution path may implicitly grant authority to perform the action.

### 10.2 Constraints remain effective across stages

Safety, regulatory, operational and other applicable constraints must remain effective throughout behavioral progression.

### 10.3 Uncertainty is represented

The behavioral model must permit incomplete, conflicting or uncertain observations and analytical conclusions.

It must not require every analysis to produce a definitive result.

### 10.4 Verification is independent of execution success

A successful execution status must not be treated as proof that the intended operational outcome has been achieved.

### 10.5 Learning is governed

Learning outputs must distinguish between:

- Knowledge updates that are already authorized.
- Improvement recommendations.
- Proposed model changes.
- Proposed policy changes.
- Changes requiring approval.

### 10.6 Failure behavior is explicit

A behavioral model must identify how relevant failures are handled. Unspecified failure paths must not silently be interpreted as successful completion.

### 10.7 Bounded execution is supported

Retries, repeated cycles and event-driven execution must have appropriate bounds or explicit termination conditions to prevent uncontrolled execution.

## 11. Illustrative Behavioral Specification

The following example illustrates a network service assurance loop. It is conceptual YAML, not the normative AOCL-CR-006 schema.

```
behavioralSpecification:
  id: aocl:behavior/network-service-assurance
  name: Network Service Assurance Behavior
  version: 1.0.0
  lifecycleStatus: Draft

  canonicalStages:
    - Intent
    - Observe
    - Analyze
    - Decide
    - Execute
    - Verify
    - Learn

  entryPoint: observe-latency

  elements:
    - id: observe-latency
      type: BehavioralStage
      stage: Observe
      activity: Acquire service latency telemetry
      outputs:
        - latency-observation

    - id: analyze-latency
      type: BehavioralStage
      stage: Analyze
      activity: Evaluate latency against the service reference
      inputs:
        - latency-observation
      outputs:
        - latency-assessment

    - id: decide-response
      type: BehavioralStage
      stage: Decide
      activity: Select an authorized remediation
      inputs:
        - latency-assessment

    - id: execute-remediation
      type: BehavioralStage
      stage: Execute
      activity: Apply traffic engineering intervention

    - id: verify-outcome
      type: BehavioralStage
      stage: Verify
      activity: Evaluate post-intervention latency

    - id: record-learning
      type: BehavioralStage
      stage: Learn
      activity: Record remediation effectiveness

    - id: escalate
      type: BehavioralActivity
      name: Request human intervention

  transitions:
    - from: observe-latency
      to: analyze-latency
      condition: observation-valid

    - from: observe-latency
      to: escalate
      condition: observation-invalid

    - from: analyze-latency
      to: decide-response
      condition: remediation-required

    - from: analyze-latency
      to: observe-latency
      condition: additional-observation-required

    - from: decide-response
      to: execute-remediation
      condition: action-authorized

    - from: decide-response
      to: escalate
      condition: human-approval-required

    - from: execute-remediation
      to: verify-outcome
      condition: execution-completed

    - from: verify-outcome
      to: record-learning
      condition: outcome-evaluated

    - from: verify-outcome
      to: analyze-latency
      condition: outcome-not-achieved

    - from: record-learning
      to: observe-latency
      condition: next-control-cycle
```

This example demonstrates several important characteristics:

- The canonical stages are identifiable.
- The operational path is not a mandatory linear sequence.
- Invalid observations can cause escalation.
- Analysis can request additional observations.
- Decision authorization is distinct from decision selection.
- Verification can return control to analysis.
- Learning can feed into a subsequent control cycle.

The example does not define detailed transition expression syntax, actuator contracts, verification rules or runtime semantics. Those are assigned to subsequent CRs.

## 12. Metamodel Validation Requirements

The following requirements are normative acceptance targets for the behavioral metamodel.

| ID      | Requirement                                                                                                                 |
| ------- | --------------------------------------------------------------------------------------------------------------------------- |
| BLM-001 | Every BehavioralSpecification SHALL have a stable identifier, name and version.                                             |
| BLM-002 | Every BehavioralSpecification SHALL reference a valid ClosedLoop.                                                           |
| BLM-003 | A BehavioralSpecification SHALL recognize all seven canonical stage classifications.                                        |
| BLM-004 | Every modeled stage instance SHALL identify its canonical stage classification.                                             |
| BLM-005 | Behavioral elements SHALL have stable identifiers and defined semantic types.                                               |
| BLM-006 | A BehavioralSpecification SHALL define at least one valid entry point or event-driven initiation mechanism.                 |
| BLM-007 | Behavioral transitions SHALL reference valid source and target elements.                                                    |
| BLM-008 | Conditional transitions SHALL identify an evaluable condition or a governed condition reference.                            |
| BLM-009 | The model SHALL support multiple alternative transitions from a behavioral element.                                         |
| BLM-010 | The model SHALL support parallel execution and explicit synchronization semantics.                                          |
| BLM-011 | The model SHALL support repeated behavioral paths and bounded repetition.                                                   |
| BLM-012 | The model SHALL support asynchronous events and event-triggered progression.                                                |
| BLM-013 | Relevant exceptional conditions SHALL have explicit handling or escalation behavior.                                        |
| BLM-014 | Retry behavior SHALL be governed by an identifiable retry policy.                                                           |
| BLM-015 | The model SHALL distinguish decision selection from authorization.                                                          |
| BLM-016 | The model SHALL distinguish execution completion from outcome achievement.                                                  |
| BLM-017 | Verification outcomes SHALL support achieved, partially achieved, not achieved and indeterminate results.                   |
| BLM-018 | Learning behavior SHALL identify whether an update is authorized, proposed or awaiting approval.                            |
| BLM-019 | The model SHALL support OODA and MAPE-K mappings without redefining canonical stages.                                       |
| BLM-020 | Custom decision architectures SHALL provide mappings to applicable canonical behavioral responsibilities.                   |
| BLM-021 | Behavioral specification lifecycle SHALL be distinct from execution status.                                                 |
| BLM-022 | Execution status SHALL be distinct from individual stage execution status.                                                  |
| BLM-023 | The model SHALL support multiple active or waiting stage instances where concurrency is permitted.                          |
| BLM-024 | A skipped stage SHALL have an explicit reason and SHALL NOT imply fulfillment of its responsibility.                        |
| BLM-025 | The model SHALL preserve applicable authority, safety and operational constraints across behavioral transitions.            |
| BLM-026 | Behavioral execution traces SHALL be attributable to a specific behavioral specification version.                           |
| BLM-027 | The model SHALL distinguish behavioral topology from actual execution history.                                              |
| BLM-028 | Behavioral graph validation SHALL identify unreachable elements and invalid or unresolved references.                       |
| BLM-029 | Repeated and cyclic paths SHALL have explicit termination, bounding or supervisory conditions where required.               |
| BLM-030 | A conformant behavioral specification SHALL be interpretable independently of a particular visual editor or runtime engine. |

## 13. Conformance Model

AOCL should distinguish structural validity from behavioral completeness.

### 13.1 Structural conformance

A behavioral specification is structurally conformant when:

- Required entities and identifiers exist.
- Stage classifications are valid.
- Transitions reference valid elements.
- Conditions and event references are structurally valid.
- The graph satisfies applicable integrity rules.
- Specification and execution lifecycle concepts remain distinct.

### 13.2 Behavioral conformance

A behavioral specification is behaviorally conformant when:

- All required behavioral responsibilities are represented.
- The modeled progression is consistent with the intended loop behavior.
- Decision authority is explicit.
- Execution is governed by applicable constraints.
- Verification is independently represented.
- Relevant exception paths are addressed.
- Learning behavior respects adaptation governance.

### 13.3 Simulation readiness

A structurally and behaviorally conformant model is not automatically simulation-ready.

Simulation readiness additionally requires sufficient definitions for:

- Transition evaluation.
- Input and output resolution.
- State and event handling.
- Action effects.
- Timing behavior where relevant.
- Verification criteria.
- Failure and termination behavior.

Simulation readiness is therefore a separate validation outcome, not a synonym for metamodel conformance.

## 14. Implementation Requirements

The implementation arising from this CR SHALL:

1. Introduce canonical stage identifiers and definitions.
2. Provide a technology-independent representation of behavioral elements and transitions.
3. Validate behavioral graph integrity.
4. Support conditional branching and alternative paths.
5. Support parallel paths and synchronization definitions.
6. Support bounded cycles and retries.
7. Support event-driven progression.
8. Represent escalation and exception paths.
9. Preserve decision architecture mappings.
10. Distinguish specification lifecycle, execution status and stage status.
11. Preserve traceability to the originating ClosedLoop and model version.
12. Provide reference examples for OODA, MAPE-K and custom decision architectures.
13. Make the behavioral model consumable by both the logical and state-based simulation engines.
14. Keep behavioral semantics independent of the canvas implementation.
15. Provide machine-readable validation results.

The canonical representation SHALL be established before introducing a separate editor-specific representation.

## 15. Migration and Compatibility

The existing AOCL model representation may already contain decision model selections, goals, process and capability references, maturity information and other loop attributes.

Migration SHALL preserve existing information.

The implementation must:

- Preserve existing closed-loop identifiers.
- Preserve existing goals and reference information where available.
- Preserve decision model selections.
- Map existing OODA and MAPE selections to the appropriate decision architecture references.
- Avoid inventing behavioral activities or transitions where the source model does not provide them.
- Mark incomplete behavioral specifications as Draft or otherwise identify their incomplete status.
- Preserve existing maturity assessment records and their source model versions.
- Avoid interpreting existing decision model selection as proof of a complete behavioral specification.

Existing loop registrations should remain usable during the migration period.

A migration must not silently convert a registered loop into an approved or simulation-ready behavioral model.

## 16. Acceptance Criteria

AOCL-CR-003 shall be accepted when:

1. The seven canonical behavioral stages are formally defined.
2. Each stage has an explicit responsibility and semantic boundary.
3. Each stage has defined inputs, outputs and completion semantics.
4. The BehavioralSpecification and BehavioralElement concepts are established.
5. Behavioral progression is represented as a directed graph.
6. The model supports conditional branching.
7. The model supports parallel execution and synchronization.
8. The model supports repeated and cyclic behavior.
9. The model supports asynchronous events.
10. Exception, retry, timeout and escalation behavior can be represented.
11. Decision selection is distinct from action authorization.
12. Execution completion is distinct from verified outcome achievement.
13. Verification supports partial, failed and indeterminate outcomes.
14. Learning and adaptation are explicitly governed.
15. OODA and MAPE-K can be mapped to the canonical lifecycle.
16. Custom decision architectures can be represented without losing canonical behavioral responsibilities.
17. Specification lifecycle and execution status are distinct.
18. Behavioral topology is distinguishable from execution history.
19. Structural and behavioral conformance can be evaluated independently.
20. A reference behavioral model can pass the applicable validation rules.
21. An incomplete or invalid reference model produces identifiable validation findings.
22. The model can be consumed by logical and state-based simulation without dependence on a particular canvas implementation.

## 17. Dependencies and Subsequent Change Requests

This CR depends on:

- **AOCL-CR-001:** Conceptual and normative foundation.
- **AOCL-CR-002:** Canonical closed-loop metamodel.

It establishes the behavioral foundation for:

| CR          | Dependency relationship                                        |
| ----------- | -------------------------------------------------------------- |
| AOCL-CR-004 | Uses behavioral stages alongside structural control components |
| AOCL-CR-005 | Defines behavioral relationships within composed loops         |
| AOCL-CR-006 | Serializes behavioral specifications and graph elements        |
| AOCL-CR-007 | Defines action contracts and state-transition semantics        |
| AOCL-CR-008 | Defines verification and evidence contracts                    |
| AOCL-CR-009 | Supplies scenarios and events to behavioral models             |
| AOCL-CR-010 | Interprets behavioral progression during execution             |
| AOCL-CR-011 | Executes logical behavioral simulation                         |
| AOCL-CR-012 | Executes state-based behavioral simulation                     |
| AOCL-CR-013 | Records and replays behavioral execution traces                |

## 18. Design Decisions and Open Questions

The following decisions are proposed for approval as part of this CR.

### D-001 — Seven canonical stages

**Recommendation:** Adopt Intent, Observe, Analyze, Decide, Execute, Verify and Learn as the canonical AOCL behavioral stages.

Rationale: They provide a common semantic foundation without forcing every implementation into a single decision architecture.

### D-002 — Behavioral graph rather than fixed workflow

**Recommendation:** Represent behavioral progression as a directed graph with explicit conditions and events.

Rationale: A fixed sequence cannot adequately represent asynchronous, concurrent, repeated and exception-driven operational behavior.

### D-003 — Stage responsibilities may be combined

**Recommendation:** Permit one implementation component or activity to fulfill multiple stage responsibilities, provided the responsibilities remain identifiable.

Rationale: The metamodel should define semantics, not prescribe software component boundaries.

### D-004 — Verification is mandatory as a modeled responsibility

**Recommendation:** Require verification responsibility in every behaviorally complete closed-loop specification.

Rationale: An action without outcome evaluation does not establish that the intended result was achieved.

### D-005 — Learning is governed and may be supervisory

**Recommendation:** Permit learning to operate asynchronously or on a slower cycle, with explicit authorization boundaries.

Rationale: Knowledge improvement and operational control need not share the same execution frequency.

### D-006 — Decision architectures remain separate

**Recommendation:** Preserve OODA, MAPE-K and custom architectures as alternative implementations mapped to the canonical lifecycle.

Rationale: This prevents AOCL's lifecycle from becoming dependent on one control or decision methodology.

### D-007 — Simulation readiness is separate from conformance

**Recommendation:** Establish simulation readiness as a separate validation outcome.

Rationale: A valid behavioral graph may still lack state, timing, action-effect or verification definitions needed for simulation.

## 19. Risks and Mitigations

| Risk                                                    | Mitigation                                                                    |
| ------------------------------------------------------- | ----------------------------------------------------------------------------- |
| Seven stages become a rigid workflow                    | Normatively define stages as responsibilities, not mandatory sequential steps |
| Decision architectures are conflated with the lifecycle | Maintain explicit architecture-to-stage mappings                              |
| Execution success is mistaken for outcome success       | Require independent verification semantics                                    |
| Unbounded retries create unstable behavior              | Require retry bounds or explicit supervisory termination                      |
| Learning changes policies without authority             | Separate knowledge updates from governed policy changes                       |
| Parallel behavior becomes ambiguous                     | Require explicit dependencies and synchronization semantics                   |
| Canvas implementation becomes the de facto model        | Establish canonical behavioral representation before editor-specific behavior |
| Simulation behavior diverges from the model             | Require simulation to consume the canonical behavioral specification          |
| Legacy models are incorrectly promoted                  | Preserve incomplete status and avoid inferred behavioral definitions          |

## 20. Proposed Resolution

Approve AOCL-CR-003 as the normative foundation for the AOCL behavioral lifecycle metamodel.

Upon approval:

1. The seven canonical behavioral stages become the authoritative AOCL behavioral vocabulary.
2. Behavioral specifications are represented as flexible directed graphs.
3. Behavioral progression supports conditional, concurrent, repeated and event-driven execution.
4. OODA, MAPE-K and custom decision architectures remain separate and mappable.
5. Verification becomes an explicit behavioral responsibility.
6. Learning remains governed and does not automatically grant policy or execution authority.
7. Subsequent metamodel, schema, execution and simulation CRs must conform to this behavioral foundation.

**Next proposed change:** AOCL-CR-004 — Establish the Canonical Control Architecture Metamodel.

This will formalize the structural control components, including the controlled system (Plant), Sensors, Observations, Controller, Actuators and Knowledge, and define how those components participate in the seven-stage behavioral lifecycle.

## Architectural review before approval

I recommend carrying forward four points as explicit review checks rather than treating the draft as implementation-ready:

1. Stage cardinality: A behavioral specification should support multiple instances of a stage. For example, a loop may have multiple Observe activities and separate Verify activities.
2. Graph termination: Cyclic behavior needs explicit termination and supervisory conditions. A graph that is structurally valid can still be operationally non-terminating.
3. Event and time semantics: The graph defines permissible progression, but event ordering, timeouts, concurrency and scheduling need precise execution semantics in CR-010.
4. Verification independence: Verification should be capable of using evidence independent of the actuator's own success response. Otherwise, the model risks verifying command acceptance rather than the actual operational outcome.

Next in sequence: AOCL-CR-004, the canonical control architecture metamodel.