#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
STABLE_VERSION = "0.5.3"
DEVELOPMENT_VERSION = "0.5.4-dev"
TARGET_VERSION = "0.5.4"
BASELINE_COMMIT = "b1df5ca09ad38e39a1b51006aa441786afdb946c"
BASELINE_TAG = "v0.5.3"
HARDENING_CHECKPOINT = "965e2c060e2193d50d0937fd425802fb1b193c60"
CANDIDATE_DATE = "2026-09-16"
DEV_MANIFEST_PATH = ROOT / "documentation/BLUEPRINT_V0_5_4_DEVELOPMENT.json"
CANDIDATE_PATH = ROOT / "documentation/BLUEPRINT_V0_5_4_RELEASE_CANDIDATE.json"
CANDIDATE_NOTES_PATH = ROOT / "documentation/BLUEPRINT_V0_5_4_RELEASE_CANDIDATE.md"
STABLE_RELEASE_PATH = ROOT / "documentation/BLUEPRINT_V0_5_4_RELEASE.json"

EXPECTED_COUNTS = {
    "phases": 29,
    "checks": 146,
    "gates": 19,
    "materialized_skills": 16,
    "planned_skills": 25,
}
EXPECTED_FROZEN_DECISIONS = {
    "cross_platform_does_not_enable_targets": True,
    "cross_platform_does_not_share_platform_gates": True,
    "platform_acceptance_remains_independent": True,
    "mobile_licensing_android_applicability_preserved": True,
    "ios_does_not_imply_mobile_licensing": True,
    "offline_scope_is_api_backed_only": True,
    "api_less_local_authoritative_is_deferred": True,
}
EXPECTED_LINEAGE = [
    {"increment": 0, "pull_request": 31, "merge_commit": "25b74c2cd92ad7aa4171196df3cc52cc3c58954d", "scope": "governed_development_lane"},
    {"increment": 1, "pull_request": 32, "merge_commit": "408880be8536828dfe12de98c2ea511e8bdcc5a8", "scope": "platform_capability_model"},
    {"increment": 2, "pull_request": 33, "merge_commit": "8207c23ccf6ab519431a26ad564a42d960033d3f", "scope": "ios_client_architecture_contracts"},
    {"increment": 3, "pull_request": 34, "merge_commit": "fad8eef654cb7825b03e77f5eb3dae6fbf7698e0", "scope": "ios_workflows_catalogs_skills"},
    {"increment": 4, "pull_request": 35, "merge_commit": "e18eda4d2676f47cdee1f9eed68f9f1a63941b1d", "scope": "cross_artifact_ios_integrity"},
    {"increment": 5, "pull_request": 36, "merge_commit": "fc4446f869f9f903b1ef1bc3761e2ec222ac602c", "scope": "governed_platform_matrix_ci"},
    {"increment": 6, "pull_request": 37, "merge_commit": "965e2c060e2193d50d0937fd425802fb1b193c60", "scope": "mobile_licensing_regression_boundary"},
]
EXPECTED_PROVENANCE = {
    "root_release": "0.5.3-stable-until-promotion",
    "development_lane": "0.5.4-dev",
    "project_and_status_contracts": "0.5.4-dev",
    "platform_bearing_client_and_experience_contracts": "0.5.4-dev",
    "catalogs_and_workflows": "0.5.4-dev",
    "ios_client_architecture_and_functional_slice_skills": "0.5.4-dev",
    "mobile_licensing_contract": "0.5.3-compatible",
    "ci_runtime_contract": "0.5.2-compatible",
    "architecture_implementation_conformance": "0.5.1-compatible",
    "unchanged_reference_compliance_and_design_contracts": "0.5.0-compatible",
}
EXPECTED_FINAL_REQUIREMENTS = {
    "final_release_pr_required": True,
    "promote_development_contracts_to_0_5_4": True,
    "set_root_version_to_0_5_4": True,
    "remove_development_version_marker": True,
    "create_stable_release_manifest_and_notes": True,
    "update_normative_and_active_docs_to_stable_0_5_4": True,
    "post_merge_stable_validation_on_exact_sha": True,
    "tag_requires_separate_explicit_human_approval": True,
    "prospective_merge_sha_is_not_release_evidence": True,
}


