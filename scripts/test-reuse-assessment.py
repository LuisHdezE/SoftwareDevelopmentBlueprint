#!/usr/bin/env python3
"""Synthetic reuse assessment tests, not real generator exports."""
import contextlib
from copy import deepcopy
import importlib.util
import io
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,ROOT/"scripts"/path)
    m=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m
p=load("reuse","validate-reuse-assessment.py")
with contextlib.redirect_stdout(io.StringIO()):
    f=load("fixtures","test-architecture-approval.py")
ledger=f.fixture()
sources=p.a.load(p.SOURCES)["sources"]
for source in sources:
    for key,value in source["required_selections"].items():
        f.resolve(ledger,key,[value])
for key,value in {"ARC-028":"Privada","ARC-031":"OpenAPI"}.items():
    f.resolve(ledger,key,[value])
for i in range(130,138):
    key=f"ARC-{i:03}"
    f.resolve(ledger,key,[f.catalog["decisions"][i-1]["options"][0]])
record={"repository":ledger["project"]["repository"],"ledger_digest":p.a.digest(ledger),"scope":"Synthetic reuse test","sources":[]}
for s in sources:
    record["sources"].append(dict(id=s["id"],commit=s["commit"],decision="REUSE",rationale="Synthetic compatible selection",components=["example"],review_evidence="synthetic-review",requested_manifest={"selection":["example"]},resolved_manifest={"selection":["example"]},changes=[]))
def check(l,r):
    try:
        result=p.evaluate(l,r,f.now)
    except Exception:
        return "BLOCKED"
    assert result["execution_authorized"] is False
    return result["status"]
assert check(ledger,record)=="READY_FOR_HUMAN_REUSE_REVIEW",p.evaluate(ledger,record,f.now)
print("PASS compatible synthetic reuse")
x=deepcopy(record)
x["sources"][1]["resolved_manifest"]["governance"]={"authentication":"sanctum"}
x["sources"][1]["changes"]=[dict(field="governance",evidence="synthetic-change",status="DECLARED_REVIEWED")]
assert check(ledger,x)=="READY_FOR_HUMAN_REUSE_REVIEW"
print("PASS declared manifest change review")
cases=[
("missing source",lambda l,r:r["sources"].pop()),
("duplicate source",lambda l,r:r["sources"].append(r["sources"][0])),
("unpinned source",lambda l,r:r["sources"][0].update(commit="main")),
("foreign project",lambda l,r:r.update(repository="other/repo")),
("stale ledger",lambda l,r:r.update(ledger_digest="0"*64)),
("missing rationale",lambda l,r:r["sources"][0].update(rationale="")),
("missing review",lambda l,r:r["sources"][0].update(review_evidence="")),
("missing components",lambda l,r:r["sources"][0].update(components=[])),
("missing manifest",lambda l,r:r["sources"][0].update(resolved_manifest={})),
("unreviewed change",lambda l,r:r["sources"][1]["resolved_manifest"].update(governance={"authentication":"sanctum"})),
("false change review",lambda l,r:r["sources"][0].update(changes=[dict(field="unknown",status="DECLARED_REVIEWED",evidence="fake")])),
("blocked source",lambda l,r:r["sources"][0].update(decision="BLOCKED")),
("new with export intent",lambda l,r:r["sources"][0].update(decision="NEW")),
("unknown decision",lambda l,r:r["sources"][0].update(decision="AUTO")),
]
for name,mutate in cases:
    l,r=deepcopy(ledger),deepcopy(record)
    mutate(l,r)
    assert check(l,r)=="BLOCKED",name
    print("PASS negative:",name)
l,r=deepcopy(ledger),deepcopy(record)
f.resolve(l,"ARC-039",["Vue"])
r["ledger_digest"]=p.a.digest(l)
assert check(l,r)=="BLOCKED"
print("PASS negative: incompatible frontend")
print("Reuse assessment: PASS (2 positive, 15 negative)")
