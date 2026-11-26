#!/usr/bin/env python3
"""Validate a proposal ledger. Approval evidence must still be authenticated by a human reviewer."""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "catalog/architecture-decisions.proposal.json"
CATALOG_COMMIT = "0c46a0396576aca34a9da43afda8cfc8dcead9a9"


def unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key: " + key)
        result[key] = value
    return result


def load(path):
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_pairs)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                     separators=(",", ":")).encode()).hexdigest()


def decision_digest(record, project, catalog_hash):
    return digest({"project": project, "catalog_hash": catalog_hash,
                   "decision": {k: v for k, v in record.items() if k != "approval"}})


def timestamp(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def blank_ledger(repository, owner, mode, catalog):
    return {
        "schema_version": "1.0.0", "protocol": "architecture-approval-proposal-1",
        "project": {"repository": repository, "owner": owner, "mode": mode},
        "catalog": {"sha256": digest(catalog), "source_commit": CATALOG_COMMIT,
                    "version": "proposal-1"},
        "decisions": [{"id": d["id"], "revision": 1, "status": "PENDING",
                       "applicability": "UNDETERMINED", "selection": [],
                       "rationale": "", "recommendation": "", "compatibility": "PENDING",
                       "approval": None, "exception_id": None} for d in catalog["decisions"]],
        "exceptions": [],
    }


def evaluate(ledger, catalog, validator, now):
    validator.validate(ledger)
    project = ledger["project"]
    pinned = ledger["catalog"]
    if pinned != {"sha256": digest(catalog), "source_commit": CATALOG_COMMIT,
                  "version": "proposal-1"}:
        raise ValueError("catalog identity mismatch")
    if not project["owner"].strip():
        raise ValueError("blank owner")
    expected = [d["id"] for d in catalog["decisions"]]
    records = ledger["decisions"]
    if [d["id"] for d in records] != expected:
        raise ValueError("exact ordered catalog coverage required")
    by_id = {d["id"]: d for d in records}
    errors = []
    def block(record, reason):
        errors.append(record["id"] + ": " + reason)

    exceptions = {}
    for ex in ledger["exceptions"]:
        if ex["exception_id"] in exceptions:
            raise ValueError("duplicate exception ID")
        exceptions[ex["exception_id"]] = ex
        if ex["decision_id"] not in by_id:
            raise ValueError("exception refers to unknown decision")
        if by_id[ex["decision_id"]]["exception_id"] != ex["exception_id"]:
            raise ValueError("unbound exception")
    evidence_ids = set()
    for record in records:
        status = record["status"]
        approval = record["approval"]
        if status not in ("APPROVED", "NOT_APPLICABLE"):
            block(record, "unresolved " + status)
            if approval is not None:
                block(record, "unresolved decision retains approval")
            continue
        if not record["rationale"].strip():
            block(record, "missing rationale")
        if approval is None:
            block(record, "missing approval")
        else:
            if (approval["owner"] != project["owner"] or
                approval["decision_id"] != record["id"] or
                approval["revision"] != record["revision"] or
                approval["catalog_sha"] != pinned["source_commit"] or
                approval["decision_digest"] != decision_digest(record, project, pinned["sha256"])):
                block(record, "approval identity or revision mismatch")
            if not approval["evidence"].strip() or timestamp(approval["at"]) > now:
                block(record, "missing or future approval evidence")
            if approval["evidence"] in evidence_ids:
                block(record, "reused individual approval evidence identifier")
            evidence_ids.add(approval["evidence"])
        if status == "APPROVED":
            if (record["applicability"] != "APPLICABLE" or not record["selection"] or
                not all(v.strip() for v in record["selection"]) or
                not record["recommendation"].strip() or record["compatibility"] != "VERIFIED"):
                block(record, "incomplete applicable decision")
        elif (record["applicability"] != "NOT_APPLICABLE" or record["selection"] or
              record["compatibility"] != "NOT_APPLICABLE" or record["exception_id"]):
            block(record, "invalid N/A resolution")
        exid = record["exception_id"]
        if exid:
            ex = exceptions.get(exid)
            if (not ex or ex["project"] != project["repository"] or
                ex["owner"] != project["owner"] or ex["decision_id"] != record["id"] or
                ex["revision"] != record["revision"] or ex["status"] != "APPROVED" or
                not (timestamp(ex["approved_at"]) <= now < timestamp(ex["expires_at"]))):
                block(record, "exception missing, stale, unapproved or expired")
            elif any(not ex[k].strip() for k in ("scope", "alternative", "rationale", "risk",
                      "mitigations", "approval_evidence", "review_trigger")):
                block(record, "incomplete exception")
        if record["id"] == "ARC-003":
            if status != "APPROVED":
                block(record, "architecture cannot be N/A")
            elif record["selection"] != ["Clean Architecture"]:
                ex = exceptions.get(exid)
                if not ex or ex["policy_id"] != "BF-P01":
                    block(record, "alternative architecture requires BF-P01 exception")
            elif exid:
                block(record, "unnecessary architecture exception")
    # Explicit mandatory controls cannot be resolved N/A.
    for key in ("ARC-001", "ARC-002", "ARC-003", "ARC-007", "ARC-121", "ARC-122", "ARC-129"):
        if by_id[key]["status"] == "NOT_APPLICABLE":
            block(by_id[key], "mandatory project decision")
    def selected(key, value):
        return by_id[key]["status"] == "APPROVED" and value in by_id[key]["selection"]
    def require(keys, why):
        for key in keys:
            if by_id[key]["status"] != "APPROVED":
                block(by_id[key], why)
    if selected("ARC-002", "Web"):
        require(["ARC-039", "ARC-046", "ARC-112"], "web architecture and browser QA required")
    if selected("ARC-129", "PUBLIC_INDEXABLE"):
        require([f"ARC-{i:03}" for i in (123,124,125,126,128,129)], "public discoverability required")
    if selected("ARC-029", "REST") or selected("ARC-029", "GraphQL"):
        require(["ARC-028", "ARC-031", *[f"ARC-{i:03}" for i in range(130,138)]],
                "HTTP API contract and operational QA required")
    if selected("ARC-002", "Android") or selected("ARC-002", "iOS"):
        require(["ARC-061", "ARC-062", "ARC-063", "ARC-064", "ARC-113"],
                "mobile architecture and platform QA required")
    # This is a structural readiness report, not authenticated human approval.
    return errors


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--init", type=Path)
    group.add_argument("--validate", type=Path)
    parser.add_argument("--repository")
    parser.add_argument("--owner")
    parser.add_argument("--mode", choices=["GREENFIELD", "BROWNFIELD", "EXTENSION"])
    args = parser.parse_args()
    catalog = load(CATALOG)
    schema = load(ROOT / "schemas/architecture-approval.proposal.schema.json")
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    if args.init:
        if not all((args.repository, args.owner, args.mode)):
            parser.error("--init requires --repository, --owner and --mode")
        ledger = blank_ledger(args.repository, args.owner, args.mode, catalog)
        validator.validate(ledger)
        with args.init.open("x", encoding="utf-8") as out:
            json.dump(ledger, out, ensure_ascii=False, indent=2)
            out.write("\n")
        print("Generated 137 PENDING decisions; implementation is BLOCKED")
        return 0
    ledger = load(args.validate)
    errors = evaluate(ledger, catalog, validator, datetime.now(timezone.utc))
    if errors:
        print("BLOCKED:", len(errors), "findings")
        print("\n".join(errors))
        return 1
    print("READY_FOR_HUMAN_REVIEW: structural checks passed; not implementation authorization")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print("BLOCKED:", exc, file=sys.stderr)
        sys.exit(1)
