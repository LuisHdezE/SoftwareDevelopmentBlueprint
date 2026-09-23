#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
CORE = ROOT / "scripts" / "validate-architecture-conformance-core.py"

spec = importlib.util.spec_from_file_location("blueprint_architecture_conformance_core", CORE)
if spec is None or spec.loader is None:
    raise RuntimeError(f"Unable to load architecture conformance validator core: {CORE}")
core = importlib.util.module_from_spec(spec)
spec.loader.exec_module(core)

# Preserve the 0.5.1-compatible component semantics while validating the active stable
# 0.5.4 root/catalog contract. Opening the 0.5.5-dev lane does not itself promote the
# architecture-conformance catalog provenance; a later increment must do that explicitly.
core.ROOT_VERSION = "0.5.4"
core.STABLE_CATALOG_VERSION = "0.5.4"
core.STABLE_COUNTS = {"phases": 29, "checks": 146, "gates": 19}

marker = ROOT / "DEVELOPMENT_VERSION"
if marker.is_file():
    development_version = marker.read_text(encoding="utf-8").strip()
    if development_version == "0.5.5-dev":
        core.active_catalog_contract = lambda: (core.STABLE_CATALOG_VERSION, core.STABLE_COUNTS)

if __name__ == "__main__":
    try:
        raise SystemExit(core.main())
    except AssertionError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
