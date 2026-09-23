# Blueprint 0.5.5-dev · API Authority Capability Model

## Status

Development contract for **Increment 1** of the governed `0.5.5-dev` hardening lane.

This document does not promote stable Blueprint `0.5.4`, does not mutate any consumer, and does not yet make workflow/gate applicability conditional. That belongs to Increment 2.

## Why this exists

Stable `0.5.4` permits `stack.backend: null` and `stack.database: null`, but downstream contracts assume API authority. The WebBlueprint compliance review exposed that a legitimate frontend-only/local/static/non-authoritative mock product cannot represent its current architecture without inventing API artifacts.

The `0.5.5-dev` authority model makes the missing distinction explicit.

## Development overlay

Stable `schemas/project.schema.json` remains unchanged and authoritative for released `0.5.4`.

Increment 1 adds:

```text
schemas/project-api-authority-v055-dev.schema.json
```

During hardening, a candidate project manifest is validated against both the stable 0.5.4 project schema and the 0.5.5-dev authority overlay. Final release closure may later fold the overlay into the promoted stable project schema.

## Contract

Every project opting into the `0.5.5-dev` authority overlay must declare:

```yaml
authority:
  api:
    mode: api_backed | api_optional
    revision: <positive integer>
    decision_ref: <governed evidence reference>
    claims:
      remote_authoritative_business_data: true|false
      server_authentication: true|false
      server_authorization: true|false
      remote_persistent_mutations: true|false
      permission_enforcement: true|false
      backend_only_invariants: true|false
```

`api_optional` additionally declares one or more allowed sources:

```yaml
allowed_sources:
  - local
  - static
  - mock_non_authoritative
```

## `api_backed`

Use `api_backed` when at least one authoritative server claim is true.

The development overlay requires:

- a non-null backend stack;
- an OpenAPI artifact location;
- at least one authoritative server claim.

This preserves the strict intent of the 0.5.4 API-backed path.

## `api_optional`

Use `api_optional` only when current executable behavior is genuinely local/static or non-authoritative mock/provider behavior.

The overlay requires every authoritative server claim to be false and forbids an `openapi` artifact location.

Therefore `api_optional` cannot claim:

- remote authoritative business data;
- server authentication;
- server authorization;
- remote persistent mutation or transition;
- permission enforcement;
- backend-only invariants.

A backend implementation may exist in the repository for unrelated reasons. Backend presence alone is not authority. Authority is an explicit semantic contract.

## Why OpenAPI is forbidden in `api_optional`

An API-optional project must not create an OpenAPI document merely to make gates green. If real API authority exists, the project belongs on the `api_backed` path.

Increment 3 will apply the same rule to client architecture and functional slices so local/static behavior can be executable without invented `operationId` values.

## `offline_mobile`

Current Blueprint semantics bind `offline_mobile` to an API-backed synchronization model. Increment 1 preserves that strict behavior. An `offline_mobile: true` manifest therefore cannot declare `api_optional`.

Changing the mobile authority model would require a separate governed decision and is outside this increment.

## Governed transitions

Authority mode changes are architectural decisions, not incidental config edits.

The contract carries:

- `revision`, beginning at `1`;
- `decision_ref`, pointing to governed evidence.

A mode transition must increase `revision` and use a new `decision_ref`. The Increment 1 validator contains positive and negative transition cases.

## Validation matrix

Positive cases:

- frontend-only local/static consumer;
- mock/provider-driven non-authoritative consumer;
- strict API-backed consumer;
- governed transition from API-optional to API-backed.

Negative cases:

- API-optional permission enforcement;
- API-optional remote persistent mutations;
- API-optional server authentication;
- API-optional OpenAPI binding;
- omitted authority declaration;
- API-backed project without OpenAPI;
- API-backed project without backend declaration;
- fake API-backed declaration with no server authority claim;
- `offline_mobile` attempting the API-optional path;
- silent authority mode transition without revision increment;
- silent authority mode transition without a new decision reference.

## Compatibility

No existing `0.5.4` consumer auto-upgrades.

The two development examples keep `blueprint.version: 0.5.4` because the hardening lane deliberately preserves released identity until final promotion. They demonstrate the candidate authority extension through the overlay.

## Next increment

Increment 2 will use this authority declaration to make server/data/API workflow phases and gates conditionally applicable while preserving the complete strict pipeline for `api_backed`.
