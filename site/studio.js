/* AOCL Studio renderer — reads studio-data.json (exported by aocl-studio from the
 * canonical artifacts) and renders the staged behavioral graph, the scenario
 * library with visibility-declared disturbances, the control model, and the
 * reference run's verdict. Read-only: this file renders projections, it never
 * carries model semantics (STU-007). Offline, hand-rolled SVG, no build step. */
"use strict";

var STAGES = ["Intent", "Observe", "Analyze", "Decide", "Execute", "Verify", "Learn"];
var EDGE_STYLE = {
  FlowsTo:               { color: "#334155", dash: "" },
  BranchesTo:            { color: "#d97706", dash: "6 3" },
  Triggers:              { color: "#0d9488", dash: "2 3" },
  ExecutesInParallelWith:{ color: "#0891b2", dash: "1 4" },
  SynchronizesWith:      { color: "#0891b2", dash: "1 4" },
  RepeatsTo:             { color: "#7c3aed", dash: "5 4" },
  ReturnsTo:             { color: "#7c3aed", dash: "5 4" },
  EscalatesTo:           { color: "#b91c1c", dash: "" },
  HandlesException:      { color: "#b91c1c", dash: "4 3" },
  TerminatesWith:        { color: "#94a3b8", dash: "3 3" },
  Invokes:               { color: "#2563eb", dash: "2 2" },
  DependsOn:             { color: "#2563eb", dash: "2 2" }
};
var TYPE_COLOR = {
  IntentReference: "#4c1d95", Observation: "#0d9488", Analysis: "#2563eb", Assessment: "#2563eb",
  Decision: "#7c3aed", Approval: "#9333ea", Action: "#b45309", Verification: "#166534",
  Learning: "#15803d", Event: "#64748b", Condition: "#64748b", Wait: "#64748b",
  Synchronization: "#0891b2", Escalation: "#b91c1c", ExceptionHandler: "#b91c1c",
  SafeState: "#166534", SubSpecification: "#475569"
};

