#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
CORE = ROOT / "scripts" / "validate-ci-runtime-core.py"

spec = importlib.util.spec_from_file_location("blueprint_ci_runtime_core", CORE)
if spec is None or spec.loader is None:
    raise RuntimeError(f"Unable to load CI runtime validator core: {CORE}")
core = importlib.util.module_from_spec(spec)
spec.loader.exec_module(core)

# CI runtime remains a 0.5.2-compatible component; 0.5.4 is an allowed consuming root.
core.SUPPORTED_ROOT_VERSIONS = set(core.SUPPORTED_ROOT_VERSIONS) | {"0.5.4"}

if __name__ == "__main__":
    try:
        raise SystemExit(core.main())
    except AssertionError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
