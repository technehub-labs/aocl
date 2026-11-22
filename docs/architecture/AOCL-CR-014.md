> **Status:** Proposed · **Drafted:** 2026-11-22 — the Studio: a read-only visual modeling surface over the canonical artifacts — the behavioral specification rendered as a staged graph, scenario libraries with visibility-declared disturbances, control contracts, and engine results · Consumes CR-002..013 artifacts; defines rules STU-001..008.

---

# AOCL-CR-014 — Establish the Studio (Graph-Based Visual Modeling Canvas)

**CR ID:** AOCL-CR-014\
**Title:** Establish the Studio (Graph-Based Visual Modeling Canvas)\
**Programme:** AOCL Studio\
**Status:** Proposed\
**Priority:** Medium\
**Type:** Studio Capability\
**Depends on:** AOCL-CR-002 through AOCL-CR-013

---

## 1. Executive Summary

This Change Request establishes the Studio: the visual surface over the canonical models. The Modeling stage and the engine tranche made the artifacts machine-readable and executable; the Studio makes them *visible* — the behavioral specification as a staged graph, scenario libraries with their disturbance visibility declarations, control contracts and authority, and engine results with their verdicts.

The Studio is **read-only over the canonical artifacts**: edits happen in the artifacts, never in the rendering (STU-007). This is the boundary that keeps the visual surface from becoming a second source of truth — the failure mode the original review warned about ("a visually attractive tool that cannot faithfully represent real operational behavior").

## 2. Scope and Boundary

In scope: the artifact bundle export (gated), the staged-graph rendering of the behavioral specification, scenario/control/evidence panels, and engine-result rendering. Out of scope: in-browser editing (a governed authoring capability is a future CR), runtime visualization of executing engines (CR-015), scenario management operations (CR-016).

## 3. Normative Rules

| ID | Requirement |
|---|---|
| STU-001 | The Studio SHALL consume only artifacts that pass their native validators — the export is conformance-gated (LSE-002 discipline applied to visualization). |
| STU-002 | Every bundle SHALL carry the artifact ids and versions it renders (provenance; TRC-002 discipline). |
| STU-003 | The graph SHALL render the canonical relationships exactly — the Studio SHALL NOT add implied sequencing, ordering or stage pipelines the artifacts do not declare. |
| STU-004 | Stage lanes SHALL reflect declared stage associations only; multi-stage elements appear at their declared positions without duplication of semantics. |
| STU-005 | Disturbance visibility declarations (CR-009 §11.5 knownToController) SHALL be rendered explicitly — the human observer may see what the simulated Controller may not, and the rendering must show that distinction. |
| STU-006 | Bundles SHALL be deterministic (stable ordering) and versioned. |
| STU-007 | The Studio SHALL be read-only over the canonical artifacts; no rendering artifact is ever a source of model semantics. |
| STU-008 | Engine results (traces, run summaries) SHALL render with their termination verdicts and verification status — never as decoration; a pending safe-state verification renders as pending. |

## 4. Conformance Profiles

Gated Export (STU-001/002/006) · Graph Fidelity (STU-003/004) · Visibility Rendering (STU-005) · Read-Only Boundary (STU-007) · Verdict Honesty (STU-008).

## 5. Reference Implementation

`aocl-studio export` produces the bundle (`studio-data.json`) from the example family; the site's Studio view (`site/studio.html`) renders it — staged lanes for the seven responsibilities, relationship-type-coded edges, condition/participation/exception panels, and the reference run's verdict. Offline-first, no build step, no CDN (site conventions).

**End of AOCL-CR-014**
