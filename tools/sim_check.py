#!/usr/bin/env python3
"""AOCL simulation batch runner — tests whether the level→policy mapping produces
plausible behavior (see model/behavior.yaml, docs/simulation.md).

Shim over the canonical core (src/aocl/simcore.py — extracted verbatim for
AOCL-CR-012; site/sim.js is its JS parity port). Deterministic (seeded xorshift),
stdlib-only. Invariants are pass/fail; FINDINGS are reported observations about
the formal model (aggregation semantics) that need a decision rather than a fix.

Usage: python3 tools/sim_check.py [--json] [--seed N]
Exit codes: 0 all invariants hold · 1 one or more failed · 2 usage error.
"""

import importlib
import os
import sys

try:
    _core = importlib.import_module("aocl.simcore")
except ImportError:
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))
    _core = importlib.import_module("aocl.simcore")

main = _core.main

if __name__ == "__main__":
    sys.exit(main())
