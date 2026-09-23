#!/usr/bin/env python3
"""Validate Blueprint 0.5.5-dev Integration QA authority semantics."""
from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schemas/integration-qa-authority-v055-dev.schema.json"
API_BACKED = ROOT / "templates/integration-qa-authority.api-backed-v055-dev.example.json"
API_OPTIONAL = ROOT / "templates/integration-qa-authority.api-optional-v055-dev.example.json"
CLIENT_BACKED = ROOT / "templates/client-slice-authority.api-backed-v055-dev.example.json"
CLIENT_OPTIONAL = ROOT / "templates/client-slice-authority.api-optional-v055-dev.example.json"
CHECKS = ROOT / "catalog/checks.yaml"
GATES = ROOT / "catalog/gates.yaml"
APPLICABILITY = ROOT / "catalog/workflow-gate-applicability-v055-dev.yaml"

COMMON_CHECKS = [
    "qa.functional",
    "qa.integration",
    "qa.security",
    "qa.responsive",
    "qa.accessibility",
    "qa.e2e",
]
STABLE_REQUIRE_ALL = [
    "qa.functional",
    "qa.real_api_transport",
    "qa.integration",
    "qa.security",
    "qa.responsive",
    "qa.accessibility",
    "qa.e2e",
]
OPTIONAL_REQUIRE_ALL = [
    "qa.functional",
    "qa.provider_runtime_transport",
    "qa.integration",
    "qa.security",
    "qa.responsive",
    "qa.accessibility",
    "qa.e2e",
]
REQUIRE_IF = ["qa.idempotency", "qa.offline"]
PREREQUISITE_GATES = ["functional_slice_ready", "visual_functional_review_pass"]


def load(path: Path) -> Any:
    text = path.read_text(encoding="utf-8")
    return json.loads(text) if path.suffix == ".json" else yaml.safe_load(text)


