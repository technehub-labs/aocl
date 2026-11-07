# ADR-006: Simulation evidence, AOCL-ARCH-001 adoption, and the aggregation decision direction

**Status:** accepted (2026-11-07, artifact draft) · **Supersedes:** none · **Context:** [AOCL-ARCH-001](../architecture/AOCL-ARCH-001.md) (Proposed), [AOCL-CR-001](../architecture/AOCL-CR-001.md) (Proposed), [review input (Rev. 1)](../architecture/AOCL-ARCH-REVIEW-INPUT.md), [simulation findings](../simulation.md)

## Context

Two things happened in sequence:

1. **The level→policy mapping was tested in simulation** (`tools/sim_check.py`, `site/simulation.html`): a deterministic state-based simulation of a loop at chosen (GD, DV, FI) against a plant under noise, drift, learnable known modes, novel one-shot events, and humans. Seven plausibility invariants were defined and — after honest iteration — **all seven hold** (restoration monotonicity, burden collapse, the L3/L4 novel-mode discriminator, velocity orthogonality, sandboxed experimentation, policy downflow via exception-upflow→playbook-conversion, veracity multiplier). Four findings survived every fix (F1–F4, below).
2. **AOCL-ARCH-001 was drafted**: a normative foundation proposing the seven-stage behavioral lifecycle (Intent, Observe, Analyze, Decide, Execute, Verify, Learn), the structural/behavioral distinction, hybrid simulation, three architecture layers, principles P01–P12, and the AOCL/CLAM boundary — preceded by a comprehensive review that demanded, among other things, outcome verification as a mandatory stage and failure-path simulation.

This ADR records what the simulation does and does not corroborate against that architecture, adopts the architecture as the baseline direction, and disposes of the simulation findings as architectural input.

## Part I — Corroboration: what the simulation validates in ARCH-001

| ARCH-001 principle / position | Simulation evidence |
|---|---|
| **P03** Observable state distinguishable from actual state | The sim's plant state `x` and its observation `obs` are distinct channels: sensor noise, missed detections, false alarms, and wrong-direction actions (DV_FLIP) all act on the observation only. The veracity-multiplier invariant is *empirical proof that conflating them conceals failure*: DV 5→2 at the same L5 shape raises human burden 13× and MTTR 2× — the review's exact warning ("passing plant state directly into the controller conceals one of the most important sources of operational failure", §7.2) demonstrated quantitatively. |
| **P06** Bounded autonomy | HITL/HOTL/HOOTL engagement semantics bound every action; the burden-shift finding (F2) quantifies the boundary of HOOTL (novelty-only engagement). |
| **P12** Reproducibility | Seeded xorshift; the JS site engine reproduces Python traces exactly across the full ladder and the governance study. |
| **P11** Composability (minimal) | The policy-downflow study is a working two-loop composition: a governing slow loop converts the fast loop's reported novel signatures into playbook entries — a 50% mean excursion cut across 8 seeds (governed 4.25 vs ungoverned 15.25). |
| **§7.2 state-based simulation feasibility** | The sim *is* a minimal state-based engine: plant state, sensor observations with error, disturbances, control actions, thresholds, outcome metrics — the review's L2 fidelity target, demonstrated at small scale. |
| **§10 failure-path demand** | The review insists success-path-only simulation is insufficient. The invariant suite is precisely a failure-path battery: misread-direction actions, drift chatter, velocity mismatch, silent accumulation under HOOTL, missed detections destroying zero-touch. |
| **§3 maturity is per-implementation** | Vectors are assessed per loop (modeler, ledger), never per enterprise. |

## Part II — Critique: where the simulation falls short of ARCH-001

The sharpest results of this review are the *gaps* — the simulation validated the level→policy mapping but cannot yet validate the behavioral lifecycle, because it has none:

