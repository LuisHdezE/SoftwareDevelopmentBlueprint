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
  - catalog/checks.yaml
  - catalog/gates.yaml
  - schemas/client-architecture.schema.json
  - schemas/interface-inventory.schema.json
  - schemas/mockup-batch.schema.json
  - documentation/CLIENT_ARCHITECTURE_CONTRACT.md
---

# React Client Architecture

## Purpose

Produce a schema-valid client architecture contract for one approved web interface slice before React implementation begins.

## When to Use

Use only after `visual_review_pass` for the exact target slice and before `web_implementation`. Re-run when API/auth/state architecture or the approved visual slice changes materially.

## Inputs

- Approved interface slice and inventory IDs.
- Approved/versioned visual references.
- Validated API/OpenAPI contract and canonical operation IDs.
- Auth/refresh lifecycle, permission and idempotency contracts.
- Design System/tokens.
- Project runtime/deployment constraints.
- Existing web client and migration constraints for Brownfield.

## Procedure

1. Create one client architecture artifact using `schemas/client-architecture.schema.json` with `platform: web` and only approved `WEB-###` IDs for the target slice.
2. Bind each implemented view/action to canonical API operation IDs. Never create convenience endpoints or hidden permission semantics in the client.
3. Record React platform decisions: rendering mode, router, server-state library, form library, build tool and browser-support policy.
4. Define the API client layer: base configuration, credential injection, refresh/rotation, concurrent-refresh handling, timeout/cancellation policy as applicable, Problem Details mapping, request ID propagation and idempotency headers.
5. Define protected/public routing and permission-aware presentation. UI may hide/disable actions; API authorization remains authoritative.
6. Separate server state from ephemeral UI state. Record cache ownership and invalidation/refetch behavior after each relevant mutation class.
7. Define form validation and accessible mapping of 422, 409, 429 and global API errors.
8. Classify loading, empty, error, 401, 403, 404, 409, 422, 429 and offline states explicitly.
9. For every high-risk/idempotent operation, define key generation per user intent, replay handling and conflict behavior without duplicating local side effects.
10. Define observability/request correlation with secret/PII redaction.
11. Define accessibility behavior and unit/component/integration/E2E boundaries before implementation.
12. For Brownfield, document coexistence, migration boundary, cutover trigger and rollback. Preserve unrelated working UI.
13. Validate the artifact and attach evidence to scoped `client_architecture_ready` for the exact `interface_slice + web` scope.

## Outputs

- Schema-valid web client architecture JSON.
- Explicit inventory/API/visual binding for the slice.
- Auth, routing, state/cache, forms/error/offline, idempotency, observability and accessibility decisions.
- Test strategy.
- Brownfield coexistence/migration plan when applicable.
- Evidence for scoped `client_architecture_ready`.

## Stop Conditions

- `visual_review_pass` is not PASS for the exact slice.
- Any inventory view in the proposed implementation is not approved.
- API/auth lifecycle or canonical operation IDs are undefined.
- Client design weakens or bypasses server authorization.
- High-risk mutation idempotency requirements are ignored.
- Brownfield replacement would remove working behavior before approved cutover.
- The artifact fails `schemas/client-architecture.schema.json` or V4-4 semantic validation.

## Guardrails

- Scope architecture to one approved interface slice and platform.
- React implementation follows the client contract; it does not silently redefine it.
- Do not persist or log credentials in weaker storage or telemetry for convenience.
- API remains the source of authorization and business truth.
- Approved visual references are implementation inputs and remain versioned.
- `client_architecture_ready` for web does not authorize Android or another slice.

## Canonical References

- `BLUEPRINT.md`
- `catalog/phases.yaml`
- `catalog/checks.yaml`
- `catalog/gates.yaml`
- `schemas/client-architecture.schema.json`
- `schemas/interface-inventory.schema.json`
- `schemas/mockup-batch.schema.json`
- `documentation/CLIENT_ARCHITECTURE_CONTRACT.md`

## Completion Signal

Complete only when a schema-valid web architecture artifact exists for the exact approved slice, all client architecture checks are evidenced, and scoped `client_architecture_ready` can legitimately evaluate to PASS for `interface_slice + web`.
