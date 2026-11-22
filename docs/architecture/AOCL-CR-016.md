> **Status:** Proposed · **Drafted:** 2026-11-22 — Scenario Management and Comparison: cross-scenario comparison under a constant model, variant differencing, verification-target coverage — the management operations over CR-009 scenario libraries · Defines rules SMC-001..010.

---

# AOCL-CR-016 — Establish Scenario Management and Comparison

**CR ID:** AOCL-CR-016\
**Title:** Establish Scenario Management and Comparison\
**Programme:** AOCL Studio\
**Status:** Proposed\
**Priority:** Medium\
**Type:** Engine Capability\
**Depends on:** AOCL-CR-009, AOCL-CR-012

---

## 1. Executive Summary

This Change Request establishes the management operations over scenario libraries: **cross-scenario comparison** (the same loop model evaluated under each scenario, differences attributable to the scenarios), **variant differencing** (what each variant changes relative to its base), and **verification-target coverage** (which claims the library's scenarios actually evaluate).

CR-009 §13.3 defined the comparison requirements; CR-012's state-based engine provides the quantitative runs. CR-016 connects them: comparison holds the model configuration constant so differences are scenario-attributable (SMC-002/006), variants are compared by declared and structural deltas (SMC-004), and coverage gaps are reported, never hidden (SMC-005).

## 2. Normative Rules

| ID | Requirement |
|---|---|
| SMC-001 | Comparison SHALL operate only over a validated scenario library sharing one model baseline (SCN-052 discipline). |
| SMC-002 | Cross-scenario comparison SHALL hold the model configuration constant — the same loop vectors, level and seed across scenarios — so observed differences are scenario-attributable. |
| SMC-003 | The comparison SHALL report per-scenario run metrics and the deltas against the library's baseline scenario. |
| SMC-004 | Variant comparison SHALL report the declared differences (extends/differences) together with the structural deltas (parameters, disturbances, initial states) versus the base scenario. |
| SMC-005 | Verification-target coverage SHALL be reported as a scenario × target matrix; targets no scenario evaluates SHALL be flagged. |
| SMC-006 | Comparison SHALL NOT conflate scenario-attributable changes with model-attributable ones: single-model runs only, model changes across a comparison are invalid. |
| SMC-007 | Comparison output SHALL be deterministic (stable ordering) and serializable. |
| SMC-008 | The seed and run configuration SHALL be carried in the comparison output (reproducibility, SCN-048 discipline). |
| SMC-009 | Comparison results are evidence about the model under scenarios — never conformance certificates (SBE-015 discipline). |
| SMC-010 | Scenarios without a quantitative interpretation in the bound engine SHALL be compared structurally (variant diff, coverage) and reported as such — no fabricated metrics. |

## 3. Conformance Profiles

Gated Comparison (SMC-001/006) · Attribution (SMC-002/003) · Variant Fidelity (SMC-004) · Coverage Honesty (SMC-005) · Reproducibility (SMC-007/008) · Verdict Honesty (SMC-009/010).

## 4. Reference Implementation

`aocl-scenario-compare` runs the state-based engine's core per scenario at the loop's assessed vectors/level and seed, reports the metric table with baseline deltas, the variant matrix (declared + structural deltas), and the coverage matrix. Scenarios with no quantitative interpretation (e.g. the multi-loop variant F) are compared structurally and reported as such.

**End of AOCL-CR-016**
