---
id: dev-android-client-architecture
title: Android Client Architecture
version: 0.5.4
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
  - schemas/project.schema.json
  - schemas/client-platform-architecture.schema.json
  - schemas/client-architecture.schema.json
  - schemas/interface-inventory.schema.json
  - schemas/functional-interface-slice.schema.json
  - documentation/CLIENT_ARCHITECTURE_CONTRACT.md
---

# Android Client Architecture

## Purpose

Produce the effective Client Architecture contract for one Android Functional Interface Slice while keeping reusable Android/platform decisions in one baseline instead of duplicating them across slices. The Blueprint does not mandate Kotlin, Compose or another framework here; implementation technology is consumer project data and may be native or cross-platform.

## When to Use

Use after `interface_inventory_ready` and `design_system_ready`, with the initial `api_gate` already PASS, and before functional Android implementation. Use only when `capabilities.android=true`. Revalidate when platform architecture, API revision/operationIds, offline policy, inventory scope, mobile strategy or slice-specific behavior changes materially.

## Inputs

- Project capability contract with `capabilities.android=true` and declared `mobile.strategy`.
- Effective Android target/toolchain choices from consumer project data.
- Executable Interface Inventory and exact legacy `APP-###` IDs for the slice.
- Design System/tokens.
- Validated OpenAPI and current API revision.
- Auth/session, permission, Problem Details, request-ID and idempotency contracts.
- Existing Android platform baseline if already approved.
- Offline/runtime/device constraints.
- Optional approved/versioned visual references when they exist.
- Existing Android client/coexistence constraints for Brownfield.

## Procedure

1. Confirm the project explicitly enables Android. `mobile.strategy=cross_platform` does not enable Android by itself.
2. Reuse an approved Android Platform Client Architecture Baseline when still applicable; otherwise create or revise one using `schemas/client-platform-architecture.schema.json`.
3. In the platform baseline define implementation language/framework, UI toolkit, architecture pattern, networking, local persistence, background work, minimum supported platform/runtime, API client, secure credential lifecycle, state ownership, forms/errors, observability, accessibility, testing and offline policy as consumer decisions.
4. If `mobile.strategy=cross_platform`, record which implementation concerns are shared and which remain Android-specific. Shared code never shares architecture acceptance, evidence or gate PASS across Android and iOS.
5. Keep server/API authority explicit even when a local store is used. API-backed offline data cannot silently become a competing business authority.
6. For Brownfield, keep coexistence, migration boundary, cutover trigger and rollback in the platform baseline. Preserve unrelated working mobile behavior.
7. Create one slice binding with `schemas/client-architecture.schema.json` for the exact `interface_slice + android` scope.
8. Bind only executable legacy `APP-###` IDs. `APP-###` remains Android-specific and must never be treated as generic mobile or reused for iOS.
9. Resolve the exact permissions, routes/destinations and OpenAPI `operationId` values from repository artifacts.
10. Record the API revision consumed by the slice. Post-baseline API changes use impact-based revalidation and may affect only dependent slices unless a cross-cutting contract changes.
11. Use `visual_references.mode = none` when no approved static visual references exist. If references are used, `approved_optional` must point to real approved/versioned assets.
12. Define async/error/offline states explicitly. If queued writes are enabled, document synchronization/conflict/idempotency behavior without bypassing server authorization.
13. Define idempotent operations only from the bound `operationId` set and protect retries from duplicate local effects.
14. Record slice-specific cache invalidation, offline overrides and testing notes only where the slice specializes the platform baseline.
15. Keep permissions presentation-aware but API-authoritative. Do not invent Android-only business operations, permissions or transitions.
16. Run `scripts/validate-client-architecture.py` to validate schema and cross-artifact integrity. Fake inventory IDs, permissions, operationIds, visual paths or incompatible baselines must fail.
17. Attach evidence to scoped `client_architecture_ready` for the exact `interface_slice + android` boundary. iOS or Web evidence cannot satisfy this scope.

## Outputs

- Validated or reused Android Platform Client Architecture Baseline.
- Schema-valid Android Slice Architecture Binding.
- Effective Client Architecture for the exact slice/platform.
- Explicit technology/toolchain choice owned by the consumer project.
- Inventory/permission/OpenAPI/API-revision traceability.
- Explicit API-backed offline specialization where applicable.
- Evidence for scoped `client_architecture_ready`.

## Stop Conditions

- `capabilities.android` is not true.
- Initial API Gate, Interface Inventory Ready or Design System Ready is not PASS.
- `APP-###` IDs or canonical operationIds are unresolved.
- The binding invents permissions/endpoints/transitions.
- Credential storage or logging weakens the platform security model.
- Offline queueing lacks conflict/idempotency semantics.
- A fake visual reference is being created merely to satisfy structure.
- Brownfield replacement would remove working behavior before approved cutover.
- Cross-artifact Client Architecture validation fails.

## Guardrails

- Android enablement comes only from `capabilities.android=true`; `cross_platform` never auto-enables a target.
- Reusable Android decisions belong to the platform baseline; slice-specific choices belong to the binding.
- Blueprint does not mandate Kotlin, Compose, Flutter, React Native, Kotlin Multiplatform or another framework.
- Cross-platform code sharing does not share platform gates, evidence or human acceptance.
- Static mockups are conditional and never a hidden prerequisite for architecture.
- API remains authoritative for authorization, validation, transitions and business truth.
- Offline persistence is explicit, API-backed and bounded in v0.5.4 hardening.
- `APP-###` is the preserved Android legacy namespace, not a generic mobile namespace.
- `client_architecture_ready` for Android does not authorize iOS, Web or another slice.

## Canonical References

- `BLUEPRINT.md`
- `catalog/phases.yaml`
- `catalog/checks.yaml`
- `catalog/gates.yaml`
- `schemas/project.schema.json`
- `schemas/client-platform-architecture.schema.json`
- `schemas/client-architecture.schema.json`
- `schemas/interface-inventory.schema.json`
- `schemas/functional-interface-slice.schema.json`
- `documentation/CLIENT_ARCHITECTURE_CONTRACT.md`

## Completion Signal

Complete only when the Android platform baseline and slice binding compose into a semantically valid effective contract, all referenced inventory/permissions/operationIds exist, technology choices remain consumer-owned, offline behavior is explicit, optional visual references are legitimate, and scoped `client_architecture_ready` can truthfully evaluate to PASS for the exact slice + Android platform without borrowing acceptance from another platform.
