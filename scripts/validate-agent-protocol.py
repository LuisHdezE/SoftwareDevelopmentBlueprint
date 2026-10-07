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

NON_COMPLETION_STATUSES = {
    "BLOCKED",
    "REJECTED",
    "QA_FAIL",
    "SECURITY_FAIL",
    "SPECIALIST_FAIL",
}


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

    dependency_ids = [item["task_id"] for item in doc["dependencies"]]
    if len(dependency_ids) != len(set(dependency_ids)):
        raise AssertionError("Task dependencies must reference unique predecessor tasks")
    if doc["task_id"] in set(dependency_ids):
        raise AssertionError("Task cannot depend on itself")


def validate_handoff(doc: dict[str, Any]) -> None:
    from_agent = doc["from_agent"]
    targets = set(doc["to_agents"])

    if from_agent in targets:
        raise AssertionError("Agent handoff cannot target the producing agent itself")
    if "human" in targets and from_agent != "auditor":
        raise AssertionError("Only Auditor may hand off a merge decision to human")

    for lineage in doc.get("revalidates", []):
        if lineage["from_revision"] >= doc["task_revision"]:
            raise AssertionError("Revalidated evidence must originate from an earlier task revision")
        if lineage["evidence_id"] in set(doc["evidence_ids"]):
            raise AssertionError("Revalidation must emit new evidence instead of reusing the historical evidence id")

    scope = doc["scope"]
    if scope == "HUMAN_DECISION" and (from_agent != "auditor" or targets != {"human"}):
        raise AssertionError("HUMAN_DECISION handoff must be exactly Auditor -> human")
    if scope != "HUMAN_DECISION" and "human" in targets:
        raise AssertionError("Only HUMAN_DECISION scope may target human")
    if scope == "LIFECYCLE_GOVERNANCE":
        lifecycle_agents = {"orchestrator", "analyst", "planner"}
        involved = {from_agent} | {target for target in targets if target != "human"}
        if not involved.issubset(lifecycle_agents):
            raise AssertionError("Lifecycle governance scope is restricted to Orchestrator, Analyst, and Planner")
    if scope == "TASK_PACKET_BOUNDARY":
        lifecycle_agents = {"orchestrator", "analyst", "planner"}
        if from_agent != "planner":
            raise AssertionError("TASK_PACKET_BOUNDARY must be produced by Planner")
        if targets & lifecycle_agents:
            raise AssertionError("TASK_PACKET_BOUNDARY cannot target lifecycle-governance agents")

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

    def require_completed_before(target: str, state_label: str) -> None:
        if target not in execution_order:
            raise AssertionError(f"{state_label} requires {target} in execution_order")
        target_index = execution_order.index(target)
        incomplete = {
            participant
            for participant in execution_order[:target_index]
            if participant != "orchestrator"
            and participants[participant] != "COMPLETED"
        }
        if incomplete:
            raise AssertionError(
                f"{state_label} cannot start before upstream participants complete: {sorted(incomplete)}"
            )

    state = doc["current_state"]
    if state in {"READY_FOR_QA", "VALIDATING"}:
        require_completed_before("qa", state)
        if participants["qa"] not in {"REQUIRED", "OPTIONAL"}:
            raise AssertionError(f"{state} requires active QA")
        if state == "VALIDATING" and current_agent != "qa":
            raise AssertionError("VALIDATING requires QA as current_agent")

    if state in {"READY_FOR_AUDIT", "AUDITING"}:
        require_completed_before("auditor", state)
        if participants["auditor"] not in {"REQUIRED", "OPTIONAL"}:
            raise AssertionError(f"{state} requires active Auditor")
        if state == "AUDITING" and current_agent != "auditor":
            raise AssertionError("AUDITING requires Auditor as current_agent")

    replanning = doc.get("replanning")
    if doc["current_state"] == "REPLANNING_REQUIRED":
        if not replanning:
            raise AssertionError("REPLANNING_REQUIRED requires replanning metadata")
        if replanning["previous_revision"] != doc["task"]["revision"]:
            raise AssertionError("REPLANNING_REQUIRED must reference the current task revision as previous_revision")
        freshness = replanning["evidence_freshness"]
        preserved = set(freshness["PRESERVED"])
        revalidate = set(freshness["REVALIDATE"])
        invalidated = set(freshness["INVALIDATED"])
        if preserved & revalidate or preserved & invalidated or revalidate & invalidated:
            raise AssertionError("Evidence freshness classes must be disjoint")
        declared_invalidations = set(replanning["invalidates"]) - {"PLAN"}
        if declared_invalidations != invalidated:
            raise AssertionError("INVALIDATED evidence must exactly match replanning invalidates")
        non_preservable = {"QA_EVIDENCE", "SECURITY_EVIDENCE", "AUDIT_EVIDENCE"}
        forbidden = preserved & non_preservable
        if forbidden:
            raise AssertionError(
                f"Independent verification evidence cannot be preserved across revisions: {sorted(forbidden)}"
            )
        rationale = replanning["preservation_rationale"]
        rationale_classes = [item["evidence_class"] for item in rationale]
        if len(rationale_classes) != len(set(rationale_classes)):
            raise AssertionError("Preservation rationale cannot duplicate evidence classes")
        if set(rationale_classes) != preserved:
            raise AssertionError("Every PRESERVED evidence class requires exactly one preservation rationale")
        if any(item["from_revision"] != replanning["previous_revision"] for item in rationale):
            raise AssertionError("Preserved evidence must identify the immediately previous revision")
        if agents["orchestrator"] != "REQUIRED":
            raise AssertionError("Replanning keeps Orchestrator active")
        if doc.get("current_agent") != "planner":
            raise AssertionError("REPLANNING_REQUIRED routes control to Planner")
        if "AUDIT_EVIDENCE" in replanning["invalidates"] and agents["auditor"] == "COMPLETED":
            raise AssertionError("Invalidated audit evidence cannot leave Auditor completed")
        if "QA_EVIDENCE" in replanning["invalidates"] and agents["qa"] == "COMPLETED":
            raise AssertionError("Invalidated QA evidence cannot leave QA completed")
        if "SECURITY_EVIDENCE" in replanning["invalidates"] and agents["security"] == "COMPLETED":
            raise AssertionError("Invalidated Security evidence cannot leave Security completed")
        if "DOCUMENTATION_EVIDENCE" in replanning["invalidates"] and agents["documentation"] == "COMPLETED":
            raise AssertionError("Invalidated Documentation evidence cannot leave Documentation completed")
        if "SPECIALIST_EVIDENCE" in replanning["invalidates"]:
            completed_specialists = [
                specialist
                for specialist, state in specialists.items()
                if state == "COMPLETED"
            ]
            if completed_specialists:
                raise AssertionError(
                    "Invalidated Specialist evidence cannot leave specialists completed: "
                    f"{sorted(completed_specialists)}"
                )
    elif replanning is not None:
        raise AssertionError("replanning metadata is only valid in REPLANNING_REQUIRED")

    executed_handoffs = set(doc["handoffs"])
    expected_handoffs = set(doc.get("expected_handoffs", []))
    overlap = executed_handoffs & expected_handoffs
    if overlap:
        raise AssertionError(
            f"Executed and expected handoff ledgers cannot overlap: {sorted(overlap)}"
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


DEPENDENCY_STATE_RANK = {
    "READY_FOR_IMPLEMENTATION": 1,
    "READY_FOR_QA": 2,
    "READY_FOR_AUDIT": 3,
    "READY_FOR_HUMAN_DECISION": 4,
    "CLOSED": 5,
}


def validate_revision_transition(
    previous: dict[str, Any],
    current: dict[str, Any],
) -> None:
    if previous["task"]["id"] != current["task"]["id"]:
        raise AssertionError("Revision transition must preserve task id")
    if current["task"]["revision"] != previous["task"]["revision"] + 1:
        raise AssertionError("Task revisions must advance exactly by one")
    if previous["current_state"] != "REPLANNING_REQUIRED":
        raise AssertionError("A new task revision requires predecessor REPLANNING_REQUIRED")
    replanning = previous.get("replanning")
    if not replanning or replanning["previous_revision"] != previous["task"]["revision"]:
        raise AssertionError("Previous revision lacks valid replanning provenance")


def validate_task_dependency_graph(tasks: list[dict[str, Any]]) -> None:
    graph = {
        task["task_id"]: [item["task_id"] for item in task["dependencies"]]
        for task in tasks
    }
    known = set(graph)

    for task_id, dependencies in graph.items():
        missing = [dependency for dependency in dependencies if dependency not in known]
        if missing:
            raise AssertionError(
                f"Task dependency graph references unknown tasks from {task_id}: {sorted(missing)}"
            )

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(task_id: str) -> None:
        if task_id in visiting:
            raise AssertionError(f"Task dependency cycle detected at {task_id}")
        if task_id in visited:
            return
        visiting.add(task_id)
        for dependency in graph[task_id]:
            visit(dependency)
        visiting.remove(task_id)
        visited.add(task_id)

    for task_id in graph:
        visit(task_id)


def validate_task_dependencies(
    task: dict[str, Any],
    predecessor_orchestrations: list[dict[str, Any]],
) -> None:
    predecessors = {
        item["task"]["id"]: item
        for item in predecessor_orchestrations
    }
    for dependency in task["dependencies"]:
        predecessor = predecessors.get(dependency["task_id"])
        if predecessor is None:
            raise AssertionError(
                f"Dependency predecessor orchestration not found: {dependency['task_id']}"
            )
        actual_state = predecessor["current_state"]
        if actual_state not in DEPENDENCY_STATE_RANK:
            raise AssertionError(
                f"Dependency predecessor {dependency['task_id']} has not reached an unlockable state: {actual_state}"
            )
        required_state = dependency["required_state"]
        if DEPENDENCY_STATE_RANK[actual_state] < DEPENDENCY_STATE_RANK[required_state]:
            raise AssertionError(
                f"Dependency predecessor {dependency['task_id']} is {actual_state}; requires {required_state}"
            )


def validate_task_packet_boundary(
    task: dict[str, Any],
    orchestration: dict[str, Any],
    handoff: dict[str, Any],
) -> None:
    lifecycle_agents = {"orchestrator", "analyst", "planner"}
    if handoff["scope"] != "TASK_PACKET_BOUNDARY":
        raise AssertionError("Planner execution admission must use TASK_PACKET_BOUNDARY")
    if handoff["from_agent"] != "planner" or handoff["status"] != "PLANNED":
        raise AssertionError("TASK_PACKET_BOUNDARY must be Planner-owned with PLANNED status")

    targets = set(handoff["to_agents"])
    if len(targets) != 1:
        raise AssertionError("TASK_PACKET_BOUNDARY must target exactly one first executor")
    if targets & lifecycle_agents or "human" in targets:
        raise AssertionError("TASK_PACKET_BOUNDARY may target only the first Task Packet executor")

    active = set(task["required_agents"]) | set(task["optional_agents"])
    if not targets.issubset(active):
        raise AssertionError("TASK_PACKET_BOUNDARY target must be active in Task Packet applicability")

    if handoff["task_id"] != task["task_id"] or handoff["task_revision"] != task["revision"]:
        raise AssertionError("TASK_PACKET_BOUNDARY must match Task Packet id and revision")

    if handoff["baseline"]["repository"] != orchestration["baseline"]["repository"]:
        raise AssertionError("TASK_PACKET_BOUNDARY repository must match orchestration baseline")
    if orchestration["baseline"].get("head_sha") is not None and handoff["baseline"]["head_sha"] != orchestration["baseline"]["head_sha"]:
        raise AssertionError("TASK_PACKET_BOUNDARY HEAD must match orchestration candidate HEAD")

    order = orchestration["execution_order"]
    if "planner" not in order:
        raise AssertionError("Planner must exist in execution_order before Task Packet execution")
    planner_index = order.index("planner")
    downstream = [
        participant
        for participant in order[planner_index + 1 :]
        if participant not in lifecycle_agents
    ]
    if not downstream:
        raise AssertionError("TASK_PACKET_BOUNDARY requires a downstream executor")
    first_executor = downstream[0]
    if targets != {first_executor}:
        raise AssertionError(
            f"TASK_PACKET_BOUNDARY must target the first downstream executor: {first_executor}"
        )
    if handoff["handoff_id"] not in set(orchestration["handoffs"]):
        raise AssertionError("Orchestration must record the TASK_PACKET_BOUNDARY handoff")


def validate_protocol_chain(
    task: dict[str, Any],
    orchestration: dict[str, Any],
    handoff_docs: list[dict[str, Any]],
) -> None:
    if task["task_id"] != orchestration["task"]["id"]:
        raise AssertionError("Task Packet and orchestration task ids must match")
    if task["revision"] != orchestration["task"]["revision"]:
        raise AssertionError("Task Packet and orchestration task revisions must match")

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
    lifecycle_agents = {"orchestrator", "analyst", "planner"}
    task_handoffs = [item for item in handoff_docs if item["task_id"] == task["task_id"]]
    boundaries = [item for item in task_handoffs if item["scope"] == "TASK_PACKET_BOUNDARY"]
    if len(boundaries) != 1:
        raise AssertionError(
            f"Exactly one TASK_PACKET_BOUNDARY is required before bounded execution; found {len(boundaries)}"
        )
    validate_task_packet_boundary(task, orchestration, boundaries[0])

    for item in handoff_docs:
        if item["task_id"] != task["task_id"]:
            continue
        scope = item["scope"]
        producer = item["from_agent"]
        targets = set(item["to_agents"])

        if scope == "LIFECYCLE_GOVERNANCE":
            involved_agents = {producer} | {target for target in targets if target != "human"}
            if not involved_agents.issubset(lifecycle_agents):
                raise AssertionError(
                    "LIFECYCLE_GOVERNANCE handoff may only involve Orchestrator, Analyst, and Planner"
                )
            if "human" in targets:
                raise AssertionError("Lifecycle governance cannot cross the human decision boundary")
        elif scope == "TASK_PACKET_BOUNDARY":
            validate_task_packet_boundary(task, orchestration, item)
        elif scope == "TASK_EXECUTION":
            involved = {producer} | {target for target in targets if target != "human"}
            lifecycle_involved = involved & lifecycle_agents
            if lifecycle_involved:
                raise AssertionError(
                    f"TASK_EXECUTION cannot include lifecycle-governance agents: {sorted(lifecycle_involved)}"
                )
            undeclared = {participant for participant in involved if participant not in declared}
            if undeclared:
                raise AssertionError(
                    f"TASK_EXECUTION handoff uses participants outside Task Packet applicability: {sorted(undeclared)}"
                )
            if "human" in targets:
                raise AssertionError("TASK_EXECUTION cannot target human")
        elif scope == "HUMAN_DECISION":
            if producer != "auditor" or targets != {"human"}:
                raise AssertionError("HUMAN_DECISION must be exactly Auditor -> human")
        else:
            raise AssertionError(f"Unknown handoff scope: {scope}")

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
        if item["task_revision"] != orchestration["task"]["revision"]:
            raise AssertionError(
                f"Handoff {handoff_id} belongs to stale task revision {item['task_revision']}, expected {orchestration['task']['revision']}"
            )
        if item["baseline"]["repository"] != repository:
            raise AssertionError(
                f"Handoff {handoff_id} repository does not match orchestration baseline"
            )
        if head_sha is not None and item["baseline"]["head_sha"] != head_sha:
            raise AssertionError(
                f"Handoff {handoff_id} HEAD does not match orchestration candidate HEAD"
            )

    participants = {**orchestration["agents"], **orchestration.get("specialists", {})}
    for participant, applicability in participants.items():
        if participant == "orchestrator" or applicability != "COMPLETED":
            continue
        completion_docs = [
            item
            for item in actual_by_id.values()
            if item["handoff_id"] in declared_ids
            and item["from_agent"] == participant
            and item["status"] not in NON_COMPLETION_STATUSES
        ]
        if not completion_docs:
            raise AssertionError(
                f"COMPLETED participant lacks successful declared handoff evidence: {participant}"
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

    analyst_handoff = validate_schema(
        "schemas/agent-handoff.schema.json",
        "templates/analyst-planner-handoff.example.yaml",
    )
    validate_handoff(analyst_handoff)
    print("PASS Analyst to Planner completion handoff contract")

    boundary_handoff = validate_schema(
        "schemas/agent-handoff.schema.json",
        "templates/planner-task-packet-boundary-handoff.example.yaml",
    )
    validate_handoff(boundary_handoff)
    print("PASS Planner Task Packet boundary handoff contract")

    chain_handoffs = [analyst_handoff, boundary_handoff, handoff]
    evidence_orchestration = copy.deepcopy(orchestration)
    evidence_orchestration["handoffs"] = [
        item["handoff_id"] for item in chain_handoffs
    ]
    validate_protocol_chain(task, evidence_orchestration, chain_handoffs)
    print("PASS completed participants are backed by declared handoff evidence")

    missing_boundary = copy.deepcopy(evidence_orchestration)
    missing_boundary["handoffs"] = [
        analyst_handoff["handoff_id"],
        handoff["handoff_id"],
    ]
    expect_failure(
        "bounded execution cannot start without exactly one Task Packet boundary",
        lambda: validate_protocol_chain(
            task,
            missing_boundary,
            [analyst_handoff, handoff],
        ),
    )

    missing_completion_evidence = copy.deepcopy(evidence_orchestration)
    missing_completion_evidence["handoffs"] = [
        boundary_handoff["handoff_id"],
        handoff["handoff_id"],
    ]
    expect_failure(
        "COMPLETED Analyst requires declared successful handoff evidence",
        lambda: validate_orchestration_handoffs(
            missing_completion_evidence,
            chain_handoffs,
        ),
    )

    failed_completion = copy.deepcopy(analyst_handoff)
    failed_completion["status"] = "BLOCKED"
    expect_failure(
        "blocking handoff cannot prove a COMPLETED participant",
        lambda: validate_orchestration_handoffs(
            evidence_orchestration,
            [failed_completion, boundary_handoff, handoff],
        ),
    )

    wrong_boundary = copy.deepcopy(boundary_handoff)
    wrong_boundary["to_agents"] = ["qa"]
    expect_failure(
        "Task Packet boundary cannot skip the first downstream executor",
        lambda: validate_protocol_chain(
            task,
            evidence_orchestration,
            [analyst_handoff, wrong_boundary, handoff],
        ),
    )

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

    previous_revision = copy.deepcopy(orchestration)
    previous_revision["current_state"] = "REPLANNING_REQUIRED"
    previous_revision["current_agent"] = "planner"
    previous_revision["agents"]["planner"] = "REQUIRED"
    previous_revision["replanning"] = {
        "reason": "REQUIREMENT_CHANGED",
        "invalidates": ["PLAN"],
        "previous_revision": previous_revision["task"]["revision"],
        "previous_baseline": copy.deepcopy(previous_revision["baseline"]),
        "evidence_freshness": {
            "PRESERVED": ["DOCUMENTATION_EVIDENCE"],
            "REVALIDATE": ["IMPLEMENTATION_EVIDENCE"],
            "INVALIDATED": [],
        },
        "preservation_rationale": [
            {
                "evidence_class": "DOCUMENTATION_EVIDENCE",
                "from_revision": previous_revision["task"]["revision"],
                "reason": "Documentation remains outside the changed planning premise.",
            }
        ],
    }
    current_revision = copy.deepcopy(orchestration)
    current_revision["task"]["revision"] = previous_revision["task"]["revision"] + 1
    validate_revision_transition(previous_revision, current_revision)
    print("PASS task revision advances monotonically from governed replanning")

    skipped_revision = copy.deepcopy(current_revision)
    skipped_revision["task"]["revision"] += 1
    expect_failure(
        "task revision cannot skip a generation",
        lambda: validate_revision_transition(previous_revision, skipped_revision),
    )

    expect_failure(
        "task revision cannot advance without governed replanning",
        lambda: validate_revision_transition(orchestration, current_revision),
    )

    graph_a = copy.deepcopy(task)
    graph_a["task_id"] = "BP-GRAPH-001"
    graph_a["dependencies"] = []
    graph_b = copy.deepcopy(task)
    graph_b["task_id"] = "BP-GRAPH-002"
    graph_b["dependencies"] = [
        {"task_id": "BP-GRAPH-001", "required_state": "READY_FOR_IMPLEMENTATION"}
    ]
    validate_task_dependency_graph([graph_a, graph_b])
    print("PASS task dependency graph is acyclic and closed")

    cyclic_a = copy.deepcopy(graph_a)
    cyclic_a["dependencies"] = [
        {"task_id": "BP-GRAPH-002", "required_state": "READY_FOR_IMPLEMENTATION"}
    ]
    expect_failure(
        "task dependency graph cannot contain cycles",
        lambda: validate_task_dependency_graph([cyclic_a, graph_b]),
    )

    unknown_dependency = copy.deepcopy(graph_b)
    unknown_dependency["dependencies"] = [
        {"task_id": "BP-MISSING-999", "required_state": "READY_FOR_IMPLEMENTATION"}
    ]
    expect_failure(
        "task dependency graph cannot reference unknown predecessor tasks",
        lambda: validate_task_dependency_graph([graph_a, unknown_dependency]),
    )

    predecessor = copy.deepcopy(orchestration)
    predecessor["task"]["id"] = "BP-PREV-001"
    predecessor["current_state"] = "READY_FOR_AUDIT"
    dependency_task = copy.deepcopy(task)
    dependency_task["dependencies"] = [
        {"task_id": "BP-PREV-001", "required_state": "READY_FOR_QA"}
    ]
    validate_task_dependencies(dependency_task, [predecessor])
    print("PASS inter-task dependency state satisfaction")

    expect_failure(
        "task dependency requires predecessor orchestration evidence",
        lambda: validate_task_dependencies(dependency_task, []),
    )

    immature_predecessor = copy.deepcopy(predecessor)
    immature_predecessor["current_state"] = "IMPLEMENTING"
    expect_failure(
        "task dependency cannot unlock from immature predecessor state",
        lambda: validate_task_dependencies(dependency_task, [immature_predecessor]),
    )

    dependency_task["dependencies"][0]["required_state"] = "READY_FOR_HUMAN_DECISION"
    expect_failure(
        "task dependency cannot unlock below required predecessor state",
        lambda: validate_task_dependencies(dependency_task, [predecessor]),
    )

    mutated = copy.deepcopy(task)
    mutated["dependencies"] = [
        {"task_id": "BP-PREV-001", "required_state": "READY_FOR_QA"},
        {"task_id": "BP-PREV-001", "required_state": "CLOSED"},
    ]
    expect_failure(
        "task dependencies cannot duplicate predecessor task",
        lambda: validate_task_packet(mutated),
    )

    mutated = copy.deepcopy(task)
    mutated["not_applicable_agents"].append("qa")
    expect_failure(
        "task applicability sets are disjoint",
        lambda: validate_task_packet(mutated),
    )

    mutated = copy.deepcopy(task)
    mutated["dependencies"].append(
        {"task_id": mutated["task_id"], "required_state": "CLOSED"}
    )
    expect_failure(
        "task cannot depend on itself",
        lambda: validate_task_packet(mutated),
    )

    revalidated_handoff = copy.deepcopy(handoff)
    revalidated_handoff["task_revision"] = 2
    revalidated_handoff["evidence_ids"] = ["EVD-CART-FRONTEND-TESTS-R2"]
    revalidated_handoff["revalidates"] = [
        {"evidence_id": "EVD-CART-FRONTEND-TESTS", "from_revision": 1}
    ]
    validate_handoff(revalidated_handoff)
    print("PASS revalidated evidence preserves lineage and emits fresh evidence")

    mutated = copy.deepcopy(revalidated_handoff)
    mutated["revalidates"][0]["from_revision"] = 2
    expect_failure(
        "revalidation evidence must come from an earlier revision",
        lambda: validate_handoff(mutated),
    )

    mutated = copy.deepcopy(revalidated_handoff)
    mutated["evidence_ids"] = ["EVD-CART-FRONTEND-TESTS"]
    expect_failure(
        "revalidation cannot recycle the historical evidence id",
        lambda: validate_handoff(mutated),
    )

    lifecycle_handoff = copy.deepcopy(handoff)
    lifecycle_handoff["handoff_id"] = "HO-BP-CART-001-ANALYST-PLANNER"
    lifecycle_handoff["scope"] = "LIFECYCLE_GOVERNANCE"
    lifecycle_handoff["from_agent"] = "analyst"
    lifecycle_handoff["to_agents"] = ["planner"]
    lifecycle_handoff["status"] = "ANALYZED"
    lifecycle_handoff["evidence_ids"] = []
    validate_handoff(lifecycle_handoff)
    print("PASS Analyst -> Planner lifecycle governance handoff")

    mutated = copy.deepcopy(lifecycle_handoff)
    mutated["to_agents"] = ["frontend"]
    expect_failure(
        "lifecycle governance cannot contain task execution participants",
        lambda: validate_handoff(mutated),
    )

    mutated = copy.deepcopy(handoff)
    mutated["scope"] = "HUMAN_DECISION"
    expect_failure(
        "human decision scope is reserved for Auditor -> human",
        lambda: validate_handoff(mutated),
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

    replanning = copy.deepcopy(orchestration)
    replanning["current_state"] = "REPLANNING_REQUIRED"
    replanning["current_agent"] = "planner"
    replanning["replanning"] = {
        "reason": "BASELINE_CHANGED",
        "invalidates": ["PLAN", "QA_EVIDENCE"],
        "previous_revision": orchestration["task"]["revision"],
        "previous_baseline": copy.deepcopy(orchestration["baseline"]),
        "evidence_freshness": {
            "PRESERVED": ["DOCUMENTATION_EVIDENCE"],
            "REVALIDATE": ["IMPLEMENTATION_EVIDENCE"],
            "INVALIDATED": ["QA_EVIDENCE"],
        },
        "preservation_rationale": [
            {
                "evidence_class": "DOCUMENTATION_EVIDENCE",
                "from_revision": orchestration["task"]["revision"],
                "reason": "Documentation remains factually unchanged by this replanning trigger.",
            }
        ],
    }
    replanning["agents"]["planner"] = "REQUIRED"
    replanning["agents"]["qa"] = "REQUIRED"
    validate_orchestration(replanning)
    print("PASS governed replanning invalidates stale evidence")

    mutated = copy.deepcopy(replanning)
    mutated["replanning"]["preservation_rationale"] = []
    expect_failure(
        "preserved evidence requires explicit rationale",
        lambda: validate_orchestration(mutated),
    )

    mutated = copy.deepcopy(replanning)
    mutated["replanning"]["preservation_rationale"][0]["from_revision"] -= 1
    expect_failure(
        "preserved evidence must identify its exact source revision",
        lambda: validate_orchestration(mutated),
    )

    mutated = copy.deepcopy(replanning)
    mutated["replanning"]["evidence_freshness"]["PRESERVED"].append("QA_EVIDENCE")
    expect_failure(
        "evidence freshness classifications cannot overlap",
        lambda: validate_orchestration(mutated),
    )

    mutated = copy.deepcopy(replanning)
    mutated["replanning"]["evidence_freshness"]["INVALIDATED"] = []
    expect_failure(
        "declared invalidation must match INVALIDATED freshness evidence",
        lambda: validate_orchestration(mutated),
    )

    mutated = copy.deepcopy(replanning)
    mutated["replanning"]["evidence_freshness"]["PRESERVED"].append("AUDIT_EVIDENCE")
    expect_failure(
        "audit verdict cannot survive into a new task revision",
        lambda: validate_orchestration(mutated),
    )

    mutated = copy.deepcopy(replanning)
    mutated["replanning"]["previous_revision"] = replanning["task"]["revision"] - 1
    expect_failure(
        "replanning must originate from the current governed revision",
        lambda: validate_orchestration(mutated),
    )

    mutated = copy.deepcopy(replanning)
    mutated["replanning"] = None
    expect_failure(
        "replanning state requires explicit invalidation metadata",
        lambda: validate_orchestration(mutated),
    )

    mutated = copy.deepcopy(replanning)
    mutated["current_agent"] = "qa"
    expect_failure(
        "replanning routes control back to Planner",
        lambda: validate_orchestration(mutated),
    )

    mutated = copy.deepcopy(replanning)
    mutated["agents"]["qa"] = "COMPLETED"
    expect_failure(
        "invalidated QA evidence cannot remain completed",
        lambda: validate_orchestration(mutated),
    )

    documentation_replanning = copy.deepcopy(replanning)
    documentation_replanning["replanning"]["invalidates"] = ["PLAN", "DOCUMENTATION_EVIDENCE"]
    documentation_replanning["replanning"]["evidence_freshness"]["PRESERVED"] = []
    documentation_replanning["replanning"]["evidence_freshness"]["INVALIDATED"] = ["DOCUMENTATION_EVIDENCE"]
    documentation_replanning["replanning"]["preservation_rationale"] = []
    documentation_replanning["agents"]["documentation"] = "REQUIRED"
    if "documentation" not in documentation_replanning["execution_order"]:
        documentation_replanning["execution_order"].insert(
            documentation_replanning["execution_order"].index("auditor"), "documentation"
        )
    validate_orchestration(documentation_replanning)
    print("PASS Documentation evidence can be invalidated coherently")

    mutated = copy.deepcopy(documentation_replanning)
    mutated["agents"]["documentation"] = "COMPLETED"
    expect_failure(
        "invalidated Documentation evidence cannot remain completed",
        lambda: validate_orchestration(mutated),
    )

    specialist_replanning = copy.deepcopy(specialist_orchestration)
    specialist_replanning["current_state"] = "REPLANNING_REQUIRED"
    specialist_replanning["current_agent"] = "planner"
    specialist_replanning["agents"]["planner"] = "REQUIRED"
    specialist_replanning["specialists"]["specialist:search-ai-discoverability"] = "REQUIRED"
    specialist_replanning["replanning"] = {
        "reason": "BASELINE_CHANGED",
        "invalidates": ["PLAN", "SPECIALIST_EVIDENCE"],
        "previous_revision": specialist_replanning["task"]["revision"],
        "previous_baseline": copy.deepcopy(specialist_replanning["baseline"]),
        "evidence_freshness": {
            "PRESERVED": [],
            "REVALIDATE": [],
            "INVALIDATED": ["SPECIALIST_EVIDENCE"],
        },
        "preservation_rationale": [],
    }
    validate_orchestration(specialist_replanning)
    print("PASS Specialist evidence can be invalidated coherently")

    mutated = copy.deepcopy(specialist_replanning)
    mutated["specialists"]["specialist:search-ai-discoverability"] = "COMPLETED"
    expect_failure(
        "invalidated Specialist evidence cannot remain completed",
        lambda: validate_orchestration(mutated),
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

    validating_with_incomplete_upstream = copy.deepcopy(orchestration)
    validating_with_incomplete_upstream["agents"]["frontend"] = "REQUIRED"
    expect_failure(
        "VALIDATING cannot begin while an upstream executor remains incomplete",
        lambda: validate_orchestration(validating_with_incomplete_upstream),
    )

    validating_wrong_owner = copy.deepcopy(orchestration)
    validating_wrong_owner["current_agent"] = "auditor"
    expect_failure(
        "VALIDATING is owned by QA",
        lambda: validate_orchestration(validating_wrong_owner),
    )

    ready_for_audit = copy.deepcopy(orchestration)
    ready_for_audit["current_state"] = "READY_FOR_AUDIT"
    ready_for_audit["current_agent"] = "auditor"
    ready_for_audit["agents"]["qa"] = "COMPLETED"
    validate_orchestration(ready_for_audit)
    print("PASS READY_FOR_AUDIT requires completed upstream execution")

    premature_audit = copy.deepcopy(ready_for_audit)
    premature_audit["agents"]["qa"] = "REQUIRED"
    expect_failure(
        "READY_FOR_AUDIT cannot skip incomplete QA",
        lambda: validate_orchestration(premature_audit),
    )

    auditing = copy.deepcopy(ready_for_audit)
    auditing["current_state"] = "AUDITING"
    validate_orchestration(auditing)
    print("PASS AUDITING starts only after upstream completion")

    auditing_wrong_owner = copy.deepcopy(auditing)
    auditing_wrong_owner["current_agent"] = "qa"
    expect_failure(
        "AUDITING is owned by Auditor",
        lambda: validate_orchestration(auditing_wrong_owner),
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

    lifecycle_chain_handoff = copy.deepcopy(lifecycle_handoff)
    lifecycle_chain_handoff["task_id"] = task["task_id"]
    lifecycle_chain_handoff["task_revision"] = task["revision"]
    lifecycle_chain_handoff["baseline"] = copy.deepcopy(handoff["baseline"])
    lifecycle_orchestration = copy.deepcopy(evidence_orchestration)
    lifecycle_orchestration["handoffs"] = [
        lifecycle_chain_handoff["handoff_id"],
        boundary_handoff["handoff_id"],
        handoff["handoff_id"],
    ]
    validate_protocol_chain(
        task,
        lifecycle_orchestration,
        [lifecycle_chain_handoff, boundary_handoff, handoff],
    )
    print("PASS lifecycle governance remains distinct from the Task Packet boundary")

    mutated_handoff = copy.deepcopy(lifecycle_chain_handoff)
    mutated_handoff["scope"] = "TASK_EXECUTION"
    expect_failure(
        "Analyst and Planner cannot masquerade as Task Packet executors",
        lambda: validate_protocol_chain(
            task,
            lifecycle_orchestration,
            [mutated_handoff, boundary_handoff, handoff],
        ),
    )

    mutated_task = copy.deepcopy(task)
    mutated_task["task_id"] = "BP-OTHER-999"
    expect_failure(
        "Task Packet and orchestration must describe the same task",
        lambda: validate_protocol_chain(
            mutated_task,
            evidence_orchestration,
            chain_handoffs,
        ),
    )

    mutated_task = copy.deepcopy(task)
    mutated_task["revision"] += 1
    expect_failure(
        "Task Packet and orchestration revisions must match",
        lambda: validate_protocol_chain(
            mutated_task,
            evidence_orchestration,
            chain_handoffs,
        ),
    )

    stale_handoff = copy.deepcopy(handoff)
    stale_handoff["task_revision"] += 1
    expect_failure(
        "handoff evidence from another task revision is stale",
        lambda: validate_orchestration_handoffs(
            evidence_orchestration,
            [analyst_handoff, boundary_handoff, stale_handoff],
        ),
    )

    mutated_task = copy.deepcopy(task)
    mutated_task["baseline"]["base_sha"] = "7654321"
    expect_failure(
        "Task Packet and orchestration must share the same baseline",
        lambda: validate_protocol_chain(
            mutated_task,
            evidence_orchestration,
            chain_handoffs,
        ),
    )

    mutated_task = copy.deepcopy(task)
    mutated_task["required_agents"].append("backend")
    mutated_task["not_applicable_agents"].remove("backend")
    expect_failure(
        "required Task Packet participant cannot be N/A in orchestration",
        lambda: validate_protocol_chain(
            mutated_task,
            evidence_orchestration,
            chain_handoffs,
        ),
    )

    mutated = copy.deepcopy(evidence_orchestration)
    mutated["handoffs"].append("HO-BP-CART-001-FAKE")
    expect_failure(
        "orchestration cannot reference nonexistent handoff evidence",
        lambda: validate_orchestration_handoffs(
            mutated,
            chain_handoffs,
        ),
    )

    mutated_handoff = copy.deepcopy(handoff)
    mutated_handoff["task_id"] = "BP-OTHER-999"
    expect_failure(
        "handoff evidence must belong to orchestration task",
        lambda: validate_orchestration_handoffs(
            evidence_orchestration,
            [analyst_handoff, boundary_handoff, mutated_handoff],
        ),
    )

    mutated_orchestration = copy.deepcopy(evidence_orchestration)
    mutated_orchestration["execution_order"].remove("frontend")
    mutated_orchestration["execution_order"].insert(
        mutated_orchestration["execution_order"].index("qa") + 1, "frontend"
    )
    expect_failure(
        "handoff producer must precede its consumer in execution order",
        lambda: validate_protocol_chain(
            task,
            mutated_orchestration,
            chain_handoffs,
        ),
    )

    mutated_handoff = copy.deepcopy(handoff)
    mutated_handoff["baseline"]["head_sha"] = "7654321"
    expect_failure(
        "handoff evidence must match orchestration candidate HEAD",
        lambda: validate_orchestration_handoffs(
            evidence_orchestration,
            [analyst_handoff, boundary_handoff, mutated_handoff],
        ),
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
