---
id: dev-ios-client-architecture
title: iOS Client Architecture
version: 0.5.4
status: materialized
category: ios
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
  - documentation/CLIENT_ARCHITECTURE_CONTRACT.md
---

# iOS Client Architecture

## Purpose

Produce the effective Client Architecture contract for one iOS Functional Interface Slice while keeping reusable iOS/platform decisions in one baseline. The skill is technology-neutral: native and cross-platform projects choose their language, framework, UI toolkit and shared-code strategy in consumer contracts rather than inheriting a mandatory implementation stack from Blueprint.

## When to Use

Use after `interface_inventory_ready` and `design_system_ready`, with the initial `api_gate` already PASS, and before iOS functional implementation. Use only when `capabilities.ios=true`. Revalidate when the iOS platform baseline, API revision/operationIds, offline policy, inventory scope, mobile strategy or slice-specific behavior changes materially.

## Inputs

- Project capability contract with `capabilities.ios=true` and declared `mobile.strategy`.
- Effective iOS target/toolchain choices from consumer project data.
- Executable Interface Inventory and exact `IOS-###` IDs when the active artifact contract supports iOS inventory materialization.
- Design System/tokens.
- Validated OpenAPI and current API revision.
- Auth/session, permission, Problem Details, request-ID and idempotency contracts.
- Existing iOS Platform Client Architecture Baseline if already approved.
- Offline/runtime/device constraints.
- Optional approved/versioned visual references when they exist.
- Existing iOS client/coexistence constraints for Brownfield.

## Procedure

1. Confirm the project explicitly enables iOS. `mobile.strategy=cross_platform` does not enable iOS by itself.
2. Reuse an approved iOS Platform Client Architecture Baseline when still applicable; otherwise create or revise one using `schemas/client-platform-architecture.schema.json`.
3. Define implementation language/framework, UI toolkit, architecture pattern, networking, local persistence, background execution, deployment target, API client, secure credential lifecycle, state ownership, forms/errors, observability, accessibility, testing and offline policy as consumer decisions. Do not mandate Swift, SwiftUI or any cross-platform framework merely because the target is iOS.
4. If `mobile.strategy=cross_platform`, record which implementation concerns are shared and which remain platform-specific. Shared code never shares architecture acceptance, evidence or gate PASS across Android and iOS.
5. Keep server/API authority explicit even when local persistence or queued work is used. API-backed offline state cannot silently become a competing business authority.
6. For Brownfield, keep coexistence, migration boundary, cutover trigger and rollback explicit. Preserve unrelated working iOS behavior.
7. Create one slice binding with `schemas/client-architecture.schema.json` for the exact `interface_slice + ios` scope and an `CLIENT-IOS-*` architecture ID.
8. Bind only `IOS-###` inventory identifiers. Never substitute legacy Android `APP-###` or Web `WEB-###` identifiers into an iOS binding.
9. Resolve exact permissions, routes/destinations and OpenAPI `operationId` values from repository artifacts. Do not invent iOS-only business operations, permissions or transitions.
10. Record the API revision consumed by the slice. Post-baseline API changes use impact-based revalidation and affect only dependent scopes unless a cross-cutting contract requires broader revalidation.
11. Use `visual_references.mode = none` when approved static references do not exist. If references are used, they must point to real approved/versioned assets.
12. Define async/error/offline states explicitly. Queued writes require synchronization, conflict and idempotency semantics without bypassing server authorization.
13. Record slice-specific cache invalidation, offline overrides and testing notes only where the slice specializes the platform baseline.
14. Run `scripts/validate-client-architecture.py`. Wrong platform IDs, foreign namespaces, incompatible baselines or fabricated references must fail.
15. Attach evidence to scoped `client_architecture_ready` for the exact `interface_slice + ios` boundary. Android or Web evidence cannot satisfy this scope.

## Outputs

- Validated or reused iOS Platform Client Architecture Baseline.
- Schema-valid iOS Slice Architecture Binding.
- Effective Client Architecture for the exact iOS slice/platform.
- Explicit technology/toolchain choice owned by the consumer project.
- Inventory/permission/OpenAPI/API-revision traceability when those artifacts are materialized.
- Explicit API-backed offline specialization when applicable.
- Evidence for scoped `client_architecture_ready`.

## Stop Conditions

- `capabilities.ios` is not true.
- Initial API Gate, Interface Inventory Ready or Design System Ready is not PASS.
- Required `IOS-###` identifiers or canonical operationIds are unresolved.
- The current hardening artifact contract cannot yet validate a required iOS executable inventory artifact.
- The binding invents permissions, endpoints, transitions or business rules.
- Credential storage or logging weakens the platform security model.
- Offline queueing lacks conflict/idempotency semantics.
- A fake visual reference would be created merely to satisfy structure.
- Brownfield replacement would remove working behavior before approved cutover.
- Cross-artifact Client Architecture validation fails.

## Guardrails

- iOS enablement comes only from `capabilities.ios=true`; `cross_platform` never auto-enables a target.
- Reusable iOS decisions belong to the platform baseline; slice-specific choices belong to the binding.
- Blueprint does not mandate Swift, SwiftUI, Flutter, React Native, Kotlin Multiplatform or another framework.
- Cross-platform code sharing does not share platform gates, evidence or human acceptance.
- Static mockups are conditional and never a hidden prerequisite for architecture.
- API remains authoritative for authorization, validation, transitions and business truth.
- Offline persistence is explicit, API-backed and bounded in v0.5.4 hardening.
- iOS alone does not imply the Android-scoped Mobile Licensing capability.
- `client_architecture_ready` for iOS does not authorize Android, Web or another slice.

## Canonical References

- `BLUEPRINT.md`
- `catalog/phases.yaml`
- `catalog/checks.yaml`
- `catalog/gates.yaml`
- `schemas/project.schema.json`
- `schemas/client-platform-architecture.schema.json`
- `schemas/client-architecture.schema.json`
- `documentation/CLIENT_ARCHITECTURE_CONTRACT.md`

## Completion Signal

Complete only when the iOS platform baseline and slice binding compose into a semantically valid effective contract, technology choices remain consumer-owned, referenced permissions/operationIds are real, offline behavior is explicit, optional visual references are legitimate, and scoped `client_architecture_ready` can truthfully evaluate to PASS for the exact slice + iOS platform without borrowing acceptance from another platform.
