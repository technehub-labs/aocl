> **Status:** Proposed · **Drafted:** 2026-11-22 — the Logical Simulation Engine: the first conforming implementation of the AOCL-CR-010 execution contract — conformance-gated interpretation of a BehavioralSpecification (CR-006) under a SimulationScenario (CR-009) with runtime visibility enforcement · Carries the CR-010 EXE rules as its implementation contract; defines engine-conformance rules LSE-001..022.

---

# AOCL-CR-011 — Establish the Logical Simulation Engine

**CR ID:** AOCL-CR-011\
**Title:** Establish the Logical Simulation Engine\
**Programme:** AOCL Engineering Engine\
**Status:** Proposed\
**Priority:** High\
**Type:** Engine Implementation\
**Depends on:** AOCL-CR-001 through AOCL-CR-010

---

## 1. Executive Summary

This Change Request establishes the Logical Simulation Engine: a deterministic, technology-independent interpreter that executes a valid BehavioralSpecification under the conditions of a SimulationScenario through an ExecutionDefinition, producing a governed trace and SimulationEvidence.

CR-010 defined *what a conforming interpretation means* (EXE-001..040). CR-011 defines the *engine-conformance rules* — what a logical engine must do to be a conforming interpreter — and ships the reference implementation.

The logical engine executes the **logical dimension**: graph-faithful activation, condition routing across separated information channels, event scheduling and ordering, the dispatch chain, approval suspension, exception resolution and safe-state handling. It deliberately does **not** implement quantitative plant dynamics: numeric state-evolution fidelity is the State-Based Simulation Engine's domain (CR-012). The reference interpretation declares the minimal numeric semantics it needs (§8) and labels them non-normative.

## 2. Problem Statement

The Modeling stage produced five machine-readable models; CR-010 bound them into a runnable contract. What remained was an actual interpreter. Without one:

- The contract would remain untested — declared policies no engine has honored are aspirations, not semantics.
- The sim-canvas prototype (tools/sim_check.py, site/sim.js) would remain the only execution path — engine-embedded, informative, and outside the canonical models entirely.
- Cross-model integration (spec ↔ scenario ↔ control ↔ evidence) would never be exercised end to end.

## 3. Objectives

1. Implement the CR-010 contract for Logical and Hybrid modes.
2. Enforce conformance gating: refuse to execute artifacts that fail their native validators.
3. Enforce runtime information visibility (EXE-036) — the load-bearing rule.
4. Produce the seven trace record classes with temporal references.
5. Produce SimulationEvidence with declared run identity (VER-039).
6. Guarantee determinism from declared inputs (LSE seed discipline).
7. Terminate only through declared outcomes, honestly reporting incomplete runs.
8. Exercise the full example family end to end as the integration proof.

## 4. Scope

In scope: the logical engine, its conformance rules, its reference interpretation, run summaries and evidence emission. Out of scope: quantitative plant dynamics and numerical solvers (CR-012), trace format and replay infrastructure (CR-013), studio visualization (CR-015).

## 5. Engine-Conformance Rules

| ID | Requirement |
|---|---|
| LSE-001 | A conforming logical engine SHALL implement the CR-010 EXE contract for Logical/Hybrid mode. |
| LSE-002 | The engine SHALL refuse to execute any bound artifact that fails its native validator, reporting the findings. |
| LSE-003 | The engine SHALL verify the ExecutionDefinition's logical readiness before running. |
| LSE-004 | The engine SHALL maintain separated actual/observed/estimated channels (EXE-037). |
| LSE-005 | The engine SHALL initialize channels from the scenario's initial conditions by declared state class. |
| LSE-006 | The engine SHALL apply disturbances to the actual channel per declared profile semantics; a disturbance declared unknown to the Controller SHALL NOT update the controller-visible view. |
| LSE-007 | The engine SHALL evaluate conditions with an explicit channel route derived from the declared evaluation context, and SHALL record unevaluable conditions as unresolved — never silently defaulted. |
| LSE-008 | The engine SHALL activate graph-faithfully from the specification's declared entry, honoring synchronization declarations. |
| LSE-009 | The engine SHALL suspend execution on Approval elements and resolve them only via declared run inputs, declared grant/rejection branches, or the declared timeout with escalation. |
| LSE-010 | The engine SHALL emit the dispatch chain (Command, Acknowledgement, ExecutionStatus, Effect, Outcome) as distinct trace records in order. |
| LSE-011 | The engine SHALL resolve exceptions through the specification's declared handler paths; unhandled exceptions SHALL escalate per the execution definition. |
| LSE-012 | The engine SHALL record safe-state transitions with their verification status — a safe state is never implicitly verified. |
| LSE-013 | The engine SHALL terminate only via a declared termination outcome, a declared verification success, or declared bounds — recording incomplete terminations as such. |
| LSE-014 | The engine SHALL be deterministic: identical declared inputs (including seed) SHALL produce identical traces. |
| LSE-015 | The engine SHALL emit all seven trace record classes with temporal references. |
| LSE-016 | The engine SHALL emit SimulationEvidence carrying run identity, scenario reference, seed and engine version (VER-039), with SimulationTime origin. |
| LSE-017 | The engine SHALL bound per-element activation (declared bound) so every run terminates. |
| LSE-018 | The engine SHALL NOT claim quantitative fidelity; its numeric semantics are declared reference interpretations, non-normative pending CR-012. |
| LSE-019 | Run identity SHALL be a deterministic function of the declared inputs. |
| LSE-020 | The engine SHALL report verification-target evaluations in the run summary, distinguishing achieved, not-achieved and not-evaluated (SCN-040/043). |
| LSE-021 | Declared run inputs (approval resolutions, declared failure injections) SHALL be part of the deterministic input set and recorded in the run summary. |
| LSE-022 | The engine SHALL report elements not activated and conditions not evaluated as run findings. |

## 6. Conformance Profiles

Structural Gate (LSE-002/003) · Activation Fidelity (LSE-008) · Visibility (LSE-004..007) · Dispatch Honesty (LSE-010) · Governance (LSE-009/011/012) · Termination Honesty (LSE-013/017/020/022) · Determinism (LSE-014/019/021) · Evidence (LSE-015/016). A logical engine can conform on structure while failing visibility or governance; profiles are reported separately.

## 7. Reference Interpretation (declared, non-normative numerics — LSE-018)

The reference implementation declares the following minimal semantics, sufficient for logical conformance and explicitly **not** a plant model:

1. **Time.** Ticks; tick duration parsed from the ExecutionDefinition's time basis (e.g. "30 s service interval" → 30 s). Scenario event times in seconds map to ticks.
2. **Channels.** `actual`, `observed`, `estimated` variable maps. Initial conditions populate by state class; observed defaults to a t0 copy of actual where no Observed state is declared.
3. **Channel routing (EXE-036).** Condition evaluation contexts route the channel: contexts indicating controller-facing or observation evaluation resolve on `observed`; contexts indicating ground truth or actuality on `actual`; estimation contexts on `estimated`. Default: controller-facing (`observed`).
4. **Disturbances.** On their onset tick, applied to the effect variable in `actual`: percent magnitudes scale (`value × (1 + mag/100)`), absolute magnitudes add. A disturbance with `knownToController: false` never touches `observed` until an observation event copies it.
5. **Observations.** Observation-received events and Observation-stage activations copy `actual` → `observed` (sensors report at observation time).
6. **Conditions.** Built-in evaluator for Threshold/State conditions whose subject names a tracked variable (optionally `variable.attr`) and whose operator is governed; the comparison value may be numeric or a scenario parameter reference. Anything else is recorded unresolved and evaluates false.
7. **Dispatch and remediation.** An executed Action emits the five chain records. Its Effect restores the variables targeted by fired (unresolved) disturbances to their pre-disturbance actual values — the modeled *intent* of remediation in logical mode. Quantitative fidelity is CR-012's.
8. **Verification.** A Verification element succeeds when the controller-visible value of the goal variable (the control model's Controlled variable) satisfies the declared reference (scenario target parameter or Reference-role variable). Its textual conditions are recorded as evaluated-by-reference.
9. **Approvals.** A grant run-input selects the first authorization-conditioned outgoing branch in declared relationship order; rejection or timeout follows the escalation branch. Timeout windows parse from the declared timeout conditions (ISO durations) with a declared default.
10. **Bounds.** Per-element activation bound (default 8) and a maximum-tick bound (scenario horizon parameter or declared default) guarantee termination.

## 8. Migration and Compatibility

The sim-canvas engines (tools/sim_check.py, site/sim.js) remain the non-normative state-based prototypes; CR-012 addresses their formalization. This engine does not alter them. The canvas's implicit policies were already carried into a Draft ExecutionDefinition by CR-010 §19; CR-011 can execute that definition once its spec/scenario bindings are canonicalized.

## 9. Acceptance Criteria

1. The engine executes the full example family (spec + scenario + control + evidence under the reference ExecutionDefinition) end to end. 2. Conformance gating rejects invalid artifacts with findings. 3. The hidden-disturbance case proves EXE-036 at runtime (controller-visible branch decisions). 4. The dispatch chain appears as five ordered distinct records. 5. Approval suspension, timeout and escalation execute per declaration. 6. Safe states record verification status. 7. Two runs with identical inputs produce identical traces; run identity is input-derived. 8. All seven trace classes appear; unevaluated conditions and unactivated elements are reported. 9. SimulationEvidence carries run identity and SimulationTime origin. 10. No quantitative plant model is introduced.

## 10. Dependencies

| CR | Relationship |
|---|---|
| AOCL-CR-012 | State-Based Simulation Engine — owns quantitative semantics; consumes the same contract |
| AOCL-CR-013 | Trace and Replay — owns trace format; CR-011 emits the declared record classes |

**End of AOCL-CR-011**
