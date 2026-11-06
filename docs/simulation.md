# Simulation: does the level→policy mapping hold up?

**Status:** draft (informative) · **Semantics under test:** `model/behavior.yaml` · **Engines:** `tools/sim_check.py` (batch + invariants), `site/simulation.html` (interactive canvas, JS port — parity-verified against Python)

Before the maturity mapping becomes formal model, we tested it: a deterministic discrete-event simulation of a plant (integrator) under disturbance, controlled by a synthetic loop whose behavior is parameterized by the level→policy mapping. This document records the semantics, the plausibility invariants, and the honest findings.

> **What this is:** an instrument for falsifying our own mappings. **What it is not:** evidence about real telecom plants, a validated model, or a normative artifact. All numbers are simulation outputs under toy dynamics.

## The behavioral semantics (the mapping under test)

Each assessment vector drives a different behavioral aspect — this is the semantics being tested:

| Vector | Behavioral role |
|---|---|
| **GD** Goal Decisioning | Reference/setpoint management (GD5 = self-set goals, bounded) |
| **DV** Data Veracity | Observation quality: sensor noise, missed detections, false alarms — and **wrong-direction actions** (a misread deviation flips the correction) |
| **FI** Feedback Intelligence | Learning speed: occurrences before a mode's playbook unlocks (L3: 3, L4: 2, L5: 1); gain adaptation at FI4+ |

Level policy (from §3.2 of the source document): L1 no action (human is the loop) · L2 static threshold + fixed response · L3 playbook pre-emption of known modes (tested countermeasure cancels the spike in flight) · L4 learned baselines + partial novel containment · L5 near-full containment + sandboxed generative experimentation. Velocity is orthogonal by construction: fast acts every tick (authority 10), slow every 100 (authority 8) and reasons on trends, not transients.

Plant: an integrator — disturbances accumulate unless actively canceled. Disturbances: noise; two **known recurring modes** (learnable); **novel one-shot events** (semi-recurring latent signatures); a **drift** (a physical rate push — the operating point moves). Humans: HITL engages on every excursion; HOTL after an escalation window; HOOTL only for novel/unprecedented events.

## The invariants (plausibility checks)

Deterministic, seeded (xorshift32); the JS engine reproduces the Python traces exactly (verified across the full ladder and the governance study). All seven hold at seed 2026:

| # | Invariant | Result |
|---|---|---|
| 1 | **Restoration**: peak severity decreases monotonically L1→L5; MTTR collapses L1→L2 and stays bounded | ✓ peaks 78→47→21→16→8; mttr 25.7→10.6→4.25→1.97→3.07 |
| 2 | **Human burden**: collapses from L1 to the autonomous band; L5 bounded | ✓ 2280→870→0→0→60 ticks |
| 3 | **Novel-mode gap** (the L3/L4 discriminator): L3 pre-empts *known* modes (count 19→3) but not novel ones (depth ≈ L2); L4 halves novel depth | ✓ 15.8→14.1→6.5 |
| 4 | **Velocity orthogonality**: no level prevents fast disturbances on a slow loop | ✓ prevention 0% at L1 AND L5 |
| 5 | **Sandboxed experimentation** (assumption 7): L5 experiments never perturb production | ✓ zero self-inflicted excursions |
| 6 | **Policy downflow**: exception upflow → playbook conversion cuts the governed loop's post-retune excursions ≥30% | ✓ 50% mean cut over an 8-seed study (15.25→4.25) |
| 7 | **Veracity multiplier**: DV 5→2 at the same L5 shape destroys the zero-touch property (human 30→780 ticks) and degrades MTTR 2× | ✓ |

## Findings — what we must look into

These are formal-model change candidates. They emerged from the iterations (several earlier "failures" were sim bugs; these survived every fix):

### F1 — min-aggregation is inconsistent (the big one)

- `(GD5, DV1, FI5)` behaves **nearly identically to pure L1**: with min-aggregation the sophisticated capabilities never activate, so the model cannot express *"sophisticated but blind"* — a loop whose decision-making is excellent but whose data is garbage. (Whether "don't act on untrustworthy data" is the RIGHT behavior for that loop is itself a question the model should be able to ask.)
- Conversely `(GD5, DV2, FI5)` — also min-L2 — behaves **better than pure L2**, because FI4+ gain adaptation and GD5 goals are **vector-gated, not level-gated**. The aggregation gates some capabilities but leaks others.

**Decision needed:** either strictly level-gate every capability (min becomes binding and the vectors are decorative), or make `(GD, DV, FI)` the behavioral profile with "level" as a reporting label. The simulation suggests the second is more expressive — but it changes what "a loop is at L4" *means* everywhere (ledger, modeler, exports). This is the biggest open question.

### F2 — L5 shifts burden; it does not eliminate it

With humans out of the loop (HOOTL), routine recovery is the loop's alone — L5's MTTR can *exceed* L4's human-assisted recovery. And novelty (including the loop's own validated deployments) still summons people. The formal model should say **L5 eliminates routine burden** — not that burden monotonically decreases to zero. "Higher autonomy ≠ better" is not a slogan; it shows up in the metrics.

### F3 — assumption 7 (sandboxing) is load-bearing

Our first L5 semantics experimented *in production*: human burden rose **above L4's**, breaking plausibility. The document's "autonomous experimentation shall be sandboxed" is not decoration — without it, L5's HOOTL semantics are unimplementable safely. The formal model must carry sandboxing as an explicit L5 policy element.

### F4 — gain×cycle co-design (velocity fit) is missing from the mapping

Level policy parameters (gain, thresholds, lead times) are velocity-independent. A high-gain L5 policy on a slow cycle accumulates unbounded silent drift (mttr 2860 vs L1's 87 in the mismatch scenario — with HOOTL, *nobody is watching*). The mapping needs either an explicit **gain×cycle co-design rule** or a **velocity-fit precondition** before high maturity is claimed. Related: escalation windows (how long a loop waits before calling a human) are engagement *policy* and must be level-independent — giving L4 a shorter window than L3 made burden non-monotone.

### F5 — the L3/L4 boundary is the document's sharpest claim — and it holds

The known/novel discriminator (L3: human-designed forecasts for known modes; L4: learns novel patterns) reproduced cleanly: L3 pre-empts known modes 84% but novel depth ≈ L2; L4 halves novel depth. This is the mapping's strongest validated structural element.

## How to reproduce

```bash
python3 tools/sim_check.py              # batch + invariants (exit 1 on any failure)
python3 tools/sim_check.py --json       # machine-readable
open site/simulation.html               # interactive canvas (also on Pages)
```

The canvas exposes vector selects, velocity, scenario, human-response slider, seed, and a governance toggle, with the live plant trace, human-engagement bars, excursion shading, and a one-click ladder comparison.

## Boundary

Toy dynamics, one plant, two known modes, three latent novel signatures. The invariants test the *internal coherence* of the mapping — they cannot establish that real loops at these levels behave this way. Pilot validation (the `mama` project's Track B) remains the path to that claim. Simulation parameters live in `model/behavior.yaml` (informative) and the engines; they are not normative model data.
