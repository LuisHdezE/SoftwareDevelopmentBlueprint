#!/usr/bin/env python3
"""Regression tests for generated, non-installed Claude Code bundle."""
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import tempfile

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("adapter", ROOT / "scripts/generate-claude-code-adapter.py")
adapter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(adapter)

with tempfile.TemporaryDirectory() as tmp:
    first, second = Path(tmp) / "first", Path(tmp) / "second"
    manifest = adapter.generate(first)
    repeated = adapter.generate(second)
    assert manifest == repeated
    assert manifest["execution_authorized"] is False and manifest["automatic_adoption"] is False
    print("PASS deterministic manifest and no authorization")

    registry = json.loads((ROOT / "catalog/agent-policy-registry.proposal.json").read_text(encoding="utf-8"))
    agents = list((first / ".claude/agents").glob("*.md"))
    assert len(agents) == len(registry["agents"]) == 12
    for role in registry["agents"]:
        name = "bf-" + role["alias"].removeprefix("@")
        generated = (first / ".claude/agents" / (name + ".md")).read_text(encoding="utf-8")
        assert ("name: " + name + "\n") in generated
        assert (ROOT / role["contract"]).read_text(encoding="utf-8") in generated
    print("PASS 12 canonical agent definitions")

    assert len(manifest["canonical_resources"]) >= 30
    for source, destination in manifest["canonical_resources"].items():
        assert destination.startswith(".blueprint/canonical/")
        assert (first / destination).read_bytes() == (ROOT / source).read_bytes()
    for generated_path, digest in manifest["files"].items():
        raw = (first / generated_path).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == digest
        assert raw == (second / generated_path).read_bytes()
    print("PASS canonical resources, hashes and deterministic bytes")

    materialized_count = 0
    for skill_path in sorted((ROOT / "skills").glob("*/SKILL.md")):
        raw = skill_path.read_text(encoding="utf-8")
        parts = raw.split("---", 2)
        if len(parts) != 3 or not re.search(r"(?m)^status:\s*materialized\s*$", parts[1]):
            continue
        materialized_count += 1
        refs_match = re.search(
            r"(?ms)^canonical_references:\s*\n((?:^[ \t]+-[^\n]*\n)+)", parts[1]
        )
        if refs_match:
            refs = re.findall(r"(?m)^[ \t]+-[ \t]+(.+?)\s*$", refs_match.group(1))
            generated_skill = (first / ".claude/skills" / ("bf-" + skill_path.parent.name) / "SKILL.md")
            generated_body = generated_skill.read_text(encoding="utf-8")
            for reference in refs:
                reference = reference.strip().strip("\"'")
                destination = manifest["canonical_resources"][reference]
                assert (first / destination).is_file()
                assert destination in generated_body
    assert materialized_count == 16
    assert len(list((first / ".claude/skills").glob("*/SKILL.md"))) == materialized_count
    print("PASS 16 native skills with resolvable canonical references")

    try:
        adapter.safe_source_path("../outside.txt")
    except ValueError:
        print("PASS unsafe resource path rejected")
    else:
        raise AssertionError("unsafe canonical resource path accepted")

    try:
        adapter.generate(first)
    except ValueError:
        print("PASS existing output blocked")
    else:
        raise AssertionError("overwrites existing output")

    assert (first / "CLAUDE.md").is_file()
    assert (first / "blueprint-adapter-manifest.json").is_file()
    print("PASS Claude adapter generation and safety (8 scenarios)")
