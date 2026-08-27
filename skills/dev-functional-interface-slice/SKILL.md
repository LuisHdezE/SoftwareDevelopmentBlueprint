---
id: dev-functional-interface-slice
title: Functional Interface Slice Execution
version: 0.5.0-dev
status: materialized
category: core
applies_to:
  - greenfield
  - brownfield
phases:
  - functional_interface_slice
  - web_implementation
  - android_implementation
  - visual_functional_review
  - integration_qa
canonical_references:
  - BLUEPRINT.md
  - schemas/functional-interface-slice.schema.json
  - schemas/interface-inventory.schema.json
  - schemas/client-architecture.schema.json
  - schemas/client-platform-architecture.schema.json
  - schemas/evidence.schema.json
  - schemas/api-impact.schema.json
  - catalog/checks.yaml
  - catalog/gates.yaml
  - workflows/greenfield.yaml
  - workflows/brownfield.yaml
---

# Functional Interface Slice Execution

## Purpose

Implement one executable `interface_slice + platform` as a real client capability using the approved Interface Inventory, effective Client Architecture and authoritative API. The slice is the canonical unit of client execution, evidence, review, QA and human acceptance.

## When to Use

Use after `client_architecture_ready = PASS` for the exact slice/platform. Use for React/Web and Kotlin/Android implementations. Re-enter the skill after a resolved `BLOCKED_BY_API` condition or after an API impact report requires affected-slice revalidation.

## Inputs

- Executable Interface Inventory with stable IDs, requirements, permissions, dependencies and `operation_ids`.
- Functional Interface Slice artifact.
- Effective Client Architecture contract: platform baseline plus slice binding.
- Design System/tokens.
- Validated OpenAPI and current API revision.
- Required auth/session, Problem Details, request-correlation and idempotency contracts.
- Existing working client boundary for Brownfield when applicable.
- Evidence registry/status artifacts.

## Procedure

1. Confirm the exact slice ID and platform. Verify every inventory ID exists, belongs to the slice/platform, and its API-backed data/actions resolve to real OpenAPI `operationId` values.
2. Confirm `client_architecture_ready = PASS` for this exact scope. Do not inherit approval from another slice or from the same slice on another platform.
3. Move lifecycle from `READY` to `IN_PROGRESS` when implementation actually begins. Keep review and QA as separate gates rather than inventing extra lifecycle states.
4. Implement routing/navigation and components from the executable inventory and Design System. Do not create interfaces outside the committed inventory merely because the framework makes them convenient.
5. Integrate the real API transport. Authoritative business data, permissions, transitions and validation come from the API/domain contract, not hardcoded client fixtures or invented local rules.
6. Implement auth/session behavior and permission-aware presentation from Client Architecture. UI may hide or disable actions, but API authorization remains authoritative.
7. Implement forms and client-side feedback without replacing server validation. Map applicable Problem Details and 401/403/404/409/422/429 behavior into explicit accessible states.
8. Implement loading, empty, filtered-empty, generic error and offline/degraded states required by the inventory/binding. Mark a state N/A only when the contract genuinely makes it inapplicable.
9. Preserve request/correlation IDs in support/error context and redact secrets/PII. The client must not create a competing durable business/security audit system.
10. Apply idempotency only to operations defined by the authoritative contract. Generate one key per user intent, preserve same-payload retry semantics and prevent duplicate local/optimistic side effects.
11. If a required authoritative API capability is missing, do not fake it. Record `BLOCKED_BY_API` as an overlay on the current lifecycle state with category, contract reference and evidence; stop only the affected boundary.
12. Resolve API blockers through a separate API/backend boundary. After the API contract changes, consume its API-impact analysis, revalidate affected dependencies and resume from the preserved lifecycle state only with resolution evidence.
13. Execute the functional Definition of Done: real API, auth/RBAC, forms/errors, observability, responsive behavior, accessibility, tests, traceability, no hardcoded authoritative business data and no invented capabilities. Include idempotency/offline checks when applicable.
14. Mark lifecycle `FUNCTIONAL` only when `functional_slice_ready = PASS` and the functional DoD is evidenced.
15. Run Visual & Functional Review against the real client. Optional approved mockups may be references, but static visuals are not a substitute for reviewing behavior. Require explicit human review completion.
16. Run Integration QA for the exact slice/platform against real transport/runtime where the project environment permits it. Cover functional behavior, security, responsive/accessibility, E2E and applicable idempotency/offline behavior.
17. Mark lifecycle `ACCEPTED` only after functional gate, Visual & Functional Review, Integration QA and explicit human acceptance all pass. Record the evidence IDs in the slice artifact/status projection.
18. For Brownfield, preserve unrelated working behavior and perform cutover/removal only at the approved replacement/release boundary.

## Outputs

- Implemented functional client slice on exactly one platform.
- Updated Functional Interface Slice artifact and lifecycle.
- Real API integration and operationId traceability.
- Functional DoD evidence.
- `BLOCKED_BY_API` record/resolution evidence when encountered.
- Visual & Functional Review evidence.
- Integration QA evidence.
- Explicit human acceptance evidence for `ACCEPTED`.

## Stop Conditions

- `client_architecture_ready` is not PASS for the exact slice/platform.
- The executable inventory is missing, stale, or references unresolved authoritative API needs.
- Required `operationId`, permission, data, state or transition is absent from the authoritative API contract.
- Implementation would hardcode authoritative business data to appear functional.
- The client would invent an endpoint, permission, transition or business rule.
- A Brownfield change would remove unrelated working behavior before approved cutover.
- Functional DoD, review, QA or human acceptance is being inferred without evidence.

## Guardrails

- Functional slice is the execution unit; Web/Android are technical profiles, not competing lifecycle owners.
- `BLOCKED_BY_API` overlays lifecycle and preserves the last valid lifecycle state.
- API remains authoritative for security and business semantics.
- Generated fixtures may support tests/prototypes but cannot masquerade as authoritative runtime data.
- `FUNCTIONAL` does not mean `ACCEPTED`.
- Visual review and Integration QA are gates, not lifecycle states.
- A PASS for one platform never authorizes another platform.
- Preserve `GENERATED != REVIEWED != APPROVED` for optional visual references.

## Canonical References

- `BLUEPRINT.md`
- `schemas/functional-interface-slice.schema.json`
- `schemas/interface-inventory.schema.json`
- `schemas/client-architecture.schema.json`
- `schemas/client-platform-architecture.schema.json`
- `schemas/evidence.schema.json`
- `schemas/api-impact.schema.json`
- `catalog/checks.yaml`
- `catalog/gates.yaml`
- `workflows/greenfield.yaml`
- `workflows/brownfield.yaml`

## Completion Signal

Complete only when the exact slice/platform has reached the intended evidenced lifecycle state without bypassing the authoritative API. For final acceptance, `functional_slice_ready`, `visual_functional_review_pass` and `integration_qa_pass` are PASS, explicit human acceptance exists, no unresolved blocker remains, and the slice artifact legitimately records `ACCEPTED`.
