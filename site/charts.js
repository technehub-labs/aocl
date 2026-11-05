/* AOCL charts: hand-rolled SVG renderers (no external dependencies, offline-first).
 * Every function returns an SVG markup string; text is escaped at the call site. */
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory();
  else root.AOCLCharts = factory();
})(typeof self !== "undefined" ? self : this, function () {
  "use strict";

  function esc(s) {
    return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  }

  function svgOpen(w, h) {
    return '<svg viewBox="0 0 ' + w + " " + h + '" xmlns="http://www.w3.org/2000/svg" role="img" style="max-width:100%;height:auto;font-family:ui-monospace,Menlo,monospace">';
  }

  var COLORS = {
    GD: "#2563eb",   // Goal Decisioning — blue
    DV: "#dc2626",   // Data Veracity — red
    FI: "#16a34a",   // Feedback Intelligence — green
    band: "#f4f0fa",
    bandEdge: "#7c3aed",
    ink: "#1e293b",
    muted: "#64748b",
    accent: "#7c3aed",
  };

  /* ---- Vector radar (triangle, L1..L5 rings) ---- */
  function radarChart(vectorLevels, size) {
    size = size || 340;
    var cx = size / 2, cy = size / 2 + 6, R = size / 2 - 46;
    var angles = { GD: -90, DV: 150, FI: 30 }; // degrees
    function pt(code, frac) {
      var a = (angles[code] * Math.PI) / 180;
      return [cx + R * frac * Math.cos(a), cy + R * frac * Math.sin(a)];
    }
    var s = svgOpen(size, size + 28);
    for (var ring = 1; ring <= 5; ring++) {
      var pts = ["GD", "DV", "FI"].map(function (c) { return pt(c, ring / 5).join(","); }).join(" ");
      s += '<polygon points="' + pts + '" fill="' + (ring === 5 ? COLORS.band : "none") + '" stroke="#e2e8f0" stroke-width="1"/>';
    }
    ["GD", "DV", "FI"].forEach(function (c) {
      var p = pt(c, 1);
      s += '<line x1="' + cx + '" y1="' + cy + '" x2="' + p[0] + '" y2="' + p[1] + '" stroke="#cbd5e1" stroke-width="1"/>';
      var lp = pt(c, 1.22);
      s += '<text x="' + lp[0] + '" y="' + lp[1] + '" text-anchor="middle" font-size="12" fill="' + COLORS[c] + '" font-weight="bold">' + c + "</text>";
    });
    var shape = ["GD", "DV", "FI"].map(function (c) { return pt(c, (vectorLevels[c] || 0) / 5).join(","); }).join(" ");
    s += '<polygon points="' + shape + '" fill="rgba(124,58,237,0.25)" stroke="' + COLORS.accent + '" stroke-width="2"/>';
    ["GD", "DV", "FI"].forEach(function (c) {
      var p = pt(c, (vectorLevels[c] || 0) / 5);
      s += '<circle cx="' + p[0] + '" cy="' + p[1] + '" r="4" fill="' + COLORS[c] + '"/>';
      var lp = pt(c, (vectorLevels[c] || 0) / 5 + 0.13);
      s += '<text x="' + lp[0] + '" y="' + lp[1] + '" text-anchor="middle" font-size="10" fill="' + COLORS.ink + '">L' + (vectorLevels[c] || 0) + "</text>";
    });
    s += '<text x="' + cx + '" y="' + (size + 18) + '" text-anchor="middle" font-size="11" fill="' + COLORS.muted + '">vector levels · overall = weakest link</text>';
    return s + "</svg>";
  }

  /* ---- E–C plane with iso-R circles and the Table 1.1 reference points ---- */
  function ecPlane(E, C, Vd, title) {
    var w = 460, h = 380, pad = 46;
    var xMax = 3.8, yMax = 1.05; // E axis is 0..1, C axis 0..~3.8; we plot E on Y, C on X
    function X(c) { return pad + (c / xMax) * (w - pad - 16); }
    function Y(e) { return h - pad - (e / yMax) * (h - pad - 24); }
    var s = svgOpen(w, h);
    s += '<rect x="' + pad + '" y="' + (h - pad - (h - pad - 24)) + '" width="' + (w - pad - 16) + '" height="' + (h - pad - 24) + '" fill="#fafafa" stroke="#e2e8f0"/>';
    // level bands (Table 1.1 R per level) as iso-R arcs: R = sqrt(E^2 + C^2)
    [0.5, 1.0, 1.7, 3.63].forEach(function (R, i) {
      var names = ["R=0.50 (L2)", "R=1.00 (L3)", "R=1.70 (L4)", "R=3.63 (L5)"];
      var steps = 60, d = "";
      for (var k = 0; k <= steps; k++) {
        var e = (R * k) / steps;
        if (e > 1) break;
        var c = Math.sqrt(Math.max(R * R - e * e, 0));
        if (c > xMax) break;
        d += (d ? " L" : "M") + X(c).toFixed(1) + " " + Y(e).toFixed(1);
      }
      if (d) s += '<path d="' + d + '" fill="none" stroke="' + COLORS.bandEdge + '" stroke-width="1" stroke-dasharray="4 3" opacity="0.6"/>';
      var lastE = Math.min(R, 1) * 0.985;
      var lc = Math.sqrt(Math.max(R * R - lastE * lastE, 0));
      if (lc <= xMax) s += '<text x="' + (X(lc) + 4) + '" y="' + (Y(lastE) - 4) + '" font-size="9" fill="' + COLORS.muted + '">' + names[i] + "</text>";
    });
    // reference points
    AOCL_REF().forEach(function (p) {
      s += '<circle cx="' + X(p.C) + '" cy="' + Y(p.E) + '" r="4" fill="#fff" stroke="' + COLORS.accent + '" stroke-width="1.5"/>';
      s += '<text x="' + (X(p.C) + 6) + '" y="' + (Y(p.E) + 3) + '" font-size="9" fill="' + COLORS.muted + '">' + p.level + "</text>";
    });
    // current position (C scaled by Vd)
    var cx = X(Math.min((C * (Vd || 1)), xMax)), cy = Y(E);
    s += '<circle cx="' + cx + '" cy="' + cy + '" r="6" fill="' + COLORS.accent + '" stroke="#fff" stroke-width="2"/>';
    s += '<text x="' + (cx + 9) + '" y="' + (cy + 4) + '" font-size="11" fill="' + COLORS.ink + '" font-weight="bold">you (E=' + E.toFixed(2) + ", C·Vd=" + (C * (Vd || 1)).toFixed(2) + ")</text>";
    // axes
    s += '<line x1="' + pad + '" y1="' + (h - pad) + '" x2="' + (w - 16) + '" y2="' + (h - pad) + '" stroke="' + COLORS.ink + '"/>';
    s += '<line x1="' + pad + '" y1="' + (h - pad) + '" x2="' + pad + '" y2="24" stroke="' + COLORS.ink + '"/>';
    s += '<text x="' + (w / 2) + '" y="' + (h - 12) + '" text-anchor="middle" font-size="11" fill="' + COLORS.ink + '">Complexity C (x Vd for effective)</text>';
    s += '<text x="14" y="' + (h / 2) + '" font-size="11" fill="' + COLORS.ink + '" transform="rotate(-90 14 ' + h / 2 + ')" text-anchor="middle">Experience E</text>';
    if (title) s += '<text x="' + (w / 2) + '" y="16" text-anchor="middle" font-size="12" fill="' + COLORS.ink + '" font-weight="bold">' + esc(title) + "</text>";
    return s + "</svg>";
  }

  function AOCL_REF() {
    if (typeof AOCL !== "undefined") return AOCL.REFERENCE_POINTS;
    return [];
  }

  /* ---- Composite realization curve (log L1-L3, exp L3-L5) with position ---- */
  function realizationCurve(E, C, Vd, level) {
    var w = 460, h = 300, pad = 44;
    var rNow = Math.sqrt(E * E + (C * (Vd || 1)) * (C * (Vd || 1)));
    function X(l) { return pad + ((l - 1) / 4) * (w - pad - 20); }
    function Y(v) { return h - pad - (v / 4.2) * (h - pad - 20); }
    var s = svgOpen(w, h);
    s += '<rect x="' + pad + '" y="24" width="' + (w - pad - 20) + '" height="' + (h - pad - 20) + '" fill="#fafafa" stroke="#e2e8f0"/>';
    // logarithmic model L1..L3 (solid) and exponential L3..L5 (solid), joined at L3
    var dLog = "", dExp = "";
    for (var l = 10; l <= 30; l++) {
      var lv = l / 10;
      var v = valueLog(lv);
      dLog += (dLog ? " L" : "M") + X(lv).toFixed(1) + " " + Y(v).toFixed(1);
    }
    for (var l2 = 30; l2 <= 50; l2++) {
      var lv2 = l2 / 10;
      var v2 = valueExp(lv2);
      dExp += (dExp ? " L" : "M") + X(lv2).toFixed(1) + " " + Y(Math.min(v2, 4.0)).toFixed(1);
    }
    s += '<path d="' + dLog + '" fill="none" stroke="#2563eb" stroke-width="2"/>';
    s += '<path d="' + dExp + '" fill="none" stroke="#16a34a" stroke-width="2"/>';
    // inflection marker at L3
    s += '<line x1="' + X(3) + '" y1="24" x2="' + X(3) + '" y2="' + (h - pad) + '" stroke="#f59e0b" stroke-dasharray="4 3" stroke-width="1.5"/>';
    s += '<text x="' + (X(3) + 5) + '" y="36" font-size="10" fill="#b45309">inflection: human-designed → machine-discovered</text>';
    [1, 2, 3, 4, 5].forEach(function (l) {
      s += '<text x="' + X(l) + '" y="' + (h - pad + 16) + '" text-anchor="middle" font-size="11" fill="' + COLORS.muted + '">L' + l + "</text>";
      s += '<text x="' + X(l) + '" y="' + (h - pad + 28) + '" text-anchor="middle" font-size="9" fill="' + COLORS.muted + '">' + esc(["Static", "Reactive", "Proactive", "Predictive", "Pre-emptive"][l - 1]) + "</text>";
    });
    if (level) {
      var vAt = level <= 3 ? valueLog(level) : Math.min(valueExp(level), 4.0);
      s += '<circle cx="' + X(level) + '" cy="' + Y(vAt) + '" r="6" fill="' + COLORS.accent + '" stroke="#fff" stroke-width="2"/>';
      s += '<text x="' + (X(level) + 9) + '" y="' + (Y(vAt) - 6) + '" font-size="10" fill="' + COLORS.ink + '">your level (R≈' + rNow.toFixed(2) + ")</text>";
    }
    s += '<text x="' + (w / 2) + '" y="' + (h - 6) + '" text-anchor="middle" font-size="10" fill="' + COLORS.muted + '">value models: ln(1+αL) — L1–L3 · exp(β(L−3)) — L3–L5 (illustrative)</text>';
    return s + "</svg>";

    function valueLog(l) { return Math.log(1 + l) / Math.log(6); }
    function valueExp(l) { return Math.exp(l - 3); }
  }

  /* ---- Effort curve e^R with marker ---- */
  function effortCurve(R) {
    var w = 460, h = 280, pad = 46;
    var rMax = 4.0, eMax = Math.exp(rMax); // ~54.6
    function X(r) { return pad + (r / rMax) * (w - pad - 20); }
    function Y(e) { return h - pad - (e / eMax) * (h - pad - 20); }
    var s = svgOpen(w, h);
    s += '<rect x="' + pad + '" y="24" width="' + (w - pad - 20) + '" height="' + (h - pad - 20) + '" fill="#fafafa" stroke="#e2e8f0"/>';
    var d = "";
    for (var k = 0; k <= 80; k++) {
      var r = (rMax * k) / 80;
      d += (d ? " L" : "M") + X(r).toFixed(1) + " " + Y(Math.exp(r)).toFixed(1);
    }
    s += '<path d="' + d + '" fill="none" stroke="#dc2626" stroke-width="2"/>';
    // reference markers
    [0.5, 1.0, 1.7, 3.63].forEach(function (r) {
      s += '<circle cx="' + X(r) + '" cy="' + Y(Math.exp(r)) + '" r="4" fill="#fff" stroke="#dc2626" stroke-width="1.5"/>';
      s += '<text x="' + (X(r) + 6) + '" y="' + (Y(Math.exp(r)) - 5) + '" font-size="9" fill="' + COLORS.muted + '">e^' + r.toFixed(2) + "=" + Math.exp(r).toFixed(1) + "</text>";
    });
    if (typeof R === "number" && R >= 0) {
      s += '<circle cx="' + X(Math.min(R, rMax)) + '" cy="' + Y(Math.exp(Math.min(R, rMax))) + '" r="6" fill="' + COLORS.accent + '" stroke="#fff" stroke-width="2"/>';
      s += '<text x="' + (X(Math.min(R, rMax)) + 9) + '" y="' + (Y(Math.exp(Math.min(R, rMax))) - 8) + '" font-size="11" fill="' + COLORS.ink + '" font-weight="bold">R=' + R.toFixed(2) + " → effort " + Math.exp(R).toFixed(1) + "×</text>";
    }
    s += '<text x="' + (w / 2) + '" y="' + (h - 8) + '" text-anchor="middle" font-size="10" fill="' + COLORS.muted + '">effort factor E_f = e^R (α = 1) — the last 5% of manual effort is the hardest</text>';
    return s + "</svg>";
  }

  /* ---- Latency budget bars (Table 3) ---- */
  function budgetBars() {
    var rows = [
      { cls: "Fast", obs: 10, dec: 10, act: 10, e2e: 100, slo: "99.999%" },
      { cls: "Tactical", obs: 60000, dec: 300000, act: 60000, e2e: 600000, slo: "99.99%" },
      { cls: "Slow", obs: 3600000, dec: 86400000, act: 14400000, e2e: 604800000, slo: "99.9%" },
    ];
    var w = 460, h = 240, labelW = 150, pad = 20;
    // log scale: 10ms .. 604.8M ms
    var minMs = 1, maxMs = 7e8;
    function X(ms) { return labelW + ((Math.log10(ms) - Math.log10(minMs)) / (Math.log10(maxMs) - Math.log10(minMs))) * (w - labelW - pad); }
    var s = svgOpen(w, h);
    var y = 34;
    rows.forEach(function (r) {
      s += '<text x="10" y="' + (y + 12) + '" font-size="12" fill="' + COLORS.ink + '" font-weight="bold">' + r.cls + '</text>';
      [["obs", r.obs], ["dec", r.dec], ["act", r.act], ["e2e", r.e2e]].forEach(function (pair, i) {
        var yy = y + i * 9 + 6;
        s += '<rect x="' + labelW + '" y="' + yy + '" width="' + Math.max(X(r.e2e) - labelW, 2) + '" height="5" rx="2.5" fill="' + ["#93c5fd", "#a5b4fc", "#c4b5fd", "#7c3aed"][i] + '" opacity="0.9"/>';
      });
      s += '<text x="' + (X(r.e2e) + 6) + '" y="' + (y + 18) + '" font-size="9" fill="' + COLORS.muted + '">e2e ' + esc(r.cls === "Fast" ? "< 100 ms" : r.cls === "Tactical" ? "< 10 min" : "< 7 days") + " · SLO " + r.slo + "</text>";
      y += 62;
    });
    s += '<text x="10" y="' + (h - 8) + '" font-size="9" fill="' + COLORS.muted + '">bars: observation, decision, actuation, end-to-end (log scale) — Table 3 reference budgets</text>';
    return s + "</svg>";
  }

  /* ---- Portfolio scatter: loops by (velocity, level) ---- */
  function portfolioScatter(loops) {
    var w = 460, h = 300, pad = 50;
    var vel = { fast: 0, tactical: 1, slow: 2 };
    function X(v) { return pad + (v / 2) * (w - pad - 24); }
    function Y(l) { return h - pad - ((l - 1) / 4) * (h - pad - 26); }
    var s = svgOpen(w, h);
    s += '<rect x="' + pad + '" y="20" width="' + (w - pad - 24) + '" height="' + (h - pad - 22) + '" fill="#fafafa" stroke="#e2e8f0"/>';
    // jitter duplicates within a cell
    var seen = {};
    loops.forEach(function (loop) {
      var key = loop.velocity + ":" + loop.level;
      var n = seen[key] || 0;
      seen[key] = n + 1;
      var dx = (n % 5) * 9 - 18, dy = Math.floor(n / 5) * 8;
      var color = loop.velocity === "fast" ? "#2563eb" : loop.velocity === "tactical" ? "#7c3aed" : "#16a34a";
      s += '<circle cx="' + (X(vel[loop.velocity]) + dx) + '" cy="' + (Y(loop.level) + dy) + '" r="7" fill="' + color + '" opacity="0.75" stroke="#fff"/>';
      if (n === 0) s += '<text x="' + (X(vel[loop.velocity]) + 10) + '" y="' + (Y(loop.level) + 3) + '" font-size="9" fill="' + COLORS.ink + '">' + esc(loop.id.length > 22 ? loop.id.slice(0, 21) + "…" : loop.id) + "</text>";
    });
    [1, 2, 3, 4, 5].forEach(function (l) {
      s += '<text x="' + (pad - 8) + '" y="' + (Y(l) + 4) + '" text-anchor="end" font-size="11" fill="' + COLORS.muted + '">L' + l + "</text>";
    });
    [["fast", 0], ["tactical", 1], ["slow", 2]].forEach(function (pair) {
      s += '<text x="' + X(pair[1]) + '" y="' + (h - pad + 18) + '" text-anchor="middle" font-size="11" fill="' + COLORS.ink + '">' + pair[0] + "</text>";
    });
    s += '<text x="' + (w / 2) + '" y="14" text-anchor="middle" font-size="12" fill="' + COLORS.ink + '" font-weight="bold">Loop portfolio (velocity × maturity level)</text>';
    return s + "</svg>";
  }

  return {
    esc: esc,
    radarChart: radarChart,
    ecPlane: ecPlane,
    realizationCurve: realizationCurve,
    effortCurve: effortCurve,
    budgetBars: budgetBars,
    portfolioScatter: portfolioScatter,
  };
})();
