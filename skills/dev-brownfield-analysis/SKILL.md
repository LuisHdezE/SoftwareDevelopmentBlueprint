---
id: dev-brownfield-analysis
title: Brownfield Analysis and Alignment
version: 0.4.0
status: materialized
category: brownfield
applies_to:
  - brownfield
phases:
  - brownfield_inspection
  - as_is
  - gap_analysis
  - target_definition
canonical_references:
  - BLUEPRINT.md
  - workflows/brownfield.yaml
  - catalog/reference-pilots.yaml
  - schemas/reference-pilots.schema.json
---

# Brownfield Analysis and Alignment

## Purpose

Reconstruct the real existing system before proposing modernization. The governing rule is ALIGN, DO NOT REWRITE.

## When to Use

Use whenever the input is an existing application, repository, archive, database, deployment, or partially documented system that must be aligned to the Blueprint.

## Inputs

- Source code and repository structure.
- Runtime/configuration/deployment information available to the project.
- Existing documentation, tests, API contracts, database assets, and UI surfaces.
- Current Blueprint version and target capabilities.

## Procedure

1. Inspect before proposing. Inventory backend, frontend, mobile, database, dependencies, integrations, security controls, tests, configuration, deployment, and operational evidence.
2. Classify statements as OBSERVED, INFERRED, or PROPOSED. Never present inferred architecture or business rules as observed fact.
3. Produce an AS-IS inventory that identifies working behavior, current contracts, technical debt, documentation drift, and unknowns.
4. Build the GAP analysis against Blueprint requirements without treating architectural difference as a defect by itself.
5. Define TO-BE decisions only where a change has a justified outcome: safety, maintainability, correctness, compatibility, operability, or an explicit product requirement.
6. Create a phased alignment/migration plan that preserves working functionality and supports coexistence where a big-bang replacement would be unsafe.
7. Record evidence paths and unresolved unknowns. Unknowns remain unknown until verified; they do not become assumptions by repetition.

## Outputs

- AS-IS inventory.
- Observed/inferred/proposed separation.
- Gap analysis against the declared Blueprint version.
- TO-BE target decisions.
- Phased alignment or migration plan with preservation/coexistence rules.

## Stop Conditions

- The actual existing solution has not been inspected.
- A proposed rewrite is justified only by aesthetic architecture preference.
- Critical behavior is unknown and the proposed change could destroy it.
- Required evidence is missing and cannot be distinguished from inference.

## Guardrails

- Preserve working behavior unless change is justified and approved.
- Do not copy product-specific rules into reusable Blueprint skills.
- Existing UI/API/database behavior is evidence, not automatically the future contract.
- Brownfield alignment may adopt, migrate, defer, keep, or mark N/A; uniform rewriting is not a success criterion.

## Canonical References

- `BLUEPRINT.md`
- `workflows/brownfield.yaml`
- `catalog/reference-pilots.yaml`
- `schemas/reference-pilots.schema.json`

## Completion Signal

The skill is complete only when its required outputs exist in the repository, the relevant Blueprint checks/gates can be evaluated from evidence, and no stop condition remains unresolved.
