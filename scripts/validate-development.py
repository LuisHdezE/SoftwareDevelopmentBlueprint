#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parents[1]
VERSION_PATH = ROOT / "VERSION"
DEVELOPMENT_VERSION_PATH = ROOT / "DEVELOPMENT_VERSION"
DEVELOPMENT_MANIFEST_PATH = ROOT / "documentation/BLUEPRINT_V0_5_5_DEVELOPMENT.json"
STABLE_VALIDATOR_PATH = ROOT / "scripts/validate-release-v054.py"
RELEASE_CLOSURE_VALIDATOR_PATH = ROOT / "scripts/validate-release-closure-v055.py"
RELEASE_CANDIDATE_PATH = ROOT / "documentation/BLUEPRINT_V0_5_5_RELEASE_CANDIDATE.json"

STABLE_VERSION = "0.5.4"
DEVELOPMENT_VERSION = "0.5.5-dev"
BASELINE_COMMIT = "8d29ba4c6caf0a382b80310dc0e88c8f1e7fb3c4"
BASELINE_TAG = "v0.5.4"
WEBBLUEPRINT_SNAPSHOT = "12cc52dabfe05ec9902f0ea6d73c7da6a19e1a74"
TRACKING_ISSUE = 41

EXPECTED_SCOPE = {
    "api_authority_models": ["api_backed", "api_optional"],
    "api_optional_allowed_sources": ["local", "static", "mock_non_authoritative"],
    "generic_compliance_validation": True,
    "status_template_provenance_reconciliation": True,
}

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

EXPECTED_GOVERNANCE = {
    "consumer_auto_upgrade": False,
    "root_version_remains_stable_during_hardening": True,
    "incremental_prs_required": True,
    "exact_head_ci_required": True,
    "final_release_closure_required": True,
    "final_release_pr_required": True,
    "post_merge_exact_sha_validation_required": True,
    "tag_requires_explicit_human_approval": True,
}

EXPECTED_INCREMENT_IDS = list(range(7))


def fail(message: str) -> None:
    raise AssertionError(message)


def load_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        fail(f"{path.relative_to(ROOT)} must contain an object")
    return value


