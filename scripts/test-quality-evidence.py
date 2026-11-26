#!/usr/bin/env python3
"""Synthetic quality-evidence preflight regression cases."""
import copy
import hashlib
import importlib.util
from pathlib import Path
import tempfile

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("quality",ROOT/"scripts/validate-quality-evidence.py")
q=importlib.util.module_from_spec(spec)
spec.loader.exec_module(q)
def fixture(root):
    plan=dict(repository="example/synthetic",candidate="a"*40,task_id="DEMO-001",revision=1,scope="Synthetic web/API change",review_evidence="synthetic reviewed scope",applicability={k:dict(required=k in {"functional","traceability","browser","http_api","architecture","security"},reason="Synthetic fixture applicability") for k in q.ROLE_KIND})
    record={k:plan[k] for k in ("repository","candidate","task_id","revision")}
    record["plan_digest"]=q.digest(plan)
    record["evidence"]=[]
    for k,a in plan["applicability"].items():
        if not a["required"]: continue
        path=k+".json"
        data=("synthetic fixture "+k).encode()
        (root/path).write_bytes(data)
        producer,kind=q.ROLE_KIND[k]
        record["evidence"].append(dict(obligation=k,producer=producer,kind=kind,runner="synthetic",version="1",environment="fixture",status="PASS",executed=1,failures=0,artifact=path,sha256=hashlib.sha256(data).hexdigest()))
    return plan,record
def rebind(p,r):
    r["plan_digest"]=q.digest(p)
def change(p,r,key,value):
    p[key]=value
    rebind(p,r)
def omit(p,r,key):
    p["applicability"].pop(key)
    rebind(p,r)
def disable(p,r,key):
    p["applicability"][key]["required"]=False
    r["evidence"]=[e for e in r["evidence"] if e["obligation"]!=key]
    rebind(p,r)
def ev(r,key):
    return next(e for e in r["evidence"] if e["obligation"]==key)
cases=[
("short SHA",lambda p,r,d:change(p,r,"candidate","abcdef1")),
("foreign project",lambda p,r,d:r.update(repository="other/project")),
("stale candidate",lambda p,r,d:r.update(candidate="b"*40)),
("stale task",lambda p,r,d:r.update(task_id="OTHER")),
("stale revision",lambda p,r,d:r.update(revision=2)),
("stale plan",lambda p,r,d:p.update(scope="changed")),
("unreviewed scope",lambda p,r,d:change(p,r,"review_evidence","")),
("omitted applicability",lambda p,r,d:omit(p,r,"browser")),
("functional waived",lambda p,r,d:disable(p,r,"functional")),
("traceability waived",lambda p,r,d:disable(p,r,"traceability")),
("missing browser",lambda p,r,d:r["evidence"].remove(ev(r,"browser"))),
("duplicate evidence",lambda p,r,d:r["evidence"].append(copy.deepcopy(r["evidence"][0]))),
("wrong security authority",lambda p,r,d:ev(r,"security").update(producer="qa")),
("build replaces browser",lambda p,r,d:ev(r,"browser").update(kind="build")),
("not run",lambda p,r,d:ev(r,"browser").update(status="NOT_RUN")),
("failed",lambda p,r,d:ev(r,"browser").update(failures=1)),
("zero executed",lambda p,r,d:ev(r,"browser").update(executed=0)),
("missing runner version",lambda p,r,d:ev(r,"browser").update(version="")),
("missing artifact",lambda p,r,d:(d/"browser.json").unlink()),
("empty artifact",lambda p,r,d:(d/"browser.json").write_bytes(b"")),
("modified artifact",lambda p,r,d:(d/"browser.json").write_bytes(b"changed")),
("absolute artifact",lambda p,r,d:ev(r,"browser").update(artifact=str(d/"browser.json"))),
("traversal",lambda p,r,d:ev(r,"browser").update(artifact="../browser.json")),
("Windows traversal",lambda p,r,d:ev(r,"browser").update(artifact="..\\browser.json")),
]
with tempfile.TemporaryDirectory() as tmp:
    d=Path(tmp)
    p,r=fixture(d)
    result=q.evaluate(p,r,d)
    assert result["status"]=="READY_FOR_INDEPENDENT_QA_REVIEW" and result["release_authorized"] is False
    print("PASS complete synthetic evidence")
for name,mutate in cases:
    with tempfile.TemporaryDirectory() as tmp:
        d=Path(tmp)
        p,r=fixture(d)
        mutate(p,r,d)
        try: q.evaluate(p,r,d)
        except ValueError: print("PASS negative:",name)
        else: raise AssertionError("accepted invalid evidence: "+name)
with tempfile.TemporaryDirectory() as tmp:
    d=Path(tmp)
    p,r=fixture(d)
    try: (d/"link.json").symlink_to(d/"browser.json")
    except OSError: print("SKIP symlink test: platform permission")
    else:
        ev(r,"browser")["artifact"]="link.json"
        try: q.evaluate(p,r,d)
        except ValueError: print("PASS negative: symlink")
        else: raise AssertionError("accepted symlink")
print("Quality evidence regression PASS")
