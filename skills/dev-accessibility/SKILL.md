---
id: dev-accessibility
title: Accessibility Contract Review
version: 0.5.0
status: materialized
category: web
applies_to:
  - greenfield
  - brownfield
phases:
  - design_system
  - mockup_review
  - functional_interface_slice
  - visual_functional_review
  - integration_qa
canonical_references:
  - schemas/design-system.schema.json
  - schemas/mockup-batch.schema.json
  - schemas/functional-interface-slice.schema.json
  - catalog/checks.yaml
  - catalog/gates.yaml
---

# Accessibility Contract Review

## Purpose

Make accessibility a continuous contract across Design System, optional mockups, functional implementation, Visual & Functional Review and Integration QA rather than a final scanner pass.

## When to Use

Use whenever client design rules are defined or a functional Web slice is implemented/reviewed/tested. Use during the conditional mockup branch only when that branch exists.

## Inputs

- Declared accessibility target, default WCAG 2.2 AA unless project policy says otherwise.
- Design tokens/components and executable Interface Inventory states.
- Optional mockup assets/specifications when present.
- Implemented semantic markup, forms and interaction behavior.
- Functional slice and QA evidence.

## Procedure

1. Check color contrast for text, controls, focus indicators and meaningful state colors. State must not rely on color alone.
2. Define keyboard navigation, visible focus, logical order, skip/navigation patterns, dialog focus management and escape behavior.
3. Ensure form controls have programmatic labels, instructions, validation messages and error association. Preserve server/API validation meaning in accessible UI feedback.
4. Prefer semantic landmarks/headings/tables/lists before ARIA. Use ARIA only where native semantics are insufficient.
5. Validate responsive reflow, zoom and minimum interaction/touch targets. Do not solve layout issues with accessibility-hostile scaling hacks.
6. Cover loading, empty, generic error, permission, conflict, validation, rate-limit and offline states with understandable text and assistive-technology announcements when needed.
7. If mockups are used, record mockup accessibility review without implying that static review proves runtime accessibility.
8. During Functional Interface Slice implementation, add automated accessibility checks plus component/integration tests appropriate to risk.
9. During Visual & Functional Review, manually verify keyboard/focus behavior and representative screen-reader semantics on the actual client.
10. During Integration QA, preserve evidence for critical flows and document justified exceptions with owner/remediation decision.

## Outputs

- Accessibility requirements in the Design System.
- Optional per-mockup accessibility evidence when applicable.
- Functional implementation accessibility evidence.
- Visual & Functional Review accessibility evidence.
- Integration QA evidence and documented exceptions.

## Stop Conditions

- Contrast or interaction requirements fail the target level.
- A critical functional flow is keyboard-inaccessible.
- Meaning depends solely on color, icon shape or hover.
- Static mockup approval is being used as proof of runtime accessibility.
- An accessibility exception has no owner or remediation decision.
- `ACCEPTED` is being proposed without required accessibility review/QA evidence.

## Guardrails

- Prefer native semantic HTML over ARIA recreation.
- Accessibility can block functional, review, QA and release gates.
- Automated scanners supplement, not replace, manual interaction/assistive-technology review.
- Optional mockups do not create an accessibility prerequisite when the project proceeds directly to functional implementation.

## Canonical References

- `schemas/design-system.schema.json`
- `schemas/mockup-batch.schema.json`
- `schemas/functional-interface-slice.schema.json`
- `catalog/checks.yaml`
- `catalog/gates.yaml`

## Completion Signal

Complete only when accessibility requirements are represented at the current delivery stage and the corresponding gate has enough real evidence to evaluate. Final slice acceptance requires runtime accessibility evidence, not merely a passing static mockup or automated scanner.
