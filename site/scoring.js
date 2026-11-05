/* AOCL scoring + realization engine (JavaScript mirror of src/aocl).
 * UMD: window.AOCL in the browser, module.exports in Node (no build step).
 * Parity is enforced by tools/corpus_check.js and tools/site_selftest.js against
 * tests/corpus.json — any drift from the Python engine blocks release.
 */
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory();
  else root.AOCL = factory();
})(typeof self !== "undefined" ? self : this, function () {
  "use strict";

  var RULESET_VERSION = "1.0.0";
  var VECTORS = [
    ["GD", "Goal Decisioning"],
    ["DV", "Data Veracity"],
    ["FI", "Feedback Intelligence"],
  ];
  var LEVEL_NAMES = { 1: "Static", 2: "Reactive", 3: "Proactive", 4: "Predictive", 5: "Pre-emptive" };
  var FRONTIERS = {
    1: ["Automation Frontier", "instrumentation, orchestration, rule engines — barrier: organizational trust"],
    2: ["Prediction Frontier", "data science capability, forecast models — barrier: data quality and feature engineering"],
    3: ["Cognition Frontier", "AI/ML infrastructure, model governance, MLOps, explainability — barriers: AI talent scarcity, non-stationary environments"],
    4: ["Autonomy Frontier", "experimentation infrastructure, digital twins, causal inference — barrier: delegating goal-setting to machines"],
  };
  var VELOCITIES = ["fast", "tactical", "slow"];
  var HITL = { 1: "HITL", 2: "HITL", 3: "HOTL", 4: "HOTL", 5: "HOOTL" };

  /* Assessment questionnaire (derived from the source document's per-level vector
   * characteristics; see model/questions.yaml). answers[level-1] = boolean for L1..L5. */
  var QUESTIONS = {
    GD: [
      "Goals are fixed; the loop executes rigid rules against them.",
      "Goals adjust after events; the loop re-evaluates against updated objectives post-hoc.",
      "The loop anticipates scenario-based objectives and self-optimizes within its policy bounds.",
      "Objectives are optimized by AI/ML; the loop works toward anticipatory goals.",
      "The loop sets and revises its own goals from high-level intent and learns through experimentation.",
    ],
    DV: [
      "Data is static; trust in it is low and unverified.",
      "Data arrives in real time with moderate, unquantified accuracy.",
      "Data is context-aware and held to a high consistency bar.",
      "Data is multi-source and cleansed before use in decisions.",
      "The loop curates its own data ecosystem, adapting sources to need.",
    ],
    FI: [
      "Feedback is basic and not integrated into control.",
      "Feedback corrects, but with delay after the event.",
      "Predictive analytics mitigate risk before manifestation.",
      "Prescriptive insights drive efficiency; models learn continuously.",
      "The loop refines and innovates autonomously — including on its own learning strategy.",
    ],
  };

  function scoreVector(code, answers) {
    /* Ladder: highest n such that ALL items for levels 1..n are true. */
    var level = 0;
    for (var i = 0; i < 5; i++) {
      if (answers[i]) level = i + 1;
      else break;
    }
    return level;
  }

  function overallLevel(vectorScores) {
    var min = 5;
    VECTORS.forEach(function (v) {
      if (vectorScores[v[0]] < min) min = vectorScores[v[0]];
    });
    return min;
  }

  function frontier(level) {
    return FRONTIERS[level] || null;
  }

  function recommendedModel(level, velocity) {
    if (VELOCITIES.indexOf(velocity) < 0) throw new Error("velocity must be fast|tactical|slow");
    if (level <= 3) return "MAPE";
    return velocity === "fast" ? "MAPE" : "OODA";
  }

  function recommendedMove(level) {
    return {
      1: "stabilize: automate thresholds to reach the Automation Frontier (reactive control)",
      2: "predict: add trend analysis and forecasting to cross the Prediction Frontier",
      3: "learn: introduce AI/ML strategy generation to cross the Cognition Frontier",
      4: "delegate: extend autonomy toward goal-setting across the Autonomy Frontier",
      5: "hold: govern at the strategic level; re-review on cadence",
    }[level];
  }

  function gapNotes(vectorScores, current) {
    var notes = [];
    var level = overallLevel(vectorScores);
    var laggards = VECTORS.filter(function (v) { return vectorScores[v[0]] === level; }).map(function (v) { return v[1]; });
    if (laggards.length < VECTORS.length) {
      notes.push("weakest link: " + laggards.join(", ") + " at L" + level + " — advance the lagging vector(s) before raising the overall level");
    }
    if (level < 5) {
      var f = FRONTIERS[level];
      notes.push("next: " + f[0] + " — " + f[1]);
    }
    if (current !== null && current !== undefined) {
      var headroom = level - current;
      if (headroom > 0) notes.push("headroom: assessed level exceeds current operation by " + headroom + "; raise after clean review cycles");
      else if (headroom < 0) notes.push("over-assessment: operating level exceeds assessed level by " + -headroom + "; reassess the vectors or step the operation down");
      else notes.push("operating level matches assessment: hold and review");
    }
    return notes;
  }

  function assess(vectorScores, current, velocity) {
    velocity = velocity || "tactical";
    var level = overallLevel(vectorScores);
    return {
      rulesetVersion: RULESET_VERSION,
      vectorLevels: { GD: vectorScores.GD, DV: vectorScores.DV, FI: vectorScores.FI },
      level: level,
      currentLevel: current === undefined ? null : current,
      velocity: velocity,
      notes: gapNotes(vectorScores, current === undefined ? null : current),
      frontier: level < 5 ? FRONTIERS[level][0] : null,
      recommendedDecisionModel: recommendedModel(level, velocity),
      hitl: HITL[level],
      recommendedMove: recommendedMove(level),
    };
  }

  /* ---------------- Realization model (informative heuristic) ---------------- */

  var REFERENCE_POINTS = [
    { level: "L1", name: "Static", E: 0.10, C: 0.10, R: 0.14 },
    { level: "L2", name: "Reactive", E: 0.30, C: 0.40, R: 0.50 },
    { level: "L3", name: "Proactive", E: 0.60, C: 0.80, R: 1.00 },
    { level: "L4", name: "Predictive", E: 0.80, C: 1.50, R: 1.70 },
    { level: "L5", name: "Pre-emptive", E: 0.95, C: 3.50, R: 3.63 },
  ];

  function checkRange(v, lo, hi, name) {
    if (typeof v !== "number" || isNaN(v) || v < lo || v > hi) {
      throw new Error(name + " must be in [" + lo + ", " + hi + "], got " + v);
    }
    return v;
  }

  function realize(E, C, Vd) {
    Vd = Vd === undefined ? 1.0 : Vd;
    checkRange(E, 0, 1, "E");
    checkRange(Vd, 0, 1, "Vd");
    if (C < 0) throw new Error("C must be >= 0, got " + C);
    return Math.sqrt(E * E + (C * Vd) * (C * Vd));
  }

  function effort(R) {
    return Math.exp(R);
  }

  function experienceFromComponents(Ed, Em, Eo, Ex) {
    return Math.min(Math.sqrt(Ed * Ed + Em * Em + Eo * Eo + Ex * Ex), 1.0);
  }

  function complexityFromComponents(Cs, Cd, Cm, Cc) {
    return Math.sqrt(Cs * Cs + Cd * Cd + Cm * Cm + Cc * Cc);
  }

  function sensitivity(E, C, Vd) {
    Vd = Vd === undefined ? 1.0 : Vd;
    var R = realize(E, C, Vd);
    if (R === 0) return { dR_dE: 0, dR_dC: 0, dR_dVd: 0, R: 0 };
    return { dR_dE: E / R, dR_dC: (C * Vd * Vd) / R, dR_dVd: (C * C * Vd) / R, R: R };
  }

  function requiredComplexity(E, targetR, Vd) {
    Vd = Vd === undefined ? 1.0 : Vd;
    if (targetR < E) throw new Error("target R below experience E — R >= E always");
    return Math.sqrt(targetR * targetR - E * E) / Vd;
  }

  function requiredExperience(C, targetR, Vd) {
    Vd = Vd === undefined ? 1.0 : Vd;
    var inner = targetR * targetR - (C * Vd) * (C * Vd);
    if (inner < 0) throw new Error("target R below the complexity term C*Vd — R >= C*Vd always");
    return Math.min(Math.sqrt(inner), 1.0);
  }

  function nearestReference(R) {
    var best = REFERENCE_POINTS[0];
    REFERENCE_POINTS.forEach(function (p) {
      if (Math.abs(p.R - R) < Math.abs(best.R - R)) best = p;
    });
    return best;
  }

  function valueBand(level) {
    return level <= 3 ? "logarithmic" : "exponential";
  }

  function valueLogarithmic(level, vMax, alpha) {
    vMax = vMax === undefined ? 1 : vMax;
    alpha = alpha === undefined ? 1 : alpha;
    return (vMax * Math.log(1 + alpha * level)) / Math.log(1 + alpha * 5);
  }

  function valueExponential(level, v0, beta) {
    v0 = v0 === undefined ? 1 : v0;
    beta = beta === undefined ? 1 : beta;
    return v0 * Math.exp(beta * (level - 3));
  }

  return {
    RULESET_VERSION: RULESET_VERSION,
    VECTORS: VECTORS,
    LEVEL_NAMES: LEVEL_NAMES,
    FRONTIERS: FRONTIERS,
    VELOCITIES: VELOCITIES,
    HITL: HITL,
    QUESTIONS: QUESTIONS,
    REFERENCE_POINTS: REFERENCE_POINTS,
    scoreVector: scoreVector,
    overallLevel: overallLevel,
    frontier: frontier,
    recommendedModel: recommendedModel,
    recommendedMove: recommendedMove,
    gapNotes: gapNotes,
    assess: assess,
    realize: realize,
    effort: effort,
    experienceFromComponents: experienceFromComponents,
    complexityFromComponents: complexityFromComponents,
    sensitivity: sensitivity,
    requiredComplexity: requiredComplexity,
    requiredExperience: requiredExperience,
    nearestReference: nearestReference,
    valueBand: valueBand,
    valueLogarithmic: valueLogarithmic,
    valueExponential: valueExponential,
  };
});