def schema_errors(doc: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    return [
        f"{'/'.join(map(str, e.absolute_path)) or '<root>'}: {e.message}"
        for e in sorted(validator.iter_errors(doc), key=lambda x: list(x.absolute_path))
    ]


def require_valid(label: str, doc: dict[str, Any], schema: dict[str, Any]) -> None:
    found = schema_errors(doc, schema)
    if found:
        raise AssertionError(f"{label} invalid: {' | '.join(found)}")
    print(f"PASS schema: {label}")


def require_invalid(label: str, doc: dict[str, Any], schema: dict[str, Any]) -> None:
    if not schema_errors(doc, schema):
        raise AssertionError(f"negative fixture unexpectedly passed: {label}")
    print(f"PASS negative: {label}")


def run(path: str) -> None:
    result = subprocess.run([sys.executable, path], cwd=ROOT, text=True, capture_output=True)
    if result.returncode != 0:
        raise AssertionError(f"{path} failed:\n{result.stdout}\n{result.stderr}")
    print(f"PASS prerequisite: {path}")


def index_by_id(doc: dict[str, Any], key: str) -> dict[str, dict[str, Any]]:
    items = doc.get(key)
    if not isinstance(items, list):
        raise AssertionError(f"{key} must be a list")
    indexed: dict[str, dict[str, Any]] = {}
    for item in items:
        if not isinstance(item, dict) or not isinstance(item.get("id"), str):
            raise AssertionError(f"every {key} item must have string id")
        indexed[item["id"]] = item
    return indexed


def main() -> int:
    if (ROOT / "DEVELOPMENT_VERSION").read_text(encoding="utf-8").strip() != "0.5.5-dev":
        raise AssertionError("Integration QA authority matrix is valid only inside governed 0.5.5-dev lane")

    for prerequisite in (
        "scripts/validate-development.py",
        "scripts/validate-api-authority-v055-dev.py",
        "scripts/validate-workflow-applicability-v055-dev.py",
        "scripts/validate-client-slice-authority-v055-dev.py",
    ):
        run(prerequisite)

    schema = load(SCHEMA)
    Draft202012Validator.check_schema(schema)
    backed = load(API_BACKED)
    optional = load(API_OPTIONAL)
    require_valid("api-backed Integration QA authority", backed, schema)
    require_valid("api-optional Integration QA authority", optional, schema)

    checks = index_by_id(load(CHECKS), "checks")
    gates = index_by_id(load(GATES), "gates")
    stable_gate = gates["integration_qa_pass"]

    if stable_gate.get("evaluation_scope") != "interface_slice_platform":
        raise AssertionError("stable integration_qa_pass scope drifted")
    if stable_gate.get("require_all") != STABLE_REQUIRE_ALL:
        raise AssertionError("stable integration_qa_pass require_all drifted from 0.5.4")
    if stable_gate.get("require_if_applicable") != REQUIRE_IF:
        raise AssertionError("stable integration_qa_pass conditional checks drifted from 0.5.4")
    if backed["effective_gate"]["require_all"] != stable_gate["require_all"]:
        raise AssertionError("api-backed Integration QA must preserve stable 0.5.4 require_all exactly")
    if backed["effective_gate"]["require_if_applicable"] != stable_gate["require_if_applicable"]:
        raise AssertionError("api-backed Integration QA conditional checks drifted")
    if backed["effective_gate"]["transport_check"] != "qa.real_api_transport":
        raise AssertionError("api-backed Integration QA transport check must remain qa.real_api_transport")
    print("PASS api-backed Integration QA preserves stable 0.5.4 strictness")

    optional_common = [
        item for item in optional["effective_gate"]["require_all"]
        if item != "qa.provider_runtime_transport"
    ]
    stable_common = [
        item for item in stable_gate["require_all"]
        if item != "qa.real_api_transport"
    ]
    if optional_common != stable_common or optional_common != COMMON_CHECKS:
        raise AssertionError("api_optional changed common Integration QA obligations")
    if optional["effective_gate"]["require_if_applicable"] != REQUIRE_IF:
        raise AssertionError("api_optional changed conditional Integration QA obligations")
    if optional["effective_gate"]["prerequisite_gates"] != PREREQUISITE_GATES:
        raise AssertionError("api_optional must preserve functional and human visual-review prerequisites")
    if "qa.real_api_transport" in optional["effective_gate"]["require_all"]:
        raise AssertionError("api_optional cannot require fake real API transport")
    if "qa.provider_runtime_transport" not in optional["effective_gate"]["require_all"]:
        raise AssertionError("api_optional requires provider runtime transport evidence")
    print("PASS api_optional swaps only transport-specific QA while preserving common QA")

    for check_id in STABLE_REQUIRE_ALL + REQUIRE_IF:
        if check_id not in checks:
            raise AssertionError(f"stable Integration QA check disappeared: {check_id}")
    if "qa.provider_runtime_transport" in checks:
        raise AssertionError("development-only provider runtime check leaked into stable 0.5.4 catalog before release closure")
    print("PASS stable 0.5.4 catalog remains unchanged during hardening")

    applicability = load(APPLICABILITY)
    optional_profile = applicability["profiles"]["api_optional"]
    if "integration_qa" in optional_profile["phase_na"]:
        raise AssertionError("api_optional cannot classify Integration QA phase N/A")
    if "integration_qa_pass" in optional_profile["gate_na"]:
        raise AssertionError("api_optional cannot classify Integration QA gate N/A")
    print("PASS Integration QA remains mandatory for api_optional")

    client_backed = load(CLIENT_BACKED)
    client_optional = load(CLIENT_OPTIONAL)
    if client_backed.get("integration_qa_ref") != "templates/integration-qa-authority.api-backed-v055-dev.example.json":
        raise AssertionError("api-backed client slice does not bind the API-backed Integration QA profile")
    if client_optional.get("integration_qa_ref") != "templates/integration-qa-authority.api-optional-v055-dev.example.json":
        raise AssertionError("api-optional client slice does not bind the provider-runtime Integration QA profile")
    if "DEFERRED_TO_INCREMENT_4" in json.dumps(client_backed) + json.dumps(client_optional):
        raise AssertionError("Increment 4 is materialized but a client slice still declares Integration QA deferred")
    print("PASS Client/Slice Authority resolves Increment 4 references")

    if backed["api_authority_mode"] != client_backed["api_authority_mode"]:
        raise AssertionError("api-backed QA profile disagrees with client slice authority")
    if optional["api_authority_mode"] != client_optional["api_authority_mode"]:
        raise AssertionError("api-optional QA profile disagrees with client slice authority")
    if set(backed["transport_contract"]["operation_ids"]) != set(client_backed["client_slice"]["authority_binding"]["operation_ids"]):
        raise AssertionError("api-backed QA operationIds drifted from client slice binding")
    if set(optional["transport_contract"]["contract_refs"]) != set(client_optional["client_slice"]["authority_binding"]["contract_refs"]):
        raise AssertionError("api-optional QA provider contracts drifted from client slice binding")
    print("PASS Integration QA transport evidence binds to slice authority")

    bad = copy.deepcopy(optional)
    bad["transport_contract"]["remote_authority"] = True
    require_invalid("api_optional provider transport cannot claim remote authority", bad, schema)

    bad = copy.deepcopy(optional)
    bad["transport_contract"]["server_security_claims"] = True
    require_invalid("api_optional provider transport cannot claim server security", bad, schema)

    bad = copy.deepcopy(optional)
    bad["effective_gate"]["transport_check"] = "qa.real_api_transport"
    require_invalid("api_optional cannot use real API transport check", bad, schema)

    bad = copy.deepcopy(optional)
    bad["effective_gate"]["require_all"] = [v for v in OPTIONAL_REQUIRE_ALL if v != "qa.security"]
    require_invalid("api_optional cannot drop security QA", bad, schema)

    bad = copy.deepcopy(optional)
    bad["effective_gate"]["prerequisite_gates"] = ["functional_slice_ready"]
    require_invalid("api_optional cannot drop human visual-review prerequisite", bad, schema)

    bad = copy.deepcopy(backed)
    bad["effective_gate"]["transport_check"] = "qa.provider_runtime_transport"
    require_invalid("api_backed cannot replace real API transport", bad, schema)

    bad = copy.deepcopy(backed)
    bad["transport_contract"]["remote_authority"] = False
    require_invalid("api_backed remote authority cannot be weakened", bad, schema)

    bad = copy.deepcopy(backed)
    bad["transport_contract"].pop("openapi_ref")
    require_invalid("api_backed cannot omit OpenAPI transport binding", bad, schema)

    serialized_optional = json.dumps(optional, sort_keys=True).lower()
    if "openapi_ref" in serialized_optional or '"remote_authority": true' in serialized_optional:
        raise AssertionError("api_optional Integration QA example contains fake API authority")
    print("PASS api_optional QA contains no fake OpenAPI or remote-authority material")

    print("Integration QA authority validation PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
