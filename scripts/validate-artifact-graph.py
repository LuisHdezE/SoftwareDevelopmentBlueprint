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
PLATFORM_PREFIX = {"web": "WEB-", "android": "APP-", "ios": "IOS-"}

SCHEMA_PAIRS = [
    ("schemas/project.schema.json", "templates/project.example.yaml"),
    ("schemas/status.schema.json", "templates/status.example.yaml"),
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


def validate_schema_instance(schema_path: str, instance: Any, label: str) -> None:
    errors = schema_errors(load(schema_path), instance)
    if errors:
        raise AssertionError(
            f"{label} failed {schema_path}:\n" + "\n".join(f"- {e}" for e in errors)
        )


def validate_schema_pair(schema_path: str, instance_path: str) -> None:
    validate_schema_instance(schema_path, load(instance_path), instance_path)


def openapi_operation_ids(document: dict) -> set[str]:
    result: set[str] = set()
    for path_item in document.get("paths", {}).values():
        if not isinstance(path_item, dict):
            continue
        for method, operation in path_item.items():
            if (
                method.lower() in {"get", "post", "put", "patch", "delete", "options", "head", "trace"}
                and isinstance(operation, dict)
                and operation.get("operationId")
            ):
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


def evidence_index(registry: dict) -> dict[str, dict]:
    result: dict[str, dict] = {}
    for item in registry["evidence"]:
        if item["id"] in result:
            raise AssertionError(f"Evidence ID duplicated: {item['id']}")
        result[item["id"]] = item
    return result


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
        "file",
        "openapi",
        "design_system",
        "mockup_manifest",
        "visual_asset",
        "functional_slice",
        "api_impact_report",
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

            if hashlib.sha256(path.read_bytes()).hexdigest().lower() != expected.lower():
                raise AssertionError(f"{item['id']} sha256 mismatch for {value}")


def platform_prefix(platform: str) -> str:
    try:
        return PLATFORM_PREFIX[platform]
    except KeyError as exc:
        raise AssertionError(f"Unknown client platform: {platform}") from exc


def assert_platform_enabled(project: dict, platform: str, label: str) -> None:
    if project.get("capabilities", {}).get(platform) is not True:
        raise AssertionError(f"{label} materializes disabled project capability {platform}")


def assert_platform_ref(value: str, platform: str, label: str) -> None:
    if not value.startswith(platform_prefix(platform)):
        raise AssertionError(f"{label} crosses {platform} namespace with {value}")


def assert_evidence_platform(
    evidence_by_id: dict[str, dict], refs: set[str] | list[str], platform: str, label: str
) -> None:
    for evidence_id in refs:
        if evidence_id not in evidence_by_id:
            raise AssertionError(f"{label} references missing evidence {evidence_id}")
        scope_platform = evidence_by_id[evidence_id].get("scope", {}).get("platform")
        if scope_platform != platform:
            raise AssertionError(
                f"{label} requires {platform} evidence but {evidence_id} is scoped to {scope_platform!r}"
            )


def validate_graph_documents(
    project: dict,
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

    for document_name, document in (("baseline", baseline), ("inventory", inventory)):
        seen_ids: set[str] = set()
        for item in document["items"]:
            platform = item["platform"]
            assert_platform_enabled(project, platform, f"{document_name}:{item['id']}")
            assert_platform_ref(item["id"], platform, f"{document_name}:{item['id']}")
            if item["id"] in seen_ids:
                raise AssertionError(f"Duplicate {document_name} interface ID: {item['id']}")
            seen_ids.add(item["id"])
            navigation = item.get("navigation", {})
            for ref in navigation.get("entry_points", []):
                assert_platform_ref(ref, platform, f"{item['id']} navigation entry point")
            for ref in navigation.get("destinations", []):
                assert_platform_ref(ref, platform, f"{item['id']} navigation destination")
            for ref in item.get("dependencies", []):
                assert_platform_ref(ref, platform, f"{item['id']} dependency")

    baseline_ids = {item["id"] for item in baseline["items"]}
    final_items = {item["id"]: item for item in inventory["items"]}
    reconciliation = {
        item["baseline_id"]: item for item in inventory.get("baseline_reconciliation", [])
    }
    if set(reconciliation) != baseline_ids:
        raise AssertionError("Executable inventory must reconcile every baseline interface ID")
    for interface_id, disposition in reconciliation.items():
        if disposition["disposition"] == "COMMITTED" and interface_id not in final_items:
            raise AssertionError(
                f"Committed baseline interface missing from executable inventory: {interface_id}"
            )

    openapi_ids = openapi_operation_ids(openapi)
    unknown_inventory_ops = sorted(inventory_operation_ids(inventory) - openapi_ids)
    if unknown_inventory_ops:
        raise AssertionError(
            f"Inventory references unknown OpenAPI operationIds: {unknown_inventory_ops}"
        )

    for item in inventory["items"]:
        if not item.get("slice_id"):
            raise AssertionError(f"{item['id']} missing slice_id in executable inventory")
        if "dependencies" not in item:
            raise AssertionError(f"{item['id']} missing dependencies in executable inventory")
        for dep in item["dependencies"]:
            if dep not in final_items:
                raise AssertionError(f"{item['id']} depends on missing interface {dep}")
            if final_items[dep]["platform"] != item["platform"]:
                raise AssertionError(f"{item['id']} depends on foreign platform interface {dep}")
        for destination in item.get("navigation", {}).get("destinations", []):
            if destination not in final_items:
                raise AssertionError(f"{item['id']} navigates to missing interface {destination}")
            if final_items[destination]["platform"] != item["platform"]:
                raise AssertionError(
                    f"{item['id']} navigates to foreign platform interface {destination}"
                )
        for data in item.get("data", []):
            if data["source"] == "api" and not data.get("operation_ids"):
                raise AssertionError(
                    f"{item['id']} API data '{data['name']}' lacks operationId binding"
                )
        for action in item.get("actions", []):
            if action.get("permission") and action["permission"] not in item.get("permissions", []):
                raise AssertionError(
                    f"{item['id']} action '{action['name']}' permission is absent from interface permissions"
                )
            if (
                action["kind"] in {"read", "create", "update", "delete", "transition"}
                and action["source_classification"] != "PROPOSED"
                and not action.get("operation_ids")
            ):
                raise AssertionError(
                    f"{item['id']} server action '{action['name']}' lacks operationId binding"
                )

    evidence_by_id = evidence_index(evidence)
    for evidence_item in evidence["evidence"]:
        scope_platform = evidence_item.get("scope", {}).get("platform")
        if scope_platform:
            assert_platform_enabled(
                project, scope_platform, f"evidence:{evidence_item['id']}"
            )

    slice_key = {(item["id"], item["platform"]): item for item in slices}
    if len(slice_key) != len(slices):
        raise AssertionError("Functional slice id+platform keys must be unique")

    for slice_doc in slices:
        platform = slice_doc["platform"]
        assert_platform_enabled(project, platform, f"slice:{slice_doc['id']}")
        expected_prefix = platform_prefix(platform)
        for inventory_id in slice_doc["inventory_ids"]:
            if inventory_id not in final_items:
                raise AssertionError(
                    f"{slice_doc['id']} references missing inventory ID {inventory_id}"
                )
            if not inventory_id.startswith(expected_prefix):
                raise AssertionError(
                    f"{slice_doc['id']} crosses platform namespace with {inventory_id}"
                )
            if final_items[inventory_id]["platform"] != platform:
                raise AssertionError(
                    f"{slice_doc['id']} binds foreign platform inventory {inventory_id}"
                )
            if final_items[inventory_id].get("slice_id") != slice_doc["id"]:
                raise AssertionError(
                    f"{inventory_id} is not assigned to slice {slice_doc['id']}"
                )

        slice_ops = set(slice_doc["api_binding"]["operation_ids"])
        if not slice_ops.issubset(openapi_ids):
            raise AssertionError(f"{slice_doc['id']} references unknown OpenAPI operationIds")
        interface_ops: set[str] = set()
        for inventory_id in slice_doc["inventory_ids"]:
            interface = final_items[inventory_id]
            for data in interface.get("data", []):
                interface_ops.update(data.get("operation_ids", []))
            for action in interface.get("actions", []):
                interface_ops.update(action.get("operation_ids", []))
        if not slice_ops.issubset(interface_ops):
            raise AssertionError(
                f"{slice_doc['id']} operationIds are not bound by its inventory interfaces"
            )

        refs = referenced_evidence_ids(slice_doc)
        missing_evidence = refs - set(evidence_by_id)
        if missing_evidence:
            raise AssertionError(
                f"{slice_doc['id']} references missing evidence IDs: {sorted(missing_evidence)}"
            )
        assert_evidence_platform(
            evidence_by_id, refs, platform, f"slice:{slice_doc['id']}"
        )

        blocker = slice_doc.get("blocker")
        if blocker and not blocker["resolved"] and slice_doc["lifecycle_status"] == "ACCEPTED":
            raise AssertionError("Unresolved BLOCKED_BY_API cannot coexist with ACCEPTED")

    status_slice_keys: set[tuple[str, str]] = set()
    for status_slice in status.get("functional_slices", []):
        platform = status_slice["platform"]
        assert_platform_enabled(project, platform, f"status slice:{status_slice['id']}")
        key = (status_slice["id"], platform)
        if key not in slice_key:
            raise AssertionError(f"Status references unknown slice/platform: {key}")
        status_slice_keys.add(key)
    if status_slice_keys != set(slice_key):
        raise AssertionError("Status functional_slices must match the materialized slice/platform set")

    for blocker in status.get("blockers", []):
        platform = blocker["platform"]
        assert_platform_enabled(project, platform, f"status blocker:{blocker['id']}")
        key = (blocker["slice_id"], platform)
        if key not in slice_key:
            raise AssertionError(f"Status blocker references unknown slice/platform: {key}")

    for gate in status.get("scoped_gates", []):
        if gate["scope"] == "interface_slice_platform":
            platform = gate["platform"]
            assert_platform_enabled(project, platform, f"scoped gate:{gate['gate']}")
            key = (gate["scope_id"], platform)
            if key not in slice_key:
                raise AssertionError(f"Scoped gate references unknown slice/platform: {key}")
            assert_evidence_platform(
                evidence_by_id,
                gate.get("evidence_ids", []),
                platform,
                f"scoped gate:{gate['gate']}:{gate['scope_id']}:{platform}",
            )
        elif gate["scope"] == "interface_slice":
            if not any(sid == gate["scope_id"] for sid, _ in slice_key):
                raise AssertionError(
                    f"Scoped gate references unknown slice: {gate['scope_id']}"
                )
            missing = set(gate.get("evidence_ids", [])) - set(evidence_by_id)
            if missing:
                raise AssertionError(
                    f"Scoped gate references missing evidence: {sorted(missing)}"
                )

    for impact in impacts:
        changed = set(impact["changed_operation_ids"])
        if not changed.issubset(openapi_ids):
            raise AssertionError(
                f"{impact['change_id']} references unknown changed operationIds"
            )
        for affected in impact["affected_slices"]:
            platform = affected["platform"]
            assert_platform_enabled(
                project, platform, f"api impact:{impact['change_id']}"
            )
            key = (affected["id"], platform)
            if key not in slice_key:
                raise AssertionError(
                    f"{impact['change_id']} references unknown affected slice {key}"
                )
            if (
                impact["classification"] == "operation_local"
                and not changed.intersection(slice_key[key]["api_binding"]["operation_ids"])
            ):
                raise AssertionError(
                    f"{impact['change_id']} operation-local change does not intersect affected slice {key}"
                )
        missing = set(impact["evidence_ids"]) - set(evidence_by_id)
        if missing:
            raise AssertionError(
                f"{impact['change_id']} references missing evidence: {sorted(missing)}"
            )

    if check_files:
        validate_evidence_quality(evidence)


def fixture_docs() -> dict[str, Any]:
    return {
        "project": copy.deepcopy(load("templates/project.example.yaml")),
        "baseline": copy.deepcopy(load("templates/interface-scope-baseline.example.json")),
        "inventory": copy.deepcopy(load("templates/interface-inventory.example.json")),
        "slice": copy.deepcopy(load("templates/functional-interface-slice.example.json")),
        "evidence": copy.deepcopy(load("templates/evidence.example.json")),
        "status": copy.deepcopy(load("templates/status.example.yaml")),
        "impact": copy.deepcopy(load("templates/api-impact.example.json")),
        "openapi": copy.deepcopy(load("tests/fixtures/artifact-graph/openapi.yaml")),
    }


def validate_fixture_schemas(docs: dict[str, Any]) -> None:
    pairs = [
        ("schemas/project.schema.json", "project"),
        ("schemas/interface-inventory.schema.json", "baseline"),
        ("schemas/interface-inventory.schema.json", "inventory"),
        ("schemas/functional-interface-slice.schema.json", "slice"),
        ("schemas/evidence.schema.json", "evidence"),
        ("schemas/status.schema.json", "status"),
        ("schemas/api-impact.schema.json", "impact"),
    ]
    for schema_name, key in pairs:
        validate_schema_instance(schema_name, docs[key], key)


def remap_platform_fixture(docs: dict[str, Any], platform: str, *, enable_target: bool) -> None:
    prefix = platform_prefix(platform)
    mapping = {
        item["id"]: f"{prefix}{item['id'].split('-', 1)[1]}"
        for item in docs["baseline"]["items"]
    }
    for key in ("baseline", "inventory"):
        docs[key]["schema_version"] = "0.5.4-dev"
        for item in docs[key]["items"]:
            old_id = item["id"]
            item["id"] = mapping[old_id]
            item["platform"] = platform
            navigation = item.get("navigation", {})
            navigation["entry_points"] = [mapping.get(value, value) for value in navigation.get("entry_points", [])]
            navigation["destinations"] = [mapping.get(value, value) for value in navigation.get("destinations", [])]
            if "dependencies" in item:
                item["dependencies"] = [mapping.get(value, value) for value in item["dependencies"]]
        for reconciliation in docs[key].get("baseline_reconciliation", []):
            reconciliation["baseline_id"] = mapping.get(
                reconciliation["baseline_id"], reconciliation["baseline_id"]
            )

    docs["slice"]["schema_version"] = "0.5.4-dev"
    docs["slice"]["platform"] = platform
    docs["slice"]["inventory_ids"] = [mapping[value] for value in docs["slice"]["inventory_ids"]]
    docs["slice"]["client_architecture"]["artifact"] = (
        f"templates/client-architecture.{platform}.example.json"
    )

    docs["evidence"]["schema_version"] = "0.5.4-dev"
    for item in docs["evidence"]["evidence"]:
        if item.get("scope", {}).get("platform"):
            item["scope"]["platform"] = platform

    docs["status"]["blueprint_version"] = "0.5.4-dev"
    for item in docs["status"].get("functional_slices", []):
        item["platform"] = platform
    for item in docs["status"].get("scoped_gates", []):
        if "platform" in item:
            item["platform"] = platform
    for item in docs["status"].get("blockers", []):
        item["platform"] = platform

    docs["impact"]["schema_version"] = "0.5.4-dev"
    for affected in docs["impact"]["affected_slices"]:
        affected["platform"] = platform

    if enable_target:
        docs["project"]["capabilities"][platform] = True


def run_fixture(docs: dict[str, Any], *, check_files: bool = False) -> None:
    validate_fixture_schemas(docs)
    validate_graph_documents(
        docs["project"],
        docs["baseline"],
        docs["inventory"],
        [docs["slice"]],
        docs["evidence"],
        docs["status"],
        [docs["impact"]],
        docs["openapi"],
        check_files=check_files,
    )


def expect_failure(label: str, mutator) -> None:
    docs = fixture_docs()
    mutator(docs)
    try:
        run_fixture(docs, check_files=False)
    except AssertionError:
        print(f"PASS negative: {label}")
        return
    raise AssertionError(f"Negative fixture unexpectedly passed: {label}")


def main() -> int:
    for schema_path, instance_path in SCHEMA_PAIRS:
        validate_schema_pair(schema_path, instance_path)
        print(f"PASS schema: {instance_path}")

    docs = fixture_docs()
    run_fixture(docs, check_files=True)
    print("PASS Cross-Artifact Semantic Integrity web fixture")

    ios_docs = fixture_docs()
    remap_platform_fixture(ios_docs, "ios", enable_target=True)
    run_fixture(ios_docs, check_files=False)
    print("PASS Cross-Artifact Semantic Integrity iOS fixture")

    expect_failure(
        "unknown inventory ID",
        lambda d: d["slice"].update({"inventory_ids": ["WEB-001", "WEB-999"]}),
    )
    expect_failure(
        "unknown operationId",
        lambda d: d["slice"]["api_binding"].update(
            {"operation_ids": ["loginUser", "doesNotExist"]}
        ),
    )
    expect_failure(
        "accepted without Integration QA",
        lambda d: d["slice"]["integration_qa"].update({"status": "PENDING"}),
    )

    def unresolved_blocker(d: dict[str, Any]) -> None:
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

    def unrelated_operation_impact(d: dict[str, Any]) -> None:
        d["impact"].update(
            {
                "changed_operation_ids": ["loginUser"],
                "affected_slices": [{"id": "operational-core", "platform": "web"}],
            }
        )
        d["slice"]["api_binding"].update({"operation_ids": ["getDashboard"]})

    expect_failure(
        "operation-local impact points to unrelated slice operation",
        unrelated_operation_impact,
    )

    def ios_disabled(d: dict[str, Any]) -> None:
        remap_platform_fixture(d, "ios", enable_target=False)

    expect_failure("ios=false rejects iOS artifacts", ios_disabled)

    def ios_gate_with_android_evidence(d: dict[str, Any]) -> None:
        remap_platform_fixture(d, "ios", enable_target=True)
        android_evidence = copy.deepcopy(
            next(item for item in d["evidence"]["evidence"] if item["id"] == "EVD-QA-001")
        )
        android_evidence["id"] = "EVD-ANDROID-QA"
        android_evidence["scope"]["platform"] = "android"
        d["evidence"]["evidence"].append(android_evidence)
        gate = next(
            item
            for item in d["status"]["scoped_gates"]
            if item["gate"] == "integration_qa_pass"
        )
        gate["evidence_ids"] = ["EVD-ANDROID-QA"]

    expect_failure(
        "Android evidence cannot satisfy iOS integration gate",
        ios_gate_with_android_evidence,
    )

    def ios_crosses_android_namespace(d: dict[str, Any]) -> None:
        remap_platform_fixture(d, "ios", enable_target=True)
        d["slice"]["inventory_ids"][0] = "APP-001"

    expect_failure("iOS slice rejects APP namespace", ios_crosses_android_namespace)

    def ios_accepted_without_qa(d: dict[str, Any]) -> None:
        remap_platform_fixture(d, "ios", enable_target=True)
        d["slice"]["integration_qa"]["status"] = "PENDING"

    expect_failure(
        "iOS ACCEPTED requires iOS integration QA",
        ios_accepted_without_qa,
    )

    print("Blueprint v0.5.4-dev artifact graph validation: PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise
