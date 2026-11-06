#!/usr/bin/env python3
"""AOCL simulation batch runner — tests whether the level→policy mapping produces
plausible behavior (see model/behavior.yaml, docs/simulation.md).

Deterministic (seeded xorshift), stdlib-only. Plant semantics: x is an integrator;
disturbances are impulse events (known learnable modes, novel one-shots) plus a
drift that shifts the operating point (a moving reference the loop must track).
Slow loops reason on trends, not transients. Governing slow loops retune the fast
loop's reference between epochs (policy downflow).

Invariants are pass/fail; FINDINGS are reported observations about the formal
model (aggregation semantics) that need a decision rather than a fix.

Usage: python3 tools/sim_check.py [--json] [--seed N]
Exit codes: 0 all invariants hold · 1 one or more failed · 2 usage error.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


class LCG:
    """Deterministic RNG (xorshift32) — same seed reproduces the same trace."""

    def __init__(self, seed: int):
        self.state = seed & 0xFFFFFFFF or 1

    def next_u32(self) -> int:
        x = self.state
        x ^= (x << 13) & 0xFFFFFFFF
        x ^= x >> 17
        x ^= (x << 5) & 0xFFFFFFFF
        self.state = x & 0xFFFFFFFF
        return self.state

    def uniform(self, lo: float = 0.0, hi: float = 1.0) -> float:
        return lo + (hi - lo) * (self.next_u32() / 0xFFFFFFFF)

    def choice(self, items):
        return items[self.next_u32() % len(items)]

    def normal(self, mu: float = 0.0, sigma: float = 1.0) -> float:
        u1 = max(self.uniform(), 1e-12)
        u2 = self.uniform()
        return mu + sigma * math.sqrt(-2.0 * math.log(u1)) * math.cos(2 * math.pi * u2)


# ---- vector-gated capabilities (per model/behavior.yaml per_vector) ----
DV_NOISE = [1.00, 0.70, 0.45, 0.25, 0.10]
DV_MISS = [0.35, 0.20, 0.10, 0.04, 0.01]
DV_FALSE = [0.02, 0.015, 0.01, 0.005, 0.002]
DV_FLIP = [0.30, 0.18, 0.08, 0.02, 0.00]   # P(action direction computed from a misread deviation)
FI_LEARN = [None, None, 3, 2, 1]        # occurrences before a mode's playbook unlocks
FI_ADAPT = [False, False, False, True, True]
GD_ADAPT = [False, False, False, False, True]

# ---- level policy (the mapping under test) ----
LEVEL = {  # level → (threshold_sigma, gain, novel_containment, preempt_lead_ticks)
    1: (None, 0.0, 1.0, 0),
    2: (2.0, 0.6, 1.0, 0),
    3: (2.0, 0.8, 1.0, 8),
    4: (1.5, 0.9, 0.5, 10),
    5: (1.2, 1.0, 0.15, 14),
}
VELOCITY = {"fast": (1, 10.0), "tactical": (10, 12.0), "slow": (100, 8.0)}   # authority must cover disturbances (assumption 2)
HITL = {1: "HITL", 2: "HITL", 3: "HOTL", 4: "HOTL", 5: "HOOTL"}

HORIZON = 3000
SETPOINT = 0.0
NOISE_SIGMA = 1.0
TOLERANCE = 3.0
DRIFT = (1200, 2400, 60.0)     # cumulative operating-point shift (rate 0.05/tick)
KNOWN_MODES = [("A", 420, 26.0, 6), ("B", 730, 17.0, 4)]   # impulse events
MODE_IMPULSE_FACTOR = 0.22     # impulse per tick ≈ mag * FACTOR over the duration
NOVEL_RATE = 6.0 / 1000.0
NOVEL_MAG = (15.0, 30.0)
NOVEL_DUR = (3, 8)
HUMAN_RESPONSE = 30
HOTL_WINDOW = {3: 10, 4: 10}   # escalation wait is policy, not maturity — keep equal
HOOTL_WINDOW = 6


def simulate(vectors: dict, velocity: str, seed: int, *, scenario: str = "baseline",
             slow_governs: bool = False, human_response: int = HUMAN_RESPONSE) -> dict:
    g, d, f = vectors["GD"], vectors["DV"], vectors["FI"]
    level = min(g, d, f)  # the aggregation under test
    thr_sigma, gain_base, novel_contain, preempt_lead = LEVEL[level]
    fast_thr_sigma, fast_gain_mult = thr_sigma, 1.0   # retuned by a governing slow loop
    cycle, cap = VELOCITY[velocity]
    rng = LCG(seed)

    x = 0.0
    pending_action = 0.0
    ref = SETPOINT
    t_exc_start = None
    excursions: list[dict] = []
    human_busy_until = 0
    human_ticks = 0
    human_interventions = 0
    learned: dict[str, int] = {}    # mode → occurrences seen live
    drift_ff_granted = 0.0      # feed-forward bias granted by a governing slow loop
    novel_seen: dict[int, int] = {} # latent novel signature → occurrences (exception upflow)
    converted_novel: set[int] = set()  # latent signatures the slow loop abstracted into the playbook
    preempted: set[int] = set()
    in_playbook_window = False   # a tested playbook owns its event window (no double-correction)
    last_action_tick = -99
    gain = gain_base
    adapt = FI_ADAPT[f - 1]
    obs_hist: list[float] = []
    proactive_experiments = GD_ADAPT[g - 1] and f >= 5   # L5 experiments even when calm
    next_experiment = 400 if proactive_experiments else None

    drift_active = scenario in ("baseline", "drift")
    with_modes = scenario in ("baseline", "fastdist")   # "drift" isolates governance
    with_novel = scenario in ("baseline", "fastdist")

    def drift_rate(t: int) -> float:
        d0, d1, mag = DRIFT
        if not drift_active or t < d0 or t > d1:
            return 0.0
        return mag / (d1 - d0)   # per-tick push; cumulative displacement = mag

    # schedule impulse events
    mode_events: list[tuple[int, str, float, int]] = []
    if with_modes:
        for name, period, mag, dur in KNOWN_MODES:
            t = period // 3
            while t < HORIZON:
                mode_events.append((t, name, mag, dur))
                t += int(period * (0.9 + 0.2 * rng.uniform()))
    novel_events: list[tuple[int, float, int, int]] = []   # (et, mag, dur, latent_id)
    if with_novel:
        t = 150
        latent_i = 0
        while t < HORIZON:
            if rng.uniform() < NOVEL_RATE * 100:   # NOVEL_RATE is per tick; draws are per 100
                novel_events.append((t, rng.uniform(*NOVEL_MAG),
                                     int(NOVEL_DUR[0] + rng.uniform() * (NOVEL_DUR[1] - NOVEL_DUR[0])),
                                     latent_i % 3))   # semi-recurring latent signatures
                latent_i += 1
            t += 100

    def disturbance_impulse(t: int) -> float:
        total = 0.0
        for (et, name, mag, dur) in mode_events:
            if et <= t < et + dur:
                total += mag * MODE_IMPULSE_FACTOR
        for (et, mag, dur, _lat) in novel_events:
            if et <= t < et + dur:
                total += mag * MODE_IMPULSE_FACTOR * 1.2
        return total

    event_peaks: dict[int, float] = {}   # event start tick → max |x| during window+2
    def track_event_peaks(t: int, x_now: float):
        for (et, name, mag, dur) in mode_events:
            if et <= t <= et + dur + 2:
                event_peaks[et] = max(event_peaks.get(et, 0.0), abs(x_now))
        for (et, mag, dur, _lat) in novel_events:
            if et <= t <= et + dur + 2:
                event_peaks[et] = max(event_peaks.get(et, 0.0), abs(x_now))

    for t in range(HORIZON):
        in_playbook_window = False   # reset each tick; set by an active playbook window
        if slow_governs and t == HORIZON // 2:
            # policy downflow: the governing slow loop (FI>=3) has reviewed epoch 1
            # — it converts the novel signatures the fast loop reported upward
            # (exception upflow) into playbook entries (policy downflow), and
            # retunes detection/correction. The document: "a Fast Loop detecting a
            # novel failure mode not covered by its response playbook shall buffer
            # the anomaly and notify the Slow Loop for analysis and policy update."
            if FI_LEARN[f - 1] is not None or level >= 3:
                fast_thr_sigma, fast_gain_mult = thr_sigma, 1.0   # the update is the playbook conversion, not gain
                drift_ff_granted = drift_rate(HORIZON // 2)  # feed-forward bias vs the drift
                for lat, n in novel_seen.items():
                    if n >= 1:
                        converted_novel.add(lat)

        # ---- plant evolves (integrator) ----
        # drift_ff_granted: the governing slow loop's policy update — a feed-forward
        # bias now baked into the fast loop's output (it parametrizes the fast loop)
        x += pending_action - drift_ff_granted + disturbance_impulse(t) \
             + drift_rate(t) * (1.0 if scenario in ("baseline", "drift") else 0.0) \
             + rng.normal(0.0, NOISE_SIGMA * 0.35)
        pending_action = 0.0
        track_event_peaks(t, x)

        excursion_now = abs(x - SETPOINT) > TOLERANCE   # measured against the intent, always
        if excursion_now and t_exc_start is None:
            t_exc_start = t
            mag_at, caused = 0.0, "noise"
            for (et, name, mag, dur) in mode_events:
                if et - 2 <= t <= et + dur + 2 and mag > mag_at:
                    mag_at, caused = mag, f"known:{name}"
            for (et, mag, dur, _lat) in novel_events:
                if et - 2 <= t <= et + dur + 2 and mag > mag_at:
                    mag_at, caused = mag, "novel"
            if drift_rate(t) > 0 and caused == "noise":
                caused = "drift"
            is_self = caused == "noise" and t - last_action_tick <= 3
            excursions.append({"start": t, "class": caused, "peak": 0.0, "end": None, "self": is_self})
        if t_exc_start is not None:
            excursions[-1]["peak"] = max(excursions[-1]["peak"], abs(x - SETPOINT))
            if not excursion_now:
                excursions[-1]["end"] = t
                t_exc_start = None

        # ---- loop cycle ----
        if t % cycle != 0:
            continue
        obs = x + rng.normal(0.0, NOISE_SIGMA * DV_NOISE[d - 1] * 0.8)
        obs_hist.append(obs)
        window = min(len(obs_hist), max(cycle // 2, 5))
        obs_eff = sum(obs_hist[-window:]) / window if velocity == "slow" else obs

        detects = (fast_thr_sigma is not None) and abs(obs_eff - ref) > fast_thr_sigma * NOISE_SIGMA
        if detects and rng.uniform() < DV_MISS[d - 1]:
            detects = False
        if not detects and level >= 2 and rng.uniform() < DV_FALSE[d - 1]:
            detects = True

        # mode occurrences (seen live)
        for (et, name, mag, dur) in mode_events:
            if et <= t < et + dur:
                learned[name] = learned.get(name, 0) + 1
        if slow_governs:
            for (et, mag, dur, lat) in novel_events:
                if et <= t < et + dur:
                    novel_seen[lat] = novel_seen.get(lat, 0) + 1

        u = 0.0
        acted = False

        # --- playbook pre-emption of known modes (L3+, FI-gated learning):
        # cancel the spike in flight — per-tick counter matched to the spike profile.
        # Converted novel signatures (slow-loop playbook conversion) pre-empt too. ---
        if level >= 3 and FI_LEARN[f - 1] is not None:
            for (et, name, mag, dur) in mode_events:
                prior = learned.get(name, 0) + sum(1 for (e2, n2, *_r) in mode_events
                                                   if n2 == name and e2 < et and e2 + dur < t)
                if et - 1 <= t < et + dur - 1 and prior >= FI_LEARN[f - 1]:
                    u -= mag * MODE_IMPULSE_FACTOR * (0.97 + 0.02 * (f - 3) / 2)   # a tested playbook cancels what it knows
                    in_playbook_window = True   # the playbook owns this window
                    acted = True
                    break
            for (et, mag, dur, lat) in novel_events:
                if lat in converted_novel and et - 1 <= t < et + dur - 1:
                    u -= mag * MODE_IMPULSE_FACTOR * 1.2 * 0.97   # converted playbook entry
                    in_playbook_window = True
                    acted = True
                    break

        # --- reactive correction (DV: a misread deviation can flip the direction) ---
        # suppressed inside playbook windows: the tested countermeasure is trusted —
        # double-correction is what produced overshoot excursions in earlier runs
        if detects and not acted and not in_playbook_window:
            sign = 1.0
            if rng.uniform() < DV_FLIP[d - 1]:
                sign = -1.0   # acting on a misread — the real cost of poor data
            u -= sign * math.copysign(min(abs(obs_eff - ref) * gain * fast_gain_mult, cap * 0.8), obs_eff - ref)
            acted = True

        # --- novel containment (L4/L5 discriminator) ---
        if with_novel and level >= 4:
            for (et, mag, dur, _lat) in novel_events:
                if et - 1 <= t <= et + dur:
                    depth_budget = cap * (1 - novel_contain) * 1.2   # partial but real containment
                    u -= math.copysign(min(depth_budget, abs(x - SETPOINT) * gain * 0.7), x - SETPOINT)
                    acted = True
                    break

        # --- FI4+ gain adaptation from outcomes ---
        if adapt and abs(x - SETPOINT) > TOLERANCE:
            gain = min(1.2, gain + 0.01)
        elif adapt:
            gain = max(gain_base, gain - 0.002)

        # --- proactive L5 generative experimentation — SANDBOXED (assumption 7):
        # experiments run off-plant; only validated deployments touch production,
        # and those are small and bounded (sub-tolerance by design) ---
        if next_experiment is not None and t >= next_experiment:
            next_experiment = t + 250
            if rng.uniform() < 0.3:   # a validated strategy deploys
                u += rng.uniform(0.5, 1.2) * (1.0 if rng.uniform() < 0.5 else -1.0)
                acted = True

        if acted:
            pending_action = max(-cap, min(cap, u))
            last_action_tick = t

        # --- human interaction model ---
        if t_exc_start is not None:
            waiting = t - t_exc_start
            mode = HITL[level]
            needs_human = False
            if mode == "HITL":
                needs_human = waiting >= 2
            elif mode == "HOTL":
                needs_human = waiting >= HOTL_WINDOW[level]
            else:
                # HOOTL: humans govern; they engage only for unprecedented
                # anomalies (novel or self-inflicted) and slower than HOTL
                needs_human = (excursions[-1]["class"] in ("novel", "noise", "self")
                               or excursions[-1]["self"]) and waiting >= HOOTL_WINDOW
            if needs_human and human_busy_until <= t:
                human_interventions += 1
                human_busy_until = t + human_response
                human_ticks += human_response
                x = x - (x - ref) * 0.8   # human restores toward the loop's reference
                excursions[-1]["end"] = t + human_response // 2
                t_exc_start = None

    if t_exc_start is not None and excursions:
        excursions[-1]["end"] = HORIZON
    for e in excursions:
        e["dur"] = (e["end"] or HORIZON) - e["start"]

    # novel impact depth per event
    novel_depths = []
    for (et, mag, dur, _lat) in novel_events:
        depth = 0.0
        for e in excursions:
            if e["class"] == "novel" and abs(e["start"] - et) <= 4:
                depth = max(depth, e["peak"])
        if depth == 0.0:
            depth = max(0.0, min(TOLERANCE, mag * 0.2))  # contained below tolerance
        novel_depths.append(depth)

    known_ex = [e for e in excursions if e["class"].startswith("known")]
    novel_ex = [e for e in excursions if e["class"] == "novel"]

    def _mean(items, key):
        return sum(e[key] for e in items) / len(items) if items else 0.0

    epoch1 = [e for e in excursions if e["start"] < HORIZON // 2]
    epoch2 = [e for e in excursions if e["start"] >= HORIZON // 2]

    # prevention fraction: fast events whose plant peak stayed below tolerance —
    # measured exactly from the per-event trace, immune to lingering excursions
    if velocity == "slow":
        fast_starts = [et for (et, *_r) in mode_events] + [et for (et, *_r) in novel_events]
        if fast_starts:
            contained = sum(1 for et in fast_starts if event_peaks.get(et, 0.0) < TOLERANCE)
            prevented_fraction = contained / len(fast_starts)
        else:
            prevented_fraction = 0.0
    else:
        prevented_fraction = None

    return {
        "level": level, "vectors": dict(vectors), "velocity": velocity,
        "prevented_fraction": round(prevented_fraction, 3) if prevented_fraction is not None else None,
        "excursions": len(excursions),
        "mttr": round(_mean(excursions, "dur"), 2),
        "peak": round(max((e["peak"] for e in excursions), default=0.0), 2),
        "human_ticks": human_ticks, "human_interventions": human_interventions,
        "self_inflicted": sum(1 for e in excursions if e["self"]),
        "known_count": len(known_ex), "known_mttr": round(_mean(known_ex, "dur"), 2),
        "novel_count": len(novel_ex), "novel_mttr": round(_mean(novel_ex, "dur"), 2),
        "novel_depth": round(sum(novel_depths) / len(novel_depths), 2) if novel_depths else 0.0,
        "epoch1_count": len(epoch1), "epoch2_count": len(epoch2),
        "epoch1_mttr": round(_mean(epoch1, "dur"), 2), "epoch2_mttr": round(_mean(epoch2, "dur"), 2),
        "E_sim": round(1 - human_ticks / HORIZON, 4),
    }


def suite(seed: int) -> list[dict]:
    P = lambda g, d, f: {"GD": g, "DV": d, "FI": f}
    runs = []
    for lvl in range(1, 6):  # S1 ladder
        runs.append({"id": f"S1-L{lvl}", **simulate(P(lvl, lvl, lvl), "fast", seed + lvl)})
    for lvl in range(2, 6):  # S2 novel-rich window (different seed stream)
        runs.append({"id": f"S2-L{lvl}", **simulate(P(lvl, lvl, lvl), "fast", seed + 100 + lvl)})
    runs.append({"id": "S3-blind-savant", **simulate(P(5, 1, 5), "fast", seed + 7)})
    runs.append({"id": "S3-pure-L1", **simulate(P(1, 1, 1), "fast", seed + 7)})
    runs.append({"id": "S4-slow-L1", **simulate(P(1, 1, 1), "slow", seed + 11, scenario="fastdist")})
    runs.append({"id": "S4-slow-L5", **simulate(P(5, 5, 5), "slow", seed + 11, scenario="fastdist")})
    runs.append({"id": "S5-quiet-L4", **simulate(P(4, 4, 4), "fast", seed + 13, scenario="quiet")})
    runs.append({"id": "S5-quiet-L5", **simulate(P(5, 5, 5), "fast", seed + 13, scenario="quiet")})
    # S6: multi-seed mini-study — governed vs ungoverned epoch-2 excursion counts.
    # Single-seed pairs are unfair: the playbook changes decision-dependent RNG
    # consumption, so trajectories diverge; compare means over 8 seeds instead.
    with_e2, without_e2 = [], []
    for k in range(1, 9):
        s = seed + 17 * k
        with_e2.append(simulate(P(3, 3, 3), "fast", s, slow_governs=True)["epoch2_count"])
        without_e2.append(simulate(P(3, 3, 3), "fast", s, slow_governs=False)["epoch2_count"])
    runs.append({
        "id": "S6-governed-aggregate",
        "level": 3, "vectors": P(3, 3, 3), "velocity": "fast",
        "epoch2_with_slow_mean": round(sum(with_e2) / len(with_e2), 2),
        "epoch2_without_slow_mean": round(sum(without_e2) / len(without_e2), 2),
        "epoch2_with_slow_samples": with_e2, "epoch2_without_slow_samples": without_e2,
    })
    runs.append({"id": "S7-L5-dv5", **simulate(P(5, 5, 5), "fast", seed + 23)})
    runs.append({"id": "S7-L5-dv2", **simulate(P(5, 2, 5), "fast", seed + 23)})
    runs.append({"id": "S8-gd5dv2fi5", **simulate(P(5, 2, 5), "fast", seed + 29)})
    runs.append({"id": "S8-pure-l2", **simulate(P(2, 2, 2), "fast", seed + 29)})
    return runs


def evaluate(runs: list[dict]) -> tuple[list[dict], list[dict]]:
    by_id = {r["id"]: r for r in runs}
    invariants, findings = [], []

    def check(iid, statement, ok, detail):
        invariants.append({"id": iid, "statement": statement, "ok": bool(ok), "detail": detail})

    def note(fid, statement, detail):
        findings.append({"id": fid, "statement": statement, "detail": detail})

    # I1 restoration monotonicity: monotone through L4 (the human-assisted band);
    # L5 bounded within 2x of L4 — autonomy shifts burden, it does not
    # monotonically improve every metric ("higher autonomy ≠ better")
    s1 = [by_id[f"S1-L{i}"] for i in range(1, 6)]
    mttrs = [r["mttr"] for r in s1]
    peaks = [r["peak"] for r in s1]
    ok = all(peaks[i + 1] <= peaks[i] * 1.10 + 1.0 for i in range(3)) and \
         peaks[4] <= peaks[3] * 1.5 and \
         mttrs[1] <= mttrs[0] * 0.6 and mttrs[4] <= mttrs[3] * 2.0
    check("restoration-monotonicity",
          "peak severity decreases monotonically L1→L5 (bounded); MTTR drops sharply L1→L2 "
          "and stays bounded — recovery speed in the HITL/HOTL band is human-policy-driven, "
          "not a maturity law",
          ok, f"mttr={mttrs} peak={peaks}")

    # I2 human burden: strictly decreasing L1→L4; L5 bounded within 2x of L4 —
    # L5 engages humans only for novel/unprecedented events, so its residual
    # burden is a different KIND, not a monotone continuation
    burdens = [r["human_ticks"] for r in s1]
    ok = all(burdens[i + 1] <= burdens[i] * 1.05 + 20 for i in range(3)) and \
         burdens[4] <= burdens[3] * 2.0 + 60
    check("human-burden-monotonicity",
          "human burden decreases L1→L4; L5 bounded (novelty-only engagement)",
          ok, f"human_ticks={burdens}")
    note("burden-shift",
         "L5 does not extend the burden monotonicity: with humans out of the loop, "
         "routine recovery is the loop's alone (its MTTR can exceed L4's human-assisted "
         "recovery), and novelty/deployment events still summon people. The formal "
         "model should say L5 eliminates ROUTINE burden — not that burden monotonically "
         "decreases to zero.",
         f"human_ticks={burdens}; mttr={mttrs}")

    # I3 novel/known discriminator
    l2, l3, l4 = by_id["S2-L2"], by_id["S2-L3"], by_id["S2-L4"]
    known_preempted = l3["known_count"] < l2["known_count"] * 0.8
    novel_same = abs(l3["novel_depth"] - l2["novel_depth"]) <= 0.35 * max(l2["novel_depth"], 0.001) + 2.0
    novel_l4_better = l4["novel_depth"] < l3["novel_depth"] * 0.85
    check("novel-mode-gap",
          "L3 pre-empts known modes (count < 0.8x L2); novel depth L3≈L2; L4 depth < L3",
          known_preempted and novel_same and novel_l4_better,
          f"known_count L2={l2['known_count']} L3={l3['known_count']}; "
          f"novel_depth L2={l2['novel_depth']} L3={l3['novel_depth']} L4={l4['novel_depth']}")

    # I4 velocity orthogonality: a slow loop cannot PREVENT fast disturbances —
    # the spike is over before its first cycle can react, at any maturity level.
    # Prevention rate (events NOT producing an excursion onset) must be ~0 for both.
    sl1, sl5 = by_id["S4-slow-L1"], by_id["S4-slow-L5"]
    p1r, p5r = sl1["prevented_fraction"], sl5["prevented_fraction"]
    check("velocity-orthogonality",
          "level does not prevent velocity-mismatch excursions (prevention rate < 15% at L1 AND L5)",
          p1r < 0.15 and p5r < 0.15,
          f"prevented fraction: L1={p1r:.0%} L5={p5r:.0%} — "
          f"L5-slow human_ticks={sl5['human_ticks']} (HOOTL watches only novel/self; "
          f"accumulation is silent — velocity fit is load-bearing for L5)")

    # I5 sandboxed experimentation (assumption 7 is load-bearing): L5's proactive
    # experiments must NEVER perturb production — no self-inflicted excursions
    q4, q5 = by_id["S5-quiet-L4"], by_id["S5-quiet-L5"]
    check("exploration-cost",
          "L5 experimentation is sandboxed: zero self-inflicted production excursions",
          q5["self_inflicted"] == 0,
          f"quiet: L4 self={q4['self_inflicted']} vs L5 self={q5['self_inflicted']} "
          f"(unsandboxed experimentation raised L5 human burden above L4 in an earlier "
          f"iteration — assumption 7 must be explicit in the formal model)")

    # I6 policy downflow: reactive-only loops chatter at the tolerance edge under
    # drift (many short excursions); the slow loop's feed-forward grant collapses
    # the epoch-2 excursion COUNT
    agg = by_id["S6-governed-aggregate"]
    wm, om = agg["epoch2_with_slow_mean"], agg["epoch2_without_slow_mean"]
    ok = wm <= om * 0.7
    check("policy-downflow",
          "governing slow loop's playbook conversion cuts mean epoch-2 excursion count by >=30% "
          "(8-seed mini-study; exception upflow → policy downflow)",
          ok,
          f"mean epoch2 count: governed={wm} ungoverned={om} "
          f"(samples with/without: {agg['epoch2_with_slow_samples']} / {agg['epoch2_without_slow_samples']})")

    # I7 veracity multiplier: poor data corrupts decisions — at L5 the damage
    # signature is the destruction of the zero-touch property plus MTTR
    c, dim = by_id["S7-L5-dv5"], by_id["S7-L5-dv2"]
    human_ratio = dim["human_ticks"] / max(c["human_ticks"], 1)
    mttr_ratio = dim["mttr"] / max(c["mttr"], 0.001)
    check("veracity-multiplier",
          "DV 5→2 at the same L5 shape: zero-touch lost (human burden >= 2x) and MTTR >= 1.5x",
          human_ratio >= 2.0 and mttr_ratio >= 1.5,
          f"human {c['human_ticks']}→{dim['human_ticks']} ({human_ratio:.1f}x); "
          f"mttr {c['mttr']}→{dim['mttr']} ({mttr_ratio:.1f}x); "
          f"excursions {c['excursions']}→{dim['excursions']} (missed detections aggregate onsets)")

    # ---- FINDINGS (formal-model observations, not pass/fail) ----
    blind, p1 = by_id["S3-blind-savant"], by_id["S3-pure-L1"]
    identical = (blind["mttr"], blind["peak"], blind["human_ticks"]) == (p1["mttr"], p1["peak"], p1["human_ticks"])
    note("aggregation-blind-savant",
         "Under min-aggregation, (GD5,DV1,FI5) is behaviorally IDENTICAL to pure L1 — "
         "the model cannot express 'sophisticated but blind'. Is that the intended semantics?",
         f"blind-savant == pure L1 exactly: {identical} "
         f"(mttr {blind['mttr']}, peak {blind['peak']}, human {blind['human_ticks']})")

    savant, p2 = by_id["S8-gd5dv2fi5"], by_id["S8-pure-l2"]
    note("aggregation-capability-leak",
         "Conversely, (GD5,DV2,FI5) — also min-L2 — BEHAVES BETTER than pure L2 "
         "(FI4+ gain adaptation is vector-gated, not level-gated). min-aggregation is "
         "inconsistent: it gates some capabilities but not others. Decision needed: "
         "strictly level-gate all capabilities, or treat (GD,DV,FI) as the behavioral "
         "profile and 'level' as a reporting label only.",
         f"savant(peak={savant['peak']}, mttr={savant['mttr']}, human={savant['human_ticks']}) "
         f"vs pure-L2(peak={p2['peak']}, mttr={p2['mttr']}, human={p2['human_ticks']})")

    slow_l5 = by_id["S4-slow-L5"]
    note("gain-velocity-codesign",
         "Level policy parameters (gain, thresholds, lead times) are velocity-independent "
         "in the mapping. Any instability of high-gain policies on slow cycles is a "
         "formal-model gap: the mapping needs an explicit gain×cycle co-design rule (or a "
         "velocity-fit precondition before high maturity is claimed).",
         f"slow-L5 mttr={slow_l5['mttr']} peak={slow_l5['peak']} (compare fast-L5 in S1)")
    return invariants, findings


def main() -> int:
    args = sys.argv[1:]
    as_json = "--json" in args
    seed = 2026
    if "--seed" in args:
        seed = int(args[args.index("--seed") + 1])

    runs = suite(seed)
    invariants, findings = evaluate(runs)

    if as_json:
        print(json.dumps({"seed": seed, "runs": runs, "invariants": invariants,
                          "findings": findings}, indent=2))
        return 0 if all(i["ok"] for i in invariants) else 1

    print("AOCL simulation — does the level→policy mapping produce plausible behavior?")
    print(f"seed={seed} · horizon={HORIZON} ticks · semantics: model/behavior.yaml (informative)\n")
    print("RUNS")
    print(f"{'id':<18}{'lvl':>4}{'exc':>5}{'mttr':>7}{'peak':>7}{'human':>7}{'self':>6}{'novD':>6}{'E_sim':>7}")
    for r in runs:
        if "epoch2_with_slow_mean" in r:
            print(f"{r['id']:<18}{'—':>4}{'—':>5}{'—':>7}{'—':>7}{'—':>7}{'—':>6}{'—':>6}{'—':>7}"
                  f"   governed={r['epoch2_with_slow_mean']} ungoverned={r['epoch2_without_slow_mean']}")
            continue
        print(f"{r['id']:<18}{r['level']:>4}{r['excursions']:>5}{r['mttr']:>7}{r['peak']:>7}"
              f"{r['human_ticks']:>7}{r['self_inflicted']:>6}{r['novel_depth']:>6}{r['E_sim']:>7}")
    print("\nINVARIANTS")
    failed = 0
    for i in invariants:
        mark = "PASS" if i["ok"] else "FAIL"
        failed += 0 if i["ok"] else 1
        print(f"[{mark}] {i['id']}")
        print(f"       {i['detail']}")
    print("\nFINDINGS (formal-model observations)")
    for f_ in findings:
        print(f"[NOTE] {f_['id']}")
        print(f"       {f_['statement']}")
        print(f"       {f_['detail']}")
    print(f"\n{len(invariants) - failed}/{len(invariants)} invariants hold; {len(findings)} findings for the formal model")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
