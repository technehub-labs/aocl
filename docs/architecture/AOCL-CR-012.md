> **Status:** Proposed · **Drafted:** 2026-11-22 — the State-Based Simulation Engine: quantitative state evolution over the CR-010 contract, formalizing the sim-canvas prototype (tools/sim_check.py) whose core is extracted verbatim as the reference interpretation · Companion to AOCL-CR-011 (the Logical Simulation Engine); both implement the same execution semantics with different fidelity · Defines engine-conformance rules SBE-001..020.

---

# AOCL-CR-012 — Establish the State-Based Simulation Engine

**CR ID:** AOCL-CR-012\
**Title:** Establish the State-Based Simulation Engine\
**Programme:** AOCL Engineering Engine\
**Status:** Proposed\
**Priority:** High\
**Type:** Engine Implementation\
**Depends on:** AOCL-CR-001 through AOCL-CR-011

---

## 1. Executive Summary

This Change Request establishes the State-Based Simulation Engine: the quantitative counterpart to CR-011's logical engine. Where the logical engine interprets the behavioral graph's structure, the state-based engine evolves **numeric plant state** under declared disturbance profiles and a declared control policy, measures the consequences (excursions, restoration, human burden), and evaluates the mapping's plausibility invariants.

The engine's quantitative reference interpretation is the sim-canvas prototype's semantics — extracted verbatim into the canonical core (`src/aocl/simcore.py`) so that the prototype, the engine, and the site's JS parity port share one source of truth. The level→policy mapping remains the informative hypothesis under test (findings F1–F4 pending user decisions).

## 2. Problem Statement

The prototype proved the mapping produces plausible behavior (7/7 invariants, docs/simulation.md, ADR-006), but as an engine-embedded script: outside the canonical models, with no conformance gating, no binding to governed scenarios, and evidence only by convention. CR-012 formalizes it: the same physics, executed under the CR-010 contract, gated by the CR-002..009 validators, emitting CR-008-conformant evidence.

## 3. Objectives

1. Implement the CR-010 contract for StateBased/Hybrid mode.
2. Enforce conformance gating and state-based readiness (EXE-005/AD-007-12/AD-009-15).
3. Evolve quantitative plant state under declared disturbance profiles (CR-009 §11.3).
4. Apply the declared control policy (the reference level→policy mapping; contract-declared gains where present).
5. Maintain separated channels with sensor-noise veracity (the observed channel is what the Controller sees).
6. Model human participation per HITL/HOTL/HOOTL windows.
7. Evaluate the plausibility invariants and report them as run verdicts.
8. Emit SimulationEvidence with run identity (VER-039) and the run's parameters (seed, scenario, vectors).

## 4. Scope

