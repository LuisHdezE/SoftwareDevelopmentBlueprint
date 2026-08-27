---
id: dev-contract-testing
title: Contract and Runtime API Testing
version: 0.5.0-dev
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
  - schemas/api-impact.schema.json
---

# Contract and Runtime API Testing

## Purpose

Prove that runtime behavior matches the approved API contract under positive, negative, security, authorization, idempotency and audit scenarios, and provide trustworthy evidence for the initial API Gate or proportionate revalidation after a contract change.

## When to Use

Use after OpenAPI and Postman gates pass and before the initial `api_gate`. Re-run relevant scopes when a post-baseline API change affects existing consumer dependencies.

## Inputs

- Validated OpenAPI and Postman artifacts for the current revision.
- Authoritative test database/runtime configuration.
- Roles/permissions and seeded/fixture identities.
- Audit/logging model.
- Known high-risk operations and rate limits.
- API-impact report listing affected operationIds/slices when applicable.

## Procedure

1. Separate evidence layers: unit/feature tests, real HTTP transport, database/integration verification and contract parity. One layer cannot silently stand in for another.
2. Run the backend suite against the authoritative database technology where feasible. Ensure shell pipelines propagate failures instead of hiding exit codes.
3. Start the real application server and execute HTTP requests through the actual routing/middleware stack when runtime evidence is required.
4. Test positive behavior for the current contract and negative/error cases for validation, authentication, authorization, not-found, conflict and rate-limit semantics where applicable.
5. Verify RBAC with identities that truly differ in permissions. Client presentation is not an authorization test.
6. Verify high-risk idempotency: same key/same payload replay, same key/different payload conflict and transactionally consistent persistence.
7. Verify durable audit for critical operations: event code, actor, target/outcome, correlation ID and absence of secrets.
8. Re-run inventory-route-OpenAPI-Postman parity by canonical operationId and preserve exact counts/current-revision evidence.
9. For a post-baseline operation-local API change, test the changed operationIds plus directly dependent contract behavior and produce evidence that affected consumers can revalidate. Preserve unrelated PASS evidence.
10. If auth, authorization, security, error contract or other cross-cutting semantics changed, widen runtime testing and impact scope appropriately rather than pretending the change is local.
11. Never resolve `BLOCKED_BY_API` solely because backend code was edited. Require updated authoritative contract, passing runtime evidence, impact analysis and blocker-resolution evidence before affected client work resumes.
12. Preserve exact-final-head CI/reports so a gate or revalidation decision can be reconstructed later.

## Outputs

- Runtime API QA report.
- Positive/negative/security results.
- RBAC/idempotency/audit evidence.
- Contract parity evidence by operationId.
- Initial API Gate evidence or focused affected-consumer revalidation evidence.
- Exact-head CI run proving the evaluated scope.

## Stop Conditions

- Any required test layer is failing.
- CI can mask command failures through shell piping/ignored exits.
- Tests use only mocks when real transport/database evidence is required.
- Authorization or audit evidence is absent for critical operations.
- A post-baseline change lacks enough runtime evidence for its declared impact scope.
- Client blocker resolution is being claimed before the authoritative contract/runtime is proven.
- Exact final head has not been verified.

## Guardrails

- A green workflow label is not proof if the underlying command failed.
- Prefer authoritative database/runtime evidence over optimistic substitutes.
- Fix test-harness defects rather than weakening assertions.
- Revalidation is impact-based: neither silent under-testing nor global retesting by reflex.
- API QA proves server authority; client UI behavior cannot substitute for backend security/business validation.

## Canonical References

- `BLUEPRINT.md`
- `catalog/checks.yaml`
- `catalog/gates.yaml`
- `schemas/evidence.schema.json`
- `schemas/api-impact.schema.json`

## Completion Signal

Complete only when required runtime/contract/security/audit layers are green on the exact evaluated head, the current OpenAPI operation set is proven against runtime and Postman, and any post-baseline impact scope has sufficient evidence for affected consumers to revalidate without falsely invalidating unrelated work.
