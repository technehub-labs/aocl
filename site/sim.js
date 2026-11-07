/* AOCL simulation engine (JS port of tools/sim_check.py's simulate() — same seeded
 * semantics, so a seed reproduces the same trace in the browser and in CI).
 * Deterministic xorshift; no dependencies. */
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory();
  else root.AOCLSim = factory();
})(typeof self !== "undefined" ? self : this, function () {
  "use strict";

  function copysign(v, s) { return Math.sign(s) * Math.abs(v); }

  function LCG(seed) {
    this.state = seed >>> 0 || 1;
  }
  LCG.prototype.nextU32 = function () {
    let x = this.state;
    x ^= (x << 13) >>> 0; x >>>= 0;
    x ^= x >>> 17;
    x ^= (x << 5) >>> 0; x >>>= 0;
    this.state = x;
    return x;
  };
  LCG.prototype.uniform = function (lo, hi) {
    lo = lo === undefined ? 0 : lo; hi = hi === undefined ? 1 : hi;
    return lo + (hi - lo) * (this.nextU32() / 0xFFFFFFFF);
  };
  LCG.prototype.normal = function (mu, sigma) {
    mu = mu || 0; sigma = sigma || 1;
    const u1 = Math.max(this.uniform(), 1e-12), u2 = this.uniform();
    return mu + sigma * Math.sqrt(-2 * Math.log(u1)) * Math.cos(2 * Math.PI * u2);
  };
  LCG.prototype.choice = function (items) { return items[this.nextU32() % items.length]; };

  const DV_NOISE = [1.00, 0.70, 0.45, 0.25, 0.10];
  const DV_MISS = [0.35, 0.20, 0.10, 0.04, 0.01];
  const DV_FALSE = [0.02, 0.015, 0.01, 0.005, 0.002];
  const DV_FLIP = [0.30, 0.18, 0.08, 0.02, 0.00];
  const FI_LEARN = [null, null, 3, 2, 1];
  const FI_ADAPT = [false, false, false, true, true];
  const GD_ADAPT = [false, false, false, false, true];
  const LEVEL = {
    1: { thr: null, gain: 0.0, contain: 1.0, lead: 0 },
    2: { thr: 2.0, gain: 0.6, contain: 1.0, lead: 0 },
    3: { thr: 2.0, gain: 0.8, contain: 1.0, lead: 8 },
    4: { thr: 1.5, gain: 0.9, contain: 0.5, lead: 10 },
    5: { thr: 1.2, gain: 1.0, contain: 0.15, lead: 14 },
  };
  const VELOCITY = { fast: [1, 10.0], tactical: [10, 12.0], slow: [100, 8.0] };
  const HITL = { 1: "HITL", 2: "HITL", 3: "HOTL", 4: "HOTL", 5: "HOOTL" };
  const HOTL_WINDOW = 10, HOOTL_WINDOW = 6, HUMAN_RESPONSE = 30;
  const HORIZON = 3000, SETPOINT = 0.0, NOISE_SIGMA = 1.0, TOLERANCE = 3.0;
  const DRIFT = [1200, 2400, 60.0], MODE_IMPULSE = 0.22;
  const KNOWN_MODES = [["A", 420, 26.0, 6], ["B", 730, 17.0, 4]];
  const NOVEL_RATE = 6.0 / 1000, NOVEL_MAG = [15.0, 30.0];

  /** params: {GD, DV, FI, velocity, seed, scenario, slowGoverns, humanResponse} */
  function simulate(p) {
    const g = p.GD, d = p.DV, f = p.FI;
    const level = Math.min(g, d, f);
    const cfg = LEVEL[level];
    const [cycle, cap] = VELOCITY[p.velocity || "fast"];
    const seed = p.seed >>> 0;
    const rng = new LCG(seed);
    const scenario = p.scenario || "baseline";
    const slowGoverns = !!p.slowGoverns;
    const humanResponse = p.humanResponse || HUMAN_RESPONSE;
    const horizon = HORIZON;

    let x = 0.0, pending = 0.0, ref = SETPOINT;
    let driftFF = 0.0;
    let thrSigma = cfg.thr, gain = cfg.gain, fastGainMult = 1.0;
    let tExcStart = null;
    const excursions = [];
    let humanBusyUntil = 0, humanTicks = 0, humanInterventions = 0;
    const learned = {}; const novelSeen = {}; const converted = new Set();
    const preempted = new Set();
    const eventPeaks = {};
    let lastActionTick = -99;
    let inPlaybook = false;
    const obsHist = [];
    const proactive = GD_ADAPT[g - 1] && f >= 5;
    let nextExperiment = proactive ? 400 : null;

    const driftActive = scenario === "baseline" || scenario === "drift";
    const withModes = scenario === "baseline" || scenario === "fastdist";
    const withNovel = scenario === "baseline" || scenario === "fastdist";

    function driftRate(t) {
      const [d0, d1, mag] = DRIFT;
      return driftActive && t >= d0 && t <= d1 ? mag / (d1 - d0) : 0.0;
    }

    const modeEvents = [];
    if (withModes) {
      for (const [name, period, mag, dur] of KNOWN_MODES) {
        let t = Math.floor(period / 3);
        while (t < horizon) {
          modeEvents.push([t, name, mag, dur]);
          t += Math.floor(period * (0.9 + 0.2 * rng.uniform()));
        }
      }
    }
    const novelEvents = [];
    if (withNovel) {
      let t = 150, li = 0;
      while (t < horizon) {
        if (rng.uniform() < NOVEL_RATE * 100) {
          novelEvents.push([t, rng.uniform(NOVEL_MAG[0], NOVEL_MAG[1]),
            Math.floor(NOVEL_DUR_LO() + rng.uniform() * (NOVEL_DUR_HI() - NOVEL_DUR_LO())), li % 3]);
          li++;
        }
        t += 100;
      }
    }
    function NOVEL_DUR_LO() { return 3; } function NOVEL_DUR_HI() { return 8; }

    function impulse(t) {
      let tot = 0;
      for (const [et, , mag, dur] of modeEvents) if (et <= t && t < et + dur) tot += mag * MODE_IMPULSE;
      for (const [et, mag, dur] of novelEvents) if (et <= t && t < et + dur) tot += mag * MODE_IMPULSE * 1.2;
      return tot;
    }
    function trackPeaks(t, xv) {
      for (const [et, , , dur] of modeEvents) if (et <= t && t <= et + dur + 2) eventPeaks[et] = Math.max(eventPeaks[et] || 0, Math.abs(xv));
      for (const [et, , dur] of novelEvents) if (et <= t && t <= et + dur + 2) eventPeaks[et] = Math.max(eventPeaks[et] || 0, Math.abs(xv));
    }

    const trace = [];   // per-tick record for the canvas: {x, ref, imp, human, exc}
    for (let t = 0; t < horizon; t++) {
      inPlaybook = false;
      if (slowGoverns && t === Math.floor(horizon / 2)) {
        if (FI_LEARN[f - 1] !== null || level >= 3) {
          fastGainMult = 1.0;
          driftFF = driftRate(Math.floor(horizon / 2));
          for (const lat in novelSeen) if (novelSeen[lat] >= 1) converted.add(parseInt(lat, 10));
        }
      }
      // plant evolves (integrator)
      x += pending - driftFF + impulse(t) + driftRate(t) + rng.normal(0, NOISE_SIGMA * 0.35);
      pending = 0;
      trackPeaks(t, x);

      const excNow = Math.abs(x - SETPOINT) > TOLERANCE;
      if (excNow && tExcStart === null) {
        tExcStart = t;
        let magAt = 0, caused = "noise";
        for (const [et, name, mag, dur] of modeEvents) if (et - 2 <= t && t <= et + dur + 2 && mag > magAt) { magAt = mag; caused = "known:" + name; }
        for (const [et, mag, dur] of novelEvents) if (et - 2 <= t && t <= et + dur + 2 && mag > magAt) { magAt = mag; caused = "novel"; }
        if (driftRate(t) > 0 && caused === "noise") caused = "drift";
        excursions.push({ start: t, cls: caused, peak: 0, end: null, self: caused === "noise" && t - lastActionTick <= 3 });
      }
      if (tExcStart !== null) {
        excursions[excursions.length - 1].peak = Math.max(excursions[excursions.length - 1].peak, Math.abs(x - SETPOINT));
        if (!excNow) { excursions[excursions.length - 1].end = t; tExcStart = null; }
      }
      trace.push({ t, x, imp: impulse(t), human: t < humanBusyUntil, exc: excNow });

      if (t % cycle !== 0) continue;
      const obs = x + rng.normal(0, NOISE_SIGMA * DV_NOISE[d - 1] * 0.8);
      obsHist.push(obs);
      const w = Math.min(obsHist.length, Math.max(Math.floor(cycle / 2), 5));
      const obsEff = p.velocity === "slow" ? obsHist.slice(-w).reduce((a, b) => a + b, 0) / w : obs;

      let detects = thrSigma !== null && Math.abs(obsEff - ref) > thrSigma * NOISE_SIGMA;
      if (detects && rng.uniform() < DV_MISS[d - 1]) detects = false;
      if (!detects && level >= 2 && rng.uniform() < DV_FALSE[d - 1]) detects = true;

      for (const [et, name] of modeEvents) if (et <= t && t < et + dur2(et)) learned[name] = (learned[name] || 0) + 1;
      function dur2(et) { const ev = modeEvents.find((e) => e[0] === et); return ev ? ev[3] : 0; }
      if (slowGoverns) for (const [et, , , lat] of novelEvents) if (et <= t && t < et + evDur(novelEvents, et)) novelSeen[lat] = (novelSeen[lat] || 0) + 1;

      let u = 0, acted = false;

      if (level >= 3 && FI_LEARN[f - 1] !== null) {
        for (const [et, name, mag, dur] of modeEvents) {
          let prior = learned[name] || 0;
          for (const [e2, n2, , d2] of modeEvents) if (n2 === name && e2 < et && e2 + d2 < t) prior++;
          if (et - 1 <= t && t < et + dur - 1 && prior >= FI_LEARN[f - 1]) {
            u -= mag * MODE_IMPULSE * (0.97 + 0.02 * (f - 3) / 2);
            inPlaybook = true;
            acted = true;
            break;
          }
        }
        if (!inPlaybook) {
          for (const [et, mag, dur, lat] of novelEvents) {
            if (converted.has(lat) && et - 1 <= t && t < et + dur - 1) {
              u -= mag * MODE_IMPULSE * 1.2 * 0.97;
              inPlaybook = true;
              acted = true;
              break;
            }
          }
        }
      }

      if (detects && !acted && !inPlaybook) {
        let sign = 1;
        if (rng.uniform() < DV_FLIP[d - 1]) sign = -1;
        u -= sign * copysign(Math.min(Math.abs(obsEff - ref) * gain * fastGainMult, cap * 0.8), obsEff - ref);
        acted = true;
      }

      if (withNovel && level >= 4) {
        for (const [et, mag, dur] of novelEvents) {
          if (et - 1 <= t && t <= et + dur) {
            const budget = cap * (1 - cfg.contain) * 1.2;
            u -= copysign(Math.min(budget, Math.abs(x - SETPOINT) * gain * 0.7), x - SETPOINT);
            acted = true;
            break;
          }
        }
      }

      if (FI_ADAPT[f - 1]) {
        if (Math.abs(x - SETPOINT) > TOLERANCE) gain = Math.min(1.2, gain + 0.01);
        else gain = Math.max(cfg.gain, gain - 0.002);
      }

      if (nextExperiment !== null && t >= nextExperiment) {
        nextExperiment = t + 250;
        if (rng.uniform() < 0.3) { u += rng.uniform(0.5, 1.2) * (rng.uniform() < 0.5 ? 1 : -1); acted = true; }
      }

      if (acted) {
        pending = Math.max(-cap, Math.min(cap, u));
        lastActionTick = t;
      }

      if (tExcStart !== null) {
        const waiting = t - tExcStart;
        const mode = HITL[level];
        let needs = false;
        if (mode === "HITL") needs = waiting >= 2;
        else if (mode === "HOTL") needs = waiting >= HOTL_WINDOW;
        else needs = (excursions[excursions.length - 1].cls === "novel" || excursions[excursions.length - 1].cls === "noise") && waiting >= HOOTL_WINDOW;
        if (needs && humanBusyUntil <= t) {
          humanInterventions++; humanBusyUntil = t + humanResponse; humanTicks += humanResponse;
          x = x - (x - ref) * 0.8;
          excursions[excursions.length - 1].end = t + Math.floor(humanResponse / 2);
          tExcStart = null;
        }
      }
    }
    if (tExcStart !== null && excursions.length) excursions[excursions.length - 1].end = horizon;
    for (const e of excursions) e.dur = (e.end === null ? horizon : e.end) - e.start;

    const novelDepth = [];
    for (const [et] of novelEvents) {
      let depth = 0;
      for (const e of excursions) if (e.cls === "novel" && Math.abs(e.start - et) <= 4) depth = Math.max(depth, e.peak);
      if (depth === 0) depth = Math.min(TOLERANCE, 6);
      novelDepth.push(depth);
    }
    const knownEx = excursions.filter((e) => e.cls.startsWith("known"));
    const mean = (arr, k) => (arr.length ? arr.reduce((a, e) => a + e[k], 0) / arr.length : 0);
    const epoch1 = excursions.filter((e) => e.start < horizon / 2);
    const epoch2 = excursions.filter((e) => e.start >= horizon / 2);

    // prevention fraction (slow loops)
    let prevented = null;
    if (p.velocity === "slow") {
      const starts = [...modeEvents.map((e) => e[0]), ...novelEvents.map((e) => e[0])];
      prevented = starts.length
        ? starts.filter((et) => (eventPeaks[et] || 0) < TOLERANCE).length / starts.length
        : 0;
    }

    return {
      level, vectors: { GD: g, DV: d, FI: f }, velocity: p.velocity || "fast",
      excursions: excursions.length,
      excursionList: excursions,
      mttr: +mean(excursions, "dur").toFixed(2),
      peak: +Math.max(...excursions.map((e) => e.peak), 0).toFixed(2),
      humanTicks: humanTicks, humanInterventions: humanInterventions,
      selfInflicted: excursions.filter((e) => e.self).length,
      novelDepth: +(novelDepth.length ? novelDepth.reduce((a, b) => a + b, 0) / novelDepth.length : 0).toFixed(2),
      epoch1Count: epoch1.length, epoch2Count: epoch2.length,
      ESim: +(1 - humanTicks / horizon).toFixed(4),
      preventedFraction: prevented === null ? null : +prevented.toFixed(3),
      trace,
    };
    function evDur(events, et) { const ev = events.find((e) => e[0] === et); return ev ? ev[2] || ev[3] : 0; }
  }

  /* ---------------- planner (port of aocl.realization fit/plan) ---------------- */

  function leastSquares(xs, ys) {
    const n = xs.length;
    const mx = xs.reduce((a, b) => a + b, 0) / n, my = ys.reduce((a, b) => a + b, 0) / n;
    let sxy = 0, sxx = 0;
    for (let i = 0; i < n; i++) { sxy += (xs[i] - mx) * (ys[i] - my); sxx += (xs[i] - mx) ** 2; }
    const b = sxx ? sxy / sxx : 0, a = my - b * mx;
    const ssTot = ys.reduce((acc, y) => acc + (y - my) ** 2, 0);
    const ssRes = ys.reduce((acc, y, i) => acc + (y - (a + b * xs[i])) ** 2, 0);
    const r2 = ssTot ? 1 - ssRes / ssTot : 1;
    return { a, b, r2 };
  }

  function fitCurveShape(points) {
    const pts = points.slice().sort((p, q) => p.level - q.level)
      .map((p) => [Number(p.level), Number(p.cost)]);
    if (pts.length < 3) throw new Error("at least 3 calibrated cost points are required");
    const xs = pts.map((p) => p[0]), ys = pts.map((p) => p[1]);
    const r2of = (pred) => {
      const my = ys.reduce((a, b) => a + b, 0) / ys.length;
      const ssTot = ys.reduce((a, y) => a + (y - my) ** 2, 0);
      const ssRes = ys.reduce((a, y, i) => a + (y - pred(xs[i])) ** 2, 0);
      return ssTot ? 1 - ssRes / ssTot : 1;
    };
    const lin = leastSquares(xs, ys);
    const lg = leastSquares(xs.map((x) => Math.log(x)), ys);
    const cands = [
      { shape: "linear", r2: lin.r2, params: { a: lin.a, b: lin.b },
        project: (l) => Math.max(lin.a + lin.b * l, 0) },
      { shape: "logarithmic", r2: lg.r2, params: { a: lg.a, b: lg.b },
        project: (l) => Math.max(lg.a + lg.b * Math.log(l), 0) },
    ];
    if (ys.every((y) => y > 0)) {
      const ex = leastSquares(xs, ys.map((y) => Math.log(y)));
      const a = Math.exp(ex.a), b = ex.b;
      cands.push({ shape: "exponential", r2: r2of((x) => a * Math.exp(b * x)),
                   params: { a: a, b: b }, project: (l) => Math.max(a * Math.exp(b * l), 0) });
    }
    const order = ["linear", "logarithmic", "exponential"];
    cands.sort((c1, c2) => (Math.round(c2.r2 * 1e4) - Math.round(c1.r2 * 1e4))
             || (order.indexOf(c1.shape) - order.indexOf(c2.shape)));
    const best = cands[0];
    return { shape: best.shape, r2: +best.r2.toFixed(4), params: best.params,
             candidates: cands, project: best.project };
  }

  const REF_EFFORT = { 1: 1.1519, 2: 1.6487, 3: 2.7183, 4: 5.4739, 5: 37.5862 };
  const AOCL_RULESET = "1.0.0";

  function planInvestment(p) {
    const budget = p.budget;
    if (budget === undefined || budget === null || budget < 0) {
      throw new Error("budget must be a non-negative number");
    }
    let costFit, cumCost, costSource;
    if (p.costPoints && p.costPoints.length >= 3) {
      costFit = fitCurveShape(p.costPoints);
      cumCost = {};
      p.costPoints.forEach((pt) => { cumCost[Number(pt.level)] = Number(pt.cost); });
      costSource = "calibrated";
    } else {
      costFit = { shape: "reference-illustration", r2: null };
      cumCost = Object.assign({}, REF_EFFORT);
      costSource = "uncalibrated reference illustration (Table 1.1)";
    }
    let valueSource, cumValue, projectValue;
    if (p.valuePoints && p.valuePoints.length >= 3) {
      const vfit = fitCurveShape(p.valuePoints.map((pt) => ({ level: pt.level, cost: pt.value })));
      cumValue = {};
      p.valuePoints.forEach((pt) => { cumValue[Number(pt.level)] = Number(pt.value); });
      valueSource = "calibrated (" + vfit.shape + ", R2=" + vfit.r2 + ")";
      projectValue = (l) => Math.max(vfit.project(l), 0);
    } else {
      valueSource = "uncalibrated research value models (log through L3, exponential from L3)";
      projectValue = (l) => (l <= 3 ? Math.log(1 + l) / Math.log(6)
                              : Math.exp(l - 3) / Math.exp(0) * Math.log(4) / Math.log(6));
      cumValue = {};
      for (let l = 1; l <= 5; l++) cumValue[l] = +projectValue(l).toFixed(4);
    }
    const rows = [];
    for (let l = 1; l <= 5; l++) {
      const keys = Object.keys(cumCost).map(Number);
      const cost = cumCost[l] !== undefined ? cumCost[l] : cumCost[Math.max.apply(null, keys)];
      const vals = Object.keys(cumValue).map(Number);
      const value = cumValue[l] !== undefined ? cumValue[l] : Math.max.apply(null, vals);
      rows.push({ level: "L" + l, cumulative_cost: +cost.toFixed(3),
                  projected_value: +value.toFixed(3), within_budget: cost <= budget,
                  benefit_per_cost: cost ? +(value / cost).toFixed(3) : null });
    }
    const reachable = rows.filter((r) => r.within_budget);
    const maxLevel = reachable.length
      ? Math.max.apply(null, reachable.map((r) => Number(r.level.slice(1)))) : 0;
    const keys = Object.keys(cumCost).map(Number).sort(function (a, b) { return a - b; });
    const marginal = [];
    for (let i = 0; i < keys.length - 1; i++) {
      const a = keys[i], b = keys[i + 1];
      const dc = cumCost[b] - cumCost[a], dv = (cumValue[b] || 0) - (cumValue[a] || 0);
      marginal.push({ transition: "L" + a + " to L" + b, marginal_cost: +dc.toFixed(3),
                      marginal_value: +dv.toFixed(3),
                      value_per_cost: dc ? +(dv / dc).toFixed(3) : null });
    }
    return { ruleset_version: AOCL_RULESET, budget: budget,
             cost_source: costSource, cost_shape: costFit.shape, cost_fit_r2: costFit.r2,
             value_source: valueSource, rows: rows,
             max_level_within_budget: "L" + maxLevel, marginal_analysis: marginal,
             status: "informative planning support — calibrate before investment decisions" };
  }

  return { simulate, LCG, LEVEL, VELOCITY, HITL, HORIZON, SETPOINT, TOLERANCE, DRIFT,
           fitCurveShape, planInvestment };
});
