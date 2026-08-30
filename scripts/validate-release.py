#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
STABLE_V4 = "0.4.0"
STABLE_V5 = "0.5.0"
STABLE_V51 = "0.5.1"
STABLE_V52 = "0.5.2"

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
V52_COUNTS = dict(V51_COUNTS)

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
    "scripts/validate-ci-runtime.py",
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


def validate_historical_releases() -> None:
    v4 = load_json("documentation/BLUEPRINT_V0_4_RELEASE.json")
    if v4.get("version") != STABLE_V4 or v4.get("status") != "stable":
        fail("historical v0.4 release manifest drifted")
    if v4.get("tag") != "v0.4.0" or v4.get("counts") != V4_COUNTS:
        fail("historical v0.4 release identity/counts drifted")

    v5 = load_json("documentation/BLUEPRINT_V0_5_RELEASE.json")
    if v5.get("version") != STABLE_V5 or v5.get("status") != "stable":
        fail("historical v0.5.0 release manifest drifted")
    if v5.get("previous_stable") != STABLE_V4 or v5.get("tag") != "v0.5.0" or v5.get("counts") != V5_COUNTS:
        fail("historical v0.5.0 lineage/counts drifted")

    v51 = load_json("documentation/BLUEPRINT_V0_5_1_RELEASE.json")
    if v51.get("version") != STABLE_V51 or v51.get("status") != "stable":
        fail("historical v0.5.1 release manifest drifted")
    if v51.get("previous_stable") != STABLE_V5 or v51.get("tag") != "v0.5.1" or v51.get("counts") != V51_COUNTS:
        fail("historical v0.5.1 lineage/counts drifted")
    hardening = v51.get("hardening_boundary", {})
    if hardening.get("pull_request") != 19 or hardening.get("merge_commit") != "8a59fa6784430eb103258c7c808922d53fa54e63":
        fail("historical v0.5.1 hardening provenance drifted")
    print("PASS historical stable releases 0.4.0, 0.5.0 and 0.5.1 preserved")


def validate_v52_release_manifest() -> None:
    release = load_json("documentation/BLUEPRINT_V0_5_2_RELEASE.json")
    if release.get("version") != STABLE_V52 or release.get("status") != "stable":
        fail("0.5.2 release manifest must declare stable 0.5.2")
    if release.get("release_date") != "2026-08-29":
        fail("0.5.2 release_date must use America/Montevideo closure date")
    if release.get("previous_stable") != STABLE_V51 or release.get("tag") != "v0.5.2":
        fail("0.5.2 lineage/tag declaration drifted")
    if release.get("pre_release_main") != "c043bead93e9c4ad6c806576623f228dae239216":
        fail("0.5.2 pre-release main must be accepted PR #22 merge")
    hardening = release.get("hardening_boundary", {})
    if hardening.get("pull_request") != 22 or hardening.get("merge_commit") != "c043bead93e9c4ad6c806576623f228dae239216":
        fail("0.5.2 hardening boundary provenance drifted")
    if release.get("counts") != V52_COUNTS:
        fail(f"0.5.2 release counts drifted: {release.get('counts')}")

    compatibility = release.get("compatibility", {})
    expected_compatibility = {
        "consumer_auto_upgrade": False,
        "brownfield_align_do_not_rewrite": True,
        "grandfather_existing_evidence": True,
        "mockups_conditional": True,
        "impact_based_api_revalidation": True,
        "unchanged_component_provenance_reuse": True,
        "github_hosted_supported": True,
        "self_hosted_supported": True,
        "hybrid_supported": True,
        "exact_head_evidence_preserved": True,
        "project_docker_capability_independent": True,
    }
    if compatibility != expected_compatibility:
        fail("0.5.2 compatibility policy drifted")

    provenance = release.get("component_provenance", {})
    expected_provenance = {
        "root_release": "0.5.2",
        "ci_runtime_schema": "0.5.2",
        "ci_runtime_template": "0.5.2",
        "blueprint_master_runtime_profile": "0.5.2",
        "project_schema": "0.5.2",
        "status_schema": "0.5.2",
        "project_status_templates": "0.5.2",
        "checks_gates_catalogs": "0.5.1-compatible",
        "unchanged_phases_workflows_skills_experience_contracts": "0.5.0-compatible",
    }
    if provenance != expected_provenance:
        fail("0.5.2 component provenance manifest drifted")
    print("PASS stable v0.5.2 release manifest")


