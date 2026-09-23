#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
STABLE_VERSION = "0.5.4"
DEVELOPMENT_VERSION = "0.5.5-dev"
TARGET_VERSION = "0.5.5"
BASELINE_COMMIT = "8d29ba4c6caf0a382b80310dc0e88c8f1e7fb3c4"
BASELINE_TAG = "v0.5.4"
HARDENING_CHECKPOINT = "d7ca0ff1cd0615445c3015c9d9b3a18983e573b7"
WEBBLUEPRINT_SNAPSHOT = "12cc52dabfe05ec9902f0ea6d73c7da6a19e1a74"
CANDIDATE_DATE = "2026-09-23"

DEV_MANIFEST_PATH = ROOT / "documentation/BLUEPRINT_V0_5_5_DEVELOPMENT.json"
CANDIDATE_PATH = ROOT / "documentation/BLUEPRINT_V0_5_5_RELEASE_CANDIDATE.json"
CANDIDATE_NOTES_PATH = ROOT / "documentation/BLUEPRINT_V0_5_5_RELEASE_CANDIDATE.md"
PILOT_REPORT_PATH = ROOT / "documentation/BLUEPRINT_V0_5_5_WEBBLUEPRINT_PILOT_REPORT.json"
STABLE_RELEASE_PATH = ROOT / "documentation/BLUEPRINT_V0_5_5_RELEASE.json"

EXPECTED_COUNTS = {
    "phases": 29,
    "checks": 146,
    "gates": 19,
    "materialized_skills": 16,
    "planned_skills": 25,
}

EXPECTED_LINEAGE = [
    {"increment": 0, "pull_request": 42, "merge_commit": "e316c31a04d7a7f8e7c746a3dd36d0cdb1d24ebe", "scope": "governed_development_lane"},
    {"increment": 1, "pull_request": 43, "merge_commit": "45ebc94c4ddacac00ebece1fe052400a25c2b060", "scope": "api_authority_capability_model"},
    {"increment": 2, "pull_request": 44, "merge_commit": "a07cf874a214d300daab5bd8214d708bffafe464", "scope": "workflow_gate_applicability"},
    {"increment": 3, "pull_request": 45, "merge_commit": "ef8dbde3af3d786cf96b26d9938a27715b8e5f43", "scope": "client_architecture_slice_authority"},
    {"increment": 4, "pull_request": 46, "merge_commit": "1b2d29ad43d7e6f30bad2b54ac972bb24704d1e4", "scope": "integration_qa_authority_matrix"},
    {"increment": 5, "pull_request": 47, "merge_commit": "828e182659975da325093e06afa84de238aef2a8", "scope": "generic_compliance_doctor"},
    {"increment": 6, "pull_request": 48, "merge_commit": "d7ca0ff1cd0615445c3015c9d9b3a18983e573b7", "scope": "template_provenance_webblueprint_pilot"},
]

EXPECTED_FROZEN_DECISIONS = {
    "api_backed_pipeline_preserves_0_5_4_strictness": True,
    "api_absence_must_be_explicit": True,
    "api_optional_is_not_a_backend_bypass": True,
    "no_fake_openapi_database_or_permissions_for_compliance": True,
    "remote_authoritative_business_semantics_require_api_backed_authority": True,
    "local_static_or_non_authoritative_mock_behavior_may_be_api_optional": True,
    "real_api_na_must_be_structurally_representable_when_legitimate": True,
    "consumer_auto_upgrade_is_forbidden": True,
    "existing_accepted_consumer_evidence_is_grandfathered": True,
}

EXPECTED_PROVENANCE = {
    "root_release": "0.5.4-stable-until-promotion",
    "development_lane": "0.5.5-dev",
    "stable_core_catalogs_and_workflows": "0.5.4-compatible",
    "api_authority_overlay": "0.5.5-dev",
    "workflow_gate_applicability_overlay": "0.5.5-dev",
    "client_slice_authority_overlay": "0.5.5-dev",
    "integration_qa_authority_overlay": "0.5.5-dev",
    "generic_compliance_doctor": "0.5.5-dev",
    "webblueprint_pilot": "0.5.5-dev-non-normative",
    "status_template": "0.5.4-active-provenance",
    "mobile_licensing_contract": "0.5.3-compatible",
    "ci_runtime_contract": "0.5.2-compatible",
    "architecture_implementation_conformance": "0.5.1-compatible",
    "unchanged_historical_contracts": "retain_prior_compatible_provenance",
}

