# Blueprint v0.5 - Executable Skill Model

## Objective

Make reusable process knowledge executable by an AI directly from the repository. A skill explains **how** to satisfy Blueprint contracts; it is never a free-standing source of product truth and cannot declare a gate passed on its own.

Stable Blueprint **0.5.0** materializes 14 skills. The active **0.5.1-dev** architecture-conformance hardening candidate materializes one additional skill, `dev-architecture-conformance`, while root `VERSION` remains the latest stable `0.5.0` until a separate patch release closure.

## Authority order

1. Consumer project contracts/evidence for its declared Blueprint version.
2. Canonical Blueprint documents/catalogs/schemas/workflows for that version.
3. Materialized `dev-*` skills.
4. Project-specific skills.
5. Reference pilots and chat context.

## Skill states

`planned` reserves an identifier but provides no runnable procedure.

`materialized` means `catalog/skills.yaml` resolves the identifier to `skills/<skill-id>/SKILL.md`, its frontmatter matches the applicable stable/development identity and automated validation passes.

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

## Blueprint 0.5.0 stable set

There are **14 materialized skills**:

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

The remaining 25 catalog identifiers stay `planned`.

`dev-functional-interface-slice` operationalizes real client delivery from executable inventory + effective Client Architecture through Functional DoD, Visual & Functional Review, Integration QA and human acceptance. It also enforces `BLOCKED_BY_API` semantics.

## Blueprint 0.5.1-dev candidate

The architecture-conformance hardening candidate has **15 materialized skills**. It preserves the stable 0.5.0 set and adds:

15. `dev-architecture-conformance`

This skill operationalizes the new REQUIRED checks:

- `architecture.implementation_constraints`;
- `architecture.implementation_conformance`;
- `architecture.conformance_guard`.

It requires testable implementation boundaries, exact-revision conformance evidence and at least one executable guard required in CI. Functional tests remain an independent dimension and cannot substitute architecture conformance.

The skill is architecture-neutral: it validates the project's approved architecture. Clean/Hexagonal dependency rules are applied only when those boundaries are actually part of the approved project contract.

During the 0.5.1 development boundary, unchanged stable 0.5.0 skill files may remain pinned to `version: 0.5.0`; the new skill uses `0.5.1-dev`. A later stable 0.5.1 release-closure boundary must converge active skill identities deliberately.

## Product neutrality

Generic `dev-*` skills must not leak product names, private routes, domain entities, secrets or hidden assumptions from a pilot. Reference pilots and older project skills may provide patterns, not norms.

## Validation

`scripts/validate-skills.py` verifies catalog identity, current mandatory set, file existence, frontmatter version/category/status, required sections, canonical references, category resolution and known product-specific leakage markers.

For the 0.5.1-dev line it additionally validates that the only newly materialized skill in this hardening boundary is `dev-architecture-conformance`.

CI:

- `.github/workflows/blueprint-skill-validation.yml`
- `.github/workflows/blueprint-architecture-conformance-validation.yml`

A new Blueprint version may change skill identity only in its explicit release/adoption process; consumer project-specific skills remain versioned by the consumer.
