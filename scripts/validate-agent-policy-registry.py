#!/usr/bin/env python3
"""Validate the proposal role projection, not actual agent execution."""
from copy import deepcopy
import json
from pathlib import Path
import re

import yaml

ROOT = Path(__file__).resolve().parents[1]
CORE = "orchestrator analyst planner architect database backend frontend qa security documentation auditor".split()
SPECIALIST = "specialist:search-ai-discoverability"
ROLE_KIND = dict(zip(CORE + [SPECIALIST], ["coordination","analysis","planning","design","implementation","implementation","implementation","verification","verification","knowledge","independent_audit","conditional_specialist"]))
ROLE_AUTHORITY = dict(zip(CORE + [SPECIALIST], ["route_tasks","analyze_requirements","plan_tasks","design_architecture","implement_persistence","implement_api","implement_client","verify_behavior","verify_security","maintain_knowledge","audit_delivery","prepare_discoverability"]))
REQUIRED = {"orchestrator":{"BF-P03","BF-P07","BF-P10","BF-P11","BF-P13"},
"architect":{"BF-P01","BF-P02","BF-P03","BF-P04","BF-P08"},
"backend":{"BF-P04","BF-P05","BF-P06"}, "frontend":{"BF-P04","BF-P07","BF-P09"},
"qa":{"BF-P06","BF-P07","BF-P10","BF-P11"}, "security":{"BF-P08","BF-P11"},
"documentation":{"BF-P12","BF-P14"}, SPECIALIST:{"BF-P09","BF-P11"}}


def unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def validate(data):
    expected = {"schema_version":"1.0.0","registry_version":"proposal-1","status":"PROPOSED","protocol":"agent-protocol-proposal-1","adoption":"explicit_opt_in","runtime_enforcement":False}
    if set(data) != set(expected) | {"agents"} or any(data[k] != v for k,v in expected.items()):
        raise ValueError("invalid proposal identity or adoption")
    constitution = yaml.safe_load((ROOT/"catalog/development-constitution.proposal.yaml").read_text(encoding="utf-8"))
    policies = {p["id"] for p in constitution["principles"]}
    specialists = yaml.safe_load((ROOT/"catalog/specialist-agents.proposal.yaml").read_text(encoding="utf-8"))["specialists"]
    if [s["id"] for s in specialists] != [SPECIALIST]:
        raise ValueError("specialist registry drift")
    roles = data["agents"]
    if [a["id"] for a in roles] != CORE + [SPECIALIST]:
        raise ValueError("role coverage or ordering")
    if len({a["authority"] for a in roles}) != 12:
        raise ValueError("duplicate primary authority")
    for a in roles:
        i = a["id"]
        short = i.split(":")[-1]
        path = ("agents/specialists/" if i == SPECIALIST else "agents/") + short + ".md"
        expected_keys = {"id","alias","kind","authority","policies","contract","version","human_approval","activation"}
        if set(a) != expected_keys or a["alias"] != "@"+short or a["contract"] != path or a["version"] != "proposal-2" or a["human_approval"] is not False:
            raise ValueError("invalid role identity or approval authority")
        if a["kind"] != ROLE_KIND[i] or a["authority"] != ROLE_AUTHORITY[i]:
            raise ValueError("role authority drift")
        if a["activation"] != ("public_indexable_surfaces_exist" if i == SPECIALIST else "scope_based"):
            raise ValueError("invalid activation")
        p = a["policies"]
        if not p or len(set(p)) != len(p) or not set(p) <= policies or not REQUIRED.get(i,set()) <= set(p):
            raise ValueError("invalid policy mapping")
        doc = (ROOT/path).read_text(encoding="utf-8")
        if doc.count("## Blueprint Factory constitution overlay (BF-OT-005, proposal)") != 1 or "explicitly adopted" not in doc:
            raise ValueError("missing adoption-bound overlay")
    if set(roles[-2]["policies"]) != policies:
        raise ValueError("auditor must review all policies")
    if specialists[0]["contract"] != roles[-1]["contract"] or specialists[0]["activation"]["condition"] != roles[-1]["activation"]:
        raise ValueError("specialist projection mismatch")


def main():
    data = json.loads((ROOT/"catalog/agent-policy-registry.proposal.json").read_text(encoding="utf-8"), object_pairs_hook=unique_pairs)
    validate(data)
    print("PASS 12 roles, 14 policies, canonical paths and authority boundaries")
    cases = {
        "missing role": lambda d:d["agents"].pop(),
        "duplicate role": lambda d:d["agents"].append(d["agents"][0]),
        "unknown role": lambda d:d["agents"][0].update(id="superagent"),
        "duplicate alias": lambda d:d["agents"][1].update(alias="@orchestrator"),
        "path substitution": lambda d:d["agents"][1].update(contract="../README.md"),
        "agent human approval": lambda d:d["agents"][0].update(human_approval=True),
        "implementer QA authority": lambda d:d["agents"][5].update(authority="verify_behavior"),
        "auditor implements": lambda d:d["agents"][10].update(kind="implementation"),
        "remove QA policy": lambda d:d["agents"][7]["policies"].remove("BF-P07"),
        "remove approval policy": lambda d:d["agents"][3]["policies"].remove("BF-P03"),
        "remove Postman policy": lambda d:d["agents"][5]["policies"].remove("BF-P06"),
        "unknown policy": lambda d:d["agents"][0]["policies"].append("BF-P99"),
        "incomplete audit": lambda d:d["agents"][10]["policies"].pop(),
        "unconditional specialist": lambda d:d["agents"][11].update(activation="scope_based"),
        "automatic adoption": lambda d:d.update(adoption="automatic"),
        "false runtime enforcement": lambda d:d.update(runtime_enforcement=True),
        "false stable status": lambda d:d.update(status="STABLE"),
    }
    for name, mutate in cases.items():
        candidate = deepcopy(data)
        mutate(candidate)
        try:
            validate(candidate)
        except ValueError:
            print("PASS negative:", name)
        else:
            raise AssertionError("accepted invalid registry: "+name)
    print("Agent policy registry: PASS (1 positive, 17 negative)")


if __name__ == "__main__":
    main()