def fail(message: str) -> None:
    raise AssertionError(message)


def load_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        fail(f"{path.relative_to(ROOT)} must contain an object")
    return value


def load_yaml(path: str) -> dict:
    value = yaml.safe_load((ROOT / path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        fail(f"{path} must contain a mapping")
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
    skills = load_yaml("catalog/skills.yaml")
    return {
        "phases": len(load_yaml("catalog/phases.yaml").get("phases", [])),
        "checks": len(load_yaml("catalog/checks.yaml").get("checks", [])),
        "gates": len(load_yaml("catalog/gates.yaml").get("gates", [])),
        "materialized_skills": len(skills.get("registry", {})),
        "planned_skills": planned_skill_count(skills),
    }


def skill_frontmatter(path: str) -> dict:
    text = (ROOT / path).read_text(encoding="utf-8-sig")
    if not text.startswith("---\n"):
        fail(f"{path} missing YAML frontmatter")
    end = text.find("\n---\n", 4)
    if end < 0:
        fail(f"{path} missing YAML frontmatter terminator")
    value = yaml.safe_load(text[4:end]) or {}
    if not isinstance(value, dict):
        fail(f"{path} frontmatter must be a mapping")
    return value


def validate_identity_and_candidate() -> tuple[dict, dict]:
    stable = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    development = (ROOT / "DEVELOPMENT_VERSION").read_text(encoding="utf-8").strip()
    if stable != STABLE_VERSION:
        fail(f"release closure must keep VERSION={STABLE_VERSION}; got {stable}")
    if development != DEVELOPMENT_VERSION:
        fail(f"release closure requires DEVELOPMENT_VERSION={DEVELOPMENT_VERSION}; got {development}")
    if STABLE_RELEASE_PATH.exists():
        fail("stable 0.5.4 release manifest must not exist during release closure")
    if not CANDIDATE_PATH.is_file() or not CANDIDATE_NOTES_PATH.is_file():
        fail("release candidate manifest and notes are required")

    dev = load_json(DEV_MANIFEST_PATH)
    candidate = load_json(CANDIDATE_PATH)
    if dev.get("target_version") != DEVELOPMENT_VERSION or dev.get("stable_version") != STABLE_VERSION or dev.get("status") != "hardening":
        fail("development manifest identity drifted during closure")
    if candidate.get("schema_version") != "1.0.0":
        fail("candidate schema_version drifted")
    if candidate.get("target_version") != TARGET_VERSION or candidate.get("development_version") != DEVELOPMENT_VERSION or candidate.get("stable_version") != STABLE_VERSION:
        fail("candidate version lineage drifted")
    if candidate.get("status") != "release_candidate" or candidate.get("candidate_date") != CANDIDATE_DATE:
        fail("candidate status/date drifted")
    expected_baseline = {"branch": "main", "commit": BASELINE_COMMIT, "tag": BASELINE_TAG}
    if candidate.get("baseline") != expected_baseline or dev.get("baseline") != expected_baseline:
        fail("0.5.4 baseline drifted")
    if candidate.get("hardening_complete_through_main") != HARDENING_CHECKPOINT:
        fail("candidate hardening checkpoint drifted")
    if candidate.get("hardening_lineage") != EXPECTED_LINEAGE:
        fail("candidate hardening lineage drifted")
    if candidate.get("frozen_decisions") != EXPECTED_FROZEN_DECISIONS or dev.get("frozen_decisions") != EXPECTED_FROZEN_DECISIONS:
        fail("candidate frozen decisions drifted")
    if candidate.get("component_provenance") != EXPECTED_PROVENANCE:
        fail("candidate component provenance drifted")
    if candidate.get("final_release_requirements") != EXPECTED_FINAL_REQUIREMENTS:
        fail("candidate final release requirements drifted")
    if candidate.get("consumer_policy") != {
        "automatic_adoption": False,
        "compliance_review_required": True,
        "explicit_consumer_change_required": True,
        "impact_appropriate_revalidation_required": True,
    }:
        fail("candidate consumer policy drifted")
    if candidate.get("deferred_scope") != {
        "api_less_local_authoritative_mobile": True,
        "ios_mobile_licensing_generalization": True,
        "universal_cross_platform_framework_mandate": True,
    }:
        fail("candidate deferred scope drifted")
    return dev, candidate


def validate_counts(dev: dict, candidate: dict) -> None:
    actual = catalog_counts()
    if actual != EXPECTED_COUNTS:
        fail(f"0.5.4-dev candidate counts drifted: expected {EXPECTED_COUNTS}, got {actual}")
    if candidate.get("counts") != EXPECTED_COUNTS:
        fail("candidate manifest counts do not match governed counts")
    closure = dev.get("closure", {})
    if closure.get("state") != "release_pr_ready" or closure.get("checkpoint_date") != CANDIDATE_DATE:
        fail("development closure state/date drifted")
    if closure.get("hardening_complete_through_main") != HARDENING_CHECKPOINT:
        fail("development closure checkpoint drifted")
    if closure.get("completed_increments") != list(range(7)):
        fail("development closure increment list drifted")
    if closure.get("counts") != EXPECTED_COUNTS:
        fail("development closure counts drifted")
    if closure.get("release_candidate_manifest") != "documentation/BLUEPRINT_V0_5_4_RELEASE_CANDIDATE.json":
        fail("development closure candidate manifest pointer drifted")
    if closure.get("release_candidate_notes") != "documentation/BLUEPRINT_V0_5_4_RELEASE_CANDIDATE.md":
        fail("development closure candidate notes pointer drifted")
    print(f"PASS release candidate counts and closure checkpoint: {EXPECTED_COUNTS}")


def validate_component_provenance() -> None:
    for path in ("catalog/phases.yaml", "catalog/checks.yaml", "catalog/gates.yaml", "catalog/skills.yaml", "workflows/greenfield.yaml", "workflows/brownfield.yaml"):
        if load_yaml(path).get("version") != DEVELOPMENT_VERSION:
            fail(f"{path} must declare {DEVELOPMENT_VERSION} during release closure")

    project = load_json(ROOT / "schemas/project.schema.json")
    if f"/blueprint/{DEVELOPMENT_VERSION}/" not in project.get("$id", ""):
        fail("project schema must retain 0.5.4-dev provenance before promotion")
    if project.get("properties", {}).get("blueprint", {}).get("properties", {}).get("version", {}).get("const") != DEVELOPMENT_VERSION:
        fail("project schema consumer version must remain 0.5.4-dev before promotion")

    dev_schemas = (
        "schemas/status.schema.json",
        "schemas/client-architecture.schema.json",
        "schemas/client-platform-architecture.schema.json",
        "schemas/evidence.schema.json",
        "schemas/api-impact.schema.json",
        "schemas/interface-inventory.schema.json",
        "schemas/functional-interface-slice.schema.json",
        "schemas/mockup-batch.schema.json",
    )
    for path in dev_schemas:
        schema = load_json(ROOT / path)
        if f"/blueprint/{DEVELOPMENT_VERSION}/" not in schema.get("$id", ""):
            fail(f"{path} must retain 0.5.4-dev provenance before promotion")

    licensing = load_json(ROOT / "schemas/mobile-licensing.schema.json")
    if "/blueprint/0.5.3/" not in licensing.get("$id", "") or licensing.get("properties", {}).get("schema_version", {}).get("const") != "0.5.3":
        fail("Mobile Licensing must retain stable 0.5.3 provenance")
    if load_yaml("templates/mobile-licensing.example.yaml").get("schema_version") != "0.5.3":
        fail("Mobile Licensing template must retain 0.5.3 provenance")
    if skill_frontmatter("skills/dev-mobile-licensing/SKILL.md").get("version") != "0.5.3":
        fail("Mobile Licensing skill must retain 0.5.3 provenance")

    for path in ("templates/ci-runtime.example.yaml", "ci/blueprint-master.runtime.yaml"):
        if load_yaml(path).get("schema_version") != "0.5.2":
            fail(f"{path} must retain 0.5.2 CI runtime provenance")
    if load_yaml("catalog/reference-pilots.yaml").get("version") != "0.5.0":
        fail("reference pilot catalog must retain 0.5.0 provenance")
    architecture_validator = (ROOT / "scripts/validate-architecture-conformance.py").read_text(encoding="utf-8")
    if 'HISTORICAL_ORIGIN = "0.5.1"' not in architecture_validator:
        fail("architecture implementation conformance origin must remain 0.5.1")
    print("PASS component provenance across stable, development and inherited contracts")


def validate_active_docs_and_wiring() -> None:
    required_tokens = {
        "README.md": [
            "Blueprint 0.5.3", "145 checks", "Compliance Review",
            "0.5.4-dev", "29 fases", "146 checks", "16 skills materializadas",
            "v0.5.4", "API-backed",
        ],
        "documentation/BLUEPRINT_CURRENT_STATE.md": [
            "Release representada: **0.5.3**", "145 checks", "PR #25", "mobile_licensing",
            "0.5.4-dev release candidate", HARDENING_CHECKPOINT, "146 checks",
            "PR #37", "API-less/local-authoritative", "aprobación humana separada",
        ],
        "documentation/BLUEPRINT_V0_5_4_RELEASE_CANDIDATE.md": [
            "does **not** declare Blueprint 0.5.4 stable", HARDENING_CHECKPOINT,
            "146 checks", "IOS-###", "cross_platform", "API-backed offline mobile",
            "does not generalize Mobile Licensing to iOS", "separate explicit human approval",
            "prospective `merge_commit_sha`",
        ],
    }
    for path, tokens in required_tokens.items():
        text = (ROOT / path).read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                fail(f"{path} missing release closure token: {token}")

    notes_lower = CANDIDATE_NOTES_PATH.read_text(encoding="utf-8").lower()
    forbidden = (
        "blueprint 0.5.4 is stable",
        "v0.5.4 has been created",
        "v0.5.4 is published",
    )
    for token in forbidden:
        if token in notes_lower:
            fail(f"candidate notes falsely claim stable publication: {token}")

    workflow = (ROOT / ".github/workflows/blueprint-release-validation.yml").read_text(encoding="utf-8")
    for path in (
        "documentation/BLUEPRINT_V0_5_4_RELEASE_CANDIDATE.json",
        "documentation/BLUEPRINT_V0_5_4_RELEASE_CANDIDATE.md",
    ):
        if workflow.count(path) < 2:
            fail(f"release workflow must watch {path} on push and pull_request")
    development_validator = (ROOT / "scripts/validate-development.py").read_text(encoding="utf-8")
    if '"scripts/validate-release-closure.py"' not in development_validator:
        fail("development validation must execute release closure validation")
    print("PASS release candidate documentation and CI wiring")


def main() -> int:
    dev, candidate = validate_identity_and_candidate()
    validate_counts(dev, candidate)
    validate_component_provenance()
    validate_active_docs_and_wiring()
    print(
        "Blueprint 0.5.4 release closure validation: PASS "
        f"(stable={STABLE_VERSION}; development={DEVELOPMENT_VERSION}; target={TARGET_VERSION})"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
