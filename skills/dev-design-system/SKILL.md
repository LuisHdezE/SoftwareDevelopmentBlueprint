---
id: dev-design-system
title: Visual Identity and Design System
version: 0.5.0
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

Define reusable, accessible visual rules that drive functional clients directly and may also drive optional mockups/prototypes. Visual Identity is conditional; the Design System is the reusable contract.

## When to Use

Use after `interface_inventory_ready` and before Client Architecture/functional implementation. Use Visual Identity only when branding, preservation or deliberate identity change actually applies. Mockups are not required to complete the Design System.

## Inputs

- Executable Interface Inventory.
- Existing colors, typography, components, logos/assets and CSS/theme configuration.
- Brand/product requirements when applicable.
- Accessibility, responsive and semantic-state requirements.
- Brownfield visual conventions that must be preserved or deliberately migrated.

## Procedure

1. Determine whether Visual Identity applies. Existing brand requirements, deliberate rebranding or Brownfield identity preservation may activate it; absence of those needs does not require inventing a logo or branding exercise.
2. Inventory existing visual language and classify what should be preserved, normalized, replaced or explicitly left optional.
3. Define design tokens for colors, typography, spacing, radii, elevation, breakpoints, motion and semantic states. Prefer semantic aliases over one-off raw values.
4. Define reusable components and interaction rules for navigation, buttons, forms, tables, cards, dialogs and feedback.
5. Define loading, empty, error, permission, conflict, rate-limit, offline and domain-status presentations required by the executable inventory.
6. Encode responsive behavior and accessibility requirements, including contrast, focus, keyboard/switch behavior and minimum target sizing.
7. For Brownfield, document migration/coexistence decisions such as duplicate fonts, rigid offsets, ad-hoc semantic colors or legacy component styles without silently rewriting runtime code.
8. Validate Design System/token artifacts. `design_system_ready` means functional clients have enough reusable rules to implement coherently even if no mockups are produced.
9. If mockups/prototypes are later activated as a risk-reduction branch, require them to consume this same Design System rather than creating a competing visual language.

## Outputs

- Schema-valid Design System artifact.
- Machine-readable design tokens.
- Accessibility/responsive/semantic-state rules.
- Conditional Visual Identity artifact when applicable.
- Brownfield preserve/normalize/migrate decisions where applicable.

## Stop Conditions

- Executable Interface Inventory is not ready.
- Identity decisions conflict with required accessibility.
- A custom identity/logo is being invented with no product need.
- Tokens reference undefined aliases or semantic states.
- A mockup or functional client is creating visual rules that contradict the Design System without an approved change.

## Guardrails

- Design System is a direct input to functional implementation, not merely a mockup styling aid.
- Visual Identity is conditional; Design System consistency/accessibility are required when client delivery applies.
- Accessibility is part of the design contract, not release polish.
- Brownfield visual debt is documented before it is changed.
- Optional mockups must consume the same tokens/components as the real client.

## Canonical References

- `schemas/design-tokens.schema.json`
- `schemas/design-system.schema.json`
- `templates/design-tokens.example.json`
- `templates/design-system.example.json`
- `catalog/gates.yaml`

## Completion Signal

Complete only when reusable design tokens/components/states exist and validate, responsive/accessibility expectations are explicit, any applicable Visual Identity decision is documented, and `design_system_ready` can truthfully PASS without requiring a mockup branch to exist.
