#!/usr/bin/env python3
"""Read-only preflight. Never dispatches agents or grants execution authority."""
import argparse
from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path
import sys

import yaml
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]

def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / filename)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

approval = module("approval", "validate-architecture-approval.py")
protocol = module("protocol", "validate-agent-protocol.py")

def evaluate(task, ledger, review, now):
    schema = approval.load(ROOT / "schemas/task-packet.schema.json")
    Draft202012Validator(schema).validate(task)
    protocol.validate_task_packet(task)
    catalog = approval.load(approval.CATALOG)
    validator = Draft202012Validator(approval.load(ROOT / "schemas/architecture-approval.proposal.schema.json"), format_checker=FormatChecker())
    errors = approval.evaluate(ledger, catalog, validator, now)
    if ledger["project"]["repository"] != task["baseline"]["repository"]:
        errors.append("task and ledger repository mismatch")
    required = set(task["required_agents"])
    if not {"qa", "auditor"} <= required:
        errors.append("QA and Auditor required for implementation preflight")
    if task["owner_agent"] not in {"backend", "frontend", "database"}:
        errors.append("unsupported implementation owner in proposal preflight")
    if task["owner_agent"] not in required:
        errors.append("implementation owner must be required")
    fields = {"repository","owner","task_digest","ledger_digest","evidence","reviewed_at","architecture_changed","status"}
    if not isinstance(review, dict) or set(review) != fields:
        errors.append("missing or malformed review record")
    else:
        if review["repository"] != ledger["project"]["repository"] or review["owner"] != ledger["project"]["owner"]:
            errors.append("review identity mismatch")
        if review["task_digest"] != approval.digest(task) or review["ledger_digest"] != approval.digest(ledger):
            errors.append("stale review binding")
        if review["status"] != "DECLARED_OWNER_REVIEW":
            errors.append("review status invalid")
        if not isinstance(review["evidence"],str) or not review["evidence"].strip():
            errors.append("missing review evidence")
        try:
            if approval.timestamp(review["reviewed_at"]) > now:
                errors.append("future review")
        except (ValueError, TypeError, AttributeError):
            errors.append("invalid review timestamp")
        if type(review["architecture_changed"]) is not bool:
            errors.append("architecture impact must be explicit")
        elif review["architecture_changed"] and "architect" not in required:
            errors.append("changed architecture requires Architect")
    return {"status":"BLOCKED" if errors else "READY_FOR_AUTHENTICATED_DISPATCH_REVIEW",
            "execution_authorized":False,"findings":errors}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", type=Path, required=True)
    parser.add_argument("--ledger", type=Path, required=True)
    parser.add_argument("--review", type=Path, required=True)
    args = parser.parse_args()
    try:
        task = yaml.safe_load(args.task.read_text(encoding="utf-8"))
        result = evaluate(task, approval.load(args.ledger), approval.load(args.review), datetime.now(timezone.utc))
    except Exception as exc:
        result = {"status":"BLOCKED","execution_authorized":False,"findings":[str(exc)]}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if result["status"] == "BLOCKED" else 0

if __name__ == "__main__":
    sys.exit(main())
