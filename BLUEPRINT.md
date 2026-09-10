# Software Development Blueprint

> Stable release: **0.5.3**  
> Canonical repository: `LuisHdezE/SoftwareDevelopmentBlueprint`

## 1. Purpose and authority

Software Development Blueprint defines a reusable, versioned and machine-readable method for discovering, reconstructing, designing, implementing, validating, releasing and maintaining software with AI-assisted delivery.

The repository is the source of truth. Chat history, handoffs and reference pilots are context or evidence, never a higher authority than the versioned Blueprint and the consumer project's own approved artifacts.

When sources conflict, use this order:

1. the consumer project's declared Blueprint version and repository-owned approved contracts/evidence;
2. the canonical Blueprint artifacts for that version;
3. materialized Blueprint skills;
4. project-specific skills and documented local conventions;
5. reference-pilot findings;
6. chat/history.

A new Blueprint release does **not** automatically upgrade consumers. Adoption requires Compliance Review and an explicit consumer change.

## 2. Rule classifications

Blueprint uses these classifications:

- **REQUIRED**: mandatory when the phase/capability applies.
- **DEFAULT**: recommended baseline unless a documented decision justifies another choice.
- **CONDITIONAL**: required only when its applicability condition is true.
- **GENERATED**: produced artifact whose existence does not by itself imply review or approval.
- **BROWNFIELD**: required for existing-system alignment when applicable.

For generated visual assets the invariant is strict:

`GENERATED != REVIEWED != APPROVED`

## 3. Delivery modes

### 3.1 Greenfield

A new solution starts from Discovery, product scope and requirements. Interfaces may be scoped after Requirements Ready so client needs can inform architecture and API design, but executable API-backed client delivery remains blocked until the initial API Gate passes.

### 3.2 Brownfield

An existing system starts with inspection and reconstruction:

`Brownfield Inspection -> AS-IS -> Gap Analysis -> TO-BE`

The governing rule is **ALIGN, DO NOT REWRITE**.

Brownfield findings distinguish `OBSERVED`, `INFERRED` and `PROPOSED`. Existing behavior is inspected before replacement is proposed. Working functionality is preserved unless a change is justified, reviewed and safely cut over.

## 4. Canonical 0.5.3 flow

### 4.1 Planning and server baseline

```text
Discovery / Brownfield reconstruction
  -> Target Definition
  -> Requirements Ready
  -> Interface Scope Baseline Ready
  -> Architecture / Security / Data Ready
  -> API Contract Ready
  -> API Implementation + Architecture Implementation Conformance
  -> OpenAPI Validation
  -> Postman Operational Contract
  -> API QA
  -> API Gate
```

### 4.2 Executable client delivery

```text
API Gate
  -> Interface Inventory Ready
  -> Design System Ready
  -> Client Architecture Ready
  -> Functional Slice Ready
  -> Visual & Functional Review Pass
  -> Integration QA Pass
  -> Release Gate
  -> Operations
```

`Visual Identity` is CONDITIONAL. `Mockups / Prototypes` are a CONDITIONAL risk-reduction branch after Design System. Neither belongs to the mandatory principal sequence.

### 4.3 Conditional capabilities

Blueprint 0.5.3 adds **Optional Mobile Licensing** as a conditional capability for Android projects. Android consumers must explicitly answer `capabilities.mobile_licensing: true|false`. If enabled, `mobile_licensing_ready` must PASS before Release Gate. If disabled, licensing artifacts and the gate are not applicable.

The canonical licensing contract is `documentation/BLUEPRINT_V0_5_3_MOBILE_LICENSING.md` with machine-readable schema/template support and the reusable `dev-mobile-licensing` skill.

## 5. Requirements, architecture, security and data

Requirements define actors, authorization intent, functional and non-functional requirements, business rules, use cases, acceptance criteria and traceability before architecture/API implementation begins.

Architecture establishes domain boundaries, decisions, security model, authoritative data model, migrations, authentication/error/versioning strategy and durable business/security audit obligations. Threat modeling is conditional on risk.

Technical/operational logs and durable business/security audit are separate concerns. Critical authentication, role/permission, sensitive CRUD, meaningful state transition, financial, administrative, integration, tenant and security events require durable accountable evidence when applicable. Secrets must not leak into logs or audit.

