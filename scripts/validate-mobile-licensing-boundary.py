#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
STABLE_VERSION = "0.5.3"
DEVELOPMENT_VERSION = "0.5.4-dev"
MATRIX_PATH = ROOT / "tests/fixtures/mobile-licensing-boundary/matrix.json"

REQUIRED_CASE_IDS = {
    "web-only-no-decision",
    "ios-native-no-decision",
    "ios-cross-platform-no-decision",
    "web-ios-cross-platform-no-decision",
    "android-native-disabled",
    "android-native-enabled",
    "android-cross-platform-disabled",
    "android-ios-native-disabled",
    "android-ios-cross-platform-disabled",
    "android-ios-cross-platform-enabled",
    "legacy-android-disabled",
    "android-native-missing-decision",
    "android-cross-platform-missing-decision",
    "android-ios-native-missing-decision",
    "android-ios-cross-platform-missing-decision",
    "legacy-android-missing-decision",
    "android-enabled-without-profile",
}

EXPECTED_POLICY = {
    "decision_required_when": {"android": True},
    "ios_alone_requires_decision": False,
    "cross_platform_changes_applicability": False,
    "enabled_profile_required": True,
}


def fail(message: str) -> None:
    raise AssertionError(message)


def load_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        fail(f"{path.relative_to(ROOT)} must contain an object")
    return value


