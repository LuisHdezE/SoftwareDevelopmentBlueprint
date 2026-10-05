#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
import pathlib
import re
import sys
from typing import Any, Callable

import yaml
from jsonschema import Draft202012Validator, FormatChecker

ROOT = pathlib.Path(__file__).resolve().parents[1]

CORE_AGENTS = (
    "orchestrator",
    "analyst",
    "planner",
    "architect",
    "database",
    "backend",
    "frontend",
    "qa",
    "security",
    "documentation",
    "auditor",
)

SPECIALIST_ID = re.compile(r"^specialist:[a-z][a-z0-9-]*$")

ROLE_STATUSES = {
    "orchestrator": {"ROUTED", "READY_FOR_HUMAN_DECISION", "BLOCKED", "REJECTED"},
    "analyst": {"ANALYZED", "BLOCKED"},
    "planner": {"PLANNED", "BLOCKED"},
    "architect": {"ARCHITECTURE_READY", "BLOCKED"},
    "database": {"DATA_READY", "BLOCKED"},
    "backend": {"BACKEND_IMPLEMENTED", "BLOCKED"},
    "frontend": {"FRONTEND_IMPLEMENTED", "BLOCKED"},
    "qa": {"QA_PASS", "QA_FAIL", "BLOCKED"},
    "security": {"SECURITY_PASS", "SECURITY_FAIL", "BLOCKED"},
    "documentation": {"DOCUMENTED", "BLOCKED"},
    "auditor": {"READY_FOR_MERGE", "BLOCKED", "REJECTED"},
}

SPECIALIST_STATUSES = {"SPECIALIST_PASS", "SPECIALIST_FAIL", "BLOCKED"}


def is_specialist(agent: str) -> bool:
    return bool(SPECIALIST_ID.fullmatch(agent))


def allowed_statuses(agent: str) -> set[str]:
    if agent in ROLE_STATUSES:
        return ROLE_STATUSES[agent]
    if is_specialist(agent):
        return SPECIALIST_STATUSES
    raise AssertionError(f"Unknown agent or specialist id: {agent}")



def load(path: str) -> Any:
    p = ROOT / path
    text = p.read_text(encoding="utf-8")
    if p.suffix == ".json":
        return json.loads(text)
    if p.suffix in {".yaml", ".yml"}:
        return yaml.safe_load(text)
    raise ValueError(f"Unsupported file type: {path}")


def validate_schema(schema_path: str, instance_path: str) -> Any:
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
    return instance


def validate_agent_contract(doc: dict[str, Any]) -> None:
    agent = doc["agent"]
    allowed = allowed_statuses(agent)
    statuses = set(doc["completion_statuses"])
    invalid = statuses - allowed
    if invalid:
        raise AssertionError(
            f"Agent {agent} declares statuses owned by another role: {sorted(invalid)}"
        )
    if agent in set(doc.get("handoff_targets", [])):
        raise AssertionError(f"Agent {agent} cannot hand off to itself")


def validate_task_packet(doc: dict[str, Any]) -> None:
    required = set(doc["required_agents"])
    optional = set(doc["optional_agents"])
    not_applicable = set(doc["not_applicable_agents"])

    overlaps = {
        "required_optional": required & optional,
        "required_not_applicable": required & not_applicable,
        "optional_not_applicable": optional & not_applicable,
    }
    bad = {name: sorted(values) for name, values in overlaps.items() if values}
    if bad:
        raise AssertionError(f"Task agent applicability sets overlap: {bad}")

    if doc["owner_agent"] not in required:
        raise AssertionError("Task owner_agent must be listed in required_agents")

    if doc["task_id"] in set(doc["dependencies"]):
        raise AssertionError("Task cannot depend on itself")


def validate_handoff(doc: dict[str, Any]) -> None:
    from_agent = doc["from_agent"]
    targets = set(doc["to_agents"])

    if from_agent in targets:
        raise AssertionError("Agent handoff cannot target the producing agent itself")
    if "human" in targets and from_agent != "auditor":
        raise AssertionError("Only Auditor may hand off a merge decision to human")

    status = doc["status"]
    if status not in allowed_statuses(from_agent):
        raise AssertionError(
            f"Handoff status {status} is not owned by agent {from_agent}"
        )

    has_blocking_item = any(item["blocking"] for item in doc["blockers"])
    has_blocking_question = any(
        item["priority"] == "BLOCKING" for item in doc["open_questions"]
    )
    if (has_blocking_item or has_blocking_question) and status not in {
        "BLOCKED",
        "REJECTED",
    }:
        raise AssertionError(
            "A successful handoff cannot carry unresolved blocking items or questions"
        )


def validate_orchestration(doc: dict[str, Any]) -> None:
    agents = doc["agents"]
    specialists = doc.get("specialists", {})
    participants = {**agents, **specialists}
    execution_order = doc["execution_order"]
    order = set(execution_order)

    if agents["orchestrator"] not in {"REQUIRED", "COMPLETED"}:
        raise AssertionError(
            "Orchestrator must be REQUIRED or COMPLETED for every adopted multi-agent orchestration"
        )
    terminal_states = {"READY_FOR_HUMAN_DECISION", "CLOSED"}
    if doc["current_state"] not in terminal_states and agents["orchestrator"] != "REQUIRED":
        raise AssertionError(
            "Orchestrator must remain REQUIRED until human-decision handoff or closure"
        )
    if doc["current_state"] == "READY_FOR_HUMAN_DECISION" and agents["orchestrator"] != "COMPLETED":
        raise AssertionError(
            "Orchestrator completes only when coordination reaches the human-decision boundary"
        )
    if "orchestrator" not in order:
        raise AssertionError(
            "Orchestrator must participate in execution_order for every adopted multi-agent orchestration"
        )
    if execution_order[0] != "orchestrator":
        raise AssertionError(
            "Orchestrator must be the first participant in execution_order"
        )

    unknown = {participant for participant in order if participant not in participants}
    if unknown:
        raise AssertionError(
            f"Execution order contains undeclared participants: {sorted(unknown)}"
        )

    not_applicable_in_order = {
        participant
        for participant in order
        if participants[participant] == "NOT_APPLICABLE"
    }
    if not_applicable_in_order:
        raise AssertionError(
            "Execution order contains NOT_APPLICABLE agents: "
            f"{sorted(not_applicable_in_order)}"
        )

    required = {
        participant
        for participant, state in participants.items()
        if state == "REQUIRED"
    }
    missing_required = required - order
    if missing_required:
        raise AssertionError(
            f"Required agents missing from execution_order: {sorted(missing_required)}"
        )

    current_agent = doc.get("current_agent")
    if current_agent is not None:
        if current_agent not in order:
            raise AssertionError("current_agent must exist in execution_order")
        if participants[current_agent] in {"NOT_APPLICABLE", "COMPLETED"}:
            raise AssertionError(
                f"current_agent cannot be {participants[current_agent]}"
            )

    blocked_by = doc["blocked_by"]
    if blocked_by and doc["current_state"] != "BLOCKED":
        raise AssertionError(
            "blocked_by must be empty unless current_state is BLOCKED"
        )
    if doc["current_state"] == "BLOCKED" and not blocked_by:
        raise AssertionError("BLOCKED orchestration requires blocked_by")

    if doc["current_state"] == "READY_FOR_HUMAN_DECISION":
        unresolved = {
            participant
            for participant, state in participants.items()
            if state in {"REQUIRED", "BLOCKED"}
        }
        if unresolved:
            raise AssertionError(
                "READY_FOR_HUMAN_DECISION cannot retain unresolved agents: "
                f"{sorted(unresolved)}"
            )
        if agents["auditor"] != "COMPLETED":
            raise AssertionError(
                "READY_FOR_HUMAN_DECISION requires completed Auditor"
            )
        auditor_handoff_marker = f"-AUDITOR"
        if not any(auditor_handoff_marker in handoff for handoff in doc["handoffs"]):
            raise AssertionError(
                "READY_FOR_HUMAN_DECISION requires a recorded Auditor handoff"
            )
        if not doc["required_human_decisions"]:
            raise AssertionError(
                "READY_FOR_HUMAN_DECISION requires an explicit human decision"
            )


