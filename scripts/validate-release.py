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
DEV_V5 = "0.5.0-dev"

V4_COUNTS = {
    "phases": 25,
    "checks": 92,
    "gates": 14,
    "materialized_skills": 13,
    "planned_skills": 25,
}

V4_ACTIVE_VERSIONED_FILES = [
    "catalog/phases.yaml",
    "catalog/checks.yaml",
    "catalog/gates.yaml",
    "catalog/skills.yaml",
    "catalog/reference-pilots.yaml",
    "workflows/greenfield.yaml",
    "workflows/brownfield.yaml",
]

V5_DEV_VERSIONED_FILES = [
    "catalog/phases.yaml",
    "catalog/checks.yaml",
    "catalog/gates.yaml",
    "workflows/greenfield.yaml",
    "workflows/brownfield.yaml",
]

V5_STILL_STABLE_FILES = [
    "catalog/skills.yaml",
    "catalog/reference-pilots.yaml",
]

V4_POST_API_PIPELINE = [
    "interface_inventory",
    "visual_identity",
    "design_system",
    "mockup_planning",
    "mockups",
    "visual_review_gate",
    "client_architecture",
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


def assert_contiguous(sequence: list[str], subsequence: list[str], label: str) -> None:
    for index in range(0, len(sequence) - len(subsequence) + 1):
        if sequence[index : index + len(subsequence)] == subsequence:
            return
    fail(f"{label} does not contain expected pipeline contiguously: {subsequence}")


def catalog_counts() -> dict[str, int]:
    phases = load_yaml("catalog/phases.yaml")
    checks = load_yaml("catalog/checks.yaml")
    gates = load_yaml("catalog/gates.yaml")
    skills = load_yaml("catalog/skills.yaml")
    return {
        "phases": len(phases.get("phases", [])),
        "checks": len(checks.get("checks", [])),
        "gates": len(gates.get("gates", [])),
        "materialized_skills": len(skills.get("registry", {})),
        "planned_skills": planned_skill_count(skills),
    }


def validate_historical_v4_release_manifest() -> None:
    release = load_json("documentation/BLUEPRINT_V0_4_RELEASE.json")
    if release.get("version") != STABLE_V4 or release.get("status") != "stable":
        fail("historical v0.4 release manifest must remain stable and unchanged")
    if release.get("previous_stable") != "0.3.0":
        fail("historical v0.4 previous stable version drifted")
    if release.get("tag") != "v0.4.0":
        fail("historical v0.4 tag drifted")
    if release.get("counts") != V4_COUNTS:
        fail("historical v0.4 release counts drifted")
    compatibility = release.get("compatibility", {})
    if compatibility != {
        "consumer_auto_upgrade": False,
        "brownfield_align_do_not_rewrite": True,
        "grandfather_existing_evidence": True,
    }:
        fail("historical v0.4 compatibility policy drifted")


def validate_reference_pilot_registry() -> None:
    catalog = load_yaml("catalog/reference-pilots.yaml")
    pilot = next(
        (item for item in catalog.get("pilots", []) if item.get("id") == "careshift-manager"),
        None,
    )
    if not pilot:
        fail("careshift-manager missing from reference pilot registry")
    if pilot.get("baseline_blueprint") != "0.3.0":
        fail("reference pilot baseline must remain 0.3.0")
    review = pilot.get("last_compliance_review", {})
    if review.get("target_blueprint") != "0.4.0-dev":
        fail("reference pilot historical compliance target must remain 0.4.0-dev")
    if review.get("consumer_version_change") != "DEFERRED":
        fail("reference pilot consumer upgrade must remain deferred")


def validate_stable_v4() -> None:
    if VERSION != STABLE_V4:
        fail(f"stable v0.4 mode requires VERSION={STABLE_V4}, got {VERSION}")

    for path in V4_ACTIVE_VERSIONED_FILES:
        document = load_yaml(path)
        if document.get("version") != VERSION:
            fail(f"{path} version must match stable VERSION ({VERSION})")

    project_example = load_yaml("templates/project.example.yaml")
    status_example = load_yaml("templates/status.example.yaml")
    if project_example.get("blueprint", {}).get("version") != VERSION:
        fail("templates/project.example.yaml must target stable VERSION")
    if status_example.get("blueprint_version") != VERSION:
        fail("templates/status.example.yaml must target stable VERSION")

    actual_counts = catalog_counts()
    if actual_counts != V4_COUNTS:
        fail(f"stable v0.4 core counts drifted: expected {V4_COUNTS}, got {actual_counts}")

    for path in ("workflows/greenfield.yaml", "workflows/brownfield.yaml"):
        workflow = load_yaml(path)
        assert_contiguous(workflow.get("sequence", []), V4_POST_API_PIPELINE, path)
        if workflow.get("gates", {}).get("per_interface_slice_after_visual_review") != "visual_review_pass":
            fail(f"{path} must map visual review to visual_review_pass in stable v0.4 mode")
        if workflow.get("gates", {}).get("per_interface_slice_platform_before_implementation") != "client_architecture_ready":
            fail(f"{path} must map client architecture to scoped gate in stable v0.4 mode")

    validate_historical_v4_release_manifest()

    for path in (
        "README.md",
        "documentation/BLUEPRINT_CURRENT_STATE.md",
        "documentation/BLUEPRINT_V0_4_RELEASE_NOTES.md",
    ):
        text = (ROOT / path).read_text(encoding="utf-8")
        if "0.4.0" not in text:
            fail(f"{path} does not identify Blueprint 0.4.0")

    print(f"PASS stable v0.4 identity and counts: {V4_COUNTS}")
    print("PASS stable v0.4 post-API pipeline")


def validate_v5_development_identity() -> None:
    if VERSION != STABLE_V4:
        fail(
            f"v0.5 development mode keeps VERSION at last stable {STABLE_V4}; got {VERSION}"
        )

    for path in V5_DEV_VERSIONED_FILES:
        document = load_yaml(path)
        if document.get("version") != DEV_V5:
            fail(f"{path} must declare {DEV_V5} during V5 development")

    for path in V5_STILL_STABLE_FILES:
        document = load_yaml(path)
        if document.get("version") != STABLE_V4:
            fail(
                f"{path} remains on {STABLE_V4} until its dedicated V5 boundary; "
                f"got {document.get('version')}"
            )

    project_example = load_yaml("templates/project.example.yaml")
    status_example = load_yaml("templates/status.example.yaml")
    if project_example.get("blueprint", {}).get("version") != STABLE_V4:
        fail("project example must remain on stable v0.4 until V5 schema/template boundary")
    if status_example.get("blueprint_version") != STABLE_V4:
        fail("status example must remain on stable v0.4 until V5 schema/template boundary")

    blueprint = (ROOT / "BLUEPRINT.md").read_text(encoding="utf-8")
    required_tokens = [
        "0.5.0-dev",
        "Interface Scope Baseline",
        "Functional Interface Slice",
        "BLOCKED_BY_API",
        "Visual & Functional Review",
        "impact",
        "hardcodeados",
        "README.md",
    ]
    for token in required_tokens:
        if token not in blueprint:
            fail(f"BLUEPRINT.md missing V5 development token: {token}")

    validate_historical_v4_release_manifest()
    validate_reference_pilot_registry()
    print("PASS V5 development identity: stable VERSION preserved, V5 catalogs/workflows explicit")


def validate_v5_catalog_semantics() -> None:
    phases_doc = load_yaml("catalog/phases.yaml")
    checks_doc = load_yaml("catalog/checks.yaml")
    gates_doc = load_yaml("catalog/gates.yaml")

    phase_by_id = {item["id"]: item for item in phases_doc.get("phases", [])}
    check_by_id = {item["id"]: item for item in checks_doc.get("checks", [])}
    gate_by_id = {item["id"]: item for item in gates_doc.get("gates", [])}

    required_phases = {
        "interface_scope_baseline",
        "interface_inventory",
        "design_system",
        "client_architecture",
        "functional_interface_slice",
        "web_implementation",
        "android_implementation",
        "visual_functional_review",
        "integration_qa",
        "mockup_planning",
        "mockups",
        "mockup_review",
    }
    missing_phases = sorted(required_phases - set(phase_by_id))
    if missing_phases:
        fail(f"V5 catalog missing phases: {missing_phases}")

    scope_phase = phase_by_id["interface_scope_baseline"]
    if scope_phase.get("requires_gates") != ["requirements_ready"]:
        fail("interface_scope_baseline must follow requirements_ready")
    if scope_phase.get("exit_gate") != "interface_scope_ready":
        fail("interface_scope_baseline must exit through interface_scope_ready")

    inventory_requires = set(phase_by_id["interface_inventory"].get("requires_gates", []))
    if inventory_requires != {"api_gate", "interface_scope_ready"}:
        fail("interface_inventory must reconcile both API Gate and Interface Scope Baseline")

    if phase_by_id["visual_identity"].get("applicability") != "CONDITIONAL":
        fail("visual_identity must be CONDITIONAL in V5")
    if phase_by_id["functional_interface_slice"].get("execution_scope") != "interface_slice_platform":
        fail("functional_interface_slice must be scoped to interface_slice_platform")

    for gate_id, scope in V5_REQUIRED_GATES.items():
        gate = gate_by_id.get(gate_id)
        if gate is None:
            fail(f"V5 catalog missing gate: {gate_id}")
        if gate.get("evaluation_scope", "project") != scope:
            fail(f"{gate_id} must use scope {scope}")

    scope_required = set(gate_by_id["interface_scope_ready"].get("require_all", []))
    if scope_required != {"ui.interface_scope_baseline", "ui.interface_scope_traceability"}:
        fail("interface_scope_ready required check set drifted")
    if "ui.brownfield_observed_interface_scope" not in set(
        gate_by_id["interface_scope_ready"].get("require_if_applicable", [])
    ):
        fail("interface_scope_ready must preserve Brownfield observed interface scope")

    if "api.change_impact_analysis" not in set(
        gate_by_id["api_contract_ready"].get("require_if_applicable", [])
    ):
        fail("api_contract_ready must require impact analysis for post-baseline changes")
    if "api.affected_consumer_revalidation" not in set(
        gate_by_id["api_qa_pass"].get("require_if_applicable", [])
    ):
        fail("api_qa_pass must support affected consumer revalidation")

    client_gate = gate_by_id["client_architecture_ready"]
    client_blocks = set(client_gate.get("blocks", []))
    if not {"functional_interface_slice", "web_implementation", "android_implementation"}.issubset(client_blocks):
        fail("client_architecture_ready must block functional implementation profiles")
    if "visual_functional_review" in client_blocks:
        fail("client architecture gate must not skip functional implementation")

    functional_required = set(gate_by_id["functional_slice_ready"].get("require_all", []))
    for check_id in {
        "functional.real_api_integration",
        "functional.no_hardcoded_business_data",
        "functional.no_invented_capabilities",
        "functional.traceability",
    }:
        if check_id not in functional_required:
            fail(f"functional_slice_ready missing required check: {check_id}")

    review_required = set(gate_by_id["visual_functional_review_pass"].get("require_all", []))
    if "review.human_complete" not in review_required:
        fail("Visual & Functional Review must require explicit human completion")

    release_required = set(gate_by_id["release_gate"].get("require_all", []))
    if "release.functional_slices_accepted" not in release_required:
        fail("Release Gate must aggregate accepted functional slices")

    if check_by_id.get("design.identity", {}).get("type") != "CONDITIONAL":
        fail("design.identity must be CONDITIONAL in V5")

    print(
        "PASS V5 catalog semantics: "
        f"{len(phase_by_id)} phases, {len(check_by_id)} checks, {len(gate_by_id)} gates"
    )


def validate_v5_workflows() -> None:
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
    expected_lifecycle = [
        "INVENTORIED",
        "READY",
        "IN_PROGRESS",
        "FUNCTIONAL",
        "ACCEPTED",
    ]

    for path in ("workflows/greenfield.yaml", "workflows/brownfield.yaml"):
        workflow = load_yaml(path)
        sequence = workflow.get("sequence", [])
        assert_contiguous(sequence, V5_POST_API_PIPELINE, path)

        requirements_index = sequence.index("requirements_domain")
        scope_index = sequence.index("interface_scope_baseline")
        architecture_index = sequence.index("architecture_security_data")
        if not requirements_index < scope_index < architecture_index:
            fail(f"{path} must place Interface Scope Baseline between requirements and architecture")

        forbidden_main = {"visual_identity", "mockup_planning", "mockups", "mockup_review"}
        leaked = sorted(forbidden_main & set(sequence))
        if leaked:
            fail(f"{path} keeps conditional visual phases in principal sequence: {leaked}")

        gates = workflow.get("gates", {})
        for key, value in expected_gate_map.items():
            if gates.get(key) != value:
                fail(f"{path} gate mapping {key} must be {value}, got {gates.get(key)}")

        api_evolution = workflow.get("api_contract_evolution", {})
        if api_evolution.get("initial_baseline_gate") != "api_gate":
            fail(f"{path} must retain project API Gate as initial baseline")
        if api_evolution.get("post_baseline_change_policy") != "impact_based_revalidation":
            fail(f"{path} must use impact-based post-baseline API revalidation")
        if api_evolution.get("operation_level_key") != "operationId":
            fail(f"{path} API impact graph must use canonical operationId")

        pipeline = workflow.get("functional_interface_slice_pipeline", {})
        if pipeline.get("scope_key") != "interface_slice_platform":
            fail(f"{path} functional pipeline scope must be interface_slice_platform")
        if pipeline.get("lifecycle") != expected_lifecycle:
            fail(f"{path} lifecycle drifted: {pipeline.get('lifecycle')}")

        quality_gates = pipeline.get("quality_gates", {})
        expected_quality_gates = {
            "functional": "functional_slice_ready",
            "visual_functional_review": "visual_functional_review_pass",
            "integration_qa": "integration_qa_pass",
        }
        if quality_gates != expected_quality_gates:
            fail(f"{path} quality gate mapping drifted: {quality_gates}")

        blocker = pipeline.get("blocker_condition", {})
        if blocker.get("id") != "BLOCKED_BY_API":
            fail(f"{path} must expose BLOCKED_BY_API blocker condition")
        if blocker.get("overlays_lifecycle") is not True:
            fail(f"{path} BLOCKED_BY_API must overlay rather than replace lifecycle")
        if blocker.get("preserves_last_lifecycle_state") is not True:
            fail(f"{path} BLOCKED_BY_API must preserve last lifecycle state")
        if blocker.get("resume_requires_resolution_evidence") is not True:
            fail(f"{path} BLOCKED_BY_API resume must require resolution evidence")

        implementations = pipeline.get("client_implementation", {})
        if implementations != {"web": "web_implementation", "android": "android_implementation"}:
            fail(f"{path} client implementation profiles drifted: {implementations}")

        conditional = workflow.get("conditional_capabilities", {})
        identity = conditional.get("visual_identity", {})
        if identity.get("applicability") != "CONDITIONAL":
            fail(f"{path} visual_identity must be conditional")
        mockups = conditional.get("mockups_prototypes", {})
        if mockups.get("sequence") != ["mockup_planning", "mockups", "mockup_review"]:
            fail(f"{path} mockup conditional sequence drifted")
        if mockups.get("exit_gate") != "mockup_review_pass":
            fail(f"{path} mockup branch must exit through mockup_review_pass")
        if mockups.get("default_blocks_functional_delivery") is not False:
            fail(f"{path} mockups must not universally block functional delivery")

    print("PASS V5 Greenfield/Brownfield audit-hardened functional delivery workflows")


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
    phases_version = load_yaml("catalog/phases.yaml").get("version")

    if phases_version == STABLE_V4:
        validate_stable_v4()
        mode = "stable-v0.4"
    elif phases_version == DEV_V5:
        validate_v5_development_identity()
        validate_v5_catalog_semantics()
        validate_v5_workflows()
        mode = "development-v0.5"
    else:
        fail(
            f"unsupported Blueprint validation state: VERSION={VERSION}, "
            f"catalog/phases.version={phases_version}"
        )

    for validator in VALIDATORS:
        run_validator(validator)

    print(
        f"\nBlueprint state validation: PASS ({mode}; VERSION={VERSION}; "
        f"catalog counts={catalog_counts()})"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
