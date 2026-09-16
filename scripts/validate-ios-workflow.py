#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
STABLE_VERSION = "0.5.3"
DEVELOPMENT_VERSION = "0.5.4-dev"
EXPECTED_COUNTS = {
    "phases": 29,
    "checks": 146,
    "gates": 19,
    "materialized_skills": 16,
    "planned_skills": 25,
}
EXPECTED_IMPLEMENTATION_MAP = {
    "web": "web_implementation",
    "android": "android_implementation",
    "ios": "ios_implementation",
}
IOS_BLOCKING_GATES = {
    "api_gate",
    "interface_inventory_ready",
    "design_system_ready",
    "client_architecture_ready",
}


def fail(message: str) -> None:
    raise AssertionError(message)


def load_yaml(path: str) -> dict:
    value = yaml.safe_load((ROOT / path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        fail(f"{path} must contain a mapping")
    return value


def by_id(values: list[dict], label: str) -> dict[str, dict]:
    result: dict[str, dict] = {}
    for item in values:
        item_id = item.get("id")
        if not isinstance(item_id, str) or not item_id:
            fail(f"{label} item missing id")
        if item_id in result:
            fail(f"duplicate {label} id: {item_id}")
        result[item_id] = item
    return result


def planned_skill_count(catalog: dict) -> int:
    result: set[str] = set()
    for category, values in catalog.get("planned_registry", {}).items():
        if not isinstance(values, list):
            fail(f"planned_registry.{category} must be a list")
        for skill_id in values:
            if skill_id in result:
                fail(f"planned skill duplicated: {skill_id}")
            result.add(skill_id)
    return len(result)


def parse_frontmatter(path: str) -> dict:
    text = (ROOT / path).read_text(encoding="utf-8-sig")
    if not text.startswith("---\n"):
        fail(f"{path} missing frontmatter")
    end = text.find("\n---\n", 4)
    if end < 0:
        fail(f"{path} missing frontmatter closing marker")
    value = yaml.safe_load(text[4:end]) or {}
    if not isinstance(value, dict):
        fail(f"{path} frontmatter must be a mapping")
    return value


def validate_identity_and_provenance() -> None:
    root_version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    development_version = (ROOT / "DEVELOPMENT_VERSION").read_text(encoding="utf-8").strip()
    if root_version != STABLE_VERSION:
        fail(f"hardening must keep VERSION={STABLE_VERSION}, got {root_version}")
    if development_version != DEVELOPMENT_VERSION:
        fail(f"DEVELOPMENT_VERSION must be {DEVELOPMENT_VERSION}, got {development_version}")
    for path in (
        "catalog/phases.yaml",
        "catalog/checks.yaml",
        "catalog/gates.yaml",
        "catalog/skills.yaml",
        "workflows/greenfield.yaml",
        "workflows/brownfield.yaml",
    ):
        if load_yaml(path).get("version") != DEVELOPMENT_VERSION:
            fail(f"{path} must declare {DEVELOPMENT_VERSION} after iOS workflow hardening")
    print("PASS iOS workflow/catalog development provenance")


def validate_phase_model() -> None:
    phases_doc = load_yaml("catalog/phases.yaml")
    phases = by_id(phases_doc.get("phases", []), "phase")
    expected = {
        "web_implementation": ("Web Implementation Profile", "web", 171),
        "android_implementation": ("Android Implementation Profile", "android", 172),
        "ios_implementation": ("iOS Implementation Profile", "ios", 173),
    }
    for phase_id, (name, capability, order) in expected.items():
        phase = phases.get(phase_id)
        if not phase:
            fail(f"missing implementation phase: {phase_id}")
        if phase.get("name") != name:
            fail(f"{phase_id} must use technology-neutral name {name}")
        if phase.get("order") != order:
            fail(f"{phase_id} order drifted")
        if phase.get("execution_scope") != "interface_slice_platform":
            fail(f"{phase_id} must remain scoped to interface_slice_platform")
        if phase.get("parent_phase") != "functional_interface_slice":
            fail(f"{phase_id} must remain child of functional_interface_slice")
        if phase.get("conditional_capability") != capability:
            fail(f"{phase_id} must be conditional on capability {capability}")
        if phase.get("requires_gates") != ["client_architecture_ready"]:
            fail(f"{phase_id} must require client_architecture_ready")
    rule = phases["functional_interface_slice"].get("rule", "")
    if "applicable platform profile" not in rule or "exact slice + platform" not in rule:
        fail("functional_interface_slice phase must remain platform-neutral and scoped")
    print("PASS web/android/iOS implementation phase model")


def validate_checks_and_gates() -> None:
    checks = by_id(load_yaml("catalog/checks.yaml").get("checks", []), "check")
    ios_inventory = checks.get("ui.ios_inventory")
    if not ios_inventory:
        fail("ui.ios_inventory check missing")
    expected_check = {
        "id": "ui.ios_inventory",
        "phase": "interface_inventory",
        "type": "CONDITIONAL",
        "capability": "ios",
        "verification": "evidence",
    }
    for key, value in expected_check.items():
        if ios_inventory.get(key) != value:
            fail(f"ui.ios_inventory.{key} must be {value}")
    licensing_decision = checks.get("requirements.mobile_licensing_decision", {})
    if licensing_decision.get("capability") != "android":
        fail("mobile licensing decision check must remain Android-scoped")

    gates = by_id(load_yaml("catalog/gates.yaml").get("gates", []), "gate")
    for gate_id in IOS_BLOCKING_GATES:
        if "ios_implementation" not in set(gates[gate_id].get("blocks", [])):
            fail(f"{gate_id} must block ios_implementation")
    inventory_gate = gates["interface_inventory_ready"]
    if "ui.ios_inventory" not in set(inventory_gate.get("require_if_applicable", [])):
        fail("interface_inventory_ready must conditionally require ui.ios_inventory")
    if gates["client_architecture_ready"].get("evaluation_scope") != "interface_slice_platform":
        fail("client_architecture_ready must remain interface_slice_platform scoped")
    if any(gate_id.startswith("ios_") for gate_id in gates):
        fail("iOS must reuse scoped canonical gates instead of introducing platform-specific gate IDs")
    print("PASS iOS inventory check and scoped gate reuse")


def validate_workflows() -> None:
    lifecycle = ["INVENTORIED", "READY", "IN_PROGRESS", "FUNCTIONAL", "ACCEPTED"]
    for path in ("workflows/greenfield.yaml", "workflows/brownfield.yaml"):
        workflow = load_yaml(path)
        pipeline = workflow.get("functional_interface_slice_pipeline", {})
        if pipeline.get("scope_key") != "interface_slice_platform":
            fail(f"{path} functional slice scope drifted")
        if pipeline.get("client_implementation") != EXPECTED_IMPLEMENTATION_MAP:
            fail(f"{path} client implementation mapping must be exactly web/android/ios")
        if pipeline.get("lifecycle") != lifecycle:
            fail(f"{path} lifecycle drifted")
        blocker = pipeline.get("blocker_condition", {})
        if blocker.get("id") != "BLOCKED_BY_API" or blocker.get("overlays_lifecycle") is not True:
            fail(f"{path} BLOCKED_BY_API overlay semantics drifted")
        rules = set(pipeline.get("rules", []))
        if "one_platform_result_does_not_authorize_another" not in rules:
            fail(f"{path} must preserve independent platform acceptance")
        licensing = workflow.get("conditional_capabilities", {}).get("mobile_licensing", {})
        if licensing.get("decision_required_when") != {"android": True}:
            fail(f"{path} mobile licensing applicability must remain exactly Android-only")
        licensing_rules = set(licensing.get("rules", []))
        if "ios_alone_does_not_trigger_mobile_licensing" not in licensing_rules:
            fail(f"{path} must explicitly preserve iOS licensing non-implication")
    print("PASS Greenfield/Brownfield iOS workflow mapping and licensing isolation")


def validate_skill_model() -> None:
    catalog = load_yaml("catalog/skills.yaml")
    registry = catalog.get("registry", {})
    ios_category = catalog.get("categories", {}).get("ios", {})
    if ios_category.get("conditional_on") != {"ios": True}:
        fail("iOS skill category must be conditional on ios=true")
    required_skills = {"dev-ios-client-architecture", "dev-functional-interface-slice"}
    if not required_skills.issubset(set(ios_category.get("skills", []))):
        fail("iOS skill category missing required skills")
    ios_spec = registry.get("dev-ios-client-architecture")
    if ios_spec != {
        "status": "materialized",
        "category": "ios",
        "path": "skills/dev-ios-client-architecture/SKILL.md",
    }:
        fail("dev-ios-client-architecture registry contract drifted")

    ios_frontmatter = parse_frontmatter("skills/dev-ios-client-architecture/SKILL.md")
    if ios_frontmatter.get("version") != DEVELOPMENT_VERSION or ios_frontmatter.get("category") != "ios":
        fail("iOS client architecture skill frontmatter provenance/category drifted")
    android_frontmatter = parse_frontmatter("skills/dev-android-client-architecture/SKILL.md")
    if android_frontmatter.get("version") != DEVELOPMENT_VERSION:
        fail("Android client architecture skill must carry 0.5.4-dev technology-neutral provenance")
    functional_frontmatter = parse_frontmatter("skills/dev-functional-interface-slice/SKILL.md")
    if functional_frontmatter.get("version") != DEVELOPMENT_VERSION:
        fail("functional slice skill must carry 0.5.4-dev provenance")
    if "ios_implementation" not in set(functional_frontmatter.get("phases", [])):
        fail("functional slice skill must include ios_implementation")

    ios_text = (ROOT / "skills/dev-ios-client-architecture/SKILL.md").read_text(encoding="utf-8")
    for token in (
        "does not enable iOS by itself",
        "does not mandate Swift",
        "iOS alone does not imply",
        "Android or Web evidence cannot satisfy this scope",
    ):
        if token not in ios_text:
            fail(f"iOS client architecture skill missing required guardrail token: {token}")
    print("PASS iOS skill/category and platform-independent acceptance guardrails")


def validate_counts() -> None:
    phases = len(load_yaml("catalog/phases.yaml").get("phases", []))
    checks = len(load_yaml("catalog/checks.yaml").get("checks", []))
    gates = len(load_yaml("catalog/gates.yaml").get("gates", []))
    skills = load_yaml("catalog/skills.yaml")
    materialized = len(skills.get("registry", {}))
    planned = planned_skill_count(skills)
    actual = {
        "phases": phases,
        "checks": checks,
        "gates": gates,
        "materialized_skills": materialized,
        "planned_skills": planned,
    }
    if actual != EXPECTED_COUNTS:
        fail(f"0.5.4-dev workflow/skill counts drifted: expected {EXPECTED_COUNTS}, got {actual}")
    print(f"PASS 0.5.4-dev workflow/skill counts: {actual}")


def main() -> int:
    validate_identity_and_provenance()
    validate_phase_model()
    validate_checks_and_gates()
    validate_workflows()
    validate_skill_model()
    validate_counts()
    print("PASS Blueprint 0.5.4-dev iOS workflow/catalog/skill validation")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"FAIL: {exc}")
        raise SystemExit(1)
