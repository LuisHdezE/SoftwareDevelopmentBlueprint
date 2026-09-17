# Client Architecture Contract - Blueprint 0.5.4

## Purpose

Client Architecture is the mandatory pre-implementation contract for each Functional Interface Slice + platform. It translates executable inventory, Design System and authoritative API contracts into implementation decisions without forcing each slice to repeat platform-wide policy.

## Composition

The canonical contract remains:

**Platform Client Architecture Baseline + Slice Architecture Binding = Effective Client Architecture Contract**

The scoped gate remains `client_architecture_ready` for the exact `interface_slice + platform`.

Supported client platforms in Blueprint 0.5.4 are `web`, `android`, and `ios`. A PASS for one platform never authorizes another platform, even when implementation code is shared through a cross-platform strategy.

## Platform Client Architecture Baseline

`schemas/client-platform-architecture.schema.json` contains decisions reused across slices on the same platform/project:

- Design System/token paths;
- OpenAPI/API client and authorization boundary;
- auth/session/refresh/logout behavior;
- credential storage and secret-redaction rules;
- permission presentation with API authoritative;
- server-state/UI-state/cache strategy;
- forms, validation, 409/422/429 mapping;
- request correlation/observability;
- accessibility;
- unit/UI/integration/E2E strategy;
- API-backed offline policy;
- implementation guardrails;
- platform-specific implementation data for Web, Android, or iOS;
- Brownfield coexistence, cutover and rollback when applicable.

Framework, language and UI toolkit technology choices are consumer data. The Blueprint defines required architectural decisions and safety boundaries but does not mandate React, Kotlin, Swift, Flutter, React Native, Kotlin Multiplatform or any other implementation technology universally.

Legacy `0.5.0` client architecture documents remain schema-compatible while new/updated platform-bearing examples may use stable `0.5.4` provenance.

## Platform namespaces

Client architecture namespaces are platform-specific and must not be reinterpreted:

- `WEB-###` -> Web executable inventory;
- `APP-###` -> Android executable inventory, preserved as the existing legacy Android namespace;
- `IOS-###` -> iOS executable inventory.

The corresponding architecture identifiers are `CLIENT-WEB-*`, `CLIENT-ANDROID-*`, and `CLIENT-IOS-*`. Platform baseline identifiers follow `CLIENT-BASELINE-WEB-*`, `CLIENT-BASELINE-ANDROID-*`, and `CLIENT-BASELINE-IOS-*`.

A document whose declared platform and identifier namespace disagree is invalid.

## Slice Architecture Binding/Override

`schemas/client-architecture.schema.json` binds the exact slice to:

- platform-compatible `WEB-###`, `APP-###`, or `IOS-###` executable inventory IDs;
- the compatible platform baseline;
- OpenAPI path and API revision;
- canonical `operationId` values;
- required permissions;
- routes/navigation;
- required async/error/offline states;
- idempotent operations;
- slice-specific cache invalidation, offline override and testing notes;
- implementation guardrails.

The effective contract is evaluated from both artifacts. A binding may specialize platform decisions but cannot weaken API authority or other required guardrails.

## Visual references are conditional

Static visual references are not mandatory.

`visual_references.mode` has two intended uses:

- `none`: no approved static reference exists or is needed; `approved_reference_paths` must be empty.
- `approved_optional`: approved references are intentionally used and every path must resolve to a real versioned approved asset.

Fake placeholder paths are invalid. A project can progress through Client Architecture with zero mockups.

## API and inventory integrity

The binding consumes `EXECUTABLE_INVENTORY`, not the early scope baseline.

For the exact slice/platform:

- every inventory ID must exist and belong to that slice once that platform inventory is materialized;
- namespaces cannot cross Web, Android, or iOS;
- declared permissions must match executable inventory;
- declared routes must cover the inventory routes;
- every bound `operationId` must exist in current OpenAPI;
- slice `operationId` set must agree with the selected inventory;
- idempotency operations must be a subset of bound operations;
- API revision is explicit for impact/revalidation.

Blueprint 0.5.4 stabilizes iOS namespace and architecture contracts as part of the governed multiplatform model.

## Security and business guardrails

The effective architecture cannot disable:

- API-authoritative authorization;
- no invented API behavior;
- approved/executable inventory only;
- no hardcoded authoritative business data;
- high-risk mutation idempotency obligations from the API contract.

UI permission presentation improves UX but never replaces server enforcement.

## Brownfield

A Brownfield platform baseline requires coexistence metadata. Existing working UI/mobile behavior remains until the approved migration/cutover boundary. Replacement is slice-scoped and rollback is explicit.

## Validation

`scripts/validate-client-architecture.py` validates:

- Web, Android and iOS platform schemas/examples;
- Web, Android and iOS slice bindings;
- semantic compatibility between baseline and binding;
- platform-specific identifier and inventory namespaces;
- technology-neutral platform declarations;
- executable Web inventory and OpenAPI references;
- Functional Interface Slice -> Web Client Architecture binding already materialized in the repository;
- conditional visual references;
- negative cases for foreign namespaces, incompatible platform baselines, fake inventory IDs, operationIds, permissions and references;
- idempotency subset rules;
- `client_architecture_ready` catalog semantics.

A schema-valid file is not enough if its cross-artifact references are false.

## Completion

`client_architecture_ready = PASS` only when the Platform Client Architecture Baseline and Slice Architecture Binding compose into a valid effective contract for the exact slice/platform and the required evidence exists. One PASS cannot authorize another slice or platform.
