#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
STABLE_VERSION = "0.5.4"
PREVIOUS_STABLE = "0.5.3"
RELEASE_DATE = "2026-09-16"
PRE_RELEASE_MAIN = "1f852ad831f6cb16b92c697fa97c46ac0e71049a"
RELEASE_MANIFEST = ROOT / "documentation/BLUEPRINT_V0_5_4_RELEASE.json"
RELEASE_NOTES = ROOT / "documentation/BLUEPRINT_V0_5_4_RELEASE_NOTES.md"
CANDIDATE_MANIFEST = ROOT / "documentation/BLUEPRINT_V0_5_4_RELEASE_CANDIDATE.json"
CANDIDATE_NOTES = ROOT / "documentation/BLUEPRINT_V0_5_4_RELEASE_CANDIDATE.md"

EXPECTED_COUNTS = {
    "phases": 29,
    "checks": 146,
    "gates": 19,
    "materialized_skills": 16,
    "planned_skills": 25,
}

PROMOTED_YAML = (
    "catalog/phases.yaml",
    "catalog/checks.yaml",
    "catalog/gates.yaml",
    "catalog/skills.yaml",
    "workflows/greenfield.yaml",
    "workflows/brownfield.yaml",
)

PROMOTED_SCHEMAS = (
    "schemas/project.schema.json",
    "schemas/status.schema.json",
    "schemas/client-architecture.schema.json",
    "schemas/client-platform-architecture.schema.json",
    "schemas/evidence.schema.json",
    "schemas/api-impact.schema.json",
    "schemas/interface-inventory.schema.json",
    "schemas/functional-interface-slice.schema.json",
    "schemas/mockup-batch.schema.json",
)

PROMOTED_EXAMPLES = (
    "templates/project.example.yaml",
    "templates/client-architecture.ios.example.json",
    "templates/client-platform-architecture.ios.example.json",
)

PROMOTED_SKILLS = (
    "skills/dev-android-client-architecture/SKILL.md",
    "skills/dev-ios-client-architecture/SKILL.md",
    "skills/dev-functional-interface-slice/SKILL.md",
)

GENERIC_VALIDATORS = (
    "scripts/validate-artifact-graph.py",
    "scripts/validate-client-architecture.py",
    "scripts/validate-reference-pilot-compliance.py",
    "scripts/validate-architecture-conformance.py",
    "scripts/validate-ci-runtime.py",
)

PLATFORM_POSITIVE = {
    "web-only", "android-native", "ios-native", "android-ios-native",
    "web-android-ios-native", "legacy-compatible-android",
    "cross-platform-android-only", "cross-platform-ios-only",
    "cross-platform-both", "api-backed-offline-android", "api-backed-offline-ios",
}
PLATFORM_NEGATIVE = {
    "ios-disabled-artifacts", "ios-slice-with-android-baseline",
    "ios-slice-with-android-evidence", "ios-accepted-without-ios-integration-qa",
    "invalid-mobile-strategy", "invalid-ios-namespace",
    "cross-platform-does-not-auto-enable-ios", "shared-gate-evidence-across-platforms",
    "offline-without-openapi",
}
LICENSING_POLICY = {
    "decision_required_when": {"android": True},
    "ios_alone_requires_decision": False,
    "cross_platform_changes_applicability": False,
    "enabled_profile_required": True,
}


def fail(message: str) -> None:
    raise AssertionError(message)


def load_json(path: str | Path) -> dict:
    p = Path(path)
    if not p.is_absolute():
        p = ROOT / p
    value = json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        fail(f"{p.relative_to(ROOT)} must contain an object")
    return value


def load_yaml(path: str | Path) -> dict:
    p = Path(path)
    if not p.is_absolute():
        p = ROOT / p
    value = yaml.safe_load(p.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        fail(f"{p.relative_to(ROOT)} must contain a mapping")
    return value


def parse_frontmatter(path: str) -> dict:
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


def validate_identity() -> dict:
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    if version != STABLE_VERSION:
        fail(f"VERSION must be {STABLE_VERSION}; got {version}")
    if (ROOT / "DEVELOPMENT_VERSION").exists():
        fail("DEVELOPMENT_VERSION must be removed from stable 0.5.4")
    if not RELEASE_MANIFEST.is_file() or not RELEASE_NOTES.is_file():
        fail("stable 0.5.4 manifest and release notes are required")
    if not CANDIDATE_MANIFEST.is_file() or not CANDIDATE_NOTES.is_file():
        fail("0.5.4 release-candidate evidence must remain preserved")

    manifest = load_json(RELEASE_MANIFEST)
    expected_identity = {
        "schema_version": "1.0.0",
        "version": STABLE_VERSION,
        "status": "stable",
        "release_date": RELEASE_DATE,
        "previous_stable": PREVIOUS_STABLE,
        "pre_release_main": PRE_RELEASE_MAIN,
        "tag": "v0.5.4",
    }
    for key, expected in expected_identity.items():
        if manifest.get(key) != expected:
            fail(f"release manifest {key} drifted: expected {expected}, got {manifest.get(key)}")
    if manifest.get("counts") != EXPECTED_COUNTS:
        fail("release manifest counts drifted")
    if manifest.get("release_rule", "").find("separate explicit human approval") < 0:
        fail("release manifest must preserve separate tag approval")
    print("PASS stable 0.5.4 release identity")
    return manifest


def validate_promoted_provenance() -> None:
    for path in PROMOTED_YAML:
        value = load_yaml(path)
        if value.get("version") != STABLE_VERSION:
            fail(f"{path} must declare version {STABLE_VERSION}")
        if "0.5.4-dev" in (ROOT / path).read_text(encoding="utf-8"):
            fail(f"{path} retains development provenance")

    for path in PROMOTED_SCHEMAS:
        schema = load_json(path)
        schema_id = schema.get("$id", "")
        if f"/blueprint/{STABLE_VERSION}/" not in schema_id:
            fail(f"{path} must use stable 0.5.4 schema provenance")
        if "0.5.4-dev" in json.dumps(schema):
            fail(f"{path} retains development provenance")
        Draft202012Validator.check_schema(schema)

    project = load_json("schemas/project.schema.json")
    project_version = project.get("properties", {}).get("blueprint", {}).get("properties", {}).get("version", {}).get("const")
    if project_version != STABLE_VERSION:
        fail("project schema blueprint.version must be stable 0.5.4")

    for path in PROMOTED_EXAMPLES:
        text = (ROOT / path).read_text(encoding="utf-8")
        if "0.5.4-dev" in text:
            fail(f"{path} retains development provenance")
        if STABLE_VERSION not in text:
            fail(f"{path} must declare stable 0.5.4 provenance")

    for path in PROMOTED_SKILLS:
        fm = parse_frontmatter(path)
        if fm.get("version") != STABLE_VERSION:
            fail(f"{path} must carry stable 0.5.4 frontmatter provenance")

    print("PASS active 0.5.4 contracts promoted from development provenance")


def validate_counts() -> None:
    actual = catalog_counts()
    if actual != EXPECTED_COUNTS:
        fail(f"stable 0.5.4 counts drifted: expected {EXPECTED_COUNTS}, got {actual}")
    print(f"PASS stable counts: {actual}")


def validate_platform_matrix() -> None:
    matrix = load_json("tests/fixtures/platform-matrix/matrix.json")
    if matrix.get("schema_version") != STABLE_VERSION:
        fail("platform matrix must declare stable 0.5.4")
    positives = matrix.get("positive_cases", [])
    negatives = matrix.get("negative_cases", [])
    positive_ids = {case.get("id") for case in positives if isinstance(case, dict)}
    negative_ids = {case.get("id") for case in negatives if isinstance(case, dict)}
    if positive_ids != PLATFORM_POSITIVE or negative_ids != PLATFORM_NEGATIVE:
        fail("governed platform matrix coverage drifted")
    if len(positives) != 11 or len(negatives) != 9:
        fail("platform matrix must remain exactly 11 positive / 9 negative cases")
    print("PASS governed platform matrix: 11 positive / 9 negative")


def validate_mobile_licensing_boundary() -> None:
    matrix = load_json("tests/fixtures/mobile-licensing-boundary/matrix.json")
    if matrix.get("schema_version") != STABLE_VERSION:
        fail("mobile licensing boundary matrix must declare stable 0.5.4")
    if matrix.get("policy") != LICENSING_POLICY:
        fail("Mobile Licensing boundary policy drifted")
    cases = matrix.get("cases", [])
    valid_count = sum(1 for case in cases if case.get("expected") == "valid")
    invalid_count = sum(1 for case in cases if case.get("expected") == "invalid")
    if len(cases) != 17 or valid_count != 11 or invalid_count != 6:
        fail("Mobile Licensing boundary must remain exactly 17 cases: 11 valid / 6 invalid")

    for path in ("workflows/greenfield.yaml", "workflows/brownfield.yaml"):
        branch = load_yaml(path).get("conditional_capabilities", {}).get("mobile_licensing", {})
        if branch.get("decision_required_when") != {"android": True}:
            fail(f"{path} Mobile Licensing applicability must remain Android-only")
        if "ios_alone_does_not_trigger_mobile_licensing" not in set(branch.get("rules", [])):
            fail(f"{path} must preserve iOS licensing non-implication")

    licensing = load_json("schemas/mobile-licensing.schema.json")
    if "/blueprint/0.5.3/" not in licensing.get("$id", ""):
        fail("Mobile Licensing schema must retain 0.5.3-compatible provenance")
    if licensing.get("properties", {}).get("schema_version", {}).get("const") != "0.5.3":
        fail("Mobile Licensing schema_version must remain 0.5.3")
    if load_yaml("templates/mobile-licensing.example.yaml").get("schema_version") != "0.5.3":
        fail("Mobile Licensing template must retain 0.5.3 provenance")
    if parse_frontmatter("skills/dev-mobile-licensing/SKILL.md").get("version") != "0.5.3":
        fail("Mobile Licensing skill must retain 0.5.3 provenance")
    print("PASS Android-only Mobile Licensing boundary and retained 0.5.3 contract")


def validate_docs_and_history() -> None:
    v53 = load_json("documentation/BLUEPRINT_V0_5_3_RELEASE.json")
    if v53.get("version") != "0.5.3" or v53.get("status") != "stable" or v53.get("counts", {}).get("checks") != 145:
        fail("historical 0.5.3 release manifest drifted")

    required_tokens = {
        "BLUEPRINT.md": ["Stable release: **0.5.4**", "iOS", "cross_platform", "API-backed", "Mobile Licensing"],
        "README.md": ["Blueprint 0.5.4", "29 fases", "146 checks", "16 skills materializadas", "Compliance Review"],
        "documentation/BLUEPRINT_CURRENT_STATE.md": ["Release representada: **0.5.4**", "146 checks", PRE_RELEASE_MAIN, "PR #38"],
        "documentation/BLUEPRINT_V0_5_4_RELEASE_NOTES.md": ["Blueprint 0.5.4", "146 checks", "v0.5.4", "separate explicit human approval"],
    }
    for path, tokens in required_tokens.items():
        text = (ROOT / path).read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                fail(f"{path} missing stable release token: {token}")

    notes = RELEASE_NOTES.read_text(encoding="utf-8").lower()
    for forbidden in ("v0.5.4 has been created", "v0.5.4 is published", "tag already created"):
        if forbidden in notes:
            fail(f"release notes falsely claim tag publication: {forbidden}")
    print("PASS active 0.5.4 documentation and immutable history")


def validate_workflow_wiring() -> None:
    release_workflow = (ROOT / ".github/workflows/blueprint-release-validation.yml").read_text(encoding="utf-8")
    for token in (
        "documentation/BLUEPRINT_V0_5_4_RELEASE.json",
        "documentation/BLUEPRINT_V0_5_4_RELEASE_NOTES.md",
        "scripts/validate-release-v054.py",
    ):
        if token not in release_workflow:
            fail(f"release workflow missing stable 0.5.4 wiring: {token}")
    print("PASS stable 0.5.4 CI wiring")


def run_generic_validators() -> None:
    for path in GENERIC_VALIDATORS:
        print(f"\n=== {path} ===")
        result = subprocess.run([sys.executable, path], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        print(result.stdout, end="")
        if result.returncode != 0:
            fail(f"nested validator failed: {path} (exit {result.returncode})")
    print("PASS generic repository validators under stable 0.5.4")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scope", choices=["full", "skills", "platform-matrix", "mobile-licensing"], default="full")
    args = parser.parse_args()

    validate_identity()
    validate_promoted_provenance()
    validate_counts()

    if args.scope in {"full", "platform-matrix"}:
        validate_platform_matrix()
    if args.scope in {"full", "mobile-licensing"}:
        validate_mobile_licensing_boundary()
    if args.scope in {"full", "skills"}:
        # Skill provenance is already enforced by validate_promoted_provenance and counts.
        print("PASS stable skill provenance and registry counts")

    if args.scope == "full":
        validate_docs_and_history()
        validate_workflow_wiring()
        run_generic_validators()

    print(f"\nBlueprint stable 0.5.4 validation: PASS (scope={args.scope})")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
