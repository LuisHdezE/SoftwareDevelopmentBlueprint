#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "catalog" / "skills.yaml"
ROOT_VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
STABLE_V53 = "0.5.3"
DEVELOPMENT_V54 = "0.5.4-dev"
LEGACY_SKILL_COMPONENT = "0.5.0"
MOBILE_LICENSING_SKILL = "dev-mobile-licensing"
DEVELOPMENT_SKILLS = {
    "dev-android-client-architecture",
    "dev-ios-client-architecture",
    "dev-functional-interface-slice",
}

REQUIRED_FRONTMATTER = {
    "id", "title", "version", "status", "category",
    "applies_to", "phases", "canonical_references",
}
REQUIRED_HEADINGS = [
    "Purpose", "When to Use", "Inputs", "Procedure", "Outputs",
    "Stop Conditions", "Guardrails", "Canonical References", "Completion Signal",
]
PRODUCT_MARKERS = ["CareShift", "VolquetasManager", "Volquetas Manager", "vm-", "GestioApp"]


def fail(message: str) -> None:
    raise AssertionError(message)


def active_catalog_version() -> str:
    marker = ROOT / "DEVELOPMENT_VERSION"
    if not marker.exists():
        return STABLE_V53
    value = marker.read_text(encoding="utf-8").strip()
    if value != DEVELOPMENT_V54:
        fail(f"unexpected DEVELOPMENT_VERSION for skill validation: {value}")
    return DEVELOPMENT_V54


def parse_frontmatter(path: Path) -> tuple[dict, str]:
    text = path.read_text(encoding="utf-8-sig")
    if not text.startswith("---\n"):
        fail(f"{path}: missing YAML frontmatter opening")
    end = text.find("\n---\n", 4)
    if end < 0:
        fail(f"{path}: missing YAML frontmatter closing")
    frontmatter = yaml.safe_load(text[4:end]) or {}
    body = text[end + 5:]
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
            for spec in conditional.values():
                if isinstance(spec, dict):
                    refs.update(spec.get("skills", []) or [])
    return refs


def expected_skill_version(skill_id: str, active_version: str) -> str:
    if active_version == DEVELOPMENT_V54 and skill_id in DEVELOPMENT_SKILLS:
        return DEVELOPMENT_V54
    if skill_id == MOBILE_LICENSING_SKILL:
        return STABLE_V53
    return LEGACY_SKILL_COMPONENT


def validate_skill(skill_id: str, spec: dict, active_version: str) -> None:
    if spec.get("status") != "materialized":
        fail(f"{skill_id}: registry status must be materialized")
    path_value = spec.get("path")
    expected_path = f"skills/{skill_id}/SKILL.md"
    if path_value != expected_path:
        fail(f"{skill_id}: path must be {expected_path}, got {path_value}")
    path = ROOT / expected_path
    if not path.is_file():
        fail(f"{skill_id}: materialized path does not exist")

    frontmatter, body = parse_frontmatter(path)
    missing = REQUIRED_FRONTMATTER - set(frontmatter)
    if missing:
        fail(f"{skill_id}: missing frontmatter fields: {sorted(missing)}")
    if frontmatter["id"] != skill_id or frontmatter["status"] != "materialized":
        fail(f"{skill_id}: frontmatter identity/status mismatch")
    if frontmatter["category"] != spec.get("category"):
        fail(f"{skill_id}: category mismatch")
    expected_version = expected_skill_version(skill_id, active_version)
    if frontmatter["version"] != expected_version:
        fail(f"{skill_id}: expected version {expected_version}, got {frontmatter['version']}")
    if not isinstance(frontmatter["applies_to"], list) or not frontmatter["applies_to"]:
        fail(f"{skill_id}: applies_to must be non-empty")
    if not isinstance(frontmatter["phases"], list) or not frontmatter["phases"]:
        fail(f"{skill_id}: phases must be non-empty")
    refs = frontmatter["canonical_references"]
    if not isinstance(refs, list) or not refs:
        fail(f"{skill_id}: canonical_references must be non-empty")
    for ref in refs:
        if not isinstance(ref, str) or not (ROOT / ref).exists():
            fail(f"{skill_id}: canonical reference missing: {ref}")
    for heading in REQUIRED_HEADINGS:
        if not re.search(rf"^## {re.escape(heading)}\s*$", body, flags=re.MULTILINE):
            fail(f"{skill_id}: missing required heading: {heading}")
    if f"# {frontmatter['title']}" not in body:
        fail(f"{skill_id}: H1 title mismatch")
    for marker in PRODUCT_MARKERS:
        if marker.lower() in body.lower():
            fail(f"{skill_id}: product-specific marker leaked: {marker}")
    if len(body.strip()) < 900:
        fail(f"{skill_id}: procedure is suspiciously small")
    print(f"PASS skill: {skill_id} -> {expected_path} ({expected_version})")


