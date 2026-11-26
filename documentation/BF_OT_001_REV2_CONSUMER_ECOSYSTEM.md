# BF-OT-001 REV2 — Consumer ecosystem capability inventory

Date: 2026-11-25/26 (America/Montevideo); status PARTIAL AUDIT / PROPOSAL.
Method: GitHub default-branch README, repository tree, selected source/ADR/QA documents. No runtime tests or fresh CI execution.

## WebBlueprint
Source: https://github.com/LuisHdezE/WebBlueprint
Observed main tree identity 6154927bbbad37ddb5372351a1298920c876128d (from REV0; re-read tree in this inspection).
README describes React/Tailwind, mobile-first, public showcase, authenticated composer, export React/Vite ZIP, component catalog, living docs, Style 1, left navigation and reusable shell. These are product capabilities, not universal stack mandates.
docs/decisions/0008-contract-first-export-architecture.md: accepted ADR, pragmatic feature-first Clean Architecture, dependency boundaries, DTO/mappers, replaceable JSON/API adapters, selection=preview=export, minimal dependency closure, exported build/tests. Preserve this as reference for frontend bootstrap.
docs/reference/mandatory-qa-gate.md: ACTIVE; registered per-view browser scenarios, rendered PR before merge, exact production candidate and post-deploy verification, responsive/accessibility/runtime evidence and owner acceptance. qa/view-registry.json and qa/browser/ are reference implementation candidates; port requirements and evidence semantics, not product-specific selectors or automatic deployment. Browser QA only when applicable, absence of execution cannot PASS.
Reconcile WebBlueprint's mock-first contract workflow with master API authority: non-authoritative design/mock work can proceed in approved scope, but real API-backed executable client acceptance must respect canonical OpenAPI and API gate; no mock may certify authoritative business behavior.
Action: reuse composer/export as optional approved technology capability; import patterns and QA rules, not project-specific FixPhone or Volquetas data.

## ApiBlueprint
Source: https://github.com/LuisHdezE/ApiBlueprint
Observed main tree identity b9e4ff6d702e6a0e7a136d76be86691cbb30b214.
README describes Laravel 13, Clean Architecture, feature library and application catalog, selected endpoint export, OpenAPI, Sanctum/RBAC/rate limits, RFC 9457 errors, correlation IDs, pagination/filter/sort, idempotency/audit and ZIP acceptance. Do not infer all feature recipes implemented or impose Laravel globally.
docs/delivery/operational-contract-audit-qa.md records historical CI #111 run 35924101353 at 2dd30646036dfc56975e80f0969bc2808271db61: 15 requests, 36 assertions, zero failures, seven canonical operations/events. This is documentary evidence only in REV2, not a fresh CI query or universal endpoint/security PASS.
scripts/run-postman-operational-contract.sh inspected: exported ZIP, isolated SQLite, synthetic users/products, local runtime, pinned Newman 6.2.1, sanitized report, semantic audit verification. Existing collection/environment/operation-coverage and PostmanOperationalContractTest provide reference patterns. Review cleanup/isolation, assertions and sanitization before reuse; never run mutation scenarios against production.
Action: reuse feature/manifest composition for approved Laravel API; generalize early endpoint inventory, operationId mapping, OpenAPI/Postman and runtime acceptance into canonical methodology, not another competing contract.

## Blueprint-ControlCenter
Source: https://github.com/LuisHdezE/Blueprint-ControlCenter
Observed main tree identity 468a167f9d7a9289e58489a1af4b930ee6e2d203.
README claims bootstrap only, but repository docs/implementation/BCC-007..009 and code tree show later implementation artifacts. Do not treat stale README as current product truth. BCC-009 records Greenfield Intake capture/list/detail/classify/discard with non-authoritative candidate classification, explicit owner acceptance boundary and historical CI #45 on implementation SHA 008aaf57c815fbdf9008b6cf9bc3f1bdd40784bb; final acceptance and exact current CI not verified.
ADR-004_VERSIONED_BLUEPRINT_ADAPTERS.md is PROPOSED: pinned methodology rulesets, version-specific applicability/evidence/gates; not the same as IDE agent invocation adapters. Reuse as design input, not assumed accepted implementation.
Action: candidate host for project intake, architecture interview/decision ledger and evidence/readiness observation, subject to approved scope and actual source verification. Keep canonical methodology in master. No automatic approval or repo writes implied.

## Blueprint-Dashboard
Source: https://github.com/LuisHdezE/Blueprint-Dashboard
Observed default branch blueprint-dashboard/foundation tree identity a085c383c5d6c6226a5c727bfbde111f08fb2b04.
README describes Laravel/React monorepo. documentation/CURRENT_STATE.md describes foundation only, but tree contains registry ingestion/application/domain/infrastructure/controller code and a Postman collection; checkpoint is stale. ADR-010 accepted: V1 strictly read-only for external repos, no automated fixes/merges/mutations; any future write requires new ADR, permission model, approval workflow, audit and rollback.
Action: compare with ControlCenter capabilities before selecting a UI/control-plane direction. No parallel development of duplicated governance features. Preserve existing read-only boundary; no retirement or merger of products without owner decision.

## Proposed ownership map (not approved architecture)
- Master: normative rules, catalog, schemas, agent definitions, gate/evidence semantics and learning policy.
- WebBlueprint: web component catalog/composer and approved export implementation.
- ApiBlueprint: Laravel API feature catalog/composer and approved export implementation.
- ControlCenter: candidate governed intake, decision/evidence observation and version-aware assessments.
- Dashboard: candidate portfolio visualization/read-only registry, overlap with ControlCenter unresolved.
- IDE adapters: thin portable invocation/projection layer, separate from ruleset adapters; platform support still unverified.
- Consumer: project-owned requirements, explicit decisions, version pins, artifacts, code, QA and approvals.

## Next
Verify exact current refs and CI, compare ControlCenter/Dashboard source modules and acceptance states; inventory master architecture templates and gate projection; run inherited validator suite on exact consolidated candidate; record independent audit and obtain owner decision before promotion. No modifications to four consumers, no merge, no release, no deployment. REV2 is not full BF-OT-001 acceptance.
