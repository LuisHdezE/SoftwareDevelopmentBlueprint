#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path

import jsonschema
import yaml

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "architecture-conformance.schema.json"
EXAMPLE_PATH = ROOT / "templates" / "architecture-conformance.example.json"
CHECKS_PATH = ROOT / "catalog" / "checks.yaml"
GATES_PATH = ROOT / "catalog" / "gates.yaml"
SKILLS_PATH = ROOT / "catalog" / "skills.yaml"
WORKFLOW_PATHS = [ROOT / "workflows" / "greenfield.yaml", ROOT / "workflows" / "brownfield.yaml"]

DEV_VERSION = "0.5.1-dev"
REQUIRED_CHECKS = {
    "architecture.implementation_constraints": ("architecture_security_data", "REQUIRED"),
    "architecture.implementation_conformance": ("api_implementation", "REQUIRED"),
    "architecture.conformance_guard": ("api_implementation", "REQUIRED"),
}


def fail(message: str) -> None:
    raise AssertionError(message)


def load_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        fail(f"{path} must contain a JSON object")
    return value


def load_yaml(path: Path) -> dict:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        fail(f"{path} must contain a YAML mapping")
    return value


def validate_semantics(document: dict) -> None:
    constraint_ids: set[str] = set()
    required_failures: list[str] = []
    for constraint in document.get("constraints", []):
        cid = constraint["id"]
        if cid in constraint_ids:
            fail(f"duplicate architecture constraint id: {cid}")
        constraint_ids.add(cid)
        if constraint.get("required") is True and constraint.get("status") != "PASS":
            required_failures.append(cid)

    guard_ids: set[str] = set()
    required_ci_guards = []
    for guard in document.get("guards", []):
        gid = guard["id"]
        if gid in guard_ids:
            fail(f"duplicate architecture guard id: {gid}")
        guard_ids.add(gid)
        if guard.get("required_in_ci") is True:
            required_ci_guards.append(guard)

    violation_ids: set[str] = set()
    for violation in document.get("violations", []):
        vid = violation["id"]
        if vid in violation_ids:
            fail(f"duplicate architecture violation id: {vid}")
        violation_ids.add(vid)
        if violation["constraint_id"] not in constraint_ids:
            fail(
                f"violation {vid} references unknown constraint "
                f"{violation['constraint_id']}"
            )

    if document.get("decision") == "PASS":
        if required_failures:
            fail(f"PASS cannot contain non-passing required constraints: {required_failures}")
        if document.get("violations"):
            fail("PASS requires zero unresolved architecture violations")
        if not required_ci_guards:
            fail("PASS requires at least one architecture guard with required_in_ci=true")
        failed_ci = [g["id"] for g in required_ci_guards if g.get("status") != "PASS"]
        if failed_ci:
            fail(f"PASS requires every required-in-CI guard to pass: {failed_ci}")
        missing_commands = [g["id"] for g in required_ci_guards if not g.get("command")]
        if missing_commands:
            fail(f"PASS requires executable commands for required-in-CI guards: {missing_commands}")


def repository_path(project_root: Path, reference: str) -> Path | None:
    if "://" in reference:
        return None
    clean = reference.split("#", 1)[0].strip()
    if not clean:
        return None
    candidate = (project_root / clean).resolve()
    try:
        candidate.relative_to(project_root.resolve())
    except ValueError:
        fail(f"repository reference escapes project root: {reference}")
    return candidate


def validate_consumer_references(document: dict, project_root: Path) -> None:
    for reference in document.get("approved_architecture_refs", []):
        path = repository_path(project_root, reference)
        if path is None or not path.exists():
            fail(f"approved architecture reference does not resolve in project repository: {reference}")

    for constraint in document.get("constraints", []):
        source_ref = constraint.get("source_ref")
        if source_ref:
            path = repository_path(project_root, source_ref)
            if path is None or not path.exists():
                fail(f"constraint {constraint['id']} source_ref does not resolve: {source_ref}")

    for guard in document.get("guards", []):
        path = repository_path(project_root, guard["artifact"])
        if path is None or not path.exists():
            fail(f"architecture guard artifact does not resolve: {guard['id']} -> {guard['artifact']}")


