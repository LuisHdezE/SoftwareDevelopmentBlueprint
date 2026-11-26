#!/usr/bin/env python3
"""Regression tests for generated, non-installed Antigravity bundle."""
import hashlib, importlib.util, json, re, tempfile
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("adapter", ROOT / "scripts/generate-antigravity-adapter.py")
adapter = importlib.util.module_from_spec(spec); spec.loader.exec_module(adapter)
with tempfile.TemporaryDirectory() as tmp:
    first, second = Path(tmp) / "first", Path(tmp) / "second"
    manifest = adapter.generate(first); repeated = adapter.generate(second)
    assert manifest == repeated
    assert manifest["execution_authorized"] is False
    assert manifest["automatic_adoption"] is False
    assert manifest["platform_permissions_assigned"] is False
    print("PASS deterministic manifest; no adoption, authorization, or permission grants")
    registry = json.loads((ROOT / "catalog/agent-policy-registry.proposal.json").read_text(encoding="utf-8"))
    agents = list((first / ".agents/agents").glob("*.md"))
    assert len(agents) == len(registry["agents"]) == 12
    for role in registry["agents"]:
        name = "bf-" + role["alias"].removeprefix("@")
        generated = (first / ".agents/agents" / (name + ".md")).read_text(encoding="utf-8")
        assert f"name: {name}\n" in generated
        assert (ROOT / role["contract"]).read_text(encoding="utf-8") in generated
        assert "tools:" not in generated and "commandExecutionPolicy:" not in generated
    print("PASS 12 agent definitions with no platform permission fields")
    assert len(manifest["canonical_resources"]) >= 30
    for source, destination in manifest["canonical_resources"].items():
        assert destination.startswith(".blueprint/canonical/")
        assert (first / destination).read_text(encoding="utf-8") == (ROOT / source).read_text(encoding="utf-8")
    for generated_path, digest in manifest["files"].items():
        raw = (first / generated_path).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == digest
        assert raw == (second / generated_path).read_bytes()
    print("PASS canonical resources, hashes and deterministic bytes")
    materialized_count = 0
    for skill_path in sorted((ROOT / "skills").glob("*/SKILL.md")):
        parts = skill_path.read_text(encoding="utf-8").split("---", 2)
        if len(parts) != 3 or not re.search(r"(?m)^status:\s*materialized\s*$", parts[1]): continue
        materialized_count += 1
        generated_skill = first / ".agents/skills" / ("bf-" + skill_path.parent.name) / "SKILL.md"
        generated_body = generated_skill.read_text(encoding="utf-8")
        assert re.match(r"(?s)^---\nname: bf-[a-z0-9-]+\ndescription: .+?\n---\n", generated_body)
        for reference in adapter.declared_resources(parts[1]):
            reference = reference.strip().strip("\"'")
            destination = manifest["canonical_resources"][reference]
            assert (first / destination).is_file() and destination in generated_body
    assert materialized_count == 16
    assert len(list((first / ".agents/skills").glob("*/SKILL.md"))) == materialized_count
    print("PASS 16 native skills and resolvable canonical references")
    root_policy = (first / "GEMINI.md").read_text(encoding="utf-8")
    assert "human authorization" in root_policy and "not installed automatically" in root_policy
    assert "Source candidate: " + manifest["source_commit"] in root_policy
    assert not (first / ".agents/workflows").exists()
    assert (first / "blueprint-adapter-manifest.json").is_file()
    print("PASS root policy, pinned source and no deprecated workflow output")
    try: adapter.safe_source_path("../outside.txt")
    except ValueError: print("PASS unsafe resource path rejected")
    else: raise AssertionError("unsafe canonical resource path accepted")
    try: adapter.generate(first)
    except ValueError: print("PASS existing output blocked")
    else: raise AssertionError("overwrites existing output")
    print("PASS Antigravity adapter generation and safety (8 scenarios)")
