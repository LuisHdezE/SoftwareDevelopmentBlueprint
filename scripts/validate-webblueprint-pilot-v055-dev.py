#!/usr/bin/env python3
"""Validate Increment 6 template provenance and the non-normative WebBlueprint pilot."""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
DOCTOR_PATH = ROOT / "scripts/validate-generic-compliance-v055-dev.py"
MANIFEST_PATH = ROOT / "documentation/BLUEPRINT_V0_5_5_WEBBLUEPRINT_PILOT_MANIFEST.json"
REPORT_PATH = ROOT / "documentation/BLUEPRINT_V0_5_5_WEBBLUEPRINT_PILOT_REPORT.json"
DEVELOPMENT_MANIFEST_PATH = ROOT / "documentation/BLUEPRINT_V0_5_5_DEVELOPMENT.json"
STATUS_TEMPLATE_PATH = ROOT / "templates/status.example.yaml"
STATUS_SCHEMA_PATH = ROOT / "schemas/status.schema.json"
APPLICABILITY_PATH = ROOT / "catalog/workflow-gate-applicability-v055-dev.yaml"

WEBBLUEPRINT_REPOSITORY = "LuisHdezE/WebBlueprint"
WEBBLUEPRINT_SNAPSHOT = "12cc52dabfe05ec9902f0ea6d73c7da6a19e1a74"
EXPECTED_SUMMARY = {"PASS": 18, "FAIL": 7, "N/A": 10, "BLOCKED": 0, "TOTAL": 35}

EXPECTED_NA = {
    "data.authoritative_database",
    "data.schema_migrations",
    "api.auth_strategy",
    "client.api_client_strategy",
    "client.api_contract_binding",
    "functional.api_dependencies_resolved",
    "functional.real_api_integration",
    "functional.auth_rbac_runtime",
    "review.api_permission_fidelity",
    "qa.real_api_transport",
}

EXPECTED_FAIL = {
    "requirements.traceability": "MISSING_EVIDENCE",
    "ui.web_inventory": "CONTRACT_VIOLATION",
    "ui.inventory_requirement_links": "MISSING_EVIDENCE",
    "client.architecture_contract": "CONTRACT_VIOLATION",
    "functional.inventory_binding": "MISSING_EVIDENCE",
    "functional.traceability": "MISSING_EVIDENCE",
    "qa.security": "MISSING_EVIDENCE",
}

REQUIRED_API_OPTIONAL_CHECK_NA = {
    "api.auth_strategy",
    "api.error_contract",
    "api.versioning_policy",
    "client.api_client_strategy",
    "client.api_contract_binding",
    "functional.api_dependencies_resolved",
    "functional.real_api_integration",
    "functional.auth_rbac_runtime",
    "review.api_permission_fidelity",
}


def fail(message: str) -> None:
    raise AssertionError(message)


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        fail(f"{path.relative_to(ROOT)} must contain a JSON object")
    return value


def load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        fail(f"{path.relative_to(ROOT)} must contain a YAML mapping")
    return value


def load_doctor() -> ModuleType:
    spec = importlib.util.spec_from_file_location("blueprint_generic_compliance_doctor", DOCTOR_PATH)
    if spec is None or spec.loader is None:
        fail("cannot load Generic Compliance Doctor")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate_identity_and_origin() -> None:
    stable = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    target = (ROOT / "DEVELOPMENT_VERSION").read_text(encoding="utf-8").strip()
    if stable != "0.5.4" or target != "0.5.5-dev":
        fail(f"Increment 6 requires stable=0.5.4 and target=0.5.5-dev; got {stable=} {target=}")

    development = load_json(DEVELOPMENT_MANIFEST_PATH)
    origin = development.get("origin", {})
    if origin.get("consumer_repository") != WEBBLUEPRINT_REPOSITORY:
        fail("development hardening origin consumer drifted")
    if origin.get("consumer_snapshot") != WEBBLUEPRINT_SNAPSHOT:
        fail("development hardening origin snapshot drifted")
    if development.get("scope", {}).get("status_template_provenance_reconciliation") is not True:
        fail("Increment 6 provenance reconciliation scope must remain explicit")

    print(f"PASS Increment 6 origin: {WEBBLUEPRINT_REPOSITORY}@{WEBBLUEPRINT_SNAPSHOT}")


