# Blueprint v0.5.0 - Functional Client Delivery Roadmap

> Stable baseline: Blueprint `0.4.0`  
> Initial stable baseline commit: `b8092a1a6da6d0e765ccd6f5ff93d5147a712e0d`  
> V5-1 merged baseline: `cceb7f1fc4d2414448425f44e9a56687472d66b3`  
> Source audit: `documentation/BLUEPRINT_V0_5_POST_API_AUDIT.md`  
> External audit disposition: `documentation/BLUEPRINT_V0_5_EXTERNAL_AUDIT_RESPONSE.md`  
> Greenfield evidence source: `LuisHdezE/CUSA-Digital`  
> Delivery rule: one active implementation PR per review boundary.  
> Consumer rule: no automatic Blueprint adoption.

## 1. Objective

Blueprint 0.5.0 evolves the client-delivery model from a mockup-centered sequence into a traceable system where another AI can reconstruct, without chat history:

- early interface scope;
- executable Interface Inventory;
- requirements and permissions;
- canonical OpenAPI `operationId` bindings;
- Functional Interface Slices;
- Client Architecture;
- functional Definition of Done;
- `BLOCKED_BY_API` blockers;
- impact of later API contract changes;
- Visual & Functional Review;
- Integration QA;
- human acceptance;
- evidence proving every relevant state/gate.

## 2. Corrected target model after V5-1A

### Pre-API planning chain

```text
Requirements Ready
  -> Interface Scope Baseline Ready
  -> Architecture Ready
  -> API Contract Ready
  -> API Implementation / OpenAPI / Postman / API QA
  -> API Gate
```

`Interface Scope Baseline` is descriptive/planning scope only. It may contain unresolved API needs and never authorizes client implementation.

### Executable client chain

```text
API Gate
  -> Interface Inventory Ready
  -> Design System Ready
  -> Client Architecture Ready
  -> Functional Slice Ready
  -> Visual & Functional Review Pass
  -> Integration QA Pass
  -> Release Gate
```

Conditional capabilities:

```text
Visual Identity       -> feeds Design System when applicable
Mockups / Prototypes  -> optional risk-reduction branch
```

### Functional slice lifecycle

```text
INVENTORIED
  -> READY
  -> IN_PROGRESS
  -> FUNCTIONAL
  -> ACCEPTED
```

Quality gates are not duplicated as lifecycle states.

`ACCEPTED` requires the applicable scoped review/QA gates and explicit human acceptance.

### API blocker model

`BLOCKED_BY_API` is an overlay condition, not a lifecycle state.

```text
lifecycle: IN_PROGRESS
blocker: BLOCKED_BY_API
```

Resolution preserves the last valid lifecycle state and requires evidence before resume.

### API evolution after the initial baseline

The initial `api_gate` remains project-scoped. Later API changes use **impact-based revalidation**:

- canonical key: OpenAPI `operationId`;
- local operation changes revalidate affected consumers only;
- unrelated accepted slices retain evidence by default;
- auth/authorization/security/error-contract/versioning or other cross-cutting changes may escalate scope;
- affected consumers cannot silently remain accepted without required revalidation.

## 3. Core v0.5 invariants

1. Interface scope may be described before API implementation, but executable client delivery does not begin before `API_GATE = PASS`.
2. Brownfield observed interfaces must be recorded before proposed replacement behavior.
3. Interface Inventory Ready reconciles early scope with the authoritative API contract.
4. Design System precedes functional implementation.
5. Client Architecture precedes implementation for the exact slice + platform.
6. API remains the authoritative authorization and business boundary.
7. Client code does not invent endpoints, permissions, business states or transitions.
8. Missing authoritative server capability produces `BLOCKED_BY_API`, not fabricated frontend behavior.
9. Hardcoded authoritative business data disqualifies `FUNCTIONAL`.
10. `GENERATED != REVIEWED != APPROVED` remains true for generated visual references.
11. Static mockups are conditional and cannot replace review of the real client.
12. Functional, responsive, accessibility and integration evidence are slice-aware.
13. Web approval never authorizes Android and vice versa.
14. API changes after the baseline require downstream impact analysis.
15. `ACCEPTED` requires quality gates plus explicit human acceptance.
16. Consumer Blueprint versions never change automatically.
17. Pilots prove/challenge the process but are not hidden normative dependencies.
18. Cross-artifact traceability must become semantically verifiable, not merely syntactically valid.
19. One active implementation PR per review boundary unless explicitly justified.

## 4. Delivery boundaries

### V5-0 - Post-API Audit & Roadmap

**Status:** MERGED.

Defined the problem, CUSA evidence, mockup dependency, Functional Interface Slice direction, no-hardcoded-authoritative-business-data rule, conditional mockups and release strategy without changing canonical behavior.

### V5-1 - Canonical Functional Delivery Model

**Status:** MERGED at baseline `cceb7f1fc4d2414448425f44e9a56687472d66b3`.

Changed canonical phases/checks/gates/workflows to:

- remove mockups from mandatory main sequence;
- introduce Functional Interface Slice;
- introduce Visual & Functional Review on the real client;
- make QA slice/platform-aware;
- preserve API authority;
- establish development validation while `VERSION` remains `0.4.0`.

### V5-1A - External Audit Model Hardening

**Goal**

Correct conceptual ownership before schemas freeze the model.

**Primary files**

- `BLUEPRINT.md`
- `catalog/phases.yaml`
- `catalog/checks.yaml`
- `catalog/gates.yaml`
- `workflows/greenfield.yaml`
- `workflows/brownfield.yaml`
- `scripts/validate-release.py`
- `documentation/BLUEPRINT_V0_5_EXTERNAL_AUDIT_RESPONSE.md`
- this roadmap.

**Required outcomes**

- add pre-API `interface_scope_baseline` + `interface_scope_ready`;
- keep executable `interface_inventory` after `api_gate`;
- keep initial API Gate project-scoped;
- add post-baseline API impact analysis and affected-consumer revalidation;
- simplify slice lifecycle to `INVENTORIED -> READY -> IN_PROGRESS -> FUNCTIONAL -> ACCEPTED`;
- keep Visual & Functional Review / Integration QA as quality gates;
- model `BLOCKED_BY_API` as overlay preserving lifecycle state;
- establish Platform Client Architecture Baseline + Slice Binding as V5-3 design direction;
- promote Cross-Artifact Semantic Integrity to a V5 release requirement;
- keep schemas/templates/skills untouched until their dedicated boundaries;
- keep CUSA untouched.

**Exit criteria**

- canonical docs/catalogs/workflows agree;
- development validator asserts the corrected model;
- stable `VERSION` remains `0.4.0`;
- no schema/template/skill migration is smuggled into the boundary;
- CI passes on final branch head;
- PR receives explicit human review before merge.

---

### V5-2 - Machine-Readable Artifact Graph

**Goal**

Encode the corrected V5-1A ownership model into schemas, templates, status and evidence.

**Primary schemas to update**

- `schemas/interface-inventory.schema.json`
- `schemas/status.schema.json`
- `schemas/project.schema.json`
- `schemas/evidence.schema.json`
- `schemas/mockup-batch.schema.json` only where compatibility/optional-path semantics require it
- review Design System/token schemas for cross-reference needs.

**New schema**

- `schemas/functional-interface-slice.schema.json`

A separate visual-review schema should exist only if it avoids, rather than creates, semantic duplication.

#### Interface maturity representation

V5-2 must choose one coherent machine-readable strategy:

A. one interface artifact/schema with explicit maturity such as baseline/executable; or
B. related early-scope and executable-inventory contracts.

Acceptance criteria:

- Brownfield observed interfaces are representable before API Gate;
- Greenfield intended scope is representable from requirements;
- unresolved API needs are legal at baseline maturity;
- executable inventory requires authoritative binding or explicit local/static declaration;
- IDs remain stable across maturity progression;
- no duplicate owner of the same semantic field.

#### Functional Interface Slice schema

Must cover at minimum:

- stable slice ID/name;
- platform;
- inventory IDs;
- dependencies;
- effective Client Architecture reference;
- required operationIds;
- lifecycle: `INVENTORIED | READY | IN_PROGRESS | FUNCTIONAL | ACCEPTED`;
- blocker overlay, including `BLOCKED_BY_API`;
- last/preserved lifecycle state when blocked;
- functional DoD evidence;
- Visual & Functional Review gate/evidence;
- Integration QA gate/evidence;
- human acceptance;
- evidence IDs.

#### BLOCKED_BY_API

Must capture:

- blocker ID;
- affected slice/interface/platform;
- preserved lifecycle state;
- missing capability category;
- missing data/operation/permission/state/transition;
- authoritative contract reference;
- evidence;
- opened/resolved timestamps;
- resolution reference;
- downstream impact/revalidation requirement when API changes.

#### API impact graph

Machine-readable artifacts must support:

- post-baseline change ID;
- changed operationIds or cross-cutting category;
- affected interfaces/slices/platforms;
- impact scope;
- revalidation evidence;
- explicit resolution before affected acceptance is restored/retained.

