---
id: dev-openapi
title: OpenAPI Contract Validation
version: 0.4.0
status: materialized
category: backend
applies_to:
  - greenfield
  - brownfield
phases:
  - openapi_validation
canonical_references:
  - BLUEPRINT.md
  - catalog/checks.yaml
  - catalog/gates.yaml
  - workflows/greenfield.yaml
  - workflows/brownfield.yaml
---

# OpenAPI Contract Validation

## Purpose

Turn the approved API contract into a lintable, machine-readable OpenAPI description and prove parity with the implemented routes.

## When to Use

Use after API implementation is complete and before Postman Contract. Use again whenever an approved API contract or route changes.

## Inputs

- Approved endpoint inventory and operation IDs.
- Implemented route list.
- Request/response/resource definitions.
- Authentication, permission, idempotency, error, and request-ID rules.

## Procedure

1. Generate or maintain OpenAPI from the approved contract, not from guesswork. Stable Blueprint endpoint IDs should map to unique `operationId` values or explicit traceability metadata.
2. Model success and error responses, including the project-standard problem representation and correlation/request ID headers.
3. Model authentication globally and override public operations explicitly. Document required permissions with machine-readable extensions when the project uses them.
4. Mark secrets/write-only fields correctly and verify response schemas do not expose passwords, hashes, refresh/reset secrets, or internal metadata.
5. Model pagination, enums, decimal/date formats, path/query parameters, and idempotency headers exactly as runtime behavior requires.
6. Lint and bundle the document with pinned tooling. Warnings that represent contract ambiguity are not gate-success noise; resolve or explicitly classify them.
7. Compare endpoint inventory, runtime routes, and OpenAPI by method+path and stable operation ID. Missing, extra, duplicate, or renamed operations fail validation.
8. Persist evidence from the exact final head and mark OpenAPI valid only after parity is proven.

## Outputs

- Version-controlled OpenAPI source.
- Lint/bundle evidence.
- Inventory-route-OpenAPI parity evidence.
- Traceability from stable endpoint IDs to operations.

## Stop Conditions

- API implementation gate is not PASS.
- Route parity differs from the approved inventory.
- Protected/public security semantics are wrong or ambiguous.
- Secrets appear in response schemas.
- The lint/bundle/parity result is not green on the exact final head.

## Guardrails

- OpenAPI is the formal API contract, not merely documentation.
- Postman is downstream operational verification and must not replace OpenAPI.
- Do not hand-edit the contract to hide runtime drift; fix the drift or return to API contract design.

## Canonical References

- `BLUEPRINT.md`
- `catalog/checks.yaml`
- `catalog/gates.yaml`
- `workflows/greenfield.yaml`
- `workflows/brownfield.yaml`

## Completion Signal

The skill is complete only when its required outputs exist in the repository, the relevant Blueprint checks/gates can be evaluated from evidence, and no stop condition remains unresolved.