When mobile licensing applies, Requirements and Architecture additionally define trial semantics, expiry behavior, activation UX, device binding, canonical signed payload, signing/verification boundaries, key lifecycle, backup separation, distribution-channel policy and mandatory positive/negative/tamper/interoperability/release tests.

## 6. Interface Scope Baseline

Blueprint 0.5.x uses an early interface maturity through `schemas/interface-inventory.schema.json` with:

`maturity: SCOPE_BASELINE`

It is created after Requirements Ready and before Architecture/API Contract Design.

Greenfield records intended interfaces derived from approved requirements and journeys. Brownfield records observed/reconciled existing interfaces before proposed replacement behavior.

The baseline may contain unresolved API needs. It must not fabricate `operationId`, permission, data or transition semantics that are not yet authoritative.

`interface_scope_ready` proves descriptive/planning completeness only. It never authorizes client implementation.

## 7. API contract, implementation, OpenAPI and API Gate

The API is the authoritative security and business boundary for API-backed clients.

API Contract Design defines stable operations, payload intent, authentication, permissions, errors, idempotency, request correlation, audit mapping and requirement traceability before implementation.

OpenAPI is the canonical machine-readable API contract. Every contracted HTTP operation uses a unique stable `operationId`. Postman operationalizes the validated OpenAPI contract and provides runtime coverage; it does not replace OpenAPI.

Initial `api_gate` is project-scoped and must PASS before API-backed executable client delivery begins.

### 7.1 Architecture Implementation Conformance

Blueprint 0.5.1 introduced the REQUIRED check:

`api.architecture_implementation_conformance`

0.5.3 retains it unchanged through compatible provenance.

The check proves that the implemented backend conforms to the architecture contract that was previously approved. Architecture design acceptance and architecture implementation conformance are distinct facts:

`architecture design acceptance != architecture implementation conformance`

Functional correctness, endpoint coverage, OpenAPI validity, Postman coverage and runtime QA do not by themselves prove architectural correctness.

When the approved architecture defines dependency direction, module boundaries, layer ownership, ports/adapters, framework isolation or equivalent constraints, conformance evidence SHOULD be executable wherever practical. Constraints that cannot reasonably be automated require explicit review evidence instead of silent assumption.

Blueprint does not universally prescribe Clean Architecture, DDD, Laravel or any fixed folder layout. The assertions must reflect the architecture the project actually approved.

`api_implemented` and `api_gate` both require this check.

### 7.2 API evolution after the initial baseline

Later API changes use impact-based revalidation rather than automatic global invalidation.

The machine-readable `api-impact` artifact records previous/new API revision, changed `operationId` values, cross-cutting contract areas, affected slice/platform scopes and required revalidation evidence.

Operation-local changes revalidate affected consumers only. Auth, authorization, security, error-contract, versioning or other cross-cutting changes may escalate to platform or project scope. Unrelated accepted evidence is preserved by default.

## 8. Executable Interface Inventory

After `api_gate = PASS`, the same interface contract progresses to:

`maturity: EXECUTABLE_INVENTORY`

It reconciles every early baseline interface as `COMMITTED`, `DEFERRED` or `DROPPED`.

Every committed interface records stable ID, platform, module, purpose, requirements, roles, permissions, data, actions, states, navigation, dependencies, priority and `slice_id`.

API-backed data/actions bind to real OpenAPI `operationId` values. Legitimate local/static behavior may explicitly have no API operation. Missing authoritative behavior is a blocker, not permission to invent an endpoint or business rule.

`interface_inventory_ready` represents the complete committed executable client backlog for the project scope.

## 9. Design System, Visual Identity and optional mockups

Design System is required for client delivery and defines reusable tokens, components, responsive behavior, semantic states and accessibility rules.

Visual Identity is CONDITIONAL. A logo or branding exercise is not fabricated merely to satisfy the process.

Mockups/prototypes are CONDITIONAL. They may be activated when visual/UX risk, pre-implementation approval, migration risk or future AI continuity justifies them.

When used, they reference executable inventory IDs, batches contain no more than 10 views, assets are repository-owned/versioned, generation/review/approval remain distinct, and `mockup_review_pass` is scoped to the interface slice.

