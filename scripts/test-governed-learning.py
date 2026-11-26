#!/usr/bin/env python3
"""Synthetic approvals only: tests never promote real lessons."""
from copy import deepcopy
from datetime import datetime,timezone
import importlib.util
import json
from pathlib import Path
import tempfile
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("retrieval",ROOT/"scripts/retrieve-governed-lessons.py")
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
v=m.v
now=datetime(2026,11,26,12,tzinfo=timezone.utc)
def fixture():
    b=dict(id="LESSON-SYNTHETIC-001",revision=1,category="environment",author="qa",source_repository="example/source",source_commit="a"*40,source_task="DEMO",created_at="2026-11-24T00:00:00Z",scope="PORTABLE",technologies=["Node.js"],title="Synthetic lesson",observation="Synthetic observation",recommendation="Synthetic advice",limitations="Fixture only",evidence=["synthetic evidence"],policy_override=False)
    review=dict(reviewer="security",body_digest=v.digest(b),status="ACCEPTED",at="2026-11-25T00:00:00Z",evidence="synthetic review",sanitization="DECLARED_SANITIZED")
    approval=dict(authority="human_owner",owner="fixture-owner",body_digest=v.digest(b),review_digest=v.digest(review),at="2026-11-26T00:00:00Z",expires_at="2026-12-26T00:00:00Z",evidence="synthetic approval")
    return dict(body=b,status="APPROVED",review=review,approval=approval),dict(repository="example/consumer",approved_technologies=["Node.js"],owner="fixture-owner",requesting_agent="backend")
def bind(l):
    l["review"]["body_digest"]=v.digest(l["body"])
    l["approval"]["body_digest"]=v.digest(l["body"])
    l["approval"]["review_digest"]=v.digest(l["review"])
def change(l,section,**kw):
    l[section].update(kw)
    bind(l)
def accept(l,c):
    result=v.evaluate(l,c,now)
    assert result["execution_authorized"] is False and result["policy_change_authorized"] is False
    return result
l,c=fixture()
assert accept(l,c)["status"]=="ELIGIBLE_FOR_ADVISORY_REVIEW"
print("PASS compatible portable lesson")
l,c=fixture()
change(l,"body",scope="PROJECT_ONLY")
c["repository"]=l["body"]["source_repository"]
accept(l,c)
print("PASS project-only within source")
cases=[
("proposal",lambda l,c:l.update(status="PROPOSED")),
("reviewed",lambda l,c:l.update(status="REVIEWED")),
("revoked",lambda l,c:l.update(status="REVOKED")),
("superseded",lambda l,c:l.update(status="SUPERSEDED")),
("rejected",lambda l,c:l.update(status="REJECTED")),
("changed body",lambda l,c:l["body"].update(recommendation="modified")),
("changed review",lambda l,c:l["review"].update(evidence="modified")),
("self review",lambda l,c:change(l,"review",reviewer="qa")),
("portable non-security review",lambda l,c:change(l,"review",reviewer="auditor")),
("unsanitized portable",lambda l,c:change(l,"review",sanitization="NOT_DISTRIBUTED")),
("wrong owner",lambda l,c:change(l,"approval",owner="other")),
("agent approval",lambda l,c:change(l,"approval",authority="orchestrator")),
("expired",lambda l,c:change(l,"approval",expires_at="2026-11-26T10:00:00Z")),
("future approval",lambda l,c:change(l,"approval",at="2026-12-01T00:00:00Z")),
("no timezone",lambda l,c:change(l,"approval",at="2026-11-26T00:00:00")),
("missing source evidence",lambda l,c:change(l,"body",evidence=[])),
("short source SHA",lambda l,c:change(l,"body",source_commit="abc123")),
("override policy",lambda l,c:change(l,"body",policy_override=True)),
("incompatible technology",lambda l,c:c.update(approved_technologies=[])),
("project-only cross-project",lambda l,c:change(l,"body",scope="PROJECT_ONLY")),
("unknown agent",lambda l,c:c.update(requesting_agent="unknown")),
("missing approval evidence",lambda l,c:change(l,"approval",evidence="")),
]
for name,mutate in cases:
    l,c=fixture()
    mutate(l,c)
    try: accept(l,c)
    except ValueError: print("PASS negative:",name)
    else: raise AssertionError(name)
def write(d,l):
    b=l["body"]
    (d/f'{b["id"]}.r{b["revision"]}.json').write_text(json.dumps(l),encoding="utf-8")
with tempfile.TemporaryDirectory() as tmp:
    d=Path(tmp)
    l,c=fixture()
    write(d,l)
    assert len(m.retrieve(d,c,now)["eligible"])==1
    print("PASS local retrieval")
    newer=deepcopy(l)
    newer["body"]["revision"]=2
    newer["status"]="REVOKED"
    write(d,newer)
    assert not m.retrieve(d,c,now)["eligible"]
    print("PASS revoked latest revision cannot fall back")
    newer["status"]="PROPOSED"
    write(d,newer)
    assert not m.retrieve(d,c,now)["eligible"]
    print("PASS pending latest revision cannot fall back")
    (d/"invalid.json").write_text(json.dumps(l),encoding="utf-8")
    try: m.retrieve(d,c,now)
    except ValueError: print("PASS malformed registry filename blocks")
    else: raise AssertionError("invalid registry filename")
assert not m.retrieve(ROOT/"knowledge/proposals",fixture()[1],now)["eligible"]
print("PASS real proposed lesson remains unavailable")
print("Governed learning regression PASS (29 scenarios)")
