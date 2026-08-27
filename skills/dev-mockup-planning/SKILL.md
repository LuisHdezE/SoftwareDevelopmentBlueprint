---
id: dev-mockup-planning
title: Mockup Planning and Review
version: 0.5.0-dev
status: materialized
category: web
applies_to:
  - greenfield
  - brownfield
phases:
  - mockup_planning
  - mockups
  - mockup_review
canonical_references:
  - schemas/mockup-batch.schema.json
  - templates/mockup-batch.example.json
  - documentation/EXPERIENCE_ARTIFACT_MODEL.md
  - schemas/evidence.schema.json
  - catalog/gates.yaml
---

# Mockup Planning and Review

## Purpose

Use mockups/prototypes as an optional risk-reduction capability when static visual exploration or pre-implementation approval adds value, while preserving traceability and explicit human review.

## When to Use

Activate only when the project, slice or reviewer deliberately chooses the conditional mockup branch after `design_system_ready`. Do not activate merely because client implementation exists. A project may proceed directly from Design System to Client Architecture without mockups.

## Inputs

- Executable Interface Inventory.
- Approved Design System/tokens.
- Target slice and platform.
- API responsibilities/`operationId`, permissions and states relevant to the selected views.
- Existing approved visual references when available.
- Explicit reason the mockup branch reduces risk or supports approval.

## Procedure

1. Record why mockups/prototypes apply to the chosen slice. If there is no meaningful visual/design risk or review need, stop the conditional branch and continue the principal functional-delivery path.
2. Choose a coherent interface slice and create a batch of no more than 10 inventory views.
3. For each view record inventory ID, platform, canonical operationIds when applicable, intended states and output/reference paths before generation.
4. Inspect repository-owned approved references. Do not rely on chat-only images, memory or invented paths.
5. Generate/version assets at declared paths. File existence proves only generation, never review or approval.
6. Review each generated view against executable inventory, API/permission contract, Design System, responsive requirements and accessibility.
7. Keep `GENERATED`, `REVIEWED` and `APPROVED` distinct. Approval requires explicit review evidence; silence or generation cannot promote status.
8. Evaluate conditional `mockup_review_pass` only for the exact interface slice when the branch was activated and every required view/evidence passes.
9. Feed approved references into Client Architecture only when they exist. Their absence is valid and must not be replaced with fake placeholders.
10. After functional implementation, Visual & Functional Review is performed on the real client. A static mockup approval never substitutes for functional review or Integration QA.

## Outputs

- Decision/evidence that the conditional mockup branch applies.
- Schema-valid mockup batch manifest.
- Versioned visual assets/specifications when generated.
- Explicit per-view review/approval evidence.
- Conditional `mockup_review_pass` result.

## Stop Conditions

- Design System Ready is not PASS.
- The branch is being treated as universally mandatory.
- Batch exceeds 10 views.
- A view references nonexistent inventory/operationId.
- A visual exists only in chat/transient storage.
- Approval is inferred from generation or reviewer silence.
- A mockup invents API behavior, permissions, business data or states.
- A fake reference path is being added to unblock Client Architecture.

## Guardrails

- Mockups/prototypes are conditional, not the main delivery pipeline.
- Generated image ≠ reviewed image ≠ approved reference.
- Design System and executable inventory remain upstream contracts.
- API remains authoritative even when a visual concept would be convenient.
- Client Architecture and functional implementation may proceed without mockups when the conditional branch is not activated.
- Final Visual & Functional Review targets the actual functional client.

## Canonical References

- `schemas/mockup-batch.schema.json`
- `templates/mockup-batch.example.json`
- `documentation/EXPERIENCE_ARTIFACT_MODEL.md`
- `schemas/evidence.schema.json`
- `catalog/gates.yaml`

## Completion Signal

Complete when the conditional decision is explicit and, if activated, the batch and review evidence are valid through `mockup_review_pass`. Completion of this skill does not itself authorize implementation; absence of this skill's branch also does not block Client Architecture unless project governance explicitly made that branch applicable.
