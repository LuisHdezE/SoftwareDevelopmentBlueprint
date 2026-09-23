# Blueprint 0.5.5-dev · WebBlueprint non-normative pilot review

## Purpose

This Increment 6 pilot re-runs the authority-sensitive part of the WebBlueprint Compliance Review after the 0.5.5-dev hardening work introduced by the original 0.5.4 review.

It is intentionally non-normative. It does not mutate WebBlueprint, does not declare that WebBlueprint has adopted Blueprint 0.5.5, and does not convert pre-adoption evidence into a consumer version change.

## Frozen inputs

- SoftwareDevelopmentBlueprint evaluation line: `0.5.5-dev`
- Stable baseline preserved during hardening: `0.5.4`
- WebBlueprint repository: `LuisHdezE/WebBlueprint`
- WebBlueprint reviewed snapshot: `12cc52dabfe05ec9902f0ea6d73c7da6a19e1a74`
- Workflow mode: `greenfield`
- API authority mode: `api_optional`
- Web capability: enabled
- Authoritative database: absent
- Consumer adopted Blueprint version: `UNMANAGED`

The WebBlueprint SHA is the same snapshot that originated hardening issue #41. Increment 6 therefore compares the improved Blueprint against the exact consumer state that exposed the original contradiction.

## Scope

This is a selected 35-check pilot, not a claim that every stable Blueprint check has been audited.

The selected scope covers:

- product/scope evidence;
- requirements traceability;
- Web Interface Inventory migration readiness;
- architecture decision records;
- database/API applicability;
- client authority applicability;
- Functional Interface Slice authority and runtime evidence;
- visual/functional human review;
- Integration QA, including provider runtime transport.

The purpose is to prove whether 0.5.5-dev can represent WebBlueprint honestly and to separate Blueprint defects from remaining consumer adoption work.

## Doctor result

| Status | Count |
| --- | ---: |
| PASS | 18 |
| FAIL | 7 |
| N/A | 10 |
| BLOCKED | 0 |
| TOTAL | 35 |

Overall status: **FAIL**.

That FAIL is expected and useful. It no longer comes from forcing an API onto a frontend-only consumer. It comes from seven concrete WebBlueprint adoption debts that remain unmaterialized in the frozen snapshot.

## What 0.5.5-dev now represents truthfully

The pilot proves that a Web frontend-only/local-static/non-authoritative-mock consumer can be evaluated without invented infrastructure.

These obligations are now legitimate `N/A` under explicit `api_optional` authority:

- authoritative database;
- database migrations when no authoritative database exists;
- API auth strategy;
- API client strategy;
- API contract binding;
- Functional Slice API dependency resolution;
- real API integration;
- server auth/RBAC runtime;
- API permission fidelity in review;
- real API transport QA.

Crucially, Integration QA itself is not N/A. WebBlueprint instead satisfies the transport-specific obligation through `qa.provider_runtime_transport`, backed by the accepted Sign In browser/runtime evidence.

This is the behavior that Blueprint 0.5.4 could not express honestly.

## Grandfathered evidence that remains valid

Existing accepted WebBlueprint evidence is not discarded merely because it predates formal Blueprint adoption.

The pilot preserves PASS for the reviewed Sign In surface where the frozen snapshot already demonstrates the required behavior, including:

- product vision and scope;
- architecture decision records;
- no hardcoded authoritative business data in the Sign In Presentation boundary;
- no invented server capability claims;
- responsive runtime behavior;
- accessibility runtime behavior;
- executable tests;
- Style 1 fidelity;
- responsive and accessibility review;
- explicit product-owner human acceptance;
- functional QA;
- provider/browser runtime transport;
- integration QA;
- responsive QA;
- accessibility QA;
- browser E2E evidence.

These PASS results do not synthesize missing governance artifacts.

## Remaining WebBlueprint adoption debts

### 1. `requirements.traceability` · MISSING_EVIDENCE

WebBlueprint does not yet expose a governed requirements-ID layer and machine-readable requirements-to-implementation traceability artifact.

### 2. `ui.web_inventory` · CONTRACT_VIOLATION

A useful CORK page inventory already exists, but it is not yet projected into the Blueprint Interface Inventory contract with governed `WEB-###` identifiers.

This is migration of useful information, not a request to discard the existing inventory.

### 3. `ui.inventory_requirement_links` · MISSING_EVIDENCE

Without governed requirement IDs, the Interface Inventory cannot yet bind views to requirements.

### 4. `client.architecture_contract` · CONTRACT_VIOLATION

The accepted Sign In implementation already demonstrates strong feature boundaries, DTOs, application contracts, use cases and replaceable adapters. However, WebBlueprint has not yet materialized the governed Blueprint Client Architecture artifact.

The correct future action is to represent the accepted architecture, not rewrite it merely for compliance.

### 5. `functional.inventory_binding` · MISSING_EVIDENCE

The accepted Sign In slice cannot bind to governed Interface Inventory IDs until the `WEB-###` projection exists.

### 6. `functional.traceability` · MISSING_EVIDENCE

Implementation and QA evidence exist, but they are not yet linked end-to-end through governed requirement and inventory identifiers.

### 7. `qa.security` · MISSING_EVIDENCE

The frozen Sign In checkpoint records architecture/data boundaries, browser runtime checks, responsive/accessibility QA and acceptance, but it does not record a dedicated Integration QA security result.

Policy is not execution evidence. The pilot therefore fails closed instead of inferring a security PASS.

## Increment 6 composition finding

Running the real consumer exposed one final Blueprint-side composition gap after Increment 5: the Generic Compliance Doctor already understood API-phase N/A and provider runtime QA, but the workflow applicability overlay had not projected the Increment 3 client/slice authority decisions into check-level applicability.

Increment 6 reconciles that seam by making these API-specific client/slice/review checks N/A only when `api_optional` authority is explicit:

- `client.api_client_strategy`;
- `client.api_contract_binding`;
- `functional.api_dependencies_resolved`;
- `functional.real_api_integration`;
- `functional.auth_rbac_runtime`;
- `review.api_permission_fidelity`.

The general client, functional, review and QA obligations remain in force. API-optional is therefore not a bypass.

## Status template provenance reconciliation

Stable release 0.5.4 identifies Project and Status contracts as 0.5.4 provenance, while the active `templates/status.example.yaml` still declared `blueprint_version: 0.5.3`.

Increment 6 reconciles the active example to `0.5.4`. The stable status schema already supports `0.5.4`, so this is a provenance correction rather than a semantic weakening.

## Adoption decision

WebBlueprint remains **UNMANAGED / not yet adopted** during this pilot.

The pilot does not authorize a consumer mutation because:

1. Blueprint 0.5.5 is still a development hardening line, not a stable release;
2. the selected pilot still reports seven real consumer adoption debts;
3. consumer auto-upgrade is forbidden;
4. an explicit future WebBlueprint adoption PR is required after stable Blueprint release closure.

The next Blueprint step is Increment 7 release closure. Only after a stable 0.5.5 release exists should WebBlueprint receive its explicit adoption work, preserving accepted implementation and QA evidence while materializing the missing governance artifacts.

## Machine-readable artifacts

- Pilot input: `documentation/BLUEPRINT_V0_5_5_WEBBLUEPRINT_PILOT_MANIFEST.json`
- Doctor output: `documentation/BLUEPRINT_V0_5_5_WEBBLUEPRINT_PILOT_REPORT.json`
- Validator: `scripts/validate-webblueprint-pilot-v055-dev.py`

The validator requires the committed report to exactly equal the Generic Compliance Doctor output. Drift is a CI failure.
