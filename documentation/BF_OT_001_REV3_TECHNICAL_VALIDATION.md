# BF-OT-001 REV3 — Technical consolidation and regression evidence

Status: PARTIAL AUDIT / PROPOSAL. Date: 2026-11-25/26 America/Montevideo.

## Control-plane boundary
Source tree inspection of ControlCenter main 468a167f9d7a9289e58489a1af4b930ee6e2d203 found Projects and Intake aggregates, ports, use cases, Eloquent adapters, controllers and unit/integration/architecture tests. Architecture approval and accepted requirement/decision aggregates are not established by this inspection. Dashboard foundation a085c383c5d6c6226a5c727bfbde111f08fb2b04 contains repository sync, scan, Blueprint registry/parser/fetcher, compliance evaluator and CI/drift/portfolio controllers. Presence is not runtime acceptance. Proposed division: ControlCenter owns intake, project decisions and human approvals; Dashboard owns read-only observation, CI and compliance views. Master owns normative rules. No merger, retirement or consumer write authorization.

## Fresh execution
Elena, isolated temporary checkout of exact candidate ca72f3e1ad2204c91e55604fbeff22469755f950. Windows Python 3.12.4, PyYAML 6.0.3, jsonschema 4.26.0. This differs from CI Python 3.14/PyYAML 6.0.2; no CI equivalence claimed. All exit codes individually captured. Existing local development repos untouched. Initial shell quoting error corrected before clone.

| Validator | Exit |
|---|---:|
| validate-agent-protocol.py | 0 |
| validate-agent-workflow-integration.py | 0 |
| validate-public-discoverability.py | 0 |
| validate-agent-system.py | 0 |
| validate-planner-task-packet-boundary.py | 0 |
| validate-agent-run.py templates/agent-run.example | 0 |
| validate-project-agent-adoption.py templates/project-agent-consumer.example/adoption.yaml --project-root templates/project-agent-consumer.example --run-dir templates/project-agent-consumer.example/.blueprint/agents/runs/BP-CART-001 | 0 |
| validate-api-authority-v055-dev.py | 0 |
| validate-ci-runtime.py | 0 |
| validate-client-architecture.py | 0 |
| validate-client-slice-authority-v055-dev.py | 0 |
| validate-generic-compliance-v055-dev.py | 0 |
| validate-integration-qa-authority-v055-dev.py | 0 |
| validate-mobile-licensing.py | 1 |
| validate-mobile-licensing-boundary.py | 1 |
| validate-reference-pilot-compliance.py | 0 |
| validate-platform-matrix-v055-dev.py | 0 |
| validate-development.py | 0 |
| validate-workflow-applicability-v055-dev.py | 0 |
| validate-webblueprint-pilot-v055-dev.py | 0 |
| validate-release-closure-v055.py | 0 |
| validate-release-v054.py | 1 |
| validate-experience-artifacts.py | 0 |
| validate-skills.py | 1 |

Totals 24 invocations: 20 exit 0, 4 exit 1. Seven agent-specific validators all passed, including positive/negative fixtures. Example run uses synthetic candidate 1234567 and is not a real independent agent execution.

## Baseline differential
Repeated four failed commands on separate detached worktree of main fcd92a52596db5ddd070002eb3f7f2ce2eef0bbf. All four reproduced with identical reasons:
- mobile-licensing and boundary: require VERSION=0.5.3, got 0.5.4.
- release-v054: DEVELOPMENT_VERSION must be removed from stable 0.5.4.
- skills: requires stable root VERSION=0.5.3, got 0.5.4.

These are pre-existing version/applicability failures, not evidence of a new agent regression. Workflow inspection confirms mobile and skill workflows select historical scripts when DEVELOPMENT_VERSION exists; release validation selects stable v054 based on VERSION alone. Requires separate governed CI dispatch correction and Linux validation. Do not change VERSION or remove DEVELOPMENT_VERSION to manufacture green status. No blanket PASS.

## Remaining
Fresh exact-head CI on compatible Linux environment, correction proposal for version-aware dispatch without changing frozen release semantics, full architecture decision crosswalk, independent review, and explicit human approval of consolidation route. No merge or release. This evidence refers to tested SHA, not the new documentation commit. Temporary clone/worktree remain on Elena.
