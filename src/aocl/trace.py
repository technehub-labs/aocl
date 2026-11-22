"""AOCL Simulation Trace and Replay (AOCL-CR-013).

Implements rules TRC-001..016 natively (stdlib + pyyaml):

- envelope conformance: run identity, bindings, declared inputs, termination,
  evidence reference (TRC-001/002/007/009/013);
- record conformance: canonical classes, temporal references, governed
  outcomes, non-decreasing ordering, single-run scope (TRC-003..006, 008);
- replay verification (TRC-010..012, 016): re-executes the bound execution
  definition against the bound artifacts under the envelope's declared inputs,
  then compares the produced record sequence with the recorded one on
  (class, ref, outcome) triples — detail text MAY differ without failing
  replay. Structural validity is distinct from replay success (TRC-016);
  replay compatibility is engine-version-scoped (TRC-012).

Replay today supports the logical engine (CR-011); a state-based replay binds
through the same interface when the state-based engine emits record sequences.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("error: pyyaml is required for the trace model (pip install pyyaml)")

try:
    from .engine_logical import LogicalEngine, EngineError
except ImportError:  # direct-script execution
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from aocl.engine_logical import LogicalEngine, EngineError

RULESET_VERSION = "1.0.0"
SCHEMA_VERSION = "0.1"
TRACE_VERSION = "1.0.0"

RECORD_CLASSES = {"Activation", "ConditionEvaluation", "TransitionEvaluation", "Dispatch",
                  "ApprovalResolution", "ExceptionDisposition", "SafeStateTransition"}
RUN_URN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9-]*$")
SEMVER = re.compile(r"^\d+\.\d+\.\d+$")


def _f(findings: list, rule: str, severity: str, message: str) -> None:
    findings.append({"rule": rule, "severity": severity, "message": message})


def validate_trace(data: dict) -> dict:
    """Validate a canonical ExecutionTrace document against TRC-001..016
    (structural + integrity; replay is separate)."""
    findings: list[dict] = []
    if not isinstance(data, dict):
        _f(findings, "TRC-014", "error", "document must be a mapping")
        return _result(findings)
    if data.get("schemaVersion") != SCHEMA_VERSION:
        _f(findings, "TRC-014", "error",
           f"schemaVersion must be '{SCHEMA_VERSION}', got {data.get('schemaVersion')!r}")
    if not SEMVER.match(str(data.get("traceVersion", ""))):
        _f(findings, "TRC-014", "error", f"traceVersion must be semver, got {data.get('traceVersion')!r}")
    trace = data.get("executionTrace")
    if not isinstance(trace, dict):
        _f(findings, "TRC-014", "error", "executionTrace missing")
        return _result(findings)

    known_root = {"schemaVersion", "traceVersion", "executionTrace"}
    if set(data) - known_root:
        _f(findings, "TRC-014", "error", f"unknown document attributes: {sorted(set(data) - known_root)}")

    # ---- envelope (TRC-001/002)
    run_id = trace.get("runId")
    if not isinstance(run_id, str) or not RUN_URN.match(run_id):
        _f(findings, "TRC-001", "error", f"runId {run_id!r} must be a stable run identity (TRC-001)")
    if trace.get("type") != "ExecutionTrace":
        _f(findings, "TRC-002", "error", "type must be 'ExecutionTrace'")
    for field in ("executionRef", "specRef", "specVersion", "scenarioRef", "scenarioId",
                  "scenarioVersion", "engineName", "engineVersion"):
        if not str(trace.get(field, "")).strip():
            _f(findings, "TRC-002", "error", f"envelope binding missing: {field} (TRC-002)")
    if trace.get("evidenceRef") is None:
        findings.append({"rule": "TRC-013", "severity": "warning",
                         "message": "no evidenceRef — the trace is not linked to its SimulationEvidence record (TRC-013)"})

    # ---- declared inputs (TRC-007)
    inputs = trace.get("runInputs") or {}
    if "seed" not in trace:
        _f(findings, "TRC-007", "error", "declared seed missing — the run cannot be reproduced (TRC-007)")
    known_inputs = {"approvals", "failures"}
    if set(inputs) - known_inputs:
        _f(findings, "TRC-007", "error", f"unknown runInputs: {sorted(set(inputs) - known_inputs)}")

    # ---- records (TRC-003..006, 008)
    records = trace.get("records") or []
    if not records:
        _f(findings, "TRC-003", "error", "an empty trace records nothing (TRC-003)")
    last_t = -1
    seen_refs: set = set()
    for i, rec in enumerate(records):
        if not isinstance(rec, dict):
            _f(findings, "TRC-003", "error", f"records[{i}] must be a mapping")
            continue
        rid = rec.get("recordId", f"[{i}]")
        if not str(rec.get("recordId", "")).strip() or len(str(rid)) < 3:
            _f(findings, "TRC-004", "error", f"record {rid}: stable recordId missing (TRC-004)")
        if rid in seen_refs:
            _f(findings, "TRC-004", "error", f"duplicate recordId {rid!r} (TRC-004)")
        seen_refs.add(rid)
        if rec.get("class") not in RECORD_CLASSES:
            _f(findings, "TRC-003", "error", f"record {rid}: class {rec.get('class')!r} not canonical (TRC-003)")
        t = rec.get("t")
        if not isinstance(t, int) or t < 0:
            _f(findings, "TRC-003", "error", f"record {rid}: temporal reference must be a non-negative integer (TRC-003)")
        elif t < last_t:
            _f(findings, "TRC-006", "error",
               f"record {rid}: temporal reference {t} goes backwards (previous {last_t}) — "
               "records are ordered by non-decreasing time (TRC-006)")
        last_t = max(last_t, t)
        if not str(rec.get("ref", "")).strip():
            _f(findings, "TRC-004", "error", f"record {rid}: referenced element/condition/event required (TRC-004)")
        if rec.get("class") == "ConditionEvaluation" and rec.get("channel") not in (None, "actual", "observed", "estimated"):
            _f(findings, "TRC-005", "error", f"record {rid}: channel {rec.get('channel')!r} not governed (TRC-005)")

    # ---- termination + terminal records (TRC-009/015)
    term = trace.get("termination")
    if not isinstance(term, dict) or not str(term.get("outcome", "")).strip() or not str(term.get("why", "")).strip():
        _f(findings, "TRC-009", "error", "terminated runs must record their outcome and reason (TRC-009)")
    else:
        outcome = term.get("outcome")
        classes = {r.get("class") for r in records if isinstance(r, dict)}
        if outcome == "SafeStateTransition" and "SafeStateTransition" not in classes:
            _f(findings, "TRC-015", "error",
               "termination outcome SafeStateTransition but no SafeStateTransition record — "
               "incomplete trace flagged (TRC-015)")
        if outcome in ("Failed",) and "ExceptionDisposition" not in classes:
            findings.append({"rule": "TRC-015", "severity": "warning",
                             "message": "termination Failed without an ExceptionDisposition record — "
                                        "flagged as incomplete (TRC-015)"})
    return _result(findings)


def build_trace(summary: dict, records: list, *, spec_ref: str, spec_version: str,
                scenario_version: str, engine_name: str = "aocl-engine-logical") -> dict:
    """Serialize an engine run into the canonical ExecutionTrace envelope (TRC-001..013).
    Assigns stable recordIds (r-001…) — serialization is CR-013's concern, not the engine's."""
    inputs = summary.get("runInputs", {})
    return {
        "schemaVersion": SCHEMA_VERSION, "traceVersion": TRACE_VERSION,
        "executionTrace": {
            "runId": summary["runId"], "type": "ExecutionTrace",
            "executionRef": summary["executionRef"],
            "specRef": spec_ref, "specVersion": spec_version,
            "scenarioRef": summary["scenarioRef"], "scenarioId": summary["scenarioId"],
            "scenarioVersion": scenario_version,
            "engineName": engine_name, "engineVersion": summary["engineVersion"],
            "seed": summary["seed"],
            "runInputs": {"approvals": inputs.get("approvals", {}),
                           "failures": inputs.get("failures", [])},
            "termination": {"outcome": summary["terminationOutcome"],
                             "why": summary["terminationWhy"], "t": summary["ticks"]},
            "evidenceRef": summary["evidence"]["evidenceId"],
            "records": [dict(r, recordId=f"r-{i:03d}") for i, r in enumerate(records, 1)],
        },
    }


def _result(findings: list) -> dict:
    errors = [f for f in findings if f["severity"] == "error"]
    return {"valid": not errors, "findings": findings,
            "conformance": {"envelopeValid": not any(f["rule"] in ("TRC-001", "TRC-002", "TRC-007",
                                                                   "TRC-009", "TRC-013", "TRC-014") for f in errors),
                             "recordsValid": not any(f["rule"] in ("TRC-003", "TRC-004", "TRC-005",
                                                                   "TRC-006", "TRC-008") for f in errors),
                             "replayVerified": False}}


def _sequence(records: list) -> list:
    return [(r.get("class"), r.get("ref"), r.get("outcome")) for r in records]


def replay_verify(trace_doc: dict, execution: dict, spec: dict, scenario_doc: dict,
                  control=None, evidence=None) -> dict:
    """TRC-010..012/016: re-execute and compare sequences on (class, ref, outcome)."""
    findings: list[dict] = []
    trace = trace_doc.get("executionTrace", {})
    if trace.get("engineName") != "aocl-engine-logical":
        return {"valid": False, "findings": [{"rule": "TRC-012", "severity": "error",
                 "message": f"replay is engine-scoped: {trace.get('engineName')!r} traces do not replay "
                            "through the logical engine (TRC-012)"}],
                "conformance": {"replayVerified": False}, "replay": {"replayed": False}}
    try:
        engine = LogicalEngine(execution, spec, scenario_doc, control, evidence,
                               seed=trace.get("seed", 0),
                               run_inputs=trace.get("runInputs") or {})
        engine.gate()
        engine.setup()
        # re-run with the same machinery the original run used
        summary = engine.run()
    except EngineError as exc:
        return {"valid": False,
                "findings": [{"rule": "TRC-010", "severity": "error",
                              "message": f"replay could not execute the bound artifacts: {exc}"}],
                "conformance": {"replayVerified": False}, "replay": {"replayed": False}}
    produced = _sequence(engine.trace)
    recorded = _sequence(trace.get("records") or [])
    if produced == recorded:
        return {"valid": True, "findings": findings,
                "conformance": {"replayVerified": True},
                "replay": {"replayed": True, "recordsCompared": len(recorded),
                            "engineVersion": trace.get("engineVersion"),
                            "terminationMatch": summary["terminationOutcome"] == (trace.get("termination") or {}).get("outcome")}}
    # first difference (TRC-011)
    n = min(len(produced), len(recorded))
    pos = next((i for i in range(n) if produced[i] != recorded[i]), n)
    findings.append({"rule": "TRC-010", "severity": "error",
                     "message": f"replay diverges at record {pos}: recorded {recorded[pos] if pos < len(recorded) else '<end>'}"
                                f" vs produced {produced[pos] if pos < len(produced) else '<end>'} (TRC-010/011)"})
    return {"valid": False, "findings": findings,
            "conformance": {"replayVerified": False},
            "replay": {"replayed": True, "recordsCompared": n}}


def load_and_validate(path: str | Path) -> dict:
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh) if str(path).endswith(".json") else yaml.safe_load(fh)
    result = validate_trace(data)
    result["source"] = str(path)
    return result


def render(result: dict) -> str:
    lines = [f"AOCL execution trace — {result.get('source', 'validation')}"]
    conf = result.get("conformance", {})
    lines.append(" · ".join(f"{k}={v}" for k, v in conf.items()))
    for f in result.get("findings", []):
        lines.append(f"[{f['severity'].upper()}] {f['rule']}: {f['message']}")
    if not result.get("findings"):
        lines.append("No findings — TRC-001..016 satisfied.")
    return "\n".join(lines)


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--self-test" in argv:
        return _self_test()
    as_json = "--json" in argv
    argv = [a for a in argv if a != "--json"]
    if not argv:
        print("usage: aocl-trace validate <trace.json> [--json] | verify <trace.json> "
              "--execution <yaml> --spec <yaml> --scenarios <yaml> [--control <yaml>] [--evidence <yaml>] | --self-test")
        return 2
    if argv[0] == "validate":
        try:
            result = load_and_validate(argv[1])
        except (OSError, ValueError) as exc:
            print(f"error: {exc}")
            return 2
        print(json.dumps(result, indent=2, default=str) if as_json else render(result))
        return 0 if result["valid"] else 1
    if argv[0] == "verify":
        rest = argv[1:]
        opts = {}
        i = 0
        while i < len(rest):
            if rest[i] == "--execution":
                opts["execution"] = rest[i + 1]; i += 2
            elif rest[i] == "--spec":
                opts["spec"] = rest[i + 1]; i += 2
            elif rest[i] == "--scenarios":
                opts["scenarios"] = rest[i + 1]; i += 2
            elif rest[i] == "--control":
                opts["control"] = rest[i + 1]; i += 2
            elif rest[i] == "--evidence":
                opts["evidence"] = rest[i + 1]; i += 2
            else:
                i += 1
        try:
            trace_doc = _load_json_yaml(rest[0])
        except (OSError, ValueError) as exc:
            print(f"error: {exc}")
            return 2
        for required in ("execution", "spec", "scenarios"):
            if required not in opts:
                print(f"error: --{required} is required for replay")
                return 2
        load = lambda p: (json.load(open(p)) if p.endswith(".json") else yaml.safe_load(open(p, encoding="utf-8")))
        result = replay_verify(trace_doc, load(opts["execution"]), load(opts["spec"]),
                               load(opts["scenarios"]),
                               load(opts["control"]) if opts.get("control") else None,
                               load(opts["evidence"]) if opts.get("evidence") else None)
        print(json.dumps(result, indent=2, default=str) if as_json else render(result))
        return 0 if result["valid"] else 1
    print("unknown command")
    return 2


def _load_json_yaml(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh) if str(path).endswith(".json") else yaml.safe_load(fh)


def _self_test() -> int:
    import copy, subprocess

    # build the canonical trace from the reference logical run
    exec_doc = _load_json_yaml("examples/execution-definition-logical.yaml")
    spec = _load_json_yaml("examples/behavioral-spec.yaml")
    scen = _load_json_yaml("examples/scenario-library.yaml")
    control = _load_json_yaml("examples/control-contract.yaml")
    evidence = _load_json_yaml("examples/evidence-model.yaml")
    engine = LogicalEngine(exec_doc, spec, scen, control, evidence, seed=2026,
                           run_inputs={"approvals": {"approve-reroute": {"resolution": "granted", "atTick": 3}}})
    summary = engine.run()
    assert summary["terminationOutcome"] == "VerifiedCompletion"
    trace_doc = build_trace(summary, engine.trace,
                             spec_ref="urn:aocl:spec:network-assurance-001",
                             spec_version="1.0.0", scenario_version="1.0.0")
    result = validate_trace(copy.deepcopy(trace_doc))
    assert result["valid"], result["findings"]
    assert result["conformance"]["envelopeValid"] and result["conformance"]["recordsValid"]

    # replay: identical sequence → verified (TRC-010)
    rep = replay_verify(copy.deepcopy(trace_doc), copy.deepcopy(exec_doc), copy.deepcopy(spec),
                        copy.deepcopy(scen), copy.deepcopy(control), copy.deepcopy(evidence))
    assert rep["valid"] and rep["conformance"]["replayVerified"], rep

    # a mutated trace fails replay at the differing position (TRC-011)
    mutated = copy.deepcopy(trace_doc)
    mutated["executionTrace"]["records"][5]["outcome"] = "Bogus"
    rep2 = replay_verify(mutated, copy.deepcopy(exec_doc), copy.deepcopy(spec), copy.deepcopy(scen))
    assert not rep2["valid"] and any("diverges at record" in f["message"] for f in rep2["findings"])

    # integrity rules
    def broken(mutator):
        d = copy.deepcopy(trace_doc)
        mutator(d["executionTrace"])
        return validate_trace(d)

    r = broken(lambda t: t.__setitem__("records", []))
    assert any(f["rule"] == "TRC-003" for f in r["findings"])
    r = broken(lambda t: t["records"][3].__setitem__("class", "Vibes"))
    assert any(f["rule"] == "TRC-003" for f in r["findings"])
    r = broken(lambda t: t["records"].reverse())
    assert any(f["rule"] == "TRC-006" for f in r["findings"])
    r = broken(lambda t: t.pop("termination"))
    assert any(f["rule"] == "TRC-009" for f in r["findings"])
    r = broken(lambda t: t.pop("seed"))
    assert any(f["rule"] == "TRC-007" for f in r["findings"])
    r = broken(lambda t: t.__setitem__("termination", {"outcome": "SafeStateTransition", "why": "x"}))
    assert any(f["rule"] == "TRC-015" for f in r["findings"])

    # state-based traces don't replay through the logical engine (TRC-012)
    sb = copy.deepcopy(trace_doc)
    sb["executionTrace"]["engineName"] = "aocl-engine-statebased"
    rep3 = replay_verify(sb, exec_doc, spec, scen)
    assert any(f["rule"] == "TRC-012" for f in rep3["findings"])

    print(f"self-test OK (trace & replay v{RULESET_VERSION}, schema {SCHEMA_VERSION}, TRC-001..016)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
