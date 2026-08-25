# Experience Artifact Model — Blueprint 0.4.0-dev

## Purpose

This document defines the repository-owned artifact model introduced by V4-2 and extended by V4-4. The goal is AI continuity: another agent must be able to inspect the project repository and determine what interfaces exist, which visuals are approved, which client architecture applies, which evidence supports a gate, and which slices are allowed to progress.

## Canonical artifact families

A consumer project may choose different paths, but should declare them in `project.yaml` through `artifact_locations`.

Recommended layout:

```text
.blueprint/
  project.yaml
  status.yaml
  evidence/
  ui/
    interface-inventory.json
    visual-identity.md
    design-system.json
    design-tokens.json
  mockups/
    batch-01/
      manifest.json
      specification.md
      prompts.md
      assets/
      evidence.md
  client-architecture/
    <slice-id>.web.json
    <slice-id>.android.json
```

## Interface inventory

`schemas/interface-inventory.schema.json` gives each interface a stable `WEB-###` or `APP-###` identity and captures purpose, roles, data, actions, states, navigation and API responsibilities.

Brownfield inventory may additionally classify evidence as `OBSERVED`, `INFERRED` or `PROPOSED`. Proposed behavior must not be silently represented as existing functionality.

## Design system and tokens

`schemas/design-system.schema.json` captures the reusable visual/interaction contract. `schemas/design-tokens.schema.json` captures machine-readable tokens and the accessibility baseline.

A custom logo is conditional. The system must not fabricate branding solely to satisfy a template.

## Mockup batches

`schemas/mockup-batch.schema.json` enforces a maximum of ten inventory views per batch.

Each view records:

- mockup ID;
- inventory ID;
- platform;
- API responsibilities when applicable;
- visual asset path;
- generation status;
- review status;
- contract review status;
- accessibility review status;
- prior approved reference inputs;
- evidence IDs.

The state model is explicit:

```text
PENDING → GENERATED → REVIEWED → APPROVED
```

These states are not interchangeable. File existence proves generation, not approval.

When a batch is `PASS`, every view must be generated and approved and the batch must have passed specification, visual and manual review.

## Versioned visual references

Approved visual assets belong in the consumer repository or in another repository-owned location declared by path. Later AI agents inspect those approved assets before generating or implementing related interfaces.

A generated image must not become a reference input until review explicitly approves it.

## Client architecture artifacts

`schemas/client-architecture.schema.json` defines the pre-implementation contract for one approved `interface_slice + platform`.

The artifact binds implementation to:

- approved inventory IDs and visual references;
- Design System/tokens;
- OpenAPI and canonical operation IDs;
- auth/refresh/logout behavior;
- permissions and routing;
- server/local state ownership and cache invalidation;
- forms and API error mapping;
- async/offline states;
- high-risk mutation idempotency;
- request correlation/observability;
- accessibility;
- unit/UI/integration/E2E strategy;
- platform-specific React or Kotlin decisions;
- Brownfield coexistence/cutover/rollback when applicable.

A web contract accepts only `WEB-###` inventory and an Android contract accepts only `APP-###` inventory. A PASS for one slice/platform does not authorize another.

Client architecture file existence does not itself imply `client_architecture_ready = PASS`; the artifact must validate and the scoped gate must have evidence.

## Evidence registry

`schemas/evidence.schema.json` standardizes evidence metadata across files, commits, CI runs, reports, schemas, visual assets and manual approvals.

Evidence may be scoped to:

- project;
- phase;
- gate;
- interface slice;
- interface;
- platform.

Checks and gates may keep lightweight inline evidence in `status.yaml`; larger evidence collections should live under the declared evidence root.

## Scoped gates

Project gates remain represented by the existing `gates` map in `status.yaml`.

V4-2 adds optional `scoped_gates` for gates that can occur more than once:

- `visual_review_pass` uses scope `interface_slice`;
- `client_architecture_ready` uses scope `interface_slice_platform`.

This keeps v0.3-style project status backward compatible while making V4-1 slice delivery representable.

## Interface slices

`interface_slices` groups stable inventory IDs into coherent delivery units. A slice may be approved and implemented without waiting for every interface in the product, but an unapproved inventory view cannot inherit another slice's gate result.

## Reference pilots

`catalog/reference-pilots.yaml` is a non-normative registry. Reference pilots provide evidence that a rule works or expose a gap in the Blueprint. They never inject hidden product-specific rules into the standard.

## Validation

`scripts/validate-experience-artifacts.py` validates schemas/templates, cross-catalog references and a positive experience fixture.

`scripts/validate-client-architecture.py` validates the V4-4 client contract, platform-specific examples, scoped gate semantics, skill bindings and negative safety cases.

The experience validator specifically verifies that:

1. batches cannot exceed ten views;
2. every batch inventory ID exists in the declared inventory;
3. generated/approved views have repository-owned asset paths;
4. approved views pass contract/accessibility review;
5. file existence alone does not imply approval;
6. scoped gates use the correct scope;
7. catalog phase/check/gate/workflow references remain internally consistent.

The client architecture validator additionally verifies that:

1. web and Android inventory namespaces cannot cross;
2. Brownfield contracts require coexistence metadata;
3. API authorization guardrails cannot be disabled;
4. idempotent operation IDs belong to the slice API binding;
5. request-correlation headers remain consistent;
6. React and Android architecture skills resolve to materialized repository files;
7. `client_architecture_ready` requires the complete V4-4 check set.

## Compatibility

V4 additions are intentionally backward compatible with v0.3 consumer status files:

- existing project-scoped gates remain valid;
- `interface_slices`, `scoped_gates`, `artifacts` and `artifact_locations` are optional;
- client architecture is adopted by existing consumers through Compliance Review, not silent migration;
- stable consumer projects remain on their declared Blueprint version until Compliance Review approves adoption.
