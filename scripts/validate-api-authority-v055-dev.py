#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
STABLE_SCHEMA_PATH = ROOT / "schemas/project.schema.json"
AUTHORITY_SCHEMA_PATH = ROOT / "schemas/project-api-authority-v055-dev.schema.json"
API_OPTIONAL_EXAMPLE = ROOT / "templates/project-v055-dev.api-optional.example.yaml"
API_BACKED_EXAMPLE = ROOT / "templates/project-v055-dev.api-backed.example.yaml"

STABLE_VERSION = "0.5.4"
DEVELOPMENT_VERSION = "0.5.5-dev"
STABLE_SCHEMA_ID = "https://eliasworks.dev/blueprint/0.5.4/project.schema.json"
AUTHORITY_SCHEMA_ID = "https://eliasworks.dev/blueprint/0.5.5-dev/project-api-authority.schema.json"

CLAIM_KEYS = (
    "remote_authoritative_business_data",
    "server_authentication",
    "server_authorization",
    "remote_persistent_mutations",
    "permission_enforcement",
    "backend_only_invariants",
)


def fail(message: str) -> None:
    raise AssertionError(message)


def load_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        fail(f"{path.relative_to(ROOT)} must contain an object")
    return value


def load_yaml(path: Path) -> dict:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        fail(f"{path.relative_to(ROOT)} must contain an object")
    return value


def errors_for(validator: Draft202012Validator, document: dict) -> list[str]:
    return [error.message for error in sorted(validator.iter_errors(document), key=lambda e: list(e.path))]


def expect_valid(validators: tuple[Draft202012Validator, ...], label: str, document: dict) -> None:
    errors: list[str] = []
    for validator in validators:
        errors.extend(errors_for(validator, document))
    if errors:
        fail(f"{label} should be valid; got: {' | '.join(errors)}")
    print(f"PASS positive: {label}")


def expect_authority_invalid(
    authority_validator: Draft202012Validator, label: str, document: dict
) -> None:
    errors = errors_for(authority_validator, document)
    if not errors:
        fail(f"{label} should be rejected by the 0.5.5-dev authority overlay")
    print(f"PASS negative: {label}")


def validate_authority_transition(previous: dict, current: dict) -> None:
    previous_api = previous["authority"]["api"]
    current_api = current["authority"]["api"]
    if previous_api["mode"] == current_api["mode"]:
        return
    if current_api["revision"] <= previous_api["revision"]:
        fail("API authority mode transition requires revision increment")
    if current_api["decision_ref"] == previous_api["decision_ref"]:
        fail("API authority mode transition requires a new governed decision_ref")


def expect_transition_invalid(label: str, previous: dict, current: dict) -> None:
    try:
        validate_authority_transition(previous, current)
    except AssertionError:
        print(f"PASS negative transition: {label}")
        return
    fail(f"{label} should be rejected")


