#!/usr/bin/env python3
from __future__ import annotations

import json
import pathlib
import sys
from typing import Any

import yaml
from jsonschema import Draft202012Validator, FormatChecker

ROOT = pathlib.Path(__file__).resolve().parents[1]


def load(path: str) -> Any:
    p = ROOT / path
    text = p.read_text(encoding="utf-8")
    if p.suffix == ".json":
        return json.loads(text)
    if p.suffix in {".yaml", ".yml"}:
        return yaml.safe_load(text)
    raise ValueError(f"Unsupported file type: {path}")


def validate(schema_path: str, instance_path: str) -> None:
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


def assert_unique(values: list[str], label: str) -> None:
    if len(values) != len(set(values)):
        raise AssertionError(f"Duplicate values in {label}: {values}")


def validate_catalog_references() -> None:
    phases = load("catalog/phases.yaml")["phases"]
    checks = load("catalog/checks.yaml")["checks"]
    gates = load("catalog/gates.yaml")["gates"]
    phase_ids = {p["id"] for p in phases}
    check_ids = {c["id"] for c in checks}
    gate_ids = {g["id"] for g in gates}

    assert_unique([p["id"] for p in phases], "phase IDs")
    assert_unique([c["id"] for c in checks], "check IDs")
    assert_unique([g["id"] for g in gates], "gate IDs")

    for check in checks:
        if check["phase"] not in phase_ids:
            raise AssertionError(
                f"Check {check['id']} references unknown phase {check['phase']}"
            )

    for gate in gates:
        if gate["phase"] not in phase_ids:
            raise AssertionError(
                f"Gate {gate['id']} references unknown phase {gate['phase']}"
            )
        for key in ("require_all", "require_if_applicable"):
            for check_id in gate.get(key, []):
                if check_id not in check_ids:
                    raise AssertionError(
                        f"Gate {gate['id']} references unknown check {check_id}"
                    )

    for workflow_path in ("workflows/greenfield.yaml", "workflows/brownfield.yaml"):
        workflow = load(workflow_path)
        for phase in workflow["sequence"]:
            if phase not in phase_ids:
                raise AssertionError(
                    f"{workflow_path} references unknown phase {phase}"
                )
        for gate in workflow.get("gates", {}).values():
            if gate not in gate_ids:
                raise AssertionError(
                    f"{workflow_path} references unknown gate {gate}"
                )


def validate_experience_pair(inventory_path: str, batch_path: str) -> None:
    inventory = load(inventory_path)
    batch = load(batch_path)
    inventory_ids = {item["id"] for item in inventory["items"]}
    views = batch["views"]

    if len(views) > 10:
        raise AssertionError(
            f"{batch_path} exceeds Blueprint batch limit: {len(views)}"
        )

    assert_unique([v["mockup_id"] for v in views], "mockup IDs")
    assert_unique([v["inventory_id"] for v in views], "batch inventory IDs")

    for view in views:
        if view["inventory_id"] not in inventory_ids:
            raise AssertionError(
                f"{view['mockup_id']} references missing inventory ID "
                f"{view['inventory_id']}"
            )

        asset = view.get("visual_asset_path")
        generated = view["generation_status"] == "GENERATED"
        approved = view["review_status"] == "APPROVED"

        if generated:
            if not asset:
                raise AssertionError(
                    f"{view['mockup_id']} is GENERATED without visual_asset_path"
                )
            if not (ROOT / asset).is_file():
                raise AssertionError(
                    f"{view['mockup_id']} asset does not exist: {asset}"
                )

        if approved:
            if not generated:
                raise AssertionError(
                    f"{view['mockup_id']} APPROVED without GENERATED status"
                )
            if view["contract_review_status"] not in {"PASS", "N/A"}:
                raise AssertionError(
                    f"{view['mockup_id']} APPROVED without contract review PASS/N/A"
                )
            if view["accessibility_review_status"] != "PASS":
                raise AssertionError(
                    f"{view['mockup_id']} APPROVED without accessibility PASS"
                )

        for reference in view.get("reference_inputs", []):
            if not (ROOT / reference).is_file():
                raise AssertionError(
                    f"{view['mockup_id']} reference input does not exist: {reference}"
                )


def validate_scoped_gate_examples() -> None:
    status = load("templates/status.example.yaml")
    for gate in status.get("scoped_gates", []):
        if gate["gate"] == "visual_review_pass" and gate["scope"] != "interface_slice":
            raise AssertionError(
                "visual_review_pass must use interface_slice scope"
            )
        if gate["gate"] == "client_architecture_ready":
            if gate["scope"] != "interface_slice_platform" or "platform" not in gate:
                raise AssertionError(
                    "client_architecture_ready must use interface_slice_platform "
                    "scope with platform"
                )


def main() -> int:
    schema_pairs = [
        ("schemas/project.schema.json", "templates/project.example.yaml"),
        ("schemas/status.schema.json", "templates/status.example.yaml"),
        (
            "schemas/interface-inventory.schema.json",
            "templates/interface-inventory.example.json",
        ),
        ("schemas/design-tokens.schema.json", "templates/design-tokens.example.json"),
        ("schemas/design-system.schema.json", "templates/design-system.example.json"),
        ("schemas/mockup-batch.schema.json", "templates/mockup-batch.example.json"),
        ("schemas/evidence.schema.json", "templates/evidence.example.json"),
        ("schemas/reference-pilots.schema.json", "catalog/reference-pilots.yaml"),
        (
            "schemas/interface-inventory.schema.json",
            "tests/fixtures/experience/interface-inventory.json",
        ),
        (
            "schemas/mockup-batch.schema.json",
            "tests/fixtures/experience/mockup-batch.json",
        ),
    ]

    for schema, instance in schema_pairs:
        validate(schema, instance)
        print(f"PASS schema: {instance} -> {schema}")

    validate_catalog_references()
    print("PASS catalog/workflow references")

    validate_experience_pair(
        "tests/fixtures/experience/interface-inventory.json",
        "tests/fixtures/experience/mockup-batch.json",
    )
    print("PASS experience fixture: inventory IDs, <=10 views, approved asset exists")

    validate_scoped_gate_examples()
    print("PASS scoped gate semantics")

    print("Blueprint V4-2 schema/evidence validation: PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise
