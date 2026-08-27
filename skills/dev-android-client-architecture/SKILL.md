---
id: dev-android-client-architecture
title: Android Client Architecture
version: 0.5.0
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
  - schemas/client-platform-architecture.schema.json
  - schemas/client-architecture.schema.json
  - schemas/interface-inventory.schema.json
  - schemas/functional-interface-slice.schema.json
  - documentation/CLIENT_ARCHITECTURE_CONTRACT.md
---

# Android Client Architecture

## Purpose

Produce the effective Client Architecture contract for one Android Functional Interface Slice while keeping reusable Kotlin/platform decisions in one baseline instead of duplicating them across slices.

## When to Use

Use after `interface_inventory_ready` and `design_system_ready`, with the initial `api_gate` already PASS, and before functional Android implementation. Static mockups are optional. Revalidate when platform architecture, API revision/operationIds, offline policy, inventory scope or slice-specific behavior changes materially.

## Inputs

- Executable Interface Inventory and exact `APP-###` IDs for the slice.
- Design System/tokens.
- Validated OpenAPI and current API revision.
- Auth/session, permission, Problem Details, request-ID and idempotency contracts.
- Existing Android platform baseline if already approved.
- Offline/runtime/device constraints.
- Optional approved/versioned visual references when they exist.
- Existing Android client/coexistence constraints for Brownfield.

## Procedure

1. Reuse an approved Android Platform Client Architecture Baseline when still applicable; otherwise create/revise one using `schemas/client-platform-architecture.schema.json`.
2. In the platform baseline define Kotlin/UI toolkit, architecture pattern, networking, local persistence, background work, minimum SDK, API client, secure credential lifecycle, state ownership, forms/errors, observability, accessibility, testing and offline policy.
3. Keep server/API authority explicit even when Room or another local store is used. Offline data cannot silently become a competing business authority.
4. For Brownfield, keep coexistence, migration boundary, cutover trigger and rollback in the platform baseline. Preserve unrelated working mobile behavior.
5. Create one slice binding with `schemas/client-architecture.schema.json` for the exact `interface_slice + android` scope.
6. Bind only executable `APP-###` IDs and resolve the exact permissions, routes/destinations and OpenAPI `operationId` values from repository artifacts.
7. Record the API revision consumed by the slice. Post-baseline API changes use impact-based revalidation and may affect only dependent slices unless a cross-cutting contract changes.
8. Use `visual_references.mode = none` when no approved static visual references exist. If references are used, `approved_optional` must point to real approved/versioned assets.
9. Define async/error/offline states explicitly. If queued writes are enabled, document synchronization/conflict/idempotency behavior without bypassing server authorization.
10. Define idempotent operations only from the bound `operationId` set and protect retries from duplicate local effects.
11. Record slice-specific cache invalidation, offline overrides and testing notes only where the slice specializes the platform baseline.
12. Keep permissions presentation-aware but API-authoritative. Do not invent mobile-only business operations, permissions or transitions.
13. Run `scripts/validate-client-architecture.py` to validate schema and cross-artifact integrity. Fake inventory IDs, permissions, operationIds, visual paths or incompatible baselines must fail.
14. Attach evidence to scoped `client_architecture_ready` for the exact `interface_slice + android` boundary.

## Outputs

- Validated/reused Android Platform Client Architecture Baseline.
- Schema-valid Android Slice Architecture Binding.
- Effective Client Architecture for the exact slice/platform.
- Inventory/permission/OpenAPI/API-revision traceability.
- Explicit offline specialization where applicable.
- Evidence for scoped `client_architecture_ready`.

## Stop Conditions

- Initial API Gate, Interface Inventory Ready or Design System Ready is not PASS.
- `APP-###` IDs or canonical operationIds are unresolved.
- The binding invents permissions/endpoints/transitions.
- Credential storage or logging weakens the platform security model.
- Offline queueing lacks conflict/idempotency semantics.
- A fake visual reference is being created merely to satisfy structure.
- Brownfield replacement would remove working behavior before approved cutover.
- Cross-artifact Client Architecture validation fails.

## Guardrails

- Reusable Android decisions belong to the platform baseline; slice-specific choices belong to the binding.
- Static mockups are conditional and never a hidden prerequisite for architecture.
- API remains authoritative for authorization, validation, transitions and business truth.
- Offline persistence is explicit and bounded.
- `client_architecture_ready` for Android does not authorize Web or another slice.

## Canonical References

- `BLUEPRINT.md`
- `catalog/phases.yaml`
- `catalog/checks.yaml`
- `catalog/gates.yaml`
- `schemas/client-platform-architecture.schema.json`
- `schemas/client-architecture.schema.json`
- `schemas/interface-inventory.schema.json`
- `schemas/functional-interface-slice.schema.json`
- `documentation/CLIENT_ARCHITECTURE_CONTRACT.md`

## Completion Signal

Complete only when the Android platform baseline and slice binding compose into a semantically valid effective contract, all referenced inventory/permissions/operationIds exist, offline behavior is explicit, optional visual references are legitimate, and scoped `client_architecture_ready` can truthfully evaluate to PASS for the exact slice + Android platform.