1. **No Verify stage (S6).** Excursion detection is the *simulator's* judgment against the setpoint — not a loop-owned verification mechanism comparing expected against actual effects. Under REQ-010 ("execution success SHALL NOT be treated as proof of outcome achievement"), the sim cannot express "action executed, outcome not achieved" — a case the review explicitly demands (§10). **The sim's loop has no S6, and the sim was blind to that until the architecture said so.**
2. **No governed learning (S7 / REQ-011).** FI learning is automatic (occurrences → playbook unlock). ARCH-001 requires learning to be governed and distinguishable from state updates. The capability-leak finding (F1) is *evidence for* REQ-011: ungoverned capability expression acting past the level gate is exactly what governance would control.
3. **No behavioral specification (P05 / REQ-006).** The loop's behavior is a level-parameterized policy, not a modeled behavioral specification. P09 ("simulation derives from canonical model semantics") is only partially honored: the sim derives from `model/behavior.yaml` (informative) plus engine-hardcoded semantics — not from a canonical behavioral specification of a *modeled* loop.
4. **No explicit temporal model.** Implicit unit ticks and cycle intervals; the review's implication C (event ordering, processing delays, observation intervals) is unmet — though the velocity semantics (trend smoothing for slow loops) is the seed of it.
5. **No intent model (P02).** The setpoint is a constant; declared constraints, priorities, and conflict rules are absent; L5's "self-set goals" is a bounded sinusoid — a placeholder, not intent modeling.

These gaps define the work: they are not defects of the invariants but the distance between a mapping-plausibility instrument and an architecture-conformant one.

## Part III — The findings, disposed against the architecture

