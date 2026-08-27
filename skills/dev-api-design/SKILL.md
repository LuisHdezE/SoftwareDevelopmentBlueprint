---
id: dev-api-design
title: API Contract Design
version: 0.5.0-dev
status: materialized
category: backend
applies_to:
  - greenfield
  - brownfield
phases:
  - api_contract_design
canonical_references:
  - BLUEPRINT.md
  - catalog/phases.yaml
  - catalog/checks.yaml
  - catalog/gates.yaml
  - schemas/interface-inventory.schema.json
  - schemas/api-impact.schema.json
  - workflows/greenfield.yaml
  - workflows/brownfield.yaml
---

# API Contract Design

## Purpose

Design the API as an explicit product contract before implementation, with stable operations, authorization, errors, idempotency, traceability and testability. Client needs may inform the contract through the early Interface Scope Baseline, but screens do not become the authority for business semantics.

## When to Use

Use after requirements and architecture gates pass and before API implementation, or when an approved post-baseline API change is required.

## Inputs

- Approved requirements/use cases and acceptance criteria.
- Architecture, security and data decisions.
- Interface Scope Baseline describing known/expected client data/actions without fabricated API bindings.
- Existing API inventory for Brownfield systems.
- Roles/permissions and high-risk mutation rules.
- Domain states, transitions and error semantics.
- Current API revision/consumer dependencies when changing an existing baseline.

## Procedure

1. Enumerate operations from approved use cases/domain behavior and reconcile legitimate client needs from Interface Scope Baseline. Do not derive business rules solely from a desired screen interaction.
2. Assign stable endpoint identifiers and unique canonical OpenAPI `operationId` values so requirements, inventory, OpenAPI, Postman, tests and Functional Interface Slices can reference the same operation.
3. Define resources, methods, paths, request/response schemas, status codes, pagination/filter/sort behavior and standard error representation.
4. Define authentication and authorization per operation. UI visibility never replaces API-side permission enforcement.
5. Identify high-risk/retryable mutations and define idempotency key, replay and conflict semantics before implementation.
6. Define request/correlation identifiers and durable audit expectations for critical business/security operations.
7. For Brownfield, compare proposed contract with observed routes/controllers/consumers and classify compatible, additive, changed or deprecated behavior explicitly.
8. Review for data minimization and prevent secrets/internal implementation metadata from leaking into response schemas.
9. Freeze the initial approved contract before implementation. Subsequent changes return through contract review rather than drifting silently in code.
10. After the initial project API Gate has consumers, create `api.change_impact_analysis` for contract changes that can affect them. Identify changed `operationId` values or cross-cutting auth/authorization/security/error/versioning areas and map affected slice/platform scopes.
11. Use `affected_only` revalidation for genuinely operation-local changes; escalate to platform/project only when the changed contract is cross-cutting. Preserve unrelated evidence.
12. Never resolve a client `BLOCKED_BY_API` by inventing behavior in the client. If the missing capability is legitimate, change the authoritative contract/backend first, record impact, then allow affected clients to revalidate.

## Outputs

- Canonical endpoint inventory with stable operation IDs and `operationId` values.
- Request/response/error contracts.
- Per-operation auth/permission metadata.
- Idempotency/correlation/audit rules where applicable.
- Brownfield compatibility decisions where applicable.
- API impact report for post-baseline changes when applicable.

## Stop Conditions

- Requirements or architecture gates are not PASS.
- Proposed API behavior is justified only by an unapproved UI idea.
- Authorization is undefined for a protected operation.
- High-risk mutation retry semantics are undefined.
- Sensitive fields would leak through the contract.
- A post-baseline breaking/change-impacting modification has no impact analysis.
- A client blocker is being bypassed with invented local semantics instead of an authoritative contract decision.

## Guardrails

- OpenAPI formalizes this contract; it is not a second independent design.
- `operationId` is a first-class downstream linkage and must not be casually renamed.
- API remains authoritative for permissions, business rules, transitions and data semantics.
- Interface Scope Baseline informs needs but does not dictate backend design blindly.
- Prefer proportional impact-based revalidation over either silent drift or global invalidation.

## Canonical References

- `BLUEPRINT.md`
- `catalog/phases.yaml`
- `catalog/checks.yaml`
- `catalog/gates.yaml`
- `schemas/interface-inventory.schema.json`
- `schemas/api-impact.schema.json`
- `workflows/greenfield.yaml`
- `workflows/brownfield.yaml`

## Completion Signal

Complete only when the API contract is traceable to approved requirements/domain decisions, stable operationIds exist, authorization/error/idempotency/audit semantics are explicit, relevant client needs are reconciled without UI-driven invention, and any post-baseline change has proportionate impact/revalidation evidence.
