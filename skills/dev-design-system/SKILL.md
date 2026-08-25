---
id: dev-design-system
title: Visual Identity and Design System
version: 0.4.0
status: materialized
category: web
applies_to:
  - greenfield
  - brownfield
phases:
  - visual_identity
  - design_system
canonical_references:
  - schemas/design-tokens.schema.json
  - schemas/design-system.schema.json
  - templates/design-tokens.example.json
  - templates/design-system.example.json
  - catalog/gates.yaml
---

# Visual Identity and Design System

## Purpose

Turn visual intent and existing product identity into reusable, accessible tokens and component rules before mockups are generated.

## When to Use

Use after interface inventory is ready and before mockup planning. In Brownfield, use it to normalize and preserve coherent existing identity rather than rebrand by default.

## Inputs

- Interface inventory.
- Existing colors, typography, components, logos/assets, and CSS/theme configuration.
- Brand/product requirements.
- Accessibility and responsive requirements.

## Procedure

1. Inventory existing visual language and classify what should be preserved, normalized, replaced, or left optional. Do not invent a custom logo if the product does not need one.
2. Define visual identity direction: primary/accent palette, typography roles, density, iconography, imagery, tone, and product-specific semantic state categories.
3. Create design tokens for colors, typography, spacing, radii, elevation, breakpoints, motion, and semantic states. Prefer semantic aliases over raw one-off values in component guidance.
4. Define reusable component and interaction rules for navigation, buttons, forms, tables, cards, dialogs, feedback, loading/empty/error/permission/offline states, and domain status presentations.
5. Validate contrast and interaction requirements against the declared accessibility target. Include minimum touch target and responsive behavior.
6. For Brownfield, document migration/coexistence decisions such as duplicate fonts, rigid offsets, forced zoom, ad-hoc semantic colors, or legacy component styles without silently rewriting runtime code.
7. Validate design-system/token artifacts and mark `design_system_ready` only when the project has evidence-backed reusable rules.

## Outputs

- Design-system artifact.
- Machine-readable design tokens.
- Accessibility/responsive/semantic-state rules.
- Brownfield preserve/normalize/migrate decisions where applicable.

## Stop Conditions

- Interface inventory is not ready.
- Identity decisions conflict with required accessibility.
- The proposed system requires a rebrand with no product justification.
- Tokens reference undefined aliases or semantic states.
- Mockups have already begun inventing a divergent visual language.

## Guardrails

- Consistency beats novelty.
- Accessibility is part of the design contract, not a post-implementation polish step.
- Brownfield visual debt is documented before it is changed.
- Approved design tokens guide mockups and client implementation.

## Canonical References

- `schemas/design-tokens.schema.json`
- `schemas/design-system.schema.json`
- `templates/design-tokens.example.json`
- `templates/design-system.example.json`
- `catalog/gates.yaml`

## Completion Signal

The skill is complete only when its required outputs exist in the repository, the relevant Blueprint checks/gates can be evaluated from evidence, and no stop condition remains unresolved.
