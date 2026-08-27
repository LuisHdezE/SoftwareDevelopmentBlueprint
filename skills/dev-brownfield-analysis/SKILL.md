---
id: dev-brownfield-analysis
title: Brownfield Analysis and Alignment
version: 0.5.0-dev
status: materialized
category: brownfield
applies_to:
  - brownfield
phases:
  - brownfield_inspection
  - as_is
  - gap_analysis
  - target_definition
  - interface_scope_baseline
canonical_references:
  - BLUEPRINT.md
  - workflows/brownfield.yaml
  - schemas/interface-inventory.schema.json
  - catalog/reference-pilots.yaml
  - schemas/reference-pilots.schema.json
---

# Brownfield Analysis and Alignment

## Purpose

Reconstruct the real existing system before proposing modernization. The governing rule is ALIGN, DO NOT REWRITE. Blueprint 0.5 also requires existing interface reality to be captured early enough to inform architecture/API design without pretending the executable client contract already exists.

## When to Use

Use whenever the input is an existing application, repository, archive, database, deployment or partially documented system that must be aligned to the Blueprint.

## Inputs

- Source code and repository structure.
- Runtime/configuration/deployment information available to the project.
- Existing documentation, tests, API contracts, database assets and UI surfaces.
- Existing roles/permissions, workflows and integrations.
- Current adopted Blueprint version and target capabilities.

## Procedure

1. Inspect before proposing. Inventory backend, frontend, mobile, database, dependencies, integrations, security controls, tests, configuration, deployment and operational evidence.
2. Classify statements as `OBSERVED`, `INFERRED` or `PROPOSED`. Never present inferred architecture, UI purpose or business rules as observed fact.
3. Produce the AS-IS inventory identifying working behavior, contracts, technical debt, documentation drift, unknowns and current client surfaces.
4. Reconstruct functional behavior and user-facing interfaces from real routes/views/components/screens. Preserve stable identifiers where downstream evidence already depends on them.
5. Build Gap Analysis against the adopted Blueprint without treating architectural difference as a defect by itself.
6. Define TO-BE decisions only where change has a justified outcome: safety, correctness, maintainability, compatibility, operability or explicit product need.
7. Create a phased alignment/migration plan supporting coexistence when big-bang replacement would risk working functionality.
8. After requirements are reconciled, capture observed/proposed client surfaces in the early Interface Scope Baseline. This artifact may record unresolved API needs and must not invent `operationId` values that do not yet exist.
9. Treat Interface Scope Baseline as planning evidence, not executable implementation permission. After the initial API Gate, reconcile it into Executable Interface Inventory with explicit COMMITTED/DEFERRED/DROPPED decisions.
10. Record evidence paths and unresolved unknowns. Unknowns remain unknown until verified; repetition never upgrades an assumption into fact.
11. When replacing a working Brownfield client slice, preserve unrelated behavior and define coexistence/cutover/rollback through Client Architecture before implementation.

## Outputs

- Technical and functional AS-IS inventory.
- Observed/inferred/proposed separation.
- Gap Analysis against the adopted Blueprint.
- TO-BE target decisions.
- Phased alignment/migration plan.
- Early Interface Scope Baseline for relevant client surfaces.
- Explicit preservation/coexistence constraints.

## Stop Conditions

- The actual existing solution has not been inspected.
- A rewrite is justified only by architectural taste.
- Critical behavior is unknown and the proposed change could destroy it.
- Proposed interfaces are being labeled OBSERVED without repository/runtime evidence.
- Missing API semantics are being fabricated in the early interface baseline.
- Required evidence is absent and cannot be distinguished from inference.

## Guardrails

- Preserve working behavior unless change is justified and approved.
- `OBSERVED`, `INFERRED` and `PROPOSED` remain distinct throughout alignment.
- Existing UI/API/database behavior is evidence, not automatically the future contract.
- Interface Scope Baseline is descriptive/planning input; Executable Interface Inventory is the post-API client backlog.
- Brownfield alignment may adopt, migrate, defer, retain or mark N/A; uniform rewriting is not success.
- Reference pilots may demonstrate lessons but never become hidden product norms.

## Canonical References

- `BLUEPRINT.md`
- `workflows/brownfield.yaml`
- `schemas/interface-inventory.schema.json`
- `catalog/reference-pilots.yaml`
- `schemas/reference-pilots.schema.json`

## Completion Signal

Complete only when the real system has been inspected, AS-IS and evidence are traceable, gaps/TO-BE/migration decisions are explicit, observed client surfaces are represented at the appropriate maturity level, and no destructive Brownfield proposal depends on an unresolved assumption disguised as fact.
