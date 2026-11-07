> **Status:** Proposed · **Queued:** 2026-11-07 — verification and evidence — Evidence as first-class, claim/criterion/method/result chains, independence classes, simulation vs operational evidence separation (VER-001..050) · Carries forward the review's pre-approval observations (kept in-document as review checks).

---

# AOCL-CR-008 — Establish the Canonical Verification and Evidence Model

**CR ID:** AOCL-CR-008\
**Title:** Establish the Canonical Verification and Evidence Model\
**Programme:** AOCL Conceptual and Modeling Foundation\
**Status:** Proposed\
**Priority:** Critical\
**Type:** Metamodel and Normative Semantics\
**Depends on:** AOCL-CR-001, AOCL-CR-002, AOCL-CR-003, AOCL-CR-004, AOCL-CR-005, AOCL-CR-006, AOCL-CR-007

---

## 1. Executive Summary

This Change Request establishes the canonical verification and evidence model for AOCL.

A closed-loop engineering framework must establish more than whether a decision was made or an action was executed. It must determine whether the controlled system changed as expected, whether the intended operational outcome was achieved, and whether sufficient trustworthy evidence exists to support those conclusions.

The preceding CRs establish:

- The canonical closed-loop model.
- The seven-stage behavioral lifecycle.
- The structural control architecture.
- Relationships, constraints and loop composition.
- Behavioral specification.
- Control contracts and state-transition semantics.

CR-008 establishes the evidence and verification foundation that connects these models to demonstrable results.

It introduces:

1. A canonical Evidence model.
2. An explicit Verification model.
3. Verification criteria and claims.
4. Evidence provenance, quality and integrity.
5. Evidence-to-claim traceability.
6. Independent verification and assurance semantics.
7. Verification of actions, transitions, outcomes and goals.
8. Evidence aggregation and confidence handling.
9. Verification findings and dispositions.
10. Simulation evidence and operational evidence distinctions.

The model SHALL support verification throughout the lifecycle, including design-time validation, simulation, testing, controlled deployment and operational monitoring.

It SHALL also preserve the distinction between evidence that demonstrates model conformance, evidence that demonstrates simulated behavior, and evidence that demonstrates real operational performance.

## 2. Problem Statement

AOCL is intended to support the specification, assessment, modeling, simulation, verification and preparation of closed loops for operational realization.

This requires a defensible way to establish whether a loop behaves correctly and whether its intended outcomes are achieved.

Several situations illustrate the problem:

| Situation                                | What is known                      | What remains unproven                                           |
| ---------------------------------------- | ---------------------------------- | --------------------------------------------------------------- |
| A Controller selects an action           | A decision was made                | Whether it was valid or authorized                              |
| An actuator acknowledges a command       | A command was received or accepted | Whether the Plant changed state                                 |
| An actuator reports successful execution | The actuator reports completion    | Whether the intended operational effect occurred                |
| A Sensor reports a target value          | A measurement was acquired         | Whether the measurement is accurate, current and representative |
| A Plant changes state                    | A transition occurred              | Whether the resulting state satisfies the intended outcome      |
| A simulation completes successfully      | A modeled scenario executed        | Whether the real operating environment will behave identically  |
| A KPI improves                           | A measured value changed           | Whether the intervention caused the improvement                 |

AOCL must therefore distinguish the event, claim and evidence associated with each verification decision.

A verification result must be explainable:

- What was being verified?
- Against which requirement, goal, contract or invariant?
- What evidence was used?
- Where did that evidence originate?
- Was it valid and sufficiently current?
- Was the evidence independent of the mechanism being evaluated?
- What verification method was applied?
- What conclusion was reached?
- What uncertainty remains?

Without these distinctions, maturity assessments, simulation results and operational claims risk being based on weak or incorrectly interpreted evidence.

## 3. Objectives

This CR SHALL:

1. Establish Evidence as a first-class model concept.
2. Establish Verification as a governed activity and result.
3. Define VerificationClaim and VerificationCriterion.
4. Define evidence provenance and integrity.
5. Distinguish evidence types and evidential strength.
6. Define evidence quality and applicability.
7. Support independent and non-independent verification.
8. Establish explicit verification outcomes.
9. Support verification at multiple levels of the closed-loop model.
10. Define evidence aggregation and conflict handling.
11. Establish traceability from Intent and Goals to verification results.
12. Support simulation, testing and operational evidence without conflating them.
13. Provide a foundation for evidence-backed assessment and realization decisions.

## 4. Scope

### 4.1 In scope

- Evidence.
- EvidenceSource.
- EvidenceRecord.
- EvidenceProvenance.
- EvidenceType.
- EvidenceQuality.
- EvidenceIntegrity.
- Verification.
- VerificationClaim.
- VerificationCriterion.
- VerificationMethod.
- VerificationResult.
- VerificationFinding.
- VerificationDisposition.
- Evidence-to-claim relationships.
- Evidence validity and freshness.
- Confidence and uncertainty.
- Independence and assurance.
- Evidence aggregation and conflicting evidence.
- Goal, outcome, transition and contract verification.
- Simulation and operational evidence classification.
- Evidence traceability and retention requirements at the model level.

### 4.2 Out of scope

| Concern                                                            | Owning CR                                                        |
| ------------------------------------------------------------------ | ---------------------------------------------------------------- |
| Control variables, state transitions and control contracts         | AOCL-CR-007                                                      |
| Scenario definitions and disturbance models                        | AOCL-CR-009                                                      |
| Runtime execution and evidence collection orchestration            | AOCL-CR-010                                                      |
| Logical simulation engine                                          | AOCL-CR-011                                                      |
| State-based simulation engine                                      | AOCL-CR-012                                                      |
| Simulation trace and replay                                        | AOCL-CR-013                                                      |
| Detailed operational evidence storage and telemetry infrastructure | Implementation and integration specifications                    |
| Existing maturity scoring rules                                    | Existing assessment model, subject to a separate governed change |

CR-008 defines evidence and verification semantics. It does not prescribe a particular observability platform, database, telemetry pipeline or verification engine.

## 5. Normative Design Principles

### P01 — Evidence-Based Claims

Every verified claim SHALL be supported by identifiable evidence or an explicitly declared verification method that establishes the claim.

### P02 — Claim Specificity

Evidence SHALL be evaluated against a defined claim or criterion. Evidence SHALL NOT be treated as universally applicable.

### P03 — Provenance Integrity

Evidence SHALL retain its source, acquisition context, temporal reference and transformation history where applicable.

### P04 — Evidential Distinction

Command acknowledgement, actuator execution, observed state, verified transition and goal achievement SHALL remain distinct evidence categories.

### P05 — Quality Awareness

Evidence SHALL be evaluated for validity, freshness, completeness, reliability and relevance.

### P06 — Independent Verification

Where independence is required, evidence or verification SHALL be sufficiently independent of the mechanism or component whose behavior is being evaluated.

### P07 — Uncertainty Transparency

Insufficient, ambiguous, conflicting or uncertain evidence SHALL NOT be silently converted into a positive verification result.

### P08 — Traceable Conclusions

Every verification result SHALL be traceable to the claim, criterion, method and evidence supporting it.

### P09 — Contextual Applicability

Evidence SHALL be evaluated within its applicable operating context, time interval, model version and scope.

### P10 — Reproducibility

Verification results SHALL preserve enough information to explain and, where feasible, reproduce the verification decision.

### P11 — Controlled Assurance

The strength of a verification conclusion SHALL be appropriate to the criticality of the claim and the quality of available evidence.

### P12 — Separation of Evidence and Assessment

Evidence is an input to assessment. Evidence SHALL NOT be conflated with maturity scores, realization scores or performance indicators.

## 6. Canonical Evidence Model

### 6.1 Evidence

An `Evidence` represents an identifiable information artifact or recorded result that supports, contradicts or qualifies a claim about a closed loop, its behavior, a state transition or an operational outcome.

Evidence may be generated by:

- Sensors.
- Observability systems.
- Controllers.
- Actuators.
- External systems.
- Human observations.
- Tests.
- Simulations.
- Analytical models.
- Audits.
- Independent verification processes.

Proposed attributes:

| Attribute            | Description                                 |
| -------------------- | ------------------------------------------- |
| evidenceId           | Stable identifier                           |
| evidenceType         | Governed evidence classification            |
| name                 | Human-readable name                         |
| description          | What the evidence represents                |
| sourceRef            | Originating source                          |
| subjectRef           | Subject to which evidence relates           |
| claimRefs            | Claims supported, contradicted or qualified |
| temporalReference    | Time or interval represented                |
| acquisitionMethod    | How evidence was obtained                   |
| provenanceRef        | Evidence provenance record                  |
| qualityAssessmentRef | Evidence quality assessment                 |
| integrityStatus      | Integrity disposition                       |
| contextRef           | Applicable operating or simulation context  |
| modelVersionRef      | Model version relevant to the evidence      |
| lifecycleStatus      | Evidence lifecycle state                    |

Evidence SHALL be independently identifiable and SHALL retain its source context.

### 6.2 EvidenceSource

An `EvidenceSource` represents the origin or producing mechanism of evidence.

Examples include:

- Sensor.
- Plant telemetry interface.
- Controller.
- Actuator.
- Event stream.
- External information system.
- Simulation engine.
- Test harness.
- Human verifier.
- Audit mechanism.

An EvidenceSource SHALL identify its source type and relevant identity.

Where applicable, it SHOULD identify:

- Source system.
- Source component.
- Source version.
- Source authority.
- Acquisition interface.
- Calibration or validation reference.
- Trust classification.

A source's existence does not automatically establish the quality or validity of its evidence.

### 6.3 EvidenceRecord

An `EvidenceRecord` represents a particular recorded evidence instance.

It may contain:

- Measured values.
- State observations.
- Execution events.
- Verification results.
- Test results.
- Simulation observations.
- Audit records.
- Human attestations.
- Analytical outputs.

EvidenceRecord is a record-level representation. It SHALL NOT be treated as equivalent to the semantic definition of Evidence.

### 6.4 EvidenceProvenance

An `EvidenceProvenance` represents the origin, derivation and transformation history of evidence.

It SHALL capture, where applicable:

- Originating source.
- Acquisition method.
- Acquisition timestamp.
- Source identity.
- Processing or transformation steps.
- Derived evidence references.
- Model or algorithm version.
- Human intervention.
- Integrity or signature references.
- Chain of custody.

Derived evidence SHALL retain traceability to its source evidence.

Evidence transformations SHALL NOT silently remove material provenance information.

## 7. Evidence Classification

### 7.1 Canonical evidence types

AOCL SHALL support the following evidence categories.

| Evidence type         | Definition                                              | Example                            |
| --------------------- | ------------------------------------------------------- | ---------------------------------- |
| ObservationEvidence   | Evidence acquired about a Plant or environment          | Latency measurement                |
| StateEvidence         | Evidence representing an established or estimated state | Network operating mode             |
| DecisionEvidence      | Evidence of a decision and its governing rationale      | Selected remediation action        |
| AuthorizationEvidence | Evidence that an action was authorized                  | Approval record                    |
| CommandEvidence       | Evidence that a command was issued or received          | API command record                 |
| ExecutionEvidence     | Evidence of actuator or execution behavior              | Actuator completion event          |
| TransitionEvidence    | Evidence that a state transition occurred               | Observed traffic allocation change |
| OutcomeEvidence       | Evidence that an operational outcome was achieved       | Verified latency below threshold   |
| ConstraintEvidence    | Evidence of constraint satisfaction or violation        | Resource utilization within limit  |
| SafetyEvidence        | Evidence relevant to safety conditions and controls     | Interlock activation               |
| TestEvidence          | Evidence generated through a test                       | Contract conformance test          |
| SimulationEvidence    | Evidence generated by a simulation run                  | Simulated response trace           |
| AuditEvidence         | Evidence generated by an audit or assurance activity    | Control authorization audit        |
| HumanAttestation      | A governed human confirmation or assessment             | Supervisor approval                |