In scope: the state-based engine, its conformance rules, the verbatim core extraction, invariant evaluation as run verdicts, run summaries and evidence. Out of scope: trace format and replay (CR-013), studio visualization (CR-015), changes to the level→policy mapping itself (that is a formal-model change gated on the user's F1–F4 decisions).

## 5. Engine-Conformance Rules

| ID | Requirement |
|---|---|
| SBE-001 | A conforming state-based engine SHALL implement the CR-010 EXE contract for StateBased/Hybrid mode. |
| SBE-002 | The engine SHALL refuse to execute any bound artifact that fails its native validator, reporting the findings (conformance gate). |
| SBE-003 | The engine SHALL verify the ExecutionDefinition's state-based readiness and the bound scenario's state-based readiness before running. |
| SBE-004 | Plant state SHALL evolve quantitatively per the declared reference interpretation (an integrator with declared return rate, noise, and disturbance injection). |
| SBE-005 | Disturbances SHALL be applied per their declared profiles (Step, Ramp, Periodic, Random) and magnitudes. |
| SBE-006 | The control policy SHALL be the declared reference mapping (level→policy per the assessment vectors) or a contract-declared policy; the source SHALL be named in the run summary. |
| SBE-007 | The observed channel SHALL be produced by observation with declared sensor noise (veracity per DV); the Controller never reads the actual channel directly. |
| SBE-008 | Human participation SHALL follow HITL/HOTL/HOOTL windows with escalation waits that are level-independent (the sim finding: the window is engagement policy, not maturity). |
| SBE-009 | Experimentation at high maturity SHALL be sandboxed (assumption 7 — load-bearing per F3): zero production perturbation. |
| SBE-010 | The engine SHALL be deterministic: identical declared inputs (including seed) SHALL produce identical results. |
| SBE-011 | Run identity SHALL be a deterministic function of the declared inputs. |
| SBE-012 | The engine SHALL evaluate the declared plausibility invariants over the run suite and report each as a run verdict — an invariant failure is a first-class result, never hidden. |
| SBE-013 | Formal-model findings (e.g. F1–F4) SHALL be reported as observations, never silently absorbed into verdicts. |
| SBE-014 | The engine SHALL emit SimulationEvidence carrying run identity, scenario, seed, vectors and engine version (VER-039), origin SimulationTime. |
| SBE-015 | The engine SHALL NOT claim the level→policy mapping is normative; runs are evidence about the hypothesis, not conformance certificates. |
| SBE-016 | The engine SHALL share its quantitative core with the prototype (single source of truth); divergence between engine and prototype is a defect. |
| SBE-017 | Multi-seed studies SHALL be used where single-seed comparisons are unfair (decision-dependent RNG consumption — the S6 rule). |
| SBE-018 | The engine SHALL report per-level run metrics (excursions, MTTR, peak, human ticks, self-inflicted, novel depth) in the run summary. |
| SBE-019 | The engine SHALL declare the horizon and tick basis from the bound artifacts, not hard-coded engine defaults where the scenario declares them. |
| SBE-020 | The engine SHALL NOT redefine domain meaning established by CR-002..009 (AOCL-P27). |

## 6. Conformance Profiles

Structural Gate (SBE-002/003) · Quantitative Fidelity (SBE-004..006) · Veracity (SBE-007) · Governance (SBE-008/009) · Determinism (SBE-010/011/017) · Verdict Honesty (SBE-012/013/015) · Evidence (SBE-014/018). Reported separately, as in CR-011.

## 7. Reference Interpretation (the extracted core, verbatim)

The quantitative semantics are `src/aocl/simcore.py` — extracted verbatim from the prototype so the engine adds no physics of its own (SBE-016). Declared characteristics:

1. **Plant**: an integrator; disturbances are impulse events (known learnable modes with periods, novel one-shots) plus a slow drift shifting the operating point.
2. **Policy source**: the level→policy mapping (thresholds, gains, pre-emption, containment, sandboxing) selected by the assessment vectors' minimum — the hypothesis under test.
3. **Veracity**: sensor noise and misdetection/false-alarm rates per DV; wrong-direction actions per DV flip probability.
4. **Humans**: HITL resolves any excursion after response time; HOTL escalates after a declared (level-independent) window; HOOTL engages on novelty only.
5. **Governance**: exception upflow → playbook conversion (policy downflow); governed slow loops retune the fast loop's reference between epochs.
6. **Invariants**: restoration monotonicity, burden collapse, the L3/L4 novel-mode discriminator, velocity orthogonality, sandboxed experimentation, policy downflow, veracity multiplier — evaluated over the declared suite (S1–S8).

## 8. Migration and Compatibility

`tools/sim_check.py` becomes a shim over the canonical core (output identical; CI unchanged in effect). `site/sim.js` remains the JS parity port pinned by `tests/sim-parity.json` — the extraction does not touch it. The engine's runs supersede none of the prototype's CI role; they formalize it.

## 9. Acceptance Criteria

1. The engine executes the bound scenario suite under the reference execution definition. 2. The conformance gate rejects invalid artifacts with findings. 3. All seven invariants evaluate and are reported as verdicts. 4. Run identity is input-derived; two runs with identical inputs are identical. 5. Evidence carries run identity, seed, vectors, engine version. 6. The prototype's CLI output is unchanged through the shim. 7. Findings are reported as observations. 8. No physics was rewritten (verbatim core, SBE-016).

## 10. Dependencies

| CR | Relationship |
|---|---|
| AOCL-CR-011 | Logical engine — same contract, structural fidelity |
| AOCL-CR-013 | Trace and Replay — owns trace format; state-based traces feed it |

**End of AOCL-CR-012**
