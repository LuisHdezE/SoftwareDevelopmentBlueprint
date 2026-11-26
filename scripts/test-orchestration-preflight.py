#!/usr/bin/env python3
"""Synthetic preflight tests; no real authorization or agent execution."""
import contextlib
from copy import deepcopy
from datetime import datetime, timezone
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile

import yaml
from jsonschema import ValidationError

ROOT = Path(__file__).resolve().parents[1]
def module(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

p = module("preflight", "orchestration-preflight.py")
with contextlib.redirect_stdout(io.StringIO()):
    fixtures = module("approval_fixtures", "test-architecture-approval.py")
now = datetime(2026, 11, 26, tzinfo=timezone.utc)
ledger = fixtures.fixture()
task = yaml.safe_load((ROOT / "templates/agent-run.example/task-packet.yaml").read_text(encoding="utf-8"))
task["baseline"]["repository"] = ledger["project"]["repository"]
task["baseline"]["base_sha"] = "a" * 40
review = dict(repository=ledger["project"]["repository"], owner=ledger["project"]["owner"],
              task_digest=p.approval.digest(task), ledger_digest=p.approval.digest(ledger),
              evidence="SYNTHETIC-review", reviewed_at="2026-11-25T12:00:00Z",
              architecture_changed=False, status="DECLARED_OWNER_REVIEW")

def bind(t,l,r):
    r.update(task_digest=p.approval.digest(t),ledger_digest=p.approval.digest(l))

def check(t,l,r):
    try:
        result = p.evaluate(t,l,r,now)
    except (ValueError, AssertionError, ValidationError):
        return "BLOCKED"
    assert result["execution_authorized"] is False
    return result["status"]

assert check(task,ledger,review) == "READY_FOR_AUTHENTICATED_DISPATCH_REVIEW"
print("PASS synthetic readiness; execution remains unauthorized")
cases = [
    ("changed task", lambda t,l,r:t.update(revision=2), False),
    ("changed ledger", lambda t,l,r:l["decisions"][0].update(rationale="changed"),False),
    ("missing review", lambda t,l,r:r.clear(),False),
    ("wrong owner", lambda t,l,r:r.update(owner="agent"),False),
    ("wrong repository", lambda t,l,r:t["baseline"].update(repository="other/repo"),True),
    ("missing QA", lambda t,l,r:t["required_agents"].remove("qa"),True),
    ("missing Auditor", lambda t,l,r:t["required_agents"].remove("auditor"),True),
    ("tests optional", lambda t,l,r:t["validation"].update(tests="conditional"),True),
    ("unknown specialist", lambda t,l,r:t["optional_agents"].append("specialist:unknown"),True),
    ("dependency unverified", lambda t,l,r:t["dependencies"].append({"task_id":"BP-PREV-001","required_state":"CLOSED"}),True),
    ("short baseline", lambda t,l,r:t["baseline"].update(base_sha="abcdef1"),True),
    ("short head", lambda t,l,r:t["baseline"].update(head_sha="abcdef1"),True),
    ("future review", lambda t,l,r:r.update(reviewed_at="2030-01-01T00:00:00Z"),False),
    ("review before approval", lambda t,l,r:r.update(reviewed_at="2026-11-24T00:00:00Z"),False),
    ("timezone absent", lambda t,l,r:r.update(reviewed_at="2026-11-25T12:00:00"),False),
    ("missing evidence", lambda t,l,r:r.update(evidence=" "),False),
    ("fake authorization", lambda t,l,r:r.update(status="AUTHORIZED"),False),
    ("architecture change without architect", lambda t,l,r:r.update(architecture_changed=True),False),
    ("unresolved architecture", lambda t,l,r:l["decisions"][2].update(status="REOPENED",approval=None),True),
    ("nonimplementation owner", lambda t,l,r:t.update(owner_agent="qa"),True),
]
for name,mutate,rebind in cases:
    t,l,r=deepcopy(task),deepcopy(ledger),deepcopy(review)
    mutate(t,l,r)
    if rebind:
        bind(t,l,r)
    assert check(t,l,r) == "BLOCKED", name
    print("PASS negative:",name)

with tempfile.TemporaryDirectory() as tmp:
    d=Path(tmp)
    tp,lp,rp=d/"task.yaml",d/"ledger.json",d/"review.json"
    tp.write_text(yaml.safe_dump(task),encoding="utf-8")
    lp.write_text(json.dumps(ledger),encoding="utf-8")
    rp.write_text(json.dumps(review),encoding="utf-8")
    cmd=[sys.executable,str(ROOT/"scripts/orchestration-preflight.py"),"--task",str(tp),"--ledger",str(lp),"--review",str(rp)]
    run=subprocess.run(cmd,capture_output=True,text=True,encoding="utf-8")
    assert run.returncode == 0, run.stdout+run.stderr
    assert json.loads(run.stdout)["execution_authorized"] is False
    print("PASS CLI readiness")
    tp.write_text(tp.read_text(encoding="utf-8")+"\ntitle: duplicate\n",encoding="utf-8")
    run=subprocess.run(cmd,capture_output=True,text=True,encoding="utf-8")
    assert run.returncode == 1 and json.loads(run.stdout)["status"] == "BLOCKED"
    assert "duplicate YAML key" in run.stdout
    print("PASS CLI duplicate YAML rejection")
print("Orchestration preflight: PASS (2 positive, 21 negative)")
