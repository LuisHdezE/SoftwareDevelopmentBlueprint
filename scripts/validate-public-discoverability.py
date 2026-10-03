#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
import pathlib
import re
import sys
from typing import Any, Callable

import yaml
from jsonschema import Draft202012Validator, FormatChecker

ROOT = pathlib.Path(__file__).resolve().parents[1]
SPECIALIST_ID = "specialist:search-ai-discoverability"

CORE_AGENTS = {
    "orchestrator",
    "analyst",
    "planner",
    "architect",
    "database",
    "backend",
    "frontend",
    "qa",
    "security",
    "documentation",
    "auditor",
}

PARTICIPANT_PATTERN = re.compile(r"^specialist:[a-z][a-z0-9-]*$")

REQUIRED_DISCOVERABILITY_CHECKS = {
    "discoverability.surface_classification",
    "discoverability.crawlability",
    "discoverability.indexability",
    "discoverability.canonical",
    "discoverability.sitemap",
    "discoverability.metadata",
    "discoverability.semantic_content",
    "discoverability.internal_linking",
    "discoverability.structured_data",
    "discoverability.ai_crawler_policy",
    "discoverability.entity_clarity",
    "discoverability.factual_consistency",
    "discoverability.measurement",
}

ECOMMERCE_CONDITIONAL_CHECKS = {
    "discoverability.ecommerce_product_structured_data",
    "discoverability.ecommerce_variant_modeling",
    "discoverability.ecommerce_price_availability_consistency",
    "discoverability.ai_product_feed_decision",
}


def load(path: str) -> Any:
    p = ROOT / path
    text = p.read_text(encoding="utf-8")
    if p.suffix == ".json":
        return json.loads(text)
    if p.suffix in {".yaml", ".yml"}:
        return yaml.safe_load(text)
    raise ValueError(f"Unsupported file type: {path}")


def validate_schema(schema_path: str, instance_path: str) -> Any:
    schema = load(schema_path)
    instance = load(instance_path)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(instance), key=lambda e: list(e.path))
    if errors:
        details = "\n".join(
            f"- {instance_path}:{'/'.join(map(str, e.path)) or '<root>'}: {e.message}"
            for e in errors
        )
        raise AssertionError(f"Schema validation failed:\n{details}")
    return instance


def is_participant(value: str) -> bool:
    return value in CORE_AGENTS or bool(PARTICIPANT_PATTERN.fullmatch(value))


def registered_specialists() -> set[str]:
    registry = validate_schema(
        "schemas/specialist-agent-registry.schema.json",
        "catalog/specialist-agents.proposal.yaml",
    )
    return {item["id"] for item in registry["specialists"]}


def validate_capability(doc: dict[str, Any]) -> None:
    classes = doc["surface_classes"]

    expected = {
        "PUBLIC_INDEXABLE": {
            "public": True,
            "index_policy": "index",
            "access_control_required": False,
        },
        "PUBLIC_NO_INDEX": {
            "public": True,
            "index_policy": "noindex",
            "access_control_required": False,
        },
        "PRIVATE": {
            "public": False,
            "index_policy": "not_applicable",
            "access_control_required": True,
        },
    }
    if classes != expected:
        raise AssertionError(
            "Surface-class semantics changed; public/index/private boundary is no longer canonical"
        )

    ai = doc["ai_search"]
    if ai["oai_searchbot_policy"] != "explicit_decision_required":
        raise AssertionError(
            "OAI-SearchBot policy must remain an explicit consumer decision"
        )
    if ai["gptbot_policy_independent"] is not True:
        raise AssertionError(
            "GPTBot training policy must remain independent from search discovery"
        )

    ecommerce = doc["ecommerce"]
    if ecommerce["ai_product_feed"]["applicability"] != "optional":
        raise AssertionError("AI product feed must remain optional")
    if ecommerce["ai_product_feed"]["access_model"] != "current_provider_eligibility_applies":
        raise AssertionError(
            "AI product feed access must defer to current provider eligibility"
        )

    gate = doc["gate"]
    if gate["id"] != "discoverability_ready" or gate["stable_gate"] is not False:
        raise AssertionError(
            "Discoverability gate must remain proposal-only in this increment"
        )


def validate_workflow(doc: dict[str, Any], registered: set[str]) -> None:
    if doc["specialist"] != SPECIALIST_ID:
        raise AssertionError("Unexpected discoverability specialist id")
    if SPECIALIST_ID not in registered:
        raise AssertionError("Discoverability specialist is not registered")

    activation = doc["activation"]
    if activation["surface_class"] != "PUBLIC_INDEXABLE":
        raise AssertionError(
            "Discoverability workflow may only activate for PUBLIC_INDEXABLE surfaces"
        )
    if activation["consumer_opt_in"] is not True:
        raise AssertionError("Discoverability consumer adoption must remain opt-in")

    workflow = doc["workflow"]
    if workflow["mode"] != "conditional_overlay":
        raise AssertionError("Discoverability workflow must remain a conditional overlay")
    if workflow["stable_sequence_mutated"] is not False:
        raise AssertionError("Discoverability overlay cannot mutate stable workflow sequence")
    if workflow["entry_after_gate"] != "interface_scope_ready":
        raise AssertionError(
            "Discoverability overlay must not begin before interface scope is ready"
        )

    sequence = workflow["sequence"]
    phase_bindings = doc["phase_bindings"]
    if set(sequence) != set(phase_bindings) or len(sequence) != len(phase_bindings):
        raise AssertionError(
            "Discoverability workflow sequence must exactly match phase bindings"
        )

    for phase in sequence:
        binding = phase_bindings[phase]
        required = set(binding["required"])
        optional = set(binding["optional"])
        if not required:
            raise AssertionError(f"{phase} must have required participants")
        if required & optional:
            raise AssertionError(
                f"{phase} has participants in both required and optional sets"
            )
        for participant in required | optional:
            if not is_participant(participant):
                raise AssertionError(
                    f"{phase} references invalid participant: {participant}"
                )
            if participant.startswith("specialist:") and participant not in registered:
                raise AssertionError(
                    f"{phase} references unregistered specialist: {participant}"
                )

    gate = doc["gate"]
    evidence = {
        (item["participant"], item["status"])
        for item in gate["required_role_evidence"]
    }
    expected_evidence = {
        (SPECIALIST_ID, "SPECIALIST_PASS"),
        ("qa", "QA_PASS"),
    }
    if evidence != expected_evidence:
        raise AssertionError(
            "discoverability_ready must require specialist PASS and independent QA PASS"
        )

    if set(gate["required_checks"]) != REQUIRED_DISCOVERABILITY_CHECKS:
        raise AssertionError(
            "discoverability_ready required checks drifted from canonical proposal set"
        )

    if set(gate["conditional_checks"]) != ECOMMERCE_CONDITIONAL_CHECKS:
        raise AssertionError(
            "Discoverability ecommerce conditional checks drifted from canonical proposal set"
        )

    if gate["stable_gate"] is not False:
        raise AssertionError("discoverability_ready is not yet a stable Blueprint gate")

    invariants = set(doc["invariants"])
    required_invariant_fragments = (
        "PRIVATE surfaces never enter discoverability flow",
        "OAI-SearchBot policy is independent from GPTBot training policy",
        "AI product feed integration is optional",
        "llms.txt is not a mandatory Blueprint requirement",
        "ranking citation rich results and shopping inclusion are never guaranteed",
    )
    for invariant in required_invariant_fragments:
        if not any(invariant in item for item in invariants):
            raise AssertionError(f"Missing discoverability invariant: {invariant}")


def expect_failure(label: str, action: Callable[[], None]) -> None:
    try:
        action()
    except AssertionError:
        print(f"PASS negative guard: {label}")
        return
    raise AssertionError(f"Negative guard did not fail: {label}")


def main() -> int:
    capability = validate_schema(
        "schemas/public-discoverability.schema.json",
        "catalog/public-discoverability.proposal.yaml",
    )
    validate_capability(capability)
    print("PASS public discoverability capability")

    registered = registered_specialists()
    if SPECIALIST_ID not in registered:
        raise AssertionError("Search & AI Discoverability specialist missing from registry")
    print("PASS discoverability specialist registration")

    workflow = validate_schema(
        "schemas/public-discoverability-workflow.schema.json",
        "catalog/public-discoverability-workflow.proposal.yaml",
    )
    validate_workflow(workflow, registered)
    print("PASS public discoverability workflow overlay")

    mutated = copy.deepcopy(capability)
    mutated["surface_classes"]["PRIVATE"]["access_control_required"] = False
    expect_failure(
        "private surface must retain access control",
        lambda: validate_capability(mutated),
    )

    mutated = copy.deepcopy(capability)
    mutated["ai_search"]["gptbot_policy_independent"] = False
    expect_failure(
        "GPTBot policy cannot be coupled to search discovery",
        lambda: validate_capability(mutated),
    )

    mutated = copy.deepcopy(capability)
    mutated["ecommerce"]["ai_product_feed"]["applicability"] = "not_applicable"
    expect_failure(
        "canonical ecommerce proposal keeps AI product feed as optional decision",
        lambda: validate_capability(mutated),
    )

    mutated = copy.deepcopy(workflow)
    mutated["activation"]["surface_class"] = "PRIVATE"
    expect_failure(
        "private surfaces cannot activate discoverability workflow",
        lambda: validate_workflow(mutated, registered),
    )

    mutated = copy.deepcopy(workflow)
    mutated["gate"]["required_role_evidence"] = [
        {"participant": SPECIALIST_ID, "status": "SPECIALIST_PASS"}
    ]
    expect_failure(
        "specialist cannot self-certify discoverability gate",
        lambda: validate_workflow(mutated, registered),
    )

    mutated = copy.deepcopy(workflow)
    mutated["gate"]["conditional_checks"].remove(
        "discoverability.ai_product_feed_decision"
    )
    expect_failure(
        "ecommerce AI product-feed applicability decision remains explicit",
        lambda: validate_workflow(mutated, registered),
    )

    print("Blueprint public discoverability proposal validation: PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise
