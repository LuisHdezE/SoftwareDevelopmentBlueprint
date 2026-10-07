#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
PROTOCOL = ROOT / "scripts" / "validate-agent-protocol.py"

spec = importlib.util.spec_from_file_location("blueprint_agent_protocol", PROTOCOL)
if spec is None or spec.loader is None:
    raise RuntimeError("Cannot load canonical Blueprint agent protocol validator")
protocol = importlib.util.module_from_spec(spec)
spec.loader.exec_module(protocol)

task = protocol.validate_schema(
    "schemas/task-packet.schema.json",
    "pilots/R12/task-packet.yaml",
)
protocol.validate_task_packet(task)

orchestration = protocol.validate_schema(
    "schemas/orchestration-state.schema.json",
    "pilots/R12/orchestration.yaml",
)
protocol.validate_orchestration(orchestration)

handoff_paths = [
    "pilots/R12/handoffs/01-analyst-planner.yaml",
    "pilots/R12/handoffs/02-planner-documentation.yaml",
    "pilots/R12/handoffs/03-documentation-qa.yaml",
    "pilots/R12/handoffs/04-qa-auditor.yaml",
    "pilots/R12/handoffs/05-auditor-human.yaml",
]
handoffs = []
for path in handoff_paths:
    handoff = protocol.validate_schema("schemas/agent-handoff.schema.json", path)
    protocol.validate_handoff(handoff)
    handoffs.append(handoff)

protocol.validate_protocol_chain(task, orchestration, handoffs)

print("R12 real multi-agent pilot protocol validation: PASS")
print("Candidate: PR #70 @ 105391b1254cef18f43d122aa6174227463925a2")
print("Evidence plane: governance/evidence/r12-agent-protocol-readme")
print("State: READY_FOR_HUMAN_DECISION")
