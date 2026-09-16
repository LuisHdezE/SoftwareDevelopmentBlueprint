#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
STABLE_VERSION = "0.5.3"
DEVELOPMENT_VERSION = "0.5.4-dev"


def fail(message: str) -> None:
    raise AssertionError(message)


def load_json(path: str) -> dict:
    value = json.loads((ROOT / path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        fail(f"{path} must contain an object")
    return value


def load_yaml(path: str) -> dict:
    value = yaml.safe_load((ROOT / path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        fail(f"{path} must contain a mapping")
    return value


def assert_valid(validator: Draft202012Validator, value: dict, label: str) -> None:
    errors = list(validator.iter_errors(value))
    if errors:
        fail(f"expected valid platform capability case to pass: {label}: " + "; ".join(e.message for e in errors))
    print(f"PASS positive platform capability case: {label}")


def expect_invalid(validator: Draft202012Validator, value: dict, label: str) -> None:
    if not list(validator.iter_errors(value)):
        fail(f"expected invalid platform capability case to fail: {label}")
    print(f"PASS negative platform capability case: {label}")


def validate_identity(schema: dict, template: dict) -> None:
    stable = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    development = (ROOT / "DEVELOPMENT_VERSION").read_text(encoding="utf-8").strip()
    if stable != STABLE_VERSION:
        fail(f"platform capability hardening must preserve VERSION={STABLE_VERSION}")
    if development != DEVELOPMENT_VERSION:
        fail(f"platform capability hardening requires DEVELOPMENT_VERSION={DEVELOPMENT_VERSION}")
    if f"/blueprint/{DEVELOPMENT_VERSION}/" not in schema.get("$id", ""):
        fail("project schema must use 0.5.4-dev provenance during hardening")
    project_version = schema.get("properties", {}).get("blueprint", {}).get("properties", {}).get("version", {}).get("const")
    if project_version != DEVELOPMENT_VERSION:
        fail("project schema blueprint.version must be const 0.5.4-dev during hardening")
    if template.get("blueprint", {}).get("version") != DEVELOPMENT_VERSION:
        fail("project template must target 0.5.4-dev during hardening")
    if "ios" not in template.get("capabilities", {}):
        fail("0.5.4-dev project template must explicitly declare ios capability")
    if template.get("mobile", {}).get("strategy") not in {"native", "cross_platform"}:
        fail("0.5.4-dev project template must explicitly declare mobile.strategy")
    if not isinstance(template.get("stack", {}).get("mobile"), (str, type(None))):
        fail("stack.mobile must remain the legacy scalar technology declaration")
    print("PASS 0.5.4-dev project contract identity and explicit mobile strategy")


def validate_matrix(validator: Draft202012Validator, template: dict) -> None:
    assert_valid(validator, template, "default Android-native template")

    migrated = copy.deepcopy(template)
    migrated["capabilities"].pop("ios", None)
    assert_valid(validator, migrated, "migrated manifest may omit ios and remain not-enabled")

    ios_only = copy.deepcopy(template)
    ios_only["capabilities"]["android"] = False
    ios_only["capabilities"]["ios"] = True
    ios_only["capabilities"].pop("mobile_licensing", None)
    ios_only["stack"]["mobile"] = "swift"
    assert_valid(validator, ios_only, "iOS-only native without Android licensing decision")

    both_native = copy.deepcopy(template)
    both_native["capabilities"]["ios"] = True
    assert_valid(validator, both_native, "Android+iOS native")

    cross_android = copy.deepcopy(template)
    cross_android["mobile"]["strategy"] = "cross_platform"
    assert_valid(validator, cross_android, "cross-platform strategy with Android target only")
    if cross_android["capabilities"]["ios"] is not False:
        fail("cross_platform must not auto-enable iOS")

    cross_ios = copy.deepcopy(ios_only)
    cross_ios["mobile"]["strategy"] = "cross_platform"
    assert_valid(validator, cross_ios, "cross-platform strategy with iOS target only")
    if cross_ios["capabilities"]["android"] is not False:
        fail("cross_platform must not auto-enable Android")

    cross_both = copy.deepcopy(template)
    cross_both["capabilities"]["ios"] = True
    cross_both["mobile"]["strategy"] = "cross_platform"
    assert_valid(validator, cross_both, "cross-platform strategy with Android+iOS")

    web_only = copy.deepcopy(template)
    web_only["capabilities"]["android"] = False
    web_only["capabilities"]["ios"] = False
    web_only["capabilities"]["offline_mobile"] = False
    web_only["capabilities"].pop("mobile_licensing", None)
    web_only.pop("mobile", None)
    web_only["stack"]["mobile"] = None
    assert_valid(validator, web_only, "web-only project without mobile strategy")

    ios_offline = copy.deepcopy(ios_only)
    ios_offline["capabilities"]["offline_mobile"] = True
    assert_valid(validator, ios_offline, "API-backed offline iOS with OpenAPI path")

    android_missing_strategy = copy.deepcopy(template)
    android_missing_strategy.pop("mobile", None)
    expect_invalid(validator, android_missing_strategy, "Android enabled without mobile.strategy")

    ios_missing_strategy = copy.deepcopy(ios_only)
    ios_missing_strategy.pop("mobile", None)
    expect_invalid(validator, ios_missing_strategy, "iOS enabled without mobile.strategy")

    invalid_strategy = copy.deepcopy(template)
    invalid_strategy["mobile"]["strategy"] = "hybrid_magic"
    expect_invalid(validator, invalid_strategy, "unsupported mobile strategy")

    meaningless_mobile = copy.deepcopy(web_only)
    meaningless_mobile["mobile"] = {"strategy": "native"}
    expect_invalid(validator, meaningless_mobile, "mobile strategy without any mobile target")

    offline_without_target = copy.deepcopy(web_only)
    offline_without_target["capabilities"]["offline_mobile"] = True
    expect_invalid(validator, offline_without_target, "offline_mobile without Android or iOS")

    offline_without_openapi = copy.deepcopy(ios_offline)
    offline_without_openapi["artifact_locations"].pop("openapi", None)
    expect_invalid(validator, offline_without_openapi, "offline_mobile without OpenAPI path")

    strategy_hidden_in_stack = copy.deepcopy(template)
    strategy_hidden_in_stack["stack"]["mobile"] = {"strategy": "native"}
    expect_invalid(validator, strategy_hidden_in_stack, "strategy object hidden inside stack.mobile")

    android_without_licensing_decision = copy.deepcopy(template)
    android_without_licensing_decision["capabilities"].pop("mobile_licensing", None)
    expect_invalid(validator, android_without_licensing_decision, "Android omitted existing licensing decision")


def main() -> int:
    schema = load_json("schemas/project.schema.json")
    Draft202012Validator.check_schema(schema)
    template = load_yaml("templates/project.example.yaml")
    validator = Draft202012Validator(schema)
    validate_identity(schema, template)
    validate_matrix(validator, template)
    print("PASS Blueprint 0.5.4-dev platform capability model")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"FAIL: {exc}")
        raise SystemExit(1)
