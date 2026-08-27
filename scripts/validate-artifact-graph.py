#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
import pathlib
import sys
from typing import Any

import yaml
from jsonschema import Draft202012Validator, FormatChecker

ROOT = pathlib.Path(__file__).resolve().parents[1]
FIXTURE_ROOT = ROOT

SCHEMA_PAIRS = [
    ("schemas/project.schema.json", "templates/project.v0.5-dev.example.yaml"),
    ("schemas/status.schema.json", "templates/status.v0.5-dev.example.yaml"),
    ("schemas/interface-inventory.schema.json", "templates/interface-scope-baseline.example.json"),
    ("schemas/interface-inventory.schema.json", "templates/interface-inventory.example.json"),
    ("schemas/functional-interface-slice.schema.json", "templates/functional-interface-slice.example.json"),
    ("schemas/evidence.schema.json", "templates/evidence.example.json"),
    ("schemas/api-impact.schema.json", "templates/api-impact.example.json"),
]


def load(path: str | pathlib.Path) -> Any:
    p = pathlib.Path(path)
    if not p.is_absolute():
        p = ROOT / p
    text = p.read_text(encoding="utf-8")
    if p.suffix == ".json":
        return json.loads(text)
    if p.suffix in {".yaml", ".yml"}:
        return yaml.safe_load(text)
    raise ValueError(f"Unsupported file type: {p}")


def schema_errors(schema: dict, instance: Any) -> list[str]:
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    return [
        f"{'/'.join(map(str, e.path)) or '<root>'}: {e.message}"
        for e in sorted(validator.iter_errors(instance), key=lambda e: list(e.path))
    ]


def validate_schema_pair(schema_path: str, instance_path: str) -> None:
    errors = schema_errors(load(schema_path), load(instance_path))
    if errors:
        raise AssertionError(
            f"{instance_path} failed {schema_path}:\n" + "\n".join(f"- {e}" for e in errors)
        )


def openapi_operation_ids(document: dict) -> set[str]:
    result: set[str] = set()
    for path_item in document.get("paths", {}).values():
        if not isinstance(path_item, dict):
            continue
        for method, operation in path_item.items():
            if method.lower() not in {"get", "post", "put", "patch", "delete", "options", "head", "trace"}:
                continue
            if isinstance(operation, dict) and operation.get("operationId"):
                result.add(operation["operationId"])
    return result


def inventory_operation_ids(inventory: dict) -> set[str]:
    result: set[str] = set()
    for item in inventory["items"]:
        for data in item.get("data", []):
            result.update(data.get("operation_ids", []))
        for action in item.get("actions", []):
            result.update(action.get("operation_ids", []))
    return result


def evidence_ids(registry: dict) -> set[str]:
    values = [item["id"] for item in registry["evidence"]]
    if len(values) != len(set(values)):
        raise AssertionError("Evidence IDs must be unique")
    return set(values)


def referenced_evidence_ids(slice_doc: dict) -> set[str]:
    refs = set(slice_doc.get("evidence_ids", []))
    refs.update(slice_doc["definition_of_done"].get("evidence_ids", []))
    refs.update(slice_doc["visual_functional_review"].get("evidence_ids", []))
    refs.update(slice_doc["integration_qa"].get("evidence_ids", []))
    refs.update(slice_doc["human_acceptance"].get("evidence_ids", []))
    blocker = slice_doc.get("blocker")
    if blocker:
        refs.update(blocker.get("evidence_ids", []))
        if blocker.get("resolution"):
            refs.update(blocker["resolution"].get("evidence_ids", []))
    return refs


def validate_evidence_quality(registry: dict) -> None:
    file_backed = {
        "file", "openapi", "design_system", "mockup_manifest", "visual_asset",
        "functional_slice", "api_impact_report",
    }
    for item in registry["evidence"]:
        if item["type"] not in file_backed:
            continue
        value = item["value"]
        if "://" in value:
            continue
        path = ROOT / value
        if not path.is_file():
            raise AssertionError(f"{item['id']} references missing file evidence: {value}")
        expected = item.get("sha256")
        if expected:
            import hashlib
            actual = hashlib.sha256(path.read_bytes()).hexdigest()
            if actual.lower() != expected.lower():
                raise AssertionError(f"{item['id']} sha256 mismatch for {value}")


