# Software Development Blueprint

> Stable release: **0.5.0**  
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

A new solution starts from Discovery, product scope and requirements. Interfaces may be scoped after Requirements Ready so client needs can inform architecture and API design, but executable client delivery remains blocked until the initial API Gate passes.

### 3.2 Brownfield

An existing system starts with inspection and reconstruction:

`Brownfield Inspection -> AS-IS -> Gap Analysis -> TO-BE`

The governing rule is **ALIGN, DO NOT REWRITE**.

Brownfield findings distinguish `OBSERVED`, `INFERRED` and `PROPOSED`. Existing behavior is inspected before replacement is proposed. Working functionality is preserved unless a change is justified, reviewed and safely cut over.

## 4. Canonical 0.5.0 flow

### 4.1 Planning and server baseline

```text
Discovery / Brownfield reconstruction
  -> Target Definition
  -> Requirements Ready
  -> Interface Scope Baseline Ready
  -> Architecture / Security / Data Ready
  -> API Contract Ready
  -> API Implementation
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

## 5. Requirements, architecture, security and data

Requirements define actors, authorization intent, functional and non-functional requirements, business rules, use cases, acceptance criteria and traceability before architecture/API implementation begins.

Architecture establishes domain boundaries, decisions, security model, authoritative data model, migrations, authentication/error/versioning strategy and durable business/security audit obligations. Threat modeling is conditional on risk.

Technical/operational logs and durable business/security audit are separate concerns. Critical authentication, role/permission, sensitive CRUD, meaningful state transition, financial, administrative, integration, tenant and security events require durable accountable evidence when applicable. Secrets must not leak into logs or audit.

## 6. Interface Scope Baseline

Blueprint 0.5.0 introduces an early interface maturity using `schemas/interface-inventory.schema.json` with:

`maturity: SCOPE_BASELINE`

It is created after Requirements Ready and before Architecture/API Contract Design.

Greenfield records intended interfaces derived from approved requirements and journeys. Brownfield records observed/reconciled existing interfaces before proposed replacement behavior.

The baseline may contain unresolved API needs. It must not fabricate `operationId`, permission, data or transition semantics that are not yet authoritative.

`interface_scope_ready` proves descriptive/planning completeness only. It never authorizes client implementation.

## 7. API contract, OpenAPI and API Gate

The API is the authoritative security and business boundary for API-backed clients.

API Contract Design defines stable operations, payload intent, authentication, permissions, errors, idempotency, request correlation, audit mapping and requirement traceability before implementation.

OpenAPI is the canonical machine-readable API contract. Every contracted HTTP operation uses a unique stable `operationId`. Postman operationalizes the validated OpenAPI contract and provides runtime coverage; it does not replace OpenAPI.

Initial `api_gate` is project-scoped and must PASS before executable client delivery begins.

### 7.1 API evolution after the initial baseline

Later API changes use impact-based revalidation rather than automatic global invalidation.

The machine-readable `api-impact` artifact records:

- previous and new API revision;
- changed `operationId` values;
- cross-cutting contract areas when applicable;
- affected slice/platform scopes;
- required revalidation policy/evidence.

Operation-local changes revalidate affected consumers only. Auth, authorization, security, error-contract, versioning or other cross-cutting changes may escalate to platform or project scope. Unrelated accepted evidence is preserved by default.

## 8. Executable Interface Inventory

After `api_gate = PASS`, the same interface contract progresses to:

`maturity: EXECUTABLE_INVENTORY`

It reconciles every early baseline interface as `COMMITTED`, `DEFERRED` or `DROPPED`.

Every committed interface records stable ID, platform, module, purpose, requirements, roles, permissions, data, actions, states, navigation, dependencies, priority and `slice_id`.

API-backed data/actions bind to real OpenAPI `operationId` values. Local/static behavior may explicitly have no API operation. Missing authoritative behavior is a blocker, not permission to invent an endpoint or business rule.

`interface_inventory_ready` represents the complete committed executable client backlog for the project scope.

## 9. Design System, Visual Identity and optional mockups

Design System is required for client delivery and defines reusable tokens, components, responsive behavior, semantic states and accessibility rules.

Visual Identity is CONDITIONAL. A logo or branding exercise is not fabricated merely to satisfy the process.

Mockups/prototypes are CONDITIONAL. They may be activated when visual/UX risk, pre-implementation approval, migration risk or future AI continuity justifies them.

When used:

- they reference executable inventory IDs;
- batches contain no more than 10 views;
- assets are repository-owned/versioned;
- generation, review and approval remain distinct;
- `mockup_review_pass` is scoped to the interface slice.

A slice with no mockups is valid. Approved visual references may inform implementation, but static approval never replaces review of the real functional client.

## 10. Client Architecture

Client implementation requires an effective architecture contract before coding for the exact `interface_slice + platform`.

The stable composition is:

```text
Platform Client Architecture Baseline
  + Slice Architecture Binding/Override
  = Effective Client Architecture Contract
