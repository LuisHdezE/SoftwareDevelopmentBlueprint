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
STABLE_V53 = "0.5.3"

V4_COUNTS = {"phases": 25, "checks": 92, "gates": 14, "materialized_skills": 13, "planned_skills": 25}
V5_COUNTS = {"phases": 28, "checks": 134, "gates": 18, "materialized_skills": 14, "planned_skills": 25}
V51_COUNTS = {"phases": 28, "checks": 135, "gates": 18, "materialized_skills": 14, "planned_skills": 25}
V52_COUNTS = dict(V51_COUNTS)
V53_COUNTS = {"phases": 28, "checks": 145, "gates": 19, "materialized_skills": 15, "planned_skills": 25}

UNCHANGED_V5_SCHEMAS = [
    "schemas/api-impact.schema.json", "schemas/client-architecture.schema.json",
    "schemas/client-platform-architecture.schema.json", "schemas/evidence.schema.json",
    "schemas/functional-interface-slice.schema.json", "schemas/interface-inventory.schema.json",
    "schemas/mockup-batch.schema.json", "schemas/design-system.schema.json",
    "schemas/design-tokens.schema.json", "schemas/reference-pilots.schema.json",
    "schemas/compliance-review.schema.json",
]
SCHEMA_VERSION_CONST_V5 = [
    "schemas/api-impact.schema.json", "schemas/client-architecture.schema.json",
    "schemas/client-platform-architecture.schema.json", "schemas/evidence.schema.json",
    "schemas/functional-interface-slice.schema.json", "schemas/interface-inventory.schema.json",
    "schemas/mockup-batch.schema.json", "schemas/design-system.schema.json",
    "schemas/design-tokens.schema.json",
]
POST_API_PIPELINE = [
    "interface_inventory", "design_system", "client_architecture",
    "functional_interface_slice", "visual_functional_review", "integration_qa",
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
    "mobile_licensing_ready": "project",
}
VALIDATORS = [
    "scripts/validate-experience-artifacts.py",
    "scripts/validate-skills.py",
    "scripts/validate-client-architecture.py",
    "scripts/validate-reference-pilot-compliance.py",
    "scripts/validate-architecture-conformance.py",
    "scripts/validate-ci-runtime.py",
    "scripts/validate-mobile-licensing.py",
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
    seen: set[str] = set()
    for category, values in catalog.get("planned_registry", {}).items():
        if not isinstance(values, list):
            fail(f"planned_registry.{category} must be a list")
        for skill_id in values:
            if skill_id in seen:
                fail(f"planned skill duplicated: {skill_id}")
            seen.add(skill_id)
    return len(seen)


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
    for index in range(len(sequence) - len(subsequence) + 1):
        if sequence[index:index + len(subsequence)] == subsequence:
            return
    fail(f"{label} missing expected contiguous pipeline: {subsequence}")


def validate_root_and_components() -> None:
    if VERSION != STABLE_V53:
        fail(f"stable release requires VERSION={STABLE_V53}, got {VERSION}")
    for path in ("catalog/checks.yaml", "catalog/gates.yaml", "catalog/skills.yaml", "workflows/greenfield.yaml", "workflows/brownfield.yaml"):
        if load_yaml(path).get("version") != STABLE_V53:
            fail(f"{path} must declare stable 0.5.3")
    if load_yaml("catalog/phases.yaml").get("version") != STABLE_V5:
        fail("unchanged phases must retain 0.5.0 provenance")
    if load_yaml("catalog/reference-pilots.yaml").get("version") != STABLE_V5:
        fail("reference pilots must retain 0.5.0 provenance")
    if load_yaml("templates/project.example.yaml").get("blueprint", {}).get("version") != STABLE_V53:
        fail("project template must declare 0.5.3")
    if load_yaml("templates/status.example.yaml").get("blueprint_version") != STABLE_V53:
        fail("status template must declare 0.5.3")
    if load_yaml("templates/mobile-licensing.example.yaml").get("schema_version") != STABLE_V53:
        fail("mobile licensing template must declare 0.5.3")
    actual = catalog_counts()
    if actual != V53_COUNTS:
        fail(f"stable 0.5.3 core counts drifted: expected {V53_COUNTS}, got {actual}")
    print(f"PASS root/component identity and counts: {V53_COUNTS}")


def validate_schema_provenance() -> None:
    project = load_json("schemas/project.schema.json")
    status = load_json("schemas/status.schema.json")
    licensing = load_json("schemas/mobile-licensing.schema.json")
    for name, schema in (("project", project), ("status", status), ("mobile licensing", licensing)):
        Draft202012Validator.check_schema(schema)
        if f"/blueprint/{STABLE_V53}/" not in schema.get("$id", ""):
            fail(f"{name} schema must be version-pinned to 0.5.3")
    if project["properties"]["blueprint"]["properties"]["version"].get("const") != STABLE_V53:
        fail("project schema consumer version must be const 0.5.3")
    if status["properties"]["blueprint_version"].get("const") != STABLE_V53:
        fail("status schema blueprint_version must be const 0.5.3")
    if licensing["properties"]["schema_version"].get("const") != STABLE_V53:
        fail("mobile licensing schema_version must be const 0.5.3")

    ci_runtime = load_json("schemas/ci-runtime.schema.json")
    Draft202012Validator.check_schema(ci_runtime)
    if "/blueprint/0.5.2/" not in ci_runtime.get("$id", "") or ci_runtime["properties"]["schema_version"].get("const") != STABLE_V52:
        fail("0.5.3 must retain CI runtime component provenance 0.5.2")
    for path in UNCHANGED_V5_SCHEMAS:
        schema = load_json(path)
        if "/blueprint/0.5.0/" not in schema.get("$id", ""):
            fail(f"unchanged schema must retain 0.5.0 provenance: {path}")
    for path in SCHEMA_VERSION_CONST_V5:
        value = load_json(path).get("properties", {}).get("schema_version", {}).get("const")
        if value != STABLE_V5:
            fail(f"unchanged schema_version must remain 0.5.0: {path}")
    print("PASS stable 0.5.3 schema provenance with compatible historical components")


def validate_historical_releases() -> None:
    v4 = load_json("documentation/BLUEPRINT_V0_4_RELEASE.json")
    if v4.get("version") != STABLE_V4 or v4.get("status") != "stable" or v4.get("tag") != "v0.4.0" or v4.get("counts") != V4_COUNTS:
        fail("historical v0.4 release drifted")
    v5 = load_json("documentation/BLUEPRINT_V0_5_RELEASE.json")
    if v5.get("version") != STABLE_V5 or v5.get("status") != "stable" or v5.get("previous_stable") != STABLE_V4 or v5.get("tag") != "v0.5.0" or v5.get("counts") != V5_COUNTS:
        fail("historical v0.5.0 release drifted")
    v51 = load_json("documentation/BLUEPRINT_V0_5_1_RELEASE.json")
    if v51.get("version") != STABLE_V51 or v51.get("status") != "stable" or v51.get("previous_stable") != STABLE_V5 or v51.get("tag") != "v0.5.1" or v51.get("counts") != V51_COUNTS:
        fail("historical v0.5.1 release drifted")
    if v51.get("hardening_boundary", {}).get("pull_request") != 19 or v51.get("hardening_boundary", {}).get("merge_commit") != "8a59fa6784430eb103258c7c808922d53fa54e63":
        fail("historical v0.5.1 hardening provenance drifted")
    v52 = load_json("documentation/BLUEPRINT_V0_5_2_RELEASE.json")
    if v52.get("version") != STABLE_V52 or v52.get("status") != "stable" or v52.get("previous_stable") != STABLE_V51 or v52.get("tag") != "v0.5.2" or v52.get("counts") != V52_COUNTS:
        fail("historical v0.5.2 release drifted")
    if v52.get("pre_release_main") != "c043bead93e9c4ad6c806576623f228dae239216":
        fail("historical v0.5.2 pre-release main drifted")
    if v52.get("hardening_boundary", {}).get("pull_request") != 22 or v52.get("hardening_boundary", {}).get("merge_commit") != "c043bead93e9c4ad6c806576623f228dae239216":
        fail("historical v0.5.2 hardening provenance drifted")
    print("PASS historical stable releases 0.4.0 through 0.5.2 preserved")


def validate_v53_manifest() -> None:
    release = load_json("documentation/BLUEPRINT_V0_5_3_RELEASE.json")
    if release.get("version") != STABLE_V53 or release.get("status") != "stable":
        fail("0.5.3 release manifest must declare stable 0.5.3")
    if release.get("release_date") != "2026-09-10" or release.get("previous_stable") != STABLE_V52 or release.get("tag") != "v0.5.3":
        fail("0.5.3 release identity/date/lineage drifted")
    hardening_sha = "5524f9b34f8328e3e6a9c88852fc8df70d9e437e"
    if release.get("pre_release_main") != hardening_sha:
        fail("0.5.3 pre_release_main must be accepted PR #25 merge")
    boundary = release.get("hardening_boundary", {})
    if boundary.get("pull_request") != 25 or boundary.get("merge_commit") != hardening_sha:
        fail("0.5.3 hardening boundary provenance drifted")
    if release.get("counts") != V53_COUNTS:
        fail("0.5.3 release counts drifted")
    expected_compatibility = {
        "consumer_auto_upgrade": False,
        "brownfield_align_do_not_rewrite": True,
        "grandfather_existing_evidence": True,
        "mockups_conditional": True,
        "impact_based_api_revalidation": True,
        "unchanged_component_provenance_reuse": True,
        "ci_execution_portability_preserved": True,
        "mobile_licensing_optional": True,
        "android_mobile_licensing_decision_required": True,
        "default_offline_signed_activation": True,
        "api_less_local_authoritative_gap_not_included": True,
    }
    if release.get("compatibility") != expected_compatibility:
        fail("0.5.3 compatibility policy drifted")
    expected_provenance = {
        "root_release": "0.5.3",
        "project_schema": "0.5.3",
        "status_schema": "0.5.3",
        "project_status_templates": "0.5.3",
        "mobile_licensing_schema_template": "0.5.3",
        "checks_gates_skills_workflows": "0.5.3",
        "mobile_licensing_skill": "0.5.3",
        "ci_runtime_contract": "0.5.2-compatible",
        "architecture_implementation_conformance": "0.5.1-compatible",
        "unchanged_phases_reference_pilots_experience_contracts": "0.5.0-compatible",
    }
    if release.get("component_provenance") != expected_provenance:
        fail("0.5.3 component provenance manifest drifted")
    policy = release.get("consumer_policy", {})
    if policy.get("automatic_adoption") is not False or policy.get("compliance_review_required") is not True or policy.get("explicit_consumer_change_required") is not True:
        fail("0.5.3 consumer adoption policy drifted")
    print("PASS stable v0.5.3 release manifest")


def validate_architecture_conformance_semantics() -> None:
    checks = by_id(load_yaml("catalog/checks.yaml").get("checks", []))
    gates = by_id(load_yaml("catalog/gates.yaml").get("gates", []))
    check_id = "api.architecture_implementation_conformance"
    check = checks.get(check_id)
    if not check or check.get("phase") != "api_implementation" or check.get("type") != "REQUIRED" or check.get("verification") != "evidence":
        fail("architecture implementation conformance check classification drifted")
    for gate_id in ("api_implemented", "api_gate"):
        if check_id not in set(gates[gate_id].get("require_all", [])):
            fail(f"{gate_id} must require architecture implementation conformance")
    print("PASS retained 0.5.1 architecture conformance semantics")


def validate_core_semantics() -> None:
    phases = by_id(load_yaml("catalog/phases.yaml").get("phases", []))
    gates = by_id(load_yaml("catalog/gates.yaml").get("gates", []))
    if phases["interface_scope_baseline"].get("requires_gates") != ["requirements_ready"]:
        fail("Interface Scope Baseline ownership drifted")
    if set(phases["interface_inventory"].get("requires_gates", [])) != {"api_gate", "interface_scope_ready"}:
        fail("Executable Interface Inventory gate dependencies drifted")
    if phases["visual_identity"].get("applicability") != "CONDITIONAL":
        fail("Visual Identity must remain conditional")
    if phases["functional_interface_slice"].get("execution_scope") != "interface_slice_platform":
        fail("Functional Interface Slice scope drifted")
    for gate_id, scope in REQUIRED_SCOPED_GATES.items():
        gate = gates.get(gate_id)
        if not gate or gate.get("evaluation_scope", "project") != scope:
            fail(f"{gate_id} must use scope {scope}")
    if "review.human_complete" not in set(gates["visual_functional_review_pass"].get("require_all", [])):
        fail("Visual & Functional Review must require human completion")
    print("PASS stable 0.5.x core semantics")


def validate_mobile_licensing_semantics() -> None:
    checks = by_id(load_yaml("catalog/checks.yaml").get("checks", []))
    gates = by_id(load_yaml("catalog/gates.yaml").get("gates", []))
    required = {
        "requirements.mobile_licensing_decision", "licensing.profile_contract",
        "licensing.security_architecture", "licensing.private_key_isolation",
        "licensing.backup_separation", "licensing.issuer_boundary",
        "licensing.key_lifecycle", "licensing.automated_tests",
        "licensing.interoperability", "licensing.release_build",
    }
    if not required.issubset(checks):
        fail("stable 0.5.3 mobile licensing checks incomplete")
    gate = gates.get("mobile_licensing_ready")
    if not gate or gate.get("applicability_capability") != "mobile_licensing" or not required.issubset(set(gate.get("require_all", []))):
        fail("mobile_licensing_ready gate contract incomplete")
    if "mobile_licensing_ready" not in set(gates["release_gate"].get("prerequisite_gates_if_applicable", [])):
        fail("release_gate must depend conditionally on mobile_licensing_ready")
    project = load_json("schemas/project.schema.json")
    text = json.dumps(project)
    if "mobile_licensing" not in text:
        fail("project schema missing mobile licensing applicability decision")
    print("PASS stable 0.5.3 optional mobile licensing semantics")


def validate_workflows() -> None:
    expected_lifecycle = ["INVENTORIED", "READY", "IN_PROGRESS", "FUNCTIONAL", "ACCEPTED"]
    for path in ("workflows/greenfield.yaml", "workflows/brownfield.yaml"):
        workflow = load_yaml(path)
        if workflow.get("version") != STABLE_V53:
            fail(f"{path} must declare 0.5.3")
        assert_contiguous(workflow.get("sequence", []), POST_API_PIPELINE, path)
        pipeline = workflow.get("functional_interface_slice_pipeline", {})
        if pipeline.get("scope_key") != "interface_slice_platform" or pipeline.get("lifecycle") != expected_lifecycle:
            fail(f"{path} functional slice lifecycle/scope drifted")
        blocker = pipeline.get("blocker_condition", {})
        if blocker.get("id") != "BLOCKED_BY_API" or blocker.get("overlays_lifecycle") is not True:
            fail(f"{path} BLOCKED_BY_API semantics drifted")
        licensing = workflow.get("conditional_capabilities", {}).get("mobile_licensing", {})
        if licensing.get("applicability") != "CONDITIONAL" or licensing.get("decision_required_when", {}).get("android") is not True or licensing.get("enabled_when", {}).get("mobile_licensing") is not True or licensing.get("exit_gate") != "mobile_licensing_ready":
            fail(f"{path} mobile licensing conditional branch drifted")
    print("PASS stable 0.5.3 workflow semantics")


def validate_ci_runtime_provenance() -> None:
    template = load_yaml("templates/ci-runtime.example.yaml")
    master = load_yaml("ci/blueprint-master.runtime.yaml")
    for label, document in (("template", template), ("master", master)):
        if document.get("schema_version") != STABLE_V52:
            fail(f"CI runtime {label} must retain 0.5.2 provenance")
        evidence = document.get("evidence", {})
        for key in ("exact_head_required", "check_run_required", "pre_execution_infrastructure_failures_distinct_from_test_failures"):
            if evidence.get(key) is not True:
                fail(f"CI runtime evidence invariant drifted: {label}.{key}")
        if document.get("runner", {}).get("project_docker_capability_independent") is not True:
            fail("runner infrastructure must remain independent from project Docker capability")
    print("PASS retained 0.5.2 CI execution portability semantics")


def validate_reference_pilot_history() -> None:
    catalog = load_yaml("catalog/reference-pilots.yaml")
    pilot = next((p for p in catalog.get("pilots", []) if p.get("id") == "careshift-manager"), None)
    if not pilot or pilot.get("baseline_blueprint") != "0.3.0":
        fail("CareShift historical reference pilot facts drifted")
    print("PASS reference pilot history preserved")


def validate_active_docs() -> None:
    required = {
        "BLUEPRINT.md": ["Stable release: **0.5.3**", "Optional Mobile Licensing", "mobile_licensing_ready", "CI Execution Portability"],
        "README.md": ["Blueprint 0.5.3", "145 checks", "Mobile Licensing", "Compliance Review"],
        "documentation/BLUEPRINT_CURRENT_STATE.md": ["Release representada: **0.5.3**", "145 checks", "mobile_licensing", "PR #25"],
        "documentation/BLUEPRINT_V0_5_3_MOBILE_LICENSING.md": ["stable 0.5.3", "mobile_licensing", "Mandatory test contract", "separate protected issuer"],
        "documentation/BLUEPRINT_V0_5_3_RELEASE_NOTES.md": ["Blueprint 0.5.3", "145 checks", "17", "v0.5.3", "no automatic consumer upgrade"],
    }
    for path, tokens in required.items():
        text = (ROOT / path).read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                fail(f"{path} missing stable 0.5.3 token: {token}")
    workflow = (ROOT / ".github/workflows/blueprint-release-validation.yml").read_text(encoding="utf-8")
    for path in ("documentation/BLUEPRINT_V0_5_3_RELEASE.json", "documentation/BLUEPRINT_V0_5_3_RELEASE_NOTES.md"):
        if path not in workflow:
            fail(f"release validation workflow does not watch {path}")
    print("PASS active 0.5.3 documentation and release workflow")


def run_validator(path: str) -> None:
    print(f"\n=== {path} ===")
    result = subprocess.run([sys.executable, path], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(result.stdout, end="")
    if result.returncode != 0:
        fail(f"nested validator failed: {path} (exit {result.returncode})")


def main() -> int:
    validate_root_and_components()
    validate_schema_provenance()
    validate_historical_releases()
    validate_v53_manifest()
    validate_reference_pilot_history()
    validate_architecture_conformance_semantics()
    validate_ci_runtime_provenance()
    validate_core_semantics()
    validate_mobile_licensing_semantics()
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
