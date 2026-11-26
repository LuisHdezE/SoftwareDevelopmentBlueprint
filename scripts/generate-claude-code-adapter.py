#!/usr/bin/env python3
"""Generate a reviewable Claude Code bundle; never install into an existing project."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
RESOURCE_PREFIX = ".blueprint/canonical"
RESOURCE_PATH_RE = re.compile(
    r"(?<![A-Za-z0-9_.-])(?:BLUEPRINT\.md|"
    r"(?:schemas|templates|catalog|documentation|workflows|scripts)/"
    r"[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)*)"
)


def safe_source_path(value):
    if "\\" in value:
        raise ValueError("canonical resource paths must use POSIX separators")
    rel = PurePosixPath(value)
    if rel.is_absolute() or not rel.parts or any(part in ("", ".", "..") for part in rel.parts):
        raise ValueError("unsafe canonical resource path")
    source = (ROOT / Path(*rel.parts)).resolve()
    if not source.is_relative_to(ROOT.resolve()) or not source.is_file():
        raise ValueError("missing or unsafe canonical resource: " + value)
    return rel.as_posix(), source


def skill_parts(path):
    raw = path.read_text(encoding="utf-8")
    parts = raw.split("---", 2)
    if len(parts) != 3:
        raise ValueError("invalid skill frontmatter: " + path.relative_to(ROOT).as_posix())
    return raw, parts[1], parts[2].lstrip()


def declared_resources(metadata):
    match = re.search(
        r"(?ms)^canonical_references:\s*\n((?:^[ \t]+-[^\n]*\n)+)",
        metadata,
    )
    if not match:
        return []
    return re.findall(r"(?m)^[ \t]+-[ \t]+(.+?)\s*$", match.group(1))


def generate(output):
    if output.exists():
        raise ValueError("output must not exist")
    sha = subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True).strip()
    if subprocess.check_output(
        ["git", "-C", str(ROOT), "status", "--porcelain", "--untracked-files=no"], text=True
    ).strip():
        raise ValueError("tracked source must be clean")

    registry = json.loads((ROOT / "catalog/agent-policy-registry.proposal.json").read_text(encoding="utf-8"))
    files = {}
    resources = {}

    # Materialize exact skill references in an isolated namespace to avoid consumer path collisions.
    materialized = []
    resource_paths = set()
    for path in sorted((ROOT / "skills").glob("*/SKILL.md")):
        _raw, metadata, body = skill_parts(path)
        if not re.search(r"(?m)^status:\s*materialized\s*$", metadata):
            continue
        materialized.append((path, metadata, body))
        for ref in declared_resources(metadata):
            rel, _source = safe_source_path(ref.strip().strip("\"'"))
            resource_paths.add(rel)
        for ref in RESOURCE_PATH_RE.findall(body):
            candidate = ROOT / ref
            if candidate.is_file():
                rel, _source = safe_source_path(ref)
                resource_paths.add(rel)

    for rel in sorted(resource_paths):
        source = ROOT / rel
        try:
            content = source.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            raise ValueError("canonical resource is not UTF-8 text: " + rel) from exc
        destination = RESOURCE_PREFIX + "/" + rel
        files[destination] = content
        resources[rel] = destination

    for agent in registry["agents"]:
        name = "bf-" + agent["alias"].removeprefix("@")
        if not re.fullmatch(r"[a-z][a-z0-9-]+", name):
            raise ValueError("invalid native agent name")
        source = agent["contract"]
        body = (ROOT / source).read_text(encoding="utf-8")
        desc = f"Blueprint {agent['id']} role: {agent['authority']}. Activate only for approved scope."
        files[f".claude/agents/{name}.md"] = (
            f"---\nname: {name}\ndescription: {json.dumps(desc)}\nmodel: inherit\n---\n\n"
            + f"Source: {source} @ {sha}\n\n"
            + body
            + "\n\nMandatory: respect approved task scope, independent verification and human approval. "
            "This generated instruction is not execution authorization. Never bypass a blocked gate or approve merge/deploy.\n"
        )

    for path, _metadata, body in materialized:
        skill_name = path.parent.name
        if not re.fullmatch(r"[a-z0-9-]+", skill_name):
            raise ValueError("invalid skill name")
        for rel in sorted(resources, key=len, reverse=True):
            body = body.replace(rel, resources[rel])
        name = "bf-" + skill_name
        files[f".claude/skills/{name}/SKILL.md"] = (
            f"---\nname: {name}\ndescription: {json.dumps('Blueprint skill ' + skill_name + '; apply only within approved task scope.')}\n---\n\n"
            + f"Source: skills/{skill_name}/SKILL.md @ {sha}\n\n"
            + body
        )

    files["CLAUDE.md"] = (
        "# Blueprint Factory proposal adapter\n\n"
        "Source candidate: " + sha + "\n\n"
        "Canonical resources referenced by materialized skills are bundled under "
        ".blueprint/canonical/ with original paths preserved inside that namespace. "
        "Use these pinned files when applying the generated skills. Load the consumer-owned "
        "architecture ledger and approved task packet before work. Directly select the "
        "appropriate bf-* agent or ask bf-orchestrator to route. Never simulate independent "
        "approval. No merge/deploy/release without human authorization. Parallelism requires "
        "proven independence and verified platform support. This bundle grants no permissions.\n"
    )
    manifest = {
        "status": "PROPOSED",
        "source_commit": sha,
        "automatic_adoption": False,
        "execution_authorized": False,
        "canonical_resources": dict(sorted(resources.items())),
        "files": {key: hashlib.sha256(value.encode()).hexdigest() for key, value in sorted(files.items())},
    }
    output.mkdir(parents=True, exist_ok=False)
    for rel, content in files.items():
        path = output / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content.encode("utf-8"))
    (output / "blueprint-adapter-manifest.json").write_bytes(
        (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode("utf-8")
    )
    return manifest


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        manifest = generate(args.output)
        print(json.dumps({
            "status": "GENERATED_FOR_REVIEW",
            "source_commit": manifest["source_commit"],
            "files": len(manifest["files"]),
            "canonical_resources": len(manifest["canonical_resources"]),
            "execution_authorized": False,
        }))
        return 0
    except Exception as exc:
        print(json.dumps({"status": "BLOCKED", "finding": str(exc)}))
        return 1


if __name__ == "__main__":
    sys.exit(main())
