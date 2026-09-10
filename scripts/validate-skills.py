#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "catalog" / "skills.yaml"
STABLE_VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
STABLE_V4 = "0.4.0"
DEV_V5 = "0.5.0-dev"
STABLE_V5 = "0.5.0"
STABLE_V51 = "0.5.1"
STABLE_V52 = "0.5.2"
DEV_V53 = "0.5.3-dev"

REQUIRED_FRONTMATTER = {
    "id",
    "title",
    "version",
    "status",
    "category",
    "applies_to",
    "phases",
    "canonical_references",
}

REQUIRED_HEADINGS = [
    "Purpose",
    "When to Use",
    "Inputs",
    "Procedure",
    "Outputs",
    "Stop Conditions",
    "Guardrails",
    "Canonical References",
    "Completion Signal",
]

PRODUCT_MARKERS = [
    "CareShift",
    "VolquetasManager",
    "Volquetas Manager",
    "vm-",
    "GestioApp",
]


def fail(message: str) -> None:
    raise AssertionError(message)


def parse_frontmatter(path: Path) -> tuple[dict, str]:
    text = path.read_text(encoding="utf-8-sig")
    if not text.startswith("---\n"):
        fail(f"{path}: missing YAML frontmatter opening")
    end = text.find("\n---\n", 4)
    if end < 0:
        fail(f"{path}: missing YAML frontmatter closing")
    frontmatter = yaml.safe_load(text[4:end]) or {}
    body = text[end + 5 :]
    if not isinstance(frontmatter, dict):
        fail(f"{path}: frontmatter must be a mapping")
    return frontmatter, body


def flatten_planned(planned_registry: dict) -> set[str]:
    result: set[str] = set()
    for category, ids in planned_registry.items():
        if not isinstance(ids, list):
            fail(f"planned_registry.{category} must be a list")
        for skill_id in ids:
            if skill_id in result:
                fail(f"planned skill duplicated: {skill_id}")
            result.add(skill_id)
    return result


def category_references(categories: dict) -> set[str]:
    refs: set[str] = set()
    for category_name, category in categories.items():
        if not isinstance(category, dict):
            continue
        for key in ("always_consider", "skills"):
            values = category.get(key, [])
            if values:
                if not isinstance(values, list):
                    fail(f"categories.{category_name}.{key} must be a list")
                refs.update(values)
        conditional = category.get("conditional", {})
        if isinstance(conditional, dict):
            for conditional_spec in conditional.values():
                if isinstance(conditional_spec, dict):
                    values = conditional_spec.get("skills", [])
                    if values:
                        refs.update(values)
    return refs


def validate_catalog_identity(catalog_version: str) -> None:
    if catalog_version == STABLE_VERSION:
        return
    if STABLE_VERSION == STABLE_V4 and catalog_version == DEV_V5:
        return
    if STABLE_VERSION in {STABLE_V51, STABLE_V52} and catalog_version == STABLE_V5:
        return
    # 0.5.3 hardening is developed on top of stable 0.5.2 before release closure.
    if STABLE_VERSION == STABLE_V52 and catalog_version == DEV_V53:
        return
    fail(
        "catalog/skills.yaml version must match root VERSION or an explicitly "
        "supported component-provenance compatibility transition; "
        f"VERSION={STABLE_VERSION}, catalog={catalog_version}"
    )


def expected_skill_version(skill_id: str, catalog_version: str) -> str:
    if catalog_version == DEV_V53 and skill_id != "dev-mobile-licensing":
        return STABLE_V5
    return catalog_version


