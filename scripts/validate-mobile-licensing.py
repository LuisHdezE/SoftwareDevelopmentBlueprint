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

REQUIRED_TESTS = {
    "trial_duration", "exact_expiry_boundary", "entitlement_transitions",
    "valid_signature_acceptance", "tampered_payload_rejection",
    "tampered_signature_rejection", "wrong_device_rejection",
    "wrong_product_rejection", "unsupported_version_rejection",
    "production_test_key_separation", "restart_upgrade_persistence",
    "backup_does_not_clone_entitlement", "expired_read_only_data_safety",
    "issuer_customer_interoperability", "release_build_verification",
    "clock_rollback_behavior", "malformed_activation_rejection",
}
REQUIRED_CHECKS = {
    "requirements.mobile_licensing_decision", "licensing.profile_contract",
    "licensing.security_architecture", "licensing.private_key_isolation",
    "licensing.backup_separation", "licensing.issuer_boundary",
    "licensing.key_lifecycle", "licensing.automated_tests",
    "licensing.interoperability", "licensing.release_build",
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


def active_project_version() -> str:
    marker = ROOT / "DEVELOPMENT_VERSION"
    if not marker.exists():
        return STABLE_VERSION
    value = marker.read_text(encoding="utf-8").strip()
    if value != DEVELOPMENT_VERSION:
        fail(f"unexpected DEVELOPMENT_VERSION for mobile licensing compatibility validation: {value}")
    return DEVELOPMENT_VERSION


def expect_invalid(validator: Draft202012Validator, value: dict, label: str) -> None:
    if not list(validator.iter_errors(value)):
        fail(f"expected invalid mobile licensing case to fail: {label}")
    print(f"PASS negative schema case: {label}")


def validate_profile_schema() -> None:
    schema = load_json("schemas/mobile-licensing.schema.json")
    Draft202012Validator.check_schema(schema)
    if f"/blueprint/{STABLE_VERSION}/" not in schema.get("$id", ""):
        fail("mobile licensing schema must retain stable 0.5.3 provenance")
    validator = Draft202012Validator(schema)
    profile = load_yaml("templates/mobile-licensing.example.yaml")
    errors = list(validator.iter_errors(profile))
    if errors:
        fail("default mobile licensing template is invalid: " + "; ".join(e.message for e in errors))
    if profile.get("schema_version") != STABLE_VERSION:
        fail("mobile licensing template must retain stable 0.5.3 provenance")
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
    missing_test = copy.deepcopy(profile)
    del missing_test["tests"]["wrong_device_rejection"]
    expect_invalid(validator, missing_test, "missing wrong-device test")
    custom_without_adr = copy.deepcopy(profile)
    custom_without_adr["strategy"] = "custom_documented"
    expect_invalid(validator, custom_without_adr, "custom strategy without ADR")
    print("PASS stable mobile licensing schema/default profile semantics")


def validate_project_applicability() -> None:
    project_version = active_project_version()
    schema = load_json("schemas/project.schema.json")
    Draft202012Validator.check_schema(schema)
    if f"/blueprint/{project_version}/" not in schema.get("$id", ""):
        fail(f"project schema must use active project contract provenance {project_version}")
    validator = Draft202012Validator(schema)
    template = load_yaml("templates/project.example.yaml")
    errors = list(validator.iter_errors(template))
    if errors:
        fail("project template invalid: " + "; ".join(e.message for e in errors))
    if template.get("blueprint", {}).get("version") != project_version:
        fail(f"project template must target {project_version}")
    if "mobile_licensing" not in template.get("capabilities", {}):
        fail("Android project template must explicitly answer mobile_licensing")

    omitted = copy.deepcopy(template)
    omitted["capabilities"].pop("mobile_licensing", None)
    expect_invalid(validator, omitted, "android project omitted licensing decision")

    enabled_without_artifact = copy.deepcopy(template)
    enabled_without_artifact["capabilities"]["mobile_licensing"] = True
    enabled_without_artifact["artifact_locations"].pop("mobile_licensing", None)
    expect_invalid(validator, enabled_without_artifact, "enabled licensing without profile path")

    no_mobile_target = copy.deepcopy(template)
    no_mobile_target["capabilities"]["android"] = False
    if "ios" in no_mobile_target["capabilities"]:
        no_mobile_target["capabilities"]["ios"] = False
    no_mobile_target["capabilities"].pop("mobile_licensing", None)
    no_mobile_target.pop("mobile", None)
    if list(validator.iter_errors(no_mobile_target)):
        fail("project with no mobile target must not be forced to declare mobile licensing")

    if project_version == DEVELOPMENT_VERSION:
        ios_only = copy.deepcopy(template)
        ios_only["capabilities"]["android"] = False
        ios_only["capabilities"]["ios"] = True
        ios_only["capabilities"].pop("mobile_licensing", None)
        if list(validator.iter_errors(ios_only)):
            fail("iOS-only project must not inherit Android mobile licensing applicability")
        print("PASS iOS-only project does not imply mobile licensing")

    print(f"PASS project-level licensing applicability semantics under project contract {project_version}")


def validate_catalog_and_workflows() -> None:
    active_version = active_project_version()
    checks_doc = load_yaml("catalog/checks.yaml")
    if checks_doc.get("version") != active_version:
        fail(f"checks catalog must declare active component provenance {active_version}")
    checks = {item.get("id"): item for item in checks_doc.get("checks", [])}
    missing = REQUIRED_CHECKS - set(checks)
    if missing:
        fail(f"missing mobile licensing checks: {sorted(missing)}")
    decision = checks.get("requirements.mobile_licensing_decision", {})
    if decision.get("capability") != "android":
        fail("mobile licensing applicability decision must remain Android-scoped")

    gates_doc = load_yaml("catalog/gates.yaml")
    if gates_doc.get("version") != active_version:
        fail(f"gates catalog must declare active component provenance {active_version}")
    gate = next((g for g in gates_doc.get("gates", []) if g.get("id") == "mobile_licensing_ready"), None)
    if not gate or gate.get("applicability_capability") != "mobile_licensing":
        fail("mobile_licensing_ready conditional gate missing")
    if not REQUIRED_CHECKS.issubset(set(gate.get("require_all", []))):
        fail("mobile_licensing_ready must require all licensing checks")
    release_gate = next(g for g in gates_doc["gates"] if g.get("id") == "release_gate")
    if "mobile_licensing_ready" not in set(release_gate.get("prerequisite_gates_if_applicable", [])):
        fail("release_gate must depend conditionally on mobile_licensing_ready")

    skills = load_yaml("catalog/skills.yaml")
    if skills.get("version") != active_version:
        fail(f"skills catalog must declare active component provenance {active_version}")
    spec = skills.get("registry", {}).get("dev-mobile-licensing")
    if not spec or spec.get("status") != "materialized":
        fail("dev-mobile-licensing must remain materialized")
    conditional = skills.get("categories", {}).get("mobile_licensing", {}).get("conditional_on", {})
    if conditional.get("mobile_licensing") is not True:
        fail("mobile licensing skill must load only when capability is true")

    for path in ("workflows/greenfield.yaml", "workflows/brownfield.yaml"):
        workflow = load_yaml(path)
        if workflow.get("version") != active_version:
            fail(f"{path} must declare active component provenance {active_version}")
        capability = workflow.get("conditional_capabilities", {}).get("mobile_licensing", {})
        if capability.get("applicability") != "CONDITIONAL":
            fail(f"{path} missing conditional mobile licensing branch")
        if capability.get("decision_required_when") != {"android": True}:
            fail(f"{path} mobile licensing decision boundary must remain exactly Android-only")
        if capability.get("enabled_when", {}).get("mobile_licensing") is not True:
            fail(f"{path} licensing enable condition drifted")
        if capability.get("exit_gate") != "mobile_licensing_ready":
            fail(f"{path} must exit licensing branch through mobile_licensing_ready")
    print(f"PASS retained Android-only mobile licensing boundary under {active_version}")


def main() -> int:
    root = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    if root != STABLE_VERSION:
        fail(f"mobile licensing compatibility validator requires VERSION={STABLE_VERSION}, got {root}")
    validate_profile_schema()
    validate_project_applicability()
    validate_catalog_and_workflows()
    print("PASS Blueprint optional mobile licensing compatibility validation")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"FAIL: {exc}")
        raise SystemExit(1)