These categories are not necessarily mutually exclusive. A record MAY be classified under multiple types where its distinct evidential roles are explicitly identified.

### 7.2 Evidence origin

Evidence SHALL also identify its origin class.

| Origin class    | Description                                     |
| --------------- | ----------------------------------------------- |
| DesignTime      | Generated during model design or validation     |
| TestTime        | Generated during controlled testing             |
| SimulationTime  | Generated during simulation                     |
| DeploymentTime  | Generated during deployment or commissioning    |
| OperationalTime | Generated by the real operating environment     |
| AuditTime       | Generated through an assurance or audit process |

Origin classification SHALL remain distinct from evidence type.

For example, a StateEvidence record may originate from a simulation or from an operational Sensor.

### 7.3 Evidence strength

Evidence strength SHALL be evaluated in relation to the claim being assessed.

AOCL SHALL NOT establish a universal ranking in which one evidence type is always stronger than another.

For example:

- A command record may be strong evidence that a command was issued.
- The same record is weak evidence that the Plant changed state.
- A direct, calibrated measurement may be strong evidence of a measured variable.
- The same measurement may be insufficient to establish that a particular Controller caused the measured change.

Evidence strength is therefore claim-dependent.

## 8. Verification Model

### 8.1 Verification

A `Verification` represents a governed evaluation of one or more claims against defined criteria using identifiable evidence and verification methods.

Proposed attributes:

| Attribute         | Description                                    |
| ----------------- | ---------------------------------------------- |
| verificationId    | Stable identifier                              |
| name              | Verification name                              |
| verificationScope | Subject or scope being verified                |
| verificationType  | Governed verification classification           |
| claimRefs         | Claims being evaluated                         |
| criterionRefs     | Applicable criteria                            |
| methodRefs        | Verification methods                           |
| evidenceRefs      | Evidence considered                            |
| resultRef         | Result of verification                         |
| verifierRef       | Responsible verifier or verification mechanism |
| independenceClass | Independence classification                    |
| temporalReference | Verification time or interval                  |
| contextRef        | Applicable context                             |
| modelVersionRef   | Model version evaluated                        |
| lifecycleStatus   | Verification lifecycle state                   |

Verification SHALL be traceable to its scope, claims, criteria and evidence.

### 8.2 VerificationClaim

A `VerificationClaim` expresses a proposition that AOCL intends to establish, reject or qualify through verification.

Examples:

- The Controller acted within its authorized scope.
- The actuator executed the requested command.
- The Plant transitioned from Degraded to Recovering.
- Service latency returned below the agreed threshold.
- A safety invariant remained satisfied.
- The closed loop achieved its stated operational objective.

A claim SHALL identify:

- Claim subject.
- Proposition or condition.
- Applicable context.
- Relevant temporal scope.
- Claim type.
- Related Intent, Goal, Contract, Transition or Constraint.
- Required assurance level, where applicable.

Claims SHALL be specific enough to determine what evidence is relevant.

### 8.3 VerificationCriterion

A `VerificationCriterion` defines the condition against which a claim is evaluated.

A criterion SHALL include, where applicable:

- Criterion identity.
- Criterion definition.
- Evaluation subject.
- Expected value or condition.
- Comparison semantics.
- Unit and tolerance.
- Operating context.
- Temporal requirements.
- Evidence requirements.
- Applicable constraints.
- Acceptance condition.

Criteria may be:

- Quantitative.
- Qualitative.
- Boolean.
- Temporal.
- Relational.
- Statistical.
- Composite.

A criterion SHALL NOT be considered satisfied solely because a related KPI improved.

### 8.4 VerificationMethod

A `VerificationMethod` defines how evidence is evaluated against a criterion.

Supported method categories SHOULD include:

- Direct measurement.
- State comparison.
- Threshold evaluation.
- Temporal evaluation.
- Statistical evaluation.
- Rule-based evaluation.
- Contract conformance.
- Invariant checking.
- Test execution.
- Simulation evaluation.
- Human inspection.
- Independent audit.
- Model-based verification.

A method SHALL identify its assumptions and applicable limitations.

The method's version or implementation identity SHOULD be retained when material to reproducibility.

## 9. Verification Levels

AOCL SHALL support verification at multiple levels.

### 9.1 Model Verification

Establishes whether the model is structurally and semantically valid.

Examples:

- Required model elements are present.
- Relationships are valid.
- Constraints are correctly referenced.
- Behavioral specifications are structurally complete.
- Control contracts are well formed.

Model verification does not establish that a real loop operates correctly.

### 9.2 Behavioral Verification

Establishes whether specified behavior conforms to the declared behavioral model.

Examples:

- A required behavioral stage is represented.
- Branch conditions are defined.
- Exception paths are handled.
- Required transitions are represented.
- Decision and action contracts are respected.

### 9.3 Contract Verification

Establishes whether decisions and interventions satisfy their declared contracts.

Examples:

- Preconditions were satisfied.
- Authority was valid.
- The action remained within its permitted scope.
- Postconditions were evaluated.

### 9.4 Transition Verification

Establishes whether a modeled state transition occurred and whether its resulting state satisfies the transition requirements.

Examples:

- The Plant moved into the expected operating mode.
- A controlled variable reached its target range.
- Applicable invariants remained satisfied.

### 9.5 Outcome Verification

Establishes whether the operational outcome defined by Intent and Goals was achieved.

