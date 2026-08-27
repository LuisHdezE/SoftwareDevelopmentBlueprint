---
id: dev-web-view-inventory
title: Web Interface Inventory
version: 0.5.0
status: materialized
category: web
applies_to:
  - greenfield
  - brownfield
phases:
  - interface_scope_baseline
  - interface_inventory
canonical_references:
  - schemas/interface-inventory.schema.json
  - templates/interface-scope-baseline.example.json
  - templates/interface-inventory.example.json
  - schemas/functional-interface-slice.schema.json
  - documentation/EXPERIENCE_ARTIFACT_MODEL.md
  - catalog/gates.yaml
---

# Web Interface Inventory

## Purpose

Maintain two explicit maturity levels for web interfaces: an early Interface Scope Baseline that captures real/planned surfaces before API design is final, and a post-API Executable Interface Inventory that becomes the authoritative client backlog.

## When to Use

Use the scope-baseline portion after Requirements Ready and before Architecture/API Contract Design. Reconcile it after the initial `api_gate` to produce `EXECUTABLE_INVENTORY` before Design System, Client Architecture and functional slice execution.

## Inputs

- Approved requirements, use cases, journeys and acceptance criteria.
- Existing routes/components/views for Brownfield.
- Roles/permissions known at the current maturity level.
- Approved OpenAPI and API Gate evidence for executable reconciliation.
- Interface dependencies and intended slice grouping.

## Procedure

1. For early discovery, enumerate actual/planned web surfaces and assign stable `WEB-###` IDs. In Brownfield, inspect real routes/components and classify each item `OBSERVED`, `INFERRED` or `PROPOSED`.
2. Create the Interface Scope Baseline with `maturity: SCOPE_BASELINE`. Capture purpose, module, requirements, roles, required data/actions, navigation, accessibility/responsive intent and unresolved API needs without inventing missing `operationId` values.
3. Do not treat the scope baseline as executable backlog. It informs architecture/API design but does not authorize client implementation.
4. After the initial API Gate passes, create/reconcile `maturity: EXECUTABLE_INVENTORY` from the baseline. Every baseline ID must have explicit `COMMITTED`, `DEFERRED` or `DROPPED` disposition with reason when not committed.
5. For each committed interface, capture stable requirements, roles, permissions, data sources, actions, states, navigation, dependencies, priority and `slice_id`.
6. Bind API-backed data and server actions to canonical OpenAPI `operation_ids`. Legacy `api_ids` may remain for compatibility but cannot replace `operationId` as the primary client API key.
7. A legitimate local/static capability may have no operationId. Label it accurately instead of inventing an API operation.
8. Ensure action permissions are declared on the interface and preserve API authorization as authoritative.
9. Assign each committed interface to a coherent Functional Interface Slice. Preserve IDs after downstream references exist; deprecate/migrate explicitly rather than casually renumbering.
10. Run schema and Cross-Artifact Semantic Integrity validation so missing destinations, dependencies, operationIds or reconciliation entries fail before downstream work.

## Outputs

- Interface Scope Baseline with stable web IDs.
- Executable Interface Inventory reconciled after API Gate.
- Requirement/permission/operationId/dependency traceability.
- Explicit baseline reconciliation decisions.
- Slice backlog with stable `slice_id` assignment.

## Stop Conditions

- Early Brownfield interfaces are described as observed without repository inspection.
- The executable inventory is being produced before the initial API Gate.
- A required API-backed action/data source has no authoritative operationId and is being guessed.
- Baseline interfaces disappear without explicit reconciliation.
- Permissions, dependencies or slice assignment are incomplete for committed interfaces.
- Downstream work references unstable/duplicate IDs.

## Guardrails

- Scope Baseline describes intent/reality; Executable Inventory authorizes downstream client work.
- Route count and interface count are not automatically equal.
- Do not redesign Brownfield behavior while pretending to inventory it.
- API-backed semantics must resolve to real OpenAPI operations.
- Interface Inventory is not a substitute for API authorization or business rules.

## Canonical References

- `schemas/interface-inventory.schema.json`
- `templates/interface-scope-baseline.example.json`
- `templates/interface-inventory.example.json`
- `schemas/functional-interface-slice.schema.json`
- `documentation/EXPERIENCE_ARTIFACT_MODEL.md`
- `catalog/gates.yaml`

## Completion Signal

Complete only when the required maturity level exists and validates. For `interface_inventory_ready`, every committed Web interface is represented in `EXECUTABLE_INVENTORY`, baseline reconciliation is explicit, API-backed semantics resolve to real operationIds, dependencies/permissions/slice IDs are valid, and downstream Functional Interface Slice planning can proceed without invented contract data.
