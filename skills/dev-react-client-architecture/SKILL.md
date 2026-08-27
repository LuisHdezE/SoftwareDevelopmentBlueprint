---
id: dev-react-client-architecture
title: React Client Architecture
version: 0.5.0-dev
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
  - schemas/client-platform-architecture.schema.json
  - schemas/client-architecture.schema.json
  - schemas/interface-inventory.schema.json
  - schemas/functional-interface-slice.schema.json
  - documentation/CLIENT_ARCHITECTURE_CONTRACT.md
---

# React Client Architecture

## Purpose

Produce the effective Client Architecture contract for one web Functional Interface Slice without repeating platform-wide decisions in every slice.

## When to Use

Use after `interface_inventory_ready` and `design_system_ready`, with the initial `api_gate` already PASS, and before functional Web implementation. Static mockups are not a prerequisite. Revalidate when platform architecture, API revision/operationIds, inventory scope or slice-specific behavior changes materially.

## Inputs

- Executable Interface Inventory and exact `WEB-###` IDs for the slice.
- Design System/tokens.
- Validated OpenAPI and current API revision.
- Auth/session, permission, Problem Details, request-ID and idempotency contracts.
- Existing Web platform baseline if one is already approved.
- Optional approved/versioned visual references when they exist.
- Existing client/coexistence constraints for Brownfield.

## Procedure

1. Reuse an approved Web Platform Client Architecture Baseline when its project/platform/API-wide decisions still apply; otherwise create or revise one with `schemas/client-platform-architecture.schema.json`.
2. In the platform baseline define React rendering mode, router, server-state/form libraries, build/browser policy, API client, auth lifecycle, state ownership, forms/error mapping, observability, accessibility, testing, offline policy and implementation guardrails.
3. For Brownfield, keep coexistence, migration boundary, cutover trigger and rollback in the platform baseline. Preserve unrelated working UI.
4. Create one slice binding using `schemas/client-architecture.schema.json` for the exact `interface_slice + web` scope.
5. Bind only executable `WEB-###` inventory IDs. Resolve exact permissions, routes and canonical OpenAPI `operationId` values from repository artifacts rather than copying guesses from prose.
6. Record the API revision consumed by the slice. API evolution after the initial gate must use impact-based revalidation rather than resetting every client indiscriminately.
7. Set `visual_references.mode = none` when no approved static references exist. When references are used, set `approved_optional` and require real approved/versioned repository paths. Never fabricate a path to satisfy the schema.
8. Define required loading/empty/error/401/403/404/409/422/429/offline states from the actual inventory/contract.
9. Define idempotent operations as a subset of the bound `operationId` set and specify user-intent key generation, replay handling and same-key/different-payload conflict behavior.
10. Record slice-specific cache invalidation, offline overrides and testing notes only where they differ from or specialize the platform baseline.
11. Keep API authorization and business semantics authoritative. The client may present permissions but cannot invent endpoints, hidden permissions, transitions or authoritative business data.
12. Run `scripts/validate-client-architecture.py` so the effective contract is checked against executable inventory and OpenAPI. Fictitious IDs, permissions, operationIds, baseline mismatches and fake visual paths must fail.
13. Attach validation/review evidence to scoped `client_architecture_ready` for the exact `interface_slice + web` boundary.

## Outputs

- Validated/reused Web Platform Client Architecture Baseline.
- Schema-valid Web Slice Architecture Binding.
- Effective Client Architecture for the exact slice/platform.
- Inventory/permission/OpenAPI/API-revision traceability.
- Optional approved visual-reference binding when used.
- Evidence for scoped `client_architecture_ready`.

## Stop Conditions

- Initial API Gate, Interface Inventory Ready or Design System Ready is not PASS.
- Inventory IDs or canonical operationIds are unresolved.
- The binding invents permissions/endpoints/business semantics.
- Platform baseline weakens auth, storage, authorization or observability controls.
- A fake/unapproved visual reference is being added only to satisfy structure.
- Brownfield replacement would remove working behavior before approved cutover.
- Cross-artifact Client Architecture validation fails.

## Guardrails

- Platform-wide decisions live in the reusable baseline; slice-specific decisions live in the binding.
- Mockups/prototypes are conditional risk-reduction artifacts, not hidden architecture gates.
- API and executable Interface Inventory remain authoritative.
- Do not hardcode authoritative business data as implementation architecture.
- `client_architecture_ready` for Web does not authorize Android or another slice.

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

Complete only when the Web platform baseline and slice binding compose into a semantically valid effective contract, all referenced inventory/permissions/operationIds exist, optional visual references are legitimate, and scoped `client_architecture_ready` can truthfully evaluate to PASS for the exact slice + Web platform.
