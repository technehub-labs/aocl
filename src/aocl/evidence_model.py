"""AOCL verification and evidence model (AOCL-CR-008).

Implements validation rules VER-001..050 natively (stdlib + pyyaml) and reports
the conformance profiles of CR-008 §19 separately — evidence structural,
provenance, quality, verification, assurance, transition verification, outcome
verification, simulation evidence, operational evidence, traceability.

Enforces the semantic boundaries that make evidence defensible:

- Execution evidence never establishes an outcome (VER-036): outcome claims
  require outcome-level evidence (OutcomeEvidence / ObservationEvidence /
  StateEvidence); command or execution records alone cannot verify an outcome
  (AD-008-07, P04).
- Transition claims require established-state evidence, not just the command
  that requested the transition (VER-034).
- Failure is distinct from insufficient evidence (AD-008-08): Failed,
  Inconclusive and Conflicting are separate governed outcomes; conflicting
  evidence is preserved, never silently resolved (VER-024, AD-008-10).
- Self-verification is never represented as independent verification
  (VER-029); safety/regulatory-critical claims need independent assurance
  (VER-030).
- Simulation evidence never substitutes for operational evidence (AD-008-11):
  origin classes are enforced per type, operational evidence must carry its
  operating context (VER-041), and cross-origin comparisons preserve origin
  classifications (VER-042).
- Positive results require evidence (VER-014); a criterion improved KPI never
  satisfies a claim by itself (P02); numeric confidence must identify its
  interpretation and derivation (VER-023).
- Incomplete chains are reported explicitly (VER-050); dispositions never
  overwrite original results (VER-017); supersession preserves history
  (VER-025, AD-008-14).

Also migrates control-model verification references into Draft evidence-model
skeletons (CR-008 §22): claims are carried as claims; assessment and
realization scores are deliberately NOT imported as evidence records
(AD-008-13); no evidence or results are fabricated.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("error: pyyaml is required for the evidence model (pip install pyyaml)")

RULESET_VERSION = "1.0.0"
SCHEMA_VERSION = "0.1"

EVIDENCE_TYPES = {"ObservationEvidence", "StateEvidence", "DecisionEvidence", "AuthorizationEvidence",
                  "CommandEvidence", "ExecutionEvidence", "TransitionEvidence", "OutcomeEvidence",
                  "ConstraintEvidence", "SafetyEvidence", "TestEvidence", "SimulationEvidence",
                  "AuditEvidence", "HumanAttestation"}
ORIGIN_CLASSES = {"DesignTime", "TestTime", "SimulationTime", "DeploymentTime", "OperationalTime", "AuditTime"}
OUTCOMES = {"Verified", "NotVerified", "Failed", "Inconclusive", "Conflicting", "NotApplicable",
            "Deferred", "Invalid"}
CLAIM_TYPES = {"Authorization", "Execution", "Transition", "Outcome", "Constraint", "Safety",
               "Learning", "Behavioral"}
INDEPENDENCE = {"Self", "Peer", "Supervisory", "Independent", "ExternalAssurance"}
CLAIM_ROLES = {"Supports", "Contradicts", "Qualifies", "Contextualizes", "Supersedes", "DerivedFrom"}
RELATIONSHIP_ROLES = {"Supports", "Contradicts", "Qualifies"}
# Evidence that can establish an ESTABLISHED transition or an OUTCOME.
STATE_LEVEL_TYPES = {"StateEvidence", "TransitionEvidence", "ObservationEvidence"}
OUTCOME_LEVEL_TYPES = {"OutcomeEvidence", "ObservationEvidence", "StateEvidence"}
COMMAND_LEVEL_TYPES = {"CommandEvidence", "ExecutionEvidence", "DecisionEvidence", "AuthorizationEvidence"}

SEMVER = re.compile(r"^\d+\.\d+\.\d+$")
EV_URN = re.compile(r"^urn:aocl:evidence:[a-z0-9][a-z0-9-]*$")
LOOP_URN = re.compile(r"^urn:aocl:loop:[a-z0-9][a-z0-9-]*$")

PROFILE_RULES = {
    "evidenceStructural": {"VER-001", "VER-002", "VER-003", "VER-004", "VER-005"},
    "evidenceProvenance": {"VER-006", "VER-007", "VER-008", "VER-009"},
    "evidenceQuality": {"VER-019", "VER-020", "VER-021", "VER-022", "VER-023", "VER-024", "VER-025"},
    "verificationConformance": {"VER-010", "VER-011", "VER-012", "VER-013", "VER-014", "VER-015",
                                "VER-016", "VER-017", "VER-018", "VER-044", "VER-045"},
    "assuranceConformance": {"VER-026", "VER-027", "VER-028", "VER-029", "VER-030"},
    "transitionVerification": {"VER-034", "VER-036"},
    "outcomeVerification": {"VER-031", "VER-035", "VER-036", "VER-037", "VER-038"},
    "simulationEvidenceConformance": {"VER-039", "VER-040", "VER-043"},
    "operationalEvidenceConformance": {"VER-041", "VER-042"},
    "traceabilityConformance": {"VER-046", "VER-047", "VER-048", "VER-049", "VER-050", "VER-001"},
}


def _f(findings: list, rule: str, severity: str, message: str) -> None:
    findings.append({"rule": rule, "severity": severity, "message": message})


def _unresolved_report(findings: list, entity: str, item: dict) -> None:
    if item.get("unresolved"):
        note = str(item.get("unresolvedNote", "")).strip()
        if not note:
            _f(findings, "VER-050", "error", f"{entity}: marked unresolved without an explanatory note")
        else:
            findings.append({"rule": "VER-050", "severity": "warning",
                             "message": f"{entity}: unresolved — {note} (incomplete chain reported explicitly, VER-050)"})


def validate_evidence_model(data: dict) -> dict:
    """Validate a canonical evidence-model document against VER-001..050.
    Returns findings and the §19 conformance profiles."""
    findings: list[dict] = []

    if not isinstance(data, dict):
        _f(findings, "VER-048", "error", "document must be a mapping")
        return _result(findings)
    if data.get("schemaVersion") != SCHEMA_VERSION:
        _f(findings, "VER-048", "error",
           f"schemaVersion must be '{SCHEMA_VERSION}' (this validator's contract), got {data.get('schemaVersion')!r}")
    if not SEMVER.match(str(data.get("modelVersion", ""))):
        _f(findings, "VER-048", "error", f"modelVersion must be semver, got {data.get('modelVersion')!r}")

    model = data.get("evidenceModel")
    if not isinstance(model, dict):
        _f(findings, "VER-048", "error", "evidenceModel missing")
        return _result(findings)

    known_root = {"schemaVersion", "modelVersion", "evidenceModel"}
    if set(data) - known_root:
        _f(findings, "VER-048", "error", f"unknown document attributes: {sorted(set(data) - known_root)}")

    if not EV_URN.match(str(model.get("id", ""))):
        _f(findings, "VER-047", "error", "evidenceModel.id must match urn:aocl:evidence:<slug>")
    if model.get("type") != "EvidenceModel":
        _f(findings, "VER-047", "error", "evidenceModel.type must be 'EvidenceModel'")
    if not str(model.get("name", "")).strip() or not str(model.get("definition", "")).strip():
        _f(findings, "VER-047", "error", "evidenceModel.name and .definition are mandatory")
    clr = model.get("closedLoopRef")
    if not isinstance(clr, dict) or not LOOP_URN.match(str(clr.get("loopId", ""))) \
            or not str(clr.get("sourceSystem", "")).strip():
        _f(findings, "VER-046", "error", "closedLoopRef must identify the governed ClosedLoop and its source system")

    known_model = {"id", "type", "name", "definition", "closedLoopRef", "evidenceSources", "evidence",
                   "provenance", "qualityAssessments", "integrity", "claims", "criteria", "methods",
                   "verifications", "results", "findings", "dispositions", "conflicts", "assurances",
                   "crossOriginComparisons", "migrationNotes"}
    unknown = set(model) - known_model
    if unknown:
        _f(findings, "VER-048", "error", f"evidenceModel: unknown attributes {sorted(unknown)}")

    # ---------------- sources
    sources = model.get("evidenceSources") or []
    source_ids = {s.get("sourceId") for s in sources if isinstance(s, dict) and s.get("sourceId")}
    for s in sources:
        if not isinstance(s, dict):
            _f(findings, "VER-003", "error", "evidenceSources entries must be mappings")
            continue
        if not str(s.get("sourceId", "")).strip() or len(str(s.get("sourceId"))) < 3:
            _f(findings, "VER-003", "error", "evidence source: stable id missing")

    # ---------------- evidence (VER-001..009, 044)
    evidence = model.get("evidence") or []
    evidence_ids: list = []
    evidence_by_id: dict = {}
    for e in evidence:
        if not isinstance(e, dict):
            _f(findings, "VER-001", "error", "evidence entries must be mappings")
            continue
        eid = e.get("evidenceId", "<missing>")
        evidence_ids.append(eid)
        evidence_by_id[eid] = e
        if not str(e.get("evidenceId", "")).strip() or len(str(eid)) < 3:
            _f(findings, "VER-001", "error", f"evidence {eid}: stable identifier missing (VER-001)")
        if e.get("evidenceType") not in EVIDENCE_TYPES:
            _f(findings, "VER-002", "error", f"evidence {eid}: declared type {e.get('evidenceType')!r} is not canonical (VER-002)")
        sref, unknown = e.get("sourceRef"), e.get("sourceUnknown")
        if not str(sref or "").strip() and unknown is not True:
            _f(findings, "VER-003", "error",
               f"evidence {eid}: must identify its source or explicitly declare sourceUnknown with a note (VER-003)")
        elif unknown is True and not str(e.get("sourceUnknownNote", "")).strip():
            _f(findings, "VER-003", "error", f"evidence {eid}: sourceUnknown requires an explanatory note (VER-003)")
        elif sref and sref not in source_ids:
            _f(findings, "VER-003", "error", f"evidence {eid}: sourceRef {sref!r} does not resolve (VER-003)")
        if not str(e.get("subjectRef", "")).strip():
            _f(findings, "VER-005", "error", f"evidence {eid}: subject or applicable scope missing (VER-005)")
        if e.get("evidenceType") in ("ObservationEvidence", "TransitionEvidence", "OutcomeEvidence") \
                and not str(e.get("temporalRef", "")).strip():
            _f(findings, "VER-004", "error",
               f"evidence {eid}: time-sensitive evidence must preserve its temporal reference — "
               "acquisition time, not ingestion time (VER-004, §11.3)")
        if e.get("originClass") not in ORIGIN_CLASSES:
            _f(findings, "VER-008", "error",
               f"evidence {eid}: originClass {e.get('originClass')!r} invalid — simulation, test and "
               "operational contexts remain distinct (VER-008, AD-008-06)")
        if e.get("evidenceType") == "SimulationEvidence":
            if e.get("originClass") != "SimulationTime":
                _f(findings, "VER-040", "error",
                   f"evidence {eid}: SimulationEvidence must carry SimulationTime origin (VER-040, AD-008-11)")
            run = e.get("simulationRun") or {}
            if not all(str(run.get(k) or "").strip() for k in ("runId", "scenarioRef", "engineVersion")):
                _f(findings, "VER-039", "error",
                   f"evidence {eid}: SimulationEvidence must identify the simulation run, scenario and engine "
                   "version plus the model versions in force (VER-039)")
        if e.get("originClass") == "OperationalTime":
            if not str(e.get("contextRef", "")).strip():
                _f(findings, "VER-041", "error",
                   f"evidence {eid}: OperationalEvidence must identify its operating context — the real "
                   "operating environment stays distinguishable from simulation or test (VER-041, §15.3)")
        for dref in e.get("derivedFromRefs", []) or []:
            if dref not in evidence_by_id:
                _f(findings, "VER-007", "error", f"evidence {eid}: derived evidence must retain traceability to its source (VER-007)")
        for rel in e.get("claimRelationships", []) or []:
            if isinstance(rel, dict) and rel.get("role") not in CLAIM_ROLES:
                _f(findings, "VER-044", "error", f"evidence {eid}: claim relationship role {rel.get('role')!r} invalid (VER-044, §13.1)")
        if e.get("supersededBy"):
            if not str(e.get("supersessionReason", "")).strip():
                _f(findings, "VER-025", "error",
                   f"evidence {eid}: supersession must preserve the reason — the original record is retained, "
                   "never silently overwritten (VER-025, AD-008-14)")
            if e["supersededBy"] not in evidence_by_id and not str(e["supersededBy"]).startswith("urn:"):
                _f(findings, "VER-025", "error", f"evidence {eid}: supersededBy {e['supersededBy']!r} does not resolve")
        _unresolved_report(findings, f"evidence {eid}", e)
    if len(evidence_ids) != len(set(evidence_ids)):
        _f(findings, "VER-001", "error", "duplicate evidenceIds (VER-001)")

    # provenance / quality / integrity blocks
    prov_ids = {p.get("provenanceId") for p in (model.get("provenance") or []) if isinstance(p, dict)}
    for p in model.get("provenance") or []:
        if isinstance(p, dict) and not str(p.get("acquisitionTime", "")).strip():
            _f(findings, "VER-006", "error", f"provenance {p.get('provenanceId')}: acquisition time missing (VER-006, §11.3)")
    qual_ids = set()
    for q in model.get("qualityAssessments") or []:
        if not isinstance(q, dict):
            continue
        qid = q.get("qualityId", "<missing>")
        qual_ids.add(qid)
        if q.get("evidenceRef") not in evidence_by_id:
            _f(findings, "VER-019", "error", f"quality assessment {qid}: evidenceRef does not resolve (VER-019)")
        dims = q.get("dimensions") or {}
        if not dims:
            _f(findings, "VER-019", "error", f"quality assessment {qid}: assess at least one applicable dimension (VER-019)")
    integ_ids = set()
    for i in model.get("integrity") or []:
        if not isinstance(i, dict):
            continue
        iid = i.get("integrityId", "<missing>")
        integ_ids.add(iid)
        if i.get("evidenceRef") not in evidence_by_id:
            _f(findings, "VER-021", "error", f"integrity record {iid}: evidenceRef does not resolve (VER-021)")
    for eid, e in evidence_by_id.items():
        if e.get("provenanceRef") and e["provenanceRef"] not in prov_ids:
            _f(findings, "VER-006", "error", f"evidence {eid}: provenanceRef {e['provenanceRef']!r} does not resolve (VER-006)")
        if e.get("originClass") in ("OperationalTime", "DeploymentTime", "AuditTime") and not e.get("provenanceRef"):
            _f(findings, "VER-006", "error",
               f"evidence {eid}: operational/deployment/audit evidence must carry its provenance record (VER-006, AD-008-04)")
        if e.get("qualityRef") and e["qualityRef"] not in qual_ids:
            _f(findings, "VER-019", "error", f"evidence {eid}: qualityRef {e['qualityRef']!r} does not resolve (VER-019)")
        if e.get("integrityRef") and e["integrityRef"] not in integ_ids:
            _f(findings, "VER-021", "error", f"evidence {eid}: integrityRef {e['integrityRef']!r} does not resolve (VER-021)")

    # ---------------- claims / criteria / methods
    claims = model.get("claims") or []
    claim_ids: set = set()
    claims_by_id: dict = {}
    assurance_ids = {a.get("assuranceId") for a in (model.get("assurances") or []) if isinstance(a, dict)}
    criteria_ids = {c.get("criterionId") for c in (model.get("criteria") or []) if isinstance(c, dict)}
    method_ids = {m.get("methodId") for m in (model.get("methods") or []) if isinstance(m, dict)}
    for c in claims:
        if not isinstance(c, dict):
            _f(findings, "VER-011", "error", "claims entries must be mappings")
            continue
        cid = c.get("claimId", "<missing>")
        claim_ids.add(cid)
        claims_by_id[cid] = c
        if not str(c.get("subject", "")).strip() or not str(c.get("proposition", "")).strip():
            _f(findings, "VER-011", "error", f"claim {cid}: subject and proposition are mandatory (VER-011, §8.2)")
        if c.get("claimType") not in CLAIM_TYPES:
            _f(findings, "VER-002", "error", f"claim {cid}: claimType {c.get('claimType')!r} not governed (AD-008-07)")
        if c.get("claimType") == "Outcome":
            if not str(c.get("goalRef", "")).strip():
                _f(findings, "VER-031", "error", f"claim {cid}: Outcome claims must reference their Goal (VER-031/046)")
            if not str(c.get("successCriterionRef", "")).strip():
                _f(findings, "VER-031", "error", f"claim {cid}: Outcome claims must reference their success criterion (VER-031)")
        if c.get("claimType") == "Learning" and not str(c.get("learningGovernanceRef", "")).strip():
            _f(findings, "VER-038", "error", f"claim {cid}: Learning claims must reference their governance boundary (VER-038)")
        if c.get("criticality") in ("Safety", "Regulatory"):
            aref = c.get("assuranceRef")
            if not aref:
                _f(findings, "VER-030", "error",
                   f"claim {cid}: safety/regulatory-critical claims require an assurance requirement (VER-030, P11)")
            elif aref not in assurance_ids:
                _f(findings, "VER-027", "error", f"claim {cid}: assuranceRef {aref!r} does not resolve (VER-027)")
        elif c.get("assuranceRef") and c["assuranceRef"] not in assurance_ids:
            _f(findings, "VER-027", "error", f"claim {cid}: assuranceRef {c['assuranceRef']!r} does not resolve (VER-027)")
        _unresolved_report(findings, f"claim {cid}", c)
    if not claims:
        _f(findings, "VER-011", "error", "at least one verification claim is required")
    for a in model.get("assurances") or []:
        if isinstance(a, dict) and not str(a.get("governingRef", "")).strip():
            _f(findings, "VER-028", "error", f"assurance {a.get('assuranceId')}: must be traceable to its governing basis (VER-028)")
    for cr in model.get("criteria") or []:
        if isinstance(cr, dict) and not str(cr.get("subjectRef", "")).strip():
            _f(findings, "VER-012", "error", f"criterion {cr.get('criterionId')}: evaluation subject missing (VER-012)")

    # ---------------- verifications (VER-010..013, 026..029, 043)
    verifications = model.get("verifications") or []
    verification_ids = set()
    verified_claims: set = set()
    for v in verifications:
        if not isinstance(v, dict):
            _f(findings, "VER-010", "error", "verifications entries must be mappings")
            continue
        vid = v.get("verificationId", "<missing>")
        verification_ids.add(vid)
        if not str(v.get("verificationScope", "")).strip():
            _f(findings, "VER-010", "error", f"verification {vid}: scope missing (VER-010)")
        vclaims = v.get("claimRefs") or []
        if not vclaims:
            _f(findings, "VER-011", "error", f"verification {vid}: must reference claims (VER-011)")
        for ref in vclaims:
            if ref not in claim_ids:
                _f(findings, "VER-011", "error", f"verification {vid}: claimRef {ref!r} does not resolve")
        for ref in v.get("criterionRefs", []) or []:
            if ref not in criteria_ids:
                _f(findings, "VER-012", "error", f"verification {vid}: criterionRef {ref!r} does not resolve (VER-012)")
        for ref in v.get("methodRefs", []) or []:
            if ref not in method_ids:
                _f(findings, "VER-013", "error", f"verification {vid}: methodRef {ref!r} does not resolve (VER-013)")
        for ref in v.get("evidenceRefs", []) or []:
            if ref not in evidence_by_id:
                _f(findings, "VER-014", "error", f"verification {vid}: evidenceRef {ref!r} does not resolve")
        if v.get("independenceClass") not in INDEPENDENCE:
            _f(findings, "VER-026", "error", f"verification {vid}: independenceClass {v.get('independenceClass')!r} not governed (VER-026)")
        verifier = str(v.get("verifierRef", "")).strip()
        for ref in vclaims:
            subj = str((claims_by_id.get(ref) or {}).get("subject", "")).strip()
            if verifier and subj and verifier == subj and v.get("independenceClass") != "Self":
                _f(findings, "VER-029", "error",
                   f"verification {vid}: verifier {verifier!r} is the claim's own subject — self-verification "
                   "is never represented as independent verification (VER-029, §12.2)")
        if v.get("independenceRequirementRef") and not str(v["independenceRequirementRef"]).strip():
            _f(findings, "VER-027", "error", f"verification {vid}: independence requirement reference empty (VER-027)")
        sim_evidence = [r for r in (v.get("evidenceRefs") or [])
                        if isinstance(evidence_by_id.get(r), dict) and evidence_by_id[r].get("evidenceType") == "SimulationEvidence"]
        if sim_evidence and not str(v.get("assumptionsAndLimitations", "")).strip():
            _f(findings, "VER-043", "error",
               f"verification {vid}: simulation-based verification must identify its assumptions and limitations (VER-043)")
        # VER-012: every evaluated claim must have applicable criteria via results
        v_results = [r for r in (model.get("results") or [])
                     if isinstance(r, dict) and r.get("verificationRef") == vid]
        covered = {r.get("claimRef") for r in v_results if r.get("criterionRef") in criteria_ids}
        for ref in vclaims:
            if ref not in covered:
                _f(findings, "VER-012", "error",
                   f"verification {vid}: claim {ref} is evaluated without an applicable criterion in any result (VER-012)")
            for r in v_results:
                if r.get("claimRef") == ref and r.get("outcome") in ("Verified", "Failed", "NotVerified"):
                    verified_claims.add(ref)

    # ---------------- results (VER-014..018, 034..037, 040, 044)
    result_ids = set()
    for r in model.get("results") or []:
        if not isinstance(r, dict):
            _f(findings, "VER-015", "error", "results entries must be mappings")
            continue
        rid = r.get("resultId", "<missing>")
        result_ids.add(rid)
        outcome = r.get("outcome")
        if r.get("verificationRef") not in verification_ids:
            _f(findings, "VER-010", "error", f"result {rid}: verificationRef {r.get('verificationRef')!r} does not resolve")
        cref = r.get("claimRef")
        if cref not in claim_ids:
            _f(findings, "VER-011", "error", f"result {rid}: claimRef {cref!r} does not resolve")
        if r.get("criterionRef") not in criteria_ids:
            _f(findings, "VER-045", "error", f"result {rid}: criterionRef {r.get('criterionRef')!r} does not resolve (VER-045)")
        if r.get("methodRef") not in method_ids:
            _f(findings, "VER-045", "error", f"result {rid}: methodRef {r.get('methodRef')!r} does not resolve (VER-045)")
        if outcome not in OUTCOMES:
            _f(findings, "VER-015", "error", f"result {rid}: outcome {outcome!r} not governed (VER-015, AD-008-08)")
        ev_refs = r.get("evidenceRefs") or []
        bad_ev = [x for x in ev_refs if x not in evidence_by_id]
        if bad_ev:
            _f(findings, "VER-014", "error", f"result {rid}: evidenceRefs do not resolve: {bad_ev}")
        if outcome == "Verified" and not ev_refs:
            _f(findings, "VER-014", "error",
               f"result {rid}: a positive result requires identifiable evidence — claims are never verified "
               "without it (VER-014, P01)")
        if outcome == "NotApplicable" and not (str(r.get("limitations", "")).strip() and str(r.get("rationale", "")).strip()):
            _f(findings, "VER-018", "error", f"result {rid}: NotApplicable requires a justified applicability decision (VER-018)")
        if outcome == "Inconclusive" and not str(r.get("limitations", "")).strip():
            _f(findings, "VER-018", "error",
               f"result {rid}: Inconclusive must state what remains unestablished — insufficient evidence is "
               "never a success (VER-018, P07)")
        conf = r.get("confidence") or {}
        if conf.get("value") is not None and not str(conf.get("derivation", "")).strip():
            _f(findings, "VER-023", "error",
               f"result {rid}: numeric confidence must identify its derivation — meaning, scale and assumptions "
               "stay attached (VER-023, §11.4)")
        if not str(r.get("rationale", "")).strip():
            _f(findings, "VER-045", "error", f"result {rid}: rationale required — conclusions must be explainable (P08, P10)")

        claim = claims_by_id.get(cref) or {}
        ctype = claim.get("claimType")
        ev_types = {evidence_by_id[x].get("evidenceType") for x in ev_refs if isinstance(evidence_by_id.get(x), dict)}
        ev_origins = {evidence_by_id[x].get("originClass") for x in ev_refs if isinstance(evidence_by_id.get(x), dict)}
        if ctype == "Transition":
            if ev_refs and not (ev_types & STATE_LEVEL_TYPES):
                _f(findings, "VER-034", "error",
                   f"result {rid}: a transition claim supported only by command/execution evidence — a commanded "
                   "state is not an established state (VER-034, P05)")
            if claim.get("transitionRef") and outcome == "Verified" and not r.get("invariantResults"):
                findings.append({"rule": "VER-037", "severity": "warning",
                                 "message": f"result {rid}: transition verification should preserve applicable invariant results (VER-037)"})
        if ctype == "Outcome":
            if ev_refs and not (ev_types & OUTCOME_LEVEL_TYPES):
                _f(findings, "VER-036", "error",
                   f"result {rid}: evidence of actuator execution does not establish a Plant outcome — outcome "
                   "claims need outcome-level evidence (VER-036, AD-008-07)")
            if ev_origins and ev_origins <= {"SimulationTime"} and outcome == "Verified" \
                    and claim.get("criticality") in ("Safety", "Regulatory", "Operational"):
                _f(findings, "VER-040", "error",
                   f"result {rid}: a {claim.get('criticality')}-critical outcome claim verified solely on "
                   "simulation evidence — SimulationEvidence does not establish operational effectiveness (VER-040, AD-008-11)")
        if ctype == "Learning" and outcome == "Verified" and not ev_refs:
            _f(findings, "VER-038", "error", f"result {rid}: learning claims must be traceable to supporting evidence (VER-038)")
        # VER-020: time-sensitive claims need freshness-assessed or timestamped evidence
        if ctype in ("Execution", "Transition", "Outcome") and outcome in ("Verified", "Failed"):
            for x in ev_refs:
                e = evidence_by_id.get(x) or {}
                if not str(e.get("temporalRef", "")).strip():
                    q = next((qq for qq in (model.get("qualityAssessments") or [])
                              if isinstance(qq, dict) and qq.get("evidenceRef") == x
                              and isinstance(qq.get("dimensions"), dict) and "freshness" in qq["dimensions"]), None)
                    if q is None:
                        _f(findings, "VER-020", "error",
                           f"result {rid}: time-sensitive claim relies on evidence {x} with no temporal reference "
                           "and no freshness assessment (VER-020, §11.3)")

    # VER-016: material issues produce findings
    material = [r for r in (model.get("results") or [])
                if isinstance(r, dict) and r.get("outcome") in ("Failed", "Conflicting", "Invalid")]
    finding_result_refs = {f.get("resultRef") for f in (model.get("findings") or []) if isinstance(f, dict)}
    for r in material:
        if r.get("resultId") not in finding_result_refs:
            _f(findings, "VER-016", "error",
               f"result {r.get('resultId')}: a {r.get('outcome')} result must have a recorded finding (VER-016)")
    for fnd in model.get("findings") or []:
        if isinstance(fnd, dict) and fnd.get("severity") not in ("Critical", "Major", "Minor", "Observation"):
            _f(findings, "VER-016", "error", f"finding {fnd.get('findingId')}: severity not governed (VER-016)")

    # VER-017 dispositions
    for d in model.get("dispositions") or []:
        if not isinstance(d, dict):
            continue
        did = d.get("dispositionId", "<missing>")
        target = d.get("targetRef")
        if target not in result_ids and target not in {f.get("findingId") for f in (model.get("findings") or []) if isinstance(f, dict)}:
            _f(findings, "VER-017", "error", f"disposition {did}: targetRef {target!r} does not resolve")
        if d.get("preservesOriginalResult") is not True:
            _f(findings, "VER-017", "error",
               f"disposition {did}: must preserve the original result — a disposition never overwrites it (VER-017)")
        if d.get("disposition") == "Waive":
            w = d.get("waiver") or {}
            if not str(w.get("authorityRef", "")).strip() or not str(w.get("justification", "")).strip():
                _f(findings, "VER-017", "error",
                   f"disposition {did}: waivers must retain authorizing authority and justification (VER-017, §10.4)")

    # VER-024 conflicts
    conflict_evidence: set = set()
    for cf in model.get("conflicts") or []:
        if not isinstance(cf, dict):
            continue
        crefs = cf.get("evidenceRefs") or []
        bad = [x for x in crefs if x not in evidence_by_id]
        if bad or len(crefs) < 2:
            _f(findings, "VER-024", "error", f"conflict {cf.get('conflictId')}: needs ≥2 resolvable evidence records (VER-024)")
        conflict_evidence.update(crefs)
    for r in (model.get("results") or []):
        if isinstance(r, dict) and r.get("outcome") == "Conflicting":
            if not (set(r.get("evidenceRefs") or []) & conflict_evidence):
                _f(findings, "VER-024", "error",
                   f"result {r.get('resultId')}: conflicting outcome without a preserved conflict record — "
                   "conflicts are never silently resolved (VER-024, AD-008-10)")

    # VER-042 cross-origin comparisons
    for cmp_ in model.get("crossOriginComparisons") or []:
        if not isinstance(cmp_, dict):
            continue
        cid = cmp_.get("comparisonId", "<missing>")
        sim_refs = cmp_.get("simulationEvidenceRefs") or []
        op_refs = cmp_.get("operationalEvidenceRefs") or []
        for x in sim_refs:
            e = evidence_by_id.get(x) or {}
            if e.get("originClass") != "SimulationTime":
                _f(findings, "VER-042", "error", f"comparison {cid}: {x} is not simulation-origin evidence (VER-042)")
        for x in op_refs:
            e = evidence_by_id.get(x) or {}
            if e.get("originClass") != "OperationalTime":
                _f(findings, "VER-042", "error", f"comparison {cid}: {x} is not operational-origin evidence (VER-042)")
        if not sim_refs or not op_refs:
            _f(findings, "VER-042", "error", f"comparison {cid}: cross-origin comparison needs both origins (VER-042)")

    # VER-050: claims never evaluated are reported explicitly
    evaluated = {r.get("claimRef") for r in (model.get("results") or []) if isinstance(r, dict)}
    for cid in sorted(claim_ids - evaluated):
        findings.append({"rule": "VER-050", "severity": "warning",
                         "message": f"claim {cid} has no verification result — incomplete chain reported explicitly, "
                                    "not silently conformant (VER-050)"})

    return _result(findings)


def _result(findings: list) -> dict:
    errors = [f for f in findings if f["severity"] == "error"]
    hit = lambda rules: any(f["rule"] in rules for f in errors)
    profiles = {name: not hit(rules) for name, rules in PROFILE_RULES.items()}
    warnings = [f for f in findings if f["severity"] == "warning"]
    return {
        "valid": not errors,
        "findings": findings,
        "conformance": {**profiles,
                        "structurallyConformant": all(v for k, v in profiles.items()
                                                      if k in ("evidenceStructural", "evidenceProvenance",
                                                               "verificationConformance")),
                        "fullyConformant": all(profiles.values()) and not warnings,
                        "reportedGaps": len(warnings)},
    }


def load_and_validate(path: str | Path) -> dict:
    with open(path, encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    result = validate_evidence_model(data)
    result["source"] = str(path)
    return result


def migrate_from_control_model(control_doc: dict) -> dict:
    """Migrate a control-model document (CR-007) into a Draft evidence-model
    skeleton (CR-008 §22). Verification references become claims (text carried,
    typing unresolved); assessment and realization scores are deliberately NOT
    imported as evidence records (AD-008-13); no evidence or results are
    fabricated."""
    findings: list[dict] = []
    if not isinstance(control_doc, dict) or not isinstance(control_doc.get("controlModel"), dict):
        _f(findings, "MIG-001", "error", "expected a canonical control-model document (CR-007)")
        return {"valid": False, "findings": findings, "spec": None}
    cm = control_doc["controlModel"]
    short = str(cm.get("id", "unknown")).rsplit(":", 1)[-1]
    claims = []
    for v in cm.get("verificationRefs") or []:
        claims.append({
            "claimId": f"claim-{v.get('verificationRef', 'ref')}".replace("_", "-"),
            "subject": cm.get("closedLoopRef", {}).get("loopId", short),
            "proposition": v.get("claim", "unspecified verification claim"),
            "claimType": "Outcome",
            "goalRef": "",
            "unresolved": True,
            "unresolvedNote": "carried from a control-model verification reference — goal linkage, criteria "
                              "and required assurance are not yet modeled (§22)",
        })
    if not claims:
        claims.append({
            "claimId": "claim-carried-placeholder", "subject": short,
            "proposition": "No verification references existed in the control model — nothing carried.",
            "claimType": "Outcome", "unresolved": True,
            "unresolvedNote": "control model declared no verification references (§22)",
        })
    missing = [
        "EvidenceSource and provenance records (VER-003/006)",
        "Evidence records — none exist yet; none fabricated (VER-001..009)",
        "Criteria and methods (VER-012/013)",
        "Verification activities and results (VER-010..018)",
        "independence and assurance requirements (VER-026..030)",
    ]
    unresolved_mappings = [
        "existing maturity scores are NOT imported as evidence records — evidence and assessment scores "
        "remain separate concepts (AD-008-13, §22)",
        "existing realization records preserved by reference only; historical success indicators are not "
        "interpreted as independently verified outcomes (§22)",
    ]
    spec = {
        "schemaVersion": SCHEMA_VERSION,
        "modelVersion": "1.0.0",
        "evidenceModel": {
            "id": f"urn:aocl:evidence:{short}",
            "type": "EvidenceModel",
            "name": f"Migrated evidence model for {short}",
            "definition": f"Skeleton migrated from control model {cm.get('id', short)}; no evidence exists yet.",
            "closedLoopRef": {"loopId": cm.get("closedLoopRef", {}).get("loopId", f"urn:aocl:loop:{short}"),
                              "sourceSystem": "control-model migration"},
            "claims": claims,
            "migrationNotes": {"missingAttributes": missing, "unresolvedMappings": unresolved_mappings},
        },
    }
    _f(findings, "MIG-004", "warning",
       f"control model {short}: migrated to Draft with {len(missing)} missing evidence attributes "
       "inventoried — scores were not converted into evidence (AD-008-13)")
    result = validate_evidence_model(spec)
    result["skeletonConformance"] = result["conformance"]
    result["spec"] = spec
    result["findings"] = findings + result["findings"]
    return result


def render(result: dict) -> str:
    lines = [f"AOCL evidence model — {result.get('source', 'validation')}"]
    conf = result.get("conformance", {})
    order = [k for k in conf if k not in ("reportedGaps",)]
    lines.append(" · ".join(f"{k}={conf.get(k)}" for k in order))
    for f in result.get("findings", []):
        lines.append(f"[{f['severity'].upper()}] {f['rule']}: {f['message']}")
    if not result.get("findings"):
        lines.append("No findings — VER-001..050 satisfied.")
    return "\n".join(lines)


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--self-test" in argv:
        return _self_test()
    as_json = "--json" in argv
    argv = [a for a in argv if a != "--json"]
    if "--migrate" in argv:
        with open(argv[argv.index("--migrate") + 1], encoding="utf-8") as fh:
            doc = yaml.safe_load(fh)
        result = migrate_from_control_model(doc)
        print(json.dumps(result, indent=2, default=str) if as_json else render_migrated(result))
        # Migration succeeds when the skeleton is produced; its expected gaps are the diagnostics (§22).
        return 0 if result.get("spec") else 1
    if not argv:
        print("usage: aocl-evidence <model.yaml> [--json] | --migrate <control-contract.yaml> | --self-test")
        return 2
    try:
        result = load_and_validate(argv[0])
    except (OSError, ValueError) as exc:
        print(f"error: {exc}")
        return 2
    print(json.dumps(result, indent=2, default=str) if as_json else render(result))
    return 0 if result["valid"] else 1


def render_migrated(result: dict) -> str:
    lines = ["AOCL evidence model — migrated Draft skeleton (CR-008 §22)"]
    for f in result.get("findings", []):
        lines.append(f"[{f['severity'].upper()}] {f['rule']}: {f['message']}")
    return "\n".join(lines)


def _self_test() -> int:
    import copy

    valid = {
        "schemaVersion": "0.1", "modelVersion": "1.0.0",
        "evidenceModel": {
            "id": "urn:aocl:evidence:network-assurance-001", "type": "EvidenceModel",
            "name": "Network Service Assurance Evidence",
            "definition": "Verification of the traffic-redistribution intervention against the latency goal.",
            "closedLoopRef": {"loopId": "urn:aocl:loop:network-assurance-001", "sourceSystem": "AOCL"},
            "evidenceSources": [
                {"sourceId": "src-telemetry", "sourceType": "Telemetry", "systemRef": "network-telemetry",
                 "trust": "calibrated production telemetry"},
                {"sourceId": "src-controller", "sourceType": "Controller", "systemRef": "assurance-controller"},
                {"sourceId": "src-approval", "sourceType": "AuditMechanism", "systemRef": "policy-approval-service"},
                {"sourceId": "src-actuator", "sourceType": "Actuator", "systemRef": "actuator-traffic-engineering"},
                {"sourceId": "src-independent", "sourceType": "Sensor", "systemRef": "independent-probe",
                 "calibrationRef": "cal-2026-10"},
                {"sourceId": "src-capacity", "sourceType": "Telemetry", "systemRef": "resource-monitor"},
                {"sourceId": "src-sim", "sourceType": "SimulationEngine", "systemRef": "aocl-sim", "version": "1.0.0"},
            ],
            "evidence": [
                {"evidenceId": "E-01", "evidenceType": "ObservationEvidence", "name": "Initial latency 72 ms",
                 "sourceRef": "src-telemetry", "subjectRef": "network-service", "temporalRef": "t0",
                 "originClass": "OperationalTime", "contextRef": "production", "provenanceRef": "prov-t0",
                 "qualityRef": "q-obs", "integrityRef": "int-t0"},
                {"evidenceId": "E-02", "evidenceType": "DecisionEvidence", "name": "Redistribution selected",
                 "sourceRef": "src-controller", "subjectRef": "assurance-controller",
                 "originClass": "OperationalTime", "contextRef": "production", "provenanceRef": "prov-prod"},
                {"evidenceId": "E-03", "evidenceType": "AuthorizationEvidence", "name": "Intervention authorized",
                 "sourceRef": "src-approval", "subjectRef": "assurance-controller",
                 "originClass": "AuditTime", "provenanceRef": "prov-auth"},
                {"evidenceId": "E-04", "evidenceType": "CommandEvidence", "name": "Command issued",
                 "sourceRef": "src-actuator", "subjectRef": "actuator-traffic-engineering",
                 "originClass": "OperationalTime", "contextRef": "production", "temporalRef": "t1",
                 "provenanceRef": "prov-prod"},
                {"evidenceId": "E-05", "evidenceType": "ExecutionEvidence", "name": "Execution reported complete",
                 "sourceRef": "src-actuator", "subjectRef": "actuator-traffic-engineering",
                 "originClass": "OperationalTime", "contextRef": "production", "temporalRef": "t1", "provenanceRef": "prov-prod"},
                {"evidenceId": "E-06", "evidenceType": "StateEvidence", "name": "Allocation changed",
                 "sourceRef": "src-telemetry", "subjectRef": "network-service", "temporalRef": "t2",
                 "originClass": "OperationalTime", "contextRef": "production", "provenanceRef": "prov-prod"},
                {"evidenceId": "E-07", "evidenceType": "OutcomeEvidence", "name": "Latency returned to 43 ms",
                 "sourceRef": "src-independent", "subjectRef": "network-service", "temporalRef": "t3",
                 "originClass": "OperationalTime", "contextRef": "production", "provenanceRef": "prov-t3",
                 "qualityRef": "q-outcome"},
                {"evidenceId": "E-08", "evidenceType": "ConstraintEvidence", "name": "Capacity constraints satisfied",
                 "sourceRef": "src-capacity", "subjectRef": "network-service",
                 "originClass": "OperationalTime", "contextRef": "production", "provenanceRef": "prov-prod"},
                {"evidenceId": "E-09", "evidenceType": "ObservationEvidence", "name": "Second probe reports 61 ms",
                 "sourceRef": "src-telemetry", "subjectRef": "network-service", "temporalRef": "t3",
                 "originClass": "OperationalTime", "contextRef": "production", "provenanceRef": "prov-prod",
                 "claimRelationships": [{"claimRef": "c-latency-goal", "role": "Contradicts"}]},
                {"evidenceId": "E-10", "evidenceType": "ObservationEvidence", "name": "Stale post-intervention observation",
                 "sourceRef": "src-telemetry", "subjectRef": "network-service",
                 "temporalRef": "t3 minus 12 minutes (outside freshness window)",
                 "originClass": "OperationalTime", "contextRef": "production", "provenanceRef": "prov-prod",
                 "qualityRef": "q-stale"},
                {"evidenceId": "E-SIM-1", "evidenceType": "SimulationEvidence", "name": "Invariant suite run",
                 "sourceRef": "src-sim", "subjectRef": "aocl-sim", "originClass": "SimulationTime",
                 "simulationRun": {"runId": "seed-2026", "scenarioRef": "urn:aocl:scenario:baseline",
                                    "seed": 2026, "engineVersion": "1.0.0",
                                    "behavioralSpecVersion": "1.0.0", "controlContractVersion": "1.0.0"}},
            ],
            "provenance": [
                {"provenanceId": "prov-prod", "originSourceRef": "src-telemetry", "acquisitionTime": "2026-11-07T10:02:00Z",
                 "processingSteps": ["telemetry pipeline, immutable store"], "chainOfCustody": "production telemetry"},
                {"provenanceId": "prov-t0", "originSourceRef": "src-telemetry", "acquisitionTime": "2026-11-07T10:00:00Z",
                 "processingSteps": ["cycle aggregation"], "chainOfCustody": "telemetry pipeline, immutable store"},
                {"provenanceId": "prov-auth", "originSourceRef": "src-approval", "acquisitionTime": "2026-11-07T10:01:00Z"},
                {"provenanceId": "prov-t3", "originSourceRef": "src-independent", "acquisitionTime": "2026-11-07T10:05:00Z",
                 "processingSteps": ["none — direct measurement"], "humanIntervention": "none"},
            ],
            "qualityAssessments": [
                {"qualityId": "q-obs", "evidenceRef": "E-01",
                 "dimensions": {"validity": {"assessment": "Sufficient"}, "freshness": {"assessment": "Sufficient", "note": "within one cycle"}},
                 "freshnessRequirement": "within one control cycle"},
                {"qualityId": "q-outcome", "evidenceRef": "E-07",
                 "dimensions": {"validity": {"assessment": "Sufficient"}, "accuracy": {"assessment": "Sufficient"},
                                 "freshness": {"assessment": "Sufficient", "note": "within evaluation window"},
                                 "reliability": {"assessment": "Sufficient", "note": "calibrated independent probe"}},
                 "freshnessRequirement": "within the 5-minute evaluation interval"},
                {"qualityId": "q-stale", "evidenceRef": "E-10",
                 "dimensions": {"freshness": {"assessment": "Insufficient", "note": "acquired 12 min before use"}},
                 "freshnessRequirement": "within 5 minutes"},
            ],
            "integrity": [
                {"integrityId": "int-t0", "evidenceRef": "E-01", "mechanism": "ImmutableRecord",
                 "reference": "telemetry store", "status": "Intact"},
            ],
            "claims": [
                {"claimId": "c-authorized", "subject": "assurance-controller", "proposition": "the redistribution decision was authorized",
                 "claimType": "Authorization", "contractRef": "ctr-redistribute", "criticality": "Operational"},
                {"claimId": "c-command", "subject": "actuator-traffic-engineering", "proposition": "the redistribution command was issued",
                 "claimType": "Execution", "criticality": "Operational"},
                {"claimId": "c-transition", "subject": "network-service", "proposition": "the plant state changed to the redistributed allocation",
                 "claimType": "Transition", "transitionRef": "tr-degraded-recovering", "criticality": "Operational"},
                {"claimId": "c-latency-goal", "subject": "network-service", "proposition": "service latency returned below 50 ms within the evaluation interval",
                 "claimType": "Outcome", "goalRef": "goal-service-latency", "successCriterionRef": "crit-latency",
                 "assuranceRef": "ass-latency", "criticality": "Operational"},
                {"claimId": "c-capacity", "subject": "network-service", "proposition": "resource constraints remained satisfied",
                 "claimType": "Constraint", "invariantRef": "inv-utilization", "criticality": "Operational"},
                {"claimId": "c-sim-behavior", "subject": "aocl-sim", "proposition": "the modeled policy responds to the modeled disturbance per its specified logic",
                 "claimType": "Behavioral", "criticality": "Informational"},
                {"claimId": "c-learning", "subject": "learning-store", "proposition": "the remediation experience record is evidence-based",
                 "claimType": "Learning", "learningGovernanceRef": "pol-learning-auth", "criticality": "Informational"},
            ],
            "criteria": [
                {"criterionId": "crit-authority", "definition": "controller authority valid at decision time",
                 "subjectRef": "assurance-controller", "evidenceRequirements": "authorization record from the approval service"},
                {"criterionId": "crit-command", "definition": "command record exists", "subjectRef": "actuator-traffic-engineering"},
                {"criterionId": "crit-exec", "definition": "execution reported complete", "subjectRef": "actuator-traffic-engineering"},
                {"criterionId": "crit-state", "definition": "traffic allocation changed", "subjectRef": "network-service"},
                {"criterionId": "crit-latency", "definition": "p95 latency below 50 ms", "subjectRef": "network-service",
                 "expected": "< 50", "unit": "ms", "comparison": "lessThan", "tolerance": "0 ms",
                 "temporalRequirement": "within 5 minutes of intervention"},
                {"criterionId": "crit-capacity", "definition": "utilization within bounds", "subjectRef": "network-service"},
                {"criterionId": "crit-sim", "definition": "modeled response matches the specified logic", "subjectRef": "aocl-sim"},
                {"criterionId": "crit-learning", "definition": "learning record cites its evidence", "subjectRef": "learning-store"},
            ],
            "methods": [
                {"methodId": "m-contract", "category": "ContractConformance", "description": "authorization audit against the contract",
                 "assumptions": "approval service records are authentic", "version": "1.0"},
                {"methodId": "m-record", "category": "RuleBasedEvaluation", "description": "command record existence check"},
                {"methodId": "m-exec", "category": "RuleBasedEvaluation", "description": "execution status check"},
                {"methodId": "m-state", "category": "StateComparison", "description": "allocation before/after comparison"},
                {"methodId": "m-measure", "category": "DirectMeasurement", "description": "independent calibrated latency measurement",
                 "limitations": "single-probe measurement"},
                {"methodId": "m-sim", "category": "SimulationEvaluation", "description": "simulation invariant suite evaluation",
                 "assumptions": "modeled environment approximates production", "limitations": "not operational evidence"},
            ],
            "verifications": [
                {"verificationId": "v-authorized", "name": "Authorization verification", "verificationScope": "assurance-controller",
                 "verificationType": "Contract", "claimRefs": ["c-authorized"], "criterionRefs": ["crit-authority"],
                 "methodRefs": ["m-contract"], "evidenceRefs": ["E-02", "E-03"],
                 "independenceClass": "Supervisory", "verifierRef": "policy-approval-service", "temporalRef": "t1"},
                {"verificationId": "v-exec", "name": "Execution verification", "verificationScope": "actuator-traffic-engineering",
                 "verificationType": "Contract", "claimRefs": ["c-command"], "criterionRefs": ["crit-command"],
                 "methodRefs": ["m-record"], "evidenceRefs": ["E-04"],
                 "independenceClass": "Self", "verifierRef": "actuator-traffic-engineering"},
                {"verificationId": "v-transition", "name": "Transition verification", "verificationScope": "network-service",
                 "verificationType": "Transition", "claimRefs": ["c-transition"], "criterionRefs": ["crit-state"],
                 "methodRefs": ["m-state"], "evidenceRefs": ["E-06"],
                 "independenceClass": "Supervisory", "verifierRef": "resource-monitor",
                 "assumptionsAndLimitations": "telemetry-derived state comparison"},
                {"verificationId": "v-outcome", "name": "Latency goal verification", "verificationScope": "network-service",
                 "verificationType": "Outcome", "claimRefs": ["c-latency-goal"], "criterionRefs": ["crit-latency"],
                 "methodRefs": ["m-measure"], "evidenceRefs": ["E-07"],
                 "independenceClass": "Independent", "verifierRef": "independent-probe",
                 "independenceRequirementRef": "ass-latency", "temporalRef": "t3"},
                {"verificationId": "v-capacity", "name": "Constraint verification", "verificationScope": "network-service",
                 "verificationType": "Operational", "claimRefs": ["c-capacity"], "criterionRefs": ["crit-capacity"],
                 "methodRefs": ["m-state"], "evidenceRefs": ["E-08"],
                 "independenceClass": "Peer", "verifierRef": "resource-monitor"},
                {"verificationId": "v-learning", "name": "Learning record verification", "verificationScope": "learning-store",
                 "verificationType": "Behavioral", "claimRefs": ["c-learning"], "criterionRefs": ["crit-learning"],
                 "methodRefs": ["m-record"], "independenceClass": "Self", "verifierRef": "learning-store"},
                {"verificationId": "v-sim", "name": "Simulated policy response", "verificationScope": "aocl-sim",
                 "verificationType": "Model", "claimRefs": ["c-sim-behavior"], "criterionRefs": ["crit-sim"],
                 "methodRefs": ["m-sim"], "evidenceRefs": ["E-SIM-1"],
                 "independenceClass": "Self", "verifierRef": "aocl-sim",
                 "assumptionsAndLimitations": "modeled disturbances only; does not establish operational effectiveness (AD-008-11)"},
                {"verificationId": "v-fidelity", "name": "Cross-origin model fidelity", "verificationScope": "aocl-sim vs production",
                 "verificationType": "Operational", "claimRefs": ["c-latency-goal"], "criterionRefs": ["crit-latency"],
                 "methodRefs": ["m-sim", "m-measure"],
                 "independenceClass": "Independent", "verifierRef": "independent-probe"},
            ],
            "results": [
                {"resultId": "r-auth", "verificationRef": "v-authorized", "claimRef": "c-authorized",
                 "criterionRef": "crit-authority", "outcome": "Verified", "evidenceRefs": ["E-02", "E-03"],
                 "methodRef": "m-contract", "rationale": "authorization record present and valid", "evaluatedAt": "t1"},
                {"resultId": "r-command", "verificationRef": "v-exec", "claimRef": "c-command",
                 "criterionRef": "crit-command", "outcome": "Verified", "evidenceRefs": ["E-04"],
                 "methodRef": "m-record", "rationale": "command record exists", "evaluatedAt": "t1"},
                {"resultId": "r-transition", "verificationRef": "v-transition", "claimRef": "c-transition",
                 "criterionRef": "crit-state", "outcome": "Verified", "evidenceRefs": ["E-06"],
                 "methodRef": "m-state", "rationale": "observed allocation changed",
                 "invariantResults": ["inv-utilization held"], "evaluatedAt": "t2"},
                {"resultId": "r-latency", "verificationRef": "v-outcome", "claimRef": "c-latency-goal",
                 "criterionRef": "crit-latency", "outcome": "Verified", "evidenceRefs": ["E-07"],
                 "methodRef": "m-measure", "rationale": "independent measurement 43 ms within the window",
                 "evaluatedAt": "t3", "validFor": "evaluation interval"},
                {"resultId": "r-capacity", "verificationRef": "v-capacity", "claimRef": "c-capacity",
                 "criterionRef": "crit-capacity", "outcome": "Verified", "evidenceRefs": ["E-08"],
                 "methodRef": "m-state", "rationale": "utilization within bounds throughout", "evaluatedAt": "t3"},
                {"resultId": "r-learning", "verificationRef": "v-learning", "claimRef": "c-learning",
                 "criterionRef": "crit-learning", "outcome": "Deferred", "methodRef": "m-record",
                 "rationale": "learning record verification scheduled after the review cycle", "evaluatedAt": "t3"},
                {"resultId": "r-sim", "verificationRef": "v-sim", "claimRef": "c-sim-behavior",
                 "criterionRef": "crit-sim", "outcome": "Verified", "evidenceRefs": ["E-SIM-1"],
                 "methodRef": "m-sim", "rationale": "7/7 invariants hold at seed 2026 — model behaves per its logic",
                 "limitations": "simulation evidence only", "evaluatedAt": "t3"},
                {"resultId": "r-fidelity", "verificationRef": "v-fidelity", "claimRef": "c-latency-goal",
                 "criterionRef": "crit-latency", "outcome": "NotApplicable",
                 "evidenceRefs": ["E-SIM-1", "E-07"], "methodRef": "m-sim",
                 "rationale": "cross-origin fidelity comparison deferred until an operational interval pairs with a simulation run",
                 "limitations": "no paired run yet — applicability decision recorded", "evaluatedAt": "t3"},
            ],
            "findings": [],
            "dispositions": [],
            "conflicts": [],
            "assurances": [
                {"assuranceId": "ass-latency", "basis": "ServiceImpact", "description": "latency goal is service-critical",
                 "requiredIndependenceClass": "Independent", "governingRef": "urn:aocl:policy:assurance-latency"},
            ],
            "crossOriginComparisons": [],
        },
    }

    base = validate_evidence_model(copy.deepcopy(valid))
    assert base["valid"], base["findings"]
    conf = base["conformance"]
    assert all(conf[k] for k in conf if k not in ("fullyConformant", "reportedGaps")), conf
    # the §21 case matrix lives in the mutation set below

    def broken(mutator):
        d = copy.deepcopy(valid)
        mutator(d["evidenceModel"])
        return validate_evidence_model(d)

    rules_hit = {
        "VER-001": lambda m: m["evidence"].append(copy.deepcopy(m["evidence"][0])),
        "VER-002": lambda m: m["evidence"][0].__setitem__("evidenceType", "Vibes"),
        "VER-003": lambda m: m["evidence"][0].pop("sourceRef"),
        "VER-004": lambda m: m["evidence"][6].pop("temporalRef"),
        "VER-005": lambda m: m["evidence"][0].pop("subjectRef"),
        "VER-006": lambda m: m["evidence"][0].pop("provenanceRef"),
        "VER-007": lambda m: m["evidence"][0].__setitem__("derivedFromRefs", ["E-GHOST"]),
        "VER-008": lambda m: m["evidence"][0].__setitem__("originClass", "Sometimes"),
        "VER-010": lambda m: m["verifications"][0].pop("verificationScope"),
        "VER-011": lambda m: m["verifications"][0].__setitem__("claimRefs", []),
        "VER-012": lambda m: m["verifications"][0].__setitem__("criterionRefs", ["crit-ghost"]),
        "VER-013": lambda m: m["verifications"][0].__setitem__("methodRefs", ["m-ghost"]),
        "VER-014": lambda m: m["results"][0].__setitem__("evidenceRefs", []),
        "VER-015": lambda m: m["results"][0].__setitem__("outcome", "SortaTrue"),
        "VER-018": lambda m: m["results"][7].pop("limitations"),
        "VER-019": lambda m: m["evidence"][0].__setitem__("qualityRef", "q-ghost"),
        "VER-020": lambda m: m["results"][1].__setitem__("evidenceRefs", ["E-02"]),
        "VER-021": lambda m: m["evidence"][0].__setitem__("integrityRef", "int-ghost"),
        "VER-023": lambda m: m["results"][3].__setitem__("confidence", {"value": 0.9, "meaning": "model confidence", "scale": "0..1"}),
        "VER-025": lambda m: (m["evidence"][7].__setitem__("supersededBy", "E-09"),),
        "VER-026": lambda m: m["verifications"][0].__setitem__("independenceClass", "Sorta"),
        "VER-027": lambda m: m["claims"][3].__setitem__("assuranceRef", "ass-ghost"),
        "VER-028": lambda m: m["assurances"][0].pop("governingRef"),
        "VER-029": lambda m: m["verifications"][3].__setitem__("verifierRef", "network-service"),
        "VER-030": lambda m: (m["claims"][3].__setitem__("criticality", "Safety"), m["claims"][3].pop("assuranceRef")),
        "VER-031": lambda m: m["claims"][3].pop("goalRef"),
        "VER-034": lambda m: m["results"][2].__setitem__("evidenceRefs", ["E-05"]),
        "VER-036": lambda m: m["results"][3].__setitem__("evidenceRefs", ["E-05"]),
        "VER-038": lambda m: m["claims"][6].pop("learningGovernanceRef"),
        "VER-039": lambda m: m["evidence"][10]["simulationRun"].pop("runId"),
        "VER-040": lambda m: m["evidence"][10].__setitem__("originClass", "OperationalTime"),
        "VER-041": lambda m: m["evidence"][0].pop("contextRef"),
        "VER-043": lambda m: m["verifications"][6].pop("assumptionsAndLimitations"),
        "VER-045": lambda m: m["results"][0].__setitem__("methodRef", "m-ghost"),
        "VER-046": lambda m: m.pop("closedLoopRef"),
        "VER-050": lambda m: m["claims"][0].__setitem__("unresolved", True),
        "VER-016": lambda m: m["results"].append({**m["results"][3], "resultId": "r-fail2", "outcome": "Failed"}),
    }
    for rule, mutator in rules_hit.items():
        r = broken(mutator)
        assert any(f["rule"] == rule for f in r["findings"]), (rule, sorted({f["rule"] for f in r["findings"]}))

    # §21.4 failure case: execution Verified, outcome Failed — separate conclusions preserved
    def failure_case(m):
        m["evidence"].append({"evidenceId": "E-FAIL", "evidenceType": "ObservationEvidence",
                              "name": "latency 65 ms after execution", "sourceRef": "src-telemetry",
                              "subjectRef": "network-service", "temporalRef": "t3", "originClass": "OperationalTime",
                              "contextRef": "production", "provenanceRef": "prov-prod"})
        m["results"].append({"resultId": "r-fail", "verificationRef": "v-outcome", "claimRef": "c-latency-goal",
                             "criterionRef": "crit-latency", "outcome": "Failed", "evidenceRefs": ["E-FAIL"],
                             "methodRef": "m-measure", "rationale": "execution verified but goal failed — preserved separately",
                             "evaluatedAt": "t3"})
        m["findings"].append({"findingId": "f-outcome", "description": "remediation did not achieve the latency goal",
                              "severity": "Major", "resultRef": "r-fail"})
    d = copy.deepcopy(valid)
    failure_case(d["evidenceModel"])
    r = validate_evidence_model(d)
    outcomes = {(x["claimRef"], x["outcome"]) for x in d["evidenceModel"]["results"]}
    assert ("c-command", "Verified") in outcomes and ("c-latency-goal", "Failed") in outcomes
    assert r["valid"], r["findings"]

    # §21.5 inconclusive case: favorable value, stale observation → Inconclusive, not Verified
    def inconclusive_case(m):
        m["results"].append({"resultId": "r-stale", "verificationRef": "v-outcome", "claimRef": "c-latency-goal",
                             "criterionRef": "crit-latency", "outcome": "Inconclusive", "evidenceRefs": ["E-10"],
                             "methodRef": "m-measure", "rationale": "favorable value but stale observation",
                             "limitations": "observation outside the freshness window", "evaluatedAt": "t3"})
    d = copy.deepcopy(valid)
    inconclusive_case(d["evidenceModel"])
    r = validate_evidence_model(d)
    assert any(x["outcome"] == "Inconclusive" for x in d["evidenceModel"]["results"])

    # §21.6 conflicting case: conflict preserved, result Conflicting, resolved by neither
    def conflict_case(m):
        m["results"].append({"resultId": "r-conf", "verificationRef": "v-outcome", "claimRef": "c-latency-goal",
                             "criterionRef": "crit-latency", "outcome": "Conflicting",
                             "evidenceRefs": ["E-07", "E-09"], "methodRef": "m-measure",
                             "rationale": "43 ms vs 61 ms over the same interval — preserved", "evaluatedAt": "t3"})
        m["conflicts"].append({"conflictId": "conf-1", "evidenceRefs": ["E-07", "E-09"],
                               "description": "independent probe vs telemetry disagree",
                               "resolutionMethod": "source-quality comparison pending", "unresolved": True})
        m["findings"].append({"findingId": "f-conf", "description": "evidence conflict on the latency goal",
                              "severity": "Major", "resultRef": "r-conf", "evidenceRefs": ["E-07", "E-09"]})
    d = copy.deepcopy(valid)
    conflict_case(d["evidenceModel"])
    r = validate_evidence_model(d)
    assert any(x["outcome"] == "Conflicting" for x in d["evidenceModel"]["results"])
    assert r["valid"], r["findings"]

    # VER-017: dispositions preserve results; waivers carry authority
    def disposition_case(m):
        m["results"].append({**m["results"][0], "resultId": "r-na", "outcome": "NotApplicable",
                             "rationale": "criterion does not apply in this context",
                             "limitations": "applicability reviewed by governance"})
    r = broken(disposition_case)
    assert r["valid"], r["findings"]
    r = broken(lambda m: m["dispositions"].append({"dispositionId": "d1", "targetRef": "r-latency",
                                                    "disposition": "Waive"}))
    assert any(f["rule"] == "VER-017" for f in r["findings"])

    # VER-024: conflicting result without a preserved conflict record
    r = broken(lambda m: m["results"].append({**m["results"][3], "resultId": "r-conf2", "outcome": "Conflicting",
                                              "rationale": "x"}))
    assert any(f["rule"] == "VER-024" for f in r["findings"])

    # migration: claims carried, scores NOT imported, nothing fabricated
    ctrl = {"schemaVersion": "0.1", "modelVersion": "1.0.0",
            "controlModel": {"id": "urn:aocl:control:net-1", "type": "ControlModel", "name": "n", "definition": "d",
                             "closedLoopRef": {"loopId": "urn:aocl:loop:net-1", "sourceSystem": "s"},
                             "controlVariables": [], "contracts": [], "authority": [],
                             "verificationRefs": [{"verificationRef": "vr-safe-mode", "claim": "safe-mode conditions hold"}]}}
    mig = migrate_from_control_model(ctrl)
    em = mig["spec"]["evidenceModel"]
    assert em["claims"][0]["proposition"] == "safe-mode conditions hold" and em["claims"][0]["unresolved"]
    assert not em.get("evidence")  # no fabricated evidence
    assert any("NOT imported" in u for u in em["migrationNotes"]["unresolvedMappings"])
    assert any("not converted" in f["message"] for f in mig["findings"])

    # round-trip serialization (VER-048)
    assert json.loads(json.dumps(valid)) == valid
    print(f"self-test OK (evidence model v{RULESET_VERSION}, schema {SCHEMA_VERSION}, VER-001..050 + migration)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
