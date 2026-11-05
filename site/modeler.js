/* AOCL Loop Modeler: visual layout where the user places closed loops on
 * Processes / Capabilities / Systems / Functions, sets velocity + maturity level,
 * and specifies each loop in the Closed-Loop-Management (CLAM) aligned format
 * (emmanuel-a-otchere/Closed-Loop-Management — data model 1.0).
 *
 * State lives in localStorage. Exports:
 *   - aocl-loop-model YAML  (consumed by the aocl-ledger / aocl-model CLIs)
 *   - aocl-clam-export JSON (CLAM-shaped provisioning payloads)
 *   - loop-ledger YAML      (deployed-loop registry)
 */
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory(require("./scoring.js"));
  else root.AOCLModeler = factory(root.AOCL);
})(typeof self !== "undefined" ? self : this, function (AOCL) {
  "use strict";

  var ENTITY_KINDS = [
    { id: "process", name: "Process", hint: "value-stream stage or operational workflow" },
    { id: "capability", name: "Capability", hint: "organizational or technical capability" },
    { id: "system", name: "System", hint: "platform, network domain, or application" },
    { id: "function", name: "Function", hint: "discrete technical function or service" },
  ];
  var DM_STEPS = { OODA: ["observe", "orient", "decide", "act"], MAPE: ["monitor", "analyze", "plan", "execute"] };
  var STATES = ["designed", "validated", "published", "active", "paused", "error", "retired"];

  function emptyModel() {
    return {
      format: "aocl-loop-model",
      model_version: "1.0.0",
      ruleset_version: AOCL.RULESET_VERSION,
      entities: [],
      loops: [],
      links: [],
    };
  }

  function slugify(name, taken) {
    var base = String(name || "item").toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "") || "item";
    var slug = base, n = 2;
    while (taken.indexOf(slug) >= 0) slug = base + "-" + n++;
    return slug;
  }

  function newLoop(entityId, defaults) {
    defaults = defaults || {};
    return {
      id: defaults.id || "loop-" + Math.random().toString(36).slice(2, 8),
      entity: entityId,
      velocity: defaults.velocity || "fast",
      level: defaults.level || 2,
      decision_model: defaults.decision_model || {
        kind: "MAPE",
        monitor: { name: "monitor-step", action: "" },
        analyze: { name: "analyze-step", action: "" },
        plan: { name: "plan-step", action: "" },
        execute: { name: "execute-step", action: "" },
      },
      goals: defaults.goals || [],
      hitl: defaults.hitl || null,
      state: defaults.state || "designed",
      owner: defaults.owner || "",
      notes: defaults.notes || "",
    };
  }

  /* ---------------- YAML serialization (constrained model shape) ---------------- */

  function needsQuote(s) {
    return /[:#{}\[\],&*?|>'"%@`]|^\s|\s$|^$|^[-?!]/.test(s) || /\s{2,}/.test(s) ||
      ["null", "true", "false", "yes", "no", "on", "off"].indexOf(s.toLowerCase()) >= 0 ||
      !isNaN(Number(s));
  }
  function yStr(s) {
    s = String(s);
    return needsQuote(s) ? '"' + s.replace(/\\/g, "\\\\").replace(/"/g, '\\"') + '"' : s;
  }
  function toYaml(value, indent) {
    indent = indent || 0;
    var pad = new Array(indent + 1).join(" ");
    if (value === null || value === undefined) return "null";
    if (typeof value === "number" || typeof value === "boolean") return String(value);
    if (typeof value === "string") return yStr(value);
    if (Array.isArray(value)) {
      if (value.length === 0) return "[]";
      return value.map(function (item) {
        if (item && typeof item === "object") {
          var inner = toYaml(item, indent + 2);
          var lines = inner.split("\n");
          var first = lines[0];
          var rest = lines.slice(1).join("\n");
          return pad + "- " + first + (rest ? "\n" + rest : "");
        }
        return pad + "- " + toYaml(item, 0);
      }).join("\n");
    }
    // object
    var keys = Object.keys(value).filter(function (k) { return value[k] !== undefined; });
    if (keys.length === 0) return "{}";
    return keys.map(function (k) {
      var v = value[k];
      if (v && typeof v === "object" && (!Array.isArray(v) || v.some(function (x) { return x && typeof x === "object"; }))) {
        return pad + yStr(k) + ":\n" + toYaml(v, indent + 2);
      }
      if (Array.isArray(v)) {
        if (v.length === 0) return pad + yStr(k) + ": []";
        if (v.every(function (x) { return x === null || typeof x !== "object"; })) {
          return pad + yStr(k) + ": [" + v.map(function (x) { return toYaml(x, 0); }).join(", ") + "]";
        }
        return pad + yStr(k) + ":\n" + toYaml(v, indent + 2);
      }
      return pad + yStr(k) + ": " + toYaml(v, 0);
    }).join("\n");
  }

  /* ---------------- CLAM export (mirrors src/aocl/model.py) ---------------- */

  function toClamExport(model) {
    var entities = {};
    model.entities.forEach(function (e) { entities[e.id] = e; });
    var decisionModels = [];
    var dmNames = {};
    model.loops.forEach(function (loop) {
      var dm = loop.decision_model;
      var name = loop.id + "-dm";
      dmNames[loop.id] = name;
      var payload = { kind: dm.kind, name: name };
      ["observe", "orient", "decide", "act", "monitor", "analyze", "plan", "execute"].forEach(function (f) {
        if (dm[f]) payload[f] = { id: dm[f].name, name: dm[f].name };
      });
      if (dm.kind === "CUSTOM") {
        payload.steps = (dm.steps || []).map(function (s) { return { name: s.name }; });
      }
      decisionModels.push(payload);
    });
    var closedLoops = model.loops.map(function (loop) {
      var entity = entities[loop.entity] || {};
      return {
        name: loop.id,
        description: loop.notes || (entity.name || loop.entity) + " — " + loop.velocity + " loop at L" + loop.level,
        decision_model: dmNames[loop.id],
        goals: (loop.goals || []).map(function (g) {
          return {
            name: g.name,
            target: {
              metric: g.target.metric, value: g.target.value,
              unit: g.target.unit === undefined ? null : g.target.unit,
              direction: g.target.direction || "AT_LEAST",
            },
            scope: g.scope || "CLOSED_LOOP",
          };
        }),
        links: (model.links || [])
          .filter(function (l) { return l.source === loop.id || l.target === loop.id; })
          .map(function (l) { return { source: l.source, target: l.target, kind: l.kind, condition: l.condition === undefined ? null : l.condition }; }),
        aocl: {
          entity: loop.entity,
          entity_kind: entity.kind,
          velocity: loop.velocity,
          level: loop.level,
          vector_levels: loop.vector_scores || null,
          hitl: loop.hitl || null,
          source_loop_id: loop.id,
        },
      };
    });
    return {
      export_format: "aocl-clam-export",
      export_version: "1.0.0",
      source_model_version: model.model_version,
      decision_models: decisionModels,
      closed_loops: closedLoops,
    };
  }

  /* ---------------- Ledger export (deployed-loop registry) ---------------- */

  function toLedgerYaml(model) {
    var entities = {};
    model.entities.forEach(function (e) { entities[e.id] = e; });
    var doc = {
      schema: 1,
      loops: model.loops.map(function (loop) {
        var entity = entities[loop.entity] || {};
        var hitl = loop.hitl || AOCL.HITL[loop.level];
        return {
          id: loop.id,
          entity: loop.entity,
          entity_kind: entity.kind || "system",
          velocity: loop.velocity,
          level: loop.level,
          vector_levels: loop.vector_scores || undefined,
          decision_model: loop.decision_model.kind,
          hitl: hitl,
          state: loop.state || "designed",
          owner: loop.owner || "unassigned",
          guardrails: loop.guardrails || [],
          last_review: loop.last_review || undefined,
          review_cadence_days: loop.review_cadence_days || undefined,
          notes: loop.notes || null,
        };
      }),
    };
    return "# AOCL loop ledger — emitted by the Loop Modeler\n" + toYaml(doc);
  }

  /* ---------------- Validation (client-side mirror of aocl/model.py) ---------------- */

  function validate(model) {
    var problems = [];
    var entityIds = {};
    model.entities.forEach(function (e, i) {
      if (!e.id || !/^[a-z0-9][a-z0-9-]*$/.test(e.id)) problems.push("entity " + i + ": id must be a lowercase slug");
      if (entityIds[e.id]) problems.push("duplicate entity id: " + e.id);
      entityIds[e.id] = true;
      if (!e.name) problems.push("entity " + (e.id || i) + ": name is required");
    });
    var loopIds = {};
    model.loops.forEach(function (loop, i) {
      var label = loop.id || "loop " + i;
      if (!loop.id || !/^[a-z0-9][a-z0-9-]*$/.test(loop.id)) problems.push(label + ": id must be a lowercase slug");
      if (loopIds[loop.id]) problems.push("duplicate loop id: " + loop.id);
      loopIds[loop.id] = true;
      if (!entityIds[loop.entity]) problems.push(label + ": entity " + loop.entity + " not found");
      if ([1, 2, 3, 4, 5].indexOf(loop.level) < 0) problems.push(label + ": level must be 1..5");
      if (["fast", "tactical", "slow"].indexOf(loop.velocity) < 0) problems.push(label + ": velocity must be fast|tactical|slow");
      var dm = loop.decision_model || {};
      if (DM_STEPS[dm.kind]) {
        DM_STEPS[dm.kind].forEach(function (step) {
          if (!dm[step] || !dm[step].name) problems.push(label + ": " + dm.kind + " model requires step '" + step + "'");
        });
      } else if (dm.kind === "CUSTOM") {
        if (!dm.steps || !dm.steps.length) problems.push(label + ": CUSTOM model requires steps");
      } else {
        problems.push(label + ": decision model kind must be OODA, MAPE, or CUSTOM");
      }
      if (loop.vector_scores) {
        var vs = loop.vector_scores;
        var vals = ["GD", "DV", "FI"].map(function (c) { return vs[c]; });
        if (vals.some(function (v) { return typeof v !== "number" || v < 1 || v > 5; })) {
          problems.push(label + ": vector_scores must be 1..5 for GD, DV, FI");
        } else if (Math.min.apply(null, vals) !== loop.level) {
          problems.push(label + ": level " + loop.level + " inconsistent with weakest vector score " + Math.min.apply(null, vals));
        }
      }
      (loop.goals || []).forEach(function (g, j) {
        if (!g.name || !g.target || !g.target.metric || typeof g.target.value !== "number") {
          problems.push(label + ": goal " + j + " requires name + target{metric, value}");
        }
      });
    });
    (model.links || []).forEach(function (l, i) {
      if (!loopIds[l.source]) problems.push("link " + i + ": source " + l.source + " is not a loop id");
      if (!loopIds[l.target]) problems.push("link " + i + ": target " + l.target + " is not a loop id");
      if (["DAISY_CHAIN", "HIERARCHICAL", "FEEDBACK"].indexOf(l.kind) < 0) problems.push("link " + i + ": kind must be DAISY_CHAIN|HIERARCHICAL|FEEDBACK");
    });
    return problems;
  }

  return {
    ENTITY_KINDS: ENTITY_KINDS,
    DM_STEPS: DM_STEPS,
    STATES: STATES,
    emptyModel: emptyModel,
    newLoop: newLoop,
    slugify: slugify,
    toYaml: toYaml,
    toClamExport: toClamExport,
    toLedgerYaml: toLedgerYaml,
    validate: validate,
  };
});
