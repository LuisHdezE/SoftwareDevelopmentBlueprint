#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
CORE = ROOT / "scripts" / "validate-artifact-graph-core.py"

spec = importlib.util.spec_from_file_location("blueprint_artifact_graph_core", CORE)
if spec is None or spec.loader is None:
    raise RuntimeError(f"Unable to load architecture conformance validator core: {CORE}")
core = importlib.util.module_from_spec(spec)
spec.loader.exec_module(core)

# Public compatibility surface consumed by repository validators such as
# validate-platform-matrix.py. The core extraction must not silently remove the
# executable validator API used by sibling validation modules.
load = core.load
fixture_docs = core.fixture_docs
validate_schema_instance = core.validate_schema_instance
validate_graph_documents = core.validate_graph_documents

_original_remap = core.remap_platform_fixture


def remap_platform_fixture(docs, platform: str, *, enable_target: bool) -> None:
    """Remap platform fixtures while inheriting the active project contract version."""
    _original_remap(docs, platform, enable_target=enable_target)
    active_version = docs.get("project", {}).get("blueprint", {}).get("version")
    if not active_version:
        raise AssertionError("platform fixture requires project.blueprint.version")

    for key in ("baseline", "inventory", "slice", "evidence", "impact"):
        docs[key]["schema_version"] = active_version
    docs["status"]["blueprint_version"] = active_version


core.remap_platform_fixture = remap_platform_fixture

_original_print = print


def version_neutral_print(*args, **kwargs):
    if args and args[0] == "Blueprint v0.5.4-dev artifact graph validation: PASS":
        args = ("Blueprint artifact graph validation: PASS", *args[1:])
    _original_print(*args, **kwargs)


core.print = version_neutral_print

if __name__ == "__main__":
    try:
        raise SystemExit(core.main())
    except Exception as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise
