# Reference Use Cases

**Status:** draft (v0.1.0) · **Source:** §6.2–6.3 · Each use case is a candidate **entity + loop set** in the [modeler](loop-modeler.md); the level progressions below are the document's own narratives.

## Telecom Operator use cases

### 1. RAN Self-Optimisation (5G NR)
Objective: maximize spectral efficiency and user throughput while minimizing energy and interference.
- **L1**: alarms to the NOC; engineer investigates (45-min manual reroute); industrial downtime. *(HITL)*
- **L2**: threshold alarms trigger manual workflows; neighbor lists via scheduled scripts; drive-test-based tuning. *(HITL)*
- **L3**: trend-analysis bot detects a 10% latency trend, proposes slice expansion; human approves in 10 minutes. *(HOTL)*
- **L4**: RL agents continuously adjust tilts, power, handover margins; rogue-interference detection auto-reconfigures spectrum; weekly retraining. *(HOTL)*
- **L5**: autonomous objective definition from business priorities (indoor coverage at business hours, stadium events on match days); digital-twin beamforming trials; sleep-mode experimentation. *(HOOTL)*
- **Reference scenario**: sub-millisecond telemetry → a "Slice Governor" detects neighbor-cell patterns historically leading to URLLC congestion → creates a *transient shadow slice*, moves non-critical traffic, expands URLLC capacity → daily human report: "pre-empted 12 SLA breaches; ROI saved: $500k". **Mathematical profile: E = 0.99, C = 4.2 → R = √(0.99² + 4.2²) ≈ 4.32** — the effort is justified by the value stream's mission criticality.

### 2. Network Slicing Assurance (5G Core + Transport)
Guarantee slice SLAs over shared infrastructure: L2 static reservations + overprovisioning → L3 predictive reallocation and isolation of degrading resources → L4 AI-driven dynamic scaling, cross-domain root-cause (RAN/transport/core), automated slice-fault remediation → L5 **autonomous slice lifecycle** (creation, optimization, retirement by demand and business value) with generative slice-template design for novel cases (holographic comms, platooning).

### 3. Customer Experience Management
Proactive issue remediation before churn: L2 reactive tickets + static IVR → L3 proactive outreach from usage anomalies → L4 churn-risk models over KPIs/devices/sentiment with auto-delivered retention offers → L5 autonomous design and testing of bundles, pricing, engagement strategies on micro-segments.

### 4. Energy Management
Minimize energy within coverage/capacity commitments: L2 time-of-day cell shutdown → L3 forecast-based sleep activation → L4 ML-optimised sleep scheduling (multi-cell coordination, emergency services, renewables) → L5 **autonomous energy-market participation** (buy/sell/store on price and carbon signals; cooling-strategy experimentation in digital twins).

### 5. Cybersecurity & Fraud Management
Detect, prevent, remediate in real time: L2 rule firewalls + volume alerts → L3 statistical signalling anomaly detection, proactive fraud-route blocking → L4 behavioural biometrics, continuous threat-signature learning, automated quarantine → L5 **autonomous threat-hunting agents** hypothesizing novel attack vectors, sandboxing them, and deploying countermeasures pre-materialization.

## Digital Service Provider use cases

### 6. Cloud-Native Application Orchestration (L4–L5)
Continuous workload rebalancing across clouds on real-time pricing/performance/compliance; self-updating orchestration policies; container-scheduling experimentation.

### 7. IT Service Management (L4–L5)
Autonomous incident categorization, change-correlation, causal root-cause, playbook execution; novel incidents get new playbooks designed **and tested in simulation before production**.

### 8. Edge Computing Orchestration (L5)
Autonomous edge placement from mobility prediction, content popularity, energy cost; application-partitioning (cloud vs edge) experimentation learning optimal policies for emerging app types.

## The consistent theme

Every case ascends the same ladder — and the [abstraction dimensions](maturity-model.md#abstraction-at-higher-levels) (parameter → temporal → semantic) explain why senior humans get *more* strategic as loops mature, not less relevant. Model each case as: entity (process/system/function) → loop set per level ambition → `HIERARCHICAL` links from the strategic slow loop to the reactive fast loops.
