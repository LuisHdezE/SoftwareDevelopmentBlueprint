#!/usr/bin/env python3
from collections import Counter
from pathlib import Path
import json
import sys

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas/compliance-review.schema.json"
REVIEW_PATH = ROOT / "documentation/BLUEPRINT_V0_4_CARESHIFT_COMPLIANCE_REVIEW.json"
PILOTS_PATH = ROOT / "catalog/reference-pilots.yaml"


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    sys.exit(1)


schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
review = json.loads(REVIEW_PATH.read_text(encoding="utf-8"))
Draft202012Validator.check_schema(schema)
errors = sorted(Draft202012Validator(schema).iter_errors(review), key=lambda e: list(e.path))
if errors:
    for error in errors:
        print(f"SCHEMA ERROR {list(error.path)}: {error.message}")
    fail("compliance review schema validation")
print(f"PASS schema: {REVIEW_PATH.relative_to(ROOT)}")

ids = [finding["id"] for finding in review["findings"]]
if len(ids) != len(set(ids)):
    fail("finding IDs must be unique")
print(f"PASS finding IDs: {len(ids)} unique")

counts = Counter(finding["classification"] for finding in review["findings"])
expected = {key: counts.get(key, 0) for key in ["KEEP", "ADOPT", "MIGRATE", "DEFER", "N/A"]}
if review["summary"] != expected:
    fail(f"summary mismatch: expected {expected}, got {review['summary']}")
print(f"PASS summary counts: {expected}")

policy = review["policy"]
if policy != {
    "automatic_migration": False,
    "align_do_not_rewrite": True,
    "grandfather_existing_evidence": True,
    "consumer_mutated_by_review": False,
}:
    fail("Brownfield compliance policy changed")
print("PASS Brownfield policy: no automatic migration / no consumer mutation")

if review["recommendation"] != "ADOPT_INCREMENTALLY":
    fail("CareShift v0.4 recommendation must remain ADOPT_INCREMENTALLY")

class_by_id = {finding["id"]: finding["classification"] for finding in review["findings"]}
required_decisions = {
    "CRF-010": "MIGRATE",
    "CRF-013": "KEEP",
    "CRF-014": "DEFER",
    "CRF-015": "DEFER",
    "CRF-016": "DEFER",
    "CRF-018": "N/A",
    "CRF-021": "N/A",
    "CRF-022": "DEFER",
}
for finding_id, classification in required_decisions.items():
    if class_by_id.get(finding_id) != classification:
        fail(f"{finding_id} must remain {classification}")
print("PASS protected pilot decisions")

if counts.get("MIGRATE", 0) != 1:
    fail("V4-5 must keep exactly one migration decision for this reviewed snapshot")
if any(finding["destructive_rewrite_allowed"] for finding in review["findings"]):
    fail("destructive rewrite cannot be authorized by compliance review")
print("PASS ALIGN, DO NOT REWRITE enforcement")

sources = {(s["repository"], s["kind"], s["ref"]): s["sha"] for s in review["reviewed_sources"]}
required_sources = {
    ("LuisHdezE/SoftwareDevelopmentBlueprint", "blueprint", "main"):
        "fb5ea5f82c80bc4b7afe600834ca3f681254b70b",
    ("LuisHdezE/CareShift_Manager", "consumer_main", "main"):
        "afeb2f7928f884285d473f9989fb5acae650e9cc",
    ("LuisHdezE/CareShift_Manager", "tracked_branch", "blueprint/mockups-batch-01"):
        "81822e07397397e3beab7eb8d317b5d2c0243ab7",
}
for key, sha in required_sources.items():
    if sources.get(key) != sha:
        fail(f"review source drift for {key}: expected {sha}, got {sources.get(key)}")
print("PASS exact reviewed source snapshots")

pilots = yaml.safe_load(PILOTS_PATH.read_text(encoding="utf-8"))
pilot = next((p for p in pilots.get("pilots", []) if p.get("id") == "careshift-manager"), None)
if not pilot:
    fail("careshift-manager missing from reference pilot registry")
review_meta = pilot.get("last_compliance_review") or {}
if review_meta.get("artifact") != "documentation/BLUEPRINT_V0_4_CARESHIFT_COMPLIANCE_REVIEW.json":
    fail("reference pilot registry does not point to V4-5 review")
if review_meta.get("recommendation") != "ADOPT_INCREMENTALLY":
    fail("reference pilot recommendation drift")
if review_meta.get("consumer_version_change") != "DEFERRED":
    fail("CareShift consumer version must remain deferred")
print("PASS reference pilot registry binding")

summary = review["summary"]
print(
    "Blueprint V4-5 pilot compliance validation: PASS "
    f"({len(review['findings'])} findings; "
    f"KEEP {summary['KEEP']}, ADOPT {summary['ADOPT']}, MIGRATE {summary['MIGRATE']}, "
    f"DEFER {summary['DEFER']}, N/A {summary['N/A']})"
)
