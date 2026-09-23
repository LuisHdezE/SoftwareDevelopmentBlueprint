#!/usr/bin/env python3
"""Generic fail-closed consumer Compliance Doctor for Blueprint 0.5.5-dev."""
from __future__ import annotations

import argparse
from collections import Counter
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_SCHEMA = ROOT / "schemas/generic-compliance-manifest-v055-dev.schema.json"
REPORT_SCHEMA = ROOT / "schemas/generic-compliance-report-v055-dev.schema.json"
CHECKS_PATH = ROOT / "catalog/checks.yaml"
APPLICABILITY_PATH = ROOT / "catalog/workflow-gate-applicability-v055-dev.yaml"

API_BACKED_EXAMPLE = ROOT / "templates/generic-compliance.api-backed-v055-dev.example.json"
API_OPTIONAL_EXAMPLE = ROOT / "templates/generic-compliance.api-optional-v055-dev.example.json"
FIXTURES_ROOT = ROOT / "tests/fixtures/generic-compliance"

VIRTUAL_PROVIDER_RUNTIME_CHECK = {
    "id": "qa.provider_runtime_transport",
    "phase": "integration_qa",
    "type": "REQUIRED",
    "verification": "evidence",
}

RESULT_STATUSES = ("PASS", "FAIL", "N/A", "BLOCKED")


def load(path: Path) -> Any:
    text = path.read_text(encoding="utf-8")
    return json.loads(text) if path.suffix == ".json" else yaml.safe_load(text)


