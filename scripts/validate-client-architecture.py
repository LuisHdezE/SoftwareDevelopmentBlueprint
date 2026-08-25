#!/usr/bin/env python3
"""Validate Blueprint V4-4 client architecture contracts and gate semantics."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas/client-architecture.schema.json"
WEB_EXAMPLE = ROOT / "templates/client-architecture.web.example.json"
ANDROID_EXAMPLE = ROOT / "templates/client-architecture.android.example.json"

EXPECTED_GATE_CHECKS = {
    "client.architecture_contract",
    "client.visual_contract_binding",
    "client.auth_lifecycle",
    "client.api_client_strategy",
    "client.api_contract_binding",
    "client.authorization_presentation",
    "client.routing_navigation",
    "client.state_cache_strategy",
    "client.forms_validation",
    "client.async_error_offline",
    "client.idempotency_strategy",
    "client.observability_correlation",
    "client.accessibility",
    "client.testing_strategy",
    "client.platform_contract",
}


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        fail(f"{path.relative_to(ROOT)} must contain a YAML object")
    return data


def schema_errors(document: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(document), key=lambda error: list(error.absolute_path))
    return [f"{'/'.join(map(str, error.absolute_path)) or '<root>'}: {error.message}" for error in errors]


def assert_schema_valid(path: Path, document: dict[str, Any], schema: dict[str, Any]) -> None:
    errors = schema_errors(document, schema)
    if errors:
        fail(f"schema validation failed for {path.relative_to(ROOT)}: {' | '.join(errors)}")
    print(f"PASS schema: {path.relative_to(ROOT)}")


def assert_schema_invalid(name: str, document: dict[str, Any], schema: dict[str, Any]) -> None:
    if not schema_errors(document, schema):
        fail(f"negative fixture unexpectedly validated: {name}")
    print(f"PASS negative schema: {name}")


def semantic_errors(document: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    platform = document["platform"]
    prefix = "WEB-" if platform == "web" else "APP-"

    if any(not inventory_id.startswith(prefix) for inventory_id in document["inventory_ids"]):
        errors.append(f"{platform} contract contains inventory ID outside {prefix} namespace")

    operations = set(document["api_contract"]["operation_ids"])
    idempotent = set(document["idempotency"]["required_operations"])
    unknown_idempotent = sorted(idempotent - operations)
    if unknown_idempotent:
        errors.append(f"idempotency references operations outside api_contract: {unknown_idempotent}")

    if document["api_contract"]["request_id_header"] != document["observability"]["request_id_header"]:
        errors.append("API and observability request ID headers differ")

    if document["mode"] == "brownfield" and "brownfield" not in document:
        errors.append("Brownfield contract lacks coexistence block")

    if document["permissions"]["api_remains_authoritative"] is not True:
        errors.append("API must remain authorization boundary")

    if document["implementation_guardrails"]["approved_inventory_only"] is not True:
        errors.append("implementation must remain limited to approved inventory")

    return errors


def assert_semantics(name: str, document: dict[str, Any]) -> None:
    errors = semantic_errors(document)
    if errors:
        fail(f"semantic validation failed for {name}: {' | '.join(errors)}")
    print(f"PASS semantics: {name}")


def validate_catalog_gate() -> None:
    checks_doc = load_yaml(ROOT / "catalog/checks.yaml")
    gates_doc = load_yaml(ROOT / "catalog/gates.yaml")
    check_ids = {entry["id"] for entry in checks_doc.get("checks", [])}
    gates = {entry["id"]: entry for entry in gates_doc.get("gates", [])}

    gate = gates.get("client_architecture_ready")
    if gate is None:
        fail("catalog/gates.yaml lacks client_architecture_ready")
    if gate.get("evaluation_scope") != "interface_slice_platform":
        fail("client_architecture_ready must use interface_slice_platform scope")

    required = set(gate.get("require_all", []))
    if required != EXPECTED_GATE_CHECKS:
        missing = sorted(EXPECTED_GATE_CHECKS - required)
        extra = sorted(required - EXPECTED_GATE_CHECKS)
        fail(f"client_architecture_ready check set drifted; missing={missing} extra={extra}")

    unknown = sorted((required | set(gate.get("require_if_applicable", []))) - check_ids)
    if unknown:
        fail(f"client_architecture_ready references unknown checks: {unknown}")

    blocks = set(gate.get("blocks", []))
    if not {"web_implementation", "android_implementation"}.issubset(blocks):
        fail("client_architecture_ready must block both web and android implementation")

    if "client.brownfield_coexistence" not in set(gate.get("require_if_applicable", [])):
        fail("Brownfield coexistence check must remain conditional on client_architecture_ready")

    print("PASS catalog: client architecture checks and scoped gate")


def validate_skills() -> None:
    catalog = load_yaml(ROOT / "catalog/skills.yaml")
    registry = catalog.get("registry", {})

    expected = {
        "dev-react-client-architecture": "web",
        "dev-android-client-architecture": "android",
    }
    for skill_id, category in expected.items():
        entry = registry.get(skill_id)
        if not entry:
            fail(f"skill registry lacks {skill_id}")
        if entry.get("status") != "materialized" or entry.get("category") != category:
            fail(f"{skill_id} registry metadata is inconsistent")
        path = ROOT / entry["path"]
        if not path.is_file():
            fail(f"{skill_id} does not resolve to a real SKILL.md")
        body = path.read_text(encoding="utf-8")
        for reference in ["schemas/client-architecture.schema.json", "documentation/CLIENT_ARCHITECTURE_CONTRACT.md"]:
            if reference not in body:
                fail(f"{skill_id} does not reference {reference}")
        print(f"PASS skill binding: {skill_id}")


def validate_blueprint_reference() -> None:
    blueprint = (ROOT / "BLUEPRINT.md").read_text(encoding="utf-8")
    required = [
        "schemas/client-architecture.schema.json",
        "interface slice + plataforma",
        "client_architecture_ready",
    ]
    for token in required:
        if token not in blueprint:
            fail(f"BLUEPRINT.md missing V4-4 token: {token}")
    print("PASS Blueprint V4-4 normative references")


def run_negative_tests(web: dict[str, Any], android: dict[str, Any], schema: dict[str, Any]) -> None:
    bad_web_namespace = copy.deepcopy(web)
    bad_web_namespace["inventory_ids"] = ["APP-999"]
    assert_schema_invalid("web rejects APP inventory", bad_web_namespace, schema)

    bad_android_platform = copy.deepcopy(android)
    bad_android_platform["web"] = {
        "framework": "react",
        "rendering_mode": "SPA",
        "router": "React Router",
        "server_state_library": "TanStack Query",
        "form_library": "React Hook Form",
        "build_tool": "Vite",
        "browser_support": "evergreen",
    }
    assert_schema_invalid("android rejects web platform block", bad_android_platform, schema)

    bad_brownfield = copy.deepcopy(web)
    del bad_brownfield["brownfield"]
    assert_schema_invalid("brownfield requires coexistence", bad_brownfield, schema)

    bad_guardrail = copy.deepcopy(android)
    bad_guardrail["implementation_guardrails"]["no_auth_bypass"] = False
    assert_schema_invalid("authorization guardrail cannot be disabled", bad_guardrail, schema)

    bad_touch = copy.deepcopy(web)
    bad_touch["accessibility"]["min_touch_target_px"] = 43
    assert_schema_invalid("touch target below 44px rejected", bad_touch, schema)

    semantic_bad = copy.deepcopy(web)
    semantic_bad["idempotency"]["required_operations"] = ["API-NOT-IN-SLICE"]
    if not semantic_errors(semantic_bad):
        fail("semantic negative fixture failed to detect unknown idempotency operation")
    print("PASS negative semantics: idempotency operation must belong to API binding")


def main() -> None:
    schema = load_json(SCHEMA_PATH)
    Draft202012Validator.check_schema(schema)
    print("PASS schema definition: schemas/client-architecture.schema.json")

    web = load_json(WEB_EXAMPLE)
    android = load_json(ANDROID_EXAMPLE)

    assert_schema_valid(WEB_EXAMPLE, web, schema)
    assert_schema_valid(ANDROID_EXAMPLE, android, schema)
    assert_semantics("web Brownfield example", web)
    assert_semantics("Android Greenfield example", android)
    run_negative_tests(web, android, schema)
    validate_catalog_gate()
    validate_skills()
    validate_blueprint_reference()

    print("Blueprint V4-4 client architecture validation: PASS (2 positive contracts, 6 negative guards)")


if __name__ == "__main__":
    main()
