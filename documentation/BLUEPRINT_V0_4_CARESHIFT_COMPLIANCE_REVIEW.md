# Blueprint v0.4.0 — CareShift Compliance Review

> Review ID: `CR-CARESHIFT-V0.4`  
> Pilot: `LuisHdezE/CareShift_Manager`  
> Baseline: Blueprint `0.3.0`  
> Target: Blueprint `0.4.0-dev`  
> Review date: `2026-08-25`  
> Policy: **ALIGN, DO NOT REWRITE**  
> Consumer mutation during this review: **NO**

## 1. Executive decision

**Recommendation: `ADOPT_INCREMENTALLY`.**

CareShift validates Blueprint v0.4 without requiring a rewrite of the pilot. Existing v0.3 Brownfield, API, Interface Inventory and Design System evidence remains valid. The pilot must not be cosmetically reorganized merely to resemble a fresh v0.4 project.

The review contains **24 decisions**:

- **KEEP:** 8
- **ADOPT:** 9
- **MIGRATE:** 1
- **DEFER:** 4
- **N/A:** 2

The only item classified **MIGRATE** is the pending mockup manifest representation. The four already-generated visual assets remain valid repository-owned evidence and must not be regenerated merely to satisfy the new schema.

## 2. Verified pilot snapshots

The review is pinned to exact repository state:

- Blueprint `main`: `fb5ea5f82c80bc4b7afe600834ca3f681254b70b` after merged V4-4.
- CareShift `main`: `afeb2f7928f884285d473f9989fb5acae650e9cc`.
- CareShift `blueprint/mockups-batch-01`: `81822e07397397e3beab7eb8d317b5d2c0243ab7`.
- At review time the mockup branch is **13 commits ahead / 0 behind** current CareShift `main`.
- Neither repository had an open PR when V4-5 began.

CareShift remains declared on Blueprint `0.3.0`; this review does not change that consumer declaration.

## 3. What the pilot already proves

CareShift retains, without re-validation for version cosmetics:

- Brownfield inspection, AS-IS, Gap Analysis and TO-BE evidence.
- Requirements, architecture/security/data and audit evidence.
- API Contract Ready and API implementation evidence.
- OpenAPI, Postman, live HTTP/MySQL API QA, security and audit verification.
- `API_GATE = PASS`.
- The 30-item Brownfield Interface Inventory with `WEB-###` identities and explicit web-only exceptions.
- Visual Identity, Design System and machine-readable Design Tokens.
- The existing project-specific mockup batch validator.
- The four generated/versioned SVG mockup references.

This is the practical meaning of grandfathering existing v0.3 evidence.

## 4. Compliance matrix

| Finding | Area | Decision | Required action |
|---|---|---|---|
| CRF-001 | Brownfield governance | **KEEP** | Preserve existing evidence and observed/inferred/proposed semantics. |
| CRF-002 | API pipeline | **KEEP** | Grandfather the existing API PASS evidence. |
| CRF-003 | Interface Inventory semantics | **KEEP** | Keep the 30-view canonical Markdown inventory. |
| CRF-004 | Machine-readable inventory | **ADOPT** | Add a non-destructive JSON companion/adapter when CareShift adopts v0.4. |
| CRF-005 | Visual Identity / Design System | **KEEP** | Preserve existing identity, tokens, responsive, RBAC and accessibility rules. |
| CRF-006 | Artifact locations | **ADOPT** | Point v0.4 `artifact_locations` to the real existing CareShift paths. |
| CRF-007 | Post-API phase decomposition | **ADOPT** | Add mockup planning, visual review and client architecture phase state on upgrade. |
| CRF-008 | Interface slices / scoped gates | **ADOPT** | Represent Operational Core as a scoped web slice. |
| CRF-009 | Mockup planning fundamentals | **KEEP** | Preserve the ten-view batch, prompts, API IDs and asset mapping. |
| CRF-010 | Mockup manifest schema | **MIGRATE** | Convert/add a v0.4-compatible manifest without changing view identities or assets. |
| CRF-011 | Generated/reviewed/approved distinction | **ADOPT** | Keep the four current visuals as `GENERATED` until explicitly reviewed. |
| CRF-012 | Visual Review Gate | **ADOPT** | Add contract, accessibility and manual review before implementation. |
| CRF-013 | Four generated SVGs | **KEEP** | Preserve and review them, do not regenerate for schema cosmetics. |
| CRF-014 | Six remaining mockups | **DEFER** | Resume only when CareShift returns to mockup product work. |
| CRF-015 | Web client architecture | **DEFER** | Create only after a slice reaches `visual_review_pass`. |
| CRF-016 | React modernization / cutover | **DEFER** | Keep Livewire active until scoped React + integration/release evidence exists. |
| CRF-017 | Brownfield coexistence | **ADOPT** | Require coexistence, cutover criteria and rollback in future client architecture. |
| CRF-018 | Android | **N/A** | CareShift has no Android capability/source. |
| CRF-019 | Materialized reusable skills | **ADOPT** | Consume them from the master Blueprint version, do not copy them into CareShift. |
| CRF-020 | Pilot-specific mockup validator | **KEEP** | Retain it and compose with v0.4 schema validation later. |
| CRF-021 | Physical path relocation | **N/A** | Do not move files solely to match recommended folder aesthetics. |
| CRF-022 | CareShift Blueprint version bump | **DEFER** | Keep `0.3.0` until Blueprint `0.4.0` is formally released and adoption is approved. |
| CRF-023 | Reference pilot governance | **KEEP** | Keep CareShift non-normative and attach this review as evidence. |
| CRF-024 | v0.4 status/evidence extensions | **ADOPT** | Add only new slice/scoped UI structures; grandfather previous PASS evidence. |

