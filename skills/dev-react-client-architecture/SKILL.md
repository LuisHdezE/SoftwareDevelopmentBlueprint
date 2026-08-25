---
id: dev-react-client-architecture
title: React Client Architecture
version: 0.4.0-dev
status: materialized
category: web
applies_to:
  - greenfield
  - brownfield
phases:
  - client_architecture
canonical_references:
  - BLUEPRINT.md
  - catalog/phases.yaml
  - catalog/gates.yaml
  - schemas/interface-inventory.schema.json
  - schemas/mockup-batch.schema.json
---

# React Client Architecture

## Purpose

Define the client-side architecture contract for an approved interface slice before React implementation begins.

## When to Use

Use only after `visual_review_pass` for the target interface slice and before `web_implementation`. Revisit when API/auth/state architecture changes.

## Inputs

- Approved interface slice and mockups.
- Validated API/OpenAPI contract.
- Auth/refresh lifecycle and permission model.
- Design system/tokens.
- Project runtime/deployment constraints.
- Existing web client for Brownfield projects.

## Procedure

1. Bind every implemented view/action to approved inventory IDs and API operations. Do not invent convenience endpoints or hidden permission semantics.
2. Define routing and layout boundaries for the slice, including protected/public routes and permission-aware presentation. API authorization remains authoritative.
3. Define the API client layer: base configuration, auth injection, token refresh/rotation, request ID propagation, cancellation/timeouts, Problem Details/error mapping, and idempotency headers for high-risk mutations.
4. Define data-fetching/cache/state ownership. Separate server state from local UI state and document invalidation/refetch behavior after mutations.
5. Define form strategy and how API validation/conflict/rate-limit errors map to accessible field/global feedback.
6. Define standard loading, empty, error, 401, 403, 404, 409, 422, 429, and offline/degraded states as applicable.
7. Define observability and correlation so client errors/support reports can retain request IDs without logging secrets.
8. Define unit/component/integration/E2E test boundaries for the slice.
9. For Brownfield, specify coexistence and migration boundaries. Existing working UI may remain until the approved slice is implemented and release migration is explicitly approved.

## Outputs

- Client architecture contract for the interface slice.
- API/auth/state/error/testing strategy.
- Brownfield coexistence/migration plan when applicable.
- Evidence for scoped `client_architecture_ready`.

## Stop Conditions

- Visual Review Gate is not PASS for the target slice.
- API/auth lifecycle is undefined.
- Client design weakens or bypasses server authorization.
- High-risk mutation idempotency requirements are ignored.
- Brownfield replacement would remove working behavior without approved coexistence/migration.

## Guardrails

- Architecture is scoped to approved interfaces and platform.
- React implementation must follow, not silently redefine, API and visual contracts.
- Do not persist or log access/refresh secrets in unsafe client storage/telemetry.
- This skill may be tightened by the V4-4 client architecture contract; downstream projects use the Blueprint version they declared.

## Canonical References

- `BLUEPRINT.md`
- `catalog/phases.yaml`
- `catalog/gates.yaml`
- `schemas/interface-inventory.schema.json`
- `schemas/mockup-batch.schema.json`

## Completion Signal

The skill is complete only when its required outputs exist in the repository, the relevant Blueprint checks/gates can be evaluated from evidence, and no stop condition remains unresolved.