def validate_protocol_chain(
    task: dict[str, Any],
    orchestration: dict[str, Any],
    handoff_docs: list[dict[str, Any]],
) -> None:
    if task["task_id"] != orchestration["task"]["id"]:
        raise AssertionError("Task Packet and orchestration task ids must match")

    task_baseline = task["baseline"]
    orchestration_baseline = orchestration["baseline"]
    for field in ("repository", "base_branch", "base_sha"):
        if task_baseline[field] != orchestration_baseline[field]:
            raise AssertionError(
                f"Task Packet and orchestration baseline mismatch: {field}"
            )

    for field in ("working_branch", "head_sha", "pull_request"):
        task_value = task_baseline.get(field)
        orchestration_value = orchestration_baseline.get(field)
        if task_value is not None and task_value != orchestration_value:
            raise AssertionError(
                f"Task Packet and orchestration candidate mismatch: {field}"
            )

    task_required = set(task["required_agents"])
    task_optional = set(task["optional_agents"])
    task_na = set(task["not_applicable_agents"])
    participants = {**orchestration["agents"], **orchestration.get("specialists", {})}

    for participant in task_required:
        if participant not in participants:
            raise AssertionError(
                f"Required Task Packet participant missing from orchestration: {participant}"
            )
        if participants[participant] in {"OPTIONAL", "NOT_APPLICABLE"}:
            raise AssertionError(
                f"Required Task Packet participant is not required/completed in orchestration: {participant}"
            )

    for participant in task_na:
        if participant in participants and participants[participant] != "NOT_APPLICABLE":
            raise AssertionError(
                f"Task Packet N/A participant is active in orchestration: {participant}"
            )

    declared = task_required | task_optional | task_na
    for item in handoff_docs:
        if item["task_id"] != task["task_id"]:
            continue
        involved = {item["from_agent"]} | {
            target for target in item["to_agents"] if target != "human"
        }
        undeclared = {
            participant
            for participant in involved
            if participant not in declared and participant != "orchestrator"
        }
        if undeclared:
            raise AssertionError(
                f"Handoff uses participants outside Task Packet applicability: {sorted(undeclared)}"
            )

    validate_orchestration_handoffs(orchestration, handoff_docs)
    validate_execution_causality(orchestration, handoff_docs)


def validate_execution_causality(
    orchestration: dict[str, Any],
    handoff_docs: list[dict[str, Any]],
) -> None:
    position = {
        participant: index
        for index, participant in enumerate(orchestration["execution_order"])
    }
    declared_ids = set(orchestration["handoffs"])

    for item in handoff_docs:
        if item["handoff_id"] not in declared_ids:
            continue
        producer = item["from_agent"]
        if producer not in position:
            raise AssertionError(
                f"Handoff producer is absent from execution_order: {producer}"
            )
        for target in item["to_agents"]:
            if target == "human":
                continue
            if target not in position:
                raise AssertionError(
                    f"Handoff target is absent from execution_order: {target}"
                )
            if position[producer] >= position[target]:
                raise AssertionError(
                    f"Handoff violates execution causality: {producer} must precede {target}"
                )


def validate_orchestration_handoffs(
    orchestration: dict[str, Any],
    handoff_docs: list[dict[str, Any]],
) -> None:
    declared_ids = set(orchestration["handoffs"])
    actual_by_id = {item["handoff_id"]: item for item in handoff_docs}

    missing = declared_ids - set(actual_by_id)
    if missing:
        raise AssertionError(
            f"Orchestration references handoffs without evidence documents: {sorted(missing)}"
        )

    task_id = orchestration["task"]["id"]
    repository = orchestration["baseline"]["repository"]
    head_sha = orchestration["baseline"].get("head_sha")

    for handoff_id in declared_ids:
        item = actual_by_id[handoff_id]
        if item["task_id"] != task_id:
            raise AssertionError(
                f"Handoff {handoff_id} belongs to task {item['task_id']}, expected {task_id}"
            )
        if item["baseline"]["repository"] != repository:
            raise AssertionError(
                f"Handoff {handoff_id} repository does not match orchestration baseline"
            )
        if head_sha is not None and item["baseline"]["head_sha"] != head_sha:
            raise AssertionError(
                f"Handoff {handoff_id} HEAD does not match orchestration candidate HEAD"
            )

    if orchestration["current_state"] == "READY_FOR_HUMAN_DECISION":
        auditor_docs = [
            item
            for item in actual_by_id.values()
            if item["handoff_id"] in declared_ids
            and item["from_agent"] == "auditor"
            and item["status"] == "READY_FOR_MERGE"
        ]
        if not auditor_docs:
            raise AssertionError(
                "READY_FOR_HUMAN_DECISION requires Auditor READY_FOR_MERGE handoff evidence"
            )


