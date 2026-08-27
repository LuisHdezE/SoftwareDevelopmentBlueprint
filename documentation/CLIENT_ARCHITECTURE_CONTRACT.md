# Client Architecture Contract — Blueprint 0.5.0-dev

## Purpose

Client Architecture is the repository-owned pre-implementation contract for client delivery. In Blueprint 0.5 the effective contract is composed instead of duplicating platform-wide decisions in every slice:

`Platform Client Architecture Baseline + Slice Architecture Binding = Effective Client Architecture Contract`

The baseline owns reusable platform decisions. The slice binding owns only what varies for one `interface_slice + platform`.

Canonical schemas:

- `schemas/client-platform-architecture.schema.json`
- `schemas/client-architecture.schema.json`

`client_architecture_ready` is still evaluated as `interface_slice_platform`. A PASS for one slice/platform authorizes neither another slice nor another platform.

## Upstream authority

Before a scoped Client Architecture PASS:

1. the initial project `api_gate` is PASS;
2. `interface_inventory_ready` is PASS;
3. `design_system_ready` is PASS;
4. the platform baseline is valid and applicable;
5. the slice binding resolves to real inventory IDs, permissions and OpenAPI `operationId` values.

Mockups/prototypes are not a universal prerequisite. When approved visual references exist they may be attached to the slice binding, but absence of static references cannot by itself block Client Architecture.

## Platform Client Architecture Baseline

One baseline is reusable by slices on the same platform/project until a change invalidates it.

It defines platform-wide decisions for:

- Design System and token ownership;
- OpenAPI/API client location and API authorization boundary;
- Problem Details/error contract and correlation/idempotency headers;
- authentication/session lifecycle and credential storage;
- permission presentation while API authorization remains authoritative;
- server/local state ownership and cache strategy;
- forms/validation mapping;
- observability, secret redaction and PII policy;
- accessibility target and interaction minimums;
- unit/UI/integration/E2E testing responsibilities;
- offline strategy;
- implementation guardrails;
- React/Web or Kotlin/Android platform contract;
- Brownfield coexistence/cutover/rollback when applicable.

Baseline approval is not slice approval. It supplies reusable decisions to scoped bindings.

## Slice Architecture Binding

The slice binding is intentionally small. It defines:

- exact `interface_slice` and platform;
- executable Interface Inventory IDs;
- reference to the platform baseline;
- optional approved visual references;
- OpenAPI path/revision and exact `operationId` set;
- permissions used by the slice;
- routes/navigation;
- required async/error/offline states;
- idempotent operations and retry semantics;
- slice-specific cache/offline/testing overrides;
- guardrails that keep API and inventory authoritative.

The binding may not invent endpoints, permissions, states, payload semantics or business transitions.

## Visual references

`visual_references.mode` has two valid forms:

- `none`: no static visual reference is required and `approved_reference_paths` is empty;
- `approved_optional`: one or more approved, versioned references are attached.

A generated image is not implicitly reviewed or approved. A reference path cannot be fabricated to satisfy a schema.

The Design System and tokens remain required regardless of whether mockups exist.

## Referential integrity

Validation must resolve the effective contract against repository artifacts, not only JSON shape.

For each binding the validator verifies at least:

- platform baseline file exists and validates;
- baseline project/mode/platform are compatible with the binding;
- Design System/token references exist;
- inventory IDs exist in the executable inventory and belong to the slice/platform;
- `operationId` values exist in OpenAPI and are bound by those inventory interfaces;
- permissions declared by the binding exist on the selected inventory interfaces;
- idempotency operations are a subset of the binding operations;
- optional visual references exist when declared;
- API and observability correlation contracts do not conflict;
- Brownfield coexistence is present when required;
- implementation guardrails cannot disable API authority or introduce authoritative hardcoded business data.

Fictitious IDs and paths must fail validation.

## API evolution

The binding records an API revision. When the API changes after the initial API Gate, `api-impact` analysis determines which bindings/slices need revalidation by affected `operationId` or by broader platform/project contract impact.

Unrelated evidence is preserved unless a cross-cutting change invalidates it.

## Web baseline

The Web baseline records React-specific decisions such as rendering mode, router, server-state library, form library, build tool and browser support.

A Web binding may contain only `WEB-*` inventory IDs.

## Android baseline

The Android baseline records Kotlin-specific decisions such as UI toolkit, architecture pattern, networking, local persistence, background work and minimum SDK.

An Android binding may contain only `APP-*` inventory IDs.

## Brownfield coexistence

For Brownfield, the platform baseline must preserve the working client until the replacement boundary is implemented, tested and explicitly approved.

It records current client surface, migration boundary, cutover trigger and rollback strategy.

Rule: **ALIGN, DO NOT REWRITE**.

## Repository layout

Recommended consumer layout:

```text
.blueprint/
  client-architecture/
    platform/
      web.json
      android.json
    slices/
      <slice-id>.web.json
      <slice-id>.android.json
```

A project may use another location when declared by its manifest.

## Gate evidence

A scoped `client_architecture_ready` PASS should identify:

- slice and platform;
- platform baseline artifact;
- slice binding artifact;
- inventory IDs;
- API revision/operationIds;
- schema + semantic validation evidence;
- human review evidence when project governance requires it.

File existence alone is insufficient.

## Compatibility

Blueprint 0.5 does not silently rewrite older consumers. Existing projects adopt the new composed contract through Compliance Review and explicit Blueprint version adoption. Reference pilots remain evidence, never hidden norm.
