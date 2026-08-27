---
id: dev-postman-qa
title: Postman Operational Contract
version: 0.5.0-dev
status: materialized
category: backend
applies_to:
  - greenfield
  - brownfield
phases:
  - postman_contract
  - api_qa
canonical_references:
  - BLUEPRINT.md
  - catalog/checks.yaml
  - catalog/gates.yaml
  - schemas/api-impact.schema.json
  - workflows/greenfield.yaml
  - workflows/brownfield.yaml
---

# Postman Operational Contract

## Purpose

Create repository-owned Postman artifacts that operationalize the validated OpenAPI contract without becoming a competing source of truth, while preserving coverage by canonical `operationId` and reusable evidence for API QA or affected-consumer revalidation.

## When to Use

Use after `openapi_valid` passes. Use during initial API QA and again for approved post-baseline API changes that require runtime verification of affected operations.

## Inputs

- Validated current OpenAPI revision.
- Stable `operationId` values and endpoint metadata.
- Test/base URL strategy.
- Auth flow and deterministic runtime fixture strategy.
- Permission, error and idempotency requirements.
- API-impact scope for a post-baseline change when applicable.

## Procedure

1. Generate or align Postman requests from the validated OpenAPI contract. Keep canonical `operationId` metadata/coverage mapping so each request can be traced to the same operation used downstream by client artifacts.
2. Commit collection and environment templates with credentials, tokens and private values empty or synthetic. Secrets belong in runtime/CI variables, never Git.
3. Create deterministic auth workflows that capture credentials without printing them and distinguish genuinely different identities/permissions where RBAC is tested.
4. Capture resource IDs needed by dependent requests and keep fixtures minimal, reproducible and clearly test-only.
5. Add assertions for intended success codes, content type, request IDs and selected response structure. Positive tests must not pass merely because some documented response occurred.
6. Add negative/error scenarios for validation, authentication, authorization, conflicts and rate limiting where applicable to the contract.
7. For high-risk mutations, include idempotency headers plus replay and changed-payload conflict scenarios as required by the API contract.
8. Validate collection coverage against OpenAPI `operationId` values. Missing or duplicate coverage is explicit evidence debt, not hidden by request names.
9. Execute Postman/Newman or the approved CLI with pinned tooling against the intended runtime and preserve machine-readable reports.
10. For a post-baseline API change, scope supplemental execution/evidence to the affected operationIds plus any required cross-cutting auth/security scenarios. Do not imply that unrelated consumers were invalidated when their dependencies did not change.
11. Feed the runtime report into API QA and, when applicable, affected-consumer revalidation evidence before resolving client blockers or advancing impacted slices.

## Outputs

- Version-controlled Postman collection.
- Non-secret environment templates.
- Coverage mapping to canonical `operationId` values.
- Operational execution report.
- Focused post-baseline verification evidence when applicable.

## Stop Conditions

- OpenAPI validation has not passed.
- A committed environment contains real credentials/tokens.
- Collection requests drift from OpenAPI method/path/operation semantics.
- A positive-flow assertion can pass on an unintended failure response.
- Required operationId coverage is incomplete/duplicated.
- A post-baseline change is declared revalidated without testing the affected runtime contract.

## Guardrails

- OpenAPI remains authoritative for the formal contract.
- Postman proves operability; it does not redefine API behavior.
- `operationId` is the coverage/linkage key, not a decorative label.
- Personal API clients may supplement testing but do not replace canonical Postman artifacts when required.
- Runtime evidence for affected operations should be reused proportionally rather than forcing unrelated retesting without cause.

## Canonical References

- `BLUEPRINT.md`
- `catalog/checks.yaml`
- `catalog/gates.yaml`
- `schemas/api-impact.schema.json`
- `workflows/greenfield.yaml`
- `workflows/brownfield.yaml`

## Completion Signal

Complete only when the collection/environment are repository-owned and non-secret, required operationIds have correct coverage, runtime execution on the intended environment is evidenced, and any post-baseline affected-operation verification needed by API QA/consumer revalidation is green on the exact final head.
