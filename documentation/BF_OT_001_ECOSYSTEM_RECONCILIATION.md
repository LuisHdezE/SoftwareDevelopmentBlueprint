# BF-OT-001 — Ecosystem reconciliation: initial inventory and mandate

Date: 2026-11-25 (America/Montevideo).
Status: INITIAL INVENTORY / NOT ACCEPTED / NO RELEASE PROMOTION.
Owner mandate: evolve the existing Blueprint ecosystem, reuse existing agents, support ChatGPT, Claude Code and Antigravity, and preserve explicit owner architecture approval.

## Observed baselines

| Repository | Observed tree SHA | Role to verify |
| --- | --- | --- |
| SoftwareDevelopmentBlueprint main | fcd92a52596db5ddd070002eb3f7f2ce2eef0bbf | Canonical methodology |
| SoftwareDevelopmentBlueprint blueprint/consumer-agent-adoption | 6683bd5e06bab6c53188f7e7a93caf6e7d678879 | Candidate agent integration baseline |
| WebBlueprint main | 6154927bbbad37ddb5372351a1298920c876128d | Web standards/tooling |
| ApiBlueprint main | b9e4ff6d702e6a0e7a136d76be86691cbb30b214 | API contracts/export/testing |
| Blueprint-ControlCenter main | 468a167f9d7a9289e58489a1af4b930ee6e2d203 | Control/adapters |
| Blueprint-Dashboard blueprint-dashboard/foundation | a085c383c5d6c6226a5c727bfbde111f08fb2b04 | Registry/monitoring |

Tree SHAs are returned by the tree API; verify exact commit ancestry separately. VERSION=0.5.4, DEVELOPMENT_VERSION=0.5.5-dev. Stable documentation describes 29 phases, 146 checks, 19 gates and 16 materialized skills. Do not replace these with a parallel workflow. The 0.5.5 RC is frozen; do not alter VERSION, DEVELOPMENT_VERSION, tags or consumers.

## Existing agent work

PR #73 is OPEN, head 6683bd5e06bab6c53188f7e7a93caf6e7d678879, base blueprint/agent-system-validation at 514520a7ade4914b6318fbcc063391958f764df9. It is a candidate working base, not a stable release or proof of full ancestry. Review the complete stacked PR graph including #57–61 and #73, identify divergent work, verify CI for exact heads and reconcile before promotion. No merge authorized by this document.

Existing core definitions: orchestrator, analyst, planner, architect, database, backend, frontend, qa, security, documentation, auditor. Existing conditional specialist: search-ai-discoverability. Preserve stable IDs and separation of authority; do not duplicate existing roles. Existing artifacts include agent contract, handoff, orchestration, specialist registry, task packet, run bundle and explicit consumer adoption schemas/validators. agents/README.md still describes an early increment; reconcile stale descriptions with actual definitions.

ApiBlueprint contains postman/ApiBlueprint.generated.postman_collection.json, postman/ApiBlueprint.local.postman_environment.json, postman/operation-coverage.json, scripts/run-postman-operational-contract.sh and tests/Feature/PostmanOperationalContractTest.php. Master contains skills/dev-postman-qa/SKILL.md. WebBlueprint has qa/ and React/Vite source. ControlCenter has docs/architecture/adr/ADR-004_VERSIONED_BLUEPRINT_ADAPTERS.md. Dashboard has agent instructions and registry ingestion code. Presence does not certify functionality.

## Owner requirements to reconcile

- Clean Architecture and engineering good practices mandatory by default; explicit owner-approved documented exceptions only. Existing brownfield ALIGN, DO NOT REWRITE remains; deviations must be inventoried and approved, not silently rewritten.
- Architecture Approval Gate: exhaustive catalog, stable decision IDs, plain-language questions, options, compatibility, recommendation and explicit individual owner approval including justified N/A. No implementation before applicable decisions are approved; changes invalidate affected approvals and evidence. Preserve existing ADRs and gates; map rather than replace. The conversational catalog ARC-001..137 is a draft, not normative yet.
- Architecture categories: project type/domain, languages/frameworks/versions, API authority/contracts, database/persistence/storage/history, frontend/state/server queries/responsive, admin (Filament or alternatives), mobile/desktop/offline/licensing, auth/security/audit, reports/BI/maps, SEO/GEO/AEO, deployment/CI/operations, testing and acceptance. Offer familiar technologies as options, never silently select.
- API-first when API applies: early endpoint inventory with operation IDs and requirement links, OpenAPI, Postman importable JSON with environments/templates, positive/negative/auth/permission/business assertions, chained flows, isolated test data and cleanup, coverage reconciliation and CLI CI reports. Never include secrets or execute destructive test collections on production. Respect legitimate api_optional projects; no invented backend.
- QA mandatory with evidence; browser execution required for applicable web behavior; platform-specific real execution for mobile/desktop where applicable. Missing execution is BLOCKED, not PASS. Existing independent QA/security/auditor authority preserved; disclose role simulation versus independent runtime.
- Public discoverability mandatory when PUBLIC_INDEXABLE exists; reuse existing specialist and gate. Private access control is real security, not robots directives; search crawling and training permissions separate.
- Persistent learning: proposed lessons with source, applicability, evidence, review, version and status. No automatic normative policy change, no secrets or private consumer domain data in shared library.
- Portable canonical agents and thin adapters for ChatGPT, Claude Code and Antigravity; verify actual supported mechanisms before implementation. Invocation by stable agent ID, pinned version/commit, project adoption, task packet, roles, evidence and approvals. No claim of independent parallel execution where not supported.

## Roadmap and gates for this lane

1. BF-OT-001: full ancestry/PR/CI inventory, content crosswalk, dependency map, duplicate/gap matrix; independent review and human decision on reconciliation strategy.
2. BF-OT-002: constitution and exception protocol aligned to canonical methodology.
3. BF-OT-003/004: decision catalog and approval contracts, validation and negative tests.
4. BF-OT-005/006: existing role registry/orchestration reconciliation; add roles only after gap proof.
5. BF-OT-007/008/009: integration of Web/API blueprints, API contract/Postman, QA and discoverability evidence.
6. BF-OT-010: governed learning.
7. BF-OT-011/012/013: portable adapters and capability tests.
8. BF-OT-014/015/016: control center/dashboard integration, pilot, independent audit and release proposal.

## Acceptance boundary

This initial inventory is documentation only. No validators or CI were executed for this order; no architecture gate, adoption or release PASS claimed. Remaining: full source inspection, exact ancestry, divergent branches, current CI evidence, complete ARC catalog transcription and crosswalk, adapter capability verification and independent audit. No consumer modifications, merges, releases or deployment.
