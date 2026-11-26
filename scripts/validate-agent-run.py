#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
PROTOCOL_PATH = ROOT / "scripts" / "validate-agent-protocol.py"


def load_protocol():
    spec = importlib.util.spec_from_file_location("blueprint_agent_protocol", PROTOCOL_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Cannot load canonical Blueprint agent protocol validator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def relative_to_root(path: pathlib.Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError as exc:
        raise AssertionError(
            f"Agent run bundle must live inside the repository root: {path}"
        ) from exc


def validate_run(run_dir: pathlib.Path) -> None:
    protocol = load_protocol()
    task_path = run_dir / "task-packet.yaml"
    orchestration_path = run_dir / "orchestration.yaml"
    handoff_dir = run_dir / "handoffs"

    if not task_path.is_file():
        raise AssertionError(f"Missing task packet: {task_path}")
    if not orchestration_path.is_file():
        raise AssertionError(f"Missing orchestration state: {orchestration_path}")
    if not handoff_dir.is_dir():
        raise AssertionError(f"Missing handoff directory: {handoff_dir}")

    handoff_paths = sorted(handoff_dir.glob("*.yaml"))
    if not handoff_paths:
        raise AssertionError(f"No handoff documents found in: {handoff_dir}")

    task = protocol.validate_schema(
        "schemas/task-packet.schema.json",
        relative_to_root(task_path),
    )
    protocol.validate_task_packet(task)

    orchestration = protocol.validate_schema(
        "schemas/orchestration-state.schema.json",
        relative_to_root(orchestration_path),
    )
    protocol.validate_orchestration(orchestration)

    handoffs = []
    for path in handoff_paths:
        handoff = protocol.validate_schema(
            "schemas/agent-handoff.schema.json",
            relative_to_root(path),
        )
        protocol.validate_handoff(handoff)
        handoffs.append(handoff)

    actual_ids = [item["handoff_id"] for item in handoffs]
    if len(actual_ids) != len(set(actual_ids)):
        raise AssertionError("Agent run bundle contains duplicate handoff ids")

    declared_ids = set(orchestration["handoffs"])
    actual_id_set = set(actual_ids)
    undeclared = actual_id_set - declared_ids
    missing = declared_ids - actual_id_set
    if undeclared or missing:
        raise AssertionError(
            "Agent run handoff ledger does not match bundle documents: "
            f"undeclared={sorted(undeclared)}, missing={sorted(missing)}"
        )

    protocol.validate_protocol_chain(task, orchestration, handoffs)

    print("Blueprint agent run validation: PASS")
    print(f"Task: {task['task_id']} revision {task['revision']}")
    print(f"State: {orchestration['current_state']}")
    print(f"Candidate HEAD: {orchestration['baseline'].get('head_sha')}")
    print(f"Executed handoffs: {len(handoffs)}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate one reusable Blueprint multi-agent run bundle."
    )
    parser.add_argument(
        "run_dir",
        type=pathlib.Path,
        help="Directory containing task-packet.yaml, orchestration.yaml and handoffs/*.yaml",
    )
    args = parser.parse_args()

    try:
        validate_run(args.run_dir)
    except (AssertionError, OSError, ValueError) as exc:
        print(f"Blueprint agent run validation: FAIL\n{exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
