#!/usr/bin/env python3
"""Regression checks for the review-only ChatGPT Projects adapter."""
import hashlib, importlib.util, json, re, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("adapter", ROOT / "scripts/generate-chatgpt-project-adapter.py")
adapter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(adapter)

with tempfile.TemporaryDirectory() as tmp:
    first, second = Path(tmp) / "first", Path(tmp) / "second"
    manifest = adapter.generate(first)
    assert manifest == adapter.generate(second)
    assert manifest["adapter"] == "chatgpt-project"
    assert manifest["execution_authorized"] is False
    assert manifest["automatic_adoption"] is False
    assert manifest["independent_agent_execution"] is False
    print("PASS deterministic manifest and no adoption, authorization, or delegation claims")

    registry = json.loads((ROOT / "catalog/agent-policy-registry.proposal.json").read_text(encoding="utf-8"))
    agent_doc = (first / "knowledge/agent-contracts.md").read_text(encoding="utf-8")
    assert len(registry["agents"]) == 12
    for role in registry["agents"]:
        contract = (ROOT / role["contract"]).read_text(encoding="utf-8")
        assert contract in agent_doc
        assert role["alias"] in agent_doc
    print("PASS all 12 canonical agent contracts preserved")

    skill_count = 0
    skill_doc = (first / "knowledge/materialized-skills.md").read_text(encoding="utf-8")
    for path in sorted((ROOT / "skills").glob("*/SKILL.md")):
        parts = path.read_text(encoding="utf-8").split("---", 2)
        if len(parts) != 3 or not re.search(r"(?m)^status:\s*materialized\s*$", parts[1]):
            continue
        skill_count += 1
        assert parts[2].lstrip() in skill_doc
    assert skill_count == 16
    print("PASS all 16 materialized skills preserved")

    assert len(manifest["canonical_resources"]) >= 30
    resource_doc = (first / "knowledge/canonical-resources.md").read_text(encoding="utf-8")
    for source, destination in manifest["canonical_resources"].items():
        assert destination.startswith(".blueprint/canonical/")
        assert f"## {source}\n" in resource_doc
        assert (ROOT / source).read_text(encoding="utf-8") in resource_doc
    for generated_path, digest in manifest["files"].items():
        raw = (first / generated_path).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == digest
        assert raw == (second / generated_path).read_bytes()
    print("PASS canonical references, exact source content, hashes and reproducible bytes")

    knowledge_files = manifest["knowledge_files"]
    assert len(knowledge_files) == 3
    for path in knowledge_files:
        assert (first / path).is_file()
    instructions = (first / "CHATGPT_PROJECT_INSTRUCTIONS.md").read_text(encoding="utf-8")
    for required in ("Clean Architecture", "one by one", "not an independent review",
                     "Never claim delegation", "Do not merge", "final approver"):
        assert required.lower() in instructions.lower()
    readme = (first / "README-SETUP.md").read_text(encoding="utf-8")
    assert "role analysis" in readme and "Data Controls" in readme
    assert len(list((first / "knowledge").glob("*.md"))) == 3
    print("PASS project instructions, approval boundaries and three-file kit")

    try:
        adapter.safe_source_path("../outside.txt")
    except ValueError:
        print("PASS unsafe source path rejected")
    else:
        raise AssertionError("unsafe source path accepted")
    try:
        adapter.generate(first)
    except ValueError:
        print("PASS existing output blocked")
    else:
        raise AssertionError("existing output overwritten")
    print("PASS ChatGPT Projects adapter safety (8 scenarios)")
