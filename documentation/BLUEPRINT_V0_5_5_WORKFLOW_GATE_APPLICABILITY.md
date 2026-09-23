# Blueprint 0.5.5-dev · Workflow & Gate Applicability

## Status

Development hardening contract for **Increment 2** of issue #41.

Stable `VERSION` remains `0.5.4`. This document does not promote a release and does not mutate any consumer repository.

## Purpose

Blueprint 0.5.4 has one strict server/API road:

`Architecture → API Contract → API Implementation → OpenAPI → Postman → API QA → API Gate → Client`

That remains correct for `authority.api.mode=api_backed`.

Increment 1 added an explicit project authority decision. Increment 2 now uses that decision to resolve whether server/data/API phases, checks and gates are applicable without inventing artifacts for a legitimate `api_optional` project.

## Governing source

Applicability is derived only after the project passes the 0.5.5-dev API Authority contract:

`authority.api.mode = api_backed | api_optional`

Absence of this declaration is an error. Applicability is never inferred from folder names, the presence of React, or a null backend alone.

Machine-readable overlay:

`catalog/workflow-gate-applicability-v055-dev.yaml`

Schema:

`schemas/workflow-gate-applicability-v055-dev.schema.json`

Validator:

`scripts/validate-workflow-applicability-v055-dev.py`

## API-backed profile

`api_backed` inherits the entire stable 0.5.4 workflow exactly.

No phase, check or gate is classified `N/A`.

The validator proves, for both Greenfield and Brownfield, that:

- workflow sequence is semantically equivalent to the stable sequence;
- workflow gate bindings are unchanged;
- every stable gate keeps the same `require_all` and `require_if_applicable` sets;
- the existing API Gate remains mandatory before executable client delivery.

This is the non-regression wall for existing API-backed consumers.

## API-optional profile

The following API-only phases are `N/A`:

- `api_contract_design`
- `api_implementation`
- `openapi_validation`
- `postman_contract`
- `api_qa`
- `api_gate`

Their checks become `N/A` automatically.

Within `architecture_security_data`, these API-specific checks are also `N/A`:

- `api.auth_strategy`
- `api.error_contract`
- `api.versioning_policy`

When `stack.database` is `null`, these database obligations are `N/A`:

- `data.schema_migrations`
- `data.authoritative_database`

`data.architecture` remains required. An API-optional product still has to explain where its data comes from and which boundary owns it.

If an API-optional project explicitly declares a database, the two database checks return automatically. `api_optional` therefore means “no authoritative API requirement”, not “no engineering rigor”.

The corresponding API-only gates are `N/A`:

- `api_contract_ready`
- `api_implemented`
- `openapi_valid`
- `postman_ready`
- `api_qa_pass`
- `api_gate`

After `architecture_security_data`, the effective workflow therefore routes directly to `interface_inventory`.

## Fail-closed behavior

The development resolver rejects or detects drift when:

- `authority.api.mode` is absent;
- an API-backed profile attempts to classify any stable API obligation `N/A`;
- an API-optional profile leaves the API Gate active;
- an API-optional profile silently restores an API-only phase;
- a database-absent API-optional profile inconsistently keeps the authoritative-database requirement;
- an effective gate still requires a check already classified `N/A`.

Increment 1 remains responsible for preventing API-optional manifests from claiming remote authoritative business data, server auth/authorization, permission enforcement, remote persistent mutations or backend-only invariants.

## Scope boundary

This increment deliberately does **not** make Client Architecture, Functional Interface Slice or Integration QA API-optional yet.

Those contracts remain strict until:

- Increment 3: client architecture and slice authority;
- Increment 4: integration QA authority matrix.

This sequencing prevents a broad “skip API” switch from weakening downstream quality gates before their schemas can express the correct alternative semantics.

## Status representation during hardening

Stable `schemas/status.schema.json` is intentionally unchanged in Increment 2.

It already supports `N/A` for phases and checks but does not yet support `N/A` for project/scoped gates. During hardening, the applicability overlay is the machine-readable authority for gate applicability. Stable status schema promotion is deferred to release closure after all dependent contracts are reconciled.

This avoids partially promoting 0.5.5 semantics into stable 0.5.4.

## Greenfield and Brownfield

The same authority model applies to both workflows.

Brownfield still preserves all existing observed-state, coexistence and cutover obligations. API-optional only removes obligations that would otherwise require inventing a server/API baseline that the target product does not possess.

## Consumer adoption

No consumer auto-adopts this development contract.

WebBlueprint remains governed by its current repository rules until:

1. the 0.5.5 hardening lane is complete;
2. a stable release is explicitly approved;
3. a new Compliance Review is executed;
4. an adoption PR is explicitly approved in WebBlueprint.