A slice with no mockups is valid. Approved visual references may inform implementation, but static approval never replaces review of the real functional client.

## 10. Client Architecture

Client implementation requires an effective architecture contract before coding for the exact `interface_slice + platform`.

The stable composition is:

```text
Platform Client Architecture Baseline
  + Slice Architecture Binding/Override
  = Effective Client Architecture Contract
```

The Platform Client Architecture Baseline declares reusable platform/project decisions such as framework/toolkit, API client and OpenAPI path, auth/session lifecycle, credential storage, permission presentation, state/cache strategy, forms/error mapping, observability/correlation/redaction, accessibility, testing, offline policy and Brownfield coexistence/cutover/rollback when applicable.

The Slice Architecture Binding/Override binds the exact inventory IDs, routes, permissions, API revision and `operationId` set, async states, idempotency requirements and slice-specific cache/offline/testing overrides.

`visual_references.mode = none` is valid. `approved_optional` requires real approved/versioned paths.

`client_architecture_ready` remains scoped to `interface_slice + platform`. Web PASS never authorizes Android, and one slice never authorizes another.

## 11. Functional Interface Slice

The Functional Interface Slice is the canonical unit of client execution, review, QA and human acceptance.

Lifecycle:

```text
INVENTORIED -> READY -> IN_PROGRESS -> FUNCTIONAL -> ACCEPTED
```

Visual & Functional Review and Integration QA are quality gates, not lifecycle states.

A slice may become `FUNCTIONAL` only when the applicable DoD is evidenced, including routing/navigation, Design System implementation, real authoritative API integration when applicable, auth/session and permission-aware presentation, forms/error states, loading/empty/error/offline states, correlation/redaction, idempotency when required, responsive behavior, accessibility, tests, traceability, no hardcoded authoritative business data and no invented API capability/permission/state/transition.

Fixtures and isolated test data are permitted when explicitly non-authoritative. They cannot masquerade as production business truth.

## 12. BLOCKED_BY_API

`BLOCKED_BY_API` is an overlay condition, not a lifecycle state.

It is used only when a required authoritative API data source, operation, permission, state, transition or contract capability is missing or incompatible.

The affected client boundary stops. The client does not fabricate server behavior. Resolution occurs in a separate API/backend boundary and the slice resumes only after resolution/revalidation evidence exists.

Ordinary frontend bugs, styling uncertainty or local implementation defects are not `BLOCKED_BY_API`.

## 13. Visual & Functional Review

Review is performed on the actual functional client intended to ship.

It checks interface fidelity, Design System fidelity, API/permission fidelity, authoritative business-data behavior, interaction/error states, responsive behavior and accessibility. Approved mockups are comparison inputs only when they exist.

`review.human_complete` is REQUIRED. CI cannot infer human review.

## 14. Integration QA and acceptance

`integration_qa_pass` is scoped to `interface_slice + platform` and covers functional behavior, real API transport when applicable, integration, security, responsive behavior, accessibility, E2E and applicable idempotency/offline behavior.

`ACCEPTED` requires Functional DoD PASS, `visual_functional_review_pass = PASS`, `integration_qa_pass = PASS`, explicit human acceptance and no unresolved `BLOCKED_BY_API`.

Release Gate aggregates every committed slice required by the release. One accepted slice cannot unlock unrelated unfinished work.

### 14.1 Optional Mobile Licensing

When `capabilities.mobile_licensing = true`, Release Gate additionally requires `mobile_licensing_ready = PASS`.

The default contract uses a configurable trial, preserves read/backup/export after expiry, binds activation to the approved product/device identity, verifies asymmetric signatures in the customer app with public material only, isolates production signing authority in a separate protected issuer, keeps business backup separate from entitlement, requires key recovery/rotation and treats fully offline anti-tamper as best-effort rather than absolute.

The machine-readable profile requires 17 positive, negative, tamper, persistence, interoperability and release-build test obligations. A project-specific strategy may replace the default only through an approved ADR with equivalent or stronger evidence.

## 15. Cross-Artifact Semantic Integrity

JSON Schema validates shape. Blueprint validators also validate semantic truth across artifacts.

The canonical graph is:

```text
requirement
  -> interface
  -> permission
  -> OpenAPI operationId when applicable
  -> Functional Interface Slice
  -> Client Architecture
  -> test/evidence
  -> review / Integration QA
  -> human acceptance
```

