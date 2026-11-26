#!/usr/bin/env python3
"""Read-only reuse review. Structural readiness is not approval or export certification."""
import argparse
import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path
import sys
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("approval", ROOT/"scripts/validate-architecture-approval.py")
a = importlib.util.module_from_spec(spec)
spec.loader.exec_module(a)
SOURCES = ROOT/"catalog/reuse-sources.proposal.json"

def evaluate(ledger, record, now):
    catalog = a.load(a.CATALOG)
    validator = Draft202012Validator(a.load(ROOT/"schemas/architecture-approval.proposal.schema.json"), format_checker=FormatChecker())
    errors = a.evaluate(ledger,catalog,validator,now)
    sources = a.load(SOURCES)
    if sources["automatic_reuse"] is not False or sources["automatic_upgrade"] is not False:
        raise ValueError("automatic reuse or upgrade forbidden")
    if set(record) != {"repository","ledger_digest","scope","sources"}:
        raise ValueError("invalid reuse record")
    if record["repository"] != ledger["project"]["repository"] or record["ledger_digest"] != a.digest(ledger):
        errors.append("stale or foreign architecture ledger")
    if not isinstance(record["scope"],str) or not record["scope"].strip():
        errors.append("missing scope")
    if not isinstance(record["sources"],list):
        raise ValueError("invalid source list")
    if [s["id"] for s in record["sources"]] != [s["id"] for s in sources["sources"]]:
        raise ValueError("all registered sources must be assessed once")
    decisions = {d["id"]:d for d in ledger["decisions"]}
    for entry, source in zip(record["sources"],sources["sources"]):
        if set(entry) != {"id","commit","decision","rationale","components","review_evidence","requested_manifest","resolved_manifest","changes"}:
            raise ValueError("invalid source assessment fields")
        if entry["commit"] != source["commit"]:
            errors.append("unpinned source: "+source["id"])
        if not isinstance(entry["rationale"],str) or not entry["rationale"].strip():
            errors.append("missing rationale: "+source["id"])
        if entry["decision"] not in {"REUSE","ADAPT","NEW","BLOCKED","NOT_APPLICABLE"}:
            errors.append("unknown decision")
        if entry["decision"] == "BLOCKED":
            errors.append("source assessment blocked")
        if entry["decision"] in {"REUSE","ADAPT"}:
            for key,value in source["required_selections"].items():
                d=decisions[key]
                if d["status"]!="APPROVED" or value not in d["selection"]:
                    errors.append("incompatible approved stack: "+key)
            if not isinstance(entry["components"],list) or not entry["components"] or not all(isinstance(v,str) and v.strip() for v in entry["components"]):
                errors.append("missing selected components")
            if not isinstance(entry["review_evidence"],str) or not entry["review_evidence"].strip():
                errors.append("missing reuse review evidence")
            requested,resolved=entry["requested_manifest"],entry["resolved_manifest"]
            if not isinstance(requested,dict) or not requested or not isinstance(resolved,dict) or not resolved:
                errors.append("missing manifest snapshots")
            else:
                changed={k for k in set(requested)|set(resolved) if k not in requested or k not in resolved or requested[k]!=resolved[k]}
                changes=entry["changes"]
                if not isinstance(changes,list) or any(not isinstance(c,dict) or set(c)!={"field","evidence","status"} for c in changes):
                    errors.append("malformed manifest change review")
                elif len(changes)!=len(changed) or {c["field"] for c in changes}!=changed or any(c["status"]!="DECLARED_REVIEWED" or not isinstance(c["evidence"],str) or not c["evidence"].strip() for c in changes):
                    errors.append("unreviewed manifest differences")
        else:
            if any(entry[k] for k in ("components","requested_manifest","resolved_manifest","changes")):
                errors.append("nonreuse assessment contains export intent")
    return {"status":"BLOCKED" if errors else "READY_FOR_HUMAN_REUSE_REVIEW","execution_authorized":False,"findings":errors}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--ledger",type=Path,required=True)
    p.add_argument("--record",type=Path,required=True)
    args=p.parse_args()
    try:
        result=evaluate(a.load(args.ledger),a.load(args.record),datetime.now(timezone.utc))
    except Exception as exc:
        result={"status":"BLOCKED","execution_authorized":False,"findings":[str(exc)]}
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return int(result["status"]=="BLOCKED")

if __name__=="__main__":
    sys.exit(main())
