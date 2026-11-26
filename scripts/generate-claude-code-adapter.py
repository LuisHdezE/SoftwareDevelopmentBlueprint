#!/usr/bin/env python3
"""Generate a reviewable Claude Code bundle; never install into an existing project."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
def generate(output):
    if output.exists():
        raise ValueError("output must not exist")
    sha=subprocess.check_output(["git","-C",str(ROOT),"rev-parse","HEAD"],text=True).strip()
    if subprocess.check_output(["git","-C",str(ROOT),"status","--porcelain","--untracked-files=no"],text=True).strip():
        raise ValueError("tracked source must be clean")
    registry=json.loads((ROOT/"catalog/agent-policy-registry.proposal.json").read_text(encoding="utf-8"))
    files={}
    for a in registry["agents"]:
        name="bf-"+a["alias"].removeprefix("@")
        if not re.fullmatch(r"[a-z][a-z0-9-]+",name):
            raise ValueError("invalid native agent name")
        source=a["contract"]
        body=(ROOT/source).read_text(encoding="utf-8")
        desc=f"Blueprint {a['id']} role: {a['authority']}. Activate only for approved scope."
        files[f".claude/agents/{name}.md"]=f"---\nname: {name}\ndescription: {json.dumps(desc)}\nmodel: inherit\n---\n\n"+f"Source: {source} @ {sha}\n\n"+body+"\n\nMandatory: respect approved task scope, independent verification and human approval. This generated instruction is not execution authorization. Never bypass a blocked gate or approve merge/deploy.\n"
    for p in sorted((ROOT/"skills").glob("*/SKILL.md")):
        raw=p.read_text(encoding="utf-8")
        if not re.fullmatch(r"[a-z0-9-]+",p.parent.name):
            raise ValueError("invalid skill name")
        parts=raw.split("---",2)
        if len(parts)!=3 or not re.search(r"(?m)^status:\s*materialized\s*$",parts[1]):
            continue
        name="bf-"+p.parent.name
        files[f".claude/skills/{name}/SKILL.md"]=f"---\nname: {name}\ndescription: {json.dumps('Blueprint skill '+p.parent.name+'; apply only within approved task scope.')}\n---\n\nSource: {p.relative_to(ROOT).as_posix()} @ {sha}\n\n"+parts[2].lstrip()
    files["CLAUDE.md"]="# Blueprint Factory proposal adapter\n\nSource candidate: "+sha+"\n\nUse only after explicit consumer adoption. Load pinned canonical constitution, architecture ledger and approved task packet before work. Directly select the appropriate bf-* agent or ask bf-orchestrator to route. Never simulate independent approval. No merge/deploy/release without human authorization. Parallelism requires proven independence and verified platform support. This bundle grants no permissions.\n"
    manifest={"status":"PROPOSED","source_commit":sha,"automatic_adoption":False,"execution_authorized":False,"files":{k:hashlib.sha256(v.encode()).hexdigest() for k,v in sorted(files.items())}}
    output.mkdir(parents=True,exist_ok=False)
    for k,v in files.items():
        p=output/k
        p.parent.mkdir(parents=True,exist_ok=True)
        p.write_bytes(v.encode())
    (output/"blueprint-adapter-manifest.json").write_bytes((json.dumps(manifest,indent=2,sort_keys=True)+"\n").encode())
    return manifest
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    try:
        m=generate(a.output)
        print(json.dumps({"status":"GENERATED_FOR_REVIEW","source_commit":m["source_commit"],"files":len(m["files"]),"execution_authorized":False}))
        return 0
    except Exception as exc:
        print(json.dumps({"status":"BLOCKED","finding":str(exc)}))
        return 1
if __name__=="__main__":
    sys.exit(main())
