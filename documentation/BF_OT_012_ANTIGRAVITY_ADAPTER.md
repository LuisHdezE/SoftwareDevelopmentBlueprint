# BF-OT-012 - Antigravity adapter proposal

Generate from a clean tracked checkout:

    python scripts/generate-antigravity-adapter.py --output NEW_DIRECTORY

The output is an isolated review bundle. The generator refuses an existing destination or a dirty tracked checkout. It does not install files into a consumer or modify Antigravity settings.

The bundle includes twelve canonical roles under .agents/agents/, materialized skills under .agents/skills/, a GEMINI.md workspace policy, and canonical text references under .blueprint/canonical/. The manifest records the source commit, source-to-bundle resource mapping, and SHA-256 of each generated file. Skill resource links are rewritten into the isolated namespace.

The adapter intentionally emits no tool allowlists or command execution policy. Runtime permissions remain under the consumer's control. The policy, agent and skill files are instructions; they do not authenticate approvals or enforce hard security boundaries. Consumer review must resolve collisions and confirm the active Antigravity version discovers the generated files before adoption.

Antigravity custom workflows are not generated because the platform documentation marks them deprecated. Repeatable processes use the native skill format. No consumer adoption, merge, deployment, or release is performed by this proposal.

## Acceptance evidence

Structural generation and integrity checks are automated by scripts/test-antigravity-adapter.py. Platform-native loading and orchestration are separate acceptance checks and must be reported only when run against the exact candidate. A generated file alone does not prove native runtime support.