Examples:

- Service latency remained within the agreed threshold.
- Availability requirements were satisfied.
- A defined operational capability was realized.

### 9.6 Operational Verification

Establishes whether a loop demonstrates the required behavior in its real operating environment.

It may include:

- Operational telemetry.
- Incident records.
- Service measurements.
- Independent tests.
- Operational audit evidence.
- Human attestations.

Operational verification SHALL distinguish observed correlation from demonstrated causal attribution.

## 10. Verification Result Model

### 10.1 VerificationResult

A `VerificationResult` represents the conclusion of a verification activity.

Proposed attributes:

| Attribute       | Description                                 |
| --------------- | ------------------------------------------- |
| resultId        | Stable identifier                           |
| verificationRef | Verification activity                       |
| claimRef        | Claim evaluated                             |
| criterionRef    | Criterion applied                           |
| outcome         | Governed result                             |
| evidenceRefs    | Evidence considered                         |
| methodRef       | Method applied                              |
| confidence      | Confidence or uncertainty, where meaningful |
| limitations     | Known limitations                           |
| rationale       | Explanation of conclusion                   |
| evaluatedAt     | Evaluation timestamp                        |
| validFor        | Applicable validity period or context       |

### 10.2 Canonical outcomes

AOCL SHALL support the following outcomes:

| Outcome       | Meaning                                                                |
| ------------- | ---------------------------------------------------------------------- |
| Verified      | The claim is sufficiently established against the applicable criterion |
| NotVerified   | The claim is not sufficiently established                              |
| Failed        | Evidence demonstrates that the criterion was not satisfied             |
| Inconclusive  | Evidence is insufficient or ambiguous                                  |
| Conflicting   | Relevant evidence supports materially incompatible conclusions         |
| NotApplicable | The criterion does not apply in the declared context                   |
| Deferred      | Verification has not yet been completed                                |
| Invalid       | The verification activity or evidence is invalid for the claim         |

These outcomes SHALL be distinct.

In particular:

- NotVerified does not necessarily mean Failed.
- Inconclusive does not mean success.
- NotApplicable requires a justified applicability decision.
- Deferred does not represent a positive result.
- Invalid means the verification basis cannot be relied upon.

### 10.3 VerificationFinding

A `VerificationFinding` records an identified condition arising from verification.

Examples include:

- Missing evidence.
- Constraint violation.
- Stale observation.
- Unauthorized action.
- Unexpected state transition.
- Inconsistent evidence.
- Unverified outcome.
- Failure to preserve an invariant.

A finding SHALL identify its severity or priority using a governed classification.

Findings SHOULD reference corrective, investigative or escalation actions where applicable.

### 10.4 VerificationDisposition

A `VerificationDisposition` defines the treatment of a verification result or finding.

Possible dispositions include:

- Accept.
- Reject.
- Escalate.
- Investigate.
- Reverify.
- Remediate.
- Waive with authorization.
- Defer.

A disposition SHALL NOT overwrite the original verification result.

A waiver SHALL retain its authorizing authority, justification, scope and validity.

## 11. Evidence Quality and Integrity

### 11.1 EvidenceQuality

Evidence quality describes how suitable evidence is for a particular verification purpose.

AOCL SHALL support the following quality dimensions:

| Dimension    | Meaning                                                              |
| ------------ | -------------------------------------------------------------------- |
| Validity     | Whether evidence measures or represents the intended subject         |
| Accuracy     | How closely the evidence represents the actual value or condition    |
| Freshness    | Whether evidence is sufficiently current                             |
| Completeness | Whether required information is present                              |
| Reliability  | Whether the source and acquisition process are dependable            |
| Relevance    | Whether evidence is applicable to the claim                          |
| Consistency  | Whether evidence agrees with other relevant evidence                 |
| Resolution   | Whether evidence has sufficient precision or granularity             |
| Traceability | Whether evidence can be traced to its source                         |
| Integrity    | Whether evidence has remained protected from unauthorized alteration |

Not every dimension is applicable to every evidence type.

Quality assessments SHALL be context-specific. AOCL SHALL not assume that one numeric quality score can adequately represent all dimensions.

### 11.2 EvidenceIntegrity

Evidence integrity concerns whether the evidence can be relied upon as an authentic and unaltered record.

It MAY include:

- Digital signatures.
- Cryptographic hashes.
- Source authentication.
- Access and modification history.
- Chain-of-custody records.
- Immutable event records.
- Trusted timestamping.

The implementation may use different integrity mechanisms, but the canonical model SHALL preserve the integrity claim and supporting references.

### 11.3 Evidence freshness

Evidence freshness SHALL be evaluated against the temporal requirements of the claim.

For example, a latency observation acquired several minutes earlier may be unsuitable for authorizing a time-sensitive network intervention.

Evidence SHALL support:

- Acquisition time.
- Relevant time interval.
- Validity period, where defined.
- Expiration or staleness condition.
- Temporal alignment with related evidence.

Freshness SHALL not be assumed merely because an evidence record was recently ingested. Acquisition time and ingestion time are distinct.

### 11.4 Evidence confidence and uncertainty

Where evidence is estimated, inferred, sampled or otherwise uncertain, the model SHALL preserve relevant uncertainty information.

Confidence SHALL be interpreted in relation to the method and evidence source.

AOCL SHALL NOT require all evidence to have a numeric confidence score.

Where a numeric confidence is used, the model SHALL identify:

- Its meaning.
- Its scale.
- Its derivation method.
- Its applicable assumptions.
- Whether it represents probability, statistical confidence, model confidence or another measure.

Confidence values from incompatible methods SHALL NOT be aggregated without an explicit, justified transformation.

## 12. Independence and Assurance

### 12.1 Verification independence

Verification independence describes the relationship between the verifier, evidence source and subject being evaluated.