The machine-readable rationale and evidence for every row lives in `documentation/BLUEPRINT_V0_4_CARESHIFT_COMPLIANCE_REVIEW.json`.

## 5. Mockup branch decision

The pending batch is intentionally preserved.

Its existing contract already has strong reusable properties:

- exactly 10 planned views;
- stable `M01-##` mockup IDs;
- stable `WEB-###` inventory IDs;
- canonical `API-*` responsibilities;
- four repository-owned generated SVGs;
- six views explicitly `PENDING`;
- batch-level specification/visual/manual-review state.

The v0.4 schema separates concepts the older manifest compresses. A future CareShift adoption slice should represent:

- `batch_id` and `interface_slice`;
- per-view `platform`;
- `generation_status`;
- `review_status`;
- `contract_review_status`;
- `accessibility_review_status`;
- `reference_inputs`;
- evidence IDs where useful;
- v0.4 batch completion semantics.

**No generated asset becomes APPROVED through migration.**

The four current SVGs remain `GENERATED` until explicit contract, accessibility and manual review is completed.

## 6. Minimal future CareShift adoption slice

When Blueprint `0.4.0` is released and CareShift explicitly adopts it, the recommended consumer change is deliberately small:

1. Update `.blueprint/project.yaml` to declare Blueprint `0.4.0` and `artifact_locations` pointing to the **existing** CareShift artifacts.
2. Extend `.blueprint/status.yaml` with the v0.4 post-API phases plus `interface_slices` and scoped gates needed by future UI work. Existing API PASS evidence is grandfathered.
3. Add a machine-readable Interface Inventory companion/adapter derived from the existing canonical Markdown inventory if schema-based automation is desired.
4. Migrate or add a v0.4-compatible mockup manifest for `Operational Core`, preserving the ten view identities, four current assets and six pending views.
5. Review the four generated visual references. Only explicitly approved views may populate `approved_references`.
6. Continue generating the remaining six images only when CareShift resumes product mockup work.
7. Create a v0.4 web client architecture contract only after the relevant interface slice passes `visual_review_pass`.
8. Keep the existing Livewire/Blade client operational until scoped React implementation, integration QA and release cutover are approved.

No physical move to `.blueprint/ui/...` is required merely for path uniformity.

## 7. React / Brownfield coexistence decision

React modernization remains **DEFERRED**, not rejected.

CareShift's current browser client is functional. Blueprint v0.4 now gives it a safe coexistence path:

`existing Livewire client → approved interface slice → visual review → web client architecture → React slice → integration QA → explicit cutover`

The API remains the authorization boundary throughout. A React slice must not silently redefine endpoints, permissions, auth lifecycle, idempotency or error semantics.

## 8. Android decision

Android is **N/A** for the current CareShift repository:

- `capabilities.android = false`;
- the inventory found no Android application source;
- no Android gate or client architecture artifact is required.

The Android v0.4 contract remains part of the Blueprint for other consumers.

## 9. Blueprint-level conclusion

The pilot demonstrates that v0.4 closes the principal gaps from the original audit:

- post-API phases are explicit;
- visual approval is slice-scoped;
- generated assets cannot imply approval;
- visual references remain versioned for AI continuity;
- client architecture is explicit before React/Kotlin implementation;
- Brownfield client coexistence is representable;
- reusable skills are executable repository artifacts;
- a v0.3 consumer can be reviewed without forced rewrite.

The compliance outcome therefore supports closing V4-5 after review and merge.

## 10. Version decision

This V4-5 review **does not** bump either repository automatically:

- Blueprint `VERSION` remains the last stable release until v0.4 is formally closed.
- CareShift remains on Blueprint `0.3.0` until `0.4.0` is released and a separate consumer adoption PR is explicitly approved.

Machine-readable source:

`documentation/BLUEPRINT_V0_4_CARESHIFT_COMPLIANCE_REVIEW.json`