def validate_development_ios_category(catalog: dict, materialized: set[str]) -> None:
    ios = catalog.get("categories", {}).get("ios")
    if not isinstance(ios, dict):
        fail("0.5.4-dev skill catalog must define ios category")
    if ios.get("conditional_on") != {"ios": True}:
        fail("iOS skill category must load only when capabilities.ios=true")
    required = {"dev-ios-client-architecture", "dev-functional-interface-slice"}
    if not required.issubset(set(ios.get("skills", []))):
        fail("iOS skill category missing required client architecture/functional slice skills")
    if "dev-ios-client-architecture" not in materialized:
        fail("0.5.4-dev must materialize dev-ios-client-architecture")


def main() -> int:
    if ROOT_VERSION != STABLE_V53:
        fail(f"skill validator requires stable root VERSION={STABLE_V53}, got {ROOT_VERSION}")
    active_version = active_catalog_version()
    catalog = yaml.safe_load(CATALOG_PATH.read_text(encoding="utf-8")) or {}
    if catalog.get("version") != active_version:
        fail(f"catalog/skills.yaml must declare active component version {active_version}")
    contract = catalog.get("skill_model", {}).get("contract", {})
    if set(contract.get("required_frontmatter", [])) != REQUIRED_FRONTMATTER:
        fail("catalog skill frontmatter contract drifted")
    if contract.get("required_sections", []) != REQUIRED_HEADINGS:
        fail("catalog skill section contract drifted")

    registry = catalog.get("registry", {})
    if not isinstance(registry, dict):
        fail("registry must be a mapping")
    planned = flatten_planned(catalog.get("planned_registry", {}))
    materialized = set(registry)
    if materialized & planned:
        fail(f"skills cannot be both materialized and planned: {sorted(materialized & planned)}")

    mandatory_key = "mandatory_v0_5_4_development_materialized" if active_version == DEVELOPMENT_V54 else "mandatory_v0_5_materialized"
    mandatory = catalog.get(mandatory_key, [])
    if not isinstance(mandatory, list) or not mandatory:
        fail(f"{mandatory_key} must be non-empty")
    missing = set(mandatory) - materialized
    if missing:
        fail(f"mandatory skills missing: {sorted(missing)}")
    if MOBILE_LICENSING_SKILL not in materialized:
        fail("mobile licensing skill must remain materialized")

    category_ids = category_references(catalog.get("categories", {}))
    unknown = category_ids - materialized - planned
    if unknown:
        fail(f"category references unknown skills: {sorted(unknown)}")
    unreferenced = materialized - category_ids
    if unreferenced:
        fail(f"materialized skills unreferenced by categories: {sorted(unreferenced)}")

    if active_version == DEVELOPMENT_V54:
        validate_development_ios_category(catalog, materialized)
        if set(mandatory) != materialized:
            fail("0.5.4-dev mandatory skill set must cover every materialized skill")

    for skill_id, spec in registry.items():
        validate_skill(skill_id, spec, active_version)

    expected_counts = (16, 25) if active_version == DEVELOPMENT_V54 else (15, 25)
    if (len(materialized), len(planned)) != expected_counts:
        fail(
            f"skill counts drifted for {active_version}: "
            f"materialized={len(materialized)}, planned={len(planned)}, expected={expected_counts}"
        )
    print(
        "Blueprint skill validation: PASS "
        f"(active={active_version}; materialized={len(materialized)}; planned={len(planned)})"
    )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except AssertionError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        sys.exit(1)
