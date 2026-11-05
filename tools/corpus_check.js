#!/usr/bin/env node
"use strict";
/* Corpus checker (JS engine): runs tests/corpus.json against site/scoring.js.
 * Mirrors tools/corpus_check.py — any drift blocks release. */
const fs = require("fs");
const path = require("path");
const AOCL = require(path.join(__dirname, "..", "site", "scoring.js"));

const corpus = JSON.parse(fs.readFileSync(path.join(__dirname, "..", "tests", "corpus.json"), "utf-8"));
if (corpus.ruleset_version !== AOCL.RULESET_VERSION) {
  console.log(`corpus (javascript): FAIL — corpus ruleset ${corpus.ruleset_version} != engine ${AOCL.RULESET_VERSION}`);
  process.exit(2);
}

let failures = 0;
for (const c of corpus.assessment_cases) {
  const r = AOCL.assess(c.vector_scores, c.current === null ? null : c.current, c.velocity || "tactical");
  const e = c.expect;
  const pairs = [
    ["level", r.level, e.level],
    ["frontier", r.frontier, e.frontier],
    ["recommended_decision_model", r.recommendedDecisionModel, e.recommended_decision_model],
    ["hitl", r.hitl, e.hitl],
    ["recommended_move", r.recommendedMove, e.recommended_move],
  ];
  for (const [field, actual, expected] of pairs) {
    if (actual !== expected) { console.log(`corpus (javascript): FAIL ${c.name}.${field}: ${JSON.stringify(actual)} != ${JSON.stringify(expected)}`); failures++; }
  }
  for (const needle of e.notes_contain) {
    if (!r.notes.some((n) => n.includes(needle))) { console.log(`corpus (javascript): FAIL ${c.name}: notes missing ${needle}`); failures++; }
  }
}
for (const c of corpus.realization_cases) {
  const R = AOCL.realize(c.E, c.C, c.Vd === undefined ? 1.0 : c.Vd);
  const eff = AOCL.effort(R);
  if (Math.round(R * 10000) / 10000 !== c.expect.R) { console.log(`corpus (javascript): FAIL ${c.name}.R: ${R} != ${c.expect.R}`); failures++; }
  if (Math.round(eff * 10000) / 10000 !== c.expect.effort) { console.log(`corpus (javascript): FAIL ${c.name}.effort: ${eff} != ${c.expect.effort}`); failures++; }
}
if (failures) { console.log(`corpus (javascript): ${failures} failure(s)`); process.exit(1); }
const n = corpus.assessment_cases.length + corpus.realization_cases.length;
console.log(`corpus (javascript): ${n} cases OK against ruleset ${AOCL.RULESET_VERSION}`);
