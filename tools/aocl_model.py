#!/usr/bin/env python3
"""Zero-install shim: prefers the installed aocl package, falls back to ../src.

import_module is used (not `from aocl import ...`) because aocl/__init__ re-exports
an `model` symbol that would shadow the submodule attribute."""
import importlib
import os
import sys

try:
    _impl = importlib.import_module("aocl.model")
except ImportError:
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))
    _impl = importlib.import_module("aocl.model")

RULESET_VERSION = _impl.RULESET_VERSION
main = _impl.main
_self_test = _impl._self_test

if __name__ == "__main__":
    sys.exit(main())
