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
DEV_V51 = "0.5.1-dev"

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

V51_DEV_COUNTS = {
    "phases": 28,
    "checks": 135,
    "gates": 18,
    "materialized_skills": 14,
    "planned_skills": 25,
}

ACTIVE_VERSIONED_YAML = [
    "catalog/phases.yaml",
    "catalog/checks.yaml",
    "catalog/gates.yaml",
    "catalog/skills.yaml",
    "catalog/reference-pilots.yaml",
    "workflows/greenfield.yaml",
    "workflows/brownfield.yaml",
]

SCHEMA_VERSIONED_IDS = [
    "schemas/project.schema.json",
    "schemas/status.schema.json",
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

SCHEMA_VERSION_CONST = [
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

V5_POST_API_PIPELINE = [
    "interface_inventory",
    "design_system",
    "client_architecture",
    "functional_interface_slice",
    "visual_functional_review",
    "integration_qa",
]

V5_REQUIRED_GATES = {
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


def is_v51_dev() -> bool:
    return (
        load_yaml("catalog/checks.yaml").get("version") == DEV_V51
        or load_yaml("catalog/gates.yaml").get("version") == DEV_V51
    )


def assert_contiguous(sequence: list[str], subsequence: list[str], label: str) -> None:
    for index in range(0, len(sequence) - len(subsequence) + 1):
        if sequence[index:index + len(subsequence)] == subsequence:
            return
    fail(f"{label} does not contain expected pipeline contiguously: {subsequence}")


def validate_historical_v4_release_manifest() -> None:
    release = load_json("documentation/BLUEPRINT_V0_4_RELEASE.json")
    expected_compatibility = {
        "consumer_auto_upgrade": False,
        "brownfield_align_do_not_rewrite": True,
        "grandfather_existing_evidence": True,
    }
    if release.get("version") != STABLE_V4 or release.get("status") != "stable":
        fail("historical v0.4 release manifest must remain stable")
    if release.get("previous_stable") != "0.3.0" or release.get("tag") != "v0.4.0":
        fail("historical v0.4 release lineage drifted")
    if release.get("counts") != V4_COUNTS:
        fail("historical v0.4 release counts drifted")
    if release.get("compatibility") != expected_compatibility:
        fail("historical v0.4 compatibility policy drifted")
    if release.get("historical_review_target") != "0.4.0-dev":
        fail("historical v0.4 review target drifted")
    print("PASS historical v0.4 release manifest preserved")


def validate_reference_pilot_history() -> None:
    catalog = load_yaml("catalog/reference-pilots.yaml")
    if catalog.get("version") != STABLE_V5:
        fail("reference pilot registry must identify stable Blueprint 0.5.0 during 0.5.1-dev hardening")
    pilot = next((p for p in catalog.get("pilots", []) if p.get("id") == "careshift-manager"), None)
    if not pilot:
        fail("careshift-manager missing from reference pilot registry")
    if pilot.get("baseline_blueprint") != "0.3.0":
        fail("CareShift historical consumer baseline must remain 0.3.0")
    review = pilot.get("last_compliance_review", {})
    if review.get("target_blueprint") != "0.4.0-dev":
        fail("CareShift historical compliance target must remain 0.4.0-dev")
    if review.get("consumer_version_change") != "DEFERRED":
        fail("CareShift historical consumer version change must remain DEFERRED")
    print("PASS reference pilot history preserved without consumer auto-upgrade")


def validate_release_manifest() -> None:
    release = load_json("documentation/BLUEPRINT_V0_5_RELEASE.json")
    if release.get("version") != STABLE_V5 or release.get("status") != "stable":
        fail("v0.5 release manifest must remain stable 0.5.0 during hardening")
    if release.get("previous_stable") != STABLE_V4:
        fail("v0.5 previous stable must be 0.4.0")
    if release.get("tag") != "v0.5.0":
        fail("v0.5 release tag must remain v0.5.0")
    if release.get("counts") != V5_COUNTS:
        fail(f"historical v0.5 release counts drifted: {release.get('counts')}")
    compatibility = release.get("compatibility", {})
    for key, expected in {
        "consumer_auto_upgrade": False,
        "brownfield_align_do_not_rewrite": True,
        "grandfather_existing_evidence": True,
        "mockups_conditional": True,
        "impact_based_api_revalidation": True,
    }.items():
        if compatibility.get(key) is not expected:
            fail(f"v0.5 compatibility policy drifted: {key}")
    expected_boundaries = {
        ("V5-0", 11), ("V5-1", 12), ("V5-1A", 13),
        ("V5-2", 14), ("V5-3", 15), ("V5-4", 16),
    }
    actual_boundaries = {(item.get("id"), item.get("pull_request")) for item in release.get("delivery_slices", [])}
    if actual_boundaries != expected_boundaries:
        fail(f"v0.5 delivery boundary manifest drifted: {actual_boundaries}")
    print("PASS stable v0.5 release manifest preserved")


def validate_version_identity() -> None:
    if VERSION != STABLE_V5:
        fail(f"0.5.1-dev semantic hardening preserves VERSION={STABLE_V5} until release closure; got {VERSION}")

    project = load_yaml("templates/project.example.yaml")
    status = load_yaml("templates/status.example.yaml")
    if project.get("blueprint", {}).get("version") != STABLE_V5:
        fail("canonical project example must remain on stable 0.5.0 before release closure")
    if status.get("blueprint_version") != STABLE_V5:
        fail("canonical status example must remain on stable 0.5.0 before release closure")

    for stale in ("templates/project.v0.5-dev.example.yaml", "templates/status.v0.5-dev.example.yaml"):
        if (ROOT / stale).exists():
            fail(f"development-only 0.5 template must not reappear: {stale}")

    actual_counts = catalog_counts()
    if is_v51_dev():
        checks_version = load_yaml("catalog/checks.yaml").get("version")
        gates_version = load_yaml("catalog/gates.yaml").get("version")
        if checks_version != DEV_V51 or gates_version != DEV_V51:
            fail("0.5.1-dev hardening requires checks and gates catalogs to move together")
        for path in ACTIVE_VERSIONED_YAML:
            if path in {"catalog/checks.yaml", "catalog/gates.yaml"}:
                continue
            if load_yaml(path).get("version") != STABLE_V5:
                fail(f"{path} must remain stable 0.5.0 until 0.5.1 release closure")
        if actual_counts != V51_DEV_COUNTS:
            fail(f"0.5.1-dev core counts drifted: expected {V51_DEV_COUNTS}, got {actual_counts}")
        print(f"PASS 0.5.1-dev hardening identity over stable VERSION={VERSION}: {V51_DEV_COUNTS}")
        return

    for path in ACTIVE_VERSIONED_YAML:
        if load_yaml(path).get("version") != STABLE_V5:
            fail(f"{path} must declare stable 0.5.0")
    if actual_counts != V5_COUNTS:
        fail(f"stable v0.5 core counts drifted: expected {V5_COUNTS}, got {actual_counts}")
    print(f"PASS stable v0.5 identity and counts: {V5_COUNTS}")


def validate_schema_provenance() -> None:
    for path in SCHEMA_VERSIONED_IDS:
        schema = load_json(path)
        expected_fragment = "/blueprint/0.5.0/"
        if expected_fragment not in schema.get("$id", ""):
            fail(f"{path} must remain version-pinned to stable 0.5.0 before release closure")
    for path in SCHEMA_VERSION_CONST:
        schema = load_json(path)
        value = schema.get("properties", {}).get("schema_version", {}).get("const")
        if value != STABLE_V5:
            fail(f"{path} schema_version must remain const 0.5.0")
    project = load_json("schemas/project.schema.json")
    project_version = project["properties"]["blueprint"]["properties"]["version"].get("const")
    if project_version != STABLE_V5:
        fail("project schema must pin consumer declaration to 0.5.0 before release closure")
    status = load_json("schemas/status.schema.json")
    if status["properties"]["blueprint_version"].get("const") != STABLE_V5:
        fail("status schema must pin blueprint_version to 0.5.0 before release closure")
    refs = load_json("schemas/reference-pilots.schema.json")
    if refs["properties"]["version"].get("const") != STABLE_V5:
        fail("reference pilot schema must pin registry version to 0.5.0 before release closure")
    compliance_text = json.dumps(load_json("schemas/compliance-review.schema.json"))
    if "blueprint_change" not in compliance_text or "v0_4_change" not in compliance_text:
        fail("compliance review schema must support neutral future findings and historical v0.4 findings")
    print("PASS stable schema provenance preserved during hardening")


def validate_catalog_semantics() -> None:
    phases_doc = load_yaml("catalog/phases.yaml")
    checks_doc = load_yaml("catalog/checks.yaml")
    gates_doc = load_yaml("catalog/gates.yaml")
    phase_by_id = {item["id"]: item for item in phases_doc.get("phases", [])}
    check_by_id = {item["id"]: item for item in checks_doc.get("checks", [])}
    gate_by_id = {item["id"]: item for item in gates_doc.get("gates", [])}
    required_phases = {
        "interface_scope_baseline", "interface_inventory", "design_system",
        "client_architecture", "functional_interface_slice", "web_implementation",
        "android_implementation", "visual_functional_review", "integration_qa",
        "mockup_planning", "mockups", "mockup_review",
    }
    missing = sorted(required_phases - set(phase_by_id))
    if missing:
        fail(f"v0.5 catalog missing phases: {missing}")
    scope = phase_by_id["interface_scope_baseline"]
    if scope.get("requires_gates") != ["requirements_ready"] or scope.get("exit_gate") != "interface_scope_ready":
        fail("Interface Scope Baseline ownership drifted")
    if set(phase_by_id["interface_inventory"].get("requires_gates", [])) != {"api_gate", "interface_scope_ready"}:
        fail("Executable Interface Inventory must reconcile API Gate + Interface Scope Baseline")
    if phase_by_id["visual_identity"].get("applicability") != "CONDITIONAL":
        fail("Visual Identity must remain conditional")
    if phase_by_id["functional_interface_slice"].get("execution_scope") != "interface_slice_platform":
        fail("Functional Interface Slice must remain slice+platform scoped")
    for gate_id, scope_name in V5_REQUIRED_GATES.items():
        gate = gate_by_id.get(gate_id)
        if not gate or gate.get("evaluation_scope", "project") != scope_name:
            fail(f"{gate_id} must use scope {scope_name}")
    if "api.change_impact_analysis" not in set(gate_by_id["api_contract_ready"].get("require_if_applicable", [])):
        fail("API Contract Ready must support post-baseline impact analysis")
    if "api.affected_consumer_revalidation" not in set(gate_by_id["api_qa_pass"].get("require_if_applicable", [])):
        fail("API QA must support affected-consumer revalidation")

    if is_v51_dev():
        conformance = check_by_id.get("api.architecture_implementation_conformance")
        if not conformance:
            fail("0.5.1-dev missing api.architecture_implementation_conformance")
        if conformance.get("phase") != "api_implementation" or conformance.get("type") != "REQUIRED" or conformance.get("verification") != "evidence":
            fail("architecture implementation conformance check classification drifted")
        for gate_id in ("api_implemented", "api_gate"):
            if "api.architecture_implementation_conformance" not in set(gate_by_id[gate_id].get("require_all", [])):
                fail(f"{gate_id} must require architecture implementation conformance")

    functional_required = set(gate_by_id["functional_slice_ready"].get("require_all", []))
    for check in ("functional.real_api_integration", "functional.no_hardcoded_business_data", "functional.no_invented_capabilities", "functional.traceability"):
        if check not in functional_required:
            fail(f"functional_slice_ready missing {check}")
    if "review.human_complete" not in set(gate_by_id["visual_functional_review_pass"].get("require_all", [])):
        fail("Visual & Functional Review must require human completion")
    if "release.functional_slices_accepted" not in set(gate_by_id["release_gate"].get("require_all", [])):
        fail("Release Gate must aggregate accepted functional slices")
    if check_by_id.get("design.identity", {}).get("type") != "CONDITIONAL":
        fail("design.identity must remain conditional")
    client_rule = gate_by_id["client_architecture_ready"].get("rule", "")
    if "Platform Client Architecture Baseline" not in client_rule or "slice-specific binding" not in client_rule:
        fail("Client Architecture gate must describe stable composed architecture")
    print("PASS catalog semantics including 0.5.1-dev hardening when active")


def validate_skill_semantics() -> None:
    skills = load_yaml("catalog/skills.yaml")
    if skills.get("version") != STABLE_V5:
        fail("skill catalog remains stable 0.5.0 until 0.5.1 release closure")
    registry = skills.get("registry", {})
    if set(skills.get("mandatory_v0_5_materialized", [])) != set(registry):
        fail("mandatory_v0_5_materialized must equal current materialized registry")
    entry = registry.get("dev-functional-interface-slice")
    if not entry or entry.get("path") != "skills/dev-functional-interface-slice/SKILL.md":
        fail("dev-functional-interface-slice must be materialized at canonical path")
    for category in ("web", "android"):
        if "dev-functional-interface-slice" not in set(skills.get("categories", {}).get(category, {}).get("skills", [])):
            fail(f"{category} category must include dev-functional-interface-slice")
    print("PASS stable v0.5 skill catalog semantics preserved")


def validate_workflows() -> None:
    expected_gate_map = {
        "after_interface_scope_baseline": "interface_scope_ready",
        "before_client_delivery": "api_gate",
        "after_interface_inventory": "interface_inventory_ready",
        "after_design_system": "design_system_ready",
        "per_slice_platform_before_implementation": "client_architecture_ready",
        "per_slice_platform_after_functional_dod": "functional_slice_ready",
        "per_slice_platform_after_visual_functional_review": "visual_functional_review_pass",
        "per_slice_platform_after_integration_qa": "integration_qa_pass",
        "before_release": "release_gate",
    }
    expected_lifecycle = ["INVENTORIED", "READY", "IN_PROGRESS", "FUNCTIONAL", "ACCEPTED"]
    for path in ("workflows/greenfield.yaml", "workflows/brownfield.yaml"):
        workflow = load_yaml(path)
        sequence = workflow.get("sequence", [])
        assert_contiguous(sequence, V5_POST_API_PIPELINE, path)
        if not sequence.index("requirements_domain") < sequence.index("interface_scope_baseline") < sequence.index("architecture_security_data"):
            fail(f"{path} must place Interface Scope Baseline between requirements and architecture")
        leaked = {"visual_identity", "mockup_planning", "mockups", "mockup_review"} & set(sequence)
        if leaked:
            fail(f"{path} leaked conditional visual phases into principal sequence: {sorted(leaked)}")
        for key, value in expected_gate_map.items():
            if workflow.get("gates", {}).get(key) != value:
                fail(f"{path} gate mapping {key} drifted")
        evolution = workflow.get("api_contract_evolution", {})
        if evolution.get("initial_baseline_gate") != "api_gate" or evolution.get("post_baseline_change_policy") != "impact_based_revalidation" or evolution.get("operation_level_key") != "operationId":
            fail(f"{path} API evolution policy drifted")
        pipeline = workflow.get("functional_interface_slice_pipeline", {})
        if pipeline.get("scope_key") != "interface_slice_platform" or pipeline.get("lifecycle") != expected_lifecycle:
            fail(f"{path} Functional Interface Slice lifecycle/scope drifted")
        blocker = pipeline.get("blocker_condition", {})
        if blocker.get("id") != "BLOCKED_BY_API" or blocker.get("overlays_lifecycle") is not True or blocker.get("preserves_last_lifecycle_state") is not True or blocker.get("resume_requires_resolution_evidence") is not True:
            fail(f"{path} BLOCKED_BY_API overlay semantics drifted")
        mockups = workflow.get("conditional_capabilities", {}).get("mockups_prototypes", {})
        if mockups.get("default_blocks_functional_delivery") is not False or mockups.get("exit_gate") != "mockup_review_pass":
            fail(f"{path} conditional mockup policy drifted")
    print("PASS stable v0.5 Greenfield/Brownfield workflows preserved")


def validate_active_documentation() -> None:
    active_docs = [
        "BLUEPRINT.md",
        "README.md",
        "documentation/BLUEPRINT_CURRENT_STATE.md",
        "documentation/EXPERIENCE_ARTIFACT_MODEL.md",
        "documentation/CLIENT_ARCHITECTURE_CONTRACT.md",
        "documentation/SKILL_MODEL.md",
        "skills/README.md",
        "documentation/BLUEPRINT_V0_5_RELEASE_NOTES.md",
    ]
    required_tokens = {
        "BLUEPRINT.md": ["0.5.0", "Interface Scope Baseline", "Functional Interface Slice", "BLOCKED_BY_API", "Platform Client Architecture Baseline", "Slice Architecture Binding/Override", "Cross-Artifact Semantic Integrity"],
        "README.md": ["Blueprint 0.5.0", "28", "134", "18", "14"],
        "documentation/BLUEPRINT_CURRENT_STATE.md": ["0.5.0", "28", "134", "18", "14", "Compliance Review"],
        "documentation/EXPERIENCE_ARTIFACT_MODEL.md": ["Blueprint 0.5.0", "SCOPE_BASELINE", "EXECUTABLE_INVENTORY", "BLOCKED_BY_API"],
        "documentation/CLIENT_ARCHITECTURE_CONTRACT.md": ["Blueprint 0.5.0", "Platform Client Architecture Baseline + Slice Architecture Binding", "visual_references.mode"],
        "documentation/SKILL_MODEL.md": ["Blueprint v0.5", "14"],
        "skills/README.md": ["v0.5", "dev-functional-interface-slice"],
        "documentation/BLUEPRINT_V0_5_RELEASE_NOTES.md": ["0.5.0", "Functional Interface Slice", "no automatic"],
    }
    for path in active_docs:
        text = (ROOT / path).read_text(encoding="utf-8")
        if "0.5.0-dev" in text or "0.4.0-dev" in text:
            fail(f"active stable documentation retains prerelease identity: {path}")
        for token in required_tokens[path]:
            if token not in text:
                fail(f"{path} missing stable release token: {token}")
    if is_v51_dev():
        hardening = ROOT / "documentation/BLUEPRINT_V0_5_1_ARCHITECTURE_CONFORMANCE_HARDENING.md"
        if not hardening.exists():
            fail("0.5.1-dev architecture hardening note missing")
    print("PASS stable documentation preserved with separate 0.5.1-dev hardening note")


def run_validator(path: str) -> None:
    print(f"\n=== {path} ===")
    result = subprocess.run([sys.executable, path], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(result.stdout, end="")
    if result.returncode != 0:
        fail(f"nested validator failed: {path} (exit {result.returncode})")


def main() -> int:
    validate_version_identity()
    validate_schema_provenance()
    validate_historical_v4_release_manifest()
    validate_reference_pilot_history()
    validate_release_manifest()
    validate_catalog_semantics()
    validate_skill_semantics()
    validate_workflows()
    validate_active_documentation()
    for validator in VALIDATORS:
        run_validator(validator)
    state = DEV_V51 if is_v51_dev() else STABLE_V5
    print(f"\nBlueprint release/development validation: PASS (state={state}; VERSION={VERSION}; counts={catalog_counts()})")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
