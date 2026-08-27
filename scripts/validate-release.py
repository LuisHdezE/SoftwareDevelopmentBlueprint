#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
STABLE_V4 = "0.4.0"
STABLE_V5 = "0.5.0"
STABLE_V51 = "0.5.1"

V4_COUNTS = {
    "phases": 25,
    "checks": 92,
    "gates": 14,
    "materialized_skills": 13,
    "planned_skills": 25,
}

V5_COUNTS = {
    "phases": 28,
    "checks": 134,
    "gates": 18,
    "materialized_skills": 14,
    "planned_skills": 25,
}

V51_COUNTS = {
    "phases": 28,
    "checks": 135,
    "gates": 18,
    "materialized_skills": 14,
    "planned_skills": 25,
}

UNCHANGED_V5_YAML_COMPONENTS = [
    "catalog/phases.yaml",
    "catalog/skills.yaml",
    "catalog/reference-pilots.yaml",
    "workflows/greenfield.yaml",
    "workflows/brownfield.yaml",
]

UNCHANGED_V5_SCHEMAS = [
    "schemas/api-impact.schema.json",
    "schemas/client-architecture.schema.json",
    "schemas/client-platform-architecture.schema.json",
    "schemas/evidence.schema.json",
    "schemas/functional-interface-slice.schema.json",
    "schemas/interface-inventory.schema.json",
    "schemas/mockup-batch.schema.json",
    "schemas/design-system.schema.json",
    "schemas/design-tokens.schema.json",
    "schemas/reference-pilots.schema.json",
    "schemas/compliance-review.schema.json",
]

SCHEMA_VERSION_CONST_V5 = [
    "schemas/api-impact.schema.json",
    "schemas/client-architecture.schema.json",
    "schemas/client-platform-architecture.schema.json",
    "schemas/evidence.schema.json",
    "schemas/functional-interface-slice.schema.json",
    "schemas/interface-inventory.schema.json",
    "schemas/mockup-batch.schema.json",
    "schemas/design-system.schema.json",
    "schemas/design-tokens.schema.json",
]

POST_API_PIPELINE = [
    "interface_inventory",
    "design_system",
    "client_architecture",
    "functional_interface_slice",
    "visual_functional_review",
    "integration_qa",
]

REQUIRED_SCOPED_GATES = {
    "interface_scope_ready": "project",
    "api_gate": "project",
    "interface_inventory_ready": "project",
    "design_system_ready": "project",
    "mockup_review_pass": "interface_slice",
    "client_architecture_ready": "interface_slice_platform",
    "functional_slice_ready": "interface_slice_platform",
    "visual_functional_review_pass": "interface_slice_platform",
    "integration_qa_pass": "interface_slice_platform",
}

VALIDATORS = [
    "scripts/validate-experience-artifacts.py",
    "scripts/validate-skills.py",
    "scripts/validate-client-architecture.py",
    "scripts/validate-reference-pilot-compliance.py",
    "scripts/validate-architecture-conformance.py",
]


def fail(message: str) -> None:
    raise AssertionError(message)


