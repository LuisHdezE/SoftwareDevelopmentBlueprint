# Blueprint v0.5 - Executable Skill Model

## Objective

Make reusable process knowledge executable by an AI directly from the repository. A skill explains **how** to satisfy Blueprint contracts; it is never a free-standing source of product truth and cannot declare a gate passed on its own.

## Authority order

1. Consumer project contracts/evidence for its declared Blueprint version.
2. Canonical Blueprint documents/catalogs/schemas/workflows for that version.
3. Materialized `dev-*` skills.
4. Project-specific skills.
5. Reference pilots and chat context.

## Skill states

`planned` reserves an identifier but provides no runnable procedure.

`materialized` means `catalog/skills.yaml` resolves the identifier to `skills/<skill-id>/SKILL.md`, its frontmatter matches the active Blueprint component provenance and automated validation passes.

## Loading algorithm

1. Read consumer `blueprint.version`, mode, stack and capabilities.
2. Read status/slice context.
3. Load only relevant core and conditional materialized skills.
4. Inspect each skill's `canonical_references` from the repository.
5. Follow Stop Conditions instead of inventing missing contracts.
6. Project-specific skills may add domain knowledge but cannot weaken canonical gates/security rules.

## Required contract

Every materialized skill has frontmatter:

- `id`
- `title`
- `version`
- `status`
- `category`
- `applies_to`
- `phases`
- `canonical_references`

Required sections:

- Purpose
- When to Use
- Inputs
- Procedure
- Outputs
- Stop Conditions
- Guardrails
- Canonical References
- Completion Signal

## Blueprint 0.5.0 set

There are **14 materialized skills** in the historical 0.5.0 component set:

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
12. `dev-android-client-architecture`
13. `dev-functional-interface-slice`
14. `dev-event-logging-audit`

The stable 0.5.3 line additionally materialized `dev-mobile-licensing`, for 15 materialized skills, while preserving 25 planned identifiers.

## Blueprint 0.5.4-dev hardening set

The 0.5.4 development lane materializes **16 skills** and keeps the existing 25 planned identifiers. It adds:

- `dev-ios-client-architecture` under a new `ios` category loaded only when `capabilities.ios=true`.

The following client-execution skills carry 0.5.4-dev provenance because their contracts were changed by the iOS/cross-platform hardening:

- `dev-android-client-architecture`
- `dev-ios-client-architecture`
- `dev-functional-interface-slice`

Unchanged skills retain their truthful historical component provenance. `dev-mobile-licensing` remains a 0.5.3 component because iOS support does not generalize the Android-scoped licensing contract.

`dev-functional-interface-slice` operationalizes real client delivery from executable inventory + effective Client Architecture through Functional DoD, Visual & Functional Review, Integration QA and human acceptance for Web, Android and iOS. It also enforces `BLOCKED_BY_API`, namespace isolation and platform-specific evidence/acceptance.

## Technology neutrality

Platform architecture skills describe required architectural decisions but do not mandate a language or framework. Native and cross-platform implementation choices belong to the consumer project contract.

`mobile.strategy=cross_platform` means implementation/code sharing strategy only. It does not enable Android or iOS automatically, and it never lets one platform reuse another platform's gate PASS, QA evidence or human acceptance.

The existing Android `APP-###` namespace remains Android-specific. iOS uses `IOS-###`; Web uses `WEB-###`.

## Product neutrality

Generic `dev-*` skills must not leak product names, private routes, domain entities, secrets or hidden assumptions from a pilot. Reference pilots and older project skills may provide patterns, not norms.

## Validation

`scripts/validate-skills.py` is mode-aware. It verifies catalog identity, active mandatory set, file existence, frontmatter version/category/status, required sections, canonical references, category resolution, skill counts and known product-specific leakage markers.

During 0.5.4 hardening, `scripts/validate-ios-workflow.py` additionally verifies the iOS skill/category, Web/Android/iOS implementation profiles, conditional iOS inventory check, scoped gate reuse and Android-only Mobile Licensing boundary.

CI: `.github/workflows/blueprint-skill-validation.yml` plus the global Blueprint Release Validation lane.

A new Blueprint version may change skill identity only in its explicit release/adoption process; consumer project-specific skills remain versioned by the consumer.
