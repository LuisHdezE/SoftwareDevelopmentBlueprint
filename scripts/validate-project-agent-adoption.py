#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
PROTOCOL_PATH = ROOT / 'scripts' / 'validate-agent-protocol.py'
RUN_VALIDATOR_PATH = ROOT / 'scripts' / 'validate-agent-run.py'


def load_module(name: str, path: pathlib.Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f'Cannot load module: {path}')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def relative_to_root(path: pathlib.Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError as exc:
        raise AssertionError(f'Consumer adoption fixture must live inside repository root: {path}') from exc


def safe_relative(value: str, label: str) -> pathlib.PurePosixPath:
    path = pathlib.PurePosixPath(value)
    if path.is_absolute() or '..' in path.parts:
        raise AssertionError(f'{label} must be a safe repository-relative path: {value}')
    if not path.parts:
        raise AssertionError(f'{label} cannot be empty')
    return path


def validate_adoption(adoption_file: pathlib.Path, project_root: pathlib.Path, run_dir: pathlib.Path) -> None:
    protocol = load_module('blueprint_agent_protocol', PROTOCOL_PATH)
    run_validator = load_module('blueprint_agent_run', RUN_VALIDATOR_PATH)

    adoption = protocol.validate_schema(
        'schemas/project-agent-protocol-adoption.schema.json',
        relative_to_root(adoption_file),
    )

    if adoption['agent_protocol']['version'] != 'agent-protocol-proposal-1':
        raise AssertionError('Consumer agent protocol version is unsupported')

    locations = adoption['artifact_locations']
    for key, value in locations.items():
        safe_relative(value, f'artifact_locations.{key}')

    run_root = (project_root / locations['agent_runs_root']).resolve()
    resolved_run = run_dir.resolve()
    try:
        resolved_run.relative_to(run_root)
    except ValueError as exc:
        raise AssertionError(
            f'Run directory must live under declared agent_runs_root: {run_root}'
        ) from exc

    run_validator.validate_run(resolved_run)

    task = protocol.load(relative_to_root(resolved_run / 'task-packet.yaml'))
    orchestration = protocol.load(relative_to_root(resolved_run / 'orchestration.yaml'))
    expected_repo = adoption['project']['repository']

    if task['baseline']['repository'] != expected_repo:
        raise AssertionError(
            'Task Packet repository does not match consumer adoption project.repository'
        )
    if orchestration['baseline']['repository'] != expected_repo:
        raise AssertionError(
            'Orchestration repository does not match consumer adoption project.repository'
        )

    print('Blueprint consumer agent adoption validation: PASS')
    print(f"Project: {adoption['project']['name']} ({expected_repo})")
    print(f"Protocol: {adoption['agent_protocol']['version']} / {adoption['agent_protocol']['mode']}")
    print(f"Run root: {locations['agent_runs_root']}")
    print(f"Validated run: {resolved_run.relative_to(project_root.resolve()).as_posix()}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description='Validate one consumer opt-in plus one reusable Blueprint agent run.'
    )
    parser.add_argument('adoption_file', type=pathlib.Path)
    parser.add_argument('--project-root', required=True, type=pathlib.Path)
    parser.add_argument('--run-dir', required=True, type=pathlib.Path)
    args = parser.parse_args()

    try:
        validate_adoption(args.adoption_file, args.project_root, args.run_dir)
    except (AssertionError, OSError, ValueError) as exc:
        print(f'Blueprint consumer agent adoption validation: FAIL\n{exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
