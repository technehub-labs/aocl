# CLAM Alignment: the Closed-Loop-Management contract

**Status:** draft (v0.1.0) · **Upstream:** [emmanuel-a-otchere/Closed-Loop-Management](https://github.com/emmanuel-a-otchere/Closed-Loop-Management) · **Code of record:** `src/aocl/model.py`, `schema/loop-model.schema.json`, `schema/clm-export.schema.json`

The Loop Modeler does not invent a loop format — it emits loop specifications aligned with **CLAM** (Closed-Loop-Automation-Management, data model 1.0), the service/data model that treats closed loops as first-class managed artifacts: discoverable, lifecycle-controlled, interlinkable, observable.

## What CLAM defines (data model 1.0)

| CLAM entity | Shape (abridged) |
|---|---|
| `ClosedLoop` | `id` (uuid, readOnly) · `name` · `description` · `decisionModelRef {id, kind}` · `goals[]` · `workflows[]` · `links[]` · `state` · `createdAt/updatedAt` |
| `DecisionModel` | Discriminated union by `kind`: **OODA** {observe, orient, decide, act} · **MAPE** {monitor, analyze, plan, execute} · **CUSTOM** {steps[]} — each step an `ActivityRef` |
| `Goal` | `{name, target {metric, value, unit?, direction: AT_LEAST\|AT_MOST\|EXACTLY}, scope}` |
| `Workflow` | `{name, path: FEEDFORWARD\|FEEDBACK, activities[]}` |
| `Activity` | `{name, action (implementation ref), inputs[], outputs[]}` |
| `ClosedLoopLink` | `{source, target, kind: DAISY_CHAIN\|HIERARCHICAL\|FEEDBACK, condition? (CEL-like)}` |
| `ClosedLoopState` | `designed → validated → published → active ⇄ paused / error → retired` |

**Decision-model kinds in CLAM: OODA, MAPE, CUSTOM** — consistent with this repository's scope (see [decision-models.md](decision-models.md)).

## The mapping (AOCL → CLAM)

| AOCL model field | CLAM target | Notes |
|---|---|---|
| `loop.id` | `ClosedLoop.name` | CLAM requires tenant-unique names; AOCL ids are slugs |
| `loop.notes` / entity context | `ClosedLoop.description` | Human-readable; the AOCL block carries the structured context |
| `loop.decision_model` | `DecisionModel` (+ `decisionModelRef`) | Steps map 1:1: OODA observe/orient/decide/act; MAPE monitor/analyze/plan/execute; CUSTOM steps |
| `loop.goals[]` | `Goal[]` | `{metric, value, unit?, direction, scope}` verbatim |
| `model.links[]` | `ClosedLoopLink[]` | `{source, target, kind, condition?}` verbatim (by loop name) |
| — | `state` | CLAM lifecycle enum carried in both the model and the ledger |
| `loop.entity`, `velocity`, `level`, `vector_scores`, `hitl` | **AOCL context block** (`aocl` in the export) | Not part of CLAM — carried alongside so no information is lost |

## The export (`aocl-clam-export`)

`aocl-model model.yaml --clam` (or the modeler's *Export CLAM payloads* button) emits:

```json
{
  "export_format": "aocl-clam-export",
  "export_version": "1.0.0",
  "decision_models": [ { "kind": "MAPE", "name": "loop-anomaly-detect-v1-dm",
                          "monitor": {"id": "read-kpis", "name": "read-kpis"}, ... } ],
  "closed_loops":   [ { "name": "loop-anomaly-detect-v1", "description": "...",
                        "decision_model": "loop-anomaly-detect-v1-dm",
                        "goals": [...], "links": [...],
                        "aocl": {"entity": "proc-anomaly-detect", "entity_kind": "process",
                                  "velocity": "fast", "level": 3, ...} } ]
}
```

## Provisioning sequence (POSTing into the CLAM service)

1. `POST /decisionModel` for each entry in `decision_models[]` (kind + step ActivityRefs) — capture the returned uuids.
2. `POST /closedLoop` for each entry in `closed_loops[]` with `{name, description, decisionModelRef: {id: <returned uuid>, kind}, state}`.
3. `POST /closedLoop/{id}/goal` for each goal; `POST /closedLoop/{id}/link` for links (after both endpoints exist).
4. Transition lifecycle explicitly via `POST /closedLoop/{id}/state` following the CLAM state machine (`designed → validated → published → active`).

The `aocl` context block is not POSTed — it is the AOCL-side record (the ledger's fields) that stays paired with each loop in this repository's files.

## Boundary and drift policy

- AOCL consumes CLAM's **format**; it does not reimplement CLAM's service, lifecycle engine, or toolkits. No CLAM code is vendored.
- The alignment is pinned to **CLAM data model 1.0** (verified against `schemas/data-model/clam-data-model-1.0.md`, 2026-11). A CLAM data-model MAJOR bump requires an AOCL ADR-style note in `CHANGELOG.md` plus schema updates and corpus cases — same discipline as the ruleset version.
- Validation is symmetric: the modeler/CLI validate the AOCL model *before* export; importing an `aocl-clam-export` back is not supported in v0.1 (the CLAM service is the system of record once provisioned — the ledger tracks the deployed loop).
