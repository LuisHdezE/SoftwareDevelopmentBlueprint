---
id: dev-contract-testing
title: Contract and Runtime API Testing
version: 0.4.0-dev
status: materialized
category: backend
applies_to:
  - greenfield
  - brownfield
phases:
  - api_qa
canonical_references:
  - BLUEPRINT.md
  - catalog/checks.yaml
  - catalog/gates.yaml
  - schemas/evidence.schema.json
---

# Contract and Runtime API Testing

## Purpose

Prove that runtime behavior matches the approved API contract under positive, negative, security, authorization, idempotency, and audit scenarios.

## When to Use

Use after OpenAPI and Postman gates pass and before `api_gate` can pass.

## Inputs

- Validated OpenAPI and Postman artifacts.
- Authoritative test database/runtime configuration.
- Roles/permissions and seeded/fixture identities.
- Audit/logging model.
- Known high-risk operations and rate limits.

## Procedure

1. Separate evidence layers: unit/feature tests, real HTTP transport tests, database/integration verification, and contract parity. Do not let one silently stand in for another.
2. Run the complete automated backend suite against the authoritative database technology where feasible. Ensure shell pipelines propagate failing exit codes (`pipefail` or equivalent).
3. Start the real application server and execute HTTP requests through the actual routing/middleware stack.
4. Test representative positive paths for every contract slice and negative/error paths for validation, authentication, authorization, not-found/conflict/rate-limit behavior where applicable.
5. Verify RBAC with identities that genuinely differ in permissions; a UI-hidden button is not an authorization test.
6. Verify high-risk idempotency: same key/same payload replay, same key/different payload conflict, and transactionally consistent persistence.
7. Verify audit evidence for critical operations, including actor, event/entity, outcome, and request/correlation ID. Confirm secrets are not persisted in audit payloads.
8. Re-run inventory-route-OpenAPI-Postman parity and dependency/security audits. Record exact counts and final-head CI evidence.

## Outputs

- Runtime API QA report.
- Positive and negative/security results.
- RBAC/idempotency/audit evidence.
- Contract parity evidence.
- Exact-head CI run proving the gate.

## Stop Conditions

- Any required test layer is failing.
- A CI step can mask a failure through shell piping or ignored exit codes.
- Tests run only on mocks when real transport/database evidence is required.
- Authorization or audit evidence is missing for critical operations.
- The exact final head has not been verified.

## Guardrails

- A green workflow label is not proof if the underlying command failed.
- Prefer authoritative database/runtime evidence over optimistic local substitutes.
- Fix test harness defects rather than weakening assertions to obtain green CI.

## Canonical References

- `BLUEPRINT.md`
- `catalog/checks.yaml`
- `catalog/gates.yaml`
- `schemas/evidence.schema.json`

## Completion Signal

The skill is complete only when its required outputs exist in the repository, the relevant Blueprint checks/gates can be evaluated from evidence, and no stop condition remains unresolved.
