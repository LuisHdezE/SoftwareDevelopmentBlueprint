---
id: dev-postman-qa
title: Postman Operational Contract
version: 0.4.0
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
  - workflows/greenfield.yaml
  - workflows/brownfield.yaml
---

# Postman Operational Contract

## Purpose

Create a repository-owned Postman collection/environment that operationalizes the approved OpenAPI contract without becoming a competing source of truth.

## When to Use

Use after `openapi_valid` passes. Use during API QA to execute contract-aware HTTP flows with non-secret environment configuration.

## Inputs

- Validated OpenAPI bundle/source.
- Stable endpoint IDs and operation metadata.
- Test/base URL strategy.
- Auth flow and runtime fixture strategy.
- Idempotency requirements.

## Procedure

1. Generate or align Postman requests from the validated OpenAPI contract. Preserve stable endpoint IDs in request names/metadata for coverage mapping.
2. Commit collection and environment templates with all credentials, tokens, and private values empty or synthetic. Secrets belong in CI/runtime variables, never Git.
3. Create deterministic auth workflows that capture access/refresh tokens without printing secrets. Order dependent requests so positive paths are actually positive.
4. Capture resource IDs needed by later requests and keep fixtures minimal and reproducible.
5. Add assertions for documented success codes, content types, request IDs, and selected response structure. Never label any arbitrary documented response as 'success'; success assertions must validate intended 2xx outcomes.
6. For high-risk mutations, include required idempotency headers and dedicated replay/conflict scenarios when the phase requires them.
7. Validate coverage against endpoint inventory/OpenAPI so every approved operation maps to exactly the expected request set.
8. Run Newman/Postman CLI with a pinned version against the intended environment and preserve reports as evidence.

## Outputs

- Version-controlled Postman collection.
- Non-secret local/staging environment templates.
- Coverage mapping to stable endpoint IDs.
- Operational execution report usable by API QA.

## Stop Conditions

- OpenAPI validation has not passed.
- A committed environment contains real credentials or tokens.
- Collection requests drift from OpenAPI method/path semantics.
- A positive-flow test can pass on an unintended non-2xx response.
- Coverage is incomplete or duplicated.

## Guardrails

- OpenAPI remains authoritative for the formal contract.
- Postman proves operability, not business-rule completeness.
- Thunder Client or another personal client may supplement testing but does not replace the canonical Postman artifacts when the Blueprint requires them.

## Canonical References

- `BLUEPRINT.md`
- `catalog/checks.yaml`
- `catalog/gates.yaml`
- `workflows/greenfield.yaml`
- `workflows/brownfield.yaml`

## Completion Signal

The skill is complete only when its required outputs exist in the repository, the relevant Blueprint checks/gates can be evaluated from evidence, and no stop condition remains unresolved.
