#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
DEV_VERSION = "0.5.3-dev"

REQUIRED_TESTS = {
    "trial_duration",
    "exact_expiry_boundary",
    "entitlement_transitions",
    "valid_signature_acceptance",
    "tampered_payload_rejection",
    "tampered_signature_rejection",
    "wrong_device_rejection",
    "wrong_product_rejection",
    "unsupported_version_rejection",
    "production_test_key_separation",
    "restart_upgrade_persistence",
    "backup_does_not_clone_entitlement",
    "expired_read_only_data_safety",
    "issuer_customer_interoperability",
    "release_build_verification",
    "clock_rollback_behavior",
    "malformed_activation_rejection",
}

REQUIRED_CHECKS = {
    "requirements.mobile_licensing_decision",
    "licensing.profile_contract",
    "licensing.security_architecture",
    "licensing.private_key_isolation",
    "licensing.backup_separation",
    "licensing.issuer_boundary",
    "licensing.key_lifecycle",
    "licensing.automated_tests",
    "licensing.interoperability",
    "licensing.release_build",
}


def fail(message: str) -> None:
    raise AssertionError(message)


def load_json(path: str) -> dict:
    value = json.loads((ROOT / path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        fail(f"{path} must contain an object")
    return value


def load_yaml(path: str) -> dict:
    value = yaml.safe_load((ROOT / path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        fail(f"{path} must contain a mapping")
    return value


def expect_invalid(validator: Draft202012Validator, value: dict, label: str) -> None:
    errors = list(validator.iter_errors(value))
    if not errors:
        fail(f"expected invalid mobile licensing case to fail: {label}")
    print(f"PASS negative schema case: {label}")


def validate_profile_schema() -> None:
    schema = load_json("schemas/mobile-licensing.schema.json")
    Draft202012Validator.check_schema(schema)
    if f"/blueprint/{DEV_VERSION}/" not in schema.get("$id", ""):
        fail("mobile licensing schema must be version-pinned to 0.5.3-dev")
    validator = Draft202012Validator(schema)
    profile = load_yaml("templates/mobile-licensing.example.yaml")
    errors = list(validator.iter_errors(profile))
    if errors:
        fail("default mobile licensing template is invalid: " + "; ".join(e.message for e in errors))

    tests = profile.get("tests", {})
    if set(tests) != REQUIRED_TESTS or not all(tests.values()):
        fail("default licensing profile must acknowledge every mandatory test")

    if profile["strategy"] != "offline_signed_device_bound_trial":
        fail("default licensing strategy drifted")
    if profile["trial"]["days"] != 7 or profile["trial"]["expired_mode"] != "read_only_with_backup_export":
        fail("default trial semantics drifted")
    if profile["security"]["customer_private_signing_key_present"] is not False:
        fail("customer app must never declare a private production signing key")
    if profile["backup"]["license_entitlement_portable"] is not False:
        fail("portable backup must not clone device-bound entitlement")

    bad_private_key = copy.deepcopy(profile)
    bad_private_key["security"]["customer_private_signing_key_present"] = True
    expect_invalid(validator, bad_private_key, "customer private signing key present")

    bad_backup = copy.deepcopy(profile)
    bad_backup["backup"]["license_entitlement_portable"] = True
    expect_invalid(validator, bad_backup, "portable entitlement cloning")

    missing_negative_test = copy.deepcopy(profile)
    del missing_negative_test["tests"]["wrong_device_rejection"]
    expect_invalid(validator, missing_negative_test, "missing wrong-device test")

    custom_without_adr = copy.deepcopy(profile)
    custom_without_adr["strategy"] = "custom_documented"
    expect_invalid(validator, custom_without_adr, "custom strategy without ADR")

    print("PASS mobile licensing schema/default profile semantics")


def validate_project_applicability() -> None:
    schema = load_json("schemas/project.schema.json")
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    template = load_yaml("templates/project.example.yaml")
    errors = list(validator.iter_errors(template))
    if errors:
        fail("project template invalid under project schema: " + "; ".join(e.message for e in errors))

    if template.get("blueprint", {}).get("version") != DEV_VERSION:
        fail("project template must target 0.5.3-dev in this hardening branch")
    if "mobile_licensing" not in template.get("capabilities", {}):
        fail("Android project template must explicitly answer mobile_licensing")

    omitted = copy.deepcopy(template)
    omitted["capabilities"].pop("mobile_licensing", None)
    expect_invalid(validator, omitted, "android project omitted licensing decision")

    enabled_without_artifact = copy.deepcopy(template)
    enabled_without_artifact["capabilities"]["mobile_licensing"] = True
    enabled_without_artifact["artifact_locations"].pop("mobile_licensing", None)
    expect_invalid(validator, enabled_without_artifact, "enabled licensing without profile path")

    non_android = copy.deepcopy(template)
    non_android["capabilities"]["android"] = False
    non_android["capabilities"].pop("mobile_licensing", None)
    errors = list(validator.iter_errors(non_android))
    if errors:
        fail("non-Android project must not be forced to declare mobile licensing")

    print("PASS project-level licensing applicability semantics")


def validate_catalog_and_workflows() -> None:
    checks = load_yaml("catalog/checks.yaml")
    check_ids = {item.get("id") for item in checks.get("checks", [])}
    missing = REQUIRED_CHECKS - check_ids
    if missing:
        fail(f"missing mobile licensing checks: {sorted(missing)}")

    gates = load_yaml("catalog/gates.yaml")
    gate = next((g for g in gates.get("gates", []) if g.get("id") == "mobile_licensing_ready"), None)
    if not gate:
        fail("mobile_licensing_ready gate missing")
    if gate.get("applicability_capability") != "mobile_licensing":
        fail("mobile_licensing_ready must be conditional on mobile_licensing capability")
    if not REQUIRED_CHECKS.issubset(set(gate.get("require_all", []))):
        fail("mobile_licensing_ready must require all licensing checks")

    skills = load_yaml("catalog/skills.yaml")
    spec = skills.get("registry", {}).get("dev-mobile-licensing")
    if not spec or spec.get("status") != "materialized":
        fail("dev-mobile-licensing must be materialized")
    conditional = skills.get("categories", {}).get("mobile_licensing", {}).get("conditional_on", {})
    if conditional.get("mobile_licensing") is not True:
        fail("mobile licensing skill category must load only when capability is true")

    for workflow_path in ("workflows/greenfield.yaml", "workflows/brownfield.yaml"):
        workflow = load_yaml(workflow_path)
        capability = workflow.get("conditional_capabilities", {}).get("mobile_licensing", {})
        if capability.get("applicability") != "CONDITIONAL":
            fail(f"{workflow_path} missing conditional mobile licensing branch")
        if capability.get("decision_required_when", {}).get("android") is not True:
            fail(f"{workflow_path} must require explicit licensing decision for Android")
        if capability.get("enabled_when", {}).get("mobile_licensing") is not True:
            fail(f"{workflow_path} licensing branch enable condition drifted")
        if capability.get("exit_gate") != "mobile_licensing_ready":
            fail(f"{workflow_path} must exit licensing branch through mobile_licensing_ready")

    print("PASS licensing catalogs/workflow semantics")


def main() -> int:
    validate_profile_schema()
    validate_project_applicability()
    validate_catalog_and_workflows()
    print("PASS Blueprint 0.5.3-dev optional mobile licensing validation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
