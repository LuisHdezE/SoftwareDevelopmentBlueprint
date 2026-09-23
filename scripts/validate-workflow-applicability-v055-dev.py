#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
TARGET_VERSION = "0.5.5-dev"
STABLE_VERSION = "0.5.4"

OVERLAY_PATH = ROOT / "catalog/workflow-gate-applicability-v055-dev.yaml"
SCHEMA_PATH = ROOT / "schemas/workflow-gate-applicability-v055-dev.schema.json"
CHECKS_PATH = ROOT / "catalog/checks.yaml"
GATES_PATH = ROOT / "catalog/gates.yaml"
WORKFLOW_PATHS = {
    "greenfield": ROOT / "workflows/greenfield.yaml",
    "brownfield": ROOT / "workflows/brownfield.yaml",
}
PROJECT_OPTIONAL_PATH = ROOT / "templates/project-v055-dev.api-optional.example.yaml"
PROJECT_BACKED_PATH = ROOT / "templates/project-v055-dev.api-backed.example.yaml"

EXPECTED_API_PHASE_NA = {
    "api_contract_design",
    "api_implementation",
    "openapi_validation",
    "postman_contract",
    "api_qa",
    "api_gate",
}
EXPECTED_API_GATE_NA = {
    "api_contract_ready",
    "api_implemented",
    "openapi_valid",
    "postman_ready",
    "api_qa_pass",
    "api_gate",
}
EXPECTED_API_OPTIONAL_CHECK_NA = {
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
EXPECTED_DATABASE_CHECKS = {
    "data.schema_migrations",
    "data.authoritative_database",
}
EXPECTED_PROVIDER_PATH_RETAINED = {
    "client.architecture_contract",
    "functional.inventory_binding",
    "functional.no_hardcoded_business_data",
    "functional.no_invented_capabilities",
    "functional.responsive_runtime",
    "functional.accessibility_runtime",
    "functional.tests",
    "functional.traceability",
    "review.design_system_fidelity",
    "review.responsive",
    "review.accessibility",
    "review.human_complete",
    "qa.functional",
    "qa.integration",
    "qa.security",
    "qa.responsive",
    "qa.accessibility",
    "qa.e2e",
}
EXPECTED_NEXT_AFTER_ARCHITECTURE = "interface_inventory"


def fail(message: str) -> None:
    raise AssertionError(message)


def load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        fail(f"{path.relative_to(ROOT)} must contain a YAML object")
    return value


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        fail(f"{path.relative_to(ROOT)} must contain a JSON object")
    return value


def validate_overlay_schema(overlay: dict[str, Any]) -> None:
    schema = load_json(SCHEMA_PATH)
    errors = sorted(
        Draft202012Validator(schema).iter_errors(overlay),
        key=lambda err: list(err.absolute_path),
    )
    if errors:
        details = "; ".join(
            f"{'/'.join(map(str, err.absolute_path)) or '<root>'}: {err.message}"
            for err in errors
        )
        fail(f"workflow applicability overlay schema validation failed: {details}")


def index_catalog(doc: dict[str, Any], key: str, label: str) -> dict[str, dict[str, Any]]:
    items = doc.get(key)
    if not isinstance(items, list):
        fail(f"catalog {label} must be a list")
    indexed: dict[str, dict[str, Any]] = {}
    for item in items:
        if not isinstance(item, dict) or not isinstance(item.get("id"), str):
            fail(f"every {label} item must be an object with string id")
        if item["id"] in indexed:
            fail(f"duplicate {label} id: {item['id']}")
        indexed[item["id"]] = item
    return indexed


def authority_mode(project: dict[str, Any]) -> str:
    try:
        mode = project["authority"]["api"]["mode"]
    except (KeyError, TypeError):
        fail("project authority.api.mode is required before workflow applicability can be resolved")
    if mode not in {"api_backed", "api_optional"}:
        fail(f"unsupported authority.api.mode: {mode}")
    return mode


def resolve(
    overlay: dict[str, Any],
    project: dict[str, Any],
    workflow: dict[str, Any],
    checks_by_id: dict[str, dict[str, Any]],
    gates_by_id: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    mode = authority_mode(project)
    profile = overlay["profiles"][mode]
    phase_na = set(profile["phase_na"])
    gate_na = set(profile["gate_na"])
    check_na = set(profile["check_na"])

    check_na.update(
        check_id
        for check_id, check in checks_by_id.items()
        if check.get("phase") in phase_na
    )

    database_present = project.get("stack", {}).get("database") is not None
    if mode == "api_optional" and not database_present:
        check_na.update(profile["check_na_when_database_absent"])

    sequence = workflow.get("sequence")
    if not isinstance(sequence, list) or not all(isinstance(value, str) for value in sequence):
        fail("workflow sequence must be a list of phase ids")
    effective_sequence = [phase for phase in sequence if phase not in phase_na]

    gate_bindings = workflow.get("gates")
    if not isinstance(gate_bindings, dict):
        fail("workflow gates must be an object")
    effective_gate_bindings = {
        point: gate_id for point, gate_id in gate_bindings.items() if gate_id not in gate_na
    }

    effective_gate_requirements: dict[str, dict[str, list[str]]] = {}
    for gate_id, gate in gates_by_id.items():
        if gate_id in gate_na:
            continue
        effective_gate_requirements[gate_id] = {
            "require_all": [
                check_id for check_id in gate.get("require_all", []) if check_id not in check_na
            ],
            "require_if_applicable": [
                check_id
                for check_id in gate.get("require_if_applicable", [])
                if check_id not in check_na
            ],
        }

    return {
        "mode": mode,
        "database_present": database_present,
        "phase_na": sorted(phase_na),
        "check_na": sorted(check_na),
        "gate_na": sorted(gate_na),
        "sequence": effective_sequence,
        "gate_bindings": effective_gate_bindings,
        "gate_requirements": effective_gate_requirements,
    }


def validate_contract_ids(
    overlay: dict[str, Any],
    checks_by_id: dict[str, dict[str, Any]],
    gates_by_id: dict[str, dict[str, Any]],
    workflows: dict[str, dict[str, Any]],
) -> None:
    if overlay.get("target_version") != TARGET_VERSION:
        fail("workflow applicability target_version drifted")
    if overlay.get("stable_version") != STABLE_VERSION:
        fail("workflow applicability stable_version drifted")
    if overlay.get("stable_workflows") != ["greenfield", "brownfield"]:
        fail("workflow applicability must govern greenfield then brownfield explicitly")

    for workflow_id, workflow in workflows.items():
        if workflow.get("version") != STABLE_VERSION or workflow.get("mode") != workflow_id:
            fail(f"{workflow_id} stable workflow identity drifted")

    optional = overlay["profiles"]["api_optional"]
    if set(optional["phase_na"]) != EXPECTED_API_PHASE_NA:
        fail("api_optional phase N/A set drifted")
    if set(optional["gate_na"]) != EXPECTED_API_GATE_NA:
        fail("api_optional gate N/A set drifted")
    if set(optional["check_na"]) != EXPECTED_API_OPTIONAL_CHECK_NA:
        fail("api_optional authority-sensitive check N/A set drifted")
    if set(optional["check_na_when_database_absent"]) != EXPECTED_DATABASE_CHECKS:
        fail("api_optional database-absence N/A set drifted")
    if optional["route"]["next_after_architecture_security_data"] != EXPECTED_NEXT_AFTER_ARCHITECTURE:
        fail("api_optional post-architecture route drifted")

    if EXPECTED_PROVIDER_PATH_RETAINED & set(optional["check_na"]):
        fail("api_optional cannot classify provider-path client/functional/review/QA obligations as N/A")

    for check_id in optional["check_na"] + optional["check_na_when_database_absent"]:
        if check_id not in checks_by_id:
            fail(f"applicability references unknown check: {check_id}")
    for gate_id in optional["gate_na"]:
        if gate_id not in gates_by_id:
            fail(f"applicability references unknown gate: {gate_id}")
    for phase_id in optional["phase_na"]:
        if not any(phase_id in workflow.get("sequence", []) for workflow in workflows.values()):
            fail(f"applicability references unknown workflow phase: {phase_id}")


def validate_api_backed_preserves_stable(
    overlay: dict[str, Any],
    backed_project: dict[str, Any],
    workflows: dict[str, dict[str, Any]],
    checks_by_id: dict[str, dict[str, Any]],
    gates_by_id: dict[str, dict[str, Any]],
) -> None:
    profile = overlay["profiles"]["api_backed"]
    expected_profile = {
        "inherit_stable_exactly": True,
        "phase_na": [],
        "check_na": [],
        "gate_na": [],
    }
    if profile != expected_profile:
        fail("api_backed profile must not override stable 0.5.4 applicability")

    for workflow_id, workflow in workflows.items():
        resolved = resolve(overlay, backed_project, workflow, checks_by_id, gates_by_id)
        if resolved["sequence"] != workflow["sequence"]:
            fail(f"api_backed {workflow_id} sequence must exactly preserve stable 0.5.4")
        if resolved["gate_bindings"] != workflow["gates"]:
            fail(f"api_backed {workflow_id} gate bindings must exactly preserve stable 0.5.4")
        if resolved["phase_na"] or resolved["check_na"] or resolved["gate_na"]:
            fail(f"api_backed {workflow_id} cannot classify stable obligations as N/A")
        for gate_id, gate in gates_by_id.items():
            effective = resolved["gate_requirements"][gate_id]
            if effective["require_all"] != gate.get("require_all", []):
                fail(f"api_backed gate {gate_id} require_all drifted")
            if effective["require_if_applicable"] != gate.get("require_if_applicable", []):
                fail(f"api_backed gate {gate_id} require_if_applicable drifted")

    print("PASS api_backed profile preserves stable 0.5.4 workflow/check/gate strictness")


def validate_api_optional_route(
    overlay: dict[str, Any],
    optional_project: dict[str, Any],
    workflows: dict[str, dict[str, Any]],
    checks_by_id: dict[str, dict[str, Any]],
    gates_by_id: dict[str, dict[str, Any]],
) -> None:
    for workflow_id, workflow in workflows.items():
        resolved = resolve(overlay, optional_project, workflow, checks_by_id, gates_by_id)
        check_na = set(resolved["check_na"])

        if set(resolved["phase_na"]) != EXPECTED_API_PHASE_NA:
            fail(f"{workflow_id} api_optional phase applicability drifted")
        if set(resolved["gate_na"]) != EXPECTED_API_GATE_NA:
            fail(f"{workflow_id} api_optional gate applicability drifted")
        if not EXPECTED_API_OPTIONAL_CHECK_NA.issubset(check_na):
            fail(f"{workflow_id} api_optional lost authority-sensitive N/A checks")
        if EXPECTED_PROVIDER_PATH_RETAINED & check_na:
            fail(f"{workflow_id} api_optional incorrectly bypasses provider-path obligations")
        if "api_gate" in resolved["gate_bindings"].values():
            fail(f"{workflow_id} api_gate cannot remain a client-delivery blocker for api_optional")
        if any(phase in resolved["sequence"] for phase in EXPECTED_API_PHASE_NA):
            fail(f"{workflow_id} api_optional effective sequence still contains API-only phase")

        sequence = resolved["sequence"]
        architecture_index = sequence.index("architecture_security_data")
        if architecture_index + 1 >= len(sequence) or sequence[architecture_index + 1] != EXPECTED_NEXT_AFTER_ARCHITECTURE:
            fail(f"{workflow_id} api_optional must route architecture_security_data directly to {EXPECTED_NEXT_AFTER_ARCHITECTURE}")

        architecture_requirements = set(resolved["gate_requirements"]["architecture_ready"]["require_all"])
        forbidden_architecture = {
            "api.auth_strategy",
            "api.error_contract",
            "api.versioning_policy",
        } | EXPECTED_DATABASE_CHECKS
        if architecture_requirements & forbidden_architecture:
            fail(f"{workflow_id} api_optional architecture_ready still requires {sorted(architecture_requirements & forbidden_architecture)}")

        for gate_id, requirements in resolved["gate_requirements"].items():
            leaked = set(requirements["require_all"]) & check_na
            leaked |= set(requirements["require_if_applicable"]) & check_na
            if leaked:
                fail(f"{workflow_id} effective gate {gate_id} still requires N/A checks: {sorted(leaked)}")

    print("PASS api_optional composes workflow, client/slice and review applicability without bypassing provider obligations")


def validate_database_condition(
    overlay: dict[str, Any],
    optional_project: dict[str, Any],
    workflows: dict[str, dict[str, Any]],
    checks_by_id: dict[str, dict[str, Any]],
    gates_by_id: dict[str, dict[str, Any]],
) -> None:
    with_database = copy.deepcopy(optional_project)
    with_database.setdefault("stack", {})["database"] = "local-persistence"

    for workflow_id, workflow in workflows.items():
        without_db = resolve(overlay, optional_project, workflow, checks_by_id, gates_by_id)
        with_db = resolve(overlay, with_database, workflow, checks_by_id, gates_by_id)
        if not EXPECTED_DATABASE_CHECKS.issubset(set(without_db["check_na"])):
            fail(f"{workflow_id} database checks must be N/A when api_optional database is absent")
        if EXPECTED_DATABASE_CHECKS & set(with_db["check_na"]):
            fail(f"{workflow_id} database checks must return when api_optional declares a database")
        architecture_requirements = set(with_db["gate_requirements"]["architecture_ready"]["require_all"])
        if not EXPECTED_DATABASE_CHECKS.issubset(architecture_requirements):
            fail(f"{workflow_id} architecture_ready must regain database checks when database exists")

    print("PASS api_optional database checks are conditional on declared database presence")


def expect_failure(label: str, callback) -> None:
    try:
        callback()
    except (AssertionError, KeyError, TypeError, ValueError):
        print(f"PASS negative case: {label}")
        return
    fail(f"negative case unexpectedly passed: {label}")


def validate_negative_cases(
    overlay: dict[str, Any],
    optional_project: dict[str, Any],
    backed_project: dict[str, Any],
    workflows: dict[str, dict[str, Any]],
    checks_by_id: dict[str, dict[str, Any]],
    gates_by_id: dict[str, dict[str, Any]],
) -> None:
    greenfield = workflows["greenfield"]

    missing_authority = copy.deepcopy(optional_project)
    missing_authority.pop("authority", None)
    expect_failure("authority declaration omitted", lambda: resolve(overlay, missing_authority, greenfield, checks_by_id, gates_by_id))

    api_backed_bypass = copy.deepcopy(overlay)
    api_backed_bypass["profiles"]["api_backed"]["phase_na"] = ["api_gate"]
    expect_failure(
        "api_backed attempts to classify API phase N/A",
        lambda: validate_api_backed_preserves_stable(api_backed_bypass, backed_project, workflows, checks_by_id, gates_by_id),
    )

    optional_gate_leak = copy.deepcopy(overlay)
    optional_gate_leak["profiles"]["api_optional"]["gate_na"].remove("api_gate")
    expect_failure("api_optional leaves api_gate active", lambda: validate_contract_ids(optional_gate_leak, checks_by_id, gates_by_id, workflows))

    optional_phase_leak = copy.deepcopy(overlay)
    optional_phase_leak["profiles"]["api_optional"]["phase_na"].remove("openapi_validation")
    expect_failure("api_optional leaves OpenAPI phase active", lambda: validate_contract_ids(optional_phase_leak, checks_by_id, gates_by_id, workflows))

    optional_db_bypass = copy.deepcopy(overlay)
    optional_db_bypass["profiles"]["api_optional"]["check_na_when_database_absent"].remove("data.authoritative_database")
    expect_failure(
        "database-absent profile keeps authoritative database requirement inconsistently",
        lambda: validate_contract_ids(optional_db_bypass, checks_by_id, gates_by_id, workflows),
    )

    slice_api_leak = copy.deepcopy(overlay)
    slice_api_leak["profiles"]["api_optional"]["check_na"].remove("functional.real_api_integration")
    expect_failure(
        "api_optional reintroduces real API requirement into provider-driven functional slice",
        lambda: validate_contract_ids(slice_api_leak, checks_by_id, gates_by_id, workflows),
    )

    provider_bypass = copy.deepcopy(overlay)
    provider_bypass["profiles"]["api_optional"]["check_na"].append("qa.security")
    expect_failure(
        "api_optional attempts to bypass provider-path security QA",
        lambda: validate_contract_ids(provider_bypass, checks_by_id, gates_by_id, workflows),
    )


def main() -> int:
    overlay = load_yaml(OVERLAY_PATH)
    validate_overlay_schema(overlay)

    checks_doc = load_yaml(CHECKS_PATH)
    gates_doc = load_yaml(GATES_PATH)
    workflows = {name: load_yaml(path) for name, path in WORKFLOW_PATHS.items()}
    optional_project = load_yaml(PROJECT_OPTIONAL_PATH)
    backed_project = load_yaml(PROJECT_BACKED_PATH)

    if checks_doc.get("version") != STABLE_VERSION:
        fail("stable checks catalog must remain 0.5.4 during hardening")
    if gates_doc.get("version") != STABLE_VERSION:
        fail("stable gates catalog must remain 0.5.4 during hardening")

    checks_by_id = index_catalog(checks_doc, "checks", "check")
    gates_by_id = index_catalog(gates_doc, "gates", "gate")

    validate_contract_ids(overlay, checks_by_id, gates_by_id, workflows)
    validate_api_backed_preserves_stable(overlay, backed_project, workflows, checks_by_id, gates_by_id)
    validate_api_optional_route(overlay, optional_project, workflows, checks_by_id, gates_by_id)
    validate_database_condition(overlay, optional_project, workflows, checks_by_id, gates_by_id)
    validate_negative_cases(overlay, optional_project, backed_project, workflows, checks_by_id, gates_by_id)

    print("\nBlueprint 0.5.5-dev workflow & gate applicability validation: PASS (api_backed strict; api_optional authority composition explicit)")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