```

The **Platform Client Architecture Baseline** declares reusable platform/project decisions such as:

- framework/toolkit and runtime strategy;
- API client and OpenAPI path;
- auth/session/refresh/logout lifecycle;
- credential storage;
- API-authoritative permissions;
- server/UI state ownership and cache strategy;
- forms and Problem Details mapping;
- observability/request correlation and redaction;
- accessibility;
- unit/UI/integration/E2E strategy;
- offline policy;
- Brownfield coexistence/cutover/rollback when applicable.

The **Slice Architecture Binding/Override** binds the exact inventory IDs, routes, permissions, API revision and `operationId` set, async states, idempotency requirements and slice-specific cache/offline/testing overrides.

`visual_references.mode = none` is valid. `approved_optional` requires real approved/versioned paths.

`client_architecture_ready` remains scoped to `interface_slice + platform`. Web PASS never authorizes Android, and one slice never authorizes another.

## 11. Functional Interface Slice

The **Functional Interface Slice** is the canonical unit of client execution, review, QA and human acceptance.

Lifecycle ownership is intentionally small:

```text
INVENTORIED -> READY -> IN_PROGRESS -> FUNCTIONAL -> ACCEPTED
```

Visual & Functional Review and Integration QA are quality gates, not lifecycle states.

### 11.1 Functional Definition of Done

A slice may become `FUNCTIONAL` only when the applicable DoD is evidenced, including:

- routing/navigation and Design System implementation;
- real authoritative API integration for business data/actions;
- auth/session and permission-aware presentation with API enforcement authoritative;
- forms and server validation/error mapping;
- loading/empty/error and applicable 401/403/404/409/422/429/offline states;
- request/correlation support with secret/PII redaction;
- idempotency when required by the API contract;
- responsive behavior;
- accessibility;
- tests;
- cross-artifact traceability;
- no hardcoded authoritative business data;
- no invented API capability, permission, state or transition.

Fixtures, Storybook data, prototypes and isolated test data are permitted when explicitly non-authoritative. They cannot masquerade as production business truth.

## 12. BLOCKED_BY_API

`BLOCKED_BY_API` is an overlay condition, not a lifecycle state.

It is used only when a required authoritative API data source, operation, permission, state, transition or contract capability is missing or incompatible.

A blocker records its category, affected slice/platform, last valid lifecycle state, current contract reference, evidence and resolution metadata.

The affected client boundary stops. The client does not fabricate server behavior. If the capability is valid, it is resolved in a separate API/backend boundary, an API impact artifact identifies affected consumers, and the slice resumes from its preserved lifecycle state only after resolution/revalidation evidence exists.

Ordinary frontend bugs, styling uncertainty or local implementation defects are not `BLOCKED_BY_API`.

## 13. Visual & Functional Review

Review is performed on the actual functional client intended to ship.

It checks interface fidelity, Design System fidelity, API/permission fidelity, authoritative business-data behavior, interaction/error states, responsive behavior and accessibility. Approved mockups are comparison inputs only when they exist.

`review.human_complete` is REQUIRED. CI cannot infer human review.

## 14. Integration QA and acceptance

`integration_qa_pass` is scoped to `interface_slice + platform` and covers functional behavior, real API transport, integration, security, responsive behavior, accessibility, E2E and applicable idempotency/offline behavior.

`ACCEPTED` requires:

- Functional DoD PASS;
- `visual_functional_review_pass = PASS`;
- `integration_qa_pass = PASS`;
- explicit human acceptance;
- no unresolved `BLOCKED_BY_API`.

Release Gate aggregates every committed slice required by the release. One accepted slice cannot unlock unrelated unfinished work.

## 15. Cross-Artifact Semantic Integrity

JSON Schema validates shape. Blueprint validators also validate semantic truth across artifacts.

The canonical graph is:

```text
requirement
  -> interface
  -> permission
  -> OpenAPI operationId
  -> Functional Interface Slice
  -> Client Architecture
  -> test/evidence
  -> review / Integration QA
  -> human acceptance
```

**Cross-Artifact Semantic Integrity** rejects syntactically valid but fictitious IDs, unknown operationIds, platform namespace mismatches, invented permissions, incompatible architecture baselines, invalid evidence references, accepted slices without quality gates and unresolved blockers hidden behind acceptance.

Evidence files are not automatically truthful because they exist. File-backed evidence must resolve; human approvals require explicit decision metadata; runtime claims require appropriate runtime/test evidence.

## 16. Skills

Materialized `dev-*` skills are versioned with the Blueprint and teach an agent how to satisfy canonical contracts. They do not become product truth and cannot declare gates PASS on their own.

Blueprint 0.5.0 materializes 14 reusable skills, including `dev-functional-interface-slice`. Project-specific knowledge remains in the consumer repository.

## 17. Git and human governance

Dependent boundaries follow:

`verified main -> short-lived branch -> exact-head validation -> PR -> human decision -> verified merge -> post-merge validation`

One active implementation PR per dependent boundary is the default. CI success is evidence, not merge authorization. Human review/acceptance remains explicit wherever required.

## 18. Versioning and schema provenance

Blueprint uses SemVer. Active 0.5.0 catalogs/workflows, canonical templates, materialized skills and version-specific schemas identify stable `0.5.0`.

Version-specific schema `$id` values include `/0.5.0/`. Validators resolve repository-local pinned schemas; schema identity never causes consumer auto-upgrade.

Historical release manifests and Compliance Reviews remain historical truth. A later release does not rewrite what an older review actually evaluated.

## 19. Reference pilots and consumer adoption

Reference pilots are non-normative. They prove or challenge Blueprint rules but cannot inject hidden product-specific requirements.

Consumers remain on the version they explicitly declare. A stable Blueprint release is followed, when desired, by a separate Compliance Review that classifies changes as KEEP / ADOPT / MIGRATE / DEFER / N/A before the consumer version is changed.

CUSA-Digital remained frozen while Blueprint 0.5.0 was constructed. Any CUSA 0.4.0 -> 0.5.0 adoption requires a new live verification, formal Compliance Review and explicit approval before Interface Inventory/client implementation continues.

## 20. Strategic boundary

Blueprint Control Center remains a documented future capability, not part of Blueprint Core 0.5.0. The preferred sequence is Blueprint Core -> reference/consumer pilots -> hardening -> Control Center when operating evidence justifies it.