def validate_graph_documents(
    baseline: dict,
    inventory: dict,
    slices: list[dict],
    evidence: dict,
    status: dict,
    impacts: list[dict],
    openapi: dict,
    *,
    check_files: bool = True,
) -> None:
    if baseline.get("maturity") != "SCOPE_BASELINE":
        raise AssertionError("Interface Scope Baseline must use maturity SCOPE_BASELINE")
    if inventory.get("maturity") != "EXECUTABLE_INVENTORY":
        raise AssertionError("Executable inventory must use maturity EXECUTABLE_INVENTORY")

    baseline_ids = {item["id"] for item in baseline["items"]}
    final_items = {item["id"]: item for item in inventory["items"]}
    reconciliation = {item["baseline_id"]: item for item in inventory.get("baseline_reconciliation", [])}
    if set(reconciliation) != baseline_ids:
        raise AssertionError("Executable inventory must reconcile every baseline interface ID")
    for interface_id, disposition in reconciliation.items():
        if disposition["disposition"] == "COMMITTED" and interface_id not in final_items:
            raise AssertionError(f"Committed baseline interface missing from executable inventory: {interface_id}")

    openapi_ids = openapi_operation_ids(openapi)
    bound_ids = inventory_operation_ids(inventory)
    unknown_inventory_ops = sorted(bound_ids - openapi_ids)
    if unknown_inventory_ops:
        raise AssertionError(f"Inventory references unknown OpenAPI operationIds: {unknown_inventory_ops}")

    for item in inventory["items"]:
        if not item.get("slice_id"):
            raise AssertionError(f"{item['id']} missing slice_id in executable inventory")
        if "dependencies" not in item:
            raise AssertionError(f"{item['id']} missing dependencies in executable inventory")
        for dep in item["dependencies"]:
            if dep not in final_items:
                raise AssertionError(f"{item['id']} depends on missing interface {dep}")
        for data in item.get("data", []):
            if data["source"] == "api" and not data.get("operation_ids"):
                raise AssertionError(f"{item['id']} API data '{data['name']}' lacks operationId binding")
        for action in item.get("actions", []):
            if action.get("permission") and action["permission"] not in item.get("permissions", []):
                raise AssertionError(
                    f"{item['id']} action '{action['name']}' permission is absent from interface permissions"
                )
            if action["kind"] in {"read", "create", "update", "delete", "transition"} and action["source_classification"] != "PROPOSED":
                if not action.get("operation_ids"):
                    raise AssertionError(f"{item['id']} server action '{action['name']}' lacks operationId binding")

    slice_key = {(item["id"], item["platform"]): item for item in slices}
    if len(slice_key) != len(slices):
        raise AssertionError("Functional slice id+platform keys must be unique")

    known_evidence = evidence_ids(evidence)
    for slice_doc in slices:
        expected_prefix = "WEB-" if slice_doc["platform"] == "web" else "APP-"
        for inventory_id in slice_doc["inventory_ids"]:
            if inventory_id not in final_items:
                raise AssertionError(f"{slice_doc['id']} references missing inventory ID {inventory_id}")
            if not inventory_id.startswith(expected_prefix):
                raise AssertionError(f"{slice_doc['id']} crosses platform namespace with {inventory_id}")
            if final_items[inventory_id].get("slice_id") != slice_doc["id"]:
                raise AssertionError(f"{inventory_id} is not assigned to slice {slice_doc['id']}")
        slice_ops = set(slice_doc["api_binding"]["operation_ids"])
        if not slice_ops.issubset(openapi_ids):
            raise AssertionError(f"{slice_doc['id']} references unknown OpenAPI operationIds")
        interface_ops = set()
        for inventory_id in slice_doc["inventory_ids"]:
            interface = final_items[inventory_id]
            for data in interface.get("data", []):
                interface_ops.update(data.get("operation_ids", []))
            for action in interface.get("actions", []):
                interface_ops.update(action.get("operation_ids", []))
        if not slice_ops.issubset(interface_ops):
            raise AssertionError(f"{slice_doc['id']} operationIds are not bound by its inventory interfaces")
        missing_evidence = referenced_evidence_ids(slice_doc) - known_evidence
        if missing_evidence:
            raise AssertionError(f"{slice_doc['id']} references missing evidence IDs: {sorted(missing_evidence)}")
        blocker = slice_doc.get("blocker")
        if blocker and not blocker["resolved"] and slice_doc["lifecycle_status"] == "ACCEPTED":
            raise AssertionError("Unresolved BLOCKED_BY_API cannot coexist with ACCEPTED")

    for gate in status.get("scoped_gates", []):
        key = (gate["scope_id"], gate.get("platform"))
        if gate["scope"] == "interface_slice_platform" and key not in slice_key:
            raise AssertionError(f"Scoped gate references unknown slice/platform: {key}")
        if gate["scope"] == "interface_slice" and not any(sid == gate["scope_id"] for sid, _ in slice_key):
            raise AssertionError(f"Scoped gate references unknown slice: {gate['scope_id']}")
        missing = set(gate.get("evidence_ids", [])) - known_evidence
        if missing:
            raise AssertionError(f"Scoped gate references missing evidence: {sorted(missing)}")

    for impact in impacts:
        changed = set(impact["changed_operation_ids"])
        if not changed.issubset(openapi_ids):
            raise AssertionError(f"{impact['change_id']} references unknown changed operationIds")
        for affected in impact["affected_slices"]:
            key = (affected["id"], affected["platform"])
            if key not in slice_key:
                raise AssertionError(f"{impact['change_id']} references unknown affected slice {key}")
            if impact["classification"] == "operation_local":
                if not changed.intersection(slice_key[key]["api_binding"]["operation_ids"]):
                    raise AssertionError(
                        f"{impact['change_id']} operation-local change does not intersect affected slice {key}"
                    )
        missing = set(impact["evidence_ids"]) - known_evidence
        if missing:
            raise AssertionError(f"{impact['change_id']} references missing evidence: {sorted(missing)}")

    if check_files:
        validate_evidence_quality(evidence)


