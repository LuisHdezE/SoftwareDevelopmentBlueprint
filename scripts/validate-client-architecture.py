#!/usr/bin/env python3
"""Validate Blueprint 0.5 composed client architecture contracts."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
BASELINE_SCHEMA_PATH = ROOT / "schemas/client-platform-architecture.schema.json"
BINDING_SCHEMA_PATH = ROOT / "schemas/client-architecture.schema.json"
WEB_BASELINE_PATH = ROOT / "templates/client-platform-architecture.web.example.json"
ANDROID_BASELINE_PATH = ROOT / "templates/client-platform-architecture.android.example.json"
WEB_BINDING_PATH = ROOT / "templates/client-architecture.web.example.json"
ANDROID_BINDING_PATH = ROOT / "templates/client-architecture.android.example.json"
INVENTORY_PATH = ROOT / "templates/interface-inventory.example.json"
OPENAPI_PATH = ROOT / "tests/fixtures/artifact-graph/openapi.yaml"
FUNCTIONAL_SLICE_PATH = ROOT / "templates/functional-interface-slice.example.json"

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
    raise AssertionError(message)


def load(path: Path) -> Any:
    text = path.read_text(encoding="utf-8")
    if path.suffix == ".json":
        return json.loads(text)
    if path.suffix in {".yaml", ".yml"}:
        return yaml.safe_load(text)
    raise ValueError(f"Unsupported file: {path}")


def schema_errors(document: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    return [
        f"{'/'.join(map(str, error.absolute_path)) or '<root>'}: {error.message}"
        for error in sorted(validator.iter_errors(document), key=lambda e: list(e.absolute_path))
    ]


def assert_schema_valid(label: str, document: dict[str, Any], schema: dict[str, Any]) -> None:
    errors = schema_errors(document, schema)
    if errors:
        fail(f"schema validation failed for {label}: {' | '.join(errors)}")
    print(f"PASS schema: {label}")


def assert_schema_invalid(label: str, document: dict[str, Any], schema: dict[str, Any]) -> None:
    if not schema_errors(document, schema):
        fail(f"negative schema fixture unexpectedly passed: {label}")
    print(f"PASS negative schema: {label}")


def openapi_operation_ids(document: dict[str, Any]) -> set[str]:
    result: set[str] = set()
    for path_item in document.get("paths", {}).values():
        if not isinstance(path_item, dict):
            continue
        for method, operation in path_item.items():
            if method.lower() not in {"get", "post", "put", "patch", "delete", "head", "options", "trace"}:
                continue
            if isinstance(operation, dict) and operation.get("operationId"):
                result.add(operation["operationId"])
    return result


def interface_operation_ids(item: dict[str, Any]) -> set[str]:
    result: set[str] = set()
    for data in item.get("data", []):
        result.update(data.get("operation_ids", []))
    for action in item.get("actions", []):
        result.update(action.get("operation_ids", []))
    return result


def validate_file_reference(value: str, label: str) -> None:
    path = ROOT / value
    if not path.is_file():
        fail(f"{label} references missing repository file: {value}")


def baseline_semantic_errors(baseline: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if baseline["api_client"]["request_id_header"] != baseline["observability"]["request_id_header"]:
        errors.append("API client and observability request ID headers differ")
    if baseline["permissions"]["api_remains_authoritative"] is not True:
        errors.append("API authorization must remain authoritative")
    guardrails = baseline["implementation_guardrails"]
    for key in (
        "no_new_api_behavior",
        "no_auth_bypass",
        "approved_inventory_only",
        "high_risk_mutations_follow_idempotency",
        "no_hardcoded_authoritative_business_data",
    ):
        if guardrails[key] is not True:
            errors.append(f"platform guardrail disabled: {key}")
    if baseline["mode"] == "brownfield" and "brownfield" not in baseline:
        errors.append("Brownfield baseline lacks coexistence contract")
    return errors


def assert_baseline_semantics(label: str, baseline: dict[str, Any]) -> None:
    errors = baseline_semantic_errors(baseline)
    if errors:
        fail(f"baseline semantics failed for {label}: {' | '.join(errors)}")
    validate_file_reference(baseline["design_system"]["design_system_path"], f"{label}.design_system")
    validate_file_reference(baseline["design_system"]["tokens_path"], f"{label}.tokens")
    validate_file_reference(baseline["api_client"]["openapi_path"], f"{label}.openapi")
    print(f"PASS semantics: {label}")


def binding_semantic_errors(
    binding: dict[str, Any],
    baseline: dict[str, Any],
    *,
    inventory: dict[str, Any] | None = None,
    openapi: dict[str, Any] | None = None,
) -> list[str]:
    errors: list[str] = []

    for key in ("project_id", "mode", "platform"):
        if binding[key] != baseline[key]:
            errors.append(f"binding {key} does not match platform baseline")

    if binding["api_binding"]["openapi_path"] != baseline["api_client"]["openapi_path"]:
        errors.append("binding OpenAPI path differs from platform baseline")

    operations = set(binding["api_binding"]["operation_ids"])
    idempotent = set(binding["idempotency"]["required_operations"])
    if not idempotent.issubset(operations):
        errors.append("idempotency operations must be a subset of binding operationIds")

    if binding["visual_references"]["mode"] == "approved_optional":
        for reference in binding["visual_references"]["approved_reference_paths"]:
            if not (ROOT / reference).is_file():
                errors.append(f"approved visual reference does not exist: {reference}")

    if openapi is not None:
        known_operation_ids = openapi_operation_ids(openapi)
        unknown = sorted(operations - known_operation_ids)
        if unknown:
            errors.append(f"binding references unknown OpenAPI operationIds: {unknown}")

    if inventory is not None:
        if inventory.get("maturity") != "EXECUTABLE_INVENTORY":
            errors.append("binding must target EXECUTABLE_INVENTORY")
        by_id = {item["id"]: item for item in inventory["items"]}
        selected: list[dict[str, Any]] = []
        for inventory_id in binding["inventory_ids"]:
            item = by_id.get(inventory_id)
            if item is None:
                errors.append(f"binding references missing inventory ID {inventory_id}")
                continue
            selected.append(item)
            if item["platform"] != binding["platform"]:
                errors.append(f"{inventory_id} platform differs from binding platform")
            if item.get("slice_id") != binding["interface_slice"]:
                errors.append(f"{inventory_id} belongs to slice {item.get('slice_id')}, not {binding['interface_slice']}")

        selected_ops: set[str] = set()
        selected_permissions: set[str] = set()
        selected_routes: set[str] = set()
        for item in selected:
            selected_ops.update(interface_operation_ids(item))
            selected_permissions.update(item.get("permissions", []))
            route = item.get("navigation", {}).get("route")
            if route:
                selected_routes.add(route)

        if operations != selected_ops:
            errors.append(
                f"binding operationIds differ from executable inventory: binding={sorted(operations)} inventory={sorted(selected_ops)}"
            )
        declared_permissions = set(binding["api_binding"]["permissions"])
        if declared_permissions != selected_permissions:
            errors.append(
                f"binding permissions differ from executable inventory: binding={sorted(declared_permissions)} inventory={sorted(selected_permissions)}"
            )
        if not selected_routes.issubset(set(binding["routing"]["routes"])):
            errors.append("binding routes do not cover executable inventory routes")

    guardrails = binding["implementation_guardrails"]
    for key in (
        "api_authoritative",
        "no_new_api_behavior",
        "approved_inventory_only",
        "no_hardcoded_authoritative_business_data",
    ):
        if guardrails[key] is not True:
            errors.append(f"slice guardrail disabled: {key}")

    return errors


def assert_binding_semantics(
    label: str,
    binding: dict[str, Any],
    baseline: dict[str, Any],
    *,
    inventory: dict[str, Any] | None = None,
    openapi: dict[str, Any] | None = None,
) -> None:
    errors = binding_semantic_errors(binding, baseline, inventory=inventory, openapi=openapi)
    if errors:
        fail(f"binding semantics failed for {label}: {' | '.join(errors)}")
    validate_file_reference(binding["platform_baseline_ref"], f"{label}.platform_baseline_ref")
    print(f"PASS semantics: {label}")


def validate_functional_slice_binding(web_binding: dict[str, Any]) -> None:
    functional = load(FUNCTIONAL_SLICE_PATH)
    artifact = functional["client_architecture"]["artifact"]
    expected = str(WEB_BINDING_PATH.relative_to(ROOT)).replace("\\", "/")
    if artifact != expected:
        fail(f"functional slice points to {artifact}, expected {expected}")
    if functional["id"] != web_binding["interface_slice"]:
        fail("functional slice id differs from client architecture binding")
    if functional["platform"] != web_binding["platform"]:
        fail("functional slice platform differs from client architecture binding")
    if set(functional["inventory_ids"]) != set(web_binding["inventory_ids"]):
        fail("functional slice inventory IDs differ from client architecture binding")
    if set(functional["api_binding"]["operation_ids"]) != set(web_binding["api_binding"]["operation_ids"]):
        fail("functional slice operationIds differ from client architecture binding")
    if functional["api_binding"]["revision"] != web_binding["api_binding"]["revision"]:
        fail("functional slice API revision differs from client architecture binding")
    print("PASS functional slice -> client architecture binding integrity")


def validate_catalog_gate() -> None:
    checks_doc = load(ROOT / "catalog/checks.yaml")
    gates_doc = load(ROOT / "catalog/gates.yaml")
    check_ids = {entry["id"] for entry in checks_doc.get("checks", [])}
    gates = {entry["id"]: entry for entry in gates_doc.get("gates", [])}

    gate = gates.get("client_architecture_ready")
    if gate is None:
        fail("catalog/gates.yaml lacks client_architecture_ready")
    if gate.get("evaluation_scope") != "interface_slice_platform":
        fail("client_architecture_ready must remain interface_slice_platform scoped")

    required = set(gate.get("require_all", []))
    if required != EXPECTED_GATE_CHECKS:
        fail(
            f"client_architecture_ready check set drifted; missing={sorted(EXPECTED_GATE_CHECKS-required)} extra={sorted(required-EXPECTED_GATE_CHECKS)}"
        )

    unknown = sorted((required | set(gate.get("require_if_applicable", []))) - check_ids)
    if unknown:
        fail(f"client_architecture_ready references unknown checks: {unknown}")
    if "client.brownfield_coexistence" not in set(gate.get("require_if_applicable", [])):
        fail("Brownfield coexistence must remain conditional on client_architecture_ready")
    print("PASS catalog: composed architecture feeds existing scoped gate")


def expect_semantic_failure(label: str, binding: dict[str, Any], baseline: dict[str, Any], inventory: dict[str, Any], openapi: dict[str, Any]) -> None:
    if not binding_semantic_errors(binding, baseline, inventory=inventory, openapi=openapi):
        fail(f"negative semantic fixture unexpectedly passed: {label}")
    print(f"PASS negative semantics: {label}")


def run_negative_tests(
    web_baseline: dict[str, Any],
    android_baseline: dict[str, Any],
    web_binding: dict[str, Any],
    android_binding: dict[str, Any],
    baseline_schema: dict[str, Any],
    binding_schema: dict[str, Any],
    inventory: dict[str, Any],
    openapi: dict[str, Any],
) -> None:
    bad_brownfield = copy.deepcopy(web_baseline)
    del bad_brownfield["brownfield"]
    assert_schema_invalid("Brownfield baseline requires coexistence", bad_brownfield, baseline_schema)

    bad_guardrail = copy.deepcopy(web_baseline)
    bad_guardrail["implementation_guardrails"]["no_hardcoded_authoritative_business_data"] = False
    assert_schema_invalid("platform hardcoded authoritative data guardrail cannot be disabled", bad_guardrail, baseline_schema)

    bad_none_visual = copy.deepcopy(web_binding)
    bad_none_visual["visual_references"]["approved_reference_paths"] = ["fake.png"]
    assert_schema_invalid("visual mode none rejects reference paths", bad_none_visual, binding_schema)

    bad_optional_visual = copy.deepcopy(web_binding)
    bad_optional_visual["visual_references"] = {"mode": "approved_optional", "approved_reference_paths": []}
    assert_schema_invalid("approved_optional requires at least one reference", bad_optional_visual, binding_schema)

    missing_optional_file = copy.deepcopy(web_binding)
    missing_optional_file["visual_references"] = {
        "mode": "approved_optional",
        "approved_reference_paths": ["does/not/exist.png"],
    }
    expect_semantic_failure("approved visual reference path must exist", missing_optional_file, web_baseline, inventory, openapi)

    wrong_namespace = copy.deepcopy(web_binding)
    wrong_namespace["inventory_ids"] = ["APP-999"]
    assert_schema_invalid("web slice binding rejects APP inventory", wrong_namespace, binding_schema)

    wrong_baseline = copy.deepcopy(web_binding)
    wrong_baseline["platform_baseline_ref"] = "templates/client-platform-architecture.android.example.json"
    expect_semantic_failure("slice cannot inherit incompatible platform baseline", wrong_baseline, android_baseline, inventory, openapi)

    unknown_inventory = copy.deepcopy(web_binding)
    unknown_inventory["inventory_ids"] = ["WEB-001", "WEB-999"]
    expect_semantic_failure("slice binding rejects unknown inventory ID", unknown_inventory, web_baseline, inventory, openapi)

    unknown_operation = copy.deepcopy(web_binding)
    unknown_operation["api_binding"]["operation_ids"] = ["loginUser", "missingOperation"]
    expect_semantic_failure("slice binding rejects unknown operationId", unknown_operation, web_baseline, inventory, openapi)

    invented_permission = copy.deepcopy(web_binding)
    invented_permission["api_binding"]["permissions"].append("invented.permission")
    expect_semantic_failure("slice binding rejects invented permission", invented_permission, web_baseline, inventory, openapi)

    bad_idempotency = copy.deepcopy(web_binding)
    bad_idempotency["idempotency"]["required_operations"] = ["missingOperation"]
    expect_semantic_failure("idempotency operation must belong to binding operationIds", bad_idempotency, web_baseline, inventory, openapi)

    android_with_web_id = copy.deepcopy(android_binding)
    android_with_web_id["inventory_ids"] = ["WEB-001"]
    assert_schema_invalid("Android binding rejects WEB inventory", android_with_web_id, binding_schema)


def validate_blueprint_references() -> None:
    blueprint = (ROOT / "BLUEPRINT.md").read_text(encoding="utf-8")
    documentation = (ROOT / "documentation/CLIENT_ARCHITECTURE_CONTRACT.md").read_text(encoding="utf-8")
    for token in (
        "Platform Client Architecture Baseline",
        "Slice Architecture Binding/Override",
        "client_architecture_ready",
    ):
        if token not in blueprint:
            fail(f"BLUEPRINT.md missing composed Client Architecture token: {token}")
    for token in (
        "Platform Client Architecture Baseline + Slice Architecture Binding",
        "visual_references.mode",
        "schemas/client-platform-architecture.schema.json",
    ):
        if token not in documentation:
            fail(f"CLIENT_ARCHITECTURE_CONTRACT.md missing token: {token}")
    print("PASS normative references: composed Client Architecture model")


def main() -> int:
    baseline_schema = load(BASELINE_SCHEMA_PATH)
    binding_schema = load(BINDING_SCHEMA_PATH)
    Draft202012Validator.check_schema(baseline_schema)
    Draft202012Validator.check_schema(binding_schema)
    print("PASS schema definitions: platform baseline + slice binding")

    web_baseline = load(WEB_BASELINE_PATH)
    android_baseline = load(ANDROID_BASELINE_PATH)
    web_binding = load(WEB_BINDING_PATH)
    android_binding = load(ANDROID_BINDING_PATH)
    inventory = load(INVENTORY_PATH)
    openapi = load(OPENAPI_PATH)

    assert_schema_valid("web platform baseline", web_baseline, baseline_schema)
    assert_schema_valid("Android platform baseline", android_baseline, baseline_schema)
    assert_schema_valid("web slice binding", web_binding, binding_schema)
    assert_schema_valid("Android slice binding", android_binding, binding_schema)

    assert_baseline_semantics("web platform baseline", web_baseline)
    assert_baseline_semantics("Android platform baseline", android_baseline)
    assert_binding_semantics(
        "web operational-core binding",
        web_binding,
        web_baseline,
        inventory=inventory,
        openapi=openapi,
    )
    assert_binding_semantics("Android example binding", android_binding, android_baseline, openapi=openapi)
    validate_functional_slice_binding(web_binding)

    run_negative_tests(
        web_baseline,
        android_baseline,
        web_binding,
        android_binding,
        baseline_schema,
        binding_schema,
        inventory,
        openapi,
    )
    validate_catalog_gate()
    validate_blueprint_references()

    print("Blueprint v0.5 client architecture validation: PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise
