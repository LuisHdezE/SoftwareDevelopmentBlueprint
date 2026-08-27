# Blueprint 0.5.0 Release Notes

Release date: **2026-08-26 (America/Montevideo)**

Previous stable: `0.4.0`

## Summary

Blueprint 0.5.0 turns post-API client delivery into a functional, slice-based and semantically verifiable workflow. It preserves the API as the authoritative security/business boundary while letting interface needs be discovered early enough to inform architecture and API design.

This release does **no automatic consumer upgrade**. Existing projects remain on their declared Blueprint version until a Compliance Review and explicit adoption change are approved.

## Major changes

### Interface Scope Baseline before API design

Interfaces can now be captured after Requirements Ready using `maturity: SCOPE_BASELINE`.

Brownfield records observed/reconciled current surfaces; Greenfield records intended surfaces from requirements/journeys. Unresolved API needs are allowed at this maturity and do not authorize invented bindings.

After the initial API Gate, the artifact matures to `EXECUTABLE_INVENTORY`, reconciling every baseline interface and binding committed API-backed behavior to real OpenAPI `operationId` values.

### Functional Interface Slice

`Functional Interface Slice` is the canonical client execution unit for one `slice + platform`.

Lifecycle is intentionally small:

`INVENTORIED -> READY -> IN_PROGRESS -> FUNCTIONAL -> ACCEPTED`

Visual & Functional Review and Integration QA remain quality gates rather than duplicated lifecycle states.

`FUNCTIONAL` requires the real functional DoD, including real API integration, auth/RBAC, forms/errors, observability, responsive/accessibility, tests, traceability, no hardcoded authoritative business data and no invented server capability.

### BLOCKED_BY_API overlay

A missing authoritative data source, operation, permission, state or transition creates `BLOCKED_BY_API` without destroying lifecycle history.

The affected client boundary stops, the API/backend is corrected separately, impact is assessed and the slice resumes only with resolution/revalidation evidence.

### API evolution and impact-based revalidation

The initial `api_gate` remains project-scoped. Later contract changes are represented by `schemas/api-impact.schema.json`.

Operation-local changes revalidate dependent slices only. Auth, authorization, security, error-contract, versioning and other cross-cutting changes can escalate scope. Unrelated accepted evidence is preserved by default.

### Client Architecture composition

Client Architecture is now composed as:

`Platform Client Architecture Baseline + Slice Architecture Binding = Effective Client Architecture Contract`

Shared platform decisions are declared once, while each slice binds executable inventory IDs, routes, permissions, API revision/operationIds and slice-specific behavior.

Static visual references are optional. `visual_references.mode = none` is valid and no fake mockup/reference path is required.

### Mockups become conditional

Mockups/prototypes remain supported as a deliberate risk-reduction branch, but they are no longer universal prerequisites for client implementation.

When used, `GENERATED != REVIEWED != APPROVED` remains mandatory and approved assets must be versioned.

### Visual & Functional Review on the real client

The review gate evaluates the actual functional client, including Design System fidelity, API/permission behavior, business-data fidelity, states, responsive behavior and accessibility. Explicit human completion is required.

### Cross-Artifact Semantic Integrity

0.5.0 adds semantic validation across real repository artifacts:

`requirement -> interface -> permission -> operationId -> Functional Interface Slice -> Client Architecture -> evidence/test -> review/QA -> acceptance`.

Negative fixtures reject nonexistent inventory IDs, fictitious operationIds, invented permissions, cross-platform namespace drift, invalid evidence references, incompatible client baselines, unresolved blockers and acceptance without required gates.

### Evidence hardening

Evidence distinguishes repository files, runtime reports, CI, test/QA, API impact and human decisions. File existence alone is insufficient for runtime claims. Human approvals carry explicit decision metadata.

### Skills

The materialized skill set grows from 13 to **14** with `dev-functional-interface-slice`. All materialized skills are stabilized at Blueprint 0.5.0 and aligned with the same API-authoritative functional-delivery model.

## Core counts

- 28 phases
- 134 checks
- 18 gates
- 14 materialized skills
- 25 planned skills

## External audit response

Before freezing schemas, the v0.5 model received adversarial external review. The accepted findings produced V5-1A and strengthened:

- early Brownfield/interface discovery without moving executable delivery before API Gate;
- impact-based API invalidation instead of reflexive global resets;
- five-state lifecycle + quality gates;
- `BLOCKED_BY_API` overlay semantics;
- deduplicated Client Architecture;
- Cross-Artifact Semantic Integrity;
- schema provenance/versioning.

The complete disposition remains in `documentation/BLUEPRINT_V0_5_EXTERNAL_AUDIT_RESPONSE.md`.

## Compatibility

- consumer_auto_upgrade: false
- Brownfield: ALIGN, DO NOT REWRITE
- existing evidence: grandfathered unless a Compliance Review identifies a real incompatibility
- mockups/prototypes: conditional
- API revalidation after baseline: impact-based
- Web and Android approvals remain independently scoped

Historical 0.4 release manifests and Compliance Reviews remain unchanged as historical truth.

## Consumer adoption

Publishing 0.5.0 does not mutate CareShift, CUSA-Digital or another consumer.

For CUSA-Digital the intended post-release sequence is:

1. verify Blueprint `main`, `VERSION` and tag;
2. verify CUSA `main` and `.blueprint/status.yaml` live;
3. perform Compliance Review `0.4.0 -> 0.5.0`;
4. classify KEEP / ADOPT / MIGRATE / DEFER / N/A;
5. adopt 0.5.0 only with explicit approval;
6. then continue Interface Inventory Ready and Functional Interface Slices.

## Strategic boundary

Blueprint Control Center remains deferred. 0.5.0 stabilizes Blueprint Core and its machine-readable delivery contracts first.

## Tag rule

The release tag is `v0.5.0`. It is created only after the release PR is merged, the approved tree is verified on `main` and post-merge validation passes. A release branch or manifest alone is not proof that the tag already exists.
