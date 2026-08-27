---
id: dev-openapi
title: OpenAPI Contract Validation
version: 0.5.0
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
  - schemas/interface-inventory.schema.json
  - schemas/api-impact.schema.json
  - workflows/greenfield.yaml
  - workflows/brownfield.yaml
---

# OpenAPI Contract Validation

## Purpose

Turn the approved API contract into the canonical machine-readable OpenAPI description, prove parity with runtime routes and provide stable `operationId` links consumed by executable Interface Inventory, Client Architecture and Functional Interface Slices.

## When to Use

Use after API implementation is complete and before Postman Contract. Re-run whenever an approved API route/contract changes, especially after the initial API Gate when existing clients may depend on affected operations.

## Inputs

- Approved endpoint inventory and stable operation identifiers.
- Implemented route list.
- Request/response/resource definitions.
- Authentication, permission, idempotency, error and request-ID rules.
- Existing downstream `operationId` dependencies when revising an established API baseline.

## Procedure

1. Generate or maintain OpenAPI from the approved API contract, never from UI guesswork. Every HTTP operation that is part of the contract receives a unique, stable `operationId`.
2. Treat `operationId` as a canonical downstream key. Executable Interface Inventory, Client Architecture, Functional Interface Slices, impact reports and tests may depend on it; rename only through an explicit contract change with impact analysis.
3. Model success and error responses, including Problem Details or the approved equivalent plus request/correlation headers.
4. Model authentication globally and override public operations explicitly. Represent required permissions using the project’s documented machine-readable convention where applicable.
5. Mark secrets/write-only fields correctly and ensure responses cannot expose passwords, hashes, reset/refresh secrets, credentials or private implementation metadata.
6. Model pagination, enums, decimal/date formats, path/query parameters, state values and idempotency headers exactly as runtime behavior requires.
7. Lint and bundle with pinned tooling. Resolve warnings that represent ambiguity rather than treating them as harmless noise.
8. Compare endpoint inventory, runtime routes and OpenAPI by method + path + stable `operationId`. Missing, extra, duplicate or silently renamed operations fail validation.
9. Verify that executable client artifacts reference only operationIds present in the validated current OpenAPI revision. Cross-artifact validators must reject fictitious operationIds.
10. For post-baseline API changes, feed changed operationIds and cross-cutting contract areas into API impact analysis. Revalidate affected client slices proportionally rather than discarding unrelated evidence.
11. Persist exact-final-head lint/parity evidence and mark OpenAPI valid only after the current revision is proven coherent.

## Outputs

- Version-controlled OpenAPI source/bundle.
- Unique stable `operationId` set.
- Lint/bundle evidence.
- Inventory-route-OpenAPI parity evidence.
- Downstream client linkage and API-impact evidence when applicable.

## Stop Conditions

- API implementation gate is not PASS.
- Route parity differs from approved inventory.
- `operationId` values are duplicate, missing or renamed without an approved contract change.
- Protected/public security semantics are wrong or ambiguous.
- Secrets appear in response schemas.
- Downstream artifacts reference operations absent from the current OpenAPI revision.
- Lint/bundle/parity is not green on the exact final head.

## Guardrails

- OpenAPI is the formal machine-readable API contract, not decorative documentation.
- `operationId` stability is part of compatibility governance.
- Postman is downstream operational verification and does not replace OpenAPI.
- Do not edit OpenAPI merely to hide runtime drift; fix the drift or return to API contract design.
- Client convenience never authorizes an invented endpoint or permission.

## Canonical References

- `BLUEPRINT.md`
- `catalog/checks.yaml`
- `catalog/gates.yaml`
- `schemas/interface-inventory.schema.json`
- `schemas/api-impact.schema.json`
- `workflows/greenfield.yaml`
- `workflows/brownfield.yaml`

## Completion Signal

Complete only when the current OpenAPI revision validates, runtime route parity is proven, every operationId is unique/stable, downstream client references resolve to real operations, and any post-baseline change has the necessary impact/revalidation evidence on the exact final head.