def validate_root_and_component_identity() -> None:
    if VERSION != STABLE_V52:
        fail(f"stable release requires VERSION={STABLE_V52}, got {VERSION}")

    if load_yaml("catalog/checks.yaml").get("version") != STABLE_V51:
        fail("0.5.2 reuses checks catalog with 0.5.1 provenance")
    if load_yaml("catalog/gates.yaml").get("version") != STABLE_V51:
        fail("0.5.2 reuses gates catalog with 0.5.1 provenance")
    for path in UNCHANGED_V5_YAML_COMPONENTS:
        if load_yaml(path).get("version") != STABLE_V5:
            fail(f"unchanged component must retain 0.5.0 provenance: {path}")

    project_template = load_yaml("templates/project.example.yaml")
    status_template = load_yaml("templates/status.example.yaml")
    if project_template.get("blueprint", {}).get("version") != STABLE_V52:
        fail("canonical project template must declare 0.5.2")
    if status_template.get("blueprint_version") != STABLE_V52:
        fail("canonical status template must declare 0.5.2")

    actual_counts = catalog_counts()
    if actual_counts != V52_COUNTS:
        fail(f"0.5.2 core counts drifted: expected {V52_COUNTS}, got {actual_counts}")
    print(f"PASS root/component identity and counts: {V52_COUNTS}")


def validate_schema_provenance() -> None:
    project = load_json("schemas/project.schema.json")
    if "/blueprint/0.5.2/" not in project.get("$id", ""):
        fail("project schema $id must be version-pinned to 0.5.2")
    if project["properties"]["blueprint"]["properties"]["version"].get("const") != STABLE_V52:
        fail("project schema consumer version must be const 0.5.2")

    status = load_json("schemas/status.schema.json")
    if "/blueprint/0.5.2/" not in status.get("$id", ""):
        fail("status schema $id must be version-pinned to 0.5.2")
    if status["properties"]["blueprint_version"].get("const") != STABLE_V52:
        fail("status schema blueprint_version must be const 0.5.2")

    ci_runtime = load_json("schemas/ci-runtime.schema.json")
    Draft202012Validator.check_schema(ci_runtime)
    if "/blueprint/0.5.2/" not in ci_runtime.get("$id", ""):
        fail("ci-runtime schema $id must be version-pinned to 0.5.2")
    if ci_runtime["properties"]["schema_version"].get("const") != STABLE_V52:
        fail("ci-runtime schema_version must be const 0.5.2")

    for path in UNCHANGED_V5_SCHEMAS:
        schema = load_json(path)
        if "/blueprint/0.5.0/" not in schema.get("$id", ""):
            fail(f"unchanged schema must retain 0.5.0 provenance: {path}")
    for path in SCHEMA_VERSION_CONST_V5:
        schema = load_json(path)
        value = schema.get("properties", {}).get("schema_version", {}).get("const")
        if value != STABLE_V5:
            fail(f"unchanged schema_version must remain const 0.5.0: {path}")
    print("PASS 0.5.2 project/status/CI runtime provenance with compatible component reuse")


