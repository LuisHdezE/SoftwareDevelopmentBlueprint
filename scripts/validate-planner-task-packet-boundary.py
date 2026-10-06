#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
import pathlib
import sys
from typing import Any, Callable

import yaml
from jsonschema import Draft202012Validator, FormatChecker

ROOT = pathlib.Path(__file__).resolve().parents[1]
LIFECYCLE_AGENTS = {"orchestrator", "analyst", "planner"}


def load(path: str) -> Any:
    target = ROOT / path
    text = target.read_text(encoding="utf-8")
    if target.suffix == ".json":
        return json.loads(text)
    if target.suffix in {".yaml", ".yml"}:
        return yaml.safe_load(text)
    raise ValueError(f"Unsupported file type: {path}")


def validate_schema(schema_path: str, instance_path: str) -> Any:
    schema = load(schema_path)
    instance = load(instance_path)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(instance), key=lambda item: list(item.path))
    if errors:
        details = "\n".join(
            f"- {instance_path}:{'/'.join(map(str, error.path)) or '<root>'}: {error.message}"
            for error in errors
        )
        raise AssertionError(f"Schema validation failed:\n{details}")
    return instance


def active_task_participants(task: dict[str, Any]) -> set[str]:
    return set(task["required_agents"]) | set(task["optional_agents"])


def validate_planner_task_packet_boundary(
    task: dict[str, Any],
    orchestration: dict[str, Any],
    handoff: dict[str, Any],
) -> None:
    if handoff["scope"] != "TASK_PACKET_BOUNDARY":
        raise AssertionError("Planner start boundary handoff must use TASK_PACKET_BOUNDARY scope")
    if handoff["from_agent"] != "planner":
        raise AssertionError("TASK_PACKET_BOUNDARY handoff must be produced by Planner")
    if handoff["status"] != "PLANNED":
        raise AssertionError("TASK_PACKET_BOUNDARY handoff must carry Planner-owned PLANNED status")
    if "human" in handoff["to_agents"]:
        raise AssertionError("TASK_PACKET_BOUNDARY cannot target human")

    if task["task_id"] != orchestration["task"]["id"] or task["task_id"] != handoff["task_id"]:
        raise AssertionError("Task Packet, orchestration, and boundary handoff must describe the same task")
    if task["revision"] != orchestration["task"]["revision"] or task["revision"] != handoff["task_revision"]:
        raise AssertionError("Task Packet, orchestration, and boundary handoff must share the same revision")

    task_baseline = task["baseline"]
    orchestration_baseline = orchestration["baseline"]
    for field in ("repository", "base_branch", "base_sha"):
        if task_baseline[field] != orchestration_baseline[field]:
            raise AssertionError(f"Task Packet and orchestration baseline mismatch: {field}")
    if handoff["baseline"]["repository"] != orchestration_baseline["repository"]:
        raise AssertionError("Boundary handoff repository must match orchestration baseline")
    if handoff["baseline"]["head_sha"] != orchestration_baseline["head_sha"]:
        raise AssertionError("Boundary handoff HEAD must match orchestration candidate HEAD")

    active = active_task_participants(task)
    not_applicable = set(task["not_applicable_agents"])
    targets = set(handoff["to_agents"])

    lifecycle_targets = targets & LIFECYCLE_AGENTS
    if lifecycle_targets:
        raise AssertionError(f"TASK_PACKET_BOUNDARY cannot target lifecycle agents: {sorted(lifecycle_targets)}")

    undeclared = targets - active
    if undeclared:
        raise AssertionError(f"TASK_PACKET_BOUNDARY target is not active in Task Packet: {sorted(undeclared)}")

    forbidden = targets & not_applicable
    if forbidden:
        raise AssertionError(f"TASK_PACKET_BOUNDARY cannot target N/A agents: {sorted(forbidden)}")

    participants = {**orchestration["agents"], **orchestration.get("specialists", {})}
    missing = targets - set(participants)
    if missing:
        raise AssertionError(f"Boundary target is absent from orchestration participants: {sorted(missing)}")
    inactive = {target for target in targets if participants[target] == "NOT_APPLICABLE"}
    if inactive:
        raise AssertionError(f"Boundary target is inactive in orchestration: {sorted(inactive)}")

    order = orchestration["execution_order"]
    if "planner" not in order:
        raise AssertionError("Planner must appear in execution_order before a start boundary can exist")
    planner_index = order.index("planner")
    downstream = [agent for agent in order[planner_index + 1 :] if agent not in LIFECYCLE_AGENTS]
    if not downstream:
        raise AssertionError("TASK_PACKET_BOUNDARY requires at least one downstream executor")
    first_executor = downstream[0]
    if targets != {first_executor}:
        raise AssertionError(
            "TASK_PACKET_BOUNDARY must target exactly the first non-lifecycle executor: "
            f"{first_executor}"
        )

    if handoff["handoff_id"] not in orchestration["handoffs"]:
        raise AssertionError("Orchestration must record the planner boundary handoff id")


def validate_scope_separation(task: dict[str, Any], handoff: dict[str, Any]) -> None:
    active = active_task_participants(task)
    targets = set(handoff["to_agents"])
    if handoff["scope"] == "LIFECYCLE_GOVERNANCE":
        involved = {handoff["from_agent"]} | targets
        if not involved.issubset(LIFECYCLE_AGENTS):
            raise AssertionError("LIFECYCLE_GOVERNANCE cannot dispatch work to Task Packet executors")
    if handoff["scope"] == "TASK_EXECUTION":
        involved = {handoff["from_agent"]} | targets
        lifecycle_involved = involved & LIFECYCLE_AGENTS
        if lifecycle_involved:
            raise AssertionError(f"TASK_EXECUTION cannot include lifecycle agents: {sorted(lifecycle_involved)}")
        undeclared = involved - active
        if undeclared:
            raise AssertionError(f"TASK_EXECUTION uses undeclared Task Packet participants: {sorted(undeclared)}")


def expect_failure(label: str, action: Callable[[], None]) -> None:
    try:
        action()
    except AssertionError:
        print(f"PASS negative guard: {label}")
        return
    raise AssertionError(f"Negative guard did not fail: {label}")


def main() -> int:
    task = validate_schema("schemas/task-packet.schema.json", "templates/task-packet.example.yaml")
    orchestration = validate_schema("schemas/orchestration-state.schema.json", "templates/orchestration.example.yaml")
    boundary = validate_schema(
        "schemas/agent-handoff.schema.json",
        "templates/planner-task-packet-boundary-handoff.example.yaml",
    )

    validate_planner_task_packet_boundary(task, orchestration, boundary)
    print("PASS Planner -> first executor Task Packet boundary")

    lifecycle_mask = copy.deepcopy(boundary)
    lifecycle_mask["scope"] = "LIFECYCLE_GOVERNANCE"
    expect_failure(
        "planner cannot dispatch executor work as lifecycle governance",
        lambda: validate_scope_separation(task, lifecycle_mask),
    )

    execution_mask = copy.deepcopy(boundary)
    execution_mask["scope"] = "TASK_EXECUTION"
    expect_failure(
        "planner cannot masquerade as a Task Packet executor",
        lambda: validate_scope_separation(task, execution_mask),
    )

    mutated = copy.deepcopy(boundary)
    mutated["to_agents"] = ["backend"]
    expect_failure(
        "boundary cannot target a not-applicable agent",
        lambda: validate_planner_task_packet_boundary(task, orchestration, mutated),
    )

    mutated = copy.deepcopy(boundary)
    mutated["to_agents"] = ["qa"]
    expect_failure(
        "boundary cannot skip the first executor",
        lambda: validate_planner_task_packet_boundary(task, orchestration, mutated),
    )

    mutated = copy.deepcopy(boundary)
    mutated["to_agents"] = ["analyst"]
    expect_failure(
        "boundary cannot target lifecycle agents",
        lambda: validate_planner_task_packet_boundary(task, orchestration, mutated),
    )

    mutated = copy.deepcopy(boundary)
    mutated["to_agents"] = ["human"]
    expect_failure(
        "boundary cannot target human",
        lambda: validate_planner_task_packet_boundary(task, orchestration, mutated),
    )

    mutated = copy.deepcopy(boundary)
    mutated["from_agent"] = "orchestrator"
    expect_failure(
        "boundary must be produced by Planner",
        lambda: validate_planner_task_packet_boundary(task, orchestration, mutated),
    )

    mutated = copy.deepcopy(orchestration)
    mutated["handoffs"] = [item for item in mutated["handoffs"] if item != boundary["handoff_id"]]
    expect_failure(
        "orchestration must record the planner boundary evidence",
        lambda: validate_planner_task_packet_boundary(task, mutated, boundary),
    )

    print("Blueprint planner task packet boundary validation: PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise
