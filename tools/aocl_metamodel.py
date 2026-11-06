#!/usr/bin/env python3
"""Zero-install shim: prefers the installed aocl package, falls back to ../src."""
import importlib
import os
import sys

try:
    _impl = importlib.import_module("aocl.metamodel")
except ImportError:
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))
    _impl = importlib.import_module("aocl.metamodel")

main = _impl.main
_self_test = _impl._self_test

if __name__ == "__main__":
    sys.exit(main())
