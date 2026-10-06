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
FIXTURE = ROOT / "tests/fixtures/agent-system/multiagent-system.example.yaml"
CHAIN_FIXTURE = ROOT / "tests/fixtures/agent-system/governed-chain.example.yaml"
EVIDENCE_FIXTURE = ROOT / "tests/fixtures/agent-system/evidence-records.example.yaml"
EVIDENCE_SCHEMA = ROOT / "schemas/evidence-record.schema.json"

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


def validate_governed_chain(doc: dict[str, Any]) -> None:
    task = doc["task_packet"]
    orchestration = doc["orchestration"]
    handoffs = doc["handoffs"]

    if task["task_id"] != orchestration["task"]["id"]:
        raise AssertionError("Task Packet and orchestration task identity must match")
    if task["revision"] != orchestration["task"]["revision"]:
        raise AssertionError("Task Packet and orchestration revision must match")
    if task["baseline"] != orchestration["baseline"]:
        raise AssertionError("Task Packet and orchestration candidate baseline must match")

    declared = set(orchestration["handoffs"])
    actual = {handoff["handoff_id"]: handoff for handoff in handoffs}
    if declared != set(actual):
        raise AssertionError("Orchestration handoff set must resolve exactly to chain documents")

    participants = set(task["required_agents"]) | set(task["required_specialists"]) | {"orchestrator"}
    order = orchestration["execution_order"]
    if not participants.issubset(set(order)):
        raise AssertionError("Every required participant must execute in the governed chain")

    position = {participant: index for index, participant in enumerate(order)}
    for handoff_id in declared:
        handoff = actual[handoff_id]
        if handoff["task_id"] != task["task_id"]:
            raise AssertionError("Handoff task identity drifted")
        if handoff["task_revision"] != task["revision"]:
            raise AssertionError("Stale handoff revision cannot satisfy current chain")
        if handoff["head_sha"] != task["baseline"]["head_sha"]:
            raise AssertionError("Handoff evidence must match exact candidate HEAD")
        if not handoff["evidence_ids"]:
            raise AssertionError("Every governed handoff requires evidence")
        producer = handoff["from_agent"]
        for target in handoff["to_agents"]:
            if target == "human":
                if producer != "auditor":
                    raise AssertionError("Only Auditor may cross the human decision boundary")
                continue
            if producer not in position or target not in position:
                raise AssertionError("Handoff participants must exist in execution order")
            if position[producer] >= position[target]:
                raise AssertionError("Handoff must preserve execution causality")

    auditor = actual.get("HO-SYS-CHAIN-001-AUDITOR-HUMAN")
    if not auditor or auditor.get("status") != "READY_FOR_MERGE":
        raise AssertionError("Current chain requires Auditor READY_FOR_MERGE handoff")
    if orchestration["current_state"] != "READY_FOR_HUMAN_DECISION":
        raise AssertionError("Audited chain must stop at human-decision boundary")
    if "merge_approval" not in orchestration["required_human_decisions"]:
        raise AssertionError("Human merge approval must remain explicit")


def validate_evidence_records(chain: dict[str, Any], evidence_doc: dict[str, Any]) -> None:
    schema = json.loads(EVIDENCE_SCHEMA.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    records = evidence_doc["evidence"]
    by_id: dict[str, dict[str, Any]] = {}

    for record in records:
        errors = sorted(validator.iter_errors(record), key=lambda e: list(e.path))
        if errors:
            raise AssertionError(f"Evidence schema invalid for {record.get('evidence_id')}: {errors[0].message}")
        if record["evidence_id"] in by_id:
            raise AssertionError("Evidence ids must be globally unique within the governed chain")
        by_id[record["evidence_id"]] = record

    task = chain["task_packet"]
    expected_baseline = task["baseline"]
    for handoff in chain["handoffs"]:
        for evidence_id in handoff["evidence_ids"]:
            if evidence_id not in by_id:
                raise AssertionError(f"Missing Evidence Record: {evidence_id}")
            record = by_id[evidence_id]
            if record["task_id"] != task["task_id"]:
                raise AssertionError("Evidence Record belongs to another task")
            if record["task_revision"] != task["revision"]:
                raise AssertionError("Evidence Record belongs to a stale task revision")
            if record["baseline"] != expected_baseline:
                raise AssertionError("Evidence Record does not match exact candidate baseline")
            if record["producer_agent"] != handoff["from_agent"]:
                raise AssertionError("Handoff cannot present evidence produced by another agent")
            if record["result"] != "PASS":
                raise AssertionError("Only PASS evidence can satisfy a successful governed handoff")

    audit = by_id.get("EVD-SYS-AUDIT-R2")
    if not audit or audit["producer_agent"] != "auditor" or audit["evidence_type"] != "AUDIT_EVIDENCE":
        raise AssertionError("Human decision boundary requires current Auditor evidence")


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

    chain = yaml.safe_load(CHAIN_FIXTURE.read_text(encoding="utf-8"))
    validate_governed_chain(chain)
    print("PASS governed Task Packet -> orchestration -> handoff -> human chain")

    evidence_doc = yaml.safe_load(EVIDENCE_FIXTURE.read_text(encoding="utf-8"))
    validate_evidence_records(chain, evidence_doc)
    print("PASS concrete Evidence Records resolve the governed chain")

    mutated_evidence = copy.deepcopy(evidence_doc)
    mutated_evidence["evidence"] = mutated_evidence["evidence"][1:]
    expect_failure("missing evidence document breaks chain", lambda: validate_evidence_records(chain, mutated_evidence))

    mutated_evidence = copy.deepcopy(evidence_doc)
    mutated_evidence["evidence"][0]["producer_agent"] = "backend"
    expect_failure("agent cannot present another producer's evidence", lambda: validate_evidence_records(chain, mutated_evidence))

    mutated_evidence = copy.deepcopy(evidence_doc)
    mutated_evidence["evidence"][2]["task_revision"] = 1
    expect_failure("stale Evidence Record cannot satisfy current revision", lambda: validate_evidence_records(chain, mutated_evidence))

    mutated_evidence = copy.deepcopy(evidence_doc)
    mutated_evidence["evidence"][3]["baseline"]["head_sha"] = "deadbeef"
    expect_failure("Evidence Record must match exact candidate HEAD", lambda: validate_evidence_records(chain, mutated_evidence))

    mutated_chain = copy.deepcopy(chain)
    mutated_chain["handoffs"][0]["task_revision"] = 1
    expect_failure("stale handoff revision breaks governed chain", lambda: validate_governed_chain(mutated_chain))

    mutated_chain = copy.deepcopy(chain)
    mutated_chain["handoffs"][1]["head_sha"] = "deadbeef"
    expect_failure("stale candidate HEAD breaks governed chain", lambda: validate_governed_chain(mutated_chain))

    mutated_chain = copy.deepcopy(chain)
    mutated_chain["handoffs"][-1]["from_agent"] = "qa"
    expect_failure("non-Auditor cannot cross human boundary", lambda: validate_governed_chain(mutated_chain))

    mutated_chain = copy.deepcopy(chain)
    mutated_chain["orchestration"]["handoffs"].append("HO-SYS-CHAIN-001-MISSING")
    expect_failure("unresolved handoff reference breaks governed chain", lambda: validate_governed_chain(mutated_chain))

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
