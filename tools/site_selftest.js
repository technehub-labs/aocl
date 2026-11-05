#!/usr/bin/env node
"use strict";
/* Site self-test: unit-tests the JS engine and asserts parity with the Python
 * engine's RULESET_VERSION (regex cross-grep, mirroring the upstream pattern). */
const fs = require("fs");
const path = require("path");
const AOCL = require("../site/scoring.js");
const Modeler = require("../site/modeler.js");

let failures = 0;
function check(name, cond) {
  if (!cond) { console.log(`site_selftest: FAIL ${name}`); failures++; }
}

/* --- engine ladder --- */
check("ladder all-true = 5", AOCL.scoreVector("GD", [true, true, true, true, true]) === 5);
check("ladder gap = below gap", AOCL.scoreVector("DV", [true, true, false, true, true]) === 2);
check("ladder none = 0", AOCL.scoreVector("FI", [false, false, false, false, false]) === 0);
check("weakest link", AOCL.overallLevel({ GD: 3, DV: 4, FI: 2 }) === 2);
check("weakest link all-5", AOCL.overallLevel({ GD: 5, DV: 5, FI: 5 }) === 5);
check("frontier names", AOCL.frontier(1)[0] === "Automation Frontier" && AOCL.frontier(4)[0] === "Autonomy Frontier");
check("no frontier at 5", AOCL.frontier(5) === null);

/* --- decision-model + HITL tables --- */
check("L1-3 -> MAPE", AOCL.recommendedModel(1, "fast") === "MAPE" && AOCL.recommendedModel(3, "slow") === "MAPE");
check("L4-5 tactical/slow -> OODA", AOCL.recommendedModel(4, "slow") === "OODA" && AOCL.recommendedModel(5, "tactical") === "OODA");
check("L4-5 fast -> MAPE", AOCL.recommendedModel(5, "fast") === "MAPE");
check("hitl map", AOCL.HITL[2] === "HITL" && AOCL.HITL[3] === "HOTL" && AOCL.HITL[5] === "HOOTL");

/* --- realization (doc worked examples) --- */
const r1 = AOCL.realize(0.6, 0.8, 0.9);
check("doc worked example R", Math.abs(r1 - 0.9372) < 0.0005);
const r2 = AOCL.realize(0.6, 0.8, 0.5);
check("doc low-veracity R", Math.abs(r2 - 0.7211) < 0.0005);
AOCL.REFERENCE_POINTS.forEach((p) => {
  check(`table ${p.level} R`, Math.abs(AOCL.realize(p.E, p.C) - p.R) < 0.01);
});
check("zero-complexity limit", Math.abs(AOCL.realize(0.8, 0) - 0.8) < 1e-9);
check("zero-experience limit", Math.abs(AOCL.realize(0, 1.2) - 1.2) < 1e-9);
check("component aggregation", Math.abs(AOCL.experienceFromComponents(0.3, 0.3, 0.3, 0.3) - 0.6) < 1e-9);
const s = AOCL.sensitivity(0.6, 0.8);
check("sensitivity identity", Math.abs(s.dR_dE - 0.6) < 1e-9 && Math.abs(s.dR_dC - 0.8) < 1e-9);
check("required complexity", Math.abs(AOCL.requiredComplexity(0.6, 1.0) - 0.8) < 1e-9);
let threw = false;
try { AOCL.requiredComplexity(0.6, 0.5); } catch (e) { threw = true; }
check("infeasible target rejected", threw);
threw = false;
try { AOCL.realize(1.5, 0.8); } catch (e) { threw = true; }
check("out-of-range E rejected", threw);
check("value bands", AOCL.valueBand(3) === "logarithmic" && AOCL.valueBand(4) === "exponential");

/* --- modeler --- */
const sample = {
  format: "aocl-loop-model", model_version: "1.0.0", ruleset_version: AOCL.RULESET_VERSION,
  entities: [{ id: "proc-1", kind: "process", name: "Detect Anomaly" }],
  loops: [{
    id: "loop-1", entity: "proc-1", velocity: "fast", level: 2,
    decision_model: { kind: "MAPE", monitor: { name: "m", action: "a" }, analyze: { name: "an", action: "b" }, plan: { name: "p", action: "c" }, execute: { name: "e", action: "d" } },
    goals: [{ name: "latency", target: { metric: "e2e_ms", value: 100, direction: "AT_MOST" } }],
  }],
  links: [],
};
check("modeler validates clean model", Modeler.validate(sample).length === 0);
check("modeler catches dangling entity", Modeler.validate({ ...sample, loops: [{ ...sample.loops[0], entity: "ghost" }] }).some((p) => p.includes("not found")));
check("modeler catches level mismatch", Modeler.validate({ ...sample, loops: [{ ...sample.loops[0], level: 4, vector_scores: { GD: 2, DV: 2, FI: 2 } }] }).some((p) => p.includes("level 4 inconsistent")));
const clam = Modeler.toClamExport(sample);
check("clam export format", clam.export_format === "aocl-clam-export" && clam.decision_models.length === 1);
check("clam export MAPE steps", ["monitor", "analyze", "plan", "execute"].every((k) => clam.decision_models[0][k]));
check("clam export loop linkage", clam.closed_loops[0].decision_model === "loop-1-dm" && clam.closed_loops[0].aocl.level === 2);
const yamlOut = Modeler.toYaml(sample);
check("yaml emits format key", yamlOut.includes("format: aocl-loop-model"));
check("yaml quotes tricky strings", Modeler.toYaml({ s: "has: colon" }).includes('"has: colon"'));
const ledgerYaml = Modeler.toLedgerYaml(sample);
check("ledger export declares schema 1", ledgerYaml.includes("schema: 1") && ledgerYaml.includes("decision_model: MAPE"));

/* --- cross-engine version parity (regex grep of the Python engine) --- */
const py = fs.readFileSync(path.join(__dirname, "..", "src", "aocl", "assess.py"), "utf-8");
const m = py.match(/RULESET_VERSION\s*=\s*"([^"]+)"/);
check("python RULESET_VERSION parity", m && m[1] === AOCL.RULESET_VERSION);

/* --- site sanity --- */
const html = fs.readFileSync(path.join(__dirname, "..", "site", "index.html"), "utf-8");
for (const needle of ['id="quiz"', 'id="lanes"', 'id="loopEditor"', "scoring.js", "charts.js", "modeler.js", "Loop Modeler"]) {
  check(`index.html contains ${needle}`, html.includes(needle));
}
const excluded = ["A", "A", "D", "E"].join("");  // the third surveyed decision model — out of scope by project direction
check("excluded decision model absent from the site", !html.includes(excluded) && !fs.readFileSync(path.join(__dirname, "..", "site", "scoring.js"), "utf-8").includes(excluded));

if (failures) { console.log(`site_selftest: ${failures} failure(s)`); process.exit(1); }
console.log(`site_selftest: OK (ruleset ${AOCL.RULESET_VERSION}, modeler + engine + parity checked)`);
