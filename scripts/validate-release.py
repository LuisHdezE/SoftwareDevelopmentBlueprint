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
DEV_V53 = "0.5.3-dev"

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
V53_DEV_COUNTS = {
    "phases": 28,
    "checks": 145,
    "gates": 19,
    "materialized_skills": 15,
    "planned_skills": 25,
}

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
BASE_VALIDATORS = [
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


def is_v53_hardening() -> bool:
    checks_version = load_yaml("catalog/checks.yaml").get("version")
    gates_version = load_yaml("catalog/gates.yaml").get("version")
    skills_version = load_yaml("catalog/skills.yaml").get("version")
    green_version = load_yaml("workflows/greenfield.yaml").get("version")
    brown_version = load_yaml("workflows/brownfield.yaml").get("version")
    versions = {checks_version, gates_version, skills_version, green_version, brown_version}
    if DEV_V53 in versions and versions != {DEV_V53}:
        fail(f"partial 0.5.3-dev component activation detected: {sorted(str(v) for v in versions)}")
    return versions == {DEV_V53}


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
    print("PASS stable v0.5.2 release manifest preserved")


def validate_root_and_component_identity(hardening: bool) -> None:
    if VERSION != STABLE_V52:
        fail(f"0.5.3-dev hardening must branch from stable VERSION={STABLE_V52}, got {VERSION}")

    phases_version = load_yaml("catalog/phases.yaml").get("version")
    refs_version = load_yaml("catalog/reference-pilots.yaml").get("version")
    if phases_version != STABLE_V5 or refs_version != STABLE_V5:
        fail("unchanged phase/reference-pilot components must retain 0.5.0 provenance")

    if hardening:
        for path in ("catalog/checks.yaml", "catalog/gates.yaml", "catalog/skills.yaml", "workflows/greenfield.yaml", "workflows/brownfield.yaml"):
            if load_yaml(path).get("version") != DEV_V53:
                fail(f"0.5.3-dev hardening component identity mismatch: {path}")
        expected_counts = V53_DEV_COUNTS
        expected_project_version = DEV_V53
    else:
        if load_yaml("catalog/checks.yaml").get("version") != STABLE_V51:
            fail("stable 0.5.2 reuses checks catalog with 0.5.1 provenance")
        if load_yaml("catalog/gates.yaml").get("version") != STABLE_V51:
            fail("stable 0.5.2 reuses gates catalog with 0.5.1 provenance")
        if load_yaml("catalog/skills.yaml").get("version") != STABLE_V5:
            fail("stable 0.5.2 reuses skill catalog with 0.5.0 provenance")
        for path in ("workflows/greenfield.yaml", "workflows/brownfield.yaml"):
            if load_yaml(path).get("version") != STABLE_V5:
                fail(f"stable 0.5.2 workflow provenance drifted: {path}")
        expected_counts = V52_COUNTS
        expected_project_version = STABLE_V52

    project_template = load_yaml("templates/project.example.yaml")
    status_template = load_yaml("templates/status.example.yaml")
    if project_template.get("blueprint", {}).get("version") != expected_project_version:
        fail(f"canonical project template must declare {expected_project_version}")
    if status_template.get("blueprint_version") != STABLE_V52:
        fail("status template remains stable 0.5.2 until release closure")

    actual_counts = catalog_counts()
    if actual_counts != expected_counts:
        fail(f"core counts drifted: expected {expected_counts}, got {actual_counts}")
    label = DEV_V53 if hardening else STABLE_V52
    print(f"PASS root/component identity for {label}: {expected_counts}")


def validate_schema_provenance(hardening: bool) -> None:
    project = load_json("schemas/project.schema.json")
    expected_project_version = DEV_V53 if hardening else STABLE_V52
    if f"/blueprint/{expected_project_version}/" not in project.get("$id", ""):
        fail(f"project schema $id must be version-pinned to {expected_project_version}")
    if project["properties"]["blueprint"]["properties"]["version"].get("const") != expected_project_version:
        fail(f"project schema consumer version must be const {expected_project_version}")

    status = load_json("schemas/status.schema.json")
    if "/blueprint/0.5.2/" not in status.get("$id", ""):
        fail("status schema remains stable 0.5.2 during 0.5.3-dev hardening")
    if status["properties"]["blueprint_version"].get("const") != STABLE_V52:
        fail("status schema blueprint_version must remain const 0.5.2 before release closure")

    ci_runtime = load_json("schemas/ci-runtime.schema.json")
    Draft202012Validator.check_schema(ci_runtime)
    if "/blueprint/0.5.2/" not in ci_runtime.get("$id", ""):
        fail("ci-runtime schema must retain stable 0.5.2 provenance")
    if ci_runtime["properties"]["schema_version"].get("const") != STABLE_V52:
        fail("ci-runtime schema_version must remain const 0.5.2")

    if hardening:
        licensing = load_json("schemas/mobile-licensing.schema.json")
        Draft202012Validator.check_schema(licensing)
        if f"/blueprint/{DEV_V53}/" not in licensing.get("$id", ""):
            fail("mobile licensing schema must be version-pinned to 0.5.3-dev")
        if licensing.get("properties", {}).get("schema_version", {}).get("const") != DEV_V53:
            fail("mobile licensing schema_version must be 0.5.3-dev")

    for path in UNCHANGED_V5_SCHEMAS:
        schema = load_json(path)
        if "/blueprint/0.5.0/" not in schema.get("$id", ""):
            fail(f"unchanged schema must retain 0.5.0 provenance: {path}")
    for path in SCHEMA_VERSION_CONST_V5:
        schema = load_json(path)
        value = schema.get("properties", {}).get("schema_version", {}).get("const")
        if value != STABLE_V5:
            fail(f"unchanged schema_version must remain const 0.5.0: {path}")
    print("PASS project/status/CI/mobile-licensing schema provenance")


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
    print("PASS 0.5.2 CI execution portability semantics preserved")


def validate_architecture_conformance_semantics() -> None:
    checks = by_id(load_yaml("catalog/checks.yaml").get("checks", []))
    gates = by_id(load_yaml("catalog/gates.yaml").get("gates", []))
    check_id = "api.architecture_implementation_conformance"
    check = checks.get(check_id)
    if not check:
        fail("architecture implementation conformance check must remain present")
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


def validate_mobile_licensing_hardening(hardening: bool) -> None:
    if not hardening:
        return
    checks = by_id(load_yaml("catalog/checks.yaml").get("checks", []))
    gates = by_id(load_yaml("catalog/gates.yaml").get("gates", []))
    required_checks = {
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
    if not required_checks.issubset(checks):
        fail("0.5.3-dev mobile licensing checks incomplete")
    gate = gates.get("mobile_licensing_ready")
    if not gate or gate.get("applicability_capability") != "mobile_licensing":
        fail("0.5.3-dev mobile_licensing_ready conditional gate missing")
    if not required_checks.issubset(set(gate.get("require_all", []))):
        fail("mobile_licensing_ready does not aggregate the full licensing contract")
    release = gates.get("release_gate", {})
    if "mobile_licensing_ready" not in set(release.get("prerequisite_gates_if_applicable", [])):
        fail("release_gate must depend conditionally on mobile_licensing_ready")
    print("PASS 0.5.3-dev conditional mobile licensing catalog semantics")


def validate_workflows(hardening: bool) -> None:
    expected_lifecycle = ["INVENTORIED", "READY", "IN_PROGRESS", "FUNCTIONAL", "ACCEPTED"]
    expected_version = DEV_V53 if hardening else STABLE_V5
    for path in ("workflows/greenfield.yaml", "workflows/brownfield.yaml"):
        workflow = load_yaml(path)
        if workflow.get("version") != expected_version:
            fail(f"{path} expected component version {expected_version}")
        assert_contiguous(workflow.get("sequence", []), POST_API_PIPELINE, path)
        pipeline = workflow.get("functional_interface_slice_pipeline", {})
        if pipeline.get("scope_key") != "interface_slice_platform" or pipeline.get("lifecycle") != expected_lifecycle:
            fail(f"{path} Functional Interface Slice lifecycle/scope drifted")
        blocker = pipeline.get("blocker_condition", {})
        if blocker.get("id") != "BLOCKED_BY_API" or blocker.get("overlays_lifecycle") is not True:
            fail(f"{path} BLOCKED_BY_API semantics drifted")
        if hardening:
            licensing = workflow.get("conditional_capabilities", {}).get("mobile_licensing", {})
            if licensing.get("applicability") != "CONDITIONAL":
                fail(f"{path} mobile licensing must be conditional")
            if licensing.get("decision_required_when", {}).get("android") is not True:
                fail(f"{path} Android licensing decision must be explicit")
            if licensing.get("enabled_when", {}).get("mobile_licensing") is not True:
                fail(f"{path} mobile licensing enable condition drifted")
            if licensing.get("exit_gate") != "mobile_licensing_ready":
                fail(f"{path} mobile licensing must exit through mobile_licensing_ready")
    label = DEV_V53 if hardening else STABLE_V52
    print(f"PASS workflow semantics for {label}")


def validate_reference_pilot_history() -> None:
    catalog = load_yaml("catalog/reference-pilots.yaml")
    if catalog.get("version") != STABLE_V5:
        fail("reference pilot registry component must retain 0.5.0 provenance")
    pilot = next((p for p in catalog.get("pilots", []) if p.get("id") == "careshift-manager"), None)
    if not pilot or pilot.get("baseline_blueprint") != "0.3.0":
        fail("CareShift historical reference-pilot facts drifted")
    print("PASS reference pilot history preserved")


def validate_active_docs(hardening: bool) -> None:
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

    if hardening:
        path = ROOT / "documentation/BLUEPRINT_V0_5_3_MOBILE_LICENSING.md"
        if not path.is_file():
            fail("0.5.3-dev mobile licensing hardening document missing")
        text = path.read_text(encoding="utf-8")
        for token in ("0.5.3-dev", "mobile_licensing", "mobile_licensing_ready", "Mandatory test contract", "separate protected issuer"):
            if token not in text:
                fail(f"0.5.3-dev licensing document missing token: {token}")
        print("PASS stable 0.5.2 docs preserved + 0.5.3-dev hardening document present")
    else:
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
    hardening = is_v53_hardening()
    validate_root_and_component_identity(hardening)
    validate_schema_provenance(hardening)
    validate_historical_releases()
    validate_v52_release_manifest()
    validate_reference_pilot_history()
    validate_architecture_conformance_semantics()
    validate_ci_runtime_semantics()
    validate_core_v5_semantics()
    validate_mobile_licensing_hardening(hardening)
    validate_workflows(hardening)
    validate_active_docs(hardening)

    validators = list(BASE_VALIDATORS)
    if hardening:
        validators.append("scripts/validate-mobile-licensing.py")
    for validator in validators:
        run_validator(validator)

    state = DEV_V53 if hardening else f"stable {STABLE_V52}"
    print(f"\nBlueprint validation: PASS (state={state}; root VERSION={VERSION}; counts={catalog_counts()})")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
