#!/usr/bin/env python3
from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import json
import yaml

ROOT = Path(__file__).resolve().parents[1]
CHECK_ID = "api.architecture_implementation_conformance"
ROOT_VERSION = "0.5.3"
CATALOG_VERSION = "0.5.3"
EXPECTED_COUNTS = (145, 19)
HISTORICAL_ORIGIN = "0.5.1"


def fail(message: str) -> None:
    raise AssertionError(message)


def load_yaml(path: str) -> dict:
    value = yaml.safe_load((ROOT / path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        fail(f"{path} must contain a mapping")
    return value


def by_id(values: list[dict]) -> dict[str, dict]:
    result: dict[str, dict] = {}
    for value in values:
        item_id = value.get("id")
        if not isinstance(item_id, str) or not item_id:
            fail("catalog entry missing id")
        if item_id in result:
            fail(f"duplicate catalog id: {item_id}")
        result[item_id] = value
    return result


def assert_contract(checks_doc: dict, gates_doc: dict) -> None:
    checks = by_id(checks_doc.get("checks", []))
    gates = by_id(gates_doc.get("gates", []))
    check = checks.get(CHECK_ID)
    if not check:
        fail(f"missing canonical check {CHECK_ID}")
    if check.get("phase") != "api_implementation" or check.get("type") != "REQUIRED" or check.get("verification") != "evidence":
        fail(f"{CHECK_ID} classification drifted")
    rule = str(check.get("rule", ""))
    for token in ("approved_architecture", "dependency_direction", "module_boundaries", "executable_assertions"):
        if token not in rule:
            fail(f"{CHECK_ID} rule missing semantic token: {token}")
    for gate_id in ("api_implemented", "api_gate"):
        if CHECK_ID not in set(gates.get(gate_id, {}).get("require_all", [])):
            fail(f"{gate_id} must require {CHECK_ID}")
    api_impl_rule = str(gates["api_implemented"].get("rule", ""))
    for token in ("approved architecture contract", "dependency direction", "executable architecture assertions"):
        if token not in api_impl_rule:
            fail(f"api_implemented rule missing token: {token}")
    api_gate_rule = str(gates["api_gate"].get("rule", ""))
    if "architecture implementation conformance" not in api_gate_rule or "runtime tests cannot substitute" not in api_gate_rule:
        fail("api_gate architecture conformance semantics drifted")


def validate_identity() -> None:
    root = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    if root != ROOT_VERSION:
        fail(f"architecture conformance validator requires root {ROOT_VERSION}, got {root}")
    checks_doc = load_yaml("catalog/checks.yaml")
    gates_doc = load_yaml("catalog/gates.yaml")
    if checks_doc.get("version") != CATALOG_VERSION or gates_doc.get("version") != CATALOG_VERSION:
        fail("stable 0.5.3 checks/gates component identity mismatch")
    if len(load_yaml("catalog/phases.yaml").get("phases", [])) != 28:
        fail("stable 0.5.3 must retain 28 phases")
    if len(checks_doc.get("checks", [])) != EXPECTED_COUNTS[0] or len(gates_doc.get("gates", [])) != EXPECTED_COUNTS[1]:
        fail("stable 0.5.3 architecture conformance counts drifted")
    assert_contract(checks_doc, gates_doc)
    manifest = json.loads((ROOT / "documentation/BLUEPRINT_V0_5_1_RELEASE.json").read_text(encoding="utf-8"))
    if manifest.get("version") != HISTORICAL_ORIGIN or manifest.get("status") != "stable" or manifest.get("counts", {}).get("checks") != 135:
        fail("historical 0.5.1 architecture-conformance provenance drifted")


def validate_negative_guards() -> None:
    checks_doc = load_yaml("catalog/checks.yaml")
    gates_doc = load_yaml("catalog/gates.yaml")
    missing_check = deepcopy(checks_doc)
    missing_check["checks"] = [item for item in missing_check.get("checks", []) if item.get("id") != CHECK_ID]
    try:
        assert_contract(missing_check, gates_doc)
    except AssertionError:
        pass
    else:
        fail("negative guard accepted missing architecture-conformance check")
    missing_binding = deepcopy(gates_doc)
    for gate in missing_binding.get("gates", []):
        if gate.get("id") == "api_gate":
            gate["require_all"] = [value for value in gate.get("require_all", []) if value != CHECK_ID]
    try:
        assert_contract(checks_doc, missing_binding)
    except AssertionError:
        pass
    else:
        fail("negative guard accepted api_gate without architecture conformance")


def validate_hardening_note() -> None:
    text = (ROOT / "documentation/BLUEPRINT_V0_5_1_ARCHITECTURE_CONFORMANCE_HARDENING.md").read_text(encoding="utf-8")
    for token in ("Architecture Implementation Conformance", CHECK_ID, "design acceptance", "implementation conformance", "executable", "Presentation", "Application", "Domain", "Infrastructure", "consumer auto-adoption"):
        if token not in text:
            fail(f"architecture-conformance hardening note missing token: {token}")


def main() -> int:
    validate_identity()
    validate_negative_guards()
    validate_hardening_note()
    print("PASS Blueprint 0.5.3 retains architecture implementation conformance")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"FAIL: {exc}")
        raise SystemExit(1)
