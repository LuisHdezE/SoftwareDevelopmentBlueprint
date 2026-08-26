# Blueprint v0.5.0 - Post-API Functional Delivery Audit

> Status: DRAFT AUDIT / V5-0  
> Source Blueprint stable: `0.4.0`  
> Reviewed master baseline: `LuisHdezE/SoftwareDevelopmentBlueprint@b8092a1a6da6d0e765ccd6f5ff93d5147a712e0d`  
> Pilot evidence source: `LuisHdezE/CUSA-Digital@f3f22538cd6871d355fa71f0b66ddf14a03bbb11`  
> Audit date: `2026-08-26`  
> Audit mode: **PRESERVE / ADJUST / NEW LEARNING / DEFER**

## 1. Purpose

This audit evaluates the Blueprint 0.4.0 post-API/client-delivery model after using CUSA-Digital as a Greenfield pilot through an accepted API Gate.

The goal is not to copy CUSA-specific requirements into the master Blueprint. The goal is to promote only reusable process knowledge that improves client delivery for Greenfield and Brownfield consumers.

The central question is:

> How should Blueprint move from an API-complete product to real functional web/Android clients while preserving traceability, security, evidence, human review and AI continuity, without forcing static mockups for every interface?

CUSA remains evidence. Blueprint remains product-independent and normative only through versioned master changes.

## 2. Repository hygiene and frozen baseline

At V5-0 start:

- `SoftwareDevelopmentBlueprint/main` is `b8092a1a6da6d0e765ccd6f5ff93d5147a712e0d`.
- `VERSION` remains `0.4.0`.
- tag `v0.4.0` resolves to the same stable main commit.
- Blueprint has no open pull requests.
- `CUSA-Digital/main` is `f3f22538cd6871d355fa71f0b66ddf14a03bbb11`.
- CUSA has no open pull requests.
- CUSA `.blueprint/status.yaml` records `api_implemented`, `openapi_valid`, `postman_ready`, `api_qa_pass` and `api_gate` as `PASS`.
- CUSA's accepted API Gate unlocks only `Interface Inventory Ready` under Blueprint 0.4.0.

Decision:

- Freeze CUSA client/interface work while Blueprint 0.5.0 is designed, implemented, reviewed and released.
- Do not mutate CUSA merely to demonstrate the proposed v0.5 model.
- After v0.5.0 release, run a separate CUSA Compliance Review and explicit adoption boundary before any interface implementation.

## 3. Executive finding

Blueprint 0.4.0 already contains most of the right primitives:

- complete Interface Inventory identities (`WEB-###`, `APP-###`);
- Design System and design tokens;
- `interface_slice` delivery scope;
- `client_architecture_ready` scoped by slice + platform;
- API-first authorization and business truth;
- OpenAPI/operation binding in Client Architecture;
- auth/session, RBAC presentation, routing, state/cache, forms/errors, idempotency, observability, accessibility, testing and offline decisions;
- Brownfield coexistence/cutover/rollback;
- evidence and scoped gates;
- explicit `GENERATED != REVIEWED != APPROVED` semantics.

The main maturity gap is not absence of client structure. It is the dependency graph.

Blueprint 0.4.0 currently requires the following post-API chain:

```text
API Gate
  -> Interface Inventory
  -> Visual Identity
  -> Design System
  -> Mockup Planning
  -> Mockup Generation
  -> Visual Review
  -> Client Architecture
  -> Web / Android Implementation
  -> Integration QA
```

This makes static mockup production and mockup approval a near-universal prerequisite for Client Architecture and implementation.

The CUSA Greenfield pilot exposed a more efficient reusable model:

1. inventory the complete product interface surface first;
2. make that inventory an executable backlog;
3. establish Design System and Client Architecture before implementation;
4. execute coherent Functional Interface Slices against the real API;
5. review the functional client that will actually ship;
6. use mockups/prototypes only when they reduce visual or UX risk.

Therefore Blueprint 0.5.0 should evolve the delivery unit from an **approved static visual slice** to an **evidence-backed Functional Interface Slice**.

## 4. Structural dependency found in v0.4

The mockup dependency is encoded in multiple canonical layers, so changing only `BLUEPRINT.md` would be incorrect.

### 4.1 Phase catalog

`catalog/phases.yaml` currently expresses:

```text
design_system
  -> mockup_planning
  -> mockups
  -> visual_review_gate
  -> client_architecture
```

`client_architecture` requires `visual_review_pass`.

### 4.2 Gate catalog

`visual_review_pass` currently requires mockup-specific checks including:

- mockup plan;
- batch limit;
- visual generation;
- versioned assets;
- asset mapping;
- contract review;
- accessibility review;
- approved visual references.

`client_architecture_ready` then blocks implementation until that visual gate has passed.

### 4.3 Client Architecture schema

`schemas/client-architecture.schema.json` requires a `visual_contract` containing non-empty `approved_reference_paths`.

The schema therefore assumes approved static visual references exist before Client Architecture can be valid.

### 4.4 Skills

Both React and Android Client Architecture skills currently stop when `visual_review_pass` has not passed and require approved/versioned visual references as inputs.

### 4.5 Validators

`validate-experience-artifacts.py`, `validate-client-architecture.py` and `validate-release.py` encode v0.4 mockup and visual-review semantics.

Conclusion:

> Mockups cannot become conditional through documentation alone. The dependency must be removed coherently from phases, gates, schemas, templates, skills, validators, tests and release validation.

## 5. Audit matrix

| Area | Classification | Blueprint 0.4.0 state | Required v0.5 action |
|---|---|---|---|
| Greenfield + Brownfield modes | PRESERVE | Explicit and shared post-API model | Preserve. |
| Brownfield `ALIGN, DO NOT REWRITE` | PRESERVE | Normative | Preserve across all client modernization changes. |
| API Gate before clients | PRESERVE | Strong project gate | Preserve. No client business implementation before API Gate. |
| API as authorization boundary | PRESERVE | Explicit in Blueprint and Client Architecture | Preserve and strengthen in Functional Slice DoD. |
| API as business truth | ADJUST | Present through client guardrails/cache rules | Make explicit for functional interfaces and hardcoded-data prohibition. |
| Interface stable IDs | PRESERVE | `WEB-###` / `APP-###` | Preserve. Stable identity remains foundational. |
| Complete product inventory | ADJUST | Inventory exists but slices may progress independently | Require complete R1/applicable interface inventory before implementation backlog execution starts. |
| Inventory as executable backlog | NEW LEARNING | Inventory is mainly design/traceability input | Add priority, dependencies, slice assignment, implementation/integration/QA/review/acceptance status and API blockers. |
| Requirement traceability per interface | ADJUST | Generic traceability exists | Make interface -> requirement/use-case/acceptance references machine-readable where practical. |
| Permission traceability per interface | PRESERVE/ADJUST | Roles/permissions are represented | Keep and make required where access-controlled. |
| API traceability | ADJUST | Inventory uses `api_ids`; Client Architecture uses canonical operation IDs | Make OpenAPI `operationIds` first-class in interface/slice execution. Preserve compatibility metadata if older API IDs exist. |
| Test traceability | NEW LEARNING | Testing strategy exists at Client Architecture level | Add interface/slice test evidence linkage. |
| Design System before implementation | PRESERVE | Strong project gate | Preserve. |
| Visual Identity | ADJUST | Required phase in canonical sequence | Treat as applicable capability feeding Design System, not a mandatory branding exercise. |
| Mockup Planning | ADJUST | Required before every visual slice | Reclassify as CONDITIONAL capability. |
| Mockup Generation | ADJUST | Required predecessor to visual review | Reclassify as CONDITIONAL capability. |
| Approved visual references | ADJUST | Mandatory Client Architecture input | Optional/conditional input. When present, remain versioned and governed by `GENERATED != REVIEWED != APPROVED`. |
| `GENERATED != REVIEWED != APPROVED` | PRESERVE | Strong invariant | Preserve for any generated artifact or prototype. |
| Interface Slice | ADJUST | Exists as visual/review grouping | Promote to Functional Interface Slice, canonical unit of execution and QA. |
| Client Architecture | ADJUST | Correct content but downstream of mockup approval | Move before Functional Slice implementation and decouple from mandatory visual references. |
| Client Architecture scope | PRESERVE | `interface_slice + platform` | Preserve. A web PASS never authorizes Android and vice versa. |
| Functional lifecycle | NEW LEARNING | Not represented canonically | Add `INVENTORIED -> READY -> IN_PROGRESS -> FUNCTIONAL -> VISUAL_FUNCTIONAL_REVIEW -> INTEGRATION_QA -> ACCEPTED`. |
| `BLOCKED_BY_API` | NEW LEARNING | Generic BLOCKED exists | Add explicit client/interface blocker meaning missing authoritative API data/permission/operation/transition. |
| API gap handling | NEW LEARNING | UI cannot invent API behavior | Add explicit stop/resume procedure and separate backend/API boundary requirement. |
| Hardcoded business data | NEW LEARNING | No explicit functional DoD prohibition | A view using hardcoded authoritative business data cannot be `FUNCTIONAL`. |
| Fixtures/mocks | ADJUST | Not explicitly separated from production functional status | Allow only in tests, Storybook/prototypes or explicitly isolated development contexts. |
| Functional Definition of Done | NEW LEARNING | Client architecture defines prerequisites, not runtime completion | Add canonical DoD for routing, real API, auth, RBAC, forms, errors, states, responsive, accessibility and tests. |
| Visual review | ADJUST | Static visual artifact centered | Replace with Visual & Functional Review over actual implemented client, with optional approved reference comparison. |
| Responsive QA | ADJUST | Design/architecture requirement exists | Require per-slice implementation evidence. |
| Accessibility QA | ADJUST | Continuous principle exists | Require per-slice implementation evidence plus manual checks appropriate to risk. |
| Functional QA | NEW LEARNING | Generic Integration QA exists | Add slice-level functional QA before acceptance. |
| Integration QA | ADJUST | Global generic phase | Make slice-scoped integration evidence possible while preserving project/release integration gate. |
| Human acceptance | ADJUST | Gate approvals exist | Represent explicit acceptance at functional slice/interface level before final accepted status. |
| Brownfield coexistence | PRESERVE | Explicit in Client Architecture | Preserve until replacement slice passes required QA/cutover approval. |
| Control Center metadata | DEFER | Control Center is out of 0.4 scope | Add only metadata needed naturally by v0.5 contracts; do not build dashboard now. |
| CUSA client implementation | DEFER | API Gate PASS, next gate unlocked | Do not start until v0.5 release + Compliance Review + explicit adoption. |

## 6. Target principle: Inventory First

Blueprint 0.5 should make the complete applicable Interface Inventory the authoritative client backlog.

`Interface Inventory Ready` should mean more than "the next batch has IDs". It should mean that the product's currently committed delivery scope has been enumerated enough to reason about:

- what interfaces exist;
- which platform each belongs to;
- which requirement/use case they satisfy;
- who can access them;
- what permissions they require;
- what authoritative data they consume;
- what operations/actions they invoke;
- what states and errors they must handle;
- how they navigate;
- what dependencies they have;
- how they group into coherent Functional Interface Slices;
- which items are blocked by missing API capability;
- what implementation/QA/review state each item has.

The inventory becomes the source for execution order, not merely a source for image generation.

## 7. Proposed interface lifecycle

Canonical progress model:

```text
INVENTORIED
  -> READY
  -> IN_PROGRESS
  -> FUNCTIONAL
  -> VISUAL_FUNCTIONAL_REVIEW
  -> INTEGRATION_QA
  -> ACCEPTED
```

Additional explicit state:

```text
BLOCKED_BY_API
```

### 7.1 INVENTORIED

The interface has a stable ID and satisfies the inventory contract.

### 7.2 READY

Dependencies required to implement the interface are known and available, including applicable Client Architecture, Design System, API operation IDs, permissions and prerequisite interfaces/slices.

### 7.3 IN_PROGRESS

Functional implementation has begun.

### 7.4 FUNCTIONAL

The interface satisfies the functional Definition of Done and uses the real authoritative API for business data/operations when required.

### 7.5 VISUAL_FUNCTIONAL_REVIEW

The actual functional interface is under review for visual quality, interaction behavior, responsive behavior, accessibility, contract fidelity and consistency with approved references when such references exist.

### 7.6 INTEGRATION_QA

The interface/slice is undergoing integration and system-level validation against its actual dependencies.

### 7.7 ACCEPTED

Required automated/manual evidence has passed and human acceptance has been explicitly recorded according to project governance.

### 7.8 BLOCKED_BY_API

The interface cannot progress because the authoritative API contract lacks required data, operation, permission semantics, state/transition or another server capability.

This status must not be used for ordinary frontend defects or design uncertainty.

## 8. `BLOCKED_BY_API` contract

When a functional interface reaches an API contract gap, the client must not invent business behavior.

Required behavior:

1. stop the affected implementation boundary;
2. mark the interface/slice `BLOCKED_BY_API`;
3. record the exact missing authoritative capability;
4. identify affected inventory IDs and operation IDs, if any;
5. attach evidence;
6. open a separate API/backend boundary when the gap is valid and in scope;
7. update authoritative API contracts first;
8. re-evaluate client dependencies;
9. resume the slice only after the blocker is resolved and evidenced.

A blocker record should be machine-readable enough to expose at least:

- blocker ID;
- affected interface/slice;
- blocked-from status;
- reason/category;
- missing data/operation/permission/state/transition;
- evidence;
- opened timestamp;
- resolution status;
- resolved timestamp when applicable.

## 9. Required rule: no hardcoded authoritative business data

Normative target for v0.5:

> A client interface cannot satisfy `FUNCTIONAL` using hardcoded business data when an authoritative API/data source is required by the product contract.

Examples that do not satisfy FUNCTIONAL when authoritative API data is required:

- hardcoded tariff lists;
- hardcoded marketplace records;
- hardcoded users/roles representing runtime business truth;
- hardcoded operational/audit records;
- fake success transitions that bypass the API.

Allowed uses include:

- static presentation copy;
- labels and icon metadata;
- design constants/tokens;
- explicit test fixtures;
- Storybook/component examples;
- prototypes/mockups;
- isolated development fixtures clearly marked non-functional/non-production.

Because this rule cannot be proven solely by JSON Schema, completion evidence should combine contract metadata, implementation tests, validator rules where practical and code/review evidence.

## 10. Functional Interface Slice

Blueprint 0.5 should define **Functional Interface Slice** as the canonical unit of client execution, functional QA, visual/functional review and acceptance.

A slice is a coherent product capability, user flow or module composed of stable inventory IDs.

Examples:

- authentication;
- public navigation;
- tariffs;
- simulator;
- marketplace;
- administration;
- RBAC;
- audit.

A slice may include multiple interfaces and may progress independently when its dependencies are satisfied.

The logical slice identity may be cross-platform, but architecture, implementation evidence and approval must remain platform-aware where behavior differs.

Therefore:

```text
slice tariffs + web != slice tariffs + android
```

A PASS/ACCEPTED state for one platform never authorizes another platform implicitly.

## 11. Functional Definition of Done

An interface/slice may become `FUNCTIONAL` only when applicable requirements are satisfied and evidenced.

Minimum target DoD:

- real routing/navigation;
- real implementation components;
- approved Design System/tokens used;
- real authoritative API integration for business data/actions;
- auth/session lifecycle implemented where required;
- permission-aware presentation implemented;
- API authorization remains authoritative;
- forms and client-side feedback implemented where applicable;
- server validation mapping preserved;
- approved Problem Details/error contract handled;
- applicable loading/empty/error states implemented;
- applicable 401/403/404/409/422/429 states implemented;
- offline/degraded state handled when applicable;
- high-risk mutations follow API idempotency requirements;
- request correlation/diagnostic context preserved;
- responsive behavior implemented;
- accessibility requirements implemented;
- no invented API capability;
- no hardcoded authoritative business data;
- minimum tests for the slice are present;
- traceability to inventory IDs, requirements, permissions and canonical operation IDs exists.

`FUNCTIONAL` does not mean visually perfect or release-ready. It means the product behavior is real enough to review and QA.

## 12. Target Client Architecture position

Client Architecture remains required before functional implementation.

Proposed sequence:

```text
Interface Inventory Ready
  -> Design System Ready
  -> Client Architecture Ready
  -> Functional Interface Slice implementation
```

Client Architecture must continue to define:

- platform and inventory IDs;
- Design System/tokens;
- OpenAPI and operation IDs;
- auth/session lifecycle;
- API client strategy;
- permissions/RBAC presentation;
- routing;
- server/local state ownership;
- cache/invalidation;
- forms/error mapping;
- async/offline states;
- idempotency;
- request correlation/observability;
- accessibility;
- testing;
- platform-specific React/Kotlin decisions;
- Brownfield coexistence/cutover/rollback when applicable.

Change required:

- approved mockup/reference paths must no longer be mandatory.
- optional approved references, when present, remain governed and versioned.
- absence of static mockups cannot by itself block a schema-valid Client Architecture contract.

## 13. Mockups and prototypes become conditional

Mockups/prototypes remain a supported Blueprint capability because they can reduce risk.

Use them when one or more of these conditions apply:

- multiple visual directions must be compared;
- human visual approval is required before code;
- UX risk is high;
- a flow is interaction-heavy or ambiguous;
- a future AI benefits from an explicit visual reference;
- a prototype can cheaply expose usability problems before implementation.

They are not required merely because an interface exists.

When mockups are used, existing governance remains valid:

```text
GENERATED != REVIEWED != APPROVED
```

Generated assets must remain versioned if they become approved references.

## 14. Visual & Functional Review

Blueprint 0.5 should replace the static-mockup-centered review gate with a review of the actual functional client.

The review should validate, as applicable:

- Interface Inventory fidelity;
- Design System/tokens;
- requirements/use-case intent;
- permissions and action availability;
- API operation bindings;
- business/error states;
- no invented capabilities;
- no hardcoded authoritative business data;
- responsive behavior;
- accessibility behavior;
- interaction consistency;
- real forms and validation feedback;
- approved visual references/mockups when they exist;
- visual polish sufficient for the delivery stage.

Static visual review may occur earlier as a conditional sub-process, but it cannot replace review of the real implementation that will ship.

## 15. Integration QA by slice

Integration QA should support scoped evidence for Functional Interface Slices while the final Release Gate still evaluates project/release readiness.

Slice-level QA should cover as applicable:

- real API transport;
- auth/session behavior;
- RBAC and 401/403 handling;
- operation/error contract mapping;
- forms/422;
- conflicts/409;
- rate limiting/429;
- idempotency/replay for risk mutations;
- loading/empty/error transitions;
- responsive behavior;
- accessibility automation plus manual checks appropriate to risk;
- critical user journey tests;
- cross-interface navigation and shared-state behavior.

## 16. Machine-readable model impact

V5 requires coordinated changes across the master contract.

### Canonical documents

- `BLUEPRINT.md`
- `README.md` at release closure
- `documentation/BLUEPRINT_CURRENT_STATE.md` at release closure

### Catalogs/workflows

- `catalog/phases.yaml`
- `catalog/checks.yaml`
- `catalog/gates.yaml`
- `catalog/skills.yaml`
- `workflows/greenfield.yaml`
- `workflows/brownfield.yaml`

### Schemas

At minimum review/update:

- `schemas/interface-inventory.schema.json`
- `schemas/client-architecture.schema.json`
- `schemas/status.schema.json`
- `schemas/project.schema.json`
- `schemas/evidence.schema.json`
- `schemas/mockup-batch.schema.json`
- `schemas/design-system.schema.json`
- `schemas/design-tokens.schema.json`

Recommended new schema:

- `schemas/functional-interface-slice.schema.json`

Potential review artifact schema if the status/evidence model alone is insufficient:

- `schemas/visual-functional-review.schema.json`

### Templates

Update:

- `templates/interface-inventory.example.json`
- `templates/client-architecture.web.example.json`
- `templates/client-architecture.android.example.json`
- `templates/status.example.yaml`
- `templates/project.example.yaml`
- `templates/evidence.example.json`
- `templates/mockup-batch.example.json`

Recommended additions:

- `templates/functional-interface-slice.example.json`
- optional review template if a dedicated review schema is adopted.

### Validators/tests

Update:

- `scripts/validate-experience-artifacts.py`
- `scripts/validate-client-architecture.py`
- `scripts/validate-skills.py`
- `scripts/validate-release.py`
- corresponding CI workflows and fixtures.

Recommended addition:

- `scripts/validate-functional-interface-slices.py`

Validators should include both positive and negative cases for:

- mockups absent but Client Architecture valid;
- mockups present and governed correctly;
- inventory operation IDs resolving to slice API binding;
- invalid namespace/platform combinations;
- illegal `FUNCTIONAL` state with unresolved `BLOCKED_BY_API`;
- acceptance without required QA/review evidence;
- disabled API authority guardrails;
- hardcoded-business-data policy evidence requirements where machine-verifiable.

## 17. Skill impact

Update materialized skills:

- `dev-web-view-inventory`
- `dev-design-system`
- `dev-mockup-planning`
- `dev-accessibility`
- `dev-react-client-architecture`
- `dev-android-client-architecture`
- review `dev-contract-testing` for client operation/test traceability.

Recommended new materialized skill:

- `dev-functional-interface-slice`

Its procedure should cover:

1. select coherent slice from complete inventory;
2. verify dependencies and Client Architecture;
3. bind inventory actions/data to canonical operation IDs;
4. implement against real API;
5. implement auth/RBAC/errors/states;
6. enforce no invented capability/no hardcoded business data;
7. implement responsive/accessibility behavior;
8. add tests/evidence;
9. mark `FUNCTIONAL` only when DoD passes;
10. submit actual client to Visual & Functional Review and Integration QA.

Do not materialize additional skills solely to increase catalog counts.

## 18. Versioning strategy

Blueprint stable remains `0.4.0` during V5 development.

V5 implementation branches may use `0.5.0-dev` in branch-specific machine-readable documents where the existing versioning contract permits prerelease development, while `VERSION` continues to represent the last stable release until the release boundary.

Only the final release boundary should change:

```text
VERSION = 0.5.0
```

No consumer auto-upgrade is permitted.

Counts for phases, checks, gates and skills must be derived from the completed catalogs. V5 must not choose arbitrary target counts in advance merely to satisfy release validation.

## 19. Compatibility

Blueprint 0.5 should be a backward-aware minor evolution.

Required compatibility principles:

- existing 0.4 consumer evidence is not silently invalidated;
- consumers remain on their declared Blueprint version until Compliance Review and explicit adoption;
- Brownfield `ALIGN, DO NOT REWRITE` remains normative;
- existing approved mockups/references remain valid evidence when adopted by a consumer;
- mockups becoming conditional does not mean deleting historical visual assets;
- current client implementations remain authoritative observed behavior in Brownfield until approved cutover;
- API contracts remain authoritative;
- pilots remain non-normative.

## 20. Blueprint Control Center strategic debt

The Blueprint Control Center remains explicitly deferred.

Strategic sequence remains:

```text
Blueprint Core
  -> pilots CareShift / CUSA
  -> hardening
  -> Blueprint Control Center
```

V5 contracts should naturally expose metadata useful to that future dashboard, including:

- consumer/adopted version;
- phases/checks/gates;
- evidence;
- compliance/drift;
- interface/slice progress;
- `BLOCKED_BY_API` blockers;
- functional/visual/integration QA;
- release state.

However V5-0 and the 0.5.0 release must not implement a dashboard, UI service, database or control-plane runtime solely for this future capability.

## 21. CUSA pilot boundary

CUSA-Digital is the Greenfield evidence source that exposed this improvement.

It does not define hidden Blueprint rules.

During Blueprint 0.5 development:

- do not start CUSA Interface Inventory;
- do not create CUSA mockups;
- do not create CUSA React implementation;
- do not change CUSA API scope/operation IDs merely for the future UI;
- do not change CUSA Blueprint version automatically.

After Blueprint 0.5.0 release:

1. verify Blueprint and CUSA live again;
2. run CUSA Compliance Review `0.4.0 -> 0.5.0`;
3. explicitly adopt 0.5.0 if approved;
4. complete the R1 Interface Inventory;
5. convert it into the functional backlog;
6. group/order Functional Interface Slices;
7. implement them against the real API.

## 22. Audit decision

Blueprint 0.5.0 should evolve the post-API pipeline to:

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

with:

```text
Visual Identity       [CONDITIONAL when applicable]
Mockups / Prototypes  [CONDITIONAL/OPTIONAL risk-reduction capability]
```

The highest-value next implementation action is not CUSA frontend work.

The next action after V5-0 acceptance is to change the master canonical phase/check/gate/workflow model in a separate V5-1 branch, while preserving the stable 0.4.0 release and historical evidence.
