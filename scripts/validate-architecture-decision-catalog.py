#!/usr/bin/env python3
"""Validate the architecture question registry, not a project's approvals."""
from copy import deepcopy
import json
from pathlib import Path
import sys

from jsonschema import Draft202012Validator, ValidationError

ROOT = Path(__file__).resolve().parents[1]
GROUPS = [
    ("project", 8), ("backend", 8), ("data", 11), ("api", 11),
    ("web", 13), ("admin", 9), ("client", 13), ("security", 12),
    ("features", 11), ("operations", 13), ("quality", 13),
    ("discoverability", 7), ("api_qa", 8),
]
EXPECTED = {
    f"ARC-{i:03}": category
    for i, category in enumerate(
        [category for category, count in GROUPS for _ in range(count)], 1
    )
}
ANCHORS = {
    "ARC-003": "BF-P01", "ARC-031": "BF-P05",
    "ARC-112": "BF-P07", "ARC-113": "BF-P07",
    **{f"ARC-{i:03}": "BF-P09" for i in range(123, 130)},
    **{f"ARC-{i:03}": "BF-P06" for i in range(130, 138)},
}


def unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"), object_pairs_hook=unique_pairs)


def validate(data, validator):
    validator.validate(data)
    decisions = data["decisions"]
    ids = [d["id"] for d in decisions]
    if ids != list(EXPECTED):
        raise ValueError("expected exact original ordered ARC-001..137")
    for d in decisions:
        if d["category"] != EXPECTED[d["id"]]:
            raise ValueError("decision category drift")
        if d.get("policy") != ANCHORS.get(d["id"]):
            raise ValueError("constitution policy anchor drift")
        if any(link not in EXPECTED or link == d["id"] for link in d["related_decisions"]):
            raise ValueError("unknown or self compatibility link")
        if not d["question"].startswith("¿") or not d["question"].endswith("?"):
            raise ValueError("interview question must be explicit")
        if any(not option.strip() for option in d["options"]):
            raise ValueError("blank option")
        if len({option.strip().casefold() for option in d["options"]}) != len(d["options"]):
            raise ValueError("duplicate normalized option")


def main():
    schema = load("schemas/architecture-decisions.proposal.schema.json")
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    data = load("catalog/architecture-decisions.proposal.json")
    validate(data, validator)
    print("PASS 137 decisions, 13 categories, policy anchors and compatibility links")
    cases = {
        "missing decision": lambda c: c["decisions"].pop(),
        "duplicate ID": lambda c: c["decisions"][1].update(id="ARC-001"),
        "unknown ID": lambda c: c["decisions"][0].update(id="ARC-999"),
        "reclassified decision": lambda c: c["decisions"][0].update(category="backend"),
        "silent default": lambda c: c["decisions"][8].update(default_selection="PHP"),
        "automatic approval": lambda c: c["decisions"][0].update(approval="agent"),
        "unjustified N/A": lambda c: c["decisions"][0].update(allow_na="always"),
        "skip applicability": lambda c: c["decisions"][0].update(applicability="optional"),
        "drop QA anchor": lambda c: c["decisions"][111].pop("policy"),
        "drop Postman anchor": lambda c: c["decisions"][130].pop("policy"),
        "unknown related decision": lambda c: c["decisions"][0].update(related_decisions=["ARC-999"]),
        "self link": lambda c: c["decisions"][0].update(related_decisions=["ARC-001"]),
        "blank option": lambda c: c["decisions"][0]["options"].append(" "),
        "duplicate option": lambda c: c["decisions"][0]["options"].append("greenfield"),
        "false approval": lambda c: c.update(status="APPROVED"),
        "missing question": lambda c: c["decisions"][0].pop("question"),
    }
    for name, mutate in cases.items():
        candidate = deepcopy(data)
        mutate(candidate)
        try:
            validate(candidate, validator)
        except (ValueError, ValidationError):
            print("PASS negative:", name)
        else:
            raise AssertionError("accepted invalid mutation: " + name)
    try:
        json.loads('{"status":"PROPOSED","status":"APPROVED"}', object_pairs_hook=unique_pairs)
    except ValueError:
        print("PASS negative: duplicate JSON key")
    else:
        raise AssertionError("accepted duplicate JSON key")
    print("Architecture decision catalog: PASS (1 positive, 17 negative)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
