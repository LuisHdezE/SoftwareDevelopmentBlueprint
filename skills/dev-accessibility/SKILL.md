---
id: dev-accessibility
title: Accessibility Contract Review
version: 0.4.0
status: materialized
category: web
applies_to:
  - greenfield
  - brownfield
phases:
  - design_system
  - visual_review_gate
  - web_implementation
  - integration_qa
canonical_references:
  - schemas/design-system.schema.json
  - schemas/mockup-batch.schema.json
  - catalog/checks.yaml
  - catalog/gates.yaml
---

# Accessibility Contract Review

## Purpose

Make accessibility a continuous contract across design, mockup review, implementation, and QA rather than a final audit.

## When to Use

Use whenever design tokens/components are defined, mockups are reviewed, or web interfaces are implemented/tested.

## Inputs

- Declared accessibility target, default WCAG 2.2 AA unless project policy says otherwise.
- Design tokens/components.
- Mockup assets/specifications.
- Implemented semantic markup and interaction behavior.

## Procedure

1. Check color contrast for text, interactive controls, focus indicators, and meaningful state colors. State must not be conveyed by color alone.
2. Define keyboard navigation, visible focus, logical tab order, skip/navigation patterns, dialog focus management, and escape behavior.
3. Ensure form controls have programmatic labels, instructions, validation messages, and error association. Preserve server/API validation meaning in accessible UI feedback.
4. Require semantic landmarks/headings/tables/lists before ARIA. Use ARIA only to add semantics not available in native elements.
5. Validate responsive layouts and minimum interaction/touch targets. Zoom/reflow must not be defeated by rigid scaling hacks.
6. Review loading, empty, error, permission, conflict, rate-limit, and offline states for understandable text and assistive-technology announcements when needed.
7. For approved mockups, record accessibility review PASS only when visual requirements are sufficient for implementation. For implemented UI, add automated checks plus manual keyboard/screen-reader spot checks appropriate to risk.

## Outputs

- Accessibility requirements in the design system.
- Per-mockup accessibility review result.
- Implementation accessibility evidence.
- Documented exceptions with rationale and remediation plan.

## Stop Conditions

- Contrast or interaction requirements fail the target level.
- A critical flow is keyboard-inaccessible.
- Meaning depends solely on color, icon shape, or hover.
- A mockup is being approved without enough information to implement accessible behavior.
- An exception has no owner or remediation decision.

## Guardrails

- Prefer native semantic HTML over ARIA recreation.
- Accessibility requirements can block visual approval and release gates.
- Automated scanners supplement, not replace, keyboard/assistive-technology review.

## Canonical References

- `schemas/design-system.schema.json`
- `schemas/mockup-batch.schema.json`
- `catalog/checks.yaml`
- `catalog/gates.yaml`

## Completion Signal

The skill is complete only when its required outputs exist in the repository, the relevant Blueprint checks/gates can be evaluated from evidence, and no stop condition remains unresolved.
