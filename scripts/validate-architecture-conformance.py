#!/usr/bin/env python3
from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
CHECK_ID = "api.architecture_implementation_conformance"
DEV_VERSION = "0.5.1-dev"
STABLE_VERSION = "0.5.0"


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
    if check.get("phase") != "api_implementation":
        fail(f"{CHECK_ID} must belong to api_implementation")
    if check.get("type") != "REQUIRED":
        fail(f"{CHECK_ID} must be REQUIRED")
    if check.get("verification") != "evidence":
        fail(f"{CHECK_ID} must require evidence")

    rule = str(check.get("rule", ""))
    for token in ("approved_architecture", "dependency_direction", "module_boundaries", "executable_assertions"):
        if token not in rule:
            fail(f"{CHECK_ID} rule missing semantic token: {token}")

    for gate_id in ("api_implemented", "api_gate"):
        gate = gates.get(gate_id)
        if not gate:
            fail(f"missing gate {gate_id}")
        required = set(gate.get("require_all", []))
        if CHECK_ID not in required:
            fail(f"{gate_id} must require {CHECK_ID}")

    api_impl_rule = str(gates["api_implemented"].get("rule", ""))
    for token in ("approved architecture contract", "dependency direction", "executable architecture assertions"):
        if token not in api_impl_rule:
            fail(f"api_implemented rule missing architecture-conformance token: {token}")

    api_gate_rule = str(gates["api_gate"].get("rule", ""))
    if "architecture implementation conformance" not in api_gate_rule:
        fail("api_gate must aggregate architecture implementation conformance")
    if "runtime tests cannot substitute" not in api_gate_rule:
        fail("api_gate must reject runtime-only substitution for architecture conformance")


def validate_development_identity() -> None:
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    if version != STABLE_VERSION:
        fail(f"semantic hardening boundary must preserve stable VERSION={STABLE_VERSION}; got {version}")

    checks_doc = load_yaml("catalog/checks.yaml")
    gates_doc = load_yaml("catalog/gates.yaml")
    if checks_doc.get("version") != DEV_VERSION:
        fail(f"catalog/checks.yaml must declare {DEV_VERSION}")
    if gates_doc.get("version") != DEV_VERSION:
        fail(f"catalog/gates.yaml must declare {DEV_VERSION}")

    phases = load_yaml("catalog/phases.yaml").get("phases", [])
    if len(phases) != 28:
        fail("0.5.1 architecture hardening must not add/remove phases")
    if len(checks_doc.get("checks", [])) != 135:
        fail("0.5.1-dev must contain exactly one additional check over stable 0.5.0")
    if len(gates_doc.get("gates", [])) != 18:
        fail("0.5.1 architecture hardening must not add/remove gates")

    assert_contract(checks_doc, gates_doc)


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
        fail("negative guard failed: missing architecture-conformance check was accepted")

    missing_gate_binding = deepcopy(gates_doc)
    for gate in missing_gate_binding.get("gates", []):
        if gate.get("id") == "api_gate":
            gate["require_all"] = [value for value in gate.get("require_all", []) if value != CHECK_ID]
    try:
        assert_contract(checks_doc, missing_gate_binding)
    except AssertionError:
        pass
    else:
        fail("negative guard failed: api_gate without architecture conformance was accepted")


def validate_hardening_note() -> None:
    path = ROOT / "documentation/BLUEPRINT_V0_5_1_ARCHITECTURE_CONFORMANCE_HARDENING.md"
    if not path.exists():
        fail("architecture-conformance hardening note missing")
    text = path.read_text(encoding="utf-8")
    for token in (
        "Architecture Implementation Conformance",
        CHECK_ID,
        "design acceptance",
        "implementation conformance",
        "executable",
        "Presentation",
        "Application",
        "Domain",
        "Infrastructure",
        "consumer auto-adoption",
    ):
        if token not in text:
            fail(f"hardening note missing token: {token}")


def main() -> int:
    validate_development_identity()
    validate_negative_guards()
    validate_hardening_note()
    print("PASS Blueprint 0.5.1-dev architecture implementation conformance hardening")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"FAIL: {exc}")
        raise SystemExit(1)
