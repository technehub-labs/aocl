> **Status:** Proposed · **Baselined:** 2026-11-08 — canonical execution semantics — how a valid BehavioralSpecification and SimulationScenario are interpreted and executed; the architectural transition connecting the Modeling stage's machine-readable models (CR-002/006/007/008/009) into a coherent execution contract · Per the review's sequence: baseline CR-010 before either simulation engine (CR-011/012) is formalized · Carries forward the review's pre-approval observations (kept in-document as review checks).

---

# AOCL-CR-010 — Establish Canonical Execution Semantics

**CR ID:** AOCL-CR-010\
**Title:** Establish Canonical Execution Semantics\
**Programme:** AOCL Conceptual and Modeling Foundation\
**Status:** Proposed\
**Priority:** Critical\
**Type:** Metamodel and Normative Semantics\
**Depends on:** AOCL-CR-001 through AOCL-CR-009

---

## 1. Executive Summary

This Change Request establishes the canonical execution semantics for AOCL: the normative rules for how a valid BehavioralSpecification (CR-006) is interpreted and executed under the conditions defined by a SimulationScenario (CR-009), producing results evaluated through the verification model (CR-008), respecting the control semantics (CR-007), without redefining any domain meaning established by CR-001..009.

CR-010 is the architectural transition between the Modeling stage and the engine tranche. It defines:

1. The ExecutionInstance — a governed, versioned binding of specification, scenario, models and mode.
2. The execution lifecycle — distinct from model lifecycles and simulation-run status.
3. Behavioral element activation semantics over the behavioral graph.
4. Condition, guard and transition evaluation order.
5. Event handling and ordering resolution honoring scenario declarations.
6. Scheduling and time semantics.
7. Action dispatch and the result chain (command → acknowledgement → execution status → effect).
8. Human participation and approval-gate handling.
9. Exception propagation and failure dispositions.
10. Safe-state execution and verification.
11. Determinism and stochastic-source governance.
12. **Information visibility at runtime** — the enforcement mechanism for the scenario's controller-visibility declarations (CR-009 §11.5).
13. Execution trace obligations (the trace format itself remains CR-013's).
14. Runtime evidence obligations (origin classes and run identity per CR-008).

The canonical domain models remain the sole source of meaning. CR-010 defines interpretation; CR-011/012 define engines; CR-013 defines trace and replay.

## 2. Problem Statement

The Modeling stage established what a loop is specified to do (CR-006), what its control actions and transitions mean (CR-007), how behavior and outcomes are verified (CR-008), and under what conditions behavior is evaluated (CR-009). What none of them defines is how a specification is *interpreted* — the order of evaluation, what happens when branches are taken, how simultaneous events resolve, when execution suspends for an approval, what an engine must never show the simulated Controller.

Without canonical execution semantics:

- Each simulation engine would embed its own interpretation, and engine results would not be comparable.
- The scenario's information-visibility declarations (SCN-027, CR-009 §11.5) would have no runtime enforcement — the simulated Controller could silently receive the scenario's hidden ground truth.
- Determinism claims would be engine-private rather than governed.
- The distinction between a commanded state and an established state (AD-007-09) could be violated by the interpreter itself.
- The evidence produced by a run could not be traced to governed run identity.

A concrete violation class illustrates the risk: an engine that evaluates a branch condition using the scenario's Actual plant state where the behavioral specification's evaluation context names the Observed channel would invalidate every data-veracity experiment the simulation exists to run. CR-010 makes that class of error a conformance failure rather than an implementation accident.

## 3. Objectives

CR-010 SHALL:

1. Establish the ExecutionInstance as a first-class, versioned model artifact.
2. Define an execution lifecycle distinct from model, specification and scenario lifecycles.
3. Define behavioral element activation semantics that honor the behavioral graph (no implied sequence).
4. Define condition, guard and transition evaluation semantics and order.
5. Define event handling, ordering resolution and deterministic tie-breaking.
6. Define scheduling and time-basis semantics for tick-based and event-driven execution.
7. Define action dispatch and result handling preserving the CR-007 evidential chain.
8. Define approval-gate suspension and human-response handling.
9. Define exception propagation, handler resolution and retry budgets.
10. Define safe-state execution with mandatory verification.
11. Govern stochastic sources and require deterministic reproducibility from declared inputs.
12. Enforce scenario information-visibility declarations at runtime.
13. Define execution trace obligations (format deferred to CR-013).
14. Define runtime evidence obligations per CR-008.

## 4. Scope

### 4.1 In scope

ExecutionInstance, execution lifecycle and state, activation semantics, evaluation order, event handling, scheduling, dispatch, approval handling, exception propagation, safe-state execution, determinism, information visibility, trace obligations, runtime evidence obligations, validation and conformance.

### 4.2 Out of scope

| Concern | Owning CR |
|---|---|
| Logical simulation engine implementation | AOCL-CR-011 |
| State-based simulation engine implementation | AOCL-CR-012 |
| Trace format, recording and deterministic replay | AOCL-CR-013 |
| Studio visualization of running executions | AOCL-CR-015 |
| Numerical solvers and integration methods | Engine specifications |

CR-010 defines what a conforming interpretation means. It does not define software architecture, threading, or any particular engine implementation.

## 5. Normative Design Principles

| ID | Principle | Normative implication |
|---|---|---|
| AOCL-P27 | Semantic Conservation | Execution never redefines domain meaning established by CR-002..009. |
| AOCL-P28 | Graph-Faithful Activation | Activation follows the behavioral graph; no implied sequencing. |
| AOCL-P29 | Evaluation Order Determinism | Evaluation order is declared; ties resolve by declared rule, never accidentally. |
| AOCL-P30 | Visibility Discipline | The simulated Controller receives exactly the information the scenario declares visible to it. |
| AOCL-P31 | Channel Separation | Actual, observed and estimated state remain separate channels at runtime. |
| AOCL-P32 | Dispatch Honesty | Command, acknowledgement, execution status and effect remain distinct runtime records. |
| AOCL-P33 | Governed Randomness | All stochastic behavior flows through declared sources and seeds. |
| AOCL-P34 | Trace Sufficiency | An execution preserves enough information to explain, and within an engine version reproduce, every decision it made. |

## 6. Canonical ExecutionInstance

### 6.1 Definition

An **ExecutionInstance** is a governed, versioned definition binding one BehavioralSpecification, one SimulationScenario (or variant), the referenced control and evidence models, and one execution mode into a runnable interpretation.

### 6.2 Attributes

| Attribute | Description |
|---|---|
| executionId | Stable identifier (`urn:aocl:execution:<slug>`) |
| name, definition | Identity |
| version | Independent semver |
| lifecycleStatus | Draft / InReview / Approved / Deprecated / Retired |
| executionMode | Logical / StateBased / Hybrid |
| behavioralSpecRef + specVersion | The specification executed (CR-006) |
| scenarioRef + scenarioVersion | The conditions applied (CR-009) |
| controlModelRef, evidenceModelRef | CR-007/CR-008 bindings |
| timeBasis | Tick / WallClock / EventDriven with declared unit |
| activation | Entry policy and graph-walk semantics |
| conditionEvaluation | Context policy, freshness policy, delegated evaluations |
| transitionEvaluation | Guard order, authority checking, effect application |
| eventHandling | Ordering resolution per scenario ordering declarations |
| scheduling | Cycle policy per the loop's velocity |
| actionDispatch | Acknowledgement/status policies, result classification, retry policy |
| humanParticipation | Approval-gate policy, timeout and fallback handling |
| exceptionHandling | Handler resolution, unhandled policy, retry budgets |
| safeStateHandling | Authority and verification requirements |
| determinism | Seed policy and declared stochastic sources |
| informationVisibility | Channel policy and controller-visibility enforcement |
| trace | Required record classes and temporal obligations |
| evidence | Runtime evidence obligations |

### 6.3 Execution lifecycle

The execution lifecycle SHALL be distinct from every model lifecycle and from simulation-run status:

**Initialized → Ready → Running → {Suspended, WaitingApproval} → Terminated | Failed | Cancelled**

An Approved ExecutionInstance does not imply it has run, nor that any expected outcome was achieved (SCN-043 discipline carries to runtime).

## 7. Activation Semantics

Activation follows the behavioral graph:

1. Execution begins at the specification's declared entry elements, under its entry conditions.
2. An element becomes active when an incoming relationship fires: a FlowsTo progression, a satisfied BranchesTo condition, a Triggers event, a resolved Wait resume, a synchronization release, a repetition (RepeatsTo/ReturnsTo) under its governing condition, or an exception path.
3. No element is active by implication of stage order. The seven responsibilities are fulfilled through the graph, not a fixed pipeline.
4. Termination occurs when a TerminatesWith outcome fires, a declared termination condition holds, or the execution lifecycle terminates externally (cancellation).
5. Non-substantive elements (Event, Condition, Wait, Synchronization) participate in activation as declared by CR-006 §7.2–7.3.

## 8. Evaluation Semantics

**Conditions and guards** are evaluated in their declared evaluation context. Where evaluation is delegated, the responsible reference and expected result contract named by the specification are used (CR-006 §9.4, CTM §9.4). Evidence whose freshness fails the declared policy blocks dependent evaluation rather than silently proceeding (VER-020 discipline at runtime).

**Transitions** evaluate in a declared order: guard first, then authority (always checked against the CR-007 AuthorityDefinition — never inferred), then effects applied as declared deltas with postcondition kinds preserved (CTM-025). Transition outcomes use the governed CR-007 classifications.

**Information visibility (P30/P31).** Every evaluation names its channel: Actual, Observed, or Estimated. Where the scenario declares a disturbance or initial state not known to the Controller, evaluations whose context names the Controller-visible channel MUST resolve against the Controller-visible view, never the scenario ground truth. This is the runtime enforcement of SCN-027/AD-009-04 and is a conformance requirement of every mode.

## 9. Event Handling

Events enter a declared queue policy. Ordering resolution honors the scenario's per-event ordering declarations (SCN-033): Independent events may resolve in any declared deterministic order; Ordered events resolve in dependency order; Concurrent events are declared as simultaneously resolved; MutuallyExclusive events resolve exactly one; Conditional and Coordinated events resolve per their declared conditions. Where multiple events remain simultaneous, tie-breaking follows the declared deterministic rule (P29) — never accidental resolution order. Event dependencies block execution of dependents until their dependencies resolve (SCN-032).

## 10. Scheduling and Time

The time basis is declared (tick, wall-clock, or event-driven). Cycle-driven loops execute per their velocity declaration (CR-002 bindings). Timeouts evaluate against declared temporal conditions. A simulation mode without a declared time basis is non-conformant.

## 11. Action Dispatch and Results

Dispatch produces the CR-007 chain as distinct runtime records: Command (Instruction) → Acknowledgement (Receipt) → ExecutionStatus (ExecutionReport) → observed/estimated effect (Measurement/Inference) → verified outcome (VerifiedOutcome). An acknowledgement never advances state as if execution occurred; an execution report never establishes plant state; outcome evaluation requires outcome-level evidence (AD-007-09, VER-034/036 enforced by the interpreter itself). Retries occur only within declared budgets (BSS-015 discipline); there is no implicit retry.

## 12. Human Participation and Approvals

An Approval element suspends the execution path into WaitingApproval. Timeout, escalation and fallback follow the CR-006 HumanParticipation declaration. A resolved approval resumes the path under the governing authorization condition; a rejected approval follows its declared branch. The approval record is produced as AuthorizationEvidence (CR-008 §7.1).

## 13. Exception Propagation

An exception resolves through the specification's HandlesException path for the affected element, with the declared disposition. Unhandled exceptions follow the declared unhandled policy — escalate per the CR-007 failure dispositions; they are never silently absorbed. Critical unresolved exceptions (BSS-026) block execution readiness. Safe-state entry uses the pre-authorized protective authority and completes only with the declared verification (CTM-032 discipline at runtime).

## 14. Determinism

All stochastic behavior flows through declared sources with a declared seed policy (SCN-049 discipline). Given the same specification, scenario, model versions and seed, a conforming engine produces the same execution trace within its own engine version (P34); cross-engine numerical identity is not claimed (CR-009 §17.2 discipline).

## 15. Trace and Evidence Obligations

Every activation, condition evaluation outcome, transition evaluation, dispatch, approval resolution, exception disposition and safe-state transition is recorded with its temporal reference. The trace format, recording infrastructure and deterministic replay are CR-013's; CR-010 defines the obligatory record classes. Runtime evidence carries the execution's run identity and an origin class per CR-008 — SimulationEvidence for simulation modes, never represented as OperationalEvidence (AD-008-11).

## 16. Conformance Requirements

| ID | Requirement |
|---|---|
| EXE-001 | Every ExecutionInstance SHALL have a stable identifier. |
| EXE-002 | Every ExecutionInstance SHALL bind its BehavioralSpecification and exact version. |
| EXE-003 | Every ExecutionInstance SHALL bind its SimulationScenario and exact version. |
| EXE-004 | Every ExecutionInstance SHALL bind the referenced control and evidence models. |
| EXE-005 | Every ExecutionInstance SHALL declare its execution mode. |
| EXE-006 | The execution lifecycle SHALL be governed and distinct from model/scenario lifecycles and run status. |
| EXE-007 | Execution lifecycle transitions SHALL be recorded with temporal references. |
| EXE-008 | Activation SHALL follow the behavioral graph without implied sequencing. |
| EXE-009 | Activation SHALL honor declared conditions and guards. |
| EXE-010 | Execution SHALL begin at the specification's declared entry. |
| EXE-011 | Termination SHALL follow the specification's declared outcomes. |
| EXE-012 | Conditions SHALL be evaluated in their declared evaluation context. |
| EXE-013 | Delegated evaluations SHALL use the named responsible reference and result contract. |
| EXE-014 | Stale or insufficient evidence SHALL block dependent evaluation, not silently proceed. |
| EXE-015 | Transition guards SHALL be evaluated before effects are applied. |
| EXE-016 | Authority SHALL be checked at dispatch against the declared AuthorityDefinition. |
| EXE-017 | Effects SHALL be applied as declared deltas with postcondition kinds preserved. |
| EXE-018 | Transition outcomes SHALL use governed classifications. |
| EXE-019 | Event ordering SHALL honor the scenario's ordering declarations. |
| EXE-020 | Simultaneous events SHALL resolve by the declared deterministic tie-break. |
| EXE-021 | Event dependencies SHALL block dependents until resolved. |
| EXE-022 | The time basis SHALL be declared. |
| EXE-023 | Cycle-driven execution SHALL follow the loop's velocity declaration. |
| EXE-024 | Dispatch SHALL preserve the command → acknowledgement → execution-status → effect chain as distinct records. |
| EXE-025 | Action results SHALL use governed outcome classifications. |
| EXE-026 | Retries SHALL occur only within declared budgets. |
| EXE-027 | Approval elements SHALL suspend execution into WaitingApproval. |
| EXE-028 | Approval timeout, escalation and fallback SHALL follow the participation declaration. |
| EXE-029 | Exceptions SHALL resolve through declared handler paths. |
| EXE-030 | Unhandled exceptions SHALL follow the declared unhandled policy, never silent absorption. |
| EXE-031 | Critical unresolved exceptions SHALL block execution readiness. |
| EXE-032 | Safe-state entry SHALL use the pre-authorized protective mechanism. |
| EXE-033 | A safe state SHALL NOT be treated as established without its declared verification. |
| EXE-034 | All stochastic behavior SHALL flow through declared seeded sources. |
| EXE-035 | Same declared inputs SHALL yield the same trace within an engine version. |
| EXE-036 | Controller-visible evaluation SHALL resolve against the Controller-visible view per scenario declarations, never scenario ground truth. |
| EXE-037 | Actual, observed and estimated channels SHALL remain separate at runtime. |
| EXE-038 | Every activation, evaluation, dispatch, transition, approval and safe-state event SHALL be traceable with temporal references. |
| EXE-039 | Runtime evidence SHALL carry run identity and governed origin class. |
| EXE-040 | Execution semantics SHALL NOT redefine domain meaning established by CR-002..009. |

## 17. Conformance Profiles

| Profile | Purpose |
|---|---|
| Structural Conformance | Identity, bindings, versions, declared policies |
| Semantic Conformance | Evaluation, dispatch, exception and approval semantics |
| Determinism Conformance | Seeds, stochastic sources, tie-breaking, reproducibility claims |
| Safety Conformance | Authority checks, safe-state handling, unhandled-exception policy |
| Visibility Conformance | Channel separation and controller-visibility enforcement |
| Logical Engine Readiness | Sufficient declared semantics for a logical engine (CR-011) |
| State-Based Engine Readiness | Sufficient declared semantics for a state-based engine (CR-012) |

Structural conformance SHALL NOT imply engine readiness. Readiness is mode-specific and distinct.

## 18. Canonical Representation and Validation

The implementation SHALL provide a machine-readable ExecutionDefinition representation, JSON Schema structural validation, semantic validation of declared policies (native validator), reference examples for logical and state-based modes, version-aware import/export, and round-trip serialization tests. Structural validation alone is not semantic validation.

## 19. Migration and Compatibility

Migration SHALL preserve existing simulation-canvas semantics as declared execution policies where mappable (the canvas's level→policy behavior is an ExecutionInstance under test — the informative mapping), never silently promote engine-embedded behavior to Approved semantics, retain unresolved mappings as findings, and leave the sim_check/sim.js engines as non-normative prototypes pending CR-011/012.

## 20. Architectural Decisions

| Decision | Resolution |
|---|---|
| AD-010-01 | ExecutionInstance is a first-class governed artifact |
| AD-010-02 | Execution lifecycle is distinct from all model lifecycles and run status |
| AD-010-03 | Activation is graph-faithful; no stage ordering is implied |
| AD-010-04 | Evaluation order and tie-breaking are declared, never accidental |
| AD-010-05 | Controller visibility is enforced at runtime from scenario declarations |
| AD-010-06 | Channel separation (actual/observed/estimated) holds at runtime |
| AD-010-07 | The dispatch chain preserves CR-007 evidential distinctions |
| AD-010-08 | Approvals suspend execution; exceptions escalate per declaration |
| AD-010-09 | Determinism flows from declared seeded sources |
| AD-010-10 | Trace obligations are normative; trace format is CR-013's |
| AD-010-11 | Runtime evidence carries governed origin class and run identity |
| AD-010-12 | CR-010 consumes CR-002..009 without redefining their semantics |

## 21. Acceptance Criteria

1. ExecutionInstance established as first-class. 2. Execution lifecycle governed and distinct. 3. Graph-faithful activation defined. 4. Evaluation semantics and order defined. 5. Event ordering resolution defined. 6. Scheduling/time basis defined. 7. Dispatch chain preserved. 8. Approval suspension defined. 9. Exception propagation defined. 10. Safe-state execution defined. 11. Determinism governed. 12. Visibility enforcement defined. 13. Trace obligations defined. 14. Evidence obligations defined. 15. Profiles distinguish structural, semantic, determinism, safety, visibility and both engine readineses. 16. Machine-readable representation validated (schema + native validator). 17. Reference definitions for both modes. 18. Migration preserves canvas semantics without promotion. 19. No engine implementation introduced. 20. Existing AOCL capabilities unaffected.

## 22. Dependencies and Next Change Requests

| CR | Title | Relationship |
|---|---|---|
| AOCL-CR-011 | Logical Simulation Engine | Implements a conforming logical interpretation |
| AOCL-CR-012 | State-Based Simulation Engine | Implements a conforming state-based interpretation |
| AOCL-CR-013 | Simulation Trace and Replay | Owns trace format, recording, deterministic replay |

**End of AOCL-CR-010**

## Architectural assessment

CR-010 closes the gap the review flagged: the sim canvas and sim_check engine currently *are* undocumented execution semantics — engine-embedded interpretations with parity pins but no normative contract. This CR makes their implicit policies (seeded determinism, per-tick scheduling, HITL/HOTL/HOOTL suspension, playbook cancellation as exception resolution, policy downflow as event coordination) explicit, governable and checkable — while leaving them non-normative prototypes until CR-011/012 implement against the contract. The visibility rule (EXE-036) is the load-bearing addition: it is what makes the veracity experiments (DV 5→2, novel-mode gaps) *valid* — without runtime visibility enforcement, the controller could read ground truth and the whole evidence chain collapses.

The next change requests are AOCL-CR-011/012 — the engines, which implement this contract.