def load_yaml(path: str) -> dict:
    value = yaml.safe_load((ROOT / path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        fail(f"{path} must contain a mapping")
    return value


def build_project_case(template: dict, case: dict) -> dict:
    project = copy.deepcopy(template)
    targets = set(case["targets"])

    capabilities = project["capabilities"]
    capabilities["web"] = "web" in targets
    capabilities["android"] = "android" in targets
    capabilities["ios"] = "ios" in targets
    capabilities["offline_mobile"] = False

    if case.get("legacy_omit_ios"):
        capabilities.pop("ios", None)

    strategy = case.get("mobile_strategy")
    has_mobile_target = "android" in targets or "ios" in targets
    if has_mobile_target:
        if strategy not in {"native", "cross_platform"}:
            fail(f"{case['id']} mobile target requires native or cross_platform strategy")
        project["mobile"] = {"strategy": strategy}
    else:
        if strategy is not None:
            fail(f"{case['id']} non-mobile case must not declare mobile strategy")
        project.pop("mobile", None)
        if "stack" in project:
            project["stack"]["mobile"] = None

    decision = case.get("mobile_licensing")
    if decision == "omit":
        capabilities.pop("mobile_licensing", None)
    elif isinstance(decision, bool):
        capabilities["mobile_licensing"] = decision
    else:
        fail(f"{case['id']} mobile_licensing must be true, false, or 'omit'")

    profile_path = case.get("profile_path")
    if profile_path:
        project["artifact_locations"]["mobile_licensing"] = "templates/mobile-licensing.example.yaml"
    else:
        project["artifact_locations"].pop("mobile_licensing", None)

    return project


def validate_matrix_contract(matrix: dict) -> list[dict]:
    if matrix.get("schema_version") != DEVELOPMENT_VERSION:
        fail(f"mobile licensing boundary matrix must declare {DEVELOPMENT_VERSION}")
    if matrix.get("policy") != EXPECTED_POLICY:
        fail("mobile licensing boundary policy drifted")

    cases = matrix.get("cases")
    if not isinstance(cases, list) or not cases:
        fail("mobile licensing boundary matrix must contain cases")

    ids = [case.get("id") for case in cases if isinstance(case, dict)]
    if len(ids) != len(cases) or any(not isinstance(case_id, str) or not case_id for case_id in ids):
        fail("every mobile licensing boundary case must have a non-empty id")
    if len(set(ids)) != len(ids):
        fail("mobile licensing boundary case ids must be unique")
    if set(ids) != REQUIRED_CASE_IDS:
        missing = sorted(REQUIRED_CASE_IDS - set(ids))
        extra = sorted(set(ids) - REQUIRED_CASE_IDS)
        fail(f"mobile licensing boundary matrix coverage drifted; missing={missing}; extra={extra}")

    valid_count = sum(1 for case in cases if case.get("expected") == "valid")
    invalid_count = sum(1 for case in cases if case.get("expected") == "invalid")
    if valid_count != 11 or invalid_count != 6:
        fail(f"mobile licensing boundary matrix must remain 11 valid / 6 invalid; got {valid_count}/{invalid_count}")

    for case in cases:
        expected = case.get("expected")
        if expected not in {"valid", "invalid"}:
            fail(f"{case['id']} expected must be valid or invalid")
        targets = case.get("targets")
        if not isinstance(targets, list) or not targets or not set(targets).issubset({"web", "android", "ios"}):
            fail(f"{case['id']} targets are invalid")
        if len(set(targets)) != len(targets):
            fail(f"{case['id']} targets must be unique")
        if expected == "invalid" and not case.get("expected_error"):
            fail(f"{case['id']} invalid case must declare expected_error")

    print("PASS mobile licensing boundary matrix contract: 11 valid / 6 invalid cases")
    return cases


def validate_workflow_boundary() -> None:
    for path in ("workflows/greenfield.yaml", "workflows/brownfield.yaml"):
        workflow = load_yaml(path)
        branch = workflow.get("conditional_capabilities", {}).get("mobile_licensing", {})
        if branch.get("decision_required_when") != {"android": True}:
            fail(f"{path} Mobile Licensing decision boundary must remain exactly Android-only")
    print("PASS workflow Mobile Licensing boundary remains exactly Android-only")


def validate_cases(cases: list[dict]) -> None:
    schema = load_json(ROOT / "schemas/project.schema.json")
    Draft202012Validator.check_schema(schema)
    if f"/blueprint/{DEVELOPMENT_VERSION}/" not in schema.get("$id", ""):
        fail("project schema must retain 0.5.4-dev provenance for boundary regression validation")

    validator = Draft202012Validator(schema)
    template = load_yaml("templates/project.example.yaml")

    for case in cases:
        project = build_project_case(template, case)
        errors = sorted(validator.iter_errors(project), key=lambda error: list(error.absolute_path))
        expected = case["expected"]

        if expected == "valid":
            if errors:
                fail(f"{case['id']} expected valid but failed: " + " | ".join(error.message for error in errors))
            if "android" in case["targets"] and case["mobile_licensing"] == "omit":
                fail(f"{case['id']} valid Android case must explicitly decide mobile_licensing")
            if "android" not in case["targets"] and case["mobile_licensing"] != "omit":
                fail(f"{case['id']} no-Android applicability proof must omit mobile_licensing")
            print(f"PASS valid licensing boundary case: {case['id']}")
            continue

        if not errors:
            fail(f"{case['id']} expected invalid but project schema accepted it")
        combined = " | ".join(error.message for error in errors)
        if case["expected_error"] not in combined:
            fail(
                f"{case['id']} failed for unexpected reason; "
                f"expected '{case['expected_error']}', got '{combined}'"
            )
        print(f"PASS invalid licensing boundary case: {case['id']}")

    print("PASS cross-platform strategy does not alter Mobile Licensing applicability")


def main() -> int:
    stable = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    development = (ROOT / "DEVELOPMENT_VERSION").read_text(encoding="utf-8").strip()
    if stable != STABLE_VERSION:
        fail(f"boundary validator requires VERSION={STABLE_VERSION}, got {stable}")
    if development != DEVELOPMENT_VERSION:
        fail(f"boundary validator requires DEVELOPMENT_VERSION={DEVELOPMENT_VERSION}, got {development}")

    matrix = load_json(MATRIX_PATH)
    cases = validate_matrix_contract(matrix)
    validate_workflow_boundary()
    validate_cases(cases)
    print("Blueprint v0.5.4-dev Mobile Licensing regression boundary: PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"FAIL: {exc}")
        raise SystemExit(1)