def validate_consumer_artifact(
    artifact_path: Path,
    project_root: Path,
    expected_revision: str | None,
) -> None:
    schema = load_json(SCHEMA_PATH)
    document = load_json(artifact_path)
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(document, schema)
    validate_semantics(document)
    validate_consumer_references(document, project_root)
    if expected_revision and document["implementation_revision"].lower() != expected_revision.lower():
        fail(
            "architecture conformance implementation_revision does not match expected exact revision: "
            f"artifact={document['implementation_revision']} expected={expected_revision}"
        )
    print(
        "Blueprint architecture conformance consumer artifact: PASS "
        f"({artifact_path}; revision={document['implementation_revision']})"
    )


def expect_semantic_failure(document: dict, label: str) -> None:
    try:
        validate_semantics(document)
    except AssertionError:
        print(f"PASS negative semantic guard: {label}")
        return
    fail(f"negative architecture conformance semantic guard did not fail: {label}")


def expect_schema_failure(document: dict, schema: dict, label: str) -> None:
    try:
        jsonschema.validate(document, schema)
    except jsonschema.ValidationError:
        print(f"PASS negative schema guard: {label}")
        return
    fail(f"negative architecture conformance schema guard did not fail: {label}")


def validate_catalog_and_gates() -> None:
    checks_doc = load_yaml(CHECKS_PATH)
    gates_doc = load_yaml(GATES_PATH)
    if checks_doc.get("version") != DEV_VERSION or gates_doc.get("version") != DEV_VERSION:
        fail("architecture conformance development catalogs must declare 0.5.1-dev")

    checks = {item["id"]: item for item in checks_doc.get("checks", [])}
    for check_id, (phase, check_type) in REQUIRED_CHECKS.items():
        check = checks.get(check_id)
        if not check:
            fail(f"missing canonical architecture conformance check: {check_id}")
        if check.get("phase") != phase or check.get("type") != check_type:
            fail(f"{check_id} phase/type drifted")

    if checks["architecture.conformance_guard"].get("verification") != "automatic":
        fail("architecture.conformance_guard must be automatically verified")

    gates = {item["id"]: item for item in gates_doc.get("gates", [])}
    architecture_required = set(gates["architecture_ready"].get("require_all", []))
    if "architecture.implementation_constraints" not in architecture_required:
        fail("architecture_ready must require architecture.implementation_constraints")

    implemented_required = set(gates["api_implemented"].get("require_all", []))
    for check_id in ("architecture.implementation_conformance", "architecture.conformance_guard"):
        if check_id not in implemented_required:
            fail(f"api_implemented must require {check_id}")

    api_gate_required = set(gates["api_gate"].get("require_all", []))
    for check_id in REQUIRED_CHECKS:
        if check_id not in api_gate_required:
            fail(f"api_gate must require {check_id}")

    print("PASS architecture conformance catalog/gate wiring")


def validate_workflows() -> None:
    required_rules = {
        "architecture_ready_must_define_verifiable_implementation_constraints",
        "api_implemented_requires_architecture_implementation_conformance",
        "api_implemented_requires_ci_enforced_architecture_conformance_guard",
        "functional_correctness_does_not_substitute_architecture_conformance",
        "api_gate_must_revalidate_architecture_conformance_on_reviewed_revision",
    }
    for path in WORKFLOW_PATHS:
        workflow = load_yaml(path)
        if workflow.get("version") != DEV_VERSION:
            fail(f"{path.name} must declare 0.5.1-dev")
        policy = workflow.get("architecture_implementation_conformance", {})
        if policy.get("schema") != "schemas/architecture-conformance.schema.json":
            fail(f"{path.name} missing architecture conformance schema binding")
        checks = set(policy.get("required_checks", []))
        if checks != set(REQUIRED_CHECKS):
            fail(f"{path.name} architecture conformance required_checks drifted: {checks}")
        rules = set(workflow.get("rules", []))
        missing = required_rules - rules
        if missing:
            fail(f"{path.name} missing architecture hardening rules: {sorted(missing)}")
    print("PASS Greenfield/Brownfield architecture conformance workflow policy")


