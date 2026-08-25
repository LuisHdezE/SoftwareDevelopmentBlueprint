# Blueprint v0.4.0 — CareShift Pilot Audit

> Status: DRAFT AUDIT  
> Source Blueprint: `0.3.0` on `main`  
> Pilot: `LuisHdezE/CareShift_Manager`  
> Audit mode: **YA EXISTE / DEBE AJUSTARSE / FALTA / NUEVO APRENDIZAJE DEL PILOTO**

## 1. Purpose

This audit compares Blueprint v0.3.0 with what was actually required to move the CareShift Brownfield pilot from repository inspection through API Gate, Interface Inventory, Visual Identity, Design System and the first mockup batch.

The goal is not to copy CareShift-specific decisions into the master Blueprint. The goal is to promote only reusable process knowledge proven useful by the pilot.

CareShift remains a reference pilot. The Blueprint remains product-independent.

## 2. Repository hygiene before v0.4 work

At audit start:

- `SoftwareDevelopmentBlueprint` has no open PRs.
- Historical branches `blueprint/core-v0.1`, `blueprint/core-v0.2-gates` and `blueprint/core-v0.3-api-stages` contain no commits exclusive from `main`; they are only behind it.
- `CareShift_Manager` has no open PRs.
- CareShift historical Blueprint branches inspected for Visual Identity, Interface Inventory, API QA, Postman, OpenAPI, API Implementation, Architecture, Requirements, Brownfield Analysis and initial adoption are absorbed by `main`.
- `CareShift_Manager/blueprint/mockups-batch-01` is intentionally **not merged** and contains the only confirmed current pilot work pending: 13 commits ahead / 0 behind at audit start.

Decision: preserve the CareShift mockup branch unchanged as pilot evidence while v0.4 work proceeds in the master Blueprint.

## 3. Executive findings

Blueprint v0.3 is strong from Brownfield inspection through API Gate. The CareShift pilot validated the overall API-first sequence and the machine-readable status/evidence approach.

The largest maturity gap is now **after API Gate**.

v0.3 names these phases:

`interface_inventory → visual_identity → mockups → web_implementation / android_implementation`

but it does not yet define them with the same rigor used for the API pipeline.

CareShift demonstrated that frontend delivery needs its own explicit contracts, checks, evidence and gates.

Second major gap: many skills are declared in `catalog/skills.yaml`, but the `skills/` directory currently contains only `README.md`. A future AI cannot reliably execute a named skill that has no versioned implementation.

Third major gap: `documentation/BLUEPRINT_CURRENT_STATE.md` is a derived checkpoint and has become stale relative to the pilot. The authority hierarchy is correct, but the process needs a reproducible way to refresh derived summaries from canonical project evidence.

## 4. Audit matrix

