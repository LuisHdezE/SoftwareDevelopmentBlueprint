#!/usr/bin/env python3
from __future__ import annotations

import copy
import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
MATRIX_PATH = ROOT / "tests/fixtures/platform-matrix/matrix.json"
GRAPH_VALIDATOR_PATH = ROOT / "scripts/validate-artifact-graph.py"
PROJECT_SCHEMA_PATH = ROOT / "schemas/project.schema.json"
PROJECT_TEMPLATE_PATH = ROOT / "templates/project.example.yaml"
DEVELOPMENT_VERSION = "0.5.4-dev"

REQUIRED_POSITIVE = {
    "web-only",
    "android-native",
    "ios-native",
    "android-ios-native",
    "web-android-ios-native",
    "legacy-compatible-android",
    "cross-platform-android-only",
    "cross-platform-ios-only",
    "cross-platform-both",
    "api-backed-offline-android",
    "api-backed-offline-ios",
}

REQUIRED_NEGATIVE = {
    "ios-disabled-artifacts",
    "ios-slice-with-android-baseline",
    "ios-slice-with-android-evidence",
    "ios-accepted-without-ios-integration-qa",
    "invalid-mobile-strategy",
    "invalid-ios-namespace",
    "cross-platform-does-not-auto-enable-ios",
    "shared-gate-evidence-across-platforms",
    "offline-without-openapi",
}


def fail(message: str) -> None:
    raise AssertionError(message)


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        fail(f"{path.relative_to(ROOT)} must contain an object")
    return value


