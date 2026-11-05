# AO-Ready Loop Assumptions

**Status:** draft (v0.1.0) · **Source:** §7.2 "Key Assumptions for AO-Ready Loops"

Designing and deploying AO-ready closed loops is predicated on seven assumptions. Each is a design obligation: where an assumption fails, the loop must degrade gracefully, not fail silently.

1. **Observability completeness** — all states relevant to control decisions are observable, directly or by inference. Unobservable states shall be **modelled (simulation) with explicit uncertainty quantification**; control actions under high uncertainty default to conservative, safe behaviours.

2. **Actuation authority** — actuators possess the authority and capability to implement control decisions. Where actuation needs external coordination (third-party interconnection, regulatory approval), the loop incorporates that **latency and uncertainty into its decision model**.

3. **Intent stability (accepted intent)** — high-level party and commercial intent is sufficiently **stable (accepted, not in negotiation)** to serve as a control reference. Rapidly oscillating objectives create reference-tracking problems that destabilize even mature loops; intent changes are filtered through slow loops and propagated gradually.

4. **Safety-envelope integrity** — safety envelopes, guardrails, and ethical constraints are correctly specified and **inviolable**. They shall be implemented in hardware or formally verified software — **not purely learned**. (This is why the ledger makes guardrails mandatory at L3+: `aocl-ledger` fails a loop claiming L3+ maturity with an empty guardrail list.)

5. **Human operator availability** — humans remain available for exception handling within bounded response times. Fully autonomous operations that never require human intervention are a **theoretical limit, not an operational assumption**. Escalation pathways shall be tested and validated.

6. **Model–environment consistency** — internal operating models (digital twins) remain consistent with the external environment within acceptable bounds. **Model drift shall be continuously monitored**, and loops degrade gracefully when dependency/accuracy/effectiveness falls below thresholds.

7. **Adversarial resilience** — adversarial actors and environmental antagonists are *assumed present*. Loops are designed with **fail-safe and fail-secure modes**; autonomous experimentation is sandboxed to prevent unintended systemic consequences.

These assumptions connect directly to the tools: the **ledger** enforces guardrail presence and review cadence (4, 5), the **velocity model** encodes deterministic behaviour and budgets (1, 2), the **modeler's HITL field** records the human-interaction contract per loop (3, 5), and the **realization design rules** bound ambition by experience (6, 7).
