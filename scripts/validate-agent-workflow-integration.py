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

CORE_AGENTS = {
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
}

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


def is_participant(value: str) -> bool:
    return value in CORE_AGENTS or bool(SPECIALIST_ID.fullmatch(value))


def allowed_statuses(agent: str) -> set[str]:
    if agent in ROLE_STATUSES:
        return ROLE_STATUSES[agent]
    if SPECIALIST_ID.fullmatch(agent):
        return SPECIALIST_STATUSES
    raise AssertionError(f"Unknown participant id: {agent}")


PRE_IMPLEMENTATION_GATES = {
    "brownfield_baseline",
    "requirements_ready",
    "interface_scope_ready",
    "architecture_ready",
    "api_contract_ready",
    "interface_inventory_ready",
    "design_system_ready",
    "client_architecture_ready",
}

IMPLEMENTATION_COMPLETION_STATUSES = {
    "BACKEND_IMPLEMENTED",
    "FRONTEND_IMPLEMENTED",
}


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


def stable_phase_sequences() -> dict[str, list[str]]:
    return {
        "greenfield": load("workflows/greenfield.yaml")["sequence"],
        "brownfield": load("workflows/brownfield.yaml")["sequence"],
    }


def stable_gate_ids() -> set[str]:
    return {item["id"] for item in load("catalog/gates.yaml")["gates"]}


def validate_phase_bindings(overlay: dict[str, Any]) -> None:
    sequences = stable_phase_sequences()
    bindings = overlay["workflow_bindings"]

    for mode, stable_sequence in sequences.items():
        phase_agents = bindings[mode]["phase_agents"]
        actual = set(phase_agents)
        expected = set(stable_sequence)

        missing = expected - actual
        extra = actual - expected
        if missing or extra:
            raise AssertionError(
                f"{mode} phase coverage mismatch: missing={sorted(missing)} extra={sorted(extra)}"
            )

        if len(phase_agents) != len(stable_sequence):
            raise AssertionError(
                f"{mode} phase mapping count differs from stable sequence"
            )

        for phase, binding in phase_agents.items():
            required = set(binding["required_agents"])
            optional = set(binding["optional_agents"])
            if not required:
                raise AssertionError(f"{mode}:{phase} must have at least one required agent")
            overlap = required & optional
            if overlap:
                raise AssertionError(
                    f"{mode}:{phase} agent sets overlap: {sorted(overlap)}"
                )
            unknown = {
                participant
                for participant in (required | optional)
                if not is_participant(participant)
            }
            if unknown:
                raise AssertionError(
                    f"{mode}:{phase} references unknown agents: {sorted(unknown)}"
                )


def validate_cross_cutting_roles(overlay: dict[str, Any]) -> None:
    roles = overlay["cross_cutting_roles"]
    for key, config in roles.items():
        if config["agent"] != key:
            raise AssertionError(
                f"Cross-cutting role key {key} must bind to agent {key}"
            )
        if config["substitutes_stable_phase"] is not False:
            raise AssertionError(
                f"Cross-cutting role {key} cannot substitute a stable phase"
            )


def validate_gate_bindings(overlay: dict[str, Any]) -> None:
    expected = stable_gate_ids()
    bindings = overlay["gate_bindings"]
    actual = set(bindings)

    missing = expected - actual
    extra = actual - expected
    if missing or extra:
        raise AssertionError(
            f"Gate coverage mismatch: missing={sorted(missing)} extra={sorted(extra)}"
        )

    for gate_id, binding in bindings.items():
        required_pairs = {
            (item["agent"], item["status"])
            for item in binding["required_role_evidence"]
        }
        conditional_pairs = {
            (item["agent"], item["status"])
            for item in binding["conditional_role_evidence"]
        }
        overlap = required_pairs & conditional_pairs
        if overlap:
            raise AssertionError(
                f"Gate {gate_id} duplicates role evidence: {sorted(overlap)}"
            )

        for item in (
            binding["required_role_evidence"]
            + binding["conditional_role_evidence"]
        ):
            agent = item["agent"]
            status = item["status"]
            if status not in allowed_statuses(agent):
                raise AssertionError(
                    f"Gate {gate_id} assigns status {status} to wrong role {agent}"
                )
            if (
                gate_id in PRE_IMPLEMENTATION_GATES
                and status in IMPLEMENTATION_COMPLETION_STATUSES
            ):
                raise AssertionError(
                    f"Pre-implementation gate {gate_id} cannot require {status}"
                )

        if binding["substitutes_stable_checks"] is not False:
            raise AssertionError(
                f"Gate {gate_id} cannot substitute stable checks"
            )
        if binding["human_decision_preserved"] is not True:
            raise AssertionError(
                f"Gate {gate_id} must preserve human decision boundaries"
            )


