# Blueprint 0.5 Client Architecture Decision

## Decision

Blueprint 0.5 uses a composed Client Architecture contract:

`Platform Client Architecture Baseline + Slice Architecture Binding = Effective Client Architecture Contract`

This replaces the former pattern of repeating platform-wide auth, API client, observability, testing, accessibility and offline decisions inside every slice artifact.

## Rationale

The external audit identified unnecessary duplication and an implicit static-mockup dependency in the 0.4-era client architecture schema. The 0.5 model keeps governance while reducing repetition:

- platform-wide decisions are owned once per platform/project;
- slice bindings carry only inventory, operationIds, permissions, routes, states and overrides that vary by slice;
- Design System/tokens remain required;
- static visual references are conditional;
- `visual_references.mode = none` is valid;
- if visual references are supplied they must be approved, versioned and real;
- API and executable Interface Inventory remain authoritative;
- `client_architecture_ready` remains scoped to `interface_slice_platform`.

## Machine enforcement

`validate-client-architecture.py` validates schema shape plus referential integrity against the executable Interface Inventory and OpenAPI fixture. Negative tests reject fabricated inventory IDs, fabricated operationIds, invented permissions, incompatible platform baselines, invalid idempotency bindings and fake visual-reference paths.

## Compatibility

This change does not auto-migrate consumer repositories. Existing consumers adopt the composed contract through Compliance Review and explicit Blueprint version adoption.
