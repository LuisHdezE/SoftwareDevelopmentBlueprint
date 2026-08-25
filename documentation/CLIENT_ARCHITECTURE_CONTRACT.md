# Client Architecture Contract — Blueprint 0.4.0-dev

## Purpose

The Client Architecture Contract is the repository-owned pre-implementation agreement for one approved `interface_slice` on one target platform.

It exists so a later AI can implement React or Android without inventing authentication behavior, permissions, API semantics, state ownership, error behavior, offline rules, testing boundaries or Brownfield replacement strategy.

The canonical schema is `schemas/client-architecture.schema.json`.

## Evaluation scope

`client_architecture_ready` is evaluated as `interface_slice_platform`.

A PASS for `ops-core + web` does not authorize implementation of:

- another interface slice;
- Android for the same slice;
- inventory items not included in that contract.

Implementation inherits no approval from neighboring slices.

## Required upstream gates

A client contract must not be approved unless:

1. `API_GATE = PASS` for the project;
2. `interface_inventory_ready = PASS`;
3. `design_system_ready = PASS`;
4. `visual_review_pass = PASS` for the exact target interface slice.

Approved visual references are inputs to the contract, not decoration.

## Required decisions

Every client architecture artifact defines:

### Visual binding

- inventory IDs included in the slice;
- approved mockup/reference paths;
- Design System and token paths;
- a hard rule that unapproved interfaces are not implemented.

### API contract binding

- OpenAPI path;
- exact operation IDs used by the slice;
- API as the authorization boundary;
- error contract;
- request-correlation header;
- idempotency header.

The client cannot invent endpoints, permissions, states, payload semantics or business transitions.

### Authentication lifecycle

The contract records:

- auth mechanism;
- access/refresh credential storage;
- refresh behavior and rotation;
- concurrent refresh policy;
- unauthenticated and forbidden behavior;
- logout behavior;
- secret logging prohibition.

Client storage must match the platform threat model. Tokens or credentials must not be moved into weaker storage merely for implementation convenience.

### Permissions and routing

Presentation may hide or disable unavailable actions, but API authorization remains authoritative.

Routing/navigation must define public/protected destinations and permission-aware navigation behavior.

### State and cache ownership

The contract separates server state from local UI state and records:

- server-state owner;
- local UI-state owner;
- cache strategy;
- mutation invalidation/refetch rules.

A client cache is never a new source of truth for authoritative business data unless an explicit offline model says so.

### Forms and API validation

Client validation improves feedback but cannot replace server validation.

The contract defines mappings for:

- API validation errors such as 422;
- conflicts such as 409;
- rate limiting such as 429;
- global Problem Details or the project's approved equivalent.

### Async, error and offline states

The contract explicitly classifies loading, empty, generic error, 401, 403, 404, 409, 422, 429 and offline as `REQUIRED` or `NOT_APPLICABLE`.

`NOT_APPLICABLE` must reflect the actual contract, not an attempt to avoid designing an inconvenient state.

### High-risk mutations and idempotency

Every operation requiring idempotency must be listed by canonical operation ID.

The client defines:

- key generation per user intent;
- replay handling;
- same-key/different-payload conflict handling;
- protection against duplicated optimistic/local effects.

### Observability

Request correlation is preserved from API response through support/error context. Client telemetry must redact secrets and follow the project's PII policy.

The client does not create a second audit system. Durable business/security audit remains server-side unless a documented architecture says otherwise.

### Accessibility

Accessibility is part of architecture, not a finishing pass.

The contract defines the target standard, keyboard/switch navigation, screen-reader/TalkBack behavior, focus management and minimum interactive target size.

### Testing

The contract defines unit, component/UI, integration and E2E responsibilities before implementation.

A strategy cannot claim runtime confidence using only mocked unit tests when the critical behavior depends on auth refresh, transport, persistence, navigation or API error mapping.

## Web profile

For Blueprint's default web stack, the platform section records React plus:

- rendering mode;
- router;
- server-state library;
- form library;
- build tool;
- browser-support policy.

The schema does not permit an Android platform block in a web contract.

## Android profile

For Blueprint's default Android stack, the platform section records Kotlin plus:

- Jetpack Compose, Views or approved hybrid toolkit;
- architecture pattern;
- networking library;
- local persistence;
- background work strategy;
- minimum SDK.

The schema does not permit a web platform block in an Android contract.

## Offline model

Offline capability is explicit, even when unsupported.

Allowed architecture modes are:

- `unsupported`;
- `degraded`;
- `read_only`;
- `queued_writes`;
- `full_offline`.

The storage and synchronization/conflict policy must be recorded. Offline queued writes must not silently bypass API authorization, idempotency or server-side business rules.

## Brownfield coexistence

When `mode = brownfield`, the contract must include a coexistence block.

The existing working client remains available until the approved replacement boundary is implemented, tested and its cutover is explicitly approved.

The contract must state:

- current client path/surface;
- migration boundary;
- cutover trigger;
- rollback strategy;
- that removal occurs only after release approval.

Rule: **ALIGN, DO NOT REWRITE**.

A new client slice is not permission to remove unrelated working behavior.

## Implementation guardrails

Every contract asserts:

- no new API behavior invented in the client;
- no authorization bypass;
- approved inventory only;
- high-risk mutations follow API idempotency requirements.

These are normative assertions, not optional prose.

## Repository layout

Recommended consumer layout:

```text
.blueprint/
  client-architecture/
    <slice-id>.web.json
    <slice-id>.android.json
```

The project may use another path if `project.yaml` declares `artifact_locations.client_architecture_root`.

## Gate evidence

A scoped `client_architecture_ready` PASS should identify:

- interface slice;
- platform;
- architecture artifact path;
- applicable inventory IDs;
- validation evidence/CI run;
- review/approval evidence when required by project governance.

File existence alone is not sufficient if the file does not validate or its scoped gate has not passed.

## Compatibility

Blueprint v0.4 adds this contract without silently migrating older consumers. Existing v0.3 projects adopt it only through Compliance Review.

Reference pilots can demonstrate compatibility or expose gaps, but remain non-normative.