def expect_failure(label: str, mutator) -> None:
    baseline = load(ROOT / "templates/interface-scope-baseline.example.json")
    inventory = load(ROOT / "templates/interface-inventory.example.json")
    slice_doc = load(ROOT / "templates/functional-interface-slice.example.json")
    evidence = load(ROOT / "templates/evidence.example.json")
    status = load(ROOT / "templates/status.v0.5-dev.example.yaml")
    impact = load(ROOT / "templates/api-impact.example.json")
    openapi = load(ROOT / "tests/fixtures/artifact-graph/openapi.yaml")
    docs = {
        "baseline": copy.deepcopy(baseline),
        "inventory": copy.deepcopy(inventory),
        "slice": copy.deepcopy(slice_doc),
        "evidence": copy.deepcopy(evidence),
        "status": copy.deepcopy(status),
        "impact": copy.deepcopy(impact),
        "openapi": copy.deepcopy(openapi),
    }
    mutator(docs)
    try:
        for schema_name, key in [
            ("schemas/interface-inventory.schema.json", "inventory"),
            ("schemas/functional-interface-slice.schema.json", "slice"),
            ("schemas/api-impact.schema.json", "impact"),
        ]:
            errors = schema_errors(load(schema_name), docs[key])
            if errors:
                raise AssertionError(errors[0])
        validate_graph_documents(
            docs["baseline"], docs["inventory"], [docs["slice"]], docs["evidence"],
            docs["status"], [docs["impact"]], docs["openapi"], check_files=False
        )
    except AssertionError:
        print(f"PASS negative: {label}")
        return
    raise AssertionError(f"Negative fixture unexpectedly passed: {label}")


def main() -> int:
    for schema_path, instance_path in SCHEMA_PAIRS:
        validate_schema_pair(schema_path, instance_path)
        print(f"PASS schema: {instance_path}")

    baseline = load(ROOT / "templates/interface-scope-baseline.example.json")
    inventory = load(ROOT / "templates/interface-inventory.example.json")
    slice_doc = load(ROOT / "templates/functional-interface-slice.example.json")
    evidence = load(ROOT / "templates/evidence.example.json")
    status = load(ROOT / "templates/status.v0.5-dev.example.yaml")
    impact = load(ROOT / "templates/api-impact.example.json")
    openapi = load(ROOT / "tests/fixtures/artifact-graph/openapi.yaml")

    validate_graph_documents(
        baseline, inventory, [slice_doc], evidence, status, [impact], openapi
    )
    print("PASS Cross-Artifact Semantic Integrity fixture")

    expect_failure(
        "unknown inventory ID",
        lambda d: d["slice"].update({"inventory_ids": ["WEB-001", "WEB-999"]}),
    )
    expect_failure(
        "unknown operationId",
        lambda d: d["slice"]["api_binding"].update({"operation_ids": ["loginUser", "doesNotExist"]}),
    )
    expect_failure(
        "accepted without Integration QA",
        lambda d: d["slice"]["integration_qa"].update({"status": "PENDING"}),
    )
    def unresolved_blocker(d):
        d["slice"]["blocker"] = {
            "id": "BLK-API-001",
            "type": "BLOCKED_BY_API",
            "category": "operation",
            "description": "Required authoritative operation missing.",
            "opened_at": "2026-08-27T01:00:00Z",
            "last_valid_lifecycle_status": "IN_PROGRESS",
            "current_contract_ref": "tests/fixtures/artifact-graph/openapi.yaml",
            "evidence_ids": ["EVD-FUNC-001"],
            "resolved": False,
            "resolution": None,
        }
    expect_failure("ACCEPTED with unresolved BLOCKED_BY_API", unresolved_blocker)
    expect_failure(
        "operation-local impact points to unrelated slice operation",
        lambda d: d["impact"].update({"changed_operation_ids": ["loginUser"], "affected_slices": [{"id":"operational-core","platform":"web"}]}) or d["slice"]["api_binding"].update({"operation_ids":["getDashboard"]}),
    )

    print("Blueprint v0.5 artifact graph validation: PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise
