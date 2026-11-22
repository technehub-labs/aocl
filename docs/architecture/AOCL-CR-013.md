> **Status:** Proposed · **Drafted:** 2026-11-22 — Simulation Trace and Replay: the canonical trace format for engine runs, trace integrity and identity rules, and deterministic replay verification · CR-010 declared the obligatory record classes; CR-013 owns their serialization, the trace envelope, and replay · Defines rules TRC-001..016.

---

# AOCL-CR-013 — Establish Simulation Trace and Replay

**CR ID:** AOCL-CR-013\
**Title:** Establish Simulation Trace and Replay\
**Programme:** AOCL Engineering Engine\
**Status:** Proposed\
**Priority:** High\
**Type:** Metamodel and Engine Implementation\
**Depends on:** AOCL-CR-001 through AOCL-CR-012

---

## 1. Executive Summary

This Change Request establishes the canonical trace model: the serialization format for engine execution traces, the integrity and identity rules that make a trace a governed artifact, and replay — the re-execution of a recorded run under its declared inputs with verification that the engine reproduces it.

CR-010 declared the obligatory trace record classes (Activation, ConditionEvaluation, TransitionEvaluation, Dispatch, ApprovalResolution, ExceptionDisposition, SafeStateTransition) and their temporal-reference obligation (EXE-038). CR-013 owns:

1. The ExecutionTrace envelope — run identity, model bindings, engine identity, declared inputs, termination.
2. Record serialization with governed classes, references, outcomes and channels.
3. Trace integrity rules (ordering, single-run scope, terminal completeness).
4. Deterministic replay and its verification semantics.
5. The relationship between traces, evidence records and run summaries.

## 2. Problem Statement

Both engines emit traces and input-derived run identities, but as engine-private JSON. Without a canonical trace model:

- A trace cannot be exchanged, validated, archived or compared across engines.
- Replay claims (CR-010 EXE-035, CR-009 §17.2) have no verification mechanism — determinism would remain an assertion, not a checked property.
- The evidence chain (VER-039 run identity) cannot be bound to the exact record sequence that produced it.

## 3. Objectives

1. Establish the ExecutionTrace as a first-class, serializable artifact.
2. Define the trace envelope: identity, bindings, declared inputs, engine identity, termination.
3. Define record serialization per the CR-010 record classes.
4. Define trace integrity rules.
5. Define replay: re-execution under declared inputs with sequence verification.
6. Bind traces to evidence and run summaries.
7. Provide machine-readable validation (schema + native validator) and a reference trace.

## 4. Scope

In scope: trace envelope and record format, trace validation, replay verification, CLI tooling. Out of scope: trace storage infrastructure and retention policy (implementation concern), studio trace visualization (CR-015), changes to the record classes (CR-010's).

## 5. Normative Rules

| ID | Requirement |
|---|---|
| TRC-001 | Every ExecutionTrace SHALL carry the run identity of the execution that produced it, matching its evidence record. |
| TRC-002 | The trace envelope SHALL bind the execution definition, specification, scenario (ids and versions) and engine name + version in force. |
| TRC-003 | Every record SHALL declare its class from the CR-010 record vocabulary and carry a temporal reference. |
| TRC-004 | Every record SHALL reference a declared element, condition, event or scenario id. |
| TRC-005 | Record outcomes SHALL use governed vocabularies where the class has them; free-text outcomes are invalid. |
| TRC-006 | Records SHALL be ordered by non-decreasing temporal reference within a run. |
| TRC-007 | The envelope SHALL carry the declared inputs (seed, approval resolutions, declared failures) needed to reproduce the run. |
| TRC-008 | A trace SHALL contain the records of exactly one run — multi-run traces are invalid. |
| TRC-009 | A terminated run's trace SHALL carry the termination outcome and reason. |
| TRC-010 | Replay SHALL re-execute from the bound artifacts under the declared inputs; a conforming engine SHALL reproduce the record sequence of class, reference and outcome (TRC-008/EXE-035). |
| TRC-011 | Replay comparison SHALL be sequence-based on (class, ref, outcome) — incidental detail text MAY differ without failing replay. |
| TRC-012 | Replay compatibility SHALL be scoped to the engine version in force; a different engine version MAY replay differently and SHALL say so. |
| TRC-013 | The trace SHALL reference the SimulationEvidence record the run emitted (VER-039). |
| TRC-014 | Traces SHALL be serializable as JSON (canonical) and YAML (human-readable) with version-aware validation. |
| TRC-015 | Incomplete traces — a terminated run whose trace lacks its terminal record classes — SHALL be flagged, not rejected: honest truncation is reportable. |
| TRC-016 | Trace validation SHALL distinguish structural validity from replay verification: a structurally valid trace may fail to replay, and that failure is a first-class result. |

## 6. Conformance Profiles

Envelope Conformance (TRC-001..002, 007..009, 013..014) · Record Conformance (TRC-003..006) · Replay (TRC-010..012, 016). Structural envelope conformance does not imply replay success (TRC-016).

## 7. Canonical Representation

The ExecutionTrace is machine-readable (schema/trace.schema.json) with native semantic validation (src/aocl/trace.py) and replay verification against the bound artifacts. The reference trace is the committed canonical trace of the CR-011 reference run.

Replay semantics (TRC-010/011): the verifier re-executes the bound execution definition against the bound artifacts with the envelope's declared inputs and seed, then compares the produced record sequence with the recorded one on (class, ref, outcome) triples. A length mismatch or first differing triple fails replay with the position reported.

## 8. Acceptance Criteria

1. The canonical trace of the reference logical run validates (schema + native validator). 2. Integrity violations (class, ordering, multi-run, missing termination) are each rejected by a specific rule. 3. Replay of the reference trace against the bound artifacts succeeds. 4. A mutated trace fails replay with the differing position reported (TRC-011 semantics). 5. Evidence reference is present. 6. No storage infrastructure is introduced.

## 9. Dependencies

| CR | Relationship |
|---|---|
| AOCL-CR-010 | Declares the record classes and temporal obligations |
| AOCL-CR-011/012 | The engines whose traces this CR serializes and replays |

**End of AOCL-CR-013**