def validate_ci_runtime_semantics() -> None:
    template = load_yaml("templates/ci-runtime.example.yaml")
    master = load_yaml("ci/blueprint-master.runtime.yaml")
    for label, document in (("template", template), ("master", master)):
        if document.get("schema_version") != STABLE_V52:
            fail(f"CI runtime {label} must declare 0.5.2")
        if document.get("orchestrator") != "github_actions":
            fail(f"CI runtime {label} must use github_actions")
        evidence = document.get("evidence", {})
        for key in ("exact_head_required", "check_run_required", "pre_execution_infrastructure_failures_distinct_from_test_failures"):
            if evidence.get(key) is not True:
                fail(f"CI runtime evidence invariant drifted: {label}.{key}")
        if document.get("runner", {}).get("project_docker_capability_independent") is not True:
            fail("runner infrastructure must remain independent from project Docker capability")
    if template.get("strategy") != "self_hosted" or template["runner"].get("container_engine") != "docker":
        fail("canonical CI runtime template must exercise self-hosted service containers")
    if master.get("strategy") != "self_hosted" or master["runner"].get("container_engine") != "none":
        fail("Blueprint Master runtime profile must remain self-hosted without service-container dependency")
    workflow = (ROOT / ".github/workflows/blueprint-ci-runtime-validation.yml").read_text(encoding="utf-8")
    if "runs-on: [self-hosted, linux, x64, blueprint]" not in workflow:
        fail("CI runtime validation workflow must select canonical self-hosted labels")
    print("PASS 0.5.2 CI execution portability semantics")


def validate_architecture_conformance_semantics() -> None:
    checks = by_id(load_yaml("catalog/checks.yaml").get("checks", []))
    gates = by_id(load_yaml("catalog/gates.yaml").get("gates", []))
    check_id = "api.architecture_implementation_conformance"
    check = checks.get(check_id)
    if not check:
        fail("0.5.2 must retain architecture implementation conformance check")
    if check.get("phase") != "api_implementation" or check.get("type") != "REQUIRED" or check.get("verification") != "evidence":
        fail("architecture implementation conformance check classification drifted")
    for gate_id in ("api_implemented", "api_gate"):
        if check_id not in set(gates[gate_id].get("require_all", [])):
            fail(f"{gate_id} must require {check_id}")
    print("PASS retained 0.5.1 architecture conformance semantics")


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
    print("PASS unchanged 0.5.0 workflows reused by 0.5.2")


def validate_reference_pilot_history() -> None:
    catalog = load_yaml("catalog/reference-pilots.yaml")
    if catalog.get("version") != STABLE_V5:
        fail("reference pilot registry component must retain 0.5.0 provenance")
    pilot = next((p for p in catalog.get("pilots", []) if p.get("id") == "careshift-manager"), None)
    if not pilot or pilot.get("baseline_blueprint") != "0.3.0":
        fail("CareShift historical reference-pilot facts drifted")
    print("PASS reference pilot history preserved")


def validate_active_docs() -> None:
    required = {
        "BLUEPRINT.md": ["Stable release: **0.5.2**", "CI Execution Portability", "schemas/ci-runtime.schema.json", "pre-execution infrastructure failure != test failure"],
        "README.md": ["Blueprint 0.5.2", "135 checks", "CI Execution Portability", "self_hosted"],
        "documentation/BLUEPRINT_CURRENT_STATE.md": ["Release representada: **0.5.2**", "135 checks", "ci-runtime", "CUSA-Digital PR #46", "Compliance Review"],
        "documentation/BLUEPRINT_V0_5_2_CI_EXECUTION_PORTABILITY.md": ["stable Blueprint `0.5.2`", "hardening PR: #22", "consumer auto-adoption"],
        "documentation/BLUEPRINT_V0_5_2_RELEASE_NOTES.md": ["Blueprint 0.5.2", "135 checks", "no automatic consumer upgrade", "v0.5.2"],
    }
    for path, tokens in required.items():
        text = (ROOT / path).read_text(encoding="utf-8")
        if "0.5.2-dev" in text:
            fail(f"stable 0.5.2 active document retains prerelease identity: {path}")
        for token in tokens:
            if token not in text:
                fail(f"{path} missing stable 0.5.2 token: {token}")
    print("PASS active 0.5.2 documentation")


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
    validate_historical_releases()
    validate_v52_release_manifest()
    validate_reference_pilot_history()
    validate_architecture_conformance_semantics()
    validate_ci_runtime_semantics()
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
