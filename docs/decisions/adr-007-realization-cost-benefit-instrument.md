# ADR-007: Realization as the core decision instrument — the cost-benefit thesis, instrumentation, and the L3 investment gate

**Status:** accepted (2026-11-07, artifact draft) · **Supersedes:** none · **Context:** [AOCL-ARCH-001](../architecture/AOCL-ARCH-001.md), [CR-002](../architecture/AOCL-CR-002.md) (queued), [CR-006](../architecture/AOCL-CR-006.md) (queued), [realization model](../realization-model.md), [ADR-006](adr-006-simulation-evidence-and-architecture-alignment.md)

## Context

The entire model rests on one postulate, which must now be treated as the organizing thesis of AOCL rather than an informative side-note:

> **Organizations invest in the sophistication of automating the adaptability, self-governance and decisioning of operational processes and systems** — pursuing higher closed-loop maturity (toward the Self-X mode, with humans out of the loop except on-the-loop for policy setting, observability and intent provisioning) — **and the cost of that investment (the automation engineering and the systems that must be put in place) grows exponentially with maturity, while incremental gains diminish** through L1–L3 and only inflect toward compounding returns at the L3–L4 boundary.

The two vectors of that postulate:

- **Complexity (C)** — the technical sophistication of such automated operations: the closed loops operating toward Self-X modes at their level; the **data-fusion requirements** (how the automation harnesses data *variety* to inform decisioning models and to learn and adapt); and the **interwoven nature of the loops** (inter-loop coupling and composition).
- **Experience (E)** — the stability, ease of use and "Self-X" properties delivered to the operator or observer and the actual end user: from high required effort at low maturity to extremely-low-to-nothing at L5, where the human role is reduced to the on-the-loop triad (policy, observability, intent provisioning).

Realization effort, in real life, is **cost to realize**. The realization model's effort factor (`E_f = e^R`) and the marginal effort jumps between levels (Table 1.1: L4→L5 more than doubles complexity for ~7× the effort) are the formal expression of the thesis. The simulation now provides the value side empirically (burden collapse 2280→0 ticks, excursion peaks 78→8 across the ladder).

## Decision

1. **The realization model is promoted from informative side-note to the core decision instrument of AOCL** — while preserving its status discipline: *uncalibrated, it remains informative; calibrated with an organization's own cost and value data, it becomes their investment-decision model.* It is still never a certification, contract or maturity score (ADR-003/CR-001 REQ-013 unchanged).
2. **The cost-benefit instrument is a first-class tool deliverable, implemented now** — not deferred behind the CR sequence. `aocl-realization --decide` provides the marginal analysis: per-transition effort deltas (e^R differences from the reference points or caller-supplied calibrated values), per-transition value deltas (log model L1–L3, exp model L3–L5), and the L3–L4 inflection as the explicit invest/hold gate.
3. **E/C/V_d measurement anchors are bound into CR-006's behavioral specification**: human-participation declarations (CR-006 §12) are the *E anchor* (manual-touch measurement per stage); control-architecture components and their fusion/dependency declarations (CR-004, carried through CR-006 traceability) are the *C anchors* (structural, dynamic, semantic, coupling); observation quality declarations are the *V_d anchor*. The spec is measurable by construction.
4. **CR-008's evidence model carries the effort-evidence chain**: the thesis is validated with *evidence of effort expended* (engineering time, integration counts, incident and burden records) against *evidence of value realized* (burden reduction, excursion reduction) — per level. SimulationEvidence (our invariant suite) is the template; OperationalEvidence is the proof.
5. **The L3 investment gate is normative programme policy**: L1–L3 tooling is complete and every loop should be taken to L3 cheaply; L4–L5 tooling and investment are **exception-driven** — pursued only where the instrument shows the value inflection justifies the e^R cost for that specific loop. The engineering programme follows its own thesis: the L4–L5 machinery (experimentation sandboxes, digital twins, self-modification support) is deliberately deferred until the evidence says it pays.

