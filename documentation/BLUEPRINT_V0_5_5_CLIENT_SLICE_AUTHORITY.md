# Blueprint 0.5.5-dev · Client Architecture & Slice Authority

## Purpose

Increment 3 closes the client-side authority contradiction discovered by the WebBlueprint compliance review without weakening the stable 0.5.4 API-backed path.

Stable 0.5.4 remains unchanged during hardening. This increment adds a development overlay that governs how Project API Authority projects into Client Platform Architecture, Client Slice Architecture and Functional Interface Slice semantics.

## Authority projection

```text
Project authority.api.mode
        |
        v
Client Platform baseline
        |
        v
Client Slice Architecture
        |
        v
Functional Interface Slice
```

The authority mode must remain identical across the chain.

## api_backed

`api_backed` preserves the existing 0.5.4 client contract:

- Client Platform authority comes from an API client and OpenAPI;
- authorization boundary is the API;
- permission source is the API contract;
- Client Slice binds OpenAPI operation IDs and permissions;
- API remains authoritative;
- `real_api` cannot be `N/A` for the governed accepted boundary.

The validator cross-checks the development overlay against the stable 0.5.4 Web platform baseline, slice architecture binding and Functional Interface Slice example. The overlay does not replace those artifacts during the development lane.

## api_optional

`api_optional` is a distinct authority model, not a weaker API-backed client.

A client may use:

- Application/provider contracts;
- mock adapters;
- local static adapters;
- local persistence adapters;
- derived/local behavior.

It must not claim:

- OpenAPI binding;
- remote authoritative business data;
- remote persistent mutations;
- server authentication or authorization;
- server permission enforcement;
- API-authoritative behavior.

The slice therefore binds provider contracts and use cases rather than fake OpenAPI operation IDs.

For a legitimate API-optional slice:

- `real_api = N/A`;
- `server_auth_rbac = N/A`;
- `provider_contract_boundary = PASS`;
- hardcoded authoritative business data remains forbidden;
- invented capabilities remain forbidden.

This fits contract-first clients such as WebBlueprint, where Presentation depends on Application contracts and replaceable mock/local adapters without asserting a trusted server boundary.

## Interface Inventory compatibility

Increment 3 does not change the Interface Inventory schema. Stable 0.5.4 already supports `local`, `static` and `derived` data sources, local actions, and optional `operation_ids`. The development validator proves that an API-optional Web item can be represented truthfully with the existing inventory contract.

## Fail-closed rules

The development schema rejects:

- `api_optional` plus API client binding;
- `api_optional` plus remote authority;
- `api_optional` plus server authorization or permissions;
- `api_optional` plus `real_api = PASS`;
- `api_backed` plus provider-only slice binding;
- `api_backed` plus `real_api = N/A`.

Project authority is cross-checked against the overlay examples.

## Deliberate non-goals

This increment does not define authority-aware Integration QA transport semantics. `integration_qa_scope` is pinned to `DEFERRED_TO_INCREMENT_4` so the boundary cannot be silently blurred.

This increment also does not mutate:

- stable `VERSION=0.5.4`;
- stable Client Architecture schemas/templates;
- stable Functional Interface Slice schema/template;
- stable gates/check catalogs;
- WebBlueprint or any other consumer.

## Release integration

Before 0.5.5 can become stable, release closure must fold the validated authority overlay into the canonical 0.5.5 client/slice contracts, documentation and validators. Until that promotion, 0.5.4 remains the only stable consumer release.