def load_yaml(path: str) -> dict:
    value = yaml.safe_load((ROOT / path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        fail(f"{path} must contain a mapping")
    return value


def load_json(path: str) -> dict:
    value = json.loads((ROOT / path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        fail(f"{path} must contain an object")
    return value


def planned_skill_count(catalog: dict) -> int:
    total = 0
    seen: set[str] = set()
    for category, values in catalog.get("planned_registry", {}).items():
        if not isinstance(values, list):
            fail(f"planned_registry.{category} must be a list")
        for skill_id in values:
            if skill_id in seen:
                fail(f"planned skill duplicated: {skill_id}")
            seen.add(skill_id)
            total += 1
    return total


def catalog_counts() -> dict[str, int]:
    return {
        "phases": len(load_yaml("catalog/phases.yaml").get("phases", [])),
        "checks": len(load_yaml("catalog/checks.yaml").get("checks", [])),
        "gates": len(load_yaml("catalog/gates.yaml").get("gates", [])),
        "materialized_skills": len(load_yaml("catalog/skills.yaml").get("registry", {})),
        "planned_skills": planned_skill_count(load_yaml("catalog/skills.yaml")),
    }


def by_id(values: list[dict]) -> dict[str, dict]:
    result: dict[str, dict] = {}
    for item in values:
        item_id = item.get("id")
        if not isinstance(item_id, str) or not item_id:
            fail("catalog item missing id")
        if item_id in result:
            fail(f"duplicate catalog id: {item_id}")
        result[item_id] = item
    return result


def assert_contiguous(sequence: list[str], subsequence: list[str], label: str) -> None:
    for index in range(0, len(sequence) - len(subsequence) + 1):
        if sequence[index:index + len(subsequence)] == subsequence:
            return
    fail(f"{label} does not contain expected pipeline contiguously: {subsequence}")


def validate_historical_v4_release() -> None:
    release = load_json("documentation/BLUEPRINT_V0_4_RELEASE.json")
    if release.get("version") != STABLE_V4 or release.get("status") != "stable":
        fail("historical v0.4 release manifest drifted")
    if release.get("tag") != "v0.4.0" or release.get("counts") != V4_COUNTS:
        fail("historical v0.4 release identity/counts drifted")
    if release.get("historical_review_target") != "0.4.0-dev":
        fail("historical v0.4 review target drifted")
    print("PASS historical v0.4 release preserved")


def validate_historical_v5_release() -> None:
    release = load_json("documentation/BLUEPRINT_V0_5_RELEASE.json")
    if release.get("version") != STABLE_V5 or release.get("status") != "stable":
        fail("historical v0.5.0 release manifest drifted")
    if release.get("previous_stable") != STABLE_V4 or release.get("tag") != "v0.5.0":
        fail("historical v0.5.0 lineage drifted")
    if release.get("counts") != V5_COUNTS:
        fail("historical v0.5.0 counts must remain 28/134/18/14/25")
    expected_boundaries = {
        ("V5-0", 11), ("V5-1", 12), ("V5-1A", 13),
        ("V5-2", 14), ("V5-3", 15), ("V5-4", 16),
    }
    actual = {(item.get("id"), item.get("pull_request")) for item in release.get("delivery_slices", [])}
    if actual != expected_boundaries:
        fail("historical v0.5.0 delivery slices drifted")
    print("PASS historical v0.5.0 release preserved")


def validate_v51_release_manifest() -> None:
    release = load_json("documentation/BLUEPRINT_V0_5_1_RELEASE.json")
    if release.get("version") != STABLE_V51 or release.get("status") != "stable":
        fail("0.5.1 release manifest must declare stable 0.5.1")
    if release.get("previous_stable") != STABLE_V5:
        fail("0.5.1 previous stable must be 0.5.0")
    if release.get("tag") != "v0.5.1":
        fail("0.5.1 tag declaration must be v0.5.1")
    if release.get("pre_release_main") != "8a59fa6784430eb103258c7c808922d53fa54e63":
        fail("0.5.1 pre-release main must be the accepted PR #19 merge")
    hardening = release.get("hardening_boundary", {})
    if hardening.get("pull_request") != 19 or hardening.get("merge_commit") != "8a59fa6784430eb103258c7c808922d53fa54e63":
        fail("0.5.1 hardening boundary provenance drifted")
    if release.get("counts") != V51_COUNTS:
        fail(f"0.5.1 release counts drifted: {release.get('counts')}")
    compatibility = release.get("compatibility", {})
    for key in (
        "consumer_auto_upgrade",
        "brownfield_align_do_not_rewrite",
        "grandfather_existing_evidence",
        "mockups_conditional",
        "impact_based_api_revalidation",
        "unchanged_component_provenance_reuse",
    ):
        if key == "consumer_auto_upgrade":
            if compatibility.get(key) is not False:
                fail("0.5.1 must not auto-upgrade consumers")
        elif compatibility.get(key) is not True:
            fail(f"0.5.1 compatibility policy drifted: {key}")
    provenance = release.get("component_provenance", {})
    expected = {
        "root_release": "0.5.1",
        "checks_catalog": "0.5.1",
        "gates_catalog": "0.5.1",
        "project_schema": "0.5.1",
        "status_schema": "0.5.1",
        "project_status_templates": "0.5.1",
        "unchanged_phases_workflows_skills_experience_contracts": "0.5.0-compatible",
    }
    if provenance != expected:
        fail("0.5.1 component provenance manifest drifted")
    print("PASS stable v0.5.1 release manifest")


def validate_root_and_component_identity() -> None:
    if VERSION != STABLE_V51:
        fail(f"stable release requires VERSION={STABLE_V51}, got {VERSION}")

    if load_yaml("catalog/checks.yaml").get("version") != STABLE_V51:
        fail("checks catalog must be 0.5.1")
    if load_yaml("catalog/gates.yaml").get("version") != STABLE_V51:
        fail("gates catalog must be 0.5.1")

    for path in UNCHANGED_V5_YAML_COMPONENTS:
        if load_yaml(path).get("version") != STABLE_V5:
            fail(f"unchanged component must retain 0.5.0 provenance: {path}")

    project_template = load_yaml("templates/project.example.yaml")
    status_template = load_yaml("templates/status.example.yaml")
    if project_template.get("blueprint", {}).get("version") != STABLE_V51:
        fail("canonical project template must declare 0.5.1")
    if status_template.get("blueprint_version") != STABLE_V51:
        fail("canonical status template must declare 0.5.1")

    actual_counts = catalog_counts()
    if actual_counts != V51_COUNTS:
        fail(f"0.5.1 core counts drifted: expected {V51_COUNTS}, got {actual_counts}")
    print(f"PASS root/component identity and counts: {V51_COUNTS}")


def validate_schema_provenance() -> None:
    project = load_json("schemas/project.schema.json")
    if "/blueprint/0.5.1/" not in project.get("$id", ""):
        fail("project schema $id must be version-pinned to 0.5.1")
    if project["properties"]["blueprint"]["properties"]["version"].get("const") != STABLE_V51:
        fail("project schema consumer version must be const 0.5.1")

    status = load_json("schemas/status.schema.json")
    if "/blueprint/0.5.1/" not in status.get("$id", ""):
        fail("status schema $id must be version-pinned to 0.5.1")
    if status["properties"]["blueprint_version"].get("const") != STABLE_V51:
        fail("status schema blueprint_version must be const 0.5.1")

    for path in UNCHANGED_V5_SCHEMAS:
        schema = load_json(path)
        if "/blueprint/0.5.0/" not in schema.get("$id", ""):
            fail(f"unchanged schema must retain 0.5.0 provenance: {path}")

    for path in SCHEMA_VERSION_CONST_V5:
        schema = load_json(path)
        value = schema.get("properties", {}).get("schema_version", {}).get("const")
        if value != STABLE_V5:
            fail(f"unchanged schema_version must remain const 0.5.0: {path}")

    refs = load_json("schemas/reference-pilots.schema.json")
    if refs["properties"]["version"].get("const") != STABLE_V5:
        fail("reference pilot schema registry version must remain 0.5.0")

    compliance_text = json.dumps(load_json("schemas/compliance-review.schema.json"))
    if "blueprint_change" not in compliance_text or "v0_4_change" not in compliance_text:
        fail("compliance review schema historical compatibility drifted")
    print("PASS 0.5.1 project/status provenance and 0.5.0 compatible schema reuse")


def validate_architecture_conformance_semantics() -> None:
    checks = by_id(load_yaml("catalog/checks.yaml").get("checks", []))
    gates = by_id(load_yaml("catalog/gates.yaml").get("gates", []))
    check_id = "api.architecture_implementation_conformance"
    check = checks.get(check_id)
    if not check:
        fail("0.5.1 missing architecture implementation conformance check")
    if check.get("phase") != "api_implementation" or check.get("type") != "REQUIRED" or check.get("verification") != "evidence":
        fail("architecture implementation conformance check classification drifted")
    for gate_id in ("api_implemented", "api_gate"):
        if check_id not in set(gates[gate_id].get("require_all", [])):
            fail(f"{gate_id} must require {check_id}")
    if "runtime tests cannot substitute" not in str(gates["api_gate"].get("rule", "")):
        fail("api_gate must reject runtime-test substitution for architecture conformance")
    print("PASS 0.5.1 architecture conformance catalog semantics")


def validate_core_v5_semantics() -> None:
    phases = by_id(load_yaml("catalog/phases.yaml").get("phases", []))
    gates = by_id(load_yaml("catalog/gates.yaml").get("gates", []))

    if phases["interface_scope_baseline"].get("requires_gates") != ["requirements_ready"]:
        fail("Interface Scope Baseline ownership drifted")
    if set(phases["interface_inventory"].get("requires_gates", [])) != {"api_gate", "interface_scope_ready"}:
        fail("Executable Interface Inventory must reconcile API Gate + Interface Scope Baseline")
    if phases["visual_identity"].get("applicability") != "CONDITIONAL":
        fail("Visual Identity must remain conditional")
    if phases["functional_interface_slice"].get("execution_scope") != "interface_slice_platform":
        fail("Functional Interface Slice must remain slice+platform scoped")

    for gate_id, scope in REQUIRED_SCOPED_GATES.items():
        gate = gates.get(gate_id)
        if not gate or gate.get("evaluation_scope", "project") != scope:
            fail(f"{gate_id} must use scope {scope}")

    if "api.change_impact_analysis" not in set(gates["api_contract_ready"].get("require_if_applicable", [])):
        fail("API Contract Ready impact analysis drifted")
    if "api.affected_consumer_revalidation" not in set(gates["api_qa_pass"].get("require_if_applicable", [])):
        fail("API QA affected-consumer revalidation drifted")
    if "review.human_complete" not in set(gates["visual_functional_review_pass"].get("require_all", [])):
        fail("Visual & Functional Review must require human completion")
    print("PASS retained 0.5.x core semantics")


def validate_workflows() -> None:
    expected_lifecycle = ["INVENTORIED", "READY", "IN_PROGRESS", "FUNCTIONAL", "ACCEPTED"]
    for path in ("workflows/greenfield.yaml", "workflows/brownfield.yaml"):
        workflow = load_yaml(path)
        assert_contiguous(workflow.get("sequence", []), POST_API_PIPELINE, path)
        pipeline = workflow.get("functional_interface_slice_pipeline", {})
        if pipeline.get("scope_key") != "interface_slice_platform" or pipeline.get("lifecycle") != expected_lifecycle:
            fail(f"{path} Functional Interface Slice lifecycle/scope drifted")
        blocker = pipeline.get("blocker_condition", {})
        if blocker.get("id") != "BLOCKED_BY_API" or blocker.get("overlays_lifecycle") is not True:
            fail(f"{path} BLOCKED_BY_API semantics drifted")
        evolution = workflow.get("api_contract_evolution", {})
        if evolution.get("post_baseline_change_policy") != "impact_based_revalidation" or evolution.get("operation_level_key") != "operationId":
            fail(f"{path} API evolution policy drifted")
    print("PASS unchanged 0.5.0 workflows reused by 0.5.1")


def validate_reference_pilot_history() -> None:
    catalog = load_yaml("catalog/reference-pilots.yaml")
    if catalog.get("version") != STABLE_V5:
        fail("reference pilot registry component must retain 0.5.0 provenance")
    pilot = next((p for p in catalog.get("pilots", []) if p.get("id") == "careshift-manager"), None)
    if not pilot:
        fail("careshift-manager missing from historical reference pilot registry")
    if pilot.get("baseline_blueprint") != "0.3.0":
        fail("CareShift historical baseline drifted")
    review = pilot.get("last_compliance_review", {})
    if review.get("target_blueprint") != "0.4.0-dev" or review.get("consumer_version_change") != "DEFERRED":
        fail("CareShift historical review facts drifted")
    print("PASS reference pilot history preserved")


def validate_active_docs() -> None:
    required = {
        "BLUEPRINT.md": ["Stable release: **0.5.1**", "Architecture Implementation Conformance", "api.architecture_implementation_conformance", "component provenance"],
        "README.md": ["Blueprint 0.5.1", "135 checks", "Architecture Implementation Conformance"],
        "documentation/BLUEPRINT_CURRENT_STATE.md": ["Release representada: **0.5.1**", "135 checks", "api.architecture_implementation_conformance", "Compliance Review"],
        "documentation/BLUEPRINT_V0_5_1_ARCHITECTURE_CONFORMANCE_HARDENING.md": ["stable Blueprint `0.5.1`", "Blueprint hardening PR: #19", "consumer auto-adoption"],
        "documentation/BLUEPRINT_V0_5_1_RELEASE_NOTES.md": ["Blueprint 0.5.1", "135 checks", "no automatic consumer upgrade", "v0.5.1"],
    }
    for path, tokens in required.items():
        text = (ROOT / path).read_text(encoding="utf-8")
        if "0.5.1-dev" in text:
            fail(f"stable 0.5.1 document retains prerelease identity: {path}")
        for token in tokens:
            if token not in text:
                fail(f"{path} missing stable 0.5.1 token: {token}")
    print("PASS active 0.5.1 documentation")


def run_validator(path: str) -> None:
    print(f"\n=== {path} ===")
    result = subprocess.run(
        [sys.executable, path],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    print(result.stdout, end="")
    if result.returncode != 0:
        fail(f"nested validator failed: {path} (exit {result.returncode})")


def main() -> int:
    validate_root_and_component_identity()
    validate_schema_provenance()
    validate_historical_v4_release()
    validate_historical_v5_release()
    validate_v51_release_manifest()
    validate_reference_pilot_history()
    validate_architecture_conformance_semantics()
    validate_core_v5_semantics()
    validate_workflows()
    validate_active_docs()
    for validator in VALIDATORS:
        run_validator(validator)
    print(f"\nBlueprint stable release validation: PASS (VERSION={VERSION}; counts={catalog_counts()})")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