## How this optimizes the implementation order

The CR dependency sequence is unchanged (CR-006 → CR-007 → CR-008 → CR-009; CR-010 baselined before engines formalize) — dependencies are real. What the thesis optimizes is **what gets built inside each CR and what gets built first in the tools**:

| Tranche | Thesis-driven emphasis |
|---|---|
| **Now (parallel to CR-006)** | The cost-benefit instrument (`aocl-realization --decide`) — because it is the instrument that makes every later investment decision evidence-based. Cheapest deliverable, highest leverage. |
| **CR-006** | Behavioral spec carries the E/C/V_d measurement anchors (decision 3). A specification that cannot measure its own manual touch, fusion requirements and coupling cannot feed the thesis. |
| **CR-007** | Control contracts are the *cost-control artifact*: a contract's authority scope is precisely what an organization buys when it automates to a level. Contracts make the purchased autonomy auditable. |
| **CR-008** | The evidence model is the *thesis-validation mechanism*: effort evidence vs value evidence, per level, per frontier (automation / prediction / cognition / autonomy). |
| **CR-009** | Scenario variants become **investment stress tests**: "is L4 worth it under THIS disturbance regime?" is a variant question, not a dashboard question. |
| **Engines** | Deferred behind CR-010 and the L3 gate — build L4/L5 simulation machinery only when instrumented loops justify it. |

## Consequences

- The realization documentation, README problem statement and tools are re-articulated to lead with the thesis (done in this change).
- The `aocl-realization --decide` mode ships now (informative, uncalibrated defaults = the research corpus reference points).
- CR-006 review checklist gains: "does the spec carry E/C/V_d anchors?" — making CR-002's AssessmentReference and the behavioral spec the two halves of the measurement.
- The L3 gate means the engine tranche (CR-011/012) can be scoped to L1–L3 semantics first — a smaller, thesis-consistent build.
- The thesis itself remains **falsifiable**: F-annotations in the sim and calibrated org data are how it gets proven or revised. A calibrated model that fails to predict effort is a finding, not a embarrassment.

## Dissent / unresolved

- The value models (log/exp) have no calibrated α/β; the instrument ships with corpus reference points and explicit "uncalibrated" labels until organizational data exists.
- Whether E should be decomposed per human *role* (operator vs observer vs end-user) is deferred — the current E is a single index over routine manual effort.


## Refinement — calibration primacy and curve-shape classification (2026-11-07)

User direction, adopted: the exponential-cost pattern was observed in **one controlled research scenario** (the corpus's Table 1.1 illustration). It demonstrates that costs *can* grow exponentially — it does not constrain every domain to that shape. Cost curves may be exponential, logarithmic or near-linear depending on domain, scope, environment and starting position, and the framework must help organizations **discover which shape applies to them** rather than assume one.

Accordingly:

1. **No baked-in constants.** The Table 1.1 multiples (including the 7× L4→L5 figure) are the reference scenario's illustration — labeled as such everywhere, never used as planning defaults where calibration exists.
2. **Cost calibration tool** — `aocl-realization --calibrate`: fit the organization's own cumulative cost-per-level points against linear, logarithmic and exponential shapes; report the supported shape with fit quality.
3. **Planning tool** — `aocl-realization --plan`: given a cost budget (and optionally a target Experience), project the L1–L5 cost/benefit curve from the calibrated (or explicitly uncalibrated reference) shape, report the highest level the budget reaches, marginal benefit-per-cost per transition, and emit the projected chart.
4. **The plan, documentation, enrichment, visualization, tools and simulations** carry this primacy: the decision table labels its multiples as the reference illustration; the canvas and planner charts distinguish calibrated from reference projections; simulation scenario variants double as investment stress tests under the calibrated curve.

This refines Decision 2 of this ADR — it does not change the CR dependency order or the L3 investment gate.
