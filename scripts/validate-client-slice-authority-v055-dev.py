#!/usr/bin/env python3
"""Validate Blueprint 0.5.5-dev client/slice authority overlay."""
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
SCHEMA = ROOT / "schemas/client-slice-authority-v055-dev.schema.json"
API_BACKED = ROOT / "templates/client-slice-authority.api-backed-v055-dev.example.json"
API_OPTIONAL = ROOT / "templates/client-slice-authority.api-optional-v055-dev.example.json"
PROJECT_BACKED = ROOT / "templates/project-v055-dev.api-backed.example.yaml"
PROJECT_OPTIONAL = ROOT / "templates/project-v055-dev.api-optional.example.yaml"
STABLE_BASELINE = ROOT / "templates/client-platform-architecture.web.example.json"
STABLE_BINDING = ROOT / "templates/client-architecture.web.example.json"
STABLE_SLICE = ROOT / "templates/functional-interface-slice.example.json"
INVENTORY_SCHEMA = ROOT / "schemas/interface-inventory.schema.json"


def load(path: Path) -> Any:
    text = path.read_text(encoding="utf-8")
    return json.loads(text) if path.suffix == ".json" else yaml.safe_load(text)


def errors(doc: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    return [f"{'/'.join(map(str, e.absolute_path)) or '<root>'}: {e.message}" for e in sorted(validator.iter_errors(doc), key=lambda x: list(x.absolute_path))]


def require_valid(label: str, doc: dict[str, Any], schema: dict[str, Any]) -> None:
    found = errors(doc, schema)
    if found:
        raise AssertionError(f"{label} invalid: {' | '.join(found)}")
    print(f"PASS schema: {label}")


def require_invalid(label: str, doc: dict[str, Any], schema: dict[str, Any]) -> None:
    if not errors(doc, schema):
        raise AssertionError(f"negative fixture unexpectedly passed: {label}")
    print(f"PASS negative: {label}")


def run(path: str) -> None:
    result = subprocess.run([sys.executable, path], cwd=ROOT, text=True, capture_output=True)
    if result.returncode != 0:
        raise AssertionError(f"{path} failed:\n{result.stdout}\n{result.stderr}")
    print(f"PASS prerequisite: {path}")


def main() -> int:
    if (ROOT / "DEVELOPMENT_VERSION").read_text(encoding="utf-8").strip() != "0.5.5-dev":
        raise AssertionError("client/slice authority overlay is valid only inside governed 0.5.5-dev lane")

    for prerequisite in (
        "scripts/validate-development.py",
        "scripts/validate-api-authority-v055-dev.py",
        "scripts/validate-workflow-applicability-v055-dev.py",
        "scripts/validate-client-architecture.py",
    ):
        run(prerequisite)

    schema = load(SCHEMA)
    Draft202012Validator.check_schema(schema)
    backed = load(API_BACKED)
    optional = load(API_OPTIONAL)
    require_valid("api-backed overlay", backed, schema)
    require_valid("api-optional overlay", optional, schema)

    project_backed = load(PROJECT_BACKED)
    project_optional = load(PROJECT_OPTIONAL)
    if project_backed["authority"]["api"]["mode"] != backed["api_authority_mode"]:
        raise AssertionError("api-backed overlay disagrees with project authority declaration")
    if project_optional["authority"]["api"]["mode"] != optional["api_authority_mode"]:
        raise AssertionError("api-optional overlay disagrees with project authority declaration")

    # API-backed projection must remain anchored exactly to the strict 0.5.4 client artifacts.
    stable_baseline = load(STABLE_BASELINE)
    stable_binding = load(STABLE_BINDING)
    stable_slice = load(STABLE_SLICE)
    backed_platform = backed["client_platform"]
    backed_slice = backed["client_slice"]
    backed_api = backed_slice["authority_binding"]
    stable_api = stable_binding["api_binding"]

    if backed_platform["baseline_ref"] != "templates/client-platform-architecture.web.example.json":
        raise AssertionError("api-backed platform baseline ref drifted from stable Web baseline")
    if backed_platform["authority_binding"]["openapi_ref"] != stable_baseline["api_client"]["openapi_path"]:
        raise AssertionError("api-backed platform overlay drifted from stable OpenAPI baseline")
    if backed_slice["architecture_ref"] != "templates/client-architecture.web.example.json":
        raise AssertionError("api-backed architecture ref drifted from stable Web binding")
    if backed_slice["functional_slice_ref"] != "templates/functional-interface-slice.example.json":
        raise AssertionError("api-backed functional slice ref drifted from stable example")
    if set(backed_slice["inventory_ids"]) != set(stable_binding["inventory_ids"]):
        raise AssertionError("api-backed inventory IDs drifted from stable client binding")
    if set(backed_slice["inventory_ids"]) != set(stable_slice["inventory_ids"]):
        raise AssertionError("api-backed inventory IDs drifted from stable functional slice")
    if backed_api["openapi_ref"] != stable_api["openapi_path"]:
        raise AssertionError("api-backed slice overlay drifted from stable OpenAPI binding")
    if backed_api["revision"] != stable_api["revision"]:
        raise AssertionError("api-backed slice API revision drifted from stable client binding")
    if set(backed_api["operation_ids"]) != set(stable_api["operation_ids"]):
        raise AssertionError("api-backed slice operation IDs drifted from stable client binding")
    if set(backed_api["operation_ids"]) != set(stable_slice["api_binding"]["operation_ids"]):
        raise AssertionError("api-backed slice operation IDs drifted from stable functional slice")
    if set(backed_api["permissions"]) != set(stable_api["permissions"]):
        raise AssertionError("api-backed slice permissions drifted from stable client binding")
    if stable_baseline["permissions"]["source"] != "api_contract" or stable_baseline["permissions"]["api_remains_authoritative"] is not True:
        raise AssertionError("stable api-backed permission authority weakened")
    if stable_binding["implementation_guardrails"]["api_authoritative"] is not True:
        raise AssertionError("stable api-backed slice authority weakened")
    print("PASS api-backed 0.5.4 strictness projection")

    # The stable Interface Inventory already represents local/static data without operationIds.
    inventory_schema = load(INVENTORY_SCHEMA)
    local_inventory = {
        "schema_version": "0.5.4",
        "project": "frontend-catalog",
        "mode": "greenfield",
        "maturity": "SCOPE_BASELINE",
        "items": [{
            "id": "WEB-001", "platform": "web", "module": "authentication", "name": "Sign In",
            "purpose": "Provider-driven sign-in demonstration surface.", "source_classification": "OBSERVED",
            "roles": [], "permissions": [],
            "data": [{"name": "Sign-in content", "source": "static", "authoritative": False}],
            "actions": [{"name": "Submit", "kind": "local", "source_classification": "OBSERVED"}],
            "states": ["default", "loading", "success", "error"],
            "navigation": {"route": "/authentication/sign-in", "entry_points": [], "destinations": []},
            "requirements": []
        }]
    }
    require_valid("API-optional interface inventory shape", local_inventory, inventory_schema)

    # Fail closed: api_optional cannot smuggle API/server authority back in.
    bad = copy.deepcopy(optional); bad["client_platform"]["authority_binding"]["remote_authority"] = True
    require_invalid("api_optional remote authority claim", bad, schema)
    bad = copy.deepcopy(optional); bad["client_platform"]["authority_binding"]["server_authorization"] = True
    require_invalid("api_optional server authorization claim", bad, schema)
    bad = copy.deepcopy(optional); bad["client_slice"]["authority_binding"]["server_permissions"] = True
    require_invalid("api_optional server permission claim", bad, schema)
    bad = copy.deepcopy(optional); bad["definition_of_done"]["real_api"] = "PASS"
    require_invalid("api_optional fake real API PASS", bad, schema)
    bad = copy.deepcopy(optional); bad["client_platform"]["authority_binding"] = copy.deepcopy(backed["client_platform"]["authority_binding"])
    require_invalid("api_optional cannot use api client binding", bad, schema)
    bad = copy.deepcopy(backed); bad["client_slice"]["authority_binding"] = copy.deepcopy(optional["client_slice"]["authority_binding"])
    require_invalid("api_backed cannot use provider slice binding", bad, schema)
    bad = copy.deepcopy(backed); bad["definition_of_done"]["real_api"] = "N/A"
    require_invalid("api_backed cannot mark real API N/A", bad, schema)

    # Optional overlay must contain no OpenAPI/API-authoritative binding keys.
    serialized = json.dumps(optional, sort_keys=True).lower()
    if "openapi_ref" in serialized or '"api_authoritative": true' in serialized:
        raise AssertionError("api_optional example contains fake API authority material")
    print("PASS api-optional has no fake OpenAPI or API-authoritative binding")

    print("Client/slice authority validation PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
