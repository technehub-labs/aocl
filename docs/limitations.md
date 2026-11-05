# Limitations

**Status:** draft (v0.1.0)

What AOCL claims, and — more importantly — what it does not.

## The realization model is a heuristic

R = √(E² + (C·V_d)²) and every number derived from it are **informative planning aids**. The source document states this explicitly and this repository preserves it on every surface (CLI outputs, site banner, export fields). Table 1.1 values are theoretical illustrations, **not measured benchmarks**; the value models (logarithmic/exponential) have no validated α/β calibration. Never use the model for contractual commitments, certification claims, or investment audits.

## A maturity level is not safety, compliance, or authority

- A loop scored L5 is not **safe** — safety comes from the guardrails, envelopes, and tested escalation paths (assumption 4; the ledger enforces guardrail presence, not their quality).
- An assessment is not a **certification** or regulatory approval, and confers none.
- A loop's maturity level is not an **autonomy grant**: the lowercase `mama` method (decision-rights, contracts, grants) is a separate instrument. A loop operating inside an L2 grant can be maturity L5; the two scales are never merged (see [naming.md](naming.md)).

## The assessment instrument is derived and unvalidated

The questionnaire in `model/questions.yaml` is **synthesized from the source document's own per-level vector characteristics** — the document ships no instrument. No inter-rater reliability study, sector calibration, or predictive-validity evidence exists yet. Treat scores as structured self-assessments pending validation; the weakest-link aggregation is a conservative rule, not an empirical finding.

## Decision-model guidance is advisory

The (level × velocity) → (OODA/MAPE) mapping is derived from the document's level descriptions. Real architectures may legitimately differ; the ledger records what is deployed rather than enforcing the suggestion. The source document's third surveyed decision model (§7.3) is out of scope here by project decision.

## The modeler is design-time only

The modeler's state lives in browser localStorage; exports are files. It does not provision anything by itself, does not replace the CLAM service as system of record, and does not import CLAM state back (v0.1). The `aocl-clam-export` payloads must be reviewed before POSTing — the export is a provisioning *draft*, not an approval.

## Coverage

The source document is telecom/digital-service oriented (RAN, slicing, CEM, energy, security, cloud, ITSM, edge). The model's constructs are sector-neutral, but every worked example is a digital-infrastructure case; other sectors should expect to add domain-specific evidence norms.

## No endorsement

References to TechNE Hub assets (GB1040/GB1042A/GB1054/GB1075, IG1219, IG1291A, IG1550/IG1552) are attribution of origin. No standards-body endorsement, conformity, or equivalence is claimed in either direction. CLAM alignment is a format contract, not a product integration claim.
