---
id: dev-android-client-architecture
title: Android Client Architecture
version: 0.4.0-dev
status: materialized
category: android
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

# Android Client Architecture

## Purpose

Produce a schema-valid client architecture contract for one approved Android interface slice before Kotlin implementation begins.

## When to Use

Use only after `visual_review_pass` for the exact Android slice and before `android_implementation`. Re-run when API/auth/offline/state architecture or the approved visual slice changes materially.

## Inputs

- Approved Android interface slice and `APP-###` inventory IDs.
- Approved/versioned visual references.
- Validated API/OpenAPI contract and canonical operation IDs.
- Auth/refresh lifecycle, permission and idempotency contracts.
- Design System/tokens.
- Android runtime constraints, minimum supported SDK and device requirements.
- Offline requirements when applicable.
- Existing Android client and migration constraints for Brownfield.

## Procedure

1. Create one client architecture artifact using `schemas/client-architecture.schema.json` with `platform: android` and only approved `APP-###` IDs for the target slice.
2. Bind each screen/action to canonical API operation IDs. Do not invent mobile-only business endpoints, permission rules or state transitions.
3. Record Kotlin platform decisions: UI toolkit, architecture pattern, networking library, local persistence, background-work strategy and minimum SDK.
4. Define credential storage using platform-appropriate secure storage. Define refresh/rotation, concurrent refresh and logout cleanup without exposing tokens in logs or crash reports.
5. Define Navigation/route boundaries, protected destinations and permission-aware presentation. API authorization remains authoritative.
6. Define repository/ViewModel/state ownership and make server state distinct from transient UI state.
7. Define cache/offline behavior explicitly. If writes can queue offline, document durable queueing, synchronization, conflict handling, retry and idempotency behavior.
8. Define form validation and mapping of 422, 409, 429 and global API errors into accessible UI state.
9. Classify loading, empty, error, 401, 403, 404, 409, 422, 429 and offline states explicitly.
10. Define request-ID propagation/support context, secret/PII redaction and client observability.
11. Define TalkBack semantics, focus/navigation behavior, switch/keyboard behavior where applicable and minimum touch targets.
12. Define unit, Compose/UI, integration and device/emulator E2E boundaries before implementation.
13. For Brownfield, document coexistence, migration boundary, cutover trigger and rollback. Preserve unrelated working mobile behavior.
14. Validate the artifact and attach evidence to scoped `client_architecture_ready` for the exact `interface_slice + android` scope.

## Outputs

- Schema-valid Android client architecture JSON.
- Explicit inventory/API/visual binding for the slice.
- Kotlin/UI/network/storage/offline/auth/navigation decisions.
- Accessibility and testing strategy.
- Brownfield coexistence/migration plan when applicable.
- Evidence for scoped `client_architecture_ready`.

## Stop Conditions

- `visual_review_pass` is not PASS for the exact Android slice.
- Any `APP-###` target is not approved.
- API/auth lifecycle or canonical operation IDs are undefined.
- Client design weakens API authorization or server business rules.
- Offline queueing is proposed without conflict/idempotency semantics.
- Credentials would be stored or logged unsafely.
- Brownfield replacement would remove working behavior before approved cutover.
- The artifact fails `schemas/client-architecture.schema.json` or V4-4 semantic validation.

## Guardrails

- Scope architecture to one approved interface slice and Android platform.
- Kotlin implementation follows the client contract; it does not silently redefine it.
- Server/API remains authoritative for authorization and business validation.
- Offline storage does not become an undocumented competing source of truth.
- Approved visual references remain versioned inputs.
- `client_architecture_ready` for Android does not authorize web or another slice.

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

Complete only when a schema-valid Android architecture artifact exists for the exact approved slice, all client architecture checks are evidenced, and scoped `client_architecture_ready` can legitimately evaluate to PASS for `interface_slice + android`.