#### Status schema ownership

`status.yaml` must avoid duplicating lifecycle and scoped gates as two competing owners.

Preferred rule:

- slice artifact owns lifecycle/blocker state;
- scoped gates own review/QA outcomes;
- project status indexes/aggregates them for human/Control Center visibility.

#### Evidence model

Evidence must become harder to fake accidentally.

The existence of an empty file/path is not enough when a check claims runtime behavior.

#### Schema provenance

Review `$id` and local/version-pinned resolution so schema provenance cannot be confused with consumer auto-upgrade.

#### Cross-Artifact Semantic Integrity

V5-2 should introduce or start a dedicated semantic validator that can resolve at least:

```text
requirement
  -> interface
  -> permission
  -> operationId
  -> functional slice
  -> evidence/test
```

V5-3 extends the graph through Client Architecture.

**Positive fixtures**

- Brownfield observed scope before API binding;
- Greenfield scope baseline;
- executable inventory after API Gate;
- slice with no mockups;
- slice with approved optional visual references;
- slice blocked by API while preserving lifecycle;
- accepted slice with required gates/evidence;
- post-baseline API change with impacted-slice revalidation.

**Negative fixtures**

- unknown requirement/interface/permission/operationId reference;
- platform namespace mismatch;
- executable inventory claiming nonexistent operationId;
- blocker represented as lifecycle state;
- blocked slice silently advanced;
- accepted slice without review/QA/human acceptance;
- API change with affected consumer but no revalidation evidence;
- mockup generation treated as approval;
- fake/empty evidence accepted for behavior that requires runtime proof.

**Exit criteria**

- schemas/examples validate;
- Functional Interface Slice is machine-readable;
- lifecycle/gates/blockers have one owner each;
- API impact can be represented;
- semantic negative fixtures are rejected;
- mockups may be absent from normal functional delivery;
- no CUSA mutation.

---

### V5-3 - Client Architecture Composition & Referential Integrity

**Goal**

Align Client Architecture with the corrected V5 model and reduce repetition without weakening scoped governance.

**Target architecture model**

```text
Platform Client Architecture Baseline
  + Slice Architecture Binding / Overrides
  = Effective Client Architecture Contract
```

The exact physical schema may use composition or references, but `client_architecture_ready` remains evaluated for each slice + platform.

**Must preserve**

- Design System/tokens;
- OpenAPI/operationIds;
- auth/session;
- API client;
- permissions;
- routing;
- state/cache/invalidation;
- forms/errors;
- async/offline;
- idempotency;
- observability/correlation;
- accessibility;
- testing;
- platform specifics;
- Brownfield coexistence/cutover/rollback.

**Visual binding change**

- approved visual references are optional/conditional;
- zero mockups is valid;
- when references exist, only approved/versioned references may be authoritative.

**Semantic validation**

Validator must cross-check:

- inventory IDs exist;
- slice owns the inventory IDs;
- operationIds exist in OpenAPI;
- operationIds belong to the slice binding;
- platform namespaces are compatible;
- architecture references valid platform baseline;
- API-authority guardrails cannot be disabled.

**Exit criteria**

- no-mockup web/Android architecture validates;
- shared platform decisions are declared once where appropriate;
- slice-specific behavior remains explicit;
- cross-artifact semantic negative tests pass.

---

### V5-4 - Executable Functional Slice Skills & QA Guidance

**Goal**

Give AI agents executable procedures based on the machine-readable graph.

**Update materialized skills**

- `dev-web-view-inventory`
- `dev-design-system`
- `dev-mockup-planning`
- `dev-accessibility`
- `dev-react-client-architecture`
- `dev-android-client-architecture`
- `dev-contract-testing` as needed.

**Materialize**

- `dev-functional-interface-slice`

**Required flow**

```text
select accepted executable inventory slice
  -> resolve dependencies
  -> validate effective Client Architecture
  -> verify permissions + operationIds
  -> implement real routing/components
  -> integrate real API
  -> auth/RBAC/forms/errors/states
  -> idempotency/correlation
  -> responsive/accessibility
  -> tests
  -> prove no hardcoded authoritative business data
  -> FUNCTIONAL
  -> Visual & Functional Review
  -> Integration QA
  -> human acceptance
  -> ACCEPTED
```

If an authoritative contract gap appears, activate `BLOCKED_BY_API`, preserve lifecycle, resolve API in a separate boundary and perform impact-based revalidation before resume.

**Exit criteria**

- skill validator passes;
- Functional Slice skill is real and product-independent;
- mockup skill is explicitly conditional;
- architecture skills use the effective architecture contract;
- no CUSA-specific behavior leaks into reusable skills.

---

### V5-5 - Integration Validation, Documentation & Stable 0.5.0 Release

**Goal**

Close the release only when the complete canonical surface is coherent.

**Validation**

Run/update as applicable:

- `validate-experience-artifacts.py`
- semantic/cross-artifact validator introduced in V5-2;
- `validate-client-architecture.py`
- `validate-functional-interface-slices.py` if separated;
- `validate-skills.py`
- historical reference-pilot validator;
- `validate-release.py`;
- all Blueprint CI workflows.

**Human/current documentation**

Update:

- `README.md`
- `documentation/BLUEPRINT_CURRENT_STATE.md`
- `documentation/EXPERIENCE_ARTIFACT_MODEL.md`
- `documentation/CLIENT_ARCHITECTURE_CONTRACT.md`
- relevant skill/functional-slice documentation.

Create:

- `documentation/BLUEPRINT_V0_5_RELEASE_NOTES.md`
- `documentation/BLUEPRINT_V0_5_RELEASE.json`

Historical 0.4 release artifacts remain historical truth.

**Stable version closure**

Only after final accepted validation:

```text
VERSION: 0.4.0 -> 0.5.0
```

Release validator must freeze actual completed counts rather than reuse v0.4 constants.

**Release exit criteria**

- catalogs/workflows/schemas/templates/skills/docs agree;
- Interface Scope Baseline and executable Inventory are coherent;
- lifecycle/gates/blocker ownership is coherent;
- API impact semantics are machine-readable;
- Cross-Artifact Semantic Integrity negative fixtures pass;
- Client Architecture supports zero mockups and deduplicated platform baseline;
- Functional Slice positive/negative fixtures pass;
- README and Current State describe stable 0.5 accurately;
- `VERSION = 0.5.0` only in the release boundary;
- merged `main` itself passes final validation;
- release/tag points to the accepted tree;
- no consumer auto-upgrade.

## 5. CUSA adoption sequence after stable 0.5.0

CUSA remains untouched during V5 Master construction.

After release:

1. verify Blueprint `main`, `VERSION`, release/tag and open PRs;
2. verify CUSA `main`, `.blueprint/status.yaml` and open PRs;
3. run Compliance Review `0.4.0 -> 0.5.0`;
4. classify KEEP / ADOPT / MIGRATE / DEFER / N/A;
5. change CUSA Blueprint version only after explicit approval;
6. reconstruct/adopt Interface Scope Baseline as required by compliance;
7. produce Interface Inventory Ready as executable R1 backlog;
8. group/order real Functional Interface Slices;
9. implement one boundary at a time against the real API;
10. use `BLOCKED_BY_API` overlay for real contract gaps;
11. perform impact-based revalidation for any API correction;
12. review real functional UI;
13. Integration QA + human acceptance;
14. proceed toward release only through accepted evidence.

## 6. Deferred broader debt

### Applicability / tailoring profiles

External audit identified that database/migration/audit requirements are too universal for some stateless/static/integration-only projects.

This is accepted architectural debt. It should be solved with explicit project capabilities/applicability rules, not fake evidence. It is intentionally kept outside the core V5 functional-client boundary unless a release-blocking contradiction appears.

### Blueprint Control Center

Remains strategic debt.

```text
Blueprint Core
  -> CareShift/CUSA pilots
  -> hardening
  -> Blueprint Control Center
  -> future 1.0 readiness
```

V5 exposes metadata useful to the future Control Center but does not build a dashboard/control-plane service.

## 7. Branch / PR discipline

Completed/current direction:

```text
V5-0   blueprint/v0.5-audit-functional-slices
V5-1   blueprint/v0.5-functional-delivery-model
V5-1A  blueprint/v0.5-external-audit-hardening
V5-2   blueprint/v0.5-functional-artifacts
V5-3   blueprint/v0.5-client-architecture
V5-4   blueprint/v0.5-functional-slice-skills
V5-5   blueprint/release-v0.5.0
```

Rules:

- next boundary starts only from merged/reverified `main`;
- do not stack work on unmerged branches;
- do not auto-merge;
- verify diff and CI before human acceptance;
- merge only the accepted boundary;
- verify new `main` after each merge;
- do not update consumers as a side effect of Master release.

## 8. Immediate next action

Current boundary is V5-1A.

```text
finish V5-1A
  -> validate final branch head
  -> open PR
  -> human review
  -> merge only if explicitly approved
  -> verify main
  -> start V5-2 Machine-Readable Artifact Graph from that exact main
```

Do not start V5-2 before V5-1A acceptance.
