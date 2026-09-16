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
DEVELOPMENT_MANIFEST_PATH = ROOT / "documentation/BLUEPRINT_V0_5_4_DEVELOPMENT.json"
STABLE_VALIDATOR_PATH = ROOT / "scripts/validate-release.py"

STABLE_VERSION = "0.5.3"
DEVELOPMENT_VERSION = "0.5.4-dev"
BASELINE_COMMIT = "b1df5ca09ad38e39a1b51006aa441786afdb946c"
BASELINE_TAG = "v0.5.3"
DEVELOPMENT_VALIDATORS = [
    "scripts/validate-platform-capabilities.py",
]

EXPECTED_FROZEN_DECISIONS = {
    "cross_platform_does_not_enable_targets": True,
    "cross_platform_does_not_share_platform_gates": True,
    "platform_acceptance_remains_independent": True,
    "mobile_licensing_android_applicability_preserved": True,
    "ios_does_not_imply_mobile_licensing": True,
    "offline_scope_is_api_backed_only": True,
    "api_less_local_authoritative_is_deferred": True,
}

EXPECTED_GOVERNANCE = {
    "consumer_auto_upgrade": False,
    "root_version_remains_stable_during_hardening": True,
    "incremental_prs_required": True,
    "final_release_pr_required": True,
    "post_merge_exact_sha_validation_required": True,
    "tag_requires_explicit_human_approval": True,
}


def fail(message: str) -> None:
    raise AssertionError(message)


def load_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        fail(f"{path.relative_to(ROOT)} must contain an object")
    return value


def load_stable_validator() -> ModuleType:
    spec = importlib.util.spec_from_file_location("blueprint_stable_release_validator", STABLE_VALIDATOR_PATH)
    if spec is None or spec.loader is None:
        fail("cannot load stable release validator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate_development_identity() -> dict:
    stable = VERSION_PATH.read_text(encoding="utf-8").strip()
    if stable != STABLE_VERSION:
        fail(f"hardening must keep VERSION={STABLE_VERSION}; got {stable}")
    if not DEVELOPMENT_VERSION_PATH.is_file():
        fail("DEVELOPMENT_VERSION is required during 0.5.4 hardening")
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
        fail("development manifest must remain in hardening status before release promotion")

    baseline = manifest.get("baseline", {})
    if baseline != {"branch": "main", "commit": BASELINE_COMMIT, "tag": BASELINE_TAG}:
        fail("0.5.4 hardening baseline drifted")

    scope = manifest.get("scope", {})
    if scope.get("client_platforms") != ["web", "android", "ios"]:
        fail("development scope must declare web/android/ios client platforms")
    if scope.get("mobile_strategy_model") != ["native", "cross_platform"]:
        fail("development scope mobile strategy model drifted")
    if scope.get("offline_mobile") != "api_backed_only":
        fail("0.5.4 hardening must remain limited to API-backed offline mobile")
    if scope.get("api_less_local_authoritative") != "deferred":
        fail("API-less/local-authoritative hardening must remain deferred")

    if manifest.get("frozen_decisions") != EXPECTED_FROZEN_DECISIONS:
        fail("0.5.4 frozen decisions drifted")
    if manifest.get("governance") != EXPECTED_GOVERNANCE:
        fail("0.5.4 governance contract drifted")

    if (ROOT / "documentation/BLUEPRINT_V0_5_4_RELEASE.json").exists():
        fail("stable 0.5.4 release manifest must not exist during hardening")

    print(f"PASS development identity: stable={STABLE_VERSION}; target={DEVELOPMENT_VERSION}")
    return manifest


def validate_stable_baseline_preserved(stable: ModuleType) -> None:
    stable.validate_historical_releases()
    stable.validate_v53_manifest()
    stable.validate_reference_pilot_history()
    stable.validate_ci_runtime_provenance()
    stable.validate_architecture_conformance_semantics()
    stable.validate_core_semantics()
    stable.validate_mobile_licensing_semantics()
    stable.validate_active_docs()
    print("PASS stable 0.5.3 baseline and inherited invariants preserved")


def run_current_validators(stable: ModuleType) -> None:
    for validator in stable.VALIDATORS:
        stable.run_validator(validator)
    for validator in DEVELOPMENT_VALIDATORS:
        stable.run_validator(validator)
    print("PASS current repository validators under 0.5.4 hardening lane")


def main() -> int:
    validate_development_identity()
    stable = load_stable_validator()
    validate_stable_baseline_preserved(stable)
    run_current_validators(stable)
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