Cross-Artifact Semantic Integrity rejects syntactically valid but fictitious IDs, unknown operationIds, platform namespace mismatches, invented permissions, incompatible architecture baselines, invalid evidence references, accepted slices without quality gates and unresolved blockers hidden behind acceptance.

## 16. Skills

Materialized `dev-*` skills teach an agent how to satisfy canonical contracts. They do not become product truth and cannot declare gates PASS on their own.

Blueprint 0.5.3 contains 15 materialized skills. The 14 pre-existing skills retain compatible 0.5.0 component provenance where their procedures did not change. `dev-mobile-licensing` is the new 0.5.3 materialized skill. Project-specific knowledge remains in the consumer repository.

## 17. Git and human governance

Dependent boundaries follow:

`verified main -> short-lived branch -> exact-head validation -> PR -> human decision -> verified merge -> post-merge validation`

One active implementation PR per dependent boundary is the default. CI success is evidence, not merge authorization. Human review/acceptance remains explicit wherever required.

### 17.1 CI Execution Portability

Blueprint 0.5.2 introduced **CI Execution Portability** and 0.5.3 preserves it unchanged.

Machine-readable contract:

`schemas/ci-runtime.schema.json`

Supported strategies are `github_hosted`, `self_hosted` and `hybrid`.

The evidence invariants remain:

`CI evidence semantics != runner ownership`

`pre-execution infrastructure failure != test failure`

A hosted or self-hosted PASS is valid only when it preserves the required exact candidate SHA, repository-owned workflow, check execution, scope, logs/artifacts and human decision separation.

For persistent self-hosted execution: trusted repository code only, fork PRs outside the persistent lane, no persistent repository secrets, least-privilege workflow permissions, workspace cleanup and a runner update policy.

Runner/container infrastructure remains independent from the product's `capabilities.docker`.

### 17.2 Optional Mobile Licensing governance

The Android applicability question is mandatory, but licensing itself is not. Enabling the capability materializes a licensing profile and makes the licensing checks/gate applicable. Disabling it leaves those obligations N/A.

A production private signing key or minting-capable shared secret in the customer application is a stop condition. Likewise, trial expiry may not hold user-owned data hostage, and portable business backup may not clone a device-bound entitlement.

## 18. Versioning and component provenance

Blueprint uses SemVer. Root `VERSION` identifies the stable Blueprint release consumed by projects.

For 0.5.3:

- root release identity: `0.5.3`;
- project/status/mobile-licensing schemas and canonical templates: `0.5.3`;
- checks/gates/skills/workflows: `0.5.3`;
- `dev-mobile-licensing`: `0.5.3`;
- CI runtime contract: `0.5.2-compatible`;
- Architecture Implementation Conformance: `0.5.1-compatible`;
- unchanged phases, reference-pilot and experience contracts: `0.5.0-compatible`.

Validators resolve repository-local pinned contracts and verify the allowed compatibility matrix. A component version never causes consumer auto-upgrade.

Historical release manifests and Compliance Reviews remain historical truth. A later release does not rewrite what an older review actually evaluated.

## 19. Reference pilots and consumer adoption

Reference pilots are non-normative. They prove or challenge Blueprint rules but cannot inject hidden product-specific requirements.

Consumer findings may be generalized only through an explicit Blueprint hardening boundary. 0.5.3 generalizes mobile licensing semantics from such a boundary without copying product-specific UI, currency, data or business logic.

Consumers remain on the version they explicitly declare. Adoption requires a separate Compliance Review that classifies changes as KEEP / ADOPT / MIGRATE / DEFER / N/A, explicit human approval and impact-appropriate revalidation.

Publishing 0.5.3 does not mutate any consumer repository.

## 20. Strategic boundary

Blueprint 0.5.3 does not solve every local-authoritative/offline Android applicability gap. In particular, the broader API-less/local-authoritative execution model remains outside this release and must be generalized separately rather than hidden behind invented API artifacts.

Blueprint Control Center remains a documented future capability, not part of Blueprint Core 0.5.3. The preferred sequence remains Blueprint Core -> reference/consumer pilots -> hardening -> Control Center when operating evidence justifies it.