| Finding | Simulation evidence | Architectural disposition | Lands in |
|---|---|---|---|
| **F1** min-aggregation inconsistency: `(5,1,5)` ≈ pure L1 (capabilities never activate — "sophisticated but blind" inexpressible) while `(5,2,5)` — also min-L2 — *outperforms* pure L2 (FI-gain adaptation is vector-gated, not level-gated) | Both directions demonstrated; 8-seed stable | ARCH-001 §9 preserves weakest-link "subject to the normative assessment rules" — the sim shows those rules **must** define how vectors bind to behavior, or implementations will diverge (our own two engines had to choose). The metamodel must carry per-vector behavioral roles as first-class, with "level" either strictly binding or explicitly a reporting label. Inconsistency is the only unacceptable option. | **AOCL-CR-002 (metamodel) — must-resolve** |
| **F2** L5 shifts burden; it does not eliminate it (routine MTTR at L5 can exceed L4's human-assisted recovery; novelty still summons people) | human_ticks [2280, 870, 0, 0, 60] | ARCH-001 §11's governance taxonomy (autonomous / human-authorized / supervised / escalation / prohibited) should distinguish **routine burden** from **novelty engagement**; maturity documentation must not claim burden monotonicity through L5 ("higher autonomy ≠ better", quantified) | **AOCL-CR-003 (behavioral lifecycle)** + maturity docs |
| **F3** Sandboxing is load-bearing: unsandboxed L5 experimentation raised human burden *above L4* and broke HOOTL plausibility | Earlier sim iteration, fixed by sandboxing; zero self-inflicted excursions since | Direct evidence for ARCH-001 §5.9 ("a learning event does not automatically authorize a policy or controller modification"): L5 loop models must declare experimentation containment as a component attribute | **AOCL-CR-004 (control component semantics)** — conformance attribute |
| **F4** gain×cycle co-design / velocity fit: high-gain policy on a slow cycle accumulates unbounded *silent* drift under HOOTL (mttr 2860 vs L1's 87) | Velocity-orthogonality scenario | ARCH-001 implication C (temporal model) + §7: couple actuation authority and gain to the observation/cycle interval, or define a **velocity-fit precondition** before L4+ is claimed; the ledger should record the fit check | **AOCL-CR-002 / CR-004** + ledger schema v2 |

## Part V — Superseded in part by ADR-007

[ADR-007](adr-007-realization-cost-benefit-instrument.md) re-frames the realization model from informative side-instrument to **the core cost-benefit decision instrument** of AOCL (informative status preserved for uncalibrated use), adds E/C/V_d measurement anchors to CR-006's behavioral specification, and establishes the L3 investment gate as programme policy. ADR-006's evidence dispositions (F1–F4) remain unchanged; the realization emphasis supplements them.

## Part IV — Hybrid realization (post-baseline development)

After this ADR's first draft, the Studio gained a **logical simulation canvas** (`site/simulation.html`): the seven-stage behavioral lifecycle is visually executable — stage toggles with omission probes, a verification-bypass mode, failure-path scenarios (stale telemetry, sensor drift, actuator fault, demand shock, **policy mismatch**: L5 capability with observe-only grant, **broken feedback**), decision-authority policies configurable per level (observe / recommend / bounded / adaptive), and a plant-state vs observed-state split with sensor delay. That places it squarely in ARCH-001 §10.1 (**logical simulation**) and directly probes REQ-006/REQ-007/REQ-010 conformance — including the review's §10 demand that failure cases, not just the success path, be simulatable.

With the batch runner + JS engine as the §10.2 (**state-based**) mode, **ADR-002's hybrid simulation is realized end to end**: logical mode validates behavioral completeness and governance semantics; state-based mode evaluates control behavior against disturbance regimes — with cross-engine parity pinned in `tests/sim-parity.json` (7 Python-pinned cases asserted in CI).

Division of labor going forward: behavioral/governance semantics evolve in the logical canvas first (fast, visual, conformance-probing); validated semantics graduate into the state-based engine's `model/behavior.yaml` and invariant suite; both must keep agreeing on whatever they share (P09, P12).

## Decisions

1. **Adopt AOCL-ARCH-001 as the architecture baseline direction** — the seven-stage behavioral lifecycle, structural/behavioral distinction, hybrid simulation, three layers, and principles P01–P12 — endorsing AOCL-CR-001 for approval. The existing assessment, realization, modeler, ledger, and CLAM-export capabilities are preserved and re-reviewed against this foundation (per CR-001 §12), not rewritten.
2. **Adopt the simulation findings F1–F4 as architectural input** with the dispositions above. The simulation is hereby an *architectural evidence instrument*: its invariant suite is Gate-3-style conformance evidence (executable behavioral semantics) and its parity-verified dual engines partially satisfy P12/Gate-4 (reproducible simulation).
3. **Designate the simulation canvas the prototype of ARCH-001's state-based simulation mode (§10.2).** Its migration path is normative: it must come to execute the CR-003 behavioral specification — gaining S6 Verify (expected-vs-actual evaluation as a loop responsibility) and governed S7 Learn — rather than parameterized policy alone (P09).
4. **The four scenarios (baseline, drift, fastdist, quiet) and the seven invariants seed the CR-009 scenario library** and become regression evidence for every subsequent engine change.

## Consequences

- CR-002 (canonical metamodel) inherits a **must-resolve**: the aggregation-binding rule (F1). Until resolved, `assess.py`/`scoring.js` keep the weakest-link label and the engines keep per-vector behavioral gating — documented, consistent within this repo, and flagged for the metamodel decision.
- The behavioral lifecycle work (CR-003) has a validated reference example: the exception-upflow → playbook-conversion → policy-downflow loop is the concrete instance of §6.2 (loop continuation) and S7 influencing subsequent cycles — use it as the worked example in CR-003 and CR-005 (composition).
- The simulation's gaps (Part II) are the acceptance criteria for its own evolution: S6 Verify, governed S7, behavioral-specification execution, explicit temporal model.
- No existing artifact is invalidated: ARCH-001 §12/CR-001 §12 migration rules apply — behavior.yaml, the ledger, and CLAM contracts are inventoried and mapped, not replaced.

## Dissent / unresolved

- The aggregation decision (F1) is genuinely open: strict level-gating preserves the ladder's meaning; vector-gated profiles are more expressive but change what levels mean downstream. The sim cannot decide this — it can only show the cost of inconsistency. Revisit at AOCL-CR-002 with the pilot evidence.
- The seven-stage lifecycle is adopted as canonical *vocabulary*; the sim's monolithic policy loop is not yet a conformant behavioral specification. Nothing here endorses the sim as CR-003-conformant.
