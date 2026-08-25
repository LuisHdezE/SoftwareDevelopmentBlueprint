# Software Development Blueprint 0.4.0 — Release Notes

> Release: `0.4.0`  
> Previous stable: `0.3.0`  
> Release date: `2026-08-25`  
> Release branch: `blueprint/release-v0.4.0`

## 1. Release objective

Blueprint 0.4.0 makes the post-API experience/client delivery pipeline as explicit, scoped, machine-readable and evidence-driven as the API pipeline established in 0.3.0.

This is a backward-aware minor release. It extends the process without automatically invalidating consumer evidence produced under 0.3.0.

## 2. Delivery slices included

The release is the reviewed composition of six boundaries:

| Slice | Pull request | Result |
| --- | --- | --- |
| V4-0 — Audit & specification freeze | PR #4 | Pilot findings and release roadmap established. |
| V4-1 — Frontend & Experience gates | PR #5 | Post-API phases/checks/gates formalized. |
| V4-2 — Schemas, templates & evidence | PR #6 | Experience artifacts and scoped status model became machine-readable. |
| V4-3 — Executable reusable skills | PR #7 | Core `dev-*` skills became real repository-owned procedures. |
| V4-4 — Client Architecture contract | PR #8 | React/Kotlin pre-implementation architecture became schema-valid and scoped. |
| V4-5 — Reference Pilot Compliance Review | PR #9 | CareShift was evaluated without automatic migration or rewrite. |

No new normative feature is introduced by the release-closure boundary after V4-5. Closure stabilizes version identity, release/current-state documentation and full-suite validation.

## 3. Stable core counts

Blueprint 0.4.0 contains:

- **25 phases**;
- **92 checks**;
- **14 gates**;
- **13 materialized reusable skills**;
- **25 planned skills**.

The counts are validated automatically and are not release prose only.

## 4. New experience pipeline

After `API_GATE = PASS`, the canonical sequence is:

```text
Interface Inventory
  → Visual Identity
  → Design System
  → Mockup Planning
  → Mockup Generation
  → Visual Review Gate
  → Client Architecture
  → Web / Android Implementation
  → Integration QA
```

The pipeline supports incremental interface delivery rather than requiring every product screen to be approved at once.

## 5. Scoped gates

### `visual_review_pass`

Evaluated per `interface_slice`.

A generated image is not an approval artifact. Versioned visual assets must pass explicit review, contract alignment and accessibility requirements before they authorize downstream work.

Rule:

`GENERATED ≠ REVIEWED ≠ APPROVED`

### `client_architecture_ready`

Evaluated per `interface_slice + platform`.

A PASS for a web slice does not authorize Android, another slice, or unapproved inventory views.

## 6. Machine-readable experience artifacts

0.4.0 adds reusable schema/template contracts for:

- Interface Inventory;
- Design Tokens;
- Design System;
- Mockup batches;
- Evidence/artifacts;
- scoped project status;
- Client Architecture;
- Reference Pilots;
- Compliance Review.

Approved visual references and important prompts/manifests belong in the consumer repository or another explicitly versioned source. Chat history is not an acceptable sole source of continuity.

## 7. Client Architecture contract

Before React/Kotlin implementation begins for an approved slice, the architecture artifact must explicitly resolve:

- auth/session lifecycle and credential storage;
- API client/OpenAPI binding;
- permissions and API-side enforcement;
- routing/navigation;
- server state/local UI state and cache invalidation;
- forms and API validation/error mapping;
- loading/empty/error/401/403/404/409/422/429/offline behavior;
- idempotency for high-risk mutations;
- request correlation, telemetry and secret/PII redaction;
- accessibility;
- testing strategy;
- offline/synchronization when applicable;
- React or Kotlin/Android platform decisions;
- Brownfield coexistence, cutover and rollback when applicable.

## 8. Skills materialized in 0.4.0

- `dev-git-workflow`
- `dev-brownfield-analysis`
- `dev-api-design`
- `dev-openapi`
- `dev-postman-qa`
- `dev-contract-testing`
- `dev-web-view-inventory`
- `dev-design-system`
- `dev-mockup-planning`
- `dev-accessibility`
- `dev-react-client-architecture`
- `dev-android-client-architecture`
- `dev-event-logging-audit`

The remaining 25 catalog entries are explicitly `planned`. They must not be treated as executable skills until materialized.

## 9. Reference Pilot result

`LuisHdezE/CareShift_Manager` remains a non-normative Brownfield reference pilot.

V4-5 result:

- KEEP: 8
- ADOPT: 9
- MIGRATE: 1
- DEFER: 4
- N/A: 2

Recommendation: `ADOPT_INCREMENTALLY`.

The only migration identified was the pending mockup manifest representation. Existing API evidence, the 30-view Interface Inventory, Visual Identity, Design System and four generated SVG references remain valid.

CareShift continues to declare Blueprint **0.3.0** until a separate consumer-adoption PR explicitly applies the approved changes. Release of the master Blueprint does not alter the consumer repository.

## 10. Compatibility policy

0.4.0 preserves these rules:

- consumer auto-upgrade: **false**;
- existing v0.3 evidence may be grandfathered after Compliance Review;
- Brownfield: **ALIGN, DO NOT REWRITE**;
- path relocation is not mandatory when compatibility/artifact-location metadata can describe existing valid files;
- current clients may coexist with new clients until cutover/release approval;
- API remains the authorization and business-contract boundary.

## 11. Deliberately deferred work

Not required for Blueprint 0.4.0 stability:

- materializing the 25 remaining planned skills;
- completing the six pending CareShift mockups;
- approving the four generated CareShift SVGs by implication;
- creating the CareShift React client architecture artifact;
- implementing/cutting over React in CareShift;
- automatically migrating CareShift to Blueprint 0.4.0;
- Blueprint Control Center;
- Blueprint 1.0.

## 12. Release validation

The release branch must pass `scripts/validate-release.py`, which verifies release identity/counts/workflows/templates and executes:

1. `validate-experience-artifacts.py`;
2. `validate-skills.py`;
3. `validate-client-architecture.py`;
4. `validate-reference-pilot-compliance.py`.

The release PR must be validated on its exact final head.

## 13. Tagging rule

The planned stable tag is `v0.4.0`.

It must **not** be created from the release branch before review. Tagging occurs only after:

1. the release PR is merged by the human reviewer;
2. merged `main` is verified to contain the exact approved release tree;
3. `VERSION` on `main` is `0.4.0`;
4. release validation remains green.