def validate_state_model(overlay: dict[str, Any]) -> None:
    state = overlay["state_model"]
    if state["blueprint_status_authority"] != "project.artifact_locations.status":
        raise AssertionError(
            "Blueprint status authority must remain the project-declared status artifact"
        )
    if state["orchestration_state_authority"] != "task_coordination_only":
        raise AssertionError("Orchestration state must be task coordination only")
    if state["no_state_substitution"] is not True:
        raise AssertionError("Agent state cannot substitute Blueprint status")


def validate_adoption(doc: dict[str, Any]) -> None:
    locations = doc["artifact_locations"]
    values = list(locations.values())
    if len(values) != len(set(values)):
        raise AssertionError("Agent artifact locations must be distinct")

    for key, value in locations.items():
        if not value.startswith(".blueprint/agents/"):
            raise AssertionError(
                f"Agent artifact location {key} must stay under .blueprint/agents/: {value}"
            )

    if not locations["orchestration_state"].endswith((".yaml", ".yml")):
        raise AssertionError("orchestration_state must be a YAML artifact")

    policies = doc["policies"]
    if policies["automatic_consumer_upgrade"] is not False:
        raise AssertionError("Automatic consumer upgrade is forbidden")
    if policies["implementer_self_certification"] is not False:
        raise AssertionError("Implementer self-certification is forbidden")
    if policies["auditor_merge_authority"] is not False:
        raise AssertionError("Auditor cannot receive merge authority")
    if policies["agent_state_substitutes_blueprint_status"] is not False:
        raise AssertionError("Agent state cannot replace Blueprint status")
    if policies["human_merge_approval"] is not True:
        raise AssertionError("Human merge approval must remain explicit")


def expect_failure(label: str, action: Callable[[], None]) -> None:
    try:
        action()
    except AssertionError:
        print(f"PASS negative guard: {label}")
        return
    raise AssertionError(f"Negative guard did not fail: {label}")


def main() -> int:
    overlay = validate_schema(
        "schemas/agent-workflow-integration.schema.json",
        "catalog/agent-workflow-integration.proposal.yaml",
    )
    adoption = validate_schema(
        "schemas/project-agent-protocol-adoption.schema.json",
        "templates/project-agent-protocol-adoption.example.yaml",
    )

    validate_phase_bindings(overlay)
    print("PASS integration: exact Greenfield/Brownfield phase coverage")

    validate_cross_cutting_roles(overlay)
    print("PASS integration: cross-cutting role ownership")

    validate_gate_bindings(overlay)
    print("PASS integration: exact stable gate coverage and role/status ownership")

    validate_state_model(overlay)
    print("PASS integration: Blueprint/orchestration state separation")

    validate_adoption(adoption)
    print("PASS integration: consumer opt-in artifact and policy boundary")

    mutated = copy.deepcopy(overlay)
    del mutated["workflow_bindings"]["greenfield"]["phase_agents"]["requirements_domain"]
    expect_failure(
        "missing stable phase is rejected",
        lambda: validate_phase_bindings(mutated),
    )

    mutated = copy.deepcopy(overlay)
    mutated["workflow_bindings"]["greenfield"]["phase_agents"]["requirements_domain"][
        "optional_agents"
    ].append("analyst")
    expect_failure(
        "phase required/optional overlap is rejected",
        lambda: validate_phase_bindings(mutated),
    )

    mutated = copy.deepcopy(overlay)
    mutated["gate_bindings"]["unknown_gate"] = copy.deepcopy(
        mutated["gate_bindings"]["requirements_ready"]
    )
    expect_failure(
        "unknown gate binding is rejected",
        lambda: validate_gate_bindings(mutated),
    )

    mutated = copy.deepcopy(overlay)
    mutated["gate_bindings"]["requirements_ready"]["conditional_role_evidence"].append(
        {"agent": "frontend", "status": "FRONTEND_IMPLEMENTED"}
    )
    expect_failure(
        "pre-implementation gate cannot require implementation completion",
        lambda: validate_gate_bindings(mutated),
    )

    mutated = copy.deepcopy(overlay)
    mutated["gate_bindings"]["api_implemented"]["required_role_evidence"][0] = {
        "agent": "qa",
        "status": "BACKEND_IMPLEMENTED",
    }
    expect_failure(
        "gate status must belong to declared role",
        lambda: validate_gate_bindings(mutated),
    )

    mutated = copy.deepcopy(adoption)
    mutated["artifact_locations"]["handoffs_root"] = "handoffs"
    expect_failure(
        "consumer agent artifacts must remain under .blueprint/agents",
        lambda: validate_adoption(mutated),
    )

    mutated = copy.deepcopy(adoption)
    mutated["policies"]["auditor_merge_authority"] = True
    expect_failure(
        "Auditor merge authority is rejected",
        lambda: validate_adoption(mutated),
    )

    print("Blueprint agent workflow integration proposal validation: PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise
