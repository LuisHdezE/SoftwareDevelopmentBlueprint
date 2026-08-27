# Experience Artifact Model - Blueprint 0.5.0

## Purpose

Define the repository-owned machine-readable graph that lets a human or AI determine what interfaces exist, which API capabilities they consume, how they are grouped into Functional Interface Slices, which client architecture applies, whether a blocker exists and what evidence supports review, QA and acceptance.

## Recommended consumer layout

```text
.blueprint/
  project.yaml
  status.yaml
  evidence/
  ui/
    interface-scope-baseline.json
    interface-inventory.json
    visual-identity.md              # conditional
    design-system.json
    design-tokens.json
  mockups/                          # conditional
    <batch>/manifest.json
  client-architecture/
    web.platform.json
    android.platform.json
    <slice>.web.json
    <slice>.android.json
  functional-slices/
    <slice>.web.json
    <slice>.android.json
  api-impacts/
    API-IMPACT-###.json
```

Consumer paths may differ when declared in `artifact_locations`.

## Interface maturity

`schemas/interface-inventory.schema.json` owns two maturity levels with stable `WEB-###` / `APP-###` identifiers.

### SCOPE_BASELINE

Created after Requirements Ready. Brownfield records observed/reconciled current interfaces; Greenfield records intended surfaces from requirements/journeys. Unresolved API needs are legal. Missing `operationId` values are not invented.

This maturity is descriptive/planning input and never authorizes implementation.

### EXECUTABLE_INVENTORY

Created after the initial API Gate. It reconciles every baseline ID as COMMITTED, DEFERRED or DROPPED and records requirements, roles, permissions, data/actions, states, navigation, dependencies, priority and slice ownership.

API-backed semantics use canonical OpenAPI `operationId` values. Local/static behavior is declared explicitly.

## Design System and identity

Design System/tokens define reusable visual and interaction rules, responsive behavior, semantic states and accessibility.

Visual Identity is conditional. The model does not require fabricated branding or a custom logo.

## Mockups / prototypes

Mockups are conditional risk-reduction artifacts.

When activated, `schemas/mockup-batch.schema.json` limits a batch to 10 inventory views and records generation/review/accessibility evidence.

State remains explicit:

`PENDING -> GENERATED -> REVIEWED -> APPROVED`

File existence proves generation only. `GENERATED != REVIEWED != APPROVED`.

A normal Functional Interface Slice may have zero mockups.

## Client Architecture

The effective model is:

**Platform Client Architecture Baseline + Slice Architecture Binding = Effective Client Architecture Contract**.

`schemas/client-platform-architecture.schema.json` owns reusable platform/project decisions. `schemas/client-architecture.schema.json` owns exact slice/platform binding and overrides.

The binding references executable inventory, API revision, canonical operationIds, permissions/routes, async states and idempotency. `visual_references.mode = none` is valid; `approved_optional` requires real repository-owned approved paths.

## Functional Interface Slice

`schemas/functional-interface-slice.schema.json` is the canonical client execution artifact.

Lifecycle:

`INVENTORIED -> READY -> IN_PROGRESS -> FUNCTIONAL -> ACCEPTED`

The slice records inventory IDs, dependencies, API revision/operationIds, Client Architecture reference, functional DoD, Visual & Functional Review, Integration QA, human acceptance and evidence IDs.

Review/QA are gates, not lifecycle states.

## BLOCKED_BY_API

A missing authoritative API data source/operation/permission/state/transition may create a `BLOCKED_BY_API` overlay.

The blocker preserves the last valid lifecycle state and records contract/evidence/resolution metadata. An unresolved blocker cannot coexist with `ACCEPTED`.

Ordinary frontend defects are not API blockers.

## API impact artifacts

`schemas/api-impact.schema.json` represents post-baseline API evolution.

It records changed operationIds or cross-cutting areas, affected slices/platforms and the revalidation policy. Operation-local changes preserve unrelated evidence; cross-cutting auth/security/error/versioning changes may widen scope.

## Evidence registry

`schemas/evidence.schema.json` standardizes file, CI, test, OpenAPI, functional slice, QA, accessibility, blocker, API-impact and human-decision evidence.

File-backed evidence must resolve to a real path when repository-local. Human approval/acceptance requires explicit decision metadata. The mere existence of an empty path is not proof of runtime behavior.

## Status ownership

`status.yaml` is a projection/index, not a competing owner of slice lifecycle.

- Functional slice artifact owns lifecycle and blocker state.
- Scoped gates own Client Architecture, functional, review and Integration QA outcomes.
- Project status aggregates/indexes those artifacts for humans and future tooling.

Scoped gates:

- `mockup_review_pass` -> `interface_slice` when the conditional branch applies;
- `client_architecture_ready` -> `interface_slice_platform`;
- `functional_slice_ready` -> `interface_slice_platform`;
- `visual_functional_review_pass` -> `interface_slice_platform`;
- `integration_qa_pass` -> `interface_slice_platform`.

## Cross-Artifact Semantic Integrity

Shape validation alone is insufficient. `scripts/validate-artifact-graph.py` resolves the graph among baseline/inventory, OpenAPI, Functional Interface Slice, status, evidence and API impact.

It rejects unknown inventory IDs, fictitious operationIds, missing reconciliation, cross-platform IDs, invalid evidence, acceptance without QA and unresolved blockers.

`scripts/validate-client-architecture.py` extends the graph through platform baselines and slice bindings, rejecting unknown inventory, permissions, operationIds, incompatible platform baselines, invalid idempotency bindings and fake optional visual references.

`scripts/validate-experience-artifacts.py` validates canonical templates, conditional mockup semantics, catalog/workflow references and invokes artifact-graph validation.

## Brownfield compatibility

Existing evidence is not destroyed merely because a newer Blueprint exists. Brownfield consumers adopt this model through Compliance Review and explicit migration decisions. Existing working clients coexist until approved cutover.

Reference pilots remain evidence sources and are never hidden normative dependencies.