def validate_specialist_registry(doc: dict[str, Any]) -> None:
    seen: set[str] = set()
    for item in doc["specialists"]:
        specialist_id = item["id"]
        if not is_specialist(specialist_id):
            raise AssertionError(f"Invalid specialist id: {specialist_id}")
        if specialist_id in seen:
            raise AssertionError(f"Duplicate specialist id: {specialist_id}")
        seen.add(specialist_id)

        if item["core_agent"] is not False:
            raise AssertionError(f"Specialist {specialist_id} cannot be a core agent")

        if item["completion_statuses"] != [
            "SPECIALIST_PASS",
            "SPECIALIST_FAIL",
            "BLOCKED",
        ]:
            raise AssertionError(
                f"Specialist {specialist_id} must use canonical specialist statuses"
            )

        contract_path = ROOT / item["contract"]
        if not contract_path.is_file():
            raise AssertionError(
                f"Specialist contract does not exist: {item['contract']}"
            )


def expect_failure(label: str, action: Callable[[], None]) -> None:
    try:
        action()
    except AssertionError:
        print(f"PASS negative guard: {label}")
        return
    raise AssertionError(f"Negative guard did not fail: {label}")


def main() -> int:
    registry = validate_schema(
        "schemas/specialist-agent-registry.schema.json",
        "catalog/specialist-agents.proposal.yaml",
    )
    validate_specialist_registry(registry)
    print("PASS specialist registry")

    pairs = [
        (
            "schemas/agent-contract.schema.json",
            "templates/agent-contract.example.yaml",
            validate_agent_contract,
        ),
        (
            "schemas/task-packet.schema.json",
            "templates/task-packet.example.yaml",
            validate_task_packet,
        ),
        (
            "schemas/agent-handoff.schema.json",
            "templates/agent-handoff.example.yaml",
            validate_handoff,
        ),
        (
            "schemas/orchestration-state.schema.json",
            "templates/orchestration.example.yaml",
            validate_orchestration,
        ),
    ]

    docs: dict[str, dict[str, Any]] = {}
    for schema_path, instance_path, semantic_validator in pairs:
        instance = validate_schema(schema_path, instance_path)
        semantic_validator(instance)
        docs[instance_path] = instance
        print(f"PASS protocol contract: {instance_path} -> {schema_path}")

    agent = docs["templates/agent-contract.example.yaml"]
    task = docs["templates/task-packet.example.yaml"]
    handoff = docs["templates/agent-handoff.example.yaml"]
    orchestration = docs["templates/orchestration.example.yaml"]

    specialist_agent = validate_schema(
        "schemas/agent-contract.schema.json",
        "templates/search-ai-discoverability-agent.example.yaml",
    )
    validate_agent_contract(specialist_agent)
    print("PASS specialist contract: search-ai-discoverability")

    specialist_task = validate_schema(
        "schemas/task-packet.schema.json",
        "templates/discoverability-task-packet.example.yaml",
    )
    validate_task_packet(specialist_task)
    print("PASS specialist task packet")

    specialist_handoff = validate_schema(
        "schemas/agent-handoff.schema.json",
        "templates/discoverability-handoff.example.yaml",
    )
    validate_handoff(specialist_handoff)
    print("PASS specialist handoff")

    specialist_orchestration = validate_schema(
        "schemas/orchestration-state.schema.json",
        "templates/discoverability-orchestration.example.yaml",
    )
    validate_orchestration(specialist_orchestration)
    print("PASS specialist orchestration")

    auditor_handoff = validate_schema(
        "schemas/agent-handoff.schema.json",
        "templates/auditor-human-handoff.example.yaml",
    )
    validate_handoff(auditor_handoff)
    print("PASS Auditor to human handoff contract")

    evidence_orchestration = copy.deepcopy(orchestration)
    evidence_orchestration["handoffs"] = [handoff["handoff_id"]]
    validate_protocol_chain(task, evidence_orchestration, [handoff])
    print("PASS Task Packet -> orchestration -> handoff chain of custody")


    mutated = copy.deepcopy(agent)
    mutated["handoff_targets"].append(mutated["agent"])
    expect_failure(
        "agent cannot hand off to itself",
        lambda: validate_agent_contract(mutated),
    )

    mutated = copy.deepcopy(agent)
    mutated["completion_statuses"] = ["FRONTEND_IMPLEMENTED"]
    expect_failure(
        "agent cannot claim another role status",
        lambda: validate_agent_contract(mutated),
    )

    mutated = copy.deepcopy(task)
    mutated["required_agents"].remove(mutated["owner_agent"])
    expect_failure(
        "task owner must be required",
        lambda: validate_task_packet(mutated),
    )

    mutated = copy.deepcopy(task)
    mutated["not_applicable_agents"].append("qa")
    expect_failure(
        "task applicability sets are disjoint",
        lambda: validate_task_packet(mutated),
    )

    mutated = copy.deepcopy(task)
    mutated["dependencies"].append(mutated["task_id"])
    expect_failure(
        "task cannot depend on itself",
        lambda: validate_task_packet(mutated),
    )

    mutated = copy.deepcopy(handoff)
    mutated["to_agents"] = ["human"]
    expect_failure(
        "only Auditor may hand off merge decision to human",
        lambda: validate_handoff(mutated),
    )

    mutated = copy.deepcopy(handoff)
    mutated["to_agents"].append(mutated["from_agent"])
    expect_failure(
        "handoff cannot target producer",
        lambda: validate_handoff(mutated),
    )

    mutated = copy.deepcopy(handoff)
    mutated["status"] = "QA_PASS"
    expect_failure(
        "handoff status belongs to producing role",
        lambda: validate_handoff(mutated),
    )

    mutated = copy.deepcopy(handoff)
    mutated["open_questions"].append(
        {
            "id": "Q-BLOCKING",
            "priority": "BLOCKING",
            "question": "Blocking question must stop successful handoff.",
        }
    )
    expect_failure(
        "successful handoff cannot carry blocking question",
        lambda: validate_handoff(mutated),
    )

    mutated = copy.deepcopy(orchestration)
    mutated["agents"]["orchestrator"] = "COMPLETED"
    expect_failure(
        "Orchestrator cannot complete while downstream work remains active",
        lambda: validate_orchestration(mutated),
    )

    mutated = copy.deepcopy(orchestration)
    mutated["agents"]["orchestrator"] = "NOT_APPLICABLE"
    expect_failure(
        "multi-agent orchestration cannot omit Orchestrator applicability",
        lambda: validate_orchestration(mutated),
    )

    mutated = copy.deepcopy(orchestration)
    mutated["execution_order"].remove("orchestrator")
    expect_failure(
        "multi-agent orchestration cannot omit Orchestrator execution",
        lambda: validate_orchestration(mutated),
    )

    mutated = copy.deepcopy(orchestration)
    mutated["execution_order"].remove("orchestrator")
    mutated["execution_order"].append("orchestrator")
    expect_failure(
        "Orchestrator must route before specialized execution",
        lambda: validate_orchestration(mutated),
    )

    mutated = copy.deepcopy(orchestration)
    mutated["execution_order"].append("backend")
    expect_failure(
        "NOT_APPLICABLE agent cannot execute",
        lambda: validate_orchestration(mutated),
    )

    mutated = copy.deepcopy(orchestration)
    mutated["blocked_by"] = ["external_dependency"]
    expect_failure(
        "blocked_by requires BLOCKED state",
        lambda: validate_orchestration(mutated),
    )

    mutated = copy.deepcopy(orchestration)
    mutated["current_state"] = "READY_FOR_HUMAN_DECISION"
    mutated["current_agent"] = None
    mutated["agents"]["qa"] = "COMPLETED"
    mutated["agents"]["auditor"] = "REQUIRED"
    expect_failure(
        "human decision requires completed Auditor",
        lambda: validate_orchestration(mutated),
    )

    mutated = copy.deepcopy(orchestration)
    mutated["current_state"] = "READY_FOR_HUMAN_DECISION"
    mutated["current_agent"] = None
    for participant, state in list(mutated["agents"].items()):
        if state == "REQUIRED":
            mutated["agents"][participant] = "COMPLETED"
    mutated["handoffs"] = [
        handoff for handoff in mutated["handoffs"] if "-AUDITOR" not in handoff
    ]
    expect_failure(
        "human decision requires recorded Auditor handoff",
        lambda: validate_orchestration(mutated),
    )

    mutated_task = copy.deepcopy(task)
    mutated_task["task_id"] = "BP-OTHER-999"
    expect_failure(
        "Task Packet and orchestration must describe the same task",
        lambda: validate_protocol_chain(mutated_task, evidence_orchestration, [handoff]),
    )

    mutated_task = copy.deepcopy(task)
    mutated_task["baseline"]["base_sha"] = "7654321"
    expect_failure(
        "Task Packet and orchestration must share the same baseline",
        lambda: validate_protocol_chain(mutated_task, evidence_orchestration, [handoff]),
    )

    mutated_task = copy.deepcopy(task)
    mutated_task["required_agents"].append("backend")
    mutated_task["not_applicable_agents"].remove("backend")
    expect_failure(
        "required Task Packet participant cannot be N/A in orchestration",
        lambda: validate_protocol_chain(mutated_task, evidence_orchestration, [handoff]),
    )

    mutated = copy.deepcopy(evidence_orchestration)
    mutated["handoffs"].append("HO-BP-CART-001-FAKE")
    expect_failure(
        "orchestration cannot reference nonexistent handoff evidence",
        lambda: validate_orchestration_handoffs(mutated, [handoff]),
    )

    mutated_handoff = copy.deepcopy(handoff)
    mutated_handoff["task_id"] = "BP-OTHER-999"
    expect_failure(
        "handoff evidence must belong to orchestration task",
        lambda: validate_orchestration_handoffs(evidence_orchestration, [mutated_handoff]),
    )

    mutated_orchestration = copy.deepcopy(evidence_orchestration)
    mutated_orchestration["execution_order"].remove("frontend")
    mutated_orchestration["execution_order"].insert(
        mutated_orchestration["execution_order"].index("qa") + 1, "frontend"
    )
    expect_failure(
        "handoff producer must precede its consumer in execution order",
        lambda: validate_protocol_chain(task, mutated_orchestration, [handoff]),
    )

    mutated_handoff = copy.deepcopy(handoff)
    mutated_handoff["baseline"]["head_sha"] = "7654321"
    expect_failure(
        "handoff evidence must match orchestration candidate HEAD",
        lambda: validate_orchestration_handoffs(evidence_orchestration, [mutated_handoff]),
    )

    mutated = copy.deepcopy(specialist_agent)
    mutated["completion_statuses"] = ["QA_PASS"]
    expect_failure(
        "specialist cannot claim QA status",
        lambda: validate_agent_contract(mutated),
    )

    mutated = copy.deepcopy(specialist_handoff)
    mutated["status"] = "READY_FOR_MERGE"
    expect_failure(
        "specialist cannot claim Auditor status",
        lambda: validate_handoff(mutated),
    )

    mutated = copy.deepcopy(specialist_orchestration)
    mutated["execution_order"].append("specialist:not-declared")
    expect_failure(
        "undeclared specialist cannot execute",
        lambda: validate_orchestration(mutated),
    )

    print("Blueprint agent protocol proposal validation: PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise
