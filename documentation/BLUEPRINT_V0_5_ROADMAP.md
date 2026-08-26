# Blueprint v0.5.0 - Functional Client Delivery Roadmap

> Baseline estable: Blueprint `0.4.0`  
> Baseline commit: `b8092a1a6da6d0e765ccd6f5ff93d5147a712e0d`  
> Source audit: `documentation/BLUEPRINT_V0_5_POST_API_AUDIT.md`  
> Greenfield evidence source: `LuisHdezE/CUSA-Digital`  
> Delivery rule: one active implementation PR per review boundary.  
> Consumer rule: no automatic Blueprint adoption.

## 1. Objective

Blueprint 0.5.0 will evolve the post-API/client pipeline from a mockup-centered approval chain into an inventory-first, architecture-first and functional-slice delivery model.

The release is complete when another AI can inspect the Blueprint plus a consumer repository and determine without chat history:

- the complete committed interface backlog;
- which requirements/use cases each interface serves;
- which actors/permissions apply;
- which canonical OpenAPI operation IDs provide data/actions;
- which interfaces belong to each Functional Interface Slice;
- which dependencies block a slice;
- whether a blocker is specifically `BLOCKED_BY_API`;
- which Client Architecture contract governs the slice/platform;
- whether implementation is merely started or genuinely `FUNCTIONAL`;
- whether authoritative business data is coming from real approved sources;
- whether functional, responsive, accessibility, visual and integration QA have passed;
- whether human acceptance has occurred;
- whether mockups/prototypes existed and, if so, which references were actually approved;
- which evidence proves each state/gate.

## 2. Target post-API model

Target principal chain:

```text
API Gate
  -> Interface Inventory Ready
  -> Design System Ready
  -> Client Architecture Ready
  -> Functional Interface Slice
  -> Visual & Functional Review
  -> Integration QA
  -> Release Gate
```

Conditional capabilities:

```text
Visual Identity       -> feeds Design System when applicable
Mockups / Prototypes  -> optional risk-reduction branch
```

The exact final phase/check/gate IDs are decided and validated in V5-1/V5-2. This roadmap defines semantic intent, not unreviewed catalog counts.

## 3. Core v0.5 invariants

The implementation must preserve these rules throughout every boundary:

1. `API_GATE = PASS` before client delivery starts.
2. Complete applicable Interface Inventory precedes functional backlog execution.
3. Design System precedes functional client implementation.
4. Client Architecture precedes implementation for the exact slice + platform.
5. API remains the authoritative authorization and business boundary.
6. Client code does not invent endpoints, permissions, business states or transitions.
7. A missing authoritative server capability produces `BLOCKED_BY_API`, not fabricated frontend behavior.
8. A view using hardcoded authoritative business data cannot be declared `FUNCTIONAL`.
9. `GENERATED != REVIEWED != APPROVED` remains true for generated mockups/prototypes/references.
10. Static mockups are conditional and cannot replace review of the real functional client.
11. Functional, responsive, accessibility and integration evidence are slice-aware.
12. A web approval does not authorize Android and an Android approval does not authorize web.
13. Brownfield continues `ALIGN, DO NOT REWRITE` and preserves working clients until approved cutover.
14. `GENERATED`, automated PASS or CI green status never substitutes required human acceptance.
15. Consumer Blueprint versions never change automatically.
16. Reference pilots prove/challenge the process but are not hidden normative dependencies.
17. One active implementation PR per review boundary unless explicitly justified.

## 4. Delivery boundaries

### V5-0 - Post-API audit & roadmap

**Goal**

Freeze the problem definition and delivery strategy before changing canonical behavior.

**Scope**

Create only:

- `documentation/BLUEPRINT_V0_5_POST_API_AUDIT.md`
- `documentation/BLUEPRINT_V0_5_ROADMAP.md`

Document:

- verified 0.4.0 baseline;
- verified CUSA API Gate state;
- structural mockup dependency;
- complete-inventory-first model;
- Functional Interface Slice;
- interface lifecycle;
- `BLOCKED_BY_API`;
- no-hardcoded-authoritative-business-data rule;
- Functional Definition of Done;
- Client Architecture repositioning;
- mockups as conditional capability;
- Visual & Functional Review;
- slice-aware QA;
- compatibility strategy;
- Control Center strategic debt;
- CUSA freeze and post-release adoption sequence.

**Explicitly out of scope**

- `BLUEPRINT.md` changes;
- `VERSION` changes;
- catalog/schema/workflow/template/skill/validator changes;
- CUSA mutations;
- Control Center implementation.

**Exit criteria**

- audit and roadmap are internally consistent;
- no normative master behavior changed;
- no consumer repository changed;
- PR is reviewed and human-approved before merge;
- V5-1 starts only from the new merged `main`.

---

### V5-1 - Canonical Functional Delivery phase/gate model

**Goal**

Change the normative process graph while keeping schemas/artifacts for the next boundary.

**Primary files**

- `BLUEPRINT.md`
- `catalog/phases.yaml`
- `catalog/checks.yaml`
- `catalog/gates.yaml`
- `workflows/greenfield.yaml`
- `workflows/brownfield.yaml`
- release/development validation support only as required to allow coherent prerelease changes.

**Required semantic changes**

#### Interface Inventory

- remains project-scoped;
- becomes complete committed-scope backlog prerequisite;
- requires stable identities and traceability sufficient for later functional execution.

#### Visual Identity

- no longer an unconditional pipeline station merely to produce branding;
- applies when product identity/brand direction is required or when Brownfield identity must be preserved/normalized;
- Design System remains required for applicable client delivery.

#### Mockups/prototypes

- remove from the mandatory principal sequence;
- represent as `CONDITIONAL` capability or conditional phase branch;
- preserve generation/review/approval semantics when used.

#### Client Architecture

- move before functional implementation;
- preserve `interface_slice + platform` evaluation scope;
- remove normative dependency on mandatory static visual approval;
- continue requiring Design System and authoritative API contract.

#### Functional Interface Slice

Formalize canonical execution unit.

Target lifecycle semantics:

```text
INVENTORIED
  -> READY
  -> IN_PROGRESS
  -> FUNCTIONAL
  -> VISUAL_FUNCTIONAL_REVIEW
  -> INTEGRATION_QA
  -> ACCEPTED
```

Additional explicit blocker:

```text
BLOCKED_BY_API
```

#### Visual & Functional Review

- review actual functional client;
- include optional comparison with approved visual references;
- remain evidence-backed and human-reviewable;
- cannot be inferred from implementation existence.

#### QA

- allow functional/integration evaluation per slice/platform;
- final Release Gate still requires appropriate project/release integration and security confidence.

**Checks to introduce or redefine conceptually**

Exact IDs are frozen during implementation review, but coverage must include:

- complete inventory/backlog traceability;
- requirements/use-case linkage;
- permission linkage;
- operationId linkage;
- slice membership/dependencies;
- Client Architecture contract binding;
- real API usage;
- no hardcoded authoritative business data;
- no invented API/business capability;
- functional routing/components/forms/states;
- auth/session/RBAC behavior;
- error contract mapping;
- responsive implementation;
- accessibility implementation;
- test evidence;
- visual/functional review;
- integration QA;
- human acceptance;
- `BLOCKED_BY_API` evidence/resolution.

**Gate strategy**

Preserve:

- `api_gate`
- `interface_inventory_ready`
- `design_system_ready`
- `client_architecture_ready` scoped to `interface_slice_platform`
- `release_gate`

Replace/redefine the old static `visual_review_pass` semantics with a Visual & Functional Review gate/check model scoped to the actual functional slice.

Introduce a functional completion/acceptance gate only if it adds clear machine-readable value instead of duplicating lifecycle status. The catalog and status schema must have one owner for each semantic concept.

**Prerelease validation requirement**

Current `validate-release.py` hardcodes the stable v0.4 pipeline and counts. V5-1 must establish a safe development-validation path that allows 0.5 work without falsely changing `VERSION` or weakening stable-release validation.

Preferred policy:

- `VERSION` remains `0.4.0` until final release boundary;
- branch artifacts/catalogs may identify `0.5.0-dev` where supported;
- release validators distinguish stable 0.4 historical validation from active v0.5 development validation rather than simply disabling checks.

**Exit criteria**

- Greenfield and Brownfield workflows express the same v0.5 client-delivery semantics;
- mockups are no longer required to reach Client Architecture/functional implementation;
- Client Architecture remains a hard pre-implementation contract;
- API authority and no-invented-capability rules are explicit;
- Functional Interface Slice lifecycle and `BLOCKED_BY_API` are normative;
- no arbitrary phase/check/gate counts are chosen in advance;
- validators/CI needed for this boundary pass;
- PR is human-reviewed before merge.

---

### V5-2 - Schemas, status, templates & evidence model

**Goal**

Make the V5-1 process machine-readable and executable by consumers and future AI agents.

**Schemas to update**

- `schemas/interface-inventory.schema.json`
- `schemas/status.schema.json`
- `schemas/project.schema.json`
- `schemas/evidence.schema.json`
- `schemas/mockup-batch.schema.json`
- review `schemas/design-system.schema.json`
- review `schemas/design-tokens.schema.json`

**New recommended schema**

- `schemas/functional-interface-slice.schema.json`

A dedicated `visual-functional-review.schema.json` should be added only if status/evidence + slice schema cannot represent review cleanly without semantic duplication.

#### Interface Inventory target fields

Each interface should support enough data to act as executable backlog, including as applicable:

- stable ID;
- platform;
- module;
- name;
- route/navigation target;
- purpose;
- requirement/use-case/acceptance references;
- roles;
- permissions;
- authoritative data sources;
- canonical operation IDs;
- actions + operation IDs + permissions;
- states;
- forms/validation expectations;
- responsive expectations;
- accessibility expectations;
- dependencies;
- priority/order;
- Functional Interface Slice assignment or planned grouping;
- implementation status;
- integration status;
- QA status/evidence references;
- Visual & Functional Review status;
- human acceptance status;
- blocker reference / `BLOCKED_BY_API` state.

Backward-aware compatibility fields may preserve older `api_ids` where useful, but canonical OpenAPI `operationIds` become first-class for client execution.

#### Functional Interface Slice schema

Should cover at minimum:

- slice ID/name;
- platform scope;
- inventory IDs;
- dependencies;
- Client Architecture artifact reference;
- required operation IDs;
- optional approved visual references;
- lifecycle status;
- blocker metadata;
- Definition of Done checks/evidence;
- functional QA;
- responsive QA;
- accessibility QA;
- Visual & Functional Review;
- Integration QA;
- human acceptance;
- evidence IDs.

#### `BLOCKED_BY_API`

Machine-readable representation should capture:

- blocker ID;
- affected interface/slice;
- blocked-from status;
- missing capability category;
- missing data/operation/permission/state/transition description;
- current authoritative contract reference;
- evidence;
- opened/resolved timestamps;
- resolution reference.

#### Status schema

Must expose progress useful to both humans and a future Control Center without requiring dashboard implementation.

It should support:

- interface/slice lifecycle;
- platform-aware scoped gates;
- blockers;
- review/QA states;
- acceptance;
- artifact/evidence references.

#### Project schema

Review artifact locations for:

- functional slices;
- functional review/QA evidence;
- mockups as optional location/capability rather than an implied mandatory root.

#### Evidence schema

Review evidence types/scopes for:

- functional implementation;
- functional QA;
- accessibility/responsive QA;
- integration/E2E;
- blocker records;
- visual-functional review;
- human acceptance.

Avoid excessive specialized evidence types if a generic auditable type + scope is sufficient.

**Templates to update/add**

Update:

- `templates/interface-inventory.example.json`
- `templates/status.example.yaml`
- `templates/project.example.yaml`
- `templates/evidence.example.json`
- `templates/mockup-batch.example.json`

Add:

- `templates/functional-interface-slice.example.json`

**Validator/test changes**

Update `validate-experience-artifacts.py` or split responsibilities if the validator becomes too broad.

Required positive scenarios:

- inventory validates as complete functional backlog example;
- functional slice validates without mockups;
- functional slice validates with optional approved mockups;
- `BLOCKED_BY_API` can be represented before FUNCTIONAL;
- accepted slice has required review/QA/acceptance evidence.

Required negative scenarios:

- slice references unknown inventory ID;
- platform namespace mismatch;
- unresolved blocker combined with illegal later lifecycle state;
- accepted without required QA/review;
- operation ID not bound to slice/client contract;
- mockup approval inferred from generation;
- mandatory business/API guardrails disabled.

**Exit criteria**

- schemas and examples validate;
- inventory is demonstrably executable as backlog;
- Functional Interface Slice is machine-readable;
- `BLOCKED_BY_API` is machine-readable;
- mockups can be absent without invalidating normal functional delivery;
- mockups remain governed correctly when present;
- status/evidence can support future Control Center views without implementing the Control Center.

---

### V5-3 - Client Architecture decoupling & pre-implementation contract

**Goal**

Align the existing strong Client Architecture contract with the v0.5 sequence.

**Primary files**

- `schemas/client-architecture.schema.json`
- `templates/client-architecture.web.example.json`
- `templates/client-architecture.android.example.json`
- `documentation/CLIENT_ARCHITECTURE_CONTRACT.md`
- `scripts/validate-client-architecture.py`
- client architecture CI workflow
- related fixtures/tests.

**Required changes**

Preserve required decisions for:

- inventory IDs;
- Design System/tokens;
- OpenAPI/operation IDs;
- auth/session;
- API client;
- permissions;
- routing;
- state/cache;
- forms/errors;
- async/offline states;
- idempotency;
- observability/request correlation;
- accessibility;
- testing;
- web/Android platform specifics;
- Brownfield coexistence.

Change visual binding so:

- Design System/tokens remain required;
- approved reference paths become optional/conditional;
- when references exist, only approved/versioned references are allowed as authoritative visual guidance;
- absence of mockups does not invalidate architecture;
- implementation remains limited to inventory IDs assigned to the slice/platform.

Add/strengthen guardrails:

- `no_hardcoded_authoritative_business_data` or equivalent normative assertion/evidence contract;
- no invented endpoints/permissions/business transitions;
- API remains authoritative;
- operation IDs consumed by the slice must align with Inventory/Functional Slice bindings.

**Validator negative cases**

- Client Architecture incorrectly requires a fake visual reference to validate;
- unapproved visual asset declared authoritative;
- operation IDs outside slice binding;
- API-authority guardrail disabled;
- web/Android namespace crossing;
- Brownfield coexistence missing;
- unsafe auth/idempotency semantics.

**Exit criteria**

- valid web/Android architecture can exist with zero mockups;
- optional approved references remain enforceable;
- exact slice/platform scoping is preserved;
- all semantic safety tests pass;
- Client Architecture clearly precedes functional implementation.

---

### V5-4 - Executable Functional Slice skills & QA guidance

**Goal**

Give AI agents executable procedures for the new client-delivery model rather than relying on catalog names alone.

**Update materialized skills**

- `dev-web-view-inventory`
- `dev-design-system`
- `dev-mockup-planning`
- `dev-accessibility`
- `dev-react-client-architecture`
- `dev-android-client-architecture`
- `dev-contract-testing` if needed for operation/test traceability.

**Materialize new skill**

- `dev-functional-interface-slice`

**Functional slice skill required flow**

```text
select coherent inventory slice
  -> validate dependencies
  -> validate Client Architecture for slice + platform
  -> verify API operation/permission bindings
  -> implement real routing/components
  -> integrate real API
  -> implement auth/RBAC/forms/errors/states
  -> enforce idempotency/correlation
  -> implement responsive/accessibility behavior
  -> add tests
  -> prove no hardcoded authoritative business data
  -> mark FUNCTIONAL only after DoD
  -> Visual & Functional Review
  -> Integration QA
  -> human acceptance
```

**Mockup skill change**

`dev-mockup-planning` remains materialized but becomes conditional:

Use when visual/UX risk or approval needs justify it, not for every interface by default.

It must preserve:

```text
GENERATED != REVIEWED != APPROVED
```

**Accessibility skill change**

Shift emphasis from per-mockup approval to continuous Design System + functional client + QA evidence while still reviewing mockups when they exist.

**Skill catalog**

- add `dev-functional-interface-slice` to the appropriate client/web/android/core profile strategy;
- remove it from planned registry if previously introduced there;
- do not count it materialized until `skills/dev-functional-interface-slice/SKILL.md` actually exists;
- update mandatory current-version materialized naming without falsifying historical 0.4 data.

**Exit criteria**

- all materialized catalog entries resolve to real files;
- skill validator passes;
- new slice skill is executable and product-independent;
- mockup skill is clearly conditional;
- React/Android architecture skills no longer require static visual approval;
- no CUSA-specific implementation detail leaks into reusable skills.

---

### V5-5 - Integration validation, documentation & release 0.5.0

**Goal**

Close the release only after the complete canonical surface is coherent.

**Validation work**

Update/execute as applicable:

- `scripts/validate-experience-artifacts.py`
- `scripts/validate-client-architecture.py`
- `scripts/validate-functional-interface-slices.py` if introduced
- `scripts/validate-skills.py`
- `scripts/validate-reference-pilot-compliance.py` only to preserve truthful historical pilot boundaries, not to rewrite CareShift review history
- `scripts/validate-release.py`
- all Blueprint CI workflows.

Release validation must derive/freeze actual completed counts rather than reusing v0.4 constants.

**Human documentation**

Update:

- `README.md`
- `documentation/BLUEPRINT_CURRENT_STATE.md`
- `documentation/EXPERIENCE_ARTIFACT_MODEL.md`
- `documentation/CLIENT_ARCHITECTURE_CONTRACT.md`
- functional slice documentation introduced during V5
- `documentation/SKILL_MODEL.md` if current-version semantics changed.

Create:

- `documentation/BLUEPRINT_V0_5_RELEASE_NOTES.md`
- `documentation/BLUEPRINT_V0_5_RELEASE.json`

Historical v0.4 release artifacts remain historical and must not be rewritten to pretend they used v0.5 semantics.

**Version closure**

Only after canonical validation and human approval:

```text
VERSION: 0.4.0 -> 0.5.0
```

Versioned active catalogs/workflows/skills/templates that require current stable identity must be reconciled to 0.5.0 according to validator rules.

**Release requirements**

- all schemas valid;
- all templates valid;
- Greenfield/Brownfield workflows coherent;
- Client Architecture supports no-mockup path;
- mockup conditional path validated;
- Functional Interface Slice positive/negative fixtures pass;
- `BLOCKED_BY_API` behavior validated;
- skill validator passes;
- release validator passes;
- release/current-state documentation matches canonical state;
- no consumer repository auto-upgraded;
- no CUSA interface implementation performed as part of master release;
- human review/approval obtained before merge/release/tag.

**Exit criteria**

Blueprint 0.5.0 is stable only when the merged `main` tree itself passes release validation and the release/tag points to the accepted tree.

---

## 5. Proposed consumer artifact model after v0.5 adoption

Recommended layout direction:

```text
.blueprint/
  project.yaml
  status.yaml
  evidence/
  ui/
    interface-inventory.json
    visual-identity.md            # when applicable
    design-system.json
    design-tokens.json
  client-architecture/
    <slice-id>.web.json
    <slice-id>.android.json
  functional-slices/
    <slice-id>.web.json
    <slice-id>.android.json
  mockups/                        # conditional
    <batch-id>/
      manifest.json
      specification.md
      prompts.md
      assets/
```

The exact paths remain configurable through project artifact locations when appropriate.

## 6. Example target inventory execution record

Illustrative only, final schema belongs to V5-2:

```yaml
id: WEB-ADM-007
name: Tariff Detail
platform: web
module: tariffs
route: /admin/tariffs/:id

requirements:
  - FR-TAR-007
roles:
  - cusa_admin
permissions:
  - tariff.read

data_sources:
  - operation_id: getTariff

actions:
  - name: edit
    operation_id: updateTariff
    permission: tariff.update

states:
  - loading
  - ready
  - forbidden
  - not_found
  - validation_error
  - server_error

responsive:
  mobile: required
  tablet: required
  desktop: required

implementation:
  status: INVENTORIED
integration:
  status: PENDING
functional_qa:
  status: PENDING
visual_functional_review:
  status: PENDING
human_acceptance:
  status: PENDING
blocker: null
```

This example demonstrates the target semantics only. CUSA will not receive this artifact during Blueprint 0.5 construction.

## 7. Functional Definition of Done target

Before a slice can transition to `FUNCTIONAL`, evidence must demonstrate applicable items from this contract:

```text
routing/navigation real
components real
Design System applied
real authoritative API binding
auth/session
permission-aware UI
API authorization authoritative
forms + validation
Problem Details / approved error contract
loading/empty/error
401/403/404/409/422/429 when applicable
offline/degraded behavior when applicable
idempotency for high-risk mutations
request correlation
responsive behavior
accessibility behavior
no invented API/business capability
no hardcoded authoritative business data
minimum tests
inventory + requirement + permission + operationId traceability
```

V5-2/V5-4 will turn this target into machine-readable checks/evidence and executable procedures.

## 8. What 0.5.0 must preserve from 0.4.0

This is an evolution, not a rewrite.

Preserve:

- Greenfield + Brownfield;
- `ALIGN, DO NOT REWRITE`;
- Requirements/Architecture/API gates;
- persistent business/security audit principles;
- machine-readable evidence;
- single source of truth;
- stable interface identities;
- Design System/tokens;
- versioned approved visual assets when they exist;
- `GENERATED != REVIEWED != APPROVED`;
- API enforcement/authorization;
- idempotency;
- request correlation;
- cache/offline not silently becoming business source of truth;
- platform-specific Client Architecture scope;
- Brownfield coexistence/cutover/rollback;
- SemVer;
- Compliance Review before consumer adoption;
- reference pilots as non-normative evidence.

## 9. Historical artifacts policy

Do not rewrite historical 0.4 artifacts to make history look like 0.5 existed earlier.

Preserve as historical truth:

- `documentation/BLUEPRINT_V0_4_RELEASE.json`
- `documentation/BLUEPRINT_V0_4_RELEASE_NOTES.md`
- `documentation/BLUEPRINT_V0_4_ROADMAP.md`
- CareShift v0.4 Compliance Review artifacts and reviewed SHAs.

Current docs such as `BLUEPRINT.md`, README and Current State may evolve in v0.5 boundaries because they describe active/current canonical behavior.

## 10. CUSA adoption sequence after v0.5.0

CUSA remains untouched by V5 implementation boundaries except read-only verification if needed.

After release:

1. start a new chat/boundary;
2. verify `SoftwareDevelopmentBlueprint/main`, `VERSION`, release/tag and open PRs;
3. verify `CUSA-Digital/main`, `.blueprint/status.yaml` and open PRs;
4. run Compliance Review `0.4.0 -> 0.5.0`;
5. decide KEEP / ADOPT / MIGRATE / DEFER / N/A as appropriate;
6. explicitly change CUSA's adopted Blueprint version only after approval;
7. begin `Interface Inventory Ready`;
8. inventory every applicable R1 web interface;
9. convert inventory into the executable functional backlog;
10. group/order slices by real dependencies;
11. implement one Functional Interface Slice/boundary at a time using the real API;
12. stop and use `BLOCKED_BY_API` if the authoritative contract is insufficient;
13. review actual functional UI;
14. run slice integration QA and human acceptance.

## 11. Blueprint Control Center debt

Control Center remains strategic debt, not a V5 delivery boundary.

Future dashboard goals include:

- consumers and adopted versions;
- phase/check/gate state;
- evidence;
- compliance/drift;
- interface inventory progress;
- functional slice lifecycle;
- `BLOCKED_BY_API` blockers;
- functional/responsive/accessibility/integration QA;
- release status.

V5 should expose metadata that makes this future work possible, but it must not create a separate control-plane database, dashboard app or runtime service now.

Strategic order remains:

```text
Blueprint Core
  -> pilots CareShift/CUSA
  -> hardening
  -> Blueprint Control Center
  -> future 1.0 readiness
```

## 12. Branch/PR discipline

Each boundary begins from the merged `main` of the previous accepted boundary.

Suggested branches:

```text
V5-0  blueprint/v0.5-audit-functional-slices
V5-1  blueprint/v0.5-functional-delivery-model
V5-2  blueprint/v0.5-functional-artifacts
V5-3  blueprint/v0.5-client-architecture
V5-4  blueprint/v0.5-functional-slice-skills
V5-5  blueprint/release-v0.5.0
```

Rules:

- do not stack V5-1 on an unmerged V5-0 branch;
- do not auto-merge;
- verify CI and diff before human acceptance;
- merge only the accepted boundary;
- verify new `main` after each merge;
- create the next branch from that verified `main`;
- do not force-push published history merely for cosmetic cleanup;
- do not update consumers as a side effect of master release.

## 13. Immediate next action

V5-0 is documentation-only.

Once its PR is reviewed and human-approved:

```text
merge V5-0
  -> verify Blueprint main
  -> confirm no unexpected PRs/drift
  -> create V5-1 from that exact main
  -> implement canonical functional delivery phase/gate model
```

Do not begin V5-1 changes on the V5-0 branch.
