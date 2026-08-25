---
id: dev-api-design
title: API Contract Design
version: 0.4.0-dev
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
  - workflows/greenfield.yaml
  - workflows/brownfield.yaml
---

# API Contract Design

## Purpose

Design the API as an explicit product contract before implementation, with stable operations, authorization, errors, idempotency, traceability, and testability.

## When to Use

Use after requirements and architecture gates pass and before API implementation begins or when an approved contract change is required.

## Inputs

- Approved requirements/use cases.
- Architecture, security, and data decisions.
- Existing API inventory for Brownfield systems.
- Roles/permissions and high-risk mutation rules.
- Domain states and error semantics.

## Procedure

1. Enumerate operations from approved use cases and existing contracts. Assign stable endpoint/operation IDs so requirements, OpenAPI, Postman, tests, and UI can trace the same operation.
2. Define resources, HTTP methods, paths, request/response schemas, status codes, pagination/filter/sort behavior, and standard error representation.
3. Define authentication and authorization per operation. Public visibility in UI never replaces API-side authorization.
4. Identify high-risk or retryable mutations and define idempotency semantics, replay behavior, and conflict behavior before implementation.
5. Define correlation/request identifiers and audit expectations for sensitive operations.
6. For Brownfield, compare proposed contract with observed routes/controllers/clients and explicitly classify compatible, additive, changed, or deprecated behavior.
7. Review the contract for data minimization. Passwords, hashes, reset secrets, internal metadata, and other sensitive implementation details must not leak into response schemas.
8. Freeze the approved inventory/contract before implementation starts. Subsequent changes return to contract review rather than silently drifting in code.

## Outputs

- Canonical endpoint inventory with stable operation IDs.
- Request/response/error contracts.
- Per-operation auth/permission metadata.
- Idempotency and correlation rules where applicable.
- Brownfield compatibility decisions where applicable.

## Stop Conditions

- Requirements or architecture gates are not PASS.
- The contract invents business behavior not supported by requirements/domain decisions.
- Authorization is undefined for a protected operation.
- High-risk mutation retry behavior is undefined.
- Sensitive fields would be exposed by the response contract.

## Guardrails

- OpenAPI will formalize this contract; it must not become a second independent design.
- UI clients consume the approved API and may not invent hidden endpoints or permissions.
- Prefer explicit compatibility decisions over accidental Brownfield breakage.

## Canonical References

- `BLUEPRINT.md`
- `catalog/phases.yaml`
- `catalog/checks.yaml`
- `catalog/gates.yaml`
- `workflows/greenfield.yaml`
- `workflows/brownfield.yaml`

## Completion Signal

The skill is complete only when its required outputs exist in the repository, the relevant Blueprint checks/gates can be evaluated from evidence, and no stop condition remains unresolved.
