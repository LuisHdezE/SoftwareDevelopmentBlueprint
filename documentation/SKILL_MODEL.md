# Blueprint v0.4 — Executable Skill Model

## Objective

Make reusable process knowledge loadable by an AI directly from the repository. A skill is an executable procedure bound to canonical Blueprint contracts, not a free-standing source of product truth.

## Authority order

When instructions disagree, use this precedence:

1. Consumer project's declared Blueprint version and approved project contracts/evidence.
2. Canonical Blueprint documents, catalogs, schemas, workflows, checks and gates for that version.
3. Materialized `dev-*` skills.
4. Project-specific skills.
5. Chat context or ad-hoc suggestions.

A skill may explain *how* to satisfy a gate. It cannot declare a gate passed on its own.

## Lifecycle

### planned

The skill identifier is catalogued for future work. An agent must not assume a runnable procedure exists.

### materialized

`catalog/skills.yaml` contains a repository path and the file passes automated skill validation. The agent may load it when its category/capability/phase applies.

## Loading algorithm

Given a consumer project:

1. Read the project manifest (`blueprint.version`, mode, stack, capabilities).
2. Read `.blueprint/status.yaml` or equivalent status artifact to identify current phase/slice.
3. Load core materialized skills relevant to the task.
4. Add conditional materialized skills for backend/web/android/saas/brownfield/devops capabilities.
5. For each loaded skill, inspect its `canonical_references`.
6. If the skill references an artifact that the consumer project does not yet have, follow the skill's stop conditions rather than inventing it.
7. Project-specific skills may add domain context but cannot weaken Blueprint gates or security rules.

## Required skill contract

Every materialized `SKILL.md` contains YAML frontmatter:

- `id`
- `title`
- `version`
- `status: materialized`
- `category`
- `applies_to`
- `phases`
- `canonical_references`

And these procedural sections:

- Purpose
- When to Use
- Inputs
- Procedure
- Outputs
- Stop Conditions
- Guardrails
- Canonical References
- Completion Signal

## Product-neutrality rule

A `dev-*` skill must not contain product-specific domain names, routes, roles, business entities, tenant names, secrets, or hidden assumptions copied from a reference implementation.

Reference pilots and older project skills may be used to discover generic patterns. They are evidence sources, not normative sources.

## Validation

`scripts/validate-skills.py` verifies:

- catalog structure;
- all mandatory v0.4 skills are `materialized`;
- each materialized path exists;
- frontmatter identity/category/status/version agrees with the catalog;
- required sections exist;
- each canonical reference exists in the Blueprint repository;
- category lists do not silently reference an unknown skill identifier;
- materialized `dev-*` skills do not contain known reference-pilot/product markers.

CI: `.github/workflows/blueprint-skill-validation.yml`.

## Future extension

V4-3 intentionally materializes the priority set required to operate the Blueprint through Brownfield analysis, API gates, visual delivery, React client architecture, accessibility, and audit. Other catalog identifiers remain `planned` and can be materialized in future releases without pretending they already exist.