def validate_skill_registration() -> None:
    skills = load_yaml(SKILLS_PATH)
    if skills.get("version") != DEV_VERSION:
        fail("skill catalog must declare 0.5.1-dev")
    registry = skills.get("registry", {})
    spec = registry.get("dev-architecture-conformance")
    if spec != {
        "status": "materialized",
        "category": "core",
        "path": "skills/dev-architecture-conformance/SKILL.md",
    }:
        fail("dev-architecture-conformance registry entry drifted")
    mandatory = set(skills.get("mandatory_v0_5_1_materialized", []))
    if "dev-architecture-conformance" not in mandatory:
        fail("dev-architecture-conformance must be mandatory for 0.5.1")
    if not (ROOT / spec["path"]).is_file():
        fail("dev-architecture-conformance materialized file is missing")
    print("PASS architecture conformance skill registration")


def run_self_test() -> None:
    schema = load_json(SCHEMA_PATH)
    example = load_json(EXAMPLE_PATH)

    if schema.get("$id") != "https://eliasworks.dev/blueprint/0.5.1-dev/architecture-conformance.schema.json":
        fail("architecture conformance schema $id must be version-pinned to 0.5.1-dev")
    if schema.get("properties", {}).get("schema_version", {}).get("const") != DEV_VERSION:
        fail("architecture conformance schema_version must be const 0.5.1-dev")

    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(example, schema)
    validate_semantics(example)
    print("PASS architecture conformance schema + positive example")

    short_revision = copy.deepcopy(example)
    short_revision["implementation_revision"] = "1234567"
    expect_schema_failure(short_revision, schema, "implementation revision must be exact 40-character Git SHA")

    missing_command = copy.deepcopy(example)
    missing_command["guards"][0].pop("command", None)
    expect_schema_failure(missing_command, schema, "required-in-CI guard must declare executable command")

    with_violation = copy.deepcopy(example)
    with_violation["violations"] = [{
        "id": "VIOL-TEST",
        "constraint_id": "ARC-DOMAIN-FRAMEWORK-FREE",
        "location": "src/example",
        "description": "Synthetic forbidden dependency",
        "severity": "HIGH",
    }]
    expect_semantic_failure(with_violation, "PASS cannot hide an unresolved violation")

    failed_constraint = copy.deepcopy(example)
    failed_constraint["constraints"][0]["status"] = "FAIL"
    expect_semantic_failure(failed_constraint, "required constraint failure blocks PASS")

    no_ci_guard = copy.deepcopy(example)
    no_ci_guard["guards"][0]["required_in_ci"] = False
    expect_semantic_failure(no_ci_guard, "PASS requires a CI-enforced architecture guard")

    failed_ci_guard = copy.deepcopy(example)
    failed_ci_guard["guards"][0]["status"] = "FAIL"
    expect_semantic_failure(failed_ci_guard, "failed CI architecture guard blocks PASS")

    unknown_constraint = copy.deepcopy(example)
    unknown_constraint["decision"] = "FAIL"
    unknown_constraint["violations"] = [{
        "id": "VIOL-UNKNOWN",
        "constraint_id": "ARC-NOT-DECLARED",
        "location": "src/example",
        "description": "Synthetic dangling reference",
        "severity": "MEDIUM",
    }]
    expect_semantic_failure(unknown_constraint, "violation must reference declared constraint")

    validate_catalog_and_gates()
    validate_workflows()
    validate_skill_registration()

    print("Blueprint 0.5.1 architecture conformance validation: PASS")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate Blueprint 0.5.1 architecture implementation conformance"
    )
    parser.add_argument(
        "artifact",
        nargs="?",
        help="Optional consumer architecture-conformance JSON artifact. Without it, run Blueprint self-tests.",
    )
    parser.add_argument(
        "--project-root",
        default=".",
        help="Consumer repository root used to resolve architecture and guard artifact references.",
    )
    parser.add_argument(
        "--expected-revision",
        help="Optional exact 40-character implementation revision expected by CI/current head.",
    )
    args = parser.parse_args()

    if args.artifact:
        validate_consumer_artifact(
            Path(args.artifact).resolve(),
            Path(args.project_root).resolve(),
            args.expected_revision,
        )
    else:
        run_self_test()
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, jsonschema.ValidationError, jsonschema.SchemaError, OSError, json.JSONDecodeError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)