def main() -> int:
    stable_schema = load_json(STABLE_SCHEMA_PATH)
    authority_schema = load_json(AUTHORITY_SCHEMA_PATH)

    if stable_schema.get("$id") != STABLE_SCHEMA_ID:
        fail("stable 0.5.4 project schema identity drifted")
    if authority_schema.get("$id") != AUTHORITY_SCHEMA_ID:
        fail("0.5.5-dev authority overlay schema identity drifted")

    Draft202012Validator.check_schema(stable_schema)
    Draft202012Validator.check_schema(authority_schema)

    stable_validator = Draft202012Validator(stable_schema)
    authority_validator = Draft202012Validator(authority_schema)
    validators = (stable_validator, authority_validator)

    api_optional = load_yaml(API_OPTIONAL_EXAMPLE)
    api_backed = load_yaml(API_BACKED_EXAMPLE)

    for document in (api_optional, api_backed):
        if document.get("blueprint", {}).get("version") != STABLE_VERSION:
            fail("hardening examples must remain based on stable project manifest 0.5.4")
    if (ROOT / "VERSION").read_text(encoding="utf-8").strip() != STABLE_VERSION:
        fail("Increment 1 must not promote root VERSION")
    if (ROOT / "DEVELOPMENT_VERSION").read_text(encoding="utf-8").strip() != DEVELOPMENT_VERSION:
        fail("Increment 1 requires the governed 0.5.5-dev lane")

    expect_valid(validators, "frontend-only local/static consumer", api_optional)

    mock_only = copy.deepcopy(api_optional)
    mock_only["project"]["name"] = "Provider Driven Mock UI"
    mock_only["authority"]["api"]["allowed_sources"] = ["mock_non_authoritative"]
    expect_valid(validators, "mock/provider-driven non-authoritative consumer", mock_only)

    expect_valid(validators, "strict API-backed consumer", api_backed)

    permission_bypass = copy.deepcopy(api_optional)
    permission_bypass["authority"]["api"]["claims"]["permission_enforcement"] = True
    expect_authority_invalid(
        authority_validator,
        "api_optional cannot claim permission enforcement",
        permission_bypass,
    )

    remote_mutation = copy.deepcopy(api_optional)
    remote_mutation["authority"]["api"]["claims"]["remote_persistent_mutations"] = True
    expect_authority_invalid(
        authority_validator,
        "api_optional cannot claim remote persistent mutation",
        remote_mutation,
    )

    server_auth = copy.deepcopy(api_optional)
    server_auth["authority"]["api"]["claims"]["server_authentication"] = True
    expect_authority_invalid(
        authority_validator,
        "api_optional cannot claim server authentication",
        server_auth,
    )

    fake_openapi = copy.deepcopy(api_optional)
    fake_openapi["artifact_locations"]["openapi"] = "openapi.yaml"
    expect_authority_invalid(
        authority_validator,
        "api_optional forbids OpenAPI binding",
        fake_openapi,
    )

    omitted_authority = copy.deepcopy(api_optional)
    omitted_authority.pop("authority")
    expect_authority_invalid(
        authority_validator,
        "API authority declaration cannot be omitted",
        omitted_authority,
    )

    backed_without_openapi = copy.deepcopy(api_backed)
    backed_without_openapi["artifact_locations"].pop("openapi")
    expect_authority_invalid(
        authority_validator,
        "api_backed requires OpenAPI artifact location",
        backed_without_openapi,
    )

    backed_without_backend = copy.deepcopy(api_backed)
    backed_without_backend["stack"]["backend"] = None
    expect_authority_invalid(
        authority_validator,
        "api_backed requires declared backend stack",
        backed_without_backend,
    )

    fake_backed = copy.deepcopy(api_backed)
    for key in CLAIM_KEYS:
        fake_backed["authority"]["api"]["claims"][key] = False
    expect_authority_invalid(
        authority_validator,
        "api_backed requires at least one authoritative server claim",
        fake_backed,
    )

    offline_optional = copy.deepcopy(api_optional)
    offline_optional["capabilities"]["android"] = True
    offline_optional["capabilities"]["mobile_licensing"] = False
    offline_optional["capabilities"]["offline_mobile"] = True
    offline_optional["mobile"] = {"strategy": "native"}
    expect_authority_invalid(
        authority_validator,
        "offline_mobile remains API-backed under current governed semantics",
        offline_optional,
    )

    legitimate_transition = copy.deepcopy(api_backed)
    legitimate_transition["authority"]["api"]["revision"] = 2
    legitimate_transition["authority"]["api"]["decision_ref"] = "ADR-API-AUTHORITY-002"
    validate_authority_transition(api_optional, legitimate_transition)
    print("PASS positive transition: governed api_optional -> api_backed")

    silent_revision = copy.deepcopy(api_backed)
    silent_revision["authority"]["api"]["revision"] = 1
    silent_revision["authority"]["api"]["decision_ref"] = "ADR-API-AUTHORITY-002"
    expect_transition_invalid(
        "mode change without revision increment",
        api_optional,
        silent_revision,
    )

    silent_decision = copy.deepcopy(api_backed)
    silent_decision["authority"]["api"]["revision"] = 2
    silent_decision["authority"]["api"]["decision_ref"] = api_optional["authority"]["api"]["decision_ref"]
    expect_transition_invalid(
        "mode change without new decision_ref",
        api_optional,
        silent_decision,
    )

    print("\nBlueprint 0.5.5-dev API authority model: PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