| Area | Classification | v0.3 state | Pilot learning / required v0.4 action |
|---|---|---|---|
| Greenfield/Brownfield modes | YA EXISTE | Explicit modes and workflows | Preserve. |
| ALIGN, DO NOT REWRITE | YA EXISTE | Brownfield rules are explicit | Preserve and make it a reusable Brownfield skill. |
| Observed / inferred / proposed | YA EXISTE | Workflow rule exists | Preserve. |
| Requirements gate | YA EXISTE | Strong catalog checks/gate | Preserve. |
| Architecture/Security/Data gate | YA EXISTE | Strong catalog checks/gate | Preserve. |
| API Contract Ready | YA EXISTE | Scope, endpoints, auth, RBAC, events, idempotency, traceability | Preserve. |
| API implementation slicing | DEBE AJUSTARSE | API implementation phase exists | Add canonical incremental-slice guidance, cumulative CI and one-active-PR boundary as proven operational practice. |
| OpenAPI formal contract | YA EXISTE | Explicit phase and gate | Preserve. |
| OpenAPI/Laravel/inventory parity | NUEVO APRENDIZAJE | Generic validation only | Promote deterministic route/inventory/OpenAPI parity checks as recommended generated evidence where applicable. |
| Postman operational contract | YA EXISTE | Explicit phase and gate | Preserve. |
| Deterministic Postman generation | NUEVO APRENDIZAJE | Not standardized | Define generated-from-OpenAPI strategy as preferred when feasible; require drift detection. |
| API runtime QA | YA EXISTE | Positive/negative/security/audit checks | Preserve. |
| Real HTTP + authoritative DB QA | NUEVO APRENDIZAJE | Evidence requirement is generic | Require runtime QA against real HTTP transport and authoritative DB when feasible; feature tests alone cannot close runtime QA. |
| CI pipe failure hygiene | NUEVO APRENDIZAJE | Not explicit | Require pipelines to propagate command exit codes (`pipefail` or equivalent) when output is piped/tee'd. |
| API Gate | YA EXISTE | Strong gate | Preserve. |
| Interface Inventory | DEBE AJUSTARSE | Phase/check exists | Define canonical schema/template: numbered IDs, route/surface, purpose, roles, data, actions, states, navigation, API responsibilities and observed gaps. |
| Web-only behavior | NUEVO APRENDIZAJE | Not explicit | Allow inventory entries with no API mapping; prohibit inventing API solely because a screen exists. |
| Brownfield UI gap recording | NUEVO APRENDIZAJE | Not explicit | Require observed UI gaps to be documented without silently fixing them during inventory. |
| Visual Identity | DEBE AJUSTARSE | Phase exists, shallow checks | Split identity direction from Design System contract; define required tokens and accessibility target. |
| Design System | DEBE AJUSTARSE | Single evidence check | Formalize tokens, shell, typography, components, domain semantics, interaction states, RBAC presentation and responsive behavior. |
| Design-system automated validation | NUEVO APRENDIZAJE | Not defined | Add machine validation for token references, contrast, breakpoints, touch target and required states. |
| Mockup batches | DEBE AJUSTARSE | Inventory prerequisite + max 10 | Add manifest/spec/prompt/assets/evidence contract and per-view traceability. |
| Versioned visual assets | NUEVO APRENDIZAJE | Not defined | Approved mockup images must be stored in the consumer repository and referenced by documentation so future AI runs can reuse them. |
| Visual references as AI context | NUEVO APRENDIZAJE | Not defined | Before generating/implementing a view, AI must inspect approved visual assets and avoid creating a new visual language without documented reason. |
| Mockup state model | FALTA | No machine model | Add statuses for specification, visuals, manual review and batch pass. |
| Mockup review gate | FALTA | No dedicated gate | Add a visual-review/mockup-ready gate before implementation of corresponding client slice. |
| Partial mockup approval | FALTA | Web implementation only globally blocked | Allow implementation by approved UI slice without requiring every product mockup to be complete, while preventing unapproved screens from implementation. |
| Accessibility design | DEBE AJUSTARSE | Skill/check named but weak | Make WCAG target and evidence explicit; require keyboard/focus, non-color semantics, reduced motion and touch targets. |
| Permission-aware UI | NUEVO APRENDIZAJE | API RBAC exists but UI rule is implicit | UI may hide/disable actions using permission context, but API remains security boundary and 403 must be handled. |
| Standard async/error states | FALTA | No canonical client-state contract | Define loading, empty, filtered-empty, 401, 403, 404, 409, 422, 429, generic Problem Details and offline/network states. |
| High-risk UI mutation semantics | NUEVO APRENDIZAJE | API idempotency exists | UI must not display success before server confirmation; retries/idempotency and destructive confirmations must align with API contract. |
| Frontend architecture phase | FALTA | Implementation follows mockups directly | Add explicit Frontend Architecture / Client Contract phase between visual approval and implementation. |
| React implementation | DEBE AJUSTARSE | Phase name exists | Require API client, auth lifecycle, routing, permissions, state management, error handling, observability and test strategy before screen implementation. |
| Android implementation | DEBE AJUSTARSE | Phase name exists | Mirror client contract rules where Android capability applies. |
| Existing clients during Brownfield modernization | NUEVO APRENDIZAJE | General preserve behavior rule exists | Current client may remain active while a new client is built. Do not replace it until integration/release gates pass. |
| Runtime UI tests | FALTA | Integration QA generic | Define component/unit, accessibility, contract/client, E2E and critical workflow expectations. |
| Skills catalog | DEBE AJUSTARSE | Catalog exists | Synchronize catalog version policy and actual skill files. |
| Skills implementation | FALTA | Only `skills/README.md` is versioned | Materialize critical reusable skills, starting with Brownfield analysis, API contract, API QA, UI inventory, design system, mockups, accessibility and Git workflow. |
| Reference pilot model | DEBE AJUSTARSE | CareShift named in BLUEPRINT.md/workflow | Formalize reference pilots without making pilot repositories normative dependencies. |
| Derived Current State | DEBE AJUSTARSE | Human checkpoint exists | Mark freshness metadata and create refresh/check procedure to detect stale pilot status. |
| Evidence schema | DEBE AJUSTARSE | Flexible evidence entries | Add visual asset/mockup batch evidence types or a generic artifact model with media metadata. |
| Status schema | DEBE AJUSTARSE | Flexible phase/check/gate state | Add optional structured `batches`/`artifacts`/`approvals` or a generic extensions contract for UI batches. |
| Branch/PR hygiene | NUEVO APRENDIZAJE | Git skill named, not implemented | Default to one active implementation PR per review boundary; verify branch ahead/behind and merged content before starting next phase. |

## 5. Frontend & Experience Delivery Pipeline proposal

v0.4 should replace the loose post-API sequence with an explicit delivery chain:

```text
API_GATE = PASS
      ↓
Interface Inventory
      ↓
Visual Identity
      ↓
Design System
      ↓
Mockup Planning
      ↓
Mockup Batch(es)
      ↓
Visual Review Gate
      ↓
Frontend / Client Architecture
      ↓
Web and/or Android Implementation Slices
      ↓
Client Integration QA
      ↓
Release Gate
```

Every phase must declare:

- input conditions;
- required artifacts;
- checks;
- evidence;
- exit criteria;
- downstream blocks;
- Greenfield/Brownfield differences;
- AI execution instructions.

## 6. Proposed consumer repository structure

The exact root remains `.blueprint/`; v0.4 should standardize a scalable UI subtree such as:

```text
.blueprint/
  ui/
    inventory/
      INTERFACE_INVENTORY.md
    identity/
      VISUAL_IDENTITY.md
      DESIGN_SYSTEM.md
      DESIGN_TOKENS.json
    mockups/
      batch-01/
        manifest.json
        specification.md
        prompts.md
        assets/
          WEB-001-login.png
          WEB-004-dashboard.png
        evidence.md
```

Migration from existing v0.3 pilot paths must be non-destructive. A v0.4 project adoption/compliance step may either migrate paths or declare compatibility aliases.

## 7. Mockup contract proposal

Each batch must be machine-readable and include:

```yaml
batch_id: BATCH-01
status: IN_PROGRESS
max_views: 10
views:
  - mockup_id: M01-01
    inventory_id: WEB-001
    title: Login
    platform: web
    api_responsibilities: [API-AUTH-001, API-AUTH-004]
    visual_asset: assets/WEB-001-login.png
    review_status: APPROVED
completion:
  specification: PASS
  visuals: IN_PROGRESS
  manual_review: IN_PROGRESS
  batch_pass: PENDING
```

Rules:

1. no more than 10 related views per generation batch;
2. every view references an existing inventory ID;
3. every API responsibility references an approved contract ID when applicable;
4. web-only behavior may explicitly declare no API mapping;
5. visual assets are stored/versioned in the project repository;
6. approved assets are AI reference inputs for later screens;
7. approval must be explicit, not inferred from image existence;
8. implementation may start only for slices covered by approved mockups and the required client-architecture gate.

## 8. Design System contract proposal

Minimum artifacts:

- `VISUAL_IDENTITY.md`
- `DESIGN_SYSTEM.md`
- `DESIGN_TOKENS.json`

Minimum machine checks where applicable:

- token JSON parses;
- semantic aliases resolve;
- primary identity anchors exist;
- responsive breakpoints are coherent;
- minimum touch target is at least 44 px;
- critical foreground/background pairs meet configured WCAG target;
- required UI states are documented;
- domain status mappings use declared semantic tokens;
- no state relies on color alone by contract.

## 9. Client architecture contract proposal

Before React/Kotlin implementation begins for an approved slice, document at minimum:

- API base/version strategy;
- auth/token lifecycle or session strategy;
- generated/manual API client decision;
- permission context and 403 behavior;
- routing/navigation structure;
- state/data fetching strategy;
- loading/empty/error/offline model;
- forms/validation mapping to API errors;
- high-risk/idempotent mutation handling;
- observability/request correlation;
- accessibility strategy;
- testing pyramid and critical E2E journeys;
- coexistence/migration plan for Brownfield client when applicable.

## 10. Reference pilot contract

CareShift should be registered as:

```yaml
id: careshift-brownfield-01
repository: LuisHdezE/CareShift_Manager
mode: brownfield
role: reference_pilot
blueprint_baseline: 0.3.0
purpose: validate Brownfield pipeline and machine-readable evidence
normative: false
```

A reference pilot may provide examples and evidence patterns but must never become a hidden dependency of the Blueprint specification.

## 11. Skills required for v0.4 foundation

Priority reusable skills to materialize as real versioned files:

1. `dev-git-workflow`
2. `dev-brownfield-analysis`
3. `dev-api-design`
4. `dev-openapi`
5. `dev-postman-qa`
6. `dev-contract-testing`
7. `dev-web-view-inventory`
8. `dev-design-system`
9. `dev-mockup-planning`
10. `dev-accessibility`
11. `dev-react-client-architecture`
12. `dev-event-logging-audit`

The catalog must reference paths that actually exist.

## 12. v0.4 implementation slices

To keep review boundaries small, v0.4 should be implemented in separate slices/PRs:

### V4-0 — Audit & specification freeze

- this audit;
- v0.4 roadmap;
- confirm compatibility strategy;
- no normative change to `main` until reviewed.

### V4-1 — Post-API phase/gate model

- phases/checks/gates/workflows;
- Interface Inventory Ready;
- Design System Ready;
- Mockup Batch Ready / Visual Review Gate;
- Client Architecture Ready.

### V4-2 — Schemas & templates

- interface inventory template/schema;
- design-token requirements/template;
- mockup batch schema/template;
- status/evidence extensions;
- reference-pilot catalog/schema.

### V4-3 — Core UI/AI skills

- implement the critical view-inventory/design-system/mockup/accessibility skills;
- ensure catalog paths resolve.

### V4-4 — Client architecture & implementation contract

- React/Kotlin client architecture guidance;
- Brownfield coexistence/migration rules;
- client QA expectations.

### V4-5 — Pilot compliance review

- evaluate CareShift v0.3 artifacts against v0.4;
- adopt only justified changes;
- do not rewrite working pilot artifacts solely to match new paths.

## 13. Compatibility principles

Blueprint 0.4 must remain backward-aware:

- v0.3 consumer projects do not auto-upgrade;
- existing `.blueprint/` evidence remains valid unless a v0.4 Compliance Review says otherwise;
- path changes require migration/alias strategy;
- CareShift must not be rewritten simply to demonstrate v0.4 aesthetics;
- a partial pilot batch may remain intentionally incomplete while the master process evolves.

## 14. Immediate decision

The highest-value next action is **not** completing the remaining six CareShift mockup images.

The highest-value next action is implementing V4-1 and V4-2 in the master Blueprint, then using the preserved CareShift `mockups-batch-01` branch to validate those new contracts.

That keeps the pilot in its correct role:

> CareShift demonstrates and tests the process. The Blueprint defines the process.
