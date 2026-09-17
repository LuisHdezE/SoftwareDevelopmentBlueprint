#!/usr/bin/env python3
from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import json
import yaml
from jsonschema import Draft202012Validator, ValidationError

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "ci-runtime.schema.json"
TEMPLATE_PATH = ROOT / "templates" / "ci-runtime.example.yaml"
MASTER_PROFILE_PATH = ROOT / "ci" / "blueprint-master.runtime.yaml"
COMPONENT_VERSION = "0.5.2"
SUPPORTED_ROOT_VERSIONS = {"0.5.2", "0.5.3"}


def fail(message: str) -> None:
    raise AssertionError(message)


def load_schema() -> dict:
    value = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        fail("ci-runtime schema must contain an object")
    Draft202012Validator.check_schema(value)
    return value


def load_yaml(path: Path) -> dict:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        fail(f"{path.relative_to(ROOT)} must contain a mapping")
    return value


def expect_invalid(validator: Draft202012Validator, candidate: dict, label: str) -> None:
    try:
        validator.validate(candidate)
    except ValidationError:
        return
    fail(f"negative fixture unexpectedly validated: {label}")


def validate_common_semantics(document: dict, label: str) -> None:
    if document.get("schema_version") != COMPONENT_VERSION:
        fail(f"{label} must declare CI runtime component {COMPONENT_VERSION}")
    if document.get("orchestrator") != "github_actions":
        fail(f"{label} must use GitHub Actions orchestration")
    if document.get("strategy") not in {"self_hosted", "hybrid", "github_hosted"}:
        fail(f"{label} has unknown CI strategy")
    runner = document["runner"]
    if runner.get("project_docker_capability_independent") is not True:
        fail(f"{label}: runner container infrastructure must remain independent from project Docker capability")
    if document["strategy"] in {"self_hosted", "hybrid"}:
        labels = set(runner.get("labels", []))
        for required in ("self-hosted", "blueprint"):
            if required not in labels:
                fail(f"{label}: self-hosted strategy missing runner label {required}")
        security = document["security"]
        if security.get("trusted_code_only") is not True:
            fail(f"{label}: self-hosted runner must execute trusted code only")
        if security.get("persistent_secrets") is not False:
            fail(f"{label}: self-hosted runner must not persist repository secrets")
        if security.get("least_privilege_permissions") is not True:
            fail(f"{label}: workflow token permissions must remain least privilege")
    evidence = document["evidence"]
    for key in ("exact_head_required", "check_run_required", "pre_execution_infrastructure_failures_distinct_from_test_failures"):
        if evidence.get(key) is not True:
            fail(f"{label}: CI runtime evidence invariant drifted: {key}")
    if document["maintenance"].get("workspace_cleanup") is not True:
        fail(f"{label}: persistent CI runtime requires workspace cleanup")


def validate_profiles(template: dict, master: dict) -> None:
    if template.get("strategy") != "self_hosted":
        fail("canonical CI runtime example must exercise self_hosted strategy")
    labels = set(template["runner"].get("labels", []))
    for required in ("self-hosted", "linux", "x64", "blueprint"):
        if required not in labels:
            fail(f"canonical example missing runner label: {required}")
    if template["runner"].get("service_containers") is not True or template["runner"].get("container_engine") != "docker":
        fail("service-container example must use Docker Engine")
    if master.get("strategy") != "self_hosted":
        fail("Blueprint Master profile must use self_hosted strategy")
    if master["runner"].get("service_containers") is not False or master["runner"].get("container_engine") != "none":
        fail("Blueprint Master core validators must not require Docker")


def validate_negative_guards(validator: Draft202012Validator, template: dict) -> None:
    candidate = deepcopy(template); candidate["runner"]["labels"].remove("self-hosted")
    expect_invalid(validator, candidate, "self-hosted label required")
    candidate = deepcopy(template); candidate["security"]["trusted_code_only"] = False
    expect_invalid(validator, candidate, "trusted code required")
    candidate = deepcopy(template); candidate["security"]["persistent_secrets"] = True
    expect_invalid(validator, candidate, "persistent secrets forbidden")
    candidate = deepcopy(template); candidate["runner"]["container_engine"] = "none"
    expect_invalid(validator, candidate, "service containers require Docker")
    candidate = deepcopy(template); candidate["evidence"]["exact_head_required"] = False
    expect_invalid(validator, candidate, "exact-head evidence cannot be disabled")
    candidate = deepcopy(template); candidate["runner"]["project_docker_capability_independent"] = False
    expect_invalid(validator, candidate, "runner Docker independent from project capability")


def main() -> int:
    root_version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    if root_version not in SUPPORTED_ROOT_VERSIONS:
        fail(f"CI runtime component {COMPONENT_VERSION} unsupported by root VERSION={root_version}")
    schema = load_schema()
    template = load_yaml(TEMPLATE_PATH)
    master = load_yaml(MASTER_PROFILE_PATH)
    validator = Draft202012Validator(schema)
    validator.validate(template)
    validator.validate(master)
    validate_common_semantics(template, "canonical template")
    validate_common_semantics(master, "Blueprint Master profile")
    validate_profiles(template, master)
    validate_negative_guards(validator, template)
    print(f"PASS CI runtime component {COMPONENT_VERSION} under Blueprint root {root_version}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"FAIL: {exc}")
        raise SystemExit(1)
