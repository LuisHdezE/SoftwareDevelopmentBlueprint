#!/usr/bin/env python3
from __future__ import annotations

import copy
import pathlib
import sys
from typing import Any, Callable

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests/fixtures/agent-system/multiagent-system.example.yaml"

CORE_AGENTS = {
    "orchestrator", "analyst", "planner", "architect", "database",
    "backend", "frontend", "qa", "security", "documentation", "auditor",
}


def load_fixture() -> dict[str, Any]:
    return yaml.safe_load(FIXTURE.read_text(encoding="utf-8"))


def validate_system(doc: dict[str, Any]) -> None:
    tasks = doc["tasks"]
    ids = [task["task_id"] for task in tasks]
    if len(ids) != len(set(ids)):
        raise AssertionError("System task ids must be unique")

    by_id = {task["task_id"]: task for task in tasks}
    graph = {task["task_id"]: [d["task_id"] for d in task["depends_on"]] for task in tasks}

    for task in tasks:
        participants = set(task["required_participants"])
        if "orchestrator" not in participants:
            raise AssertionError("Every governed task requires Orchestrator")
        if "auditor" not in participants:
            raise AssertionError("Every human-decision task requires Auditor")
        unknown = {
            p for p in participants
            if p not in CORE_AGENTS and not p.startswith("specialist:")
        }
        if unknown:
            raise AssertionError(f"Unknown participants: {sorted(unknown)}")
        for dependency in task["depends_on"]:
            if dependency["task_id"] not in by_id:
                raise AssertionError("Task graph references an unknown predecessor")
            if dependency["task_id"] == task["task_id"]:
                raise AssertionError("Task cannot depend on itself")

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(task_id: str) -> None:
        if task_id in visiting:
            raise AssertionError("System task graph cannot contain cycles")
        if task_id in visited:
            return
        visiting.add(task_id)
        for predecessor in graph[task_id]:
            visit(predecessor)
        visiting.remove(task_id)
        visited.add(task_id)

    for task_id in graph:
        visit(task_id)

    public = by_id["SYS-PUBLIC-002"]
    if "specialist:search-ai-discoverability" not in set(public["required_participants"]):
        raise AssertionError("Public indexable system task requires Search/AI Discoverability specialist")

    governance = doc["governance"]
    revision = governance["revision_transition"]
    if revision != {"requires_replanning": True, "exact_increment": 1}:
        raise AssertionError("System revision transition must be governed and monotonic")

    evidence = governance["evidence"]
    if evidence["stale_revision_may_satisfy_current_gate"]:
        raise AssertionError("Stale revision evidence cannot satisfy a current gate")
    if evidence["stale_head_may_satisfy_current_gate"]:
        raise AssertionError("Stale HEAD evidence cannot satisfy a current gate")
    if evidence["audit_may_be_preserved_across_revision"]:
        raise AssertionError("Audit evidence cannot be preserved across revisions")
    if not evidence["revalidation_emits_new_evidence"]:
        raise AssertionError("Revalidation must emit fresh evidence")

    authority = governance["authority"]
    if not authority["auditor_may_recommend_ready_for_merge"]:
        raise AssertionError("Auditor must be able to emit READY_FOR_MERGE recommendation")
    if authority["auditor_may_merge"]:
        raise AssertionError("Auditor cannot hold merge authority")
    if not authority["human_merge_approval_required"]:
        raise AssertionError("Human merge approval is mandatory")


def expect_failure(label: str, action: Callable[[], None]) -> None:
    try:
        action()
    except AssertionError:
        print(f"PASS negative guard: {label}")
        return
    raise AssertionError(f"Negative guard did not fail: {label}")


def main() -> int:
    doc = load_fixture()
    validate_system(doc)
    print("PASS complete multi-agent system fixture")

    mutated = copy.deepcopy(doc)
    mutated["tasks"][1]["depends_on"][0]["task_id"] = "SYS-MISSING-999"
    expect_failure("unknown predecessor fails closed", lambda: validate_system(mutated))

    mutated = copy.deepcopy(doc)
    mutated["tasks"][0]["depends_on"] = [
        {"task_id": "SYS-PUBLIC-002", "required_state": "READY_FOR_IMPLEMENTATION"}
    ]
    expect_failure("cyclic task graph fails closed", lambda: validate_system(mutated))

    mutated = copy.deepcopy(doc)
    mutated["tasks"][1]["required_participants"].remove("specialist:search-ai-discoverability")
    expect_failure("public task cannot omit discoverability specialist", lambda: validate_system(mutated))

    mutated = copy.deepcopy(doc)
    mutated["governance"]["evidence"]["stale_revision_may_satisfy_current_gate"] = True
    expect_failure("stale revision evidence cannot certify current task", lambda: validate_system(mutated))

    mutated = copy.deepcopy(doc)
    mutated["governance"]["evidence"]["stale_head_may_satisfy_current_gate"] = True
    expect_failure("stale HEAD evidence cannot certify candidate", lambda: validate_system(mutated))

    mutated = copy.deepcopy(doc)
    mutated["governance"]["evidence"]["audit_may_be_preserved_across_revision"] = True
    expect_failure("audit evidence cannot survive revision unchanged", lambda: validate_system(mutated))

    mutated = copy.deepcopy(doc)
    mutated["governance"]["authority"]["auditor_may_merge"] = True
    expect_failure("Auditor cannot merge", lambda: validate_system(mutated))

    mutated = copy.deepcopy(doc)
    mutated["governance"]["authority"]["human_merge_approval_required"] = False
    expect_failure("human merge authority cannot be removed", lambda: validate_system(mutated))

    print("Blueprint multi-agent system validation: PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise
