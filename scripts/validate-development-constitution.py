#!/usr/bin/env python3
"""Validate the proposal catalog, not consumer runtime compliance."""
from copy import deepcopy
import json
from pathlib import Path
import re
import sys

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]


class UniqueLoader(yaml.SafeLoader):
    """Reject duplicate keys instead of silently overwriting policy."""


def unique_mapping(loader, node):
    mapping = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node)
        if key in mapping:
            raise ValueError(f"duplicate YAML key: {key}")
        mapping[key] = loader.construct_object(value_node)
    return mapping


UniqueLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique_mapping
)


def validate(catalog, document, validator):
    validator.validate(catalog)
    expected = [entry["id"] for entry in catalog["principles"]]
    actual = re.findall(r"^- (BF-P\d{2}) — ", document, re.MULTILINE)
    if actual != expected:
        raise ValueError("constitution document policy IDs/order differ from catalog")


def main():
    schema = json.loads((ROOT / "schemas/development-constitution.proposal.schema.json").read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    catalog = yaml.load((ROOT / "catalog/development-constitution.proposal.yaml").read_text(encoding="utf-8"), Loader=UniqueLoader)
    document = (ROOT / catalog["source"]).read_text(encoding="utf-8")
    validate(catalog, document, validator)
    print("PASS constitution proposal: 14 pinned principles and document alignment")
    mutations = {
        "missing policy": lambda c: c["principles"].pop(),
        "duplicate policy": lambda c: c["principles"].__setitem__(1, c["principles"][0]),
        "weaken Clean Architecture": lambda c: c["principles"][0].update(applicability="optional"),
        "drop architecture approval": lambda c: c["principles"][2].update(exception="owner_approved"),
        "waive QA": lambda c: c["principles"][6].update(exception="owner_approved"),
        "weaken security": lambda c: c["principles"][7].update(applicability="optional"),
        "skip public discoverability": lambda c: c["principles"][8].update(applicability="optional"),
        "permit automatic adoption": lambda c: c.update(automatic_adoption=True),
        "claim approved status": lambda c: c.update(status="APPROVED"),
        "claim runtime enforcement": lambda c: c["enforcement"].update(state="ENFORCED"),
        "allow agent approval": lambda c: c["exception_policy"].update(approval_authority="agent"),
        "allow blanket waiver": lambda c: c["exception_policy"].update(blanket_waivers=True),
        "allow evidence-free PASS": lambda c: c["exception_policy"].update(missing_evidence_pass=True),
        "allow QA bypass": lambda c: c["exception_policy"].update(qa_bypass=True),
        "allow security bypass": lambda c: c["exception_policy"].update(security_bypass=True),
        "omit expiry field": lambda c: c["exception_policy"]["required_fields"].remove("expires_at"),
        "omit rejected exception block": lambda c: c["exception_policy"]["blocking_states"].remove("REJECTED"),
        "unknown policy field": lambda c: c.update(waiver=True),
    }
    for name, mutate in mutations.items():
        changed = deepcopy(catalog)
        mutate(changed)
        if validator.is_valid(changed):
            raise AssertionError(f"negative fixture accepted: {name}")
        print(f"PASS negative: {name}")
    try:
        validate(catalog, document.replace("- BF-P07 — ", "- BF-P99 — "), validator)
    except ValueError:
        print("PASS negative: document/catalog ID drift")
    else:
        raise AssertionError("document drift accepted")
    try:
        yaml.load("status: PROPOSED\nstatus: APPROVED\n", Loader=UniqueLoader)
    except ValueError:
        print("PASS negative: duplicate YAML key")
    else:
        raise AssertionError("duplicate YAML key accepted")
    print("Constitution proposal validation: PASS (1 positive, 20 negative)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
