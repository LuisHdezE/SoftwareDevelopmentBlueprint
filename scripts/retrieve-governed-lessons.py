#!/usr/bin/env python3
"""Local lesson registry. Latest revision only; no fallback to revoked history."""
import argparse
from datetime import datetime,timezone
import importlib.util
import json
from pathlib import Path
import re
import sys

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("lesson",ROOT/"scripts/validate-governed-lesson.py")
v=importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)
STATES={"PROPOSED","REVIEWED","APPROVED","REJECTED","REVOKED","SUPERSEDED"}
def retrieve(directory,context,now):
    latest={}
    if not directory.is_dir():
        raise ValueError("registry missing")
    for p in sorted(directory.glob("*.json")):
        if p.is_symlink() or not p.is_file():
            raise ValueError("unsafe registry entry")
        record=v.load(p)
        body=record["body"]
        ident,rev=body["id"],body["revision"]
        if not re.fullmatch(r"LESSON-[A-Z0-9-]+",ident) or type(rev) is not int or rev<1:
            raise ValueError("invalid registry identity")
        if p.name!=f"{ident}.r{rev}.json" or record["status"] not in STATES:
            raise ValueError("invalid registry filename or state")
        if ident not in latest or rev>latest[ident]["body"]["revision"]:
            latest[ident]=record
    eligible=[]
    for ident,record in sorted(latest.items()):
        if record["status"]!="APPROVED":
            continue
        try:
            v.evaluate(record,context,now)
        except (ValueError,TypeError,KeyError,AttributeError):
            continue
        eligible.append(record)
    return {"status":"ADVISORY_RESULTS_ONLY","eligible":eligible,"execution_authorized":False,"policy_change_authorized":False}
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--registry",type=Path,required=True)
    p.add_argument("--context",type=Path,required=True)
    args=p.parse_args()
    try:
        print(json.dumps(retrieve(args.registry,v.load(args.context),datetime.now(timezone.utc)),ensure_ascii=False))
        return 0
    except Exception as exc:
        print(json.dumps({"status":"BLOCKED","finding":str(exc),"execution_authorized":False}))
        return 1
if __name__=="__main__":
    sys.exit(main())