def schema_errors(doc: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    return [
        f"{'/'.join(map(str, e.absolute_path)) or '<root>'}: {e.message}"
        for e in sorted(validator.iter_errors(doc), key=lambda item: list(item.absolute_path))
    ]


def require_schema(label: str, doc: dict[str, Any], schema: dict[str, Any]) -> None:
    errors = schema_errors(doc, schema)
    if errors:
        raise AssertionError(f"{label} invalid: {' | '.join(errors)}")


def run_prerequisites() -> None:
    if (ROOT / "DEVELOPMENT_VERSION").read_text(encoding="utf-8").strip() != "0.5.5-dev":
        raise AssertionError("Generic Compliance Doctor is valid only inside governed 0.5.5-dev lane")
    result = subprocess.run(
        [sys.executable, "scripts/validate-integration-qa-authority-v055-dev.py"],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        raise AssertionError(
            "Increment 4 prerequisite failed:\n"
            f"{result.stdout}\n{result.stderr}"
        )
    print("PASS prerequisite: Integration QA Authority Matrix")


def index_unique(items: list[dict[str, Any]], key: str, label: str) -> dict[str, dict[str, Any]]:
    indexed: dict[str, dict[str, Any]] = {}
    for item in items:
        value = item.get(key)
        if not isinstance(value, str) or not value:
            raise AssertionError(f"{label} item requires non-empty {key}")
        if value in indexed:
            raise AssertionError(f"duplicate {label} {key}: {value}")
        indexed[value] = item
    return indexed


def catalog_checks() -> dict[str, dict[str, Any]]:
    doc = load(CHECKS_PATH)
    items = doc.get("checks")
    if not isinstance(items, list):
        raise AssertionError("catalog/checks.yaml checks must be a list")
    checks = index_unique(items, "id", "catalog check")
    if VIRTUAL_PROVIDER_RUNTIME_CHECK["id"] in checks:
        raise AssertionError(
            "development-only qa.provider_runtime_transport leaked into stable catalog before release closure"
        )
    checks[VIRTUAL_PROVIDER_RUNTIME_CHECK["id"]] = VIRTUAL_PROVIDER_RUNTIME_CHECK
    return checks


def applicability_profile(api_mode: str) -> dict[str, Any]:
    doc = load(APPLICABILITY_PATH)
    if doc.get("target_version") != "0.5.5-dev":
        raise AssertionError("workflow applicability target version drifted")
    profiles = doc.get("profiles")
    if not isinstance(profiles, dict) or api_mode not in profiles:
        raise AssertionError(f"missing workflow applicability profile: {api_mode}")
    profile = profiles[api_mode]
    if not isinstance(profile, dict):
        raise AssertionError(f"invalid workflow applicability profile: {api_mode}")
    return profile


def check_applicability(
    check: dict[str, Any],
    manifest: dict[str, Any],
    profile: dict[str, Any],
) -> tuple[bool | None, str]:
    check_id = check["id"]
    api_mode = manifest["authority"]["api_mode"]
    workflow_mode = manifest["blueprint"]["workflow_mode"]
    capabilities = manifest["capabilities"]

    if check_id == "qa.provider_runtime_transport":
        if api_mode == "api_optional":
            return True, "API-optional consumers require provider/runtime transport evidence."
        return False, "Provider/runtime transport is development-only and N/A for API-backed consumers."

    if api_mode == "api_optional":
        if check_id == "qa.real_api_transport":
            return False, "Real API transport is N/A for API-optional consumers."
        if check.get("phase") in set(profile.get("phase_na", [])):
            return False, f"Phase {check.get('phase')} is N/A under API-optional authority."
        if check_id in set(profile.get("check_na", [])):
            return False, "Check is explicitly N/A under API-optional authority."
        if (
            capabilities.get("database") is False
            and check_id in set(profile.get("check_na_when_database_absent", []))
        ):
            return False, "Check is N/A because the consumer declares no authoritative database."

    if check.get("type") == "BROWNFIELD" and workflow_mode != "brownfield":
        return False, "Brownfield-only check is N/A for a greenfield consumer."

    capability = check.get("capability")
    if isinstance(capability, str) and not capabilities.get(capability, False):
        return False, f"Capability {capability} is disabled."

    if check.get("type") == "CONDITIONAL" and not isinstance(capability, str):
        conditions = manifest.get("conditions", {})
        if check_id not in conditions:
            return None, "Conditional applicability was not declared by the consumer manifest."
        if conditions[check_id] is False:
            return False, "Consumer explicitly declares the conditional check not applicable."

    return True, "Check is applicable to the declared consumer profile."


def evidence_version_is_accepted(evidence: dict[str, Any], manifest: dict[str, Any]) -> bool:
    version = evidence.get("blueprint_version")
    if not version:
        return True
    if evidence.get("grandfathered") is True:
        return True
    accepted_for = set(evidence.get("accepted_for", []))
    adopted = manifest["blueprint"]["adopted_version"]
    evaluation = manifest["blueprint"]["evaluation_version"]
    return version in {adopted, evaluation} or evaluation in accepted_for


def result(
    check_id: str,
    status: str,
    reason_code: str,
    rationale: str,
    evidence_refs: list[str] | None = None,
    declared_status: str | None = None,
) -> dict[str, Any]:
    value: dict[str, Any] = {
        "check_id": check_id,
        "status": status,
        "reason_code": reason_code,
        "rationale": rationale,
        "evidence_refs": evidence_refs or [],
    }
    if declared_status is not None:
        value["declared_status"] = declared_status
    return value


def evaluate_check(
    check_id: str,
    check: dict[str, Any] | None,
    assessment: dict[str, Any] | None,
    evidence_by_id: dict[str, dict[str, Any]],
    manifest: dict[str, Any],
    profile: dict[str, Any],
) -> dict[str, Any]:
    if check is None:
        declared = assessment.get("declared_status") if assessment else None
        return result(
            check_id,
            "FAIL",
            "CONTRACT_VIOLATION",
            "Manifest scopes an unknown Blueprint check ID.",
            declared_status=declared,
        )

    applicable, rationale = check_applicability(check, manifest, profile)
    declared = assessment.get("declared_status") if assessment else None

    if applicable is False:
        if assessment is not None and declared != "N/A":
            return result(
                check_id,
                "FAIL",
                "CONTRACT_VIOLATION",
                f"{rationale} Consumer declared {declared} instead of N/A.",
                assessment.get("evidence_refs", []),
                declared,
            )
        return result(
            check_id,
            "N/A",
            "NOT_APPLICABLE",
            rationale,
            assessment.get("evidence_refs", []) if assessment else [],
            declared,
        )

    if applicable is None:
        return result(
            check_id,
            "BLOCKED",
            "PREREQUISITE_BLOCKED",
            rationale,
            assessment.get("evidence_refs", []) if assessment else [],
            declared,
        )

    if assessment is None:
        return result(
            check_id,
            "FAIL",
            "MISSING_EVIDENCE",
            "Applicable check has no consumer assessment or evidence binding.",
        )

    if declared == "N/A":
        return result(
            check_id,
            "FAIL",
            "CONTRACT_VIOLATION",
            "Applicable Blueprint check cannot be declared N/A.",
            assessment.get("evidence_refs", []),
            declared,
        )

    if declared == "BLOCKED":
        return result(
            check_id,
            "BLOCKED",
            "PREREQUISITE_BLOCKED",
            assessment.get("rationale", "Consumer declares this check blocked by a prerequisite."),
            assessment.get("evidence_refs", []),
            declared,
        )

    if declared == "FAIL":
        return result(
            check_id,
            "FAIL",
            assessment["reason_code"],
            assessment["rationale"],
            assessment.get("evidence_refs", []),
            declared,
        )

    refs = assessment.get("evidence_refs", [])
    missing = [ref for ref in refs if ref not in evidence_by_id]
    if missing:
        return result(
            check_id,
            "FAIL",
            "MISSING_EVIDENCE",
            f"Referenced evidence IDs are absent from manifest: {', '.join(missing)}.",
            refs,
            declared,
        )

    missing_state = [ref for ref in refs if evidence_by_id[ref].get("state") == "MISSING"]
    if missing_state:
        return result(
            check_id,
            "FAIL",
            "MISSING_EVIDENCE",
            f"Evidence is declared missing: {', '.join(missing_state)}.",
            refs,
            declared,
        )

    stale = [ref for ref in refs if evidence_by_id[ref].get("state") == "STALE"]
    if stale:
        return result(
            check_id,
            "FAIL",
            "STALE_EVIDENCE",
            f"Evidence is stale: {', '.join(stale)}.",
            refs,
            declared,
        )

    mismatched = [
        ref for ref in refs
        if not evidence_version_is_accepted(evidence_by_id[ref], manifest)
    ]
    if mismatched:
        return result(
            check_id,
            "FAIL",
            "VERSION_MISMATCH",
            f"Evidence version is not accepted for this evaluation: {', '.join(mismatched)}.",
            refs,
            declared,
        )

    return result(
        check_id,
        "PASS",
        "PASS",
        "Applicable check has present, current and version-compatible evidence.",
        refs,
        declared,
    )


def build_report(manifest: dict[str, Any]) -> dict[str, Any]:
    manifest_schema = load(MANIFEST_SCHEMA)
    report_schema = load(REPORT_SCHEMA)
    Draft202012Validator.check_schema(manifest_schema)
    Draft202012Validator.check_schema(report_schema)
    require_schema("generic compliance manifest", manifest, manifest_schema)

    checks = catalog_checks()
    profile = applicability_profile(manifest["authority"]["api_mode"])
    evidence_by_id = index_unique(manifest["evidence"], "id", "evidence")
    assessments = index_unique(manifest["assessments"], "check_id", "assessment")

    scope = manifest["scope"]
    if scope["mode"] == "full":
        check_ids = list(checks)
    else:
        check_ids = scope["check_ids"]

    results = [
        evaluate_check(
            check_id,
            checks.get(check_id),
            assessments.get(check_id),
            evidence_by_id,
            manifest,
            profile,
        )
        for check_id in check_ids
    ]

    counts = Counter(item["status"] for item in results)
    summary = {status: counts.get(status, 0) for status in RESULT_STATUSES}
    summary["TOTAL"] = len(results)
    if summary["FAIL"] > 0:
        overall = "FAIL"
    elif summary["BLOCKED"] > 0:
        overall = "BLOCKED"
    else:
        overall = "PASS"

    consumer = {
        "id": manifest["consumer"]["id"],
        "repository": manifest["consumer"]["repository"],
    }
    if "snapshot" in manifest["consumer"]:
        consumer["snapshot"] = manifest["consumer"]["snapshot"]

    report = {
        "schema_version": "0.5.5-dev",
        "consumer": consumer,
        "evaluation": {
            "blueprint_version": manifest["blueprint"]["evaluation_version"],
            "adopted_version": manifest["blueprint"]["adopted_version"],
            "workflow_mode": manifest["blueprint"]["workflow_mode"],
            "api_authority_mode": manifest["authority"]["api_mode"],
            "scope_mode": scope["mode"],
        },
        "overall_status": overall,
        "summary": summary,
        "results": results,
    }
    require_schema("generic compliance report", report, report_schema)
    return report


def render_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# Blueprint Generic Compliance Doctor",
        "",
        f"- Consumer: `{report['consumer']['repository']}`",
        f"- Evaluation: `{report['evaluation']['blueprint_version']}`",
        f"- Adopted Blueprint: `{report['evaluation']['adopted_version']}`",
        f"- Workflow: `{report['evaluation']['workflow_mode']}`",
        f"- API authority: `{report['evaluation']['api_authority_mode']}`",
        f"- Overall: **{report['overall_status']}**",
        "",
        "## Summary",
        "",
        f"- PASS: {summary['PASS']}",
        f"- FAIL: {summary['FAIL']}",
        f"- N/A: {summary['N/A']}",
        f"- BLOCKED: {summary['BLOCKED']}",
        f"- TOTAL: {summary['TOTAL']}",
        "",
        "## Results",
        "",
        "| Check | Status | Reason | Evidence |",
        "| --- | --- | --- | --- |",
    ]
    for item in report["results"]:
        evidence = ", ".join(item["evidence_refs"]) or "-"
        rationale = item["rationale"].replace("|", "\\|").replace("\n", " ")
        lines.append(
            f"| `{item['check_id']}` | **{item['status']}** | "
            f"`{item['reason_code']}`: {rationale} | {evidence} |"
        )
    return "\n".join(lines) + "\n"


def write_report(report: dict[str, Any], json_path: Path | None, md_path: Path | None) -> None:
    if json_path is not None:
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if md_path is not None:
        md_path.parent.mkdir(parents=True, exist_ok=True)
        md_path.write_text(render_markdown(report), encoding="utf-8")


def assert_reason(report: dict[str, Any], check_id: str, status: str, reason_code: str) -> None:
    item = next((entry for entry in report["results"] if entry["check_id"] == check_id), None)
    if item is None:
        raise AssertionError(f"fixture did not report {check_id}")
    if item["status"] != status or item["reason_code"] != reason_code:
        raise AssertionError(
            f"{check_id}: expected {status}/{reason_code}, "
            f"got {item['status']}/{item['reason_code']}"
        )


def self_test() -> None:
    backed = build_report(load(API_BACKED_EXAMPLE))
    if backed["overall_status"] != "PASS":
        raise AssertionError("api-backed positive example must PASS")
    print("PASS positive: generic api-backed consumer")

    optional = build_report(load(API_OPTIONAL_EXAMPLE))
    if optional["overall_status"] != "PASS":
        raise AssertionError("api-optional positive example must PASS")
    assert_reason(optional, "api.auth_strategy", "N/A", "NOT_APPLICABLE")
    assert_reason(optional, "qa.real_api_transport", "N/A", "NOT_APPLICABLE")
    assert_reason(optional, "qa.provider_runtime_transport", "PASS", "PASS")
    print("PASS positive: generic api-optional consumer with honest N/A transport semantics")

    cases = [
        ("missing-evidence.json", "qa.security", "FAIL", "MISSING_EVIDENCE"),
        ("stale-evidence.json", "qa.security", "FAIL", "STALE_EVIDENCE"),
        ("version-mismatch.json", "qa.security", "FAIL", "VERSION_MISMATCH"),
        ("invalid-na-claim.json", "api.auth_strategy", "FAIL", "CONTRACT_VIOLATION"),
        ("blocked-prerequisite.json", "qa.security", "BLOCKED", "PREREQUISITE_BLOCKED"),
    ]
    for filename, check_id, status, reason_code in cases:
        report = build_report(load(FIXTURES_ROOT / filename))
        assert_reason(report, check_id, status, reason_code)
        if report["overall_status"] == "PASS":
            raise AssertionError(f"negative fixture unexpectedly passed: {filename}")
        print(f"PASS negative: {filename} -> {status}/{reason_code}")

    serialized = (
        MANIFEST_SCHEMA.read_text(encoding="utf-8")
        + REPORT_SCHEMA.read_text(encoding="utf-8")
        + Path(__file__).read_text(encoding="utf-8")
    ).lower()
    forbidden = [
        "care" + "shift-manager",
        "care" + "shift_manager",
        "luishdeze/" + "care" + "shift_manager",
        "luishdeze/" + "web" + "blueprint",
        "/" + "login",
        "/" + "checkout",
    ]
    found = [term for term in forbidden if term in serialized]
    if found:
        raise AssertionError(f"generic engine contains consumer/product constants: {found}")
    print("PASS genericity: engine contains no CareShift/WebBlueprint/product route constants")
    print("Generic Compliance Doctor validation PASS")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--report-json", type=Path)
    parser.add_argument("--report-md", type=Path)
    parser.add_argument("--skip-prerequisites", action="store_true")
    args = parser.parse_args()

    if not args.skip_prerequisites:
        run_prerequisites()

    if args.manifest is None:
        self_test()
        return 0

    manifest_path = args.manifest
    if not manifest_path.is_absolute():
        manifest_path = ROOT / manifest_path
    report = build_report(load(manifest_path))
    write_report(report, args.report_json, args.report_md)
    print(json.dumps(report["summary"], sort_keys=True))
    print(f"Generic Compliance Doctor: {report['overall_status']}")
    return 0 if report["overall_status"] == "PASS" else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, FileNotFoundError, json.JSONDecodeError, yaml.YAMLError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
