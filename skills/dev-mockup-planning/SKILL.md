---
id: dev-mockup-planning
title: Mockup Planning and Visual Review
version: 0.4.0-dev
status: materialized
category: web
applies_to:
  - greenfield
  - brownfield
phases:
  - mockup_planning
  - mockups
  - visual_review_gate
canonical_references:
  - schemas/mockup-batch.schema.json
  - templates/mockup-batch.example.json
  - documentation/EXPERIENCE_ARTIFACT_MODEL.md
  - schemas/evidence.schema.json
  - catalog/gates.yaml
---

# Mockup Planning and Visual Review

## Purpose

Plan and review visual interface batches so every generated image is traceable, versioned, and explicitly approved before implementation.

## When to Use

Use after `design_system_ready` and for every interface slice that needs web or Android visual approval.

## Inputs

- Schema-valid interface inventory.
- Approved design system/tokens.
- Existing approved visual references.
- API responsibilities and permission/state constraints for the target slice.

## Procedure

1. Choose a coherent interface slice and create a mockup batch containing no more than 10 inventory views. Prefer related views that establish reusable visual patterns.
2. For each view record inventory ID, platform, API responsibilities, intended states, prompt/specification path, and output asset path before generation.
3. Inspect already approved visual references in the repository and declare which ones guide the new batch. Do not rely on chat-only images or memory.
4. Generate assets and version them at the declared paths. File existence moves a view to generated evidence only; it never implies review or approval.
5. Review each generated view against the inventory/API contract, design system, permissions, responsive behavior, and accessibility requirements.
6. Set explicit review states. `GENERATED`, `REVIEWED`, and `APPROVED` are distinct. An approved view requires contract/accessibility review PASS and an approved visual reference path.
7. Evaluate `visual_review_pass` for the interface slice only when every view in that slice satisfies the mockup schema and evidence requirements.
8. Allow an approved slice to progress without waiting for the whole product, but block any unapproved view from client architecture/implementation.

## Outputs

- Schema-valid mockup batch manifest.
- Versioned visual assets and prompt/specification artifacts.
- Per-view review/approval evidence.
- Scoped `visual_review_pass` evaluation.

## Stop Conditions

- Design System Gate is not PASS.
- The batch exceeds 10 views.
- A mockup references an inventory ID that does not exist.
- A visual exists only in chat or an external transient location.
- Approval is being inferred from generation or from reviewer silence.
- The mockup invents API behavior, permissions, or states.

## Guardrails

- Generated image ≠ reviewed image ≠ approved mockup.
- Approved assets must live in the project repository and be reusable by future AI agents.
- Visual review is scoped, explicit, and evidence-backed.
- The API contract remains authoritative even when a visual concept would be more convenient.

## Canonical References

- `schemas/mockup-batch.schema.json`
- `templates/mockup-batch.example.json`
- `documentation/EXPERIENCE_ARTIFACT_MODEL.md`
- `schemas/evidence.schema.json`
- `catalog/gates.yaml`

## Completion Signal

The skill is complete only when its required outputs exist in the repository, the relevant Blueprint checks/gates can be evaluated from evidence, and no stop condition remains unresolved.