def validate_skill(skill_id: str, spec: dict, catalog_version: str) -> None:
    if spec.get("status") != "materialized":
        fail(f"{skill_id}: registry status must be materialized")
    path_value = spec.get("path")
    if not isinstance(path_value, str):
        fail(f"{skill_id}: materialized registry entry requires path")
    path = ROOT / path_value
    if not path.is_file():
        fail(f"{skill_id}: materialized path does not exist: {path_value}")

    expected_path = f"skills/{skill_id}/SKILL.md"
    if path_value != expected_path:
        fail(f"{skill_id}: path must be {expected_path}, got {path_value}")

    frontmatter, body = parse_frontmatter(path)
    missing = REQUIRED_FRONTMATTER - set(frontmatter)
    if missing:
        fail(f"{skill_id}: missing frontmatter fields: {sorted(missing)}")

    if frontmatter["id"] != skill_id:
        fail(f"{skill_id}: frontmatter id mismatch")
    if frontmatter["status"] != "materialized":
        fail(f"{skill_id}: frontmatter status must be materialized")
    if frontmatter["category"] != spec.get("category"):
        fail(
            f"{skill_id}: category mismatch "
            f"catalog={spec.get('category')} file={frontmatter['category']}"
        )
    expected_version = expected_skill_version(skill_id, catalog_version)
    if frontmatter["version"] != expected_version:
        fail(
            f"{skill_id}: expected version {expected_version}, "
            f"got {frontmatter['version']}"
        )
    if not isinstance(frontmatter["applies_to"], list) or not frontmatter["applies_to"]:
        fail(f"{skill_id}: applies_to must be a non-empty list")
    if not isinstance(frontmatter["phases"], list) or not frontmatter["phases"]:
        fail(f"{skill_id}: phases must be a non-empty list")

    canonical_refs = frontmatter["canonical_references"]
    if not isinstance(canonical_refs, list) or not canonical_refs:
        fail(f"{skill_id}: canonical_references must be a non-empty list")
    for ref in canonical_refs:
        if not isinstance(ref, str):
            fail(f"{skill_id}: canonical reference must be a string")
        if not (ROOT / ref).exists():
            fail(f"{skill_id}: canonical reference does not exist: {ref}")

    for heading in REQUIRED_HEADINGS:
        if not re.search(rf"^## {re.escape(heading)}\s*$", body, flags=re.MULTILINE):
            fail(f"{skill_id}: missing required heading: {heading}")

    if f"# {frontmatter['title']}" not in body:
        fail(f"{skill_id}: H1 title must match frontmatter title")

    for marker in PRODUCT_MARKERS:
        if marker.lower() in body.lower():
            fail(f"{skill_id}: product-specific marker leaked into reusable skill: {marker}")

    if len(body.strip()) < 900:
        fail(f"{skill_id}: procedure is suspiciously small to be executable")

    print(f"PASS skill: {skill_id} -> {path_value}")


def main() -> int:
    if not STABLE_VERSION:
        fail("VERSION must not be empty")

    catalog = yaml.safe_load(CATALOG_PATH.read_text(encoding="utf-8")) or {}
    catalog_version = catalog.get("version")
    if not isinstance(catalog_version, str):
        fail("catalog/skills.yaml requires string version")
    validate_catalog_identity(catalog_version)

    skill_model = catalog.get("skill_model", {})
    contract = skill_model.get("contract", {})
    declared_frontmatter = set(contract.get("required_frontmatter", []))
    if declared_frontmatter != REQUIRED_FRONTMATTER:
        fail("catalog skill contract required_frontmatter drifted from validator")

    declared_sections = contract.get("required_sections", [])
    if declared_sections != REQUIRED_HEADINGS:
        fail("catalog skill contract required_sections drifted from validator")

    registry = catalog.get("registry", {})
    if not isinstance(registry, dict):
        fail("registry must be a mapping")

    historical_v4 = catalog.get("mandatory_v0_4_materialized", [])
    if not isinstance(historical_v4, list) or len(historical_v4) != len(set(historical_v4)):
        fail("mandatory_v0_4_materialized must be a unique list")

    current_mandatory_key = (
        "mandatory_v0_5_materialized"
        if catalog_version.startswith("0.5")
        else "mandatory_v0_4_materialized"
    )
    mandatory = catalog.get(current_mandatory_key, [])
    if not isinstance(mandatory, list) or not mandatory or len(mandatory) != len(set(mandatory)):
        fail(f"{current_mandatory_key} must be a non-empty unique list")

    planned = flatten_planned(catalog.get("planned_registry", {}))
    materialized = set(registry)

    overlap = materialized & planned
    if overlap:
        fail(f"skill cannot be materialized and planned: {sorted(overlap)}")

    missing_mandatory = set(mandatory) - materialized
    if missing_mandatory:
        fail(f"mandatory skills not materialized: {sorted(missing_mandatory)}")

    category_ids = category_references(catalog.get("categories", {}))
    unknown = category_ids - materialized - planned
    if unknown:
        fail(f"category references unknown skills: {sorted(unknown)}")

    unreferenced_materialized = materialized - category_ids
    if unreferenced_materialized:
        fail(
            "materialized skills must appear in at least one category: "
            f"{sorted(unreferenced_materialized)}"
        )

    for skill_id, spec in registry.items():
        validate_skill(skill_id, spec, catalog_version)

    print(
        "Blueprint skill validation: PASS "
        f"(root VERSION {STABLE_VERSION}; skill component {catalog_version}; "
        f"{len(materialized)} materialized, {len(planned)} planned)"
    )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except AssertionError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        sys.exit(1)
