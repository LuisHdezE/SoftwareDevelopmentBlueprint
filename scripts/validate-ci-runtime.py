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
DEV_VERSION = "0.5.3-dev"

CANONICAL_SERVICES = {
    "mysql": {"image": "mysql:8.4", "container_port": 3306},
    "postgresql": {"image": "postgres:16", "container_port": 5432},
    "redis": {"image": "redis:8.10.1", "container_port": 6379},
}


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
    if document.get("schema_version") != DEV_VERSION:
        fail(f"{label} must declare {DEV_VERSION}")
    if document.get("orchestrator") != "github_actions":
        fail(f"{label} must use GitHub Actions orchestration in {DEV_VERSION}")
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
    for key in (
        "exact_head_required",
        "check_run_required",
        "pre_execution_infrastructure_failures_distinct_from_test_failures",
    ):
        if evidence.get(key) is not True:
            fail(f"{label}: CI runtime evidence invariant drifted: {key}")

    if document["maintenance"].get("workspace_cleanup") is not True:
        fail(f"{label}: persistent CI runtime requires workspace cleanup")


def validate_service_policy(document: dict, label: str) -> None:
    runner = document["runner"]
    services = document.get("services")

    if runner.get("service_containers") is False:
        if services is not None:
            fail(f"{label}: services must be absent when service_containers=false")
        return

    if not isinstance(services, dict):
        fail(f"{label}: service_containers=true requires services policy")

    expected = {
        "isolation": "per_job",
        "lifecycle": "ephemeral",
        "host_port_policy": "dynamic",
        "runtime_port_discovery": "github_actions_service_context",
        "shared_image_cache": True,
        "shared_runtime_instances": False,
        "healthcheck_required": True,
    }
    for key, value in expected.items():
        if services.get(key) != value:
            fail(f"{label}: service policy drifted: {key}")

    catalog = services.get("catalog")
    if not isinstance(catalog, dict) or not catalog:
        fail(f"{label}: service catalog must not be empty")

    for service_id, definition in catalog.items():
        image = str(definition.get("image", ""))
        if image.endswith(":latest"):
            fail(f"{label}: floating latest tag forbidden for {service_id}")


def validate_development_profiles(template: dict, master: dict) -> None:
    if template.get("strategy") != "self_hosted":
        fail("canonical development example must exercise self_hosted strategy")
    labels = set(template["runner"].get("labels", []))
    for required in ("self-hosted", "linux", "x64", "blueprint"):
        if required not in labels:
            fail(f"canonical development example missing runner label: {required}")
    if template["runner"].get("service_containers") is not True:
        fail("canonical development example must exercise service-container support")
    if template["runner"].get("container_engine") != "docker":
        fail("service-container example must use Docker Engine")

    catalog = template["services"]["catalog"]
    if catalog != CANONICAL_SERVICES:
        fail(f"canonical development service catalog drifted: {catalog}")

    if master.get("strategy") != "self_hosted":
        fail("Blueprint Master development profile must use self_hosted strategy")
    if master["runner"].get("service_containers") is not False:
        fail("Blueprint Master validator profile does not require service containers")
    if master["runner"].get("container_engine") != "none":
        fail("Blueprint Master profile must not require Docker for core validators")
    if "services" in master:
        fail("Blueprint Master profile must not declare service policy when service containers are disabled")


def validate_negative_guards(validator: Draft202012Validator, template: dict) -> None:
    candidate = deepcopy(template)
    candidate["runner"]["labels"].remove("self-hosted")
    expect_invalid(validator, candidate, "self-hosted label required")

    candidate = deepcopy(template)
    candidate["security"]["trusted_code_only"] = False
    expect_invalid(validator, candidate, "trusted code required")

    candidate = deepcopy(template)
    candidate["security"]["persistent_secrets"] = True
    expect_invalid(validator, candidate, "persistent secrets forbidden")

    candidate = deepcopy(template)
    candidate["runner"]["container_engine"] = "none"
    expect_invalid(validator, candidate, "service containers require Docker")

    candidate = deepcopy(template)
    candidate.pop("services")
    expect_invalid(validator, candidate, "service containers require service policy")

    candidate = deepcopy(template)
    candidate["services"]["host_port_policy"] = "static"
    expect_invalid(validator, candidate, "static host ports forbidden")

    candidate = deepcopy(template)
    candidate["services"]["shared_runtime_instances"] = True
    expect_invalid(validator, candidate, "shared runtime service instances forbidden")

    candidate = deepcopy(template)
    candidate["services"]["catalog"]["redis"]["image"] = "redis:latest"
    expect_invalid(validator, candidate, "floating latest service image forbidden")

    candidate = deepcopy(template)
    candidate["services"]["catalog"]["redis"]["container_port"] = 6380
    expect_invalid(validator, candidate, "canonical Redis container port required")

    candidate = deepcopy(template)
    candidate["evidence"]["exact_head_required"] = False
    expect_invalid(validator, candidate, "exact-head evidence cannot be disabled")

    candidate = deepcopy(template)
    candidate["runner"]["project_docker_capability_independent"] = False
    expect_invalid(validator, candidate, "runner Docker must remain independent from project capability")


def main() -> int:
    schema = load_schema()
    template = load_yaml(TEMPLATE_PATH)
    master = load_yaml(MASTER_PROFILE_PATH)
    validator = Draft202012Validator(schema)

    validator.validate(template)
    validator.validate(master)
    validate_common_semantics(template, "canonical template")
    validate_common_semantics(master, "Blueprint Master profile")
    validate_service_policy(template, "canonical template")
    validate_service_policy(master, "Blueprint Master profile")
    validate_development_profiles(template, master)
    validate_negative_guards(validator, template)

    print("PASS Blueprint 0.5.3-dev ephemeral CI service contract")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"FAIL: {exc}")
        raise SystemExit(1)
