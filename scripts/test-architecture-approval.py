#!/usr/bin/env python3
"""Synthetic approval ledger fixtures; never real owner approval."""
import importlib.util
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker, ValidationError

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("approval", ROOT / "scripts/validate-architecture-approval.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
catalog = m.load(m.CATALOG)
validator = Draft202012Validator(m.load(ROOT / "schemas/architecture-approval.proposal.schema.json"),
                                 format_checker=FormatChecker())
now = datetime(2026, 11, 26, tzinfo=timezone.utc)


def sign(ledger, d):
    d["approval"] = {
        "authority": "human_owner", "owner": ledger["project"]["owner"],
        "decision_id": d["id"], "revision": d["revision"],
        "catalog_sha": ledger["catalog"]["source_commit"],
        "decision_digest": m.decision_digest(d, ledger["project"], ledger["catalog"]["sha256"]),
        "evidence": "SYNTHETIC-" + d["id"], "at": "2026-11-25T00:00:00Z",
    }


def resolve(ledger, key, selection=None):
    d = ledger["decisions"][int(key[4:]) - 1]
    d.update(status="APPROVED" if selection else "NOT_APPLICABLE",
             applicability="APPLICABLE" if selection else "NOT_APPLICABLE",
             selection=selection or [], rationale="Synthetic test rationale",
             recommendation="Synthetic recommendation" if selection else "",
             compatibility="VERIFIED" if selection else "NOT_APPLICABLE")
    sign(ledger, d)


def fixture():
    l = m.blank_ledger("example/synthetic", "Synthetic owner", "GREENFIELD", catalog)
    for d in l["decisions"]:
        resolve(l, d["id"])
    for k, v in {"ARC-001":"Greenfield", "ARC-002":"Escritorio", "ARC-003":"Clean Architecture",
                 "ARC-007":"Monorepo", "ARC-121":"Técnica", "ARC-122":"QA",
                 "ARC-129":"PRIVATE"}.items():
        resolve(l, k, [v])
    return l


def fails(name, ledger):
    try:
        errors = m.evaluate(ledger, catalog, validator, now)
    except (ValueError, ValidationError):
        errors = ["invalid structure"]
    if not errors:
        raise AssertionError("invalid fixture passed: " + name)
    print("PASS negative:", name)


l = fixture()
assert not m.evaluate(l, catalog, validator, now)
print("PASS synthetic complete ledger (structural only)")
pending = m.blank_ledger("example/synthetic", "Synthetic owner", "GREENFIELD", catalog)
assert len(m.evaluate(pending, catalog, validator, now)) >= 137
print("PASS initialized ledger blocks all 137 decisions")
cases = {
    "missing decision": lambda x: x["decisions"].pop(),
    "duplicate decision": lambda x: x["decisions"][1].update(id="ARC-001"),
    "missing approval": lambda x: x["decisions"][0].update(approval=None),
    "wrong owner": lambda x: x["decisions"][0]["approval"].update(owner="agent"),
    "changed selection": lambda x: x["decisions"][0].update(selection=["Brownfield"]),
    "changed revision": lambda x: x["decisions"][0].update(revision=2),
    "wrong catalog": lambda x: x["catalog"].update(sha256="0"*64),
    "reused approval": lambda x: x["decisions"][1]["approval"].update(evidence="SYNTHETIC-ARC-001"),
    "future approval": lambda x: x["decisions"][0]["approval"].update(at="2030-01-01T00:00:00Z"),
    "reopened decision": lambda x: x["decisions"][0].update(status="REOPENED", approval=None),
    "rejected decision": lambda x: x["decisions"][0].update(status="REJECTED", approval=None),
    "missing compatibility": lambda x: x["decisions"][0].update(compatibility="PENDING"),
    "unjustified N/A": lambda x: x["decisions"][3].update(rationale=""),
    "architecture N/A": lambda x: resolve(x,"ARC-003"),
    "alternative without exception": lambda x: resolve(x,"ARC-003",["Alternative"]),
    "web without browser QA": lambda x: resolve(x,"ARC-002",["Web"]),
    "public without discoverability": lambda x: resolve(x,"ARC-129",["PUBLIC_INDEXABLE"]),
    "HTTP without Postman": lambda x: resolve(x,"ARC-029",["REST"]),
    "mobile without QA": lambda x: resolve(x,"ARC-002",["Android"]),
}
for name, mutate in cases.items():
    x = deepcopy(l)
    mutate(x)
    fails(name, x)
x = deepcopy(l)
resolve(x,"ARC-003",["Alternative"])
d=x["decisions"][2]
d["exception_id"]="EX-001"
x["exceptions"]=[dict(exception_id="EX-001",policy_id="BF-P01",project="example/synthetic",
    decision_id="ARC-003",revision=1,scope="synthetic",alternative="Alternative",
    rationale="test",risk="test",mitigations="test",owner="Synthetic owner",
    approval_evidence="SYNTHETIC-EX",approved_at="2026-11-25T00:00:00Z",
    review_trigger="test",expires_at="2026-12-01T00:00:00Z",affected_tests=["test"],status="APPROVED")]
sign(x,d)
assert not m.evaluate(x,catalog,validator,now)
print("PASS bounded synthetic exception")
for name, key, value in [("expired exception","expires_at","2026-11-25T12:00:00Z"),
                         ("pending exception","status","PENDING"),
                         ("forbidden waiver","policy_id","BF-P07"),
                         ("cross-project exception","project","other/project"),
                         ("stale exception","revision",2)]:
    y=deepcopy(x)
    y["exceptions"][0][key]=value
    fails(name,y)
print("Architecture approval fixtures: PASS")