function esc(s) {
  return String(s == null ? "" : s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

function renderGraph(spec) {
  var W = 1160, laneTop = 46, colW = (W - 40) / STAGES.length, rowH = 64;
  var nodes = spec.elements || [];
  // position: first declared stage → column; index within column → row
  var byStage = {};
  nodes.forEach(function (n) {
    var stage = (n.stages && n.stages[0]) || "Execute";
    (byStage[stage] = byStage[stage] || []).push(n);
  });
  var pos = {};
  STAGES.forEach(function (stage, si) {
    (byStage[stage] || []).forEach(function (n, ri) {
      pos[n.id] = { x: 20 + si * colW + colW / 2, y: laneTop + 34 + ri * rowH, stage: stage, si: si };
    });
  });
  var maxRows = Math.max.apply(null, STAGES.map(function (s) { return (byStage[s] || []).length; }));
  var H = laneTop + 34 + Math.max(maxRows, 1) * rowH + 10;

  var s = ['<svg viewBox="0 0 ' + W + ' ' + H + '" xmlns="http://www.w3.org/2000/svg" role="img" ',
           'style="font-family:ui-monospace,Menlo,monospace">'];
  // stage lanes
  STAGES.forEach(function (stage, si) {
    s.push('<rect x="' + (20 + si * colW) + '" y="' + laneTop + '" width="' + (colW - 6) + '" height="' + (H - laneTop - 8) +
           '" fill="#fafafa" stroke="#e2e8f0" rx="6"/>');
    s.push('<text x="' + (20 + si * colW + (colW - 6) / 2) + '" y="' + (laneTop + 18) +
           '" text-anchor="middle" font-size="11" font-weight="bold" fill="#4c1d95">' + stage + '</text>');
  });
  // edges under nodes
  (spec.relationships || []).forEach(function (r) {
    var a = pos[r.source], b = pos[r.target];
    if (!a || !b) return;
    var st = EDGE_STYLE[r.type] || { color: "#2563eb", dash: "2 2" };
    var x1 = a.x + (b.si > a.si ? 66 : -66), y1 = a.y + 4;
    var x2 = b.x + (b.si > a.si ? -70 : 70), y2 = b.y + 4;
    var mx = (x1 + x2) / 2;
    s.push('<path d="M' + x1 + ' ' + y1 + ' C ' + mx + ' ' + y1 + ', ' + mx + ' ' + y2 + ', ' + x2 + ' ' + y2 +
           '" fill="none" stroke="' + st.color + '" stroke-width="1.4"' +
           (st.dash ? ' stroke-dasharray="' + st.dash + '"' : '') + ' opacity="0.75"/>');
    if (r.conditionRef) {
      s.push('<circle cx="' + mx + '" cy="' + ((y1 + y2) / 2) + '" r="3.4" fill="#fff" stroke="' + st.color + '"/>');
      s.push('<text x="' + (mx + 6) + '" y="' + ((y1 + y2) / 2 + 3) + '" font-size="8" fill="' + st.color + '">' +
             esc(r.conditionRef.replace(/^cond-/, "")) + '</text>');
    }
    if (r.type === "TerminatesWith") {
      s.push('<text x="' + (mx + 6) + '" y="' + ((y1 + y2) / 2 - 4) + '" font-size="8" fill="' + st.color + '">' +
             esc(r.terminationOutcome || "") + '</text>');
    }
  });
  // nodes
  nodes.forEach(function (n) {
    var p = pos[n.id];
    if (!p) return;
    var color = TYPE_COLOR[n.type] || "#475569";
    s.push('<rect x="' + (p.x - 66) + '" y="' + (p.y - 18) + '" width="132" height="40" rx="7" fill="#fff" stroke="' +
           color + '" stroke-width="1.6"/>');
    s.push('<text x="' + p.x + '" y="' + (p.y - 2) + '" text-anchor="middle" font-size="9.5" font-weight="bold" fill="' +
           color + '">' + esc(n.type) + '</text>');
    s.push('<text x="' + p.x + '" y="' + (p.y + 12) + '" text-anchor="middle" font-size="9" fill="#334155">' +
           esc(String(n.name || n.id).slice(0, 22)) + '</text>');
    var extra = (n.stages || []).slice(1);
    if (extra.length) {
      s.push('<text x="' + (p.x + 70) + '" y="' + (p.y - 10) + '" font-size="7.5" fill="#94a3b8">+' +
             esc(extra.join("+")) + '</text>');
    }
  });
  s.push("</svg>");
  return s.join("");
}

function renderScenarios(lib) {
  return (lib.scenarios || []).map(function (sc) {
    var chips = (sc.disturbances || []).map(function (d) {
      var hidden = d.knownToController === false;
      return '<span class="chip ' + (hidden ? "hidden" : "visible") + '" title="' +
             esc(d.type + " · " + d.profile + " · " + d.magnitude + " " + (d.magnitudeUnit || "")) + '">' +
             (hidden ? "-controller-blind: " : "controller-known: ") + esc(d.name) + "</span>";
    }).join("");
    var diffs = (sc.differences || []).length
      ? '<div class="muted">variant of ' + esc(sc.extends) + ": " + esc(sc.differences.join("; ")) + "</div>" : "";
    return '<div class="scen"><b>' + esc(sc.scenarioId) + "</b> <span class='muted'>" + esc(sc.type) +
           " · v" + esc(sc.version) + " · " + esc(sc.lifecycleStatus) + "</span>" + diffs +
           "<div style='margin-top:4px'>" + (chips || "<span class='muted'>no disturbances</span>") + "</div></div>";
  }).join("");
}

function renderControl(control) {
  if (!control) return '<span class="muted">no control model bound</span>';
  var rows = control.contracts.map(function (c) {
    return "<tr><td>" + esc(c.contractId) + "</td><td>" + esc(c.contractType) + "</td><td>" + esc(c.subjectRef) + "</td></tr>";
  }).join("");
  var auth = control.authority.map(function (a) {
    return "<tr><td>" + esc(a.authorityId) + "</td><td>" + esc(a.subjectRef) + "</td><td>" + esc(a.authorityClass || "") + "</td></tr>";
  }).join("");
  var inv = control.invariants.map(function (i) {
    return "<tr><td>" + esc(i.priorityClass) + "</td><td>" + esc(i.statement) + "</td></tr>";
  }).join("");
  return "<div class='muted'>contracts</div><table><tr><th>contract</th><th>type</th><th>subject</th></tr>" + rows +
         "</table><div class='muted' style='margin-top:8px'>authority</div><table><tr><th>authority</th><th>subject</th><th>class</th></tr>" + auth +
         "</table><div class='muted' style='margin-top:8px'>invariants</div><table><tr><th>class</th><th>statement</th></tr>" + inv + "</table>";
}

function renderVerdict(trace) {
  if (!trace) return;
  var el = document.getElementById("verdict");
  var t = trace.termination || {};
  var ok = t.outcome === "VerifiedCompletion";
  el.className = "verdict" + (ok ? "" : " warn");
  el.innerHTML = "<b>" + esc(trace.runId) + "</b> — " + esc(t.outcome) +
    " (" + esc(t.why || "") + ") · " + esc(String(trace.recordCount)) + " records · " +
    esc(trace.engineName) + "@" + esc(trace.engineVersion);
}

fetch("studio-data.json").then(function (r) {
  if (!r.ok) throw new Error("studio-data.json " + r.status);
  return r.json();
}).then(function (b) {
  document.getElementById("meta").textContent =
    "bundle v" + b.bundleVersion + " · ruleset " + b.rulesetVersion + " · " + b.spec.ref + " v" + b.spec.version +
    " (" + b.spec.lifecycleStatus + ")";
  document.getElementById("specmeta").textContent =
    (b.spec.elements.length) + " elements · " + (b.spec.relationships.length) +
    " relationships · entry: " + (b.spec.entry.join(", ") || "—") +
    " · termination: " + (b.spec.terminationOutcomes.join(", ") || "—");
  document.getElementById("graph").innerHTML = renderGraph(b.spec);
  document.getElementById("scenarios").innerHTML = renderScenarios(b.scenarios);
  document.getElementById("control").innerHTML = renderControl(b.control);
  renderVerdict(b.trace);
}).catch(function (e) {
  document.getElementById("err").textContent = "studio bundle unavailable: " + e.message +
    " — regenerate with: aocl-studio export … --out site/studio-data.json";
});
