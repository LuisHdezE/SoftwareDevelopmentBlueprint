# Experience Artifact Model — Blueprint 0.4.0-dev

## Purpose

This document defines the repository-owned artifact model introduced by V4-2. The goal is AI continuity: another agent must be able to inspect the project repository and determine what interfaces exist, which visuals are approved, which evidence supports a gate, and which slices are allowed to progress.

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

The validator specifically verifies that:

1. batches cannot exceed ten views;
2. every batch inventory ID exists in the declared inventory;
3. generated/approved views have repository-owned asset paths;
4. approved views pass contract/accessibility review;
5. file existence alone does not imply approval;
6. scoped gates use the correct scope;
7. catalog phase/check/gate/workflow references remain internally consistent.

## Compatibility

V4-2 additions are intentionally backward compatible with v0.3 consumer status files:

- existing project-scoped gates remain valid;
- `interface_slices`, `scoped_gates`, `artifacts` and `artifact_locations` are optional;
- stable consumer projects remain on their declared Blueprint version until Compliance Review approves adoption.