def validate_status_template_provenance() -> None:
    template = load_yaml(STATUS_TEMPLATE_PATH)
    schema = load_json(STATUS_SCHEMA_PATH)
    Draft202012Validator.check_schema(schema)
    errors = list(Draft202012Validator(schema).iter_errors(template))
    if errors:
        fail("status.example.yaml no longer validates against the stable status schema")
    if template.get("blueprint_version") != "0.5.4":
        fail("status.example.yaml must declare active 0.5.4 provenance")
    if "/blueprint/0.5.4/" not in schema.get("$id", ""):
        fail("status schema must retain 0.5.4 provenance")
    print("PASS status template provenance reconciled to 0.5.4")


def validate_authority_applicability() -> None:
    applicability = load_yaml(APPLICABILITY_PATH)
    profile = applicability.get("profiles", {}).get("api_optional", {})
    check_na = set(profile.get("check_na", []))
    missing = REQUIRED_API_OPTIONAL_CHECK_NA - check_na
    if missing:
        fail(f"api_optional applicability does not compose client/slice authority: missing {sorted(missing)}")
    invariants = profile.get("invariants", {})
    if invariants.get("client_slice_api_checks_are_na_when_provider_authority_is_explicit") is not True:
        fail("client/slice API-optional N/A invariant is missing")
    if invariants.get("provider_contract_and_runtime_obligations_remain_required") is not True:
        fail("provider authority obligations must remain required")
    print("PASS API-optional applicability composes workflow, client/slice and review semantics")


def validate_pilot() -> None:
    manifest = load_json(MANIFEST_PATH)
    if manifest.get("consumer") != {
        "id": "webblueprint",
        "repository": WEBBLUEPRINT_REPOSITORY,
        "snapshot": WEBBLUEPRINT_SNAPSHOT,
    }:
        fail("WebBlueprint pilot consumer identity drifted")
    if manifest.get("blueprint", {}).get("adopted_version") != "UNMANAGED":
        fail("pilot must not pretend WebBlueprint has already adopted a Blueprint release")
    if manifest.get("authority", {}).get("api_mode") != "api_optional":
        fail("WebBlueprint pilot must remain explicitly api_optional")
    if manifest.get("capabilities", {}).get("database") is not False:
        fail("WebBlueprint pilot must not invent an authoritative database")

    doctor = load_doctor()
    report = doctor.build_report(manifest)
    expected_report = load_json(REPORT_PATH)
    if report != expected_report:
        fail("committed WebBlueprint pilot report does not match Generic Compliance Doctor output")

    if report.get("overall_status") != "FAIL":
        fail("pilot must remain fail-closed while consumer governance evidence is incomplete")
    if report.get("summary") != EXPECTED_SUMMARY:
        fail(f"pilot summary drifted: expected {EXPECTED_SUMMARY}, got {report.get('summary')}")

    by_id = {item["check_id"]: item for item in report.get("results", [])}
    for check_id in EXPECTED_NA:
        item = by_id.get(check_id)
        if item is None or item.get("status") != "N/A" or item.get("reason_code") != "NOT_APPLICABLE":
            fail(f"expected truthful API-optional N/A outcome for {check_id}")

    for check_id, reason in EXPECTED_FAIL.items():
        item = by_id.get(check_id)
        if item is None or item.get("status") != "FAIL" or item.get("reason_code") != reason:
            fail(f"expected remaining consumer debt {check_id}={reason}")

    for check_id in (
        "functional.no_hardcoded_business_data",
        "functional.no_invented_capabilities",
        "functional.responsive_runtime",
        "functional.accessibility_runtime",
        "functional.tests",
        "review.human_complete",
        "qa.functional",
        "qa.provider_runtime_transport",
        "qa.integration",
        "qa.responsive",
        "qa.accessibility",
        "qa.e2e",
    ):
        item = by_id.get(check_id)
        if item is None or item.get("status") != "PASS":
            fail(f"expected grandfathered accepted WebBlueprint evidence to remain PASS for {check_id}")

    print("PASS non-normative WebBlueprint pilot report matches Generic Compliance Doctor")
    print(f"PASS pilot summary: {EXPECTED_SUMMARY}")
    print("PASS pilot remains non-adopting and fail-closed; no WebBlueprint mutation is authorized")


def main() -> int:
    validate_identity_and_origin()
    validate_status_template_provenance()
    validate_authority_applicability()
    validate_pilot()
    print("\nBlueprint Increment 6 validation: PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
