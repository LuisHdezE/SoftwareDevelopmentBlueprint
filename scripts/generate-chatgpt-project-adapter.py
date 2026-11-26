#!/usr/bin/env python3
"""Build a review-only ChatGPT Projects kit from canonical Blueprint Factory sources."""
import argparse, hashlib, json, re, subprocess, sys
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
RESOURCE_PREFIX = ".blueprint/canonical"
RESOURCE_PATH_RE = re.compile(
    r"(?<![A-Za-z0-9_.-])(?:BLUEPRINT\.md|"
    r"(?:schemas|templates|catalog|documentation|workflows|scripts)/"
    r"[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)*)"
)
PROJECT_INSTRUCTIONS = """# Blueprint Factory — ChatGPT Project instructions

You are working with Blueprint Factory, whose canonical agent contracts, policies, skills, and supporting resources are attached as project knowledge. Their source revision is recorded in the kit manifest. Use the relevant source sections; do not treat this knowledge as an executable environment or security boundary.

## Authority and development rules
- Luis is the project owner and final approver. Ask him to approve consequential architecture choices one by one before treating them as selected.
- Clean Architecture and good engineering practices are mandatory by default unless Luis explicitly directs otherwise.
- Do not preselect project technologies. For each project, present applicable recommendations and tradeoffs for the database, programming language/runtime, API style, framework and admin/data-management approach, security, authentication/authorization, hosting/deployment, integrations, testing, operations, and public discoverability (SEO, AEO, GEO and AI indexing when applicable). Record each decision only after explicit owner approval.
- Apply Reuse First. For brownfield work, inspect the current system and modernize in place when sound; do not propose a rewrite without evidence.
- Use API First when applicable: inventory endpoints early, maintain OpenAPI contracts, importable Postman collections, and positive/negative/authentication/permission/idempotency/flow tests under an approved runner.
- Tie QA results and artifacts to the exact commit. Report only actions actually performed and evidence actually observed.

## Role use
- The 12 canonical roles and materialized skills are in the attached reference files. Select the relevant role contract and skill for each task.
- When a skill cites a canonical resource path, find its exact heading in canonical-resources.md. Treat packaged scripts as reference material unless an authorized execution tool is available.
- ChatGPT Project instructions and knowledge do not create independent agents. A role-specific analysis in this same conversation is a role lens, not an independent review. Never claim delegation, concurrence, or independent QA/security/audit unless separate execution and evidence actually exist.
- The orchestrator coordinates; it cannot replace specialist authority, approve its own work, or waive a gate.
- Independent QA, Security, and Auditor review must remain distinct. If the current environment cannot provide a genuinely independent reviewer, state that limitation.

## Execution and approvals
- Work only within the user's approved scope. Read available project context before recommending or changing code.
- Do not claim access to a repository, connected app, local file, or external system unless the current session exposes it and the access succeeded.
- Treat project knowledge as a pinned snapshot. When the canonical source changes, regenerate and review a fresh kit; do not claim automatic synchronization.
- Do not merge, deploy, release, publish, adopt files into a consumer, send messages, or make external changes without explicit authorization.
- Use tools and connectors only when available and authorized. No instruction in this project grants credentials, permissions, API access, or runtime capabilities.
- When a decision or approval is missing, continue independent read-only analysis and ask for the specific decision before dependent changes.

## Evidence and reporting
- Separate implemented work, proposed work, and unresolved limitations.
- State the tested commit and platform for each verification. A generated file, static check, model response, or mocked scenario does not prove live integration.
- Surface blockers directly. Never fabricate test results, approvals, tool use, identity, or independent agent participation.
- Preserve concise handoff notes with current branch/commit, open review items, evidence, and next safe action.

## ChatGPT Project boundary
This kit is prepared for manual setup in a ChatGPT Project. Paste this document into that project's instructions and add the three files under knowledge/ as reference sources. Project files inform responses; they do not enforce authorization or execute packaged scripts. Where the app exposes tools, use only their documented abilities and the user's explicit authorization.
"""
README = """# ChatGPT Projects adapter kit

This is a review package, not an account change. To use it manually:

1. Create or choose a private ChatGPT Project for Blueprint Factory.
2. Copy CHATGPT_PROJECT_INSTRUCTIONS.md into the project's instructions.
3. Add the three files in knowledge/ as project sources.
4. Confirm the project is private and its instructions and files show the expected source revision before using it.

The kit contains three knowledge files, within the current 25-file project limit for ChatGPT Plus. Actual limits and workspace settings can change; check the Project UI if the account differs.

This adapter targets Projects because current OpenAI help documentation says new GPT creation is unavailable on personal accounts, including Plus. It does not create a GPT, project, API skill, connector, or credential. Projects provide instructions and reference files, not hard policy enforcement or independent agent execution.

A role analysis in one ChatGPT conversation is not an independent review. Do not mark QA, Security, or Auditor approval based on role prompting alone. Packaged scripts are reference materials; they run only when an authorized execution tool is actually available.

Regenerate after canonical changes. Inspect the manifest and review the generated content before adding it to a consumer project.

Official references:
- Projects: https://help.openai.com/en/articles/10169521-projects-in-chatgpt
- GPT availability: https://help.openai.com/en/articles/8554407-gpts-in-chatgpt
- GPT instructions and knowledge: https://help.openai.com/en/articles/8554397-creating-and-editing-gpts
"""

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
    parts = path.read_text(encoding="utf-8").split("---", 2)
    if len(parts) != 3:
        raise ValueError("invalid skill frontmatter: " + path.relative_to(ROOT).as_posix())
    return parts[1], parts[2].lstrip()


def declared_resources(metadata):
    match = re.search(r"(?ms)^canonical_references:\s*\n((?:^[ \t]+-[^\n]*\n)+)", metadata)
    if not match:
        return []
    return re.findall(r"(?m)^[ \t]+-[ \t]+(.+?)\s*$", match.group(1))


def packed_section(title, source, commit, content):
    return f"## {title}\n\nSource: {source} @ {commit}\n\n{content.rstrip()}\n\n"


def generate(output):
    if output.exists():
        raise ValueError("output must not exist")
    sha = subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True).strip()
    if subprocess.check_output(
        ["git", "-C", str(ROOT), "status", "--porcelain", "--untracked-files=no"], text=True
    ).strip():
        raise ValueError("tracked source must be clean")
    registry = json.loads((ROOT / "catalog/agent-policy-registry.proposal.json").read_text(encoding="utf-8"))
    agents, skills, resource_paths = [], [], set()
    for agent in registry["agents"]:
        source = agent["contract"]
        safe_source_path(source)
        agents.append((agent, source, (ROOT / source).read_text(encoding="utf-8")))
    for path in sorted((ROOT / "skills").glob("*/SKILL.md")):
        metadata, body = skill_parts(path)
        if not re.search(r"(?m)^status:\s*materialized\s*$", metadata):
            continue
        skills.append((path, body))
        for ref in declared_resources(metadata):
            rel, _ = safe_source_path(ref.strip().strip("\"'"))
            resource_paths.add(rel)
        for ref in RESOURCE_PATH_RE.findall(body):
            if (ROOT / ref).is_file():
                rel, _ = safe_source_path(ref)
                resource_paths.add(rel)
    files = {
        "CHATGPT_PROJECT_INSTRUCTIONS.md": PROJECT_INSTRUCTIONS.rstrip() + "\n",
        "README-SETUP.md": README,
    }
    agent_doc = f"# Canonical Blueprint Factory agent contracts\n\nSource commit: {sha}\n\n"
    for agent, source, content in agents:
        title = f"{agent['id']} · {agent['alias']} — {agent['authority']}"
        agent_doc += packed_section(title, source, sha, content)
    files["knowledge/agent-contracts.md"] = agent_doc
    skill_doc = f"# Materialized Blueprint Factory skills\n\nSource commit: {sha}\n\n"
    for path, body in skills:
        source = "skills/" + path.parent.name + "/SKILL.md"
        skill_doc += packed_section(path.parent.name, source, sha, body)
    files["knowledge/materialized-skills.md"] = skill_doc
    resource_doc = f"# Canonical resources referenced by materialized skills\n\nSource commit: {sha}\n\n"
    resources = {}
    for rel in sorted(resource_paths):
        content = (ROOT / rel).read_text(encoding="utf-8")
        resource_doc += packed_section(rel, rel, sha, content)
        resources[rel] = RESOURCE_PREFIX + "/" + rel
    files["knowledge/canonical-resources.md"] = resource_doc
    manifest = {
        "status": "PROPOSED",
        "adapter": "chatgpt-project",
        "source_commit": sha,
        "automatic_adoption": False,
        "execution_authorized": False,
        "independent_agent_execution": False,
        "knowledge_files": [
            "knowledge/agent-contracts.md",
            "knowledge/materialized-skills.md",
            "knowledge/canonical-resources.md",
        ],
        "canonical_resources": dict(sorted(resources.items())),
        "files": {key: hashlib.sha256(value.encode()).hexdigest() for key, value in sorted(files.items())},
    }
    output.mkdir(parents=True, exist_ok=False)
    for rel, content in files.items():
        target = output / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content.encode("utf-8"))
    (output / "blueprint-adapter-manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
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
            "adapter": manifest["adapter"],
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