AOCL SHALL support the following classifications:

| Classification          | Meaning                                                                        |
| ----------------------- | ------------------------------------------------------------------------------ |
| SelfVerification        | The component or mechanism evaluates its own behavior                          |
| PeerVerification        | A separate peer component evaluates the subject                                |
| SupervisoryVerification | A supervisory mechanism evaluates the subject                                  |
| IndependentVerification | Verification is performed by a sufficiently independent mechanism or authority |
| ExternalAssurance       | Verification is performed by an external assurance authority or party          |

These classifications do not automatically determine whether verification is adequate.

Adequacy depends on the criticality of the claim, applicable governance requirements and the independence needed to establish it.

### 12.2 Independence requirements

Where independent verification is required, the model SHALL specify:

- Required independence level.
- Subject from which independence is required.
- Evidence-source restrictions.
- Verification authority.
- Applicable governance basis.

A Controller SHALL NOT be treated as an independent verifier of its own success merely because it receives an acknowledgement from its Actuator.

### 12.3 Assurance level

An `AssuranceRequirement` defines the degree of confidence or independence required to accept a claim.

It MAY be based on:

- Operational criticality.
- Safety implications.
- Regulatory obligations.
- Financial exposure.
- Service impact.
- Reversibility of the intervention.
- Risk of an incorrect verification conclusion.

AOCL SHALL support assurance requirements without imposing a universal risk classification or numerical assurance scale.

## 13. Evidence Relationships and Aggregation

### 13.1 Evidence-to-claim relationships

Evidence SHALL be explicitly associated with claims.

The relationship SHALL identify its evidential role:

- Supports.
- Contradicts.
- Qualifies.
- Contextualizes.
- Supersedes.
- DerivedFrom.

A single evidence record MAY relate to multiple claims, provided the relationship and applicability are explicit.

### 13.2 Evidence aggregation

A Verification MAY use multiple evidence records.

Aggregation MAY include:

- Multiple measurements.
- Measurements over a defined interval.
- Independent observations.
- Correlated observations.
- Derived evidence.
- Human and automated evidence.
- Simulation and test evidence.

The aggregation method SHALL be declared.

Where evidence is correlated, the verification process SHALL avoid treating repeated observations of the same underlying source as independent confirmation.

### 13.3 Conflicting evidence

Where relevant evidence conflicts, AOCL SHALL preserve the conflict.

The model SHALL support:

- Identifying conflicting records.
- Comparing provenance and quality.
- Establishing temporal relevance.
- Identifying incompatible measurement methods.
- Recording the resolution method.
- Recording unresolved uncertainty.

A conflict SHALL NOT be silently resolved by selecting the most favorable evidence.

### 13.4 Evidence supersession

Evidence may become obsolete or be superseded by newer or corrected evidence.

Supersession SHALL preserve the original record and the reason for supersession.

A new record SHALL NOT silently overwrite the historical evidence supporting an earlier verification result.

## 14. Verification of Closed-Loop Behavior

### 14.1 Intent and Goal verification

AOCL SHALL support verification of whether declared Goals and their associated success criteria have been achieved.

Goal verification SHALL reference:

- The Goal.
- Its success criteria.
- Relevant ReferenceConditions.
- Applicable Constraints.
- The evidence used.
- The verification method.
- The verification result.

Goal achievement SHALL NOT be inferred solely from the success of individual behavioral stages.

### 14.2 Behavioral stage verification

The seven canonical behavioral stages SHALL be verifiable where applicable.

| Stage   | Verification focus                                                         |
| ------- | -------------------------------------------------------------------------- |
| Intent  | Intent and constraints are represented and traceable                       |
| Observe | Required observations are acquired with appropriate provenance and quality |
| Analyze | Analysis is based on valid and applicable information                      |
| Decide  | Decision satisfies applicable policy, contract and authority               |
| Execute | Authorized action is executed within the permitted scope                   |
| Verify  | Resulting state and outcome are evaluated against criteria                 |
| Learn   | Learning records are evidence-based and governed                           |

A behavioral stage being present in a specification does not establish that it was successfully realized in operation.

### 14.3 Control contract verification

Verification SHALL establish whether:

- Preconditions were satisfied.
- Authorization was valid.
- The action remained within its permitted scope.
- Applicable constraints were respected.
- Expected effects were evaluated.
- Postconditions were established.

A contract may be structurally conformant while an individual execution fails its conditions.

### 14.4 State-transition verification

Transition verification SHALL establish:

- The source-state condition.
- The transition trigger.
- The relevant intervention or disturbance.
- The target-state condition.
- The evidence supporting the transition.
- Applicable invariant results.
- Any unresolved transition uncertainty.

Transition verification SHALL distinguish an intended transition from an observed or established transition.

### 14.5 Outcome verification

Outcome verification SHALL establish whether the resulting operational condition satisfies the relevant Goal and success criteria.

It SHALL consider:

- The intended outcome.
- Actual or established state.
- Measurement and observation quality.
- Applicable temporal conditions.
- Constraints and invariants.
- Evidence provenance.
- Required assurance level.

A successful action SHALL NOT automatically result in a verified outcome.

## 15. Simulation, Test and Operational Evidence

### 15.1 Evidence origin separation

AOCL SHALL preserve the distinction between:

- Model-validation evidence.
- Test evidence.
- Simulation evidence.
- Deployment evidence.
- Operational evidence.
- Independent assurance evidence.

Evidence from one origin class SHALL NOT silently be substituted for another.

### 15.2 SimulationEvidence

SimulationEvidence is generated by executing a model under a defined simulation scenario.

It MAY establish:

- Whether the model behaves according to its specified logic.
- Whether expected state transitions occur in the simulated environment.
- Whether a control policy responds to modeled disturbances.
- Whether constraints are violated under a scenario.
- Whether modeled failure paths are handled.
- Whether the simulated loop exhibits oscillation, instability or undesirable behavior.

