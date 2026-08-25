#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
EXPECTED_VERSION = "0.4.0"
EXPECTED_COUNTS = {
    "phases": 25,
    "checks": 92,
    "gates": 14,
    "materialized_skills": 13,
    "planned_skills": 25,
}
ACTIVE_VERSIONED_FILES = [
    "catalog/phases.yaml",
    "catalog/checks.yaml",
    "catalog/gates.yaml",
    "catalog/skills.yaml",
    "catalog/reference-pilots.yaml",
    "workflows/greenfield.yaml",
    "workflows/brownfield.yaml",
]
POST_API_PIPELINE = [
    "interface_inventory",
    "visual_identity",
    "design_system",
    "mockup_planning",
    "mockups",
    "visual_review_gate",
    "client_architecture",
]
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
    fail(f"{label} does not contain canonical post-API pipeline contiguously")


def validate_release_identity() -> tuple[dict, dict, dict, dict]:
    if VERSION != EXPECTED_VERSION:
        fail(f"VERSION must be {EXPECTED_VERSION}, got {VERSION}")

    for path in ACTIVE_VERSIONED_FILES:
        document = load_yaml(path)
        if document.get("version") != VERSION:
            fail(f"{path} version must match VERSION ({VERSION})")

    project_example = load_yaml("templates/project.example.yaml")
    if project_example.get("blueprint", {}).get("version") != VERSION:
        fail("templates/project.example.yaml must target current stable VERSION")

    status_example = load_yaml("templates/status.example.yaml")
    if status_example.get("blueprint_version") != VERSION:
        fail("templates/status.example.yaml must target current stable VERSION")

    phases = load_yaml("catalog/phases.yaml")
    checks = load_yaml("catalog/checks.yaml")
    gates = load_yaml("catalog/gates.yaml")
    skills = load_yaml("catalog/skills.yaml")

    actual_counts = {
        "phases": len(phases.get("phases", [])),
        "checks": len(checks.get("checks", [])),
        "gates": len(gates.get("gates", [])),
        "materialized_skills": len(skills.get("registry", {})),
        "planned_skills": planned_skill_count(skills),
    }
    if actual_counts != EXPECTED_COUNTS:
        fail(f"stable core counts drifted: expected {EXPECTED_COUNTS}, got {actual_counts}")

    return phases, checks, gates, skills


def validate_workflows() -> None:
    for path in ("workflows/greenfield.yaml", "workflows/brownfield.yaml"):
        workflow = load_yaml(path)
        assert_contiguous(workflow.get("sequence", []), POST_API_PIPELINE, path)
        if workflow.get("gates", {}).get("per_interface_slice_after_visual_review") != "visual_review_pass":
            fail(f"{path} must map visual review to visual_review_pass")
        if workflow.get("gates", {}).get("per_interface_slice_platform_before_implementation") != "client_architecture_ready":
            fail(f"{path} must map client architecture to scoped gate")


def validate_release_manifest() -> None:
    release = load_json("documentation/BLUEPRINT_V0_4_RELEASE.json")
    if release.get("version") != VERSION or release.get("status") != "stable":
        fail("release manifest must declare current VERSION as stable")
    if release.get("previous_stable") != "0.3.0":
        fail("release manifest previous stable version drifted")
    if release.get("tag") != "v0.4.0":
        fail("release manifest stable tag must be v0.4.0")
    if release.get("counts") != EXPECTED_COUNTS:
        fail("release manifest core counts do not match validated counts")

    slices = release.get("delivery_slices", [])
    expected = [(f"V4-{index}", index + 4) for index in range(6)]
    actual = [(item.get("id"), item.get("pull_request")) for item in slices]
    if actual != expected:
        fail(f"release delivery slice history drifted: {actual}")

    compatibility = release.get("compatibility", {})
    if compatibility != {
        "consumer_auto_upgrade": False,
        "brownfield_align_do_not_rewrite": True,
        "grandfather_existing_evidence": True,
    }:
        fail("release compatibility policy drifted")

    pilot = release.get("reference_pilot", {})
    if pilot.get("declared_blueprint") != "0.3.0":
        fail("CareShift must remain declared on 0.3.0 at master release closure")
    if pilot.get("recommendation") != "ADOPT_INCREMENTALLY":
        fail("CareShift compliance recommendation drifted")
    if pilot.get("version_change") != "DEFERRED":
        fail("CareShift consumer version change must remain DEFERRED")
    if release.get("historical_review_target") != "0.4.0-dev":
        fail("historical prerelease review target must remain truthful")


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


def validate_human_release_docs() -> None:
    for path in (
        "README.md",
        "documentation/BLUEPRINT_CURRENT_STATE.md",
        "documentation/BLUEPRINT_V0_4_RELEASE_NOTES.md",
    ):
        text = (ROOT / path).read_text(encoding="utf-8")
        if "0.4.0" not in text:
            fail(f"{path} does not identify Blueprint 0.4.0")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    if "v0.1.0" in readme or "en construcción" in readme:
        fail("README still contains obsolete early-core release messaging")


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
    validate_release_identity()
    print(f"PASS release identity and counts: {EXPECTED_COUNTS}")

    validate_workflows()
    print("PASS stable Greenfield/Brownfield post-API pipeline")

    validate_release_manifest()
    print("PASS machine-readable 0.4.0 release manifest")

    validate_reference_pilot_registry()
    print("PASS reference pilot compatibility and historical review boundary")

    validate_human_release_docs()
    print("PASS release/current-state documentation freshness markers")

    for validator in VALIDATORS:
        run_validator(validator)

    print(
        "\nBlueprint 0.4.0 release validation: PASS "
        "(25 phases, 92 checks, 14 gates, 13 materialized skills, 25 planned skills)"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
