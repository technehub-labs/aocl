# Value Streams: HITL/HOTL/HOOTL per stage

**Status:** draft (v0.1.0) · **Source:** §6.1 ("Deep Dive & Reference Cases") · **Companion:** `docs/use-cases.md`

Reference to the AOCL assurance value-stream research: an organisation's assurance value streams are the primary candidates for closed-loop integration. Each stream decomposes into **stages**, each requiring an explicit human-interaction model:

- **HITL** — human-in-the-loop: humans participate in decision-making, continuously or on exception.
- **HOTL** — human-on-the-loop: the loop acts autonomously; humans supervise and can intervene.
- **HOOTL** — human-out-of-the-loop: the loop acts; humans govern at the strategic level.

The engine derives the level-appropriate default (L1–L2 HITL · L3–L4 HOTL · L5 HOOTL); the ledger records what is actually deployed per stage.

## "Detect and Handle Anomaly Event" — the Stability Engine

Goal: service availability > 99.99% by minimizing the gap between event occurrence and rectification.

**Stage 1 — Detect Anomaly Event** *(MAPE: Monitor)*
- L1/L2 (HITL): humans watch dashboards; alarms are silos.
- L3/L4 (HOTL): AI-driven trouble-ticket compression cuts alarm noise > 80%; deterioration predicted ~15 minutes before impact.
- L5 (HOOTL): self-curated data ecosystems identify "silent deterioration" through cross-domain pattern matching without predefined rules.

**Stage 2 — Analyze Anomaly Event (Diagnosis)**
Goal: accurate root-cause identification; prevent "No Fault Found" site visits.
- HITL: engineer traces a signaling storm across five CLIs — 120 minutes.
- HOTL: a diagnosis bot proposes three candidate causes (BGP flapping / hardware / congestion); the human confirms — 5 minutes.
- HOOTL: the system self-tests the suspect interface, verifies the fault, initiates a virtual re-route — 10 seconds.

**Stage 3 — Determine and Execute Solution**
Goal: fastest recovery with minimal service loss. Loop mechanics: a **fast inner loop** (automated traffic re-routing at the SDN layer) inside a **slow outer loop** (policy adjustment preventing next week's congestion pattern).
- HITL: human drafts the change, CAB approval, manual execution.
- HOTL: system proposes a golden-configuration update; human approves.
- HOOTL: system applies a transient fix, monitors success, then evolves network policy to mitigate permanently.

## "Assure and Improve Customer Network Experience" — QoE

Quality of Experience, not just up/down availability.

**Detect Customer Network Experience GAP** — CEI and NNPS as primary sensors: L2 post-event complaints; L4 predictive modelling finds "silently suffering" users (poor video streaming, no complaint); L5 autonomous slice experimentation optimizing QoE for high-value segments in real time.

**Design Optimization Solution** — the logic engine is Next-Best-Action: the "solution" is not only a technical fix (antenna tilt) but an **operational offer** ("we detected poor Wi-Fi; here's a free mesh extender").

## "Resolve Customer Network Complaints"

- **Receive and Triage** — multi-channel bots (chat, voice, app) as initial sensing; the bot doesn't just talk: it initiates a **sub-loop** checking the customer's fiber line status in real time while the customer types.
- **Identify Root Cause & Execute Plan** — the trouble ticket becomes a **"living object"** travelling the MAPE-K cycle, picking up data-veracity markers at each hop.

## Using these streams

Map each stage to a loop in the [modeler](loop-modeler.md): the stage is the **entity** (kind: process); the loop's level follows the stage's HITL ambition; inner/outer loop pairs become `HIERARCHICAL` links. The ledger then tracks every stage-loop's review cadence and guardrails.