EXPECTED_CONSUMER_POLICY = {
    "automatic_adoption": False,
    "compliance_review_required": True,
    "explicit_consumer_change_required": True,
    "impact_appropriate_revalidation_required": True,
}

EXPECTED_DEFERRED_SCOPE = {
    "consumer_specific_governance_materialization": True,
    "automatic_consumer_adoption": True,
    "remote_authoritative_semantics_under_api_optional": True,
    "webblueprint_adoption_until_stable_0_5_5": True,
}

EXPECTED_FINAL_REQUIREMENTS = {
    "final_release_pr_required": True,
    "promote_development_contracts_to_0_5_5": True,
    "set_root_version_to_0_5_5": True,
    "remove_development_version_marker": True,
    "create_stable_release_manifest_and_notes": True,
    "update_normative_and_active_docs_to_stable_0_5_5": True,
    "post_merge_stable_validation_on_exact_sha": True,
    "tag_requires_separate_explicit_human_approval": True,
    "prospective_merge_sha_is_not_release_evidence": True,
    "webblueprint_adoption_requires_separate_explicit_pr": True,
}

EXPECTED_PILOT_SUMMARY = {
    "PASS": 18,
    "FAIL": 7,
    "N/A": 10,
    "BLOCKED": 0,
    "TOTAL": 35,
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


def planned_skill_count(catalog: dict[str, Any]) -> int:
    seen: set[str] = set()
    for category, values in catalog.get("planned_registry", {}).items():
        if not isinstance(values, list):
            fail(f"planned_registry.{category} must be a list")
        for skill_id in values:
            if not isinstance(skill_id, str) or not skill_id:
                fail(f"planned_registry.{category} contains invalid skill id")
            if skill_id in seen:
                fail(f"planned skill duplicated: {skill_id}")
            seen.add(skill_id)
    return len(seen)


def catalog_counts() -> dict[str, int]:
    skills = load_yaml(ROOT / "catalog/skills.yaml")
    return {
        "phases": len(load_yaml(ROOT / "catalog/phases.yaml").get("phases", [])),
        "checks": len(load_yaml(ROOT / "catalog/checks.yaml").get("checks", [])),
        "gates": len(load_yaml(ROOT / "catalog/gates.yaml").get("gates", [])),
        "materialized_skills": len(skills.get("registry", {})),
        "planned_skills": planned_skill_count(skills),
    }


def validate_identity() -> tuple[dict[str, Any], dict[str, Any]]:
    stable = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    development = (ROOT / "DEVELOPMENT_VERSION").read_text(encoding="utf-8").strip()
    if stable != STABLE_VERSION:
        fail(f"release-candidate closure must keep VERSION={STABLE_VERSION}; got {stable}")
    if development != DEVELOPMENT_VERSION:
        fail(f"release-candidate closure requires DEVELOPMENT_VERSION={DEVELOPMENT_VERSION}; got {development}")
    if STABLE_RELEASE_PATH.exists():
        fail("stable 0.5.5 release manifest must not exist during release-candidate closure")
    if not CANDIDATE_PATH.is_file() or not CANDIDATE_NOTES_PATH.is_file():
        fail("0.5.5 release-candidate manifest and notes are required")

    dev = load_json(DEV_MANIFEST_PATH)
    candidate = load_json(CANDIDATE_PATH)

    if dev.get("target_version") != DEVELOPMENT_VERSION or dev.get("stable_version") != STABLE_VERSION:
        fail("0.5.5 development manifest identity drifted")
    if dev.get("status") != "hardening":
        fail("development manifest remains hardening until stable promotion")

    expected_baseline = {"branch": "main", "commit": BASELINE_COMMIT, "tag": BASELINE_TAG}
    if dev.get("baseline") != expected_baseline or candidate.get("baseline") != expected_baseline:
        fail("0.5.5 baseline drifted")

    if candidate.get("schema_version") != "1.0.0":
        fail("release-candidate schema_version drifted")
    if candidate.get("target_version") != TARGET_VERSION:
        fail("release-candidate target_version drifted")
    if candidate.get("development_version") != DEVELOPMENT_VERSION:
        fail("release-candidate development_version drifted")
    if candidate.get("stable_version") != STABLE_VERSION:
        fail("release-candidate stable_version drifted")
    if candidate.get("status") != "release_candidate" or candidate.get("candidate_date") != CANDIDATE_DATE:
        fail("release-candidate status/date drifted")
    if candidate.get("hardening_complete_through_main") != HARDENING_CHECKPOINT:
        fail("release-candidate hardening checkpoint drifted")

    print(f"PASS candidate identity: stable={STABLE_VERSION}; development={DEVELOPMENT_VERSION}; target={TARGET_VERSION}")
    return dev, candidate


def validate_closure(dev: dict[str, Any], candidate: dict[str, Any]) -> None:
    closure = dev.get("closure", {})
    if closure.get("state") != "release_pr_ready":
        fail("development closure must be release_pr_ready")
    if closure.get("checkpoint_date") != CANDIDATE_DATE:
        fail("development closure checkpoint date drifted")
    if closure.get("hardening_complete_through_main") != HARDENING_CHECKPOINT:
        fail("development closure hardening SHA drifted")
    if closure.get("completed_increments") != list(range(7)):
        fail("development closure completed increments must be 0..6")
    if closure.get("release_candidate_manifest") != "documentation/BLUEPRINT_V0_5_5_RELEASE_CANDIDATE.json":
        fail("development closure candidate manifest pointer drifted")
    if closure.get("release_candidate_notes") != "documentation/BLUEPRINT_V0_5_5_RELEASE_CANDIDATE.md":
        fail("development closure candidate notes pointer drifted")

    actual_counts = catalog_counts()
    if actual_counts != EXPECTED_COUNTS:
        fail(f"stable core counts drifted: expected {EXPECTED_COUNTS}, got {actual_counts}")
    if closure.get("counts") != EXPECTED_COUNTS or candidate.get("counts") != EXPECTED_COUNTS:
        fail("closure/candidate counts do not match governed counts")

    if candidate.get("hardening_lineage") != EXPECTED_LINEAGE:
        fail("release-candidate hardening lineage drifted")
    if candidate.get("frozen_decisions") != EXPECTED_FROZEN_DECISIONS:
        fail("release-candidate frozen decisions drifted")
    if candidate.get("component_provenance") != EXPECTED_PROVENANCE:
        fail("release-candidate component provenance drifted")
    if candidate.get("consumer_policy") != EXPECTED_CONSUMER_POLICY:
        fail("release-candidate consumer policy drifted")
    if candidate.get("deferred_scope") != EXPECTED_DEFERRED_SCOPE:
        fail("release-candidate deferred scope drifted")
    if candidate.get("final_release_requirements") != EXPECTED_FINAL_REQUIREMENTS:
        fail("release-candidate final release requirements drifted")

    print(f"PASS closure checkpoint and counts: {EXPECTED_COUNTS}")
    print("PASS hardening lineage PR #42 through PR #48 frozen")


def validate_pilot(candidate: dict[str, Any]) -> None:
    pilot = candidate.get("webblueprint_pilot", {})
    if pilot.get("repository") != "LuisHdezE/WebBlueprint":
        fail("candidate WebBlueprint pilot repository drifted")
    if pilot.get("snapshot") != WEBBLUEPRINT_SNAPSHOT:
        fail("candidate WebBlueprint pilot snapshot drifted")
    if pilot.get("adopted_version") != "UNMANAGED":
        fail("release candidate must not pretend WebBlueprint has adopted Blueprint")
    if pilot.get("evaluation_version") != DEVELOPMENT_VERSION:
        fail("candidate WebBlueprint evaluation version drifted")
    if pilot.get("overall_status") != "FAIL":
        fail("WebBlueprint pilot must remain fail-closed during release candidate closure")
    if pilot.get("summary") != EXPECTED_PILOT_SUMMARY:
        fail("candidate WebBlueprint pilot summary drifted")
    if pilot.get("consumer_mutated") is not False:
        fail("release candidate cannot claim a WebBlueprint mutation")

    report = load_json(PILOT_REPORT_PATH)
    if report.get("consumer", {}).get("repository") != "LuisHdezE/WebBlueprint":
        fail("committed pilot report consumer drifted")
    if report.get("consumer", {}).get("snapshot") != WEBBLUEPRINT_SNAPSHOT:
        fail("committed pilot report snapshot drifted")
    if report.get("evaluation", {}).get("adopted_version") != "UNMANAGED":
        fail("committed pilot report must remain UNMANAGED")
    if report.get("evaluation", {}).get("blueprint_version") != DEVELOPMENT_VERSION:
        fail("committed pilot report evaluation version drifted")
    if report.get("overall_status") != "FAIL" or report.get("summary") != EXPECTED_PILOT_SUMMARY:
        fail("committed pilot report result drifted")

    print(f"PASS WebBlueprint pilot remains non-normative and fail-closed: {EXPECTED_PILOT_SUMMARY}")


def validate_docs_and_wiring() -> None:
    required_tokens = {
        "README.md": [
            "Blueprint 0.5.4",
            "Release candidate 0.5.5-dev",
            HARDENING_CHECKPOINT,
            "18 PASS / 7 FAIL / 10 N/A / 0 BLOCKED",
            "UNMANAGED",
            "v0.5.5",
        ],
        "documentation/BLUEPRINT_CURRENT_STATE.md": [
            "Release estable representada: **0.5.4**",
            "Release candidate activa: **0.5.5-dev**",
            HARDENING_CHECKPOINT,
            "#42",
            "#48",
            "18**;",
            "UNMANAGED",
            "v0.5.5",
        ],
        "documentation/BLUEPRINT_V0_5_5_RELEASE_CANDIDATE.md": [
            "does **not** declare Blueprint 0.5.5 stable",
            HARDENING_CHECKPOINT,
            "18",
            "7",
            "10",
            "UNMANAGED",
            "separate explicit human approval",
            "prospective `merge_commit_sha`",
        ],
    }
    for relative, tokens in required_tokens.items():
        text = (ROOT / relative).read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                fail(f"{relative} missing release-candidate token: {token}")

    notes_lower = CANDIDATE_NOTES_PATH.read_text(encoding="utf-8").lower()
    forbidden = (
        "blueprint 0.5.5 is stable",
        "v0.5.5 has been created",
        "v0.5.5 is published",
        "webblueprint has adopted 0.5.5",
    )
    for token in forbidden:
        if token in notes_lower:
            fail(f"candidate notes falsely claim completed promotion/adoption: {token}")

    workflow = (ROOT / ".github/workflows/blueprint-release-validation.yml").read_text(encoding="utf-8")
    for path in (
        "documentation/BLUEPRINT_V0_5_5_RELEASE_CANDIDATE.json",
        "documentation/BLUEPRINT_V0_5_5_RELEASE_CANDIDATE.md",
        "scripts/validate-release-closure-v055.py",
    ):
        if workflow.count(path) < 2:
            fail(f"release workflow must watch {path} on push and pull_request")

    development_validator = (ROOT / "scripts/validate-development.py").read_text(encoding="utf-8")
    if 'validate-release-closure-v055.py' not in development_validator:
        fail("development validation must execute 0.5.5 release-candidate closure validation")

    print("PASS active docs distinguish stable 0.5.4 from candidate 0.5.5-dev")
    print("PASS release workflow watches 0.5.5 candidate closure artifacts")


def main() -> int:
    dev, candidate = validate_identity()
    validate_closure(dev, candidate)
    validate_pilot(candidate)
    validate_docs_and_wiring()
    print(
        "\nBlueprint 0.5.5 release-candidate closure validation: PASS "
        f"(stable={STABLE_VERSION}; development={DEVELOPMENT_VERSION}; target={TARGET_VERSION})"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