def load_module(path: Path, module_name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        fail(f"cannot load validator: {path.relative_to(ROOT)}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_stable_validator() -> ModuleType:
    return load_module(STABLE_VALIDATOR_PATH, "blueprint_stable_v054_validator")


def validate_development_identity() -> dict:
    stable = VERSION_PATH.read_text(encoding="utf-8").strip()
    if stable != STABLE_VERSION:
        fail(f"0.5.5 hardening must keep VERSION={STABLE_VERSION}; got {stable}")

    if not DEVELOPMENT_VERSION_PATH.is_file():
        fail("DEVELOPMENT_VERSION is required during 0.5.5 hardening")
    target = DEVELOPMENT_VERSION_PATH.read_text(encoding="utf-8").strip()
    if target != DEVELOPMENT_VERSION:
        fail(f"DEVELOPMENT_VERSION must be {DEVELOPMENT_VERSION}; got {target}")

    manifest = load_json(DEVELOPMENT_MANIFEST_PATH)
    if manifest.get("schema_version") != "1.0.0":
        fail("development manifest schema_version drifted")
    if manifest.get("target_version") != DEVELOPMENT_VERSION:
        fail("development manifest target_version drifted")
    if manifest.get("stable_version") != STABLE_VERSION:
        fail("development manifest stable_version drifted")
    if manifest.get("status") != "hardening":
        fail("development manifest must remain in hardening status before stable promotion")

    baseline = manifest.get("baseline", {})
    if baseline != {"branch": "main", "commit": BASELINE_COMMIT, "tag": BASELINE_TAG}:
        fail("0.5.5 hardening baseline drifted")

    origin = manifest.get("origin", {})
    if origin.get("compliance_review") != "CR-WEBBLUEPRINT-SDB-0.5.4":
        fail("0.5.5 hardening must preserve its WebBlueprint compliance-review origin")
    if origin.get("consumer_repository") != "LuisHdezE/WebBlueprint":
        fail("0.5.5 hardening consumer origin drifted")
    if origin.get("consumer_snapshot") != WEBBLUEPRINT_SNAPSHOT:
        fail("reviewed WebBlueprint snapshot drifted")
    if origin.get("tracking_issue") != TRACKING_ISSUE:
        fail("0.5.5 hardening tracking issue drifted")

    if manifest.get("scope") != EXPECTED_SCOPE:
        fail("0.5.5 development scope drifted")
    if manifest.get("frozen_decisions") != EXPECTED_FROZEN_DECISIONS:
        fail("0.5.5 frozen decisions drifted")
    if manifest.get("governance") != EXPECTED_GOVERNANCE:
        fail("0.5.5 governance contract drifted")

    increments = manifest.get("planned_increments")
    if not isinstance(increments, list):
        fail("planned_increments must be a list")
    increment_ids = [item.get("id") for item in increments if isinstance(item, dict)]
    if increment_ids != EXPECTED_INCREMENT_IDS:
        fail(f"planned increment IDs must remain {EXPECTED_INCREMENT_IDS}; got {increment_ids}")
    if any(not isinstance(item.get("name"), str) or not item.get("name") for item in increments):
        fail("every planned increment requires a non-empty name")
    if any(not isinstance(item.get("goal"), str) or not item.get("goal") for item in increments):
        fail("every planned increment requires a non-empty goal")

    if (ROOT / "documentation/BLUEPRINT_V0_5_5_RELEASE.json").exists():
        fail("stable 0.5.5 release manifest must not exist during hardening/release-candidate closure")

    print(f"PASS development identity: stable={STABLE_VERSION}; target={DEVELOPMENT_VERSION}")
    print(f"PASS origin: WebBlueprint@{WEBBLUEPRINT_SNAPSHOT}; issue #{TRACKING_ISSUE}")
    print("PASS 0.5.5 frozen API-authority and governance decisions")
    return manifest


def validate_stable_baseline_preserved(stable: ModuleType) -> None:
    release = stable.load_json("documentation/BLUEPRINT_V0_5_4_RELEASE.json")
    expected_identity = {
        "schema_version": "1.0.0",
        "version": STABLE_VERSION,
        "status": "stable",
        "tag": BASELINE_TAG,
    }
    for key, expected in expected_identity.items():
        if release.get(key) != expected:
            fail(f"stable 0.5.4 release manifest {key} drifted: expected {expected}, got {release.get(key)}")

    stable.validate_promoted_provenance()
    stable.validate_counts()
    stable.validate_platform_matrix()
    stable.validate_mobile_licensing_boundary()
    stable.validate_docs_and_history()
    stable.validate_workflow_wiring()
    stable.run_generic_validators()
    print("PASS stable 0.5.4 contracts, counts, history and inherited validators preserved")


def validate_release_candidate_closure(manifest: dict) -> None:
    closure = manifest.get("closure")
    if closure is None:
        if RELEASE_CANDIDATE_PATH.exists():
            fail("release-candidate manifest exists without governed development closure state")
        return
    if not isinstance(closure, dict):
        fail("development closure must be an object")
    if not RELEASE_CANDIDATE_PATH.is_file():
        fail("governed development closure requires 0.5.5 release-candidate manifest")
    module = load_module(RELEASE_CLOSURE_VALIDATOR_PATH, "blueprint_release_closure_v055_validator")
    result = module.main()
    if result != 0:
        fail(f"0.5.5 release-candidate closure validator returned {result}")
    print("PASS 0.5.5 release-candidate closure nested validation")


def main() -> int:
    manifest = validate_development_identity()
    stable = load_stable_validator()
    validate_stable_baseline_preserved(stable)
    validate_release_candidate_closure(manifest)
    print(
        "\nBlueprint development validation: PASS "
        f"(stable={STABLE_VERSION}; target={DEVELOPMENT_VERSION})"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