def load_graph_validator() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "blueprint_artifact_graph_validator", GRAPH_VALIDATOR_PATH
    )
    if spec is None or spec.loader is None:
        fail("cannot load artifact graph validator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate_matrix_contract(matrix: dict[str, Any]) -> None:
    if matrix.get("schema_version") != DEVELOPMENT_VERSION:
        fail(f"platform matrix must declare schema_version={DEVELOPMENT_VERSION}")

    positives = matrix.get("positive_cases")
    negatives = matrix.get("negative_cases")
    if not isinstance(positives, list) or not isinstance(negatives, list):
        fail("platform matrix positive_cases and negative_cases must be arrays")

    positive_ids = {item.get("id") for item in positives if isinstance(item, dict)}
    negative_ids = {item.get("id") for item in negatives if isinstance(item, dict)}
    if positive_ids != REQUIRED_POSITIVE:
        fail(
            "platform matrix positive coverage drifted: "
            f"expected={sorted(REQUIRED_POSITIVE)} actual={sorted(positive_ids)}"
        )
    if negative_ids != REQUIRED_NEGATIVE:
        fail(
            "platform matrix negative coverage drifted: "
            f"expected={sorted(REQUIRED_NEGATIVE)} actual={sorted(negative_ids)}"
        )

    for case in positives:
        if not isinstance(case, dict):
            fail("positive matrix cases must be objects")
        targets = case.get("targets")
        graph_platforms = case.get("graph_platforms")
        if not isinstance(targets, list) or not targets:
            fail(f"{case.get('id')} must declare non-empty targets")
        if not isinstance(graph_platforms, list) or not graph_platforms:
            fail(f"{case.get('id')} must declare non-empty graph_platforms")
        if not set(graph_platforms).issubset({"web", "android", "ios"}):
            fail(f"{case.get('id')} declares an unknown graph platform")
        if not set(graph_platforms).issubset(set(targets)):
            fail(f"{case.get('id')} materializes a platform outside declared targets")
        strategy = case.get("mobile_strategy")
        has_mobile = bool({"android", "ios"} & set(targets))
        if has_mobile and strategy not in {"native", "cross_platform"}:
            fail(f"{case.get('id')} mobile targets require native or cross_platform strategy")
        if not has_mobile and strategy is not None:
            fail(f"{case.get('id')} web-only case must not declare mobile strategy")

    for case in negatives:
        if not isinstance(case, dict):
            fail("negative matrix cases must be objects")
        if not isinstance(case.get("scenario"), str) or not case["scenario"]:
            fail(f"{case.get('id')} must declare a negative scenario")
        if not isinstance(case.get("expected_message"), str) or not case["expected_message"]:
            fail(f"{case.get('id')} must declare expected_message")

    print(
        "PASS platform matrix contract: "
        f"{len(positives)} positive / {len(negatives)} negative cases"
    )


def load_project_template(graph: ModuleType) -> dict[str, Any]:
    template = graph.load(PROJECT_TEMPLATE_PATH)
    if not isinstance(template, dict):
        fail("project template must contain a mapping")
    return template


def project_for_case(graph: ModuleType, case: dict[str, Any]) -> dict[str, Any]:
    project = copy.deepcopy(load_project_template(graph))
    targets = set(case["targets"])

    for platform in ("web", "android", "ios"):
        project["capabilities"][platform] = platform in targets

    project["capabilities"]["offline_mobile"] = bool(case.get("offline_mobile", False))

    if "android" in targets:
        project["capabilities"]["mobile_licensing"] = False
    else:
        project["capabilities"].pop("mobile_licensing", None)

    mobile_targets = targets & {"android", "ios"}
    if mobile_targets:
        project["mobile"] = {"strategy": case["mobile_strategy"]}
        if case["mobile_strategy"] == "cross_platform":
            project["stack"]["mobile"] = "shared-client"
        elif mobile_targets == {"ios"}:
            project["stack"]["mobile"] = "swift"
        else:
            project["stack"]["mobile"] = "kotlin"
    else:
        project.pop("mobile", None)
        project["stack"]["mobile"] = None

    if case.get("legacy_omit_ios"):
        project["capabilities"].pop("ios", None)

    return project


def assert_project_valid(
    validator: Draft202012Validator, project: dict[str, Any], label: str
) -> None:
    errors = list(validator.iter_errors(project))
    if errors:
        fail(
            f"expected valid project case to pass: {label}: "
            + "; ".join(error.message for error in errors)
        )


def assert_project_invalid(
    validator: Draft202012Validator,
    project: dict[str, Any],
    label: str,
    expected_message: str,
) -> None:
    errors = list(validator.iter_errors(project))
    if not errors:
        fail(f"expected invalid project case to fail: {label}")
    text = "; ".join(error.message for error in errors)
    if expected_message not in text:
        fail(
            f"{label} failed for an unexpected reason; "
            f"expected message containing {expected_message!r}, got {text!r}"
        )


def replace_exact(value: Any, mapping: dict[str, str]) -> Any:
    if isinstance(value, str):
        return mapping.get(value, value)
    if isinstance(value, list):
        return [replace_exact(item, mapping) for item in value]
    if isinstance(value, dict):
        return {key: replace_exact(item, mapping) for key, item in value.items()}
    return value


def namespace_fixture_ids(docs: dict[str, Any], platform: str) -> dict[str, Any]:
    evidence_mapping = {
        item["id"]: f"EVD-{platform.upper()}-{item['id'][4:]}"
        for item in docs["evidence"]["evidence"]
    }
    impact_id = docs["impact"]["change_id"]
    mapping = dict(evidence_mapping)
    impact_number = {"web": "101", "android": "201", "ios": "301"}[platform]
    mapping[impact_id] = f"API-IMPACT-{impact_number}"
    return replace_exact(docs, mapping)


def single_platform_docs(
    graph: ModuleType, project: dict[str, Any], platform: str
) -> dict[str, Any]:
    docs = graph.fixture_docs()
    graph.remap_platform_fixture(docs, platform, enable_target=True)
    docs["project"] = copy.deepcopy(project)
    docs = namespace_fixture_ids(docs, platform)
    return docs


def combine_platform_docs(
    graph: ModuleType, project: dict[str, Any], platforms: list[str]
) -> dict[str, Any]:
    parts = [single_platform_docs(graph, project, platform) for platform in platforms]
    first = copy.deepcopy(parts[0])

    baseline = first["baseline"]
    baseline["schema_version"] = DEVELOPMENT_VERSION
    baseline["items"] = []
    baseline["baseline_reconciliation"] = []

    inventory = first["inventory"]
    inventory["schema_version"] = DEVELOPMENT_VERSION
    inventory["items"] = []
    inventory["baseline_reconciliation"] = []

    evidence = first["evidence"]
    evidence["schema_version"] = DEVELOPMENT_VERSION
    evidence["evidence"] = []

    status = first["status"]
    status["blueprint_version"] = DEVELOPMENT_VERSION
    status["functional_slices"] = []
    status["scoped_gates"] = []
    status["blockers"] = []
    status["api_impacts"] = []
    status["artifacts"] = []

    slices: list[dict[str, Any]] = []
    impacts: list[dict[str, Any]] = []

    for part in parts:
        baseline["items"].extend(copy.deepcopy(part["baseline"]["items"]))
        baseline["baseline_reconciliation"].extend(
            copy.deepcopy(part["baseline"].get("baseline_reconciliation", []))
        )
        inventory["items"].extend(copy.deepcopy(part["inventory"]["items"]))
        inventory["baseline_reconciliation"].extend(
            copy.deepcopy(part["inventory"].get("baseline_reconciliation", []))
        )
        evidence["evidence"].extend(copy.deepcopy(part["evidence"]["evidence"]))
        status["functional_slices"].extend(
            copy.deepcopy(part["status"].get("functional_slices", []))
        )
        status["scoped_gates"].extend(
            copy.deepcopy(part["status"].get("scoped_gates", []))
        )
        status["blockers"].extend(copy.deepcopy(part["status"].get("blockers", [])))
        status["api_impacts"].extend(copy.deepcopy(part["status"].get("api_impacts", [])))
        status["artifacts"].extend(copy.deepcopy(part["status"].get("artifacts", [])))
        slices.append(copy.deepcopy(part["slice"]))
        impacts.append(copy.deepcopy(part["impact"]))

    return {
        "project": copy.deepcopy(project),
        "baseline": baseline,
        "inventory": inventory,
        "slices": slices,
        "evidence": evidence,
        "status": status,
        "impacts": impacts,
        "openapi": copy.deepcopy(first["openapi"]),
    }


def validate_combined_schemas(graph: ModuleType, docs: dict[str, Any]) -> None:
    graph.validate_schema_instance("schemas/project.schema.json", docs["project"], "project")
    graph.validate_schema_instance(
        "schemas/interface-inventory.schema.json", docs["baseline"], "baseline"
    )
    graph.validate_schema_instance(
        "schemas/interface-inventory.schema.json", docs["inventory"], "inventory"
    )
    graph.validate_schema_instance("schemas/evidence.schema.json", docs["evidence"], "evidence")
    graph.validate_schema_instance("schemas/status.schema.json", docs["status"], "status")
    for index, slice_doc in enumerate(docs["slices"], start=1):
        graph.validate_schema_instance(
            "schemas/functional-interface-slice.schema.json",
            slice_doc,
            f"slice[{index}]",
        )
    for index, impact in enumerate(docs["impacts"], start=1):
        graph.validate_schema_instance(
            "schemas/api-impact.schema.json", impact, f"impact[{index}]"
        )


def run_combined_graph(graph: ModuleType, docs: dict[str, Any]) -> None:
    validate_combined_schemas(graph, docs)
    graph.validate_graph_documents(
        docs["project"],
        docs["baseline"],
        docs["inventory"],
        docs["slices"],
        docs["evidence"],
        docs["status"],
        docs["impacts"],
        docs["openapi"],
        check_files=False,
    )


def run_positive_cases(
    graph: ModuleType,
    project_validator: Draft202012Validator,
    matrix: dict[str, Any],
) -> None:
    for case in matrix["positive_cases"]:
        project = project_for_case(graph, case)
        assert_project_valid(project_validator, project, case["id"])
        docs = combine_platform_docs(graph, project, case["graph_platforms"])
        run_combined_graph(graph, docs)

        enabled = {
            platform
            for platform in ("web", "android", "ios")
            if project.get("capabilities", {}).get(platform) is True
        }
        if set(case["graph_platforms"]) - enabled:
            fail(f"{case['id']} graph contains a disabled target")

        if case["mobile_strategy"] == "cross_platform":
            declared = set(case["targets"])
            actual = {
                platform
                for platform in ("android", "ios")
                if project.get("capabilities", {}).get(platform) is True
            }
            if actual != declared & {"android", "ios"}:
                fail(f"{case['id']} cross_platform strategy auto-enabled a target")

        print(f"PASS positive platform matrix case: {case['id']}")


def expect_graph_failure(
    graph: ModuleType,
    docs: dict[str, Any],
    label: str,
    expected_message: str,
) -> None:
    try:
        run_combined_graph(graph, docs)
    except AssertionError as exc:
        text = str(exc)
        if expected_message not in text:
            fail(
                f"{label} failed for an unexpected reason; "
                f"expected {expected_message!r}, got {text!r}"
            )
        print(f"PASS negative platform matrix case: {label}")
        return
    fail(f"negative platform matrix case unexpectedly passed: {label}")


def base_case(
    graph: ModuleType,
    *,
    targets: list[str],
    strategy: str | None,
    platforms: list[str],
    offline: bool = False,
) -> dict[str, Any]:
    case = {
        "id": "synthetic",
        "targets": targets,
        "mobile_strategy": strategy,
        "offline_mobile": offline,
        "graph_platforms": platforms,
    }
    project = project_for_case(graph, case)
    return combine_platform_docs(graph, project, platforms)


def run_negative_case(
    graph: ModuleType,
    project_validator: Draft202012Validator,
    case: dict[str, Any],
) -> None:
    scenario = case["scenario"]
    label = case["id"]
    expected = case["expected_message"]

    if scenario == "invalid_mobile_strategy":
        project_case = {
            "id": label,
            "targets": ["android"],
            "mobile_strategy": "cross_platform",
            "offline_mobile": False,
            "graph_platforms": ["android"],
        }
        project = project_for_case(graph, project_case)
        project["mobile"]["strategy"] = "hybrid_magic"
        assert_project_invalid(project_validator, project, label, expected)
        print(f"PASS negative platform matrix case: {label}")
        return

    if scenario == "offline_without_openapi":
        project_case = {
            "id": label,
            "targets": ["ios"],
            "mobile_strategy": "native",
            "offline_mobile": True,
            "graph_platforms": ["ios"],
        }
        project = project_for_case(graph, project_case)
        project["artifact_locations"].pop("openapi", None)
        assert_project_invalid(project_validator, project, label, expected)
        print(f"PASS negative platform matrix case: {label}")
        return

    if scenario == "ios_disabled_artifacts":
        docs = base_case(
            graph,
            targets=["web"],
            strategy=None,
            platforms=["web"],
        )
        ios_project = copy.deepcopy(docs["project"])
        ios_docs = single_platform_docs(graph, ios_project, "ios")
        combined = {
            "project": ios_project,
            "baseline": ios_docs["baseline"],
            "inventory": ios_docs["inventory"],
            "slices": [ios_docs["slice"]],
            "evidence": ios_docs["evidence"],
            "status": ios_docs["status"],
            "impacts": [ios_docs["impact"]],
            "openapi": ios_docs["openapi"],
        }
        expect_graph_failure(graph, combined, label, expected)
        return

    if scenario == "cross_platform_does_not_auto_enable_ios":
        docs = base_case(
            graph,
            targets=["android"],
            strategy="cross_platform",
            platforms=["android"],
        )
        project = copy.deepcopy(docs["project"])
        ios_docs = single_platform_docs(graph, project, "ios")
        combined = {
            "project": project,
            "baseline": ios_docs["baseline"],
            "inventory": ios_docs["inventory"],
            "slices": [ios_docs["slice"]],
            "evidence": ios_docs["evidence"],
            "status": ios_docs["status"],
            "impacts": [ios_docs["impact"]],
            "openapi": ios_docs["openapi"],
        }
        expect_graph_failure(graph, combined, label, expected)
        return

    if scenario == "ios_slice_with_android_baseline":
        docs = base_case(
            graph,
            targets=["android", "ios"],
            strategy="native",
            platforms=["android"],
        )
        slice_doc = docs["slices"][0]
        slice_doc["platform"] = "ios"
        slice_doc["inventory_ids"] = [
            item.replace("APP-", "IOS-") for item in slice_doc["inventory_ids"]
        ]
        expect_graph_failure(graph, docs, label, expected)
        return

    if scenario == "ios_slice_with_android_evidence":
        docs = base_case(
            graph,
            targets=["android", "ios"],
            strategy="native",
            platforms=["ios"],
        )
        qa_id = next(
            item["id"]
            for item in docs["evidence"]["evidence"]
            if item["type"] == "integration_qa"
        )
        qa = next(item for item in docs["evidence"]["evidence"] if item["id"] == qa_id)
        qa["scope"]["platform"] = "android"
        expect_graph_failure(graph, docs, label, expected)
        return

    if scenario == "ios_accepted_without_integration_qa":
        docs = base_case(
            graph,
            targets=["ios"],
            strategy="native",
            platforms=["ios"],
        )
        docs["slices"][0]["integration_qa"]["status"] = "PENDING"
        expect_graph_failure(graph, docs, label, expected)
        return

    if scenario == "invalid_ios_namespace":
        docs = base_case(
            graph,
            targets=["ios"],
            strategy="native",
            platforms=["ios"],
        )
        docs = replace_exact(docs, {"IOS-001": "APP-001"})
        expect_graph_failure(graph, docs, label, expected)
        return

    if scenario == "shared_gate_evidence_across_platforms":
        docs = base_case(
            graph,
            targets=["android", "ios"],
            strategy="cross_platform",
            platforms=["android", "ios"],
        )
        android_qa = next(
            item["id"]
            for item in docs["evidence"]["evidence"]
            if item["type"] == "integration_qa"
            and item.get("scope", {}).get("platform") == "android"
        )
        ios_gate = next(
            gate
            for gate in docs["status"]["scoped_gates"]
            if gate["gate"] == "integration_qa_pass" and gate.get("platform") == "ios"
        )
        ios_gate["evidence_ids"] = [android_qa]
        expect_graph_failure(graph, docs, label, expected)
        return

    fail(f"unsupported negative matrix scenario: {scenario}")


def validate_ci_contract() -> None:
    workflow = (ROOT / ".github/workflows/blueprint-platform-matrix-validation.yml").read_text(
        encoding="utf-8"
    )
    required_paths = [
        "VERSION",
        "DEVELOPMENT_VERSION",
        "scripts/validate-platform-matrix.py",
        "tests/fixtures/platform-matrix/**",
        "scripts/validate-artifact-graph.py",
        "schemas/project.schema.json",
        "schemas/status.schema.json",
        "schemas/evidence.schema.json",
        "schemas/api-impact.schema.json",
        "schemas/interface-inventory.schema.json",
        "schemas/functional-interface-slice.schema.json",
        "templates/project.example.yaml",
        "templates/status.example.yaml",
        "templates/evidence.example.json",
        "templates/api-impact.example.json",
        "templates/interface-scope-baseline.example.json",
        "templates/interface-inventory.example.json",
        "templates/functional-interface-slice.example.json",
    ]
    for path in required_paths:
        if path not in workflow:
            fail(f"platform matrix workflow does not watch {path}")
    if "python scripts/validate-platform-matrix.py" not in workflow:
        fail("platform matrix workflow does not execute the matrix validator")

    print("PASS platform matrix CI wiring")


def main() -> int:
    matrix = load_json(MATRIX_PATH)
    validate_matrix_contract(matrix)

    graph = load_graph_validator()
    project_schema = graph.load(PROJECT_SCHEMA_PATH)
    Draft202012Validator.check_schema(project_schema)
    project_validator = Draft202012Validator(project_schema)

    run_positive_cases(graph, project_validator, matrix)
    for case in matrix["negative_cases"]:
        run_negative_case(graph, project_validator, case)

    validate_ci_contract()
    print("Blueprint v0.5.4-dev platform matrix validation: PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