SimulationEvidence SHALL reference:

- Model version.
- Behavioral specification version.
- Control-contract version.
- Scenario version.
- Simulation configuration.
- Engine and engine version.
- Initial conditions.
- Random seed, where applicable.
- Run identity.
- Relevant trace or result records.

SimulationEvidence SHALL NOT automatically establish real-world operational effectiveness.

### 15.3 OperationalEvidence

OperationalEvidence is acquired from a real operating environment.

It MAY establish:

- Actual system behavior.
- Measured operational outcomes.
- Intervention effectiveness.
- Service performance.
- Constraint satisfaction.
- Operational stability over a defined interval.

OperationalEvidence SHALL retain sufficient context to distinguish the real operating environment from a simulated or test environment.

### 15.4 Cross-origin verification

AOCL MAY compare evidence from different origins.

For example, simulation results may be compared with operational measurements to evaluate model fidelity.

Such comparisons SHALL identify:

- The compared model and operating contexts.
- Relevant temporal intervals.
- Variable mappings.
- Differences in assumptions.
- Known limitations.
- The conclusion supported by the comparison.

Simulation and operational evidence SHALL remain separately identifiable.

## 16. Evidence Traceability

AOCL SHALL support a traceability chain connecting:

**Intent → Goal → Success Criterion → Behavioral Specification → Control Contract → Action or Transition → Verification Claim → Evidence → Verification Result**

The traceability model SHALL also support references to:

- Plant.
- Sensor.
- Observation.
- Controller.
- Actuator.
- ControlVariable.
- State.
- StateTransition.
- StateInvariant.
- SafeState.
- ControlConstraint.
- EnterpriseReference.
- AssessmentReference.
- SimulationReference.

The chain SHALL support both forward and backward navigation.

For example, it should be possible to determine which evidence supports a Goal and which Goals are affected by a particular state transition.

Missing traceability SHALL be reported as a conformance finding where required by the applicable verification profile.

## 17. Canonical Metamodel Components

CR-008 introduces the following principal concepts.

| Concept                    | Responsibility                                                     |
| -------------------------- | ------------------------------------------------------------------ |
| Evidence                   | Semantic representation of supporting or contradicting information |
| EvidenceSource             | Originating source of evidence                                     |
| EvidenceRecord             | Recorded evidence instance                                         |
| EvidenceProvenance         | Origin and transformation history                                  |
| EvidenceQuality            | Assessment of evidence suitability                                 |
| EvidenceIntegrity          | Authenticity and integrity status                                  |
| EvidenceType               | Governed classification of evidence                                |
| Verification               | Governed evaluation activity                                       |
| VerificationClaim          | Proposition being evaluated                                        |
| VerificationCriterion      | Condition against which a claim is evaluated                       |
| VerificationMethod         | Method used to evaluate evidence                                   |
| VerificationResult         | Conclusion of a verification activity                              |
| VerificationFinding        | Identified issue or condition                                      |
| VerificationDisposition    | Governed treatment of a result or finding                          |
| AssuranceRequirement       | Required assurance for a claim                                     |
| IndependenceClassification | Relationship between verifier and subject                          |
| EvidenceRelationship       | Explicit evidential relationship                                   |
| EvidenceAggregation        | Governed combination of evidence                                   |
| EvidenceValidity           | Contextual and temporal applicability                              |

The implementation MAY use shared structural types, but it SHALL preserve the semantic distinctions.

## 18. Conformance Requirements

### 18.1 Evidence conformance

**VER-001:** Every Evidence record SHALL have a stable identifier.

**VER-002:** Evidence SHALL have a declared evidence type.

**VER-003:** Evidence SHALL identify its source or explicitly declare that its source is unknown.

**VER-004:** Evidence SHALL preserve its temporal reference where applicable.

**VER-005:** Evidence SHALL identify its subject or applicable scope.

**VER-006:** Evidence provenance SHALL be preserved.

**VER-007:** Derived evidence SHALL retain traceability to its source evidence.

**VER-008:** Evidence origin SHALL distinguish simulation, test and operational contexts.

**VER-009:** Evidence SHALL retain its applicable model and context references where material.

### 18.2 Verification conformance

**VER-010:** Every Verification SHALL identify its scope.

**VER-011:** Every Verification SHALL reference one or more claims.

**VER-012:** Every evaluated claim SHALL have applicable criteria.

**VER-013:** Verification methods SHALL be identifiable.

**VER-014:** Verification results SHALL reference the evidence considered.

**VER-015:** Verification results SHALL use governed outcome classifications.

**VER-016:** Verification findings SHALL be recorded where material issues are identified.

**VER-017:** Verification dispositions SHALL preserve the original result.

**VER-018:** NotApplicable outcomes SHALL have a justification.

### 18.3 Quality and integrity conformance

**VER-019:** Evidence quality SHALL be assessable against applicable dimensions.

**VER-020:** Evidence freshness SHALL be evaluated where time sensitivity applies.

**VER-021:** Evidence integrity SHALL be represented where required.

**VER-022:** Evidence uncertainty SHALL be preserved where material.

**VER-023:** Numeric confidence values SHALL identify their interpretation and derivation.

**VER-024:** Conflicting evidence SHALL be explicitly represented.

**VER-025:** Evidence supersession SHALL preserve historical records.

### 18.4 Independence and assurance conformance

**VER-026:** Verification independence SHALL be classifiable.

**VER-027:** Required independence SHALL be explicit where applicable.

**VER-028:** Assurance requirements SHALL be traceable to their governing basis.

**VER-029:** Self-verification SHALL NOT be represented as independent verification.

**VER-030:** Verification adequacy SHALL be evaluated against the claim's criticality and required assurance.

### 18.5 Closed-loop verification conformance

**VER-031:** Goal verification SHALL reference the relevant success criteria.

**VER-032:** Behavioral verification SHALL distinguish specification completeness from realized behavior.

**VER-033:** Contract verification SHALL evaluate applicable preconditions, authority and postconditions.

**VER-034:** Transition verification SHALL distinguish commanded state from established state.

**VER-035:** Outcome verification SHALL evaluate the intended operational condition.

**VER-036:** Evidence of actuator execution SHALL NOT automatically establish Plant outcome.

**VER-037:** Verification SHALL preserve applicable invariant and constraint results.

**VER-038:** Learning claims SHALL be traceable to supporting evidence.

### 18.6 Simulation and operational conformance

**VER-039:** SimulationEvidence SHALL identify the simulation run and relevant model versions.

**VER-040:** SimulationEvidence SHALL NOT be represented as OperationalEvidence.

**VER-041:** OperationalEvidence SHALL identify its operating context.

**VER-042:** Cross-origin evidence comparison SHALL preserve origin classifications.

**VER-043:** Simulation verification SHALL identify relevant assumptions and limitations.

### 18.7 Traceability and interoperability

**VER-044:** Evidence SHALL be traceable to applicable claims.

**VER-045:** Verification results SHALL be traceable to their criteria and methods.

**VER-046:** Goal verification SHALL be traceable to Intent and relevant control models.

**VER-047:** Evidence records SHALL support stable references and versioning.

**VER-048:** The canonical representation SHALL support machine-readable serialization.

**VER-049:** Structural validation SHALL be supplemented by semantic validation.

**VER-050:** Incomplete evidence chains SHALL be reported explicitly.

## 19. Conformance Profiles

AOCL SHALL distinguish the following profiles.

| Profile                          | Purpose                                                      |
| -------------------------------- | ------------------------------------------------------------ |
| Evidence Structural Conformance  | Validates evidence records and required references           |
| Evidence Provenance Conformance  | Validates source and transformation traceability             |
| Evidence Quality Conformance     | Evaluates evidence suitability for its intended use          |
| Verification Conformance         | Validates claims, criteria, methods and results              |
| Assurance Conformance            | Evaluates required independence and assurance conditions     |
| Transition Verification          | Establishes whether defined state transitions occurred       |
| Outcome Verification             | Evaluates whether intended Goals were achieved               |
| Simulation Evidence Conformance  | Validates evidence generated by simulation                   |
| Operational Evidence Conformance | Validates evidence acquired from real operating environments |

Passing evidence structural conformance SHALL NOT automatically imply that an operational claim has been verified.

Likewise, a model that has valid verification definitions may still lack the evidence required to produce a positive verification result.

## 20. Canonical Representation and Validation

The implementation SHALL provide:

1. A canonical machine-readable Evidence representation.
2. A canonical Verification representation.
3. JSON Schema validation for structural correctness.
4. Semantic validation for evidence references and provenance.
5. Validation of claim-to-criterion applicability.
6. Validation of evidence origin and context.
7. Validation of evidence temporal applicability.
8. Validation of verification independence requirements.
9. Validation of evidence aggregation references.
10. Version-aware import and export.
11. Round-trip serialization tests.
12. Reference examples covering successful, failed, inconclusive and conflicting verification.

The model SHALL support human-readable YAML serialization where consistent with AOCL conventions.

Structural schema validation SHALL NOT be treated as sufficient to establish evidence quality or claim validity.

## 21. Illustrative Example — Network Service Assurance

### 21.1 Verification objective

Establish whether a traffic redistribution intervention successfully restores network service latency to the required operating range.

**Goal:** Maintain service latency below 50 ms.

**Control action:** Redistribute traffic to an alternative route.

**Expected outcome:** Measured service latency returns below 50 ms within the applicable evaluation interval.

### 21.2 Evidence records

| Evidence | Type                  | Source                          | What it establishes                     |
| -------- | --------------------- | ------------------------------- | --------------------------------------- |
| E-01     | ObservationEvidence   | Network telemetry               | Initial latency was 72 ms               |
| E-02     | DecisionEvidence      | Service assurance Controller    | Redistribution was selected             |
| E-03     | AuthorizationEvidence | Policy and approval service     | Intervention was authorized             |
| E-04     | CommandEvidence       | Traffic engineering interface   | Redistribution command was issued       |
| E-05     | ExecutionEvidence     | Actuator interface              | Redistribution was reported complete    |
| E-06     | StateEvidence         | Network telemetry               | Traffic allocation changed              |
| E-07     | OutcomeEvidence       | Independent service measurement | Latency returned to 43 ms               |
| E-08     | ConstraintEvidence    | Resource monitoring             | Capacity constraints remained satisfied |

### 21.3 Verification claims

| Claim                           | Criterion                   | Evidence   | Result   |
| ------------------------------- | --------------------------- | ---------- | -------- |
| Decision was authorized         | Controller authority valid  | E-02, E-03 | Verified |
| Command was issued              | Command record exists       | E-04       | Verified |
| Actuator executed action        | Execution reported complete | E-05       | Verified |
| Plant state changed             | Traffic allocation changed  | E-06       | Verified |
| Service latency target achieved | Latency below 50 ms         | E-07       | Verified |
| Resource constraint preserved   | Resource use within bounds  | E-08       | Verified |

The final Goal verification is supported by the outcome evidence, not merely by the actuator execution record.

### 21.4 Failure case — Successful execution, unsuccessful outcome

Assume E-05 reports successful execution, but subsequent telemetry records latency at 65 ms.

The correct result is:

- Command execution: Verified.
- Actuator execution: Verified.
- Expected state transition: potentially Verified, depending on state evidence.
- Latency Goal: Failed.
- Overall remediation outcome: Not achieved.

AOCL SHALL preserve these separate conclusions.

### 21.5 Inconclusive case — Stale observation

Assume post-intervention telemetry reports 43 ms, but the observation timestamp falls outside the permitted freshness interval.

The result SHALL be Inconclusive or Invalid, depending on the applicable criterion and evidence rules.

AOCL SHALL NOT treat the target as achieved solely because the reported value is favorable.

### 21.6 Conflicting evidence case

Assume one telemetry source reports 43 ms and another reports 61 ms over the same relevant interval.

The evidence conflict SHALL be preserved and investigated.

The overall Goal SHALL NOT be marked Verified until the applicable verification method resolves the discrepancy or establishes that the claim can be accepted despite the difference.

## 22. Migration and Compatibility

Existing AOCL assessment, realization and operational records SHALL be reviewed for evidence-related information that can be mapped into the new model.

Migration SHALL:

- Preserve existing assessment identifiers.
- Preserve existing maturity results and their historical context.
- Preserve realization records.
- Preserve existing operational and simulation references.
- Preserve available evidence provenance.
- Identify evidence whose source or quality is unknown.
- Avoid fabricating verification claims or results.
- Avoid treating existing scores as evidence records.
- Avoid interpreting historical success indicators as independently verified outcomes.
- Retain unresolved evidence mappings as explicit migration findings.

Existing maturity assessments SHALL remain governed by their established assessment rules until changed through an appropriately scoped CR.

Evidence-backed assessment improvements SHALL not silently alter the meaning or calculation of existing maturity dimensions.

## 23. Architectural Decisions

The following decisions are proposed for formal adoption.

| Decision  | Proposed resolution                                                     |
| --------- | ----------------------------------------------------------------------- |
| AD-008-01 | Evidence is a first-class AOCL model concept                            |
| AD-008-02 | Verification is a governed evaluation activity                          |
| AD-008-03 | Verification claims and criteria are explicit                           |
| AD-008-04 | Evidence provenance is mandatory                                        |
| AD-008-05 | Evidence quality is multidimensional and claim-dependent                |
| AD-008-06 | Evidence origin distinguishes simulation, test and operational contexts |
| AD-008-07 | Command, execution, transition and outcome evidence remain distinct     |
| AD-008-08 | Verification outcomes distinguish failure from insufficient evidence    |
| AD-008-09 | Independence requirements are explicit                                  |
| AD-008-10 | Conflicting evidence is preserved rather than silently resolved         |
| AD-008-11 | SimulationEvidence does not establish operational effectiveness         |
| AD-008-12 | Verification results remain traceable to model and evidence versions    |
| AD-008-13 | Evidence and assessment scores remain separate concepts                 |
| AD-008-14 | Historical evidence and verification results are preserved              |

## 24. Acceptance Criteria

This CR is accepted when:

1. Evidence is established as a first-class model concept.
2. EvidenceSource and EvidenceProvenance are defined.
3. EvidenceRecord is distinguishable from the semantic Evidence definition.
4. Evidence types and origin classifications are defined.
5. Verification is established as a governed activity.
6. VerificationClaim and VerificationCriterion are defined.
7. VerificationMethod is defined.
8. VerificationResult and its outcome classifications are established.
9. VerificationFinding and VerificationDisposition are defined.
10. Evidence quality dimensions are established.
11. Evidence integrity and freshness semantics are defined.
12. Confidence and uncertainty are represented without requiring inappropriate numeric scoring.
13. Independence and assurance classifications are defined.
14. Evidence-to-claim relationships are explicit.
15. Evidence aggregation and conflict handling are defined.
16. Goal and outcome verification semantics are established.
17. Contract and state-transition verification are supported.
18. SimulationEvidence is distinguished from OperationalEvidence.
19. Traceability from Intent to evidence is supported.
20. Verification conformance profiles are defined.
21. Structural and semantic validation requirements are documented.
22. A successful network service assurance example is validated.
23. Failure, inconclusive and conflicting evidence cases are represented.
24. Migration preserves existing AOCL assessment and realization information.
25. No runtime orchestration or simulation-engine implementation is introduced prematurely.

## 25. Dependencies and Next Change Requests

CR-008 completes the verification and evidence foundation of the Modeling stage.

The next deliverable is:

**AOCL-CR-009 — Establish the Canonical Simulation Scenario and Disturbance Model.**

CR-009 SHALL define:

- SimulationScenario.
- Scenario identity and versioning.
- Initial conditions.
- Initial Plant and component states.
- Disturbance definitions.
- Disturbance schedules and event conditions.
- Scenario parameters.
- Environmental conditions.
- Simulation assumptions.
- Scenario variants.
- Expected observations and verification references.
- Scenario-to-model compatibility.
- Scenario reproducibility requirements.

It SHALL build on the StateSpace and StateTransition concepts from CR-007 and the Evidence and Verification concepts from CR-008.

The subsequent engine sequence remains:

| CR          | Deliverable                   |
| ----------- | ----------------------------- |
| AOCL-CR-010 | Canonical Execution Semantics |
| AOCL-CR-011 | Logical Simulation Engine     |
| AOCL-CR-012 | State-Based Simulation Engine |
| AOCL-CR-013 | Simulation Trace and Replay   |

## 26. Recommendation

Approve AOCL-CR-008 as the canonical verification and evidence foundation.

This CR establishes the mechanism by which AOCL can distinguish what a model specifies, what a loop executes, what state changes occur and what outcomes can actually be demonstrated.

It is particularly important that AOCL does not equate successful execution with successful control.

A closed loop is only demonstrably effective when its intended outcomes are established against explicit criteria using evidence of sufficient quality and assurance.

With CR-008, the Modeling stage now has a coherent basis for representing the full chain from Intent through intervention to verified outcome.

**End of AOCL-CR-008.**

Next in sequence: AOCL-CR-009 — Establish the Canonical Simulation Scenario and Disturbance Model. This will complete the core modeling foundation before we move into execution semantics and simulation engines.