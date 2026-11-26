# BF-OT-011 — Claude Code adapter proposal

Generate from a clean tracked checkout with python scripts/generate-claude-code-adapter.py --output NEW_DIRECTORY. The bundle is a review candidate, not an installation or authorization. Review its manifest and conflicts before adopting any files into a consumer.

The generator creates twelve bf-* agents and every skill marked materialized. It parses each skill's canonical_references, adds referenced text resources and referenced companion scripts beneath .blueprint/canonical/, preserves each source path below that namespace, and rewrites the skill's path references to the bundled location. The manifest maps source paths to bundle paths and records SHA-256 for every generated and copied file. This namespace avoids silently overwriting consumer files. The generated bundle is self-contained for those materialized skill references; consumer-owned architecture ledgers and approved task packets remain external inputs.

Canonical agent contracts and skills remain the sole source of truth. The manifest pins source HEAD. Native names use bf-*; select an agent with Claude Code --agent bf-architect or ask bf-orchestrator to route. The installed Windows CLI 2.1.325 exposes --agent, --agents, --print, structured output and tool controls. Runtime loading and model execution are separate acceptance tests.

For orchestration, require actual subagent invocation evidence and prerequisite handoffs. Parallelism is permitted only for independent scopes and must be confirmed from runtime evidence. No automatic permission escalation, consumer adoption, merge, deploy or release.

The generated bundle provides instruction-level governance, not a sandbox or authenticated gate. Human review must verify source provenance, consumer adoption, runtime permissions and independent QA. Native agent discovery, skill loading, sequential delegation and concurrent delegation must be tested separately. No consumer adoption occurs in this proposal.
