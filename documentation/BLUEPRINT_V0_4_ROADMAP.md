# Blueprint v0.4.0 — Implementation Roadmap

> Baseline: Blueprint `0.3.0`  
> Source audit: `documentation/BLUEPRINT_V0_4_PILOT_AUDIT.md`  
> Reference pilot: `LuisHdezE/CareShift_Manager`  
> Delivery rule: one active implementation PR per review boundary.

## Objective

Blueprint 0.4.0 will make the post-API client-delivery pipeline as explicit, machine-readable and evidence-driven as the API pipeline validated by CareShift.

The release is complete when another AI can consume the Blueprint and a project repository and determine, without relying on chat history:

- what phase the project is in;
- what is blocked and why;
- which artifacts must exist;
- which checks and gates must pass;
- which visual references are approved;
- which interfaces may be implemented;
- which reusable skills to load;
- what evidence proves completion.

## Delivery slices

### V4-0 — Audit & roadmap

**Scope**

- Pilot audit against v0.3.
- Repository/branch hygiene verification.
- v0.4 roadmap.
- Preserve CareShift mockup branch as pending pilot evidence.

**Exit criteria**

- Audit classifies findings as `YA EXISTE`, `DEBE AJUSTARSE`, `FALTA`, or `NUEVO APRENDIZAJE DEL PILOTO`.
- No normative v0.3 catalog/workflow/schema behavior changed.
- PR reviewed and merged before V4-1 begins.

### V4-1 — Frontend & Experience phase/gate model

**Scope**

Update canonical:

- `BLUEPRINT.md`
- `catalog/phases.yaml`
- `catalog/checks.yaml`
- `catalog/gates.yaml`
- `workflows/greenfield.yaml`
- `workflows/brownfield.yaml`

**Target phase chain**

```text
API_GATE
  → interface_inventory
  → visual_identity
  → design_system
  → mockup_planning
  → mockups
  → visual_review_gate
  → client_architecture
  → web_implementation / android_implementation
  → integration_qa
```

**Target gates**

- `interface_inventory_ready`
- `design_system_ready`
- `mockups_ready` or `visual_review_pass`
- `client_architecture_ready`

Implementation must support slice-level visual approval so approved screens can progress without waiting for every screen in the product.

**Exit criteria**

- Every post-API phase has explicit prerequisites and downstream blocks.
- Greenfield and Brownfield workflows are consistent.
- Web/Android implementation cannot begin for an unapproved interface slice.

### V4-2 — Schemas, templates & evidence model

**Scope**

Add/update:

- interface inventory schema/template;
- design-system/token schema or validation contract;
- mockup batch schema/template;
- evidence/artifact metadata;
- status schema extensions;
- reference pilot registry/schema;
- consumer project examples.

**Required mockup fields**

- batch ID;
- mockup ID;
- inventory ID;
- platform;
- API responsibilities when applicable;
- visual asset path;
- review status;
- batch completion status.

**Exit criteria**

- A validator can determine whether a batch exceeds 10 views.
- A validator can verify that every mockup references an inventory item.
- Image existence alone does not imply approval.
- Visual asset paths are machine-readable.

### V4-3 — Executable reusable skills

**Scope**

Materialize priority skills declared in the catalog.

Initial mandatory set:

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
- `dev-event-logging-audit`

**Exit criteria**

- Catalog entries resolve to real versioned files.
- Each skill declares when to use it, inputs, procedure, outputs, stop conditions and canonical references.
- Skills do not copy product-specific CareShift knowledge.

### V4-4 — Client Architecture & Implementation contract

**Scope**

Formalize web and Android pre-implementation decisions:

- auth lifecycle;
- API client strategy;
- permissions;
- routing;
- data fetching/state;
- forms/API validation;
- standard async/error/offline states;
- idempotent/high-risk mutations;
- observability/request correlation;
- accessibility;
- unit/component/E2E testing;
- Brownfield coexistence/migration.

**Exit criteria**

- React/Kotlin implementation phases receive a complete client contract.
- API remains authorization boundary.
- Existing Brownfield client can coexist until release migration is approved.

### V4-5 — Reference pilot compliance review

**Scope**

Run CareShift against Blueprint v0.4 without automatic migration.

**Rules**

- `ALIGN, DO NOT REWRITE` remains active.
- Existing v0.3 evidence is grandfathered unless v0.4 introduces a critical missing safety requirement.
- The pending `blueprint/mockups-batch-01` branch is used to test the new mockup schema and visual-reference rules.
- Path migration is optional unless approved by compliance review.

**Exit criteria**

- Compliance report states `KEEP`, `ADOPT`, `MIGRATE`, `DEFER`, or `N/A` per v0.4 change.
- No working CareShift functionality is rewritten merely to make the pilot look like a fresh v0.4 project.

## Cross-cutting v0.4 rules

1. **AI continuity must live in the repository.** Important decisions, prompts, manifests, evidence and approved visual assets cannot exist only in chat history.
2. **Approved visual assets are reference inputs.** Later AI agents inspect them before generating or implementing related views.
3. **No visual approval by implication.** Generated image ≠ reviewed image ≠ approved mockup.
4. **Runtime evidence beats optimistic CI labels.** Pipelines must propagate exit codes and distinguish feature/unit tests from real transport/integration verification.
5. **API contracts remain authoritative.** UI cannot invent endpoints, permissions, states or mutations because they are visually convenient.
6. **One active implementation PR per boundary.** Avoid stacked review chains unless explicitly justified.
7. **Reference pilots are non-normative.** They prove or challenge the Blueprint but do not define hidden product-specific rules.

## Versioning strategy

`0.4.0` is a minor Blueprint release because it extends the process and machine-readable contract without intentionally invalidating v0.3 consumer evidence.

Consumer projects remain on their declared Blueprint version until a Compliance Review approves adoption.

## Immediate next action

Merge V4-0 audit/roadmap first. Then create a fresh branch from updated `main` for V4-1. Do not stack V4-1 onto the audit branch.
