#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
STABLE_VERSION = "0.5.2"
DEV_VERSION = "0.5.3-dev"
EXPECTED_COUNTS = {
    "phases": 28,
    "checks": 135,
    "gates": 18,
    "materialized_skills": 14,
    "planned_skills": 25,
}


def fail(message: str) -> None:
    raise AssertionError(message)


def load_yaml(path: str) -> dict:
    value = yaml.safe_load((ROOT / path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        fail(f"{path} must contain a mapping")
    return value


def load_json(path: str) -> dict:
    value = json.loads((ROOT / path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        fail(f"{path} must contain an object")
    return value


def planned_skill_count(catalog: dict) -> int:
    seen: set[str] = set()
    for values in catalog.get("planned_registry", {}).values():
        for skill_id in values:
            if skill_id in seen:
                fail(f"planned skill duplicated: {skill_id}")
            seen.add(skill_id)
    return len(seen)


def catalog_counts() -> dict[str, int]:
    return {
        "phases": len(load_yaml("catalog/phases.yaml").get("phases", [])),
        "checks": len(load_yaml("catalog/checks.yaml").get("checks", [])),
        "gates": len(load_yaml("catalog/gates.yaml").get("gates", [])),
        "materialized_skills": len(load_yaml("catalog/skills.yaml").get("registry", {})),
        "planned_skills": planned_skill_count(load_yaml("catalog/skills.yaml")),
    }


def validate_stable_baseline_preserved() -> None:
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    if version != STABLE_VERSION:
        fail(f"0.5.3-dev hardening must keep root VERSION={STABLE_VERSION}, got {version}")

    release = load_json("documentation/BLUEPRINT_V0_5_2_RELEASE.json")
    if release.get("version") != STABLE_VERSION or release.get("status") != "stable" or release.get("tag") != "v0.5.2":
        fail("stable 0.5.2 release manifest drifted during 0.5.3-dev hardening")

    project = load_yaml("templates/project.example.yaml")
    status = load_yaml("templates/status.example.yaml")
    if project.get("blueprint", {}).get("version") != STABLE_VERSION:
        fail("consumer project template must remain stable 0.5.2 during hardening")
    if status.get("blueprint_version") != STABLE_VERSION:
        fail("consumer status template must remain stable 0.5.2 during hardening")

    counts = catalog_counts()
    if counts != EXPECTED_COUNTS:
        fail(f"0.5.3-dev must not alter core counts: {counts}")


def validate_development_identity() -> None:
    schema = load_json("schemas/ci-runtime.schema.json")
    if "/blueprint/0.5.3-dev/" not in schema.get("$id", ""):
        fail("ci-runtime schema must use 0.5.3-dev $id")
    if schema.get("properties", {}).get("schema_version", {}).get("const") != DEV_VERSION:
        fail("ci-runtime schema_version must be 0.5.3-dev")

    template = load_yaml("templates/ci-runtime.example.yaml")
    master = load_yaml("ci/blueprint-master.runtime.yaml")
    if template.get("schema_version") != DEV_VERSION or master.get("schema_version") != DEV_VERSION:
        fail("0.5.3-dev runtime profiles must declare development identity")

    policy = (ROOT / "documentation" / "BLUEPRINT_V0_5_3_EPHEMERAL_CI_SERVICES.md").read_text(encoding="utf-8")
    for token in (
        "runner != service instance",
        "shared image cache != shared mutable runtime",
        "host port allocation = dynamic",
        "mysql:8.4",
        "postgres:16",
        "redis:8.10.1",
        "consumer auto-upgrade",
    ):
        if token not in policy:
            fail(f"0.5.3-dev policy documentation missing token: {token}")


def run_ci_runtime_validator() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/validate-ci-runtime.py"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    print(result.stdout, end="")
    if result.returncode != 0:
        fail("0.5.3-dev CI runtime validator failed")


def main() -> int:
    validate_stable_baseline_preserved()
    print("PASS stable 0.5.2 baseline preserved")
    validate_development_identity()
    print("PASS 0.5.3-dev boundary identity")
    run_ci_runtime_validator()
    print(f"PASS Blueprint {DEV_VERSION} hardening boundary with stable VERSION={STABLE_VERSION}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
