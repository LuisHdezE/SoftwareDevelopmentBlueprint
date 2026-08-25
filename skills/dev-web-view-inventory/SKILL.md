---
id: dev-web-view-inventory
title: Web Interface Inventory
version: 0.4.0
status: materialized
category: web
applies_to:
  - greenfield
  - brownfield
phases:
  - interface_inventory
canonical_references:
  - schemas/interface-inventory.schema.json
  - templates/interface-inventory.example.json
  - documentation/EXPERIENCE_ARTIFACT_MODEL.md
  - catalog/gates.yaml
---

# Web Interface Inventory

## Purpose

Create a stable, numbered inventory of actual/planned web interfaces before visual design begins, with enough contract detail for later mockups and implementation.

## When to Use

Use after `api_gate` passes and before visual identity/design-system/mockup planning for web-capable projects.

## Inputs

- Approved API contract.
- Existing routes/components/views for Brownfield projects.
- Roles/permissions.
- Known user journeys and states.

## Procedure

1. Enumerate interface surfaces and deduplicate routes that render the same underlying interface. Do not count nested widgets as full pages unless they are independently navigable surfaces.
2. Assign stable `WEB-###` identifiers. Preserve IDs once referenced by downstream mockups/evidence; deprecate rather than casually renumber.
3. For each view capture purpose, access/roles, data shown, user actions, important states, and related API responsibilities when applicable.
4. For Brownfield, distinguish observed behavior, inferred intent, proposed changes, and observed gaps such as static placeholders or controls without actions.
5. Mark web-only/local behaviors that legitimately have no API endpoint instead of inventing API operations merely to fill a column.
6. Validate the inventory against the schema and register the artifact path in the project manifest/status model.
7. Use the inventory IDs as the only allowed entry points into mockup batches and client slices.

## Outputs

- Schema-valid interface inventory.
- Stable `WEB-###` identifiers.
- Per-view API/permission/state traceability.
- Brownfield observed/inferred/proposed annotations where applicable.

## Stop Conditions

- API Gate is not PASS.
- Interfaces are being invented before requirements/contracts justify them.
- A Brownfield route/component has not been inspected but is described as observed.
- Downstream work references unstable or duplicate view IDs.

## Guardrails

- Route count and screen count are not automatically equal.
- Do not redesign during inventory; describe first.
- UI inventory is a contract for design traceability, not a substitute for API authorization.

## Canonical References

- `schemas/interface-inventory.schema.json`
- `templates/interface-inventory.example.json`
- `documentation/EXPERIENCE_ARTIFACT_MODEL.md`
- `catalog/gates.yaml`

## Completion Signal

The skill is complete only when its required outputs exist in the repository, the relevant Blueprint checks/gates can be evaluated from evidence, and no stop condition remains unresolved.
