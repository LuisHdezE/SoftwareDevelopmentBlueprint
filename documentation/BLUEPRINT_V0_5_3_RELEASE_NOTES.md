# Software Development Blueprint 0.5.3 Release Notes

## Summary

Blueprint 0.5.3 is a focused mobile-governance hardening release over 0.5.2. It stabilizes **Optional Mobile Licensing** as a reusable conditional capability without turning commercial activation into a universal requirement.

The hardening was accepted through PR #25 and merged to `main` as `5524f9b34f8328e3e6a9c88852fc8df70d9e437e`. That commit is the pre-release baseline for this closure.

Stable 0.5.3 contains **28 phases, 145 checks, 19 gates, 15 materialized skills and 25 planned skills**.

## What changes

Android consumers must explicitly answer whether commercial mobile licensing applies. The canonical project capability is:

`capabilities.mobile_licensing: true|false`

For non-Android consumers, the capability is not forced. For Android consumers, silence is no longer accepted as a valid applicability decision.

When licensing is disabled, licensing artifacts and checks are not required and `mobile_licensing_ready` does not block release. When enabled, the default strategy is:

`configurable trial -> expired read-only safety mode -> device-bound signed activation -> offline entitlement`

A consumer may adopt another strategy only through an approved architecture decision with equivalent or stronger security, data-safety and verification evidence.

## Default safety invariants

The default profile preserves user-owned data after trial expiry. Expiration may block protected business mutations, but read access, backup/export and activation/help remain available.

The customer application verifies asymmetric signatures with public verification material only. A production private signing key or minting-capable shared secret must never ship in the customer application or its repository.

Portable business-data backup is separated from device-bound entitlement. Restoring business data on another device must not silently clone a license.

The signing authority belongs to a **separate protected issuer** boundary with production/test key separation, recovery and rotation defined before release.

Fully offline anti-tamper remains best-effort. Blueprint does not claim that a device owner can be made cryptographically powerless without an external authority.

## Mandatory test contract

When mobile licensing is enabled, **17** canonical test obligations are required:

1. configurable trial duration;
2. exact trial-expiry boundary;
3. entitlement transitions;
4. valid signature acceptance;
5. tampered payload rejection;
6. tampered signature rejection;
7. wrong-device rejection;
8. wrong-product rejection;
9. unsupported-version rejection;
10. production/test key separation;
11. restart and supported-upgrade persistence;
12. backup does not clone entitlement;
13. expired read-only data safety;
14. issuer/customer interoperability;
15. exact release-build verification;
16. approved clock-rollback behavior;
17. malformed activation rejection without crash or unlock.

These tests are not decorative documentation. The `mobile_licensing_ready` gate requires evidence that the applicable contract has actually been satisfied.

## New gate and skill

0.5.3 adds the project-scoped conditional gate:

`mobile_licensing_ready`

It becomes a prerequisite of `release_gate` only when `capabilities.mobile_licensing = true`.

The reusable procedure is materialized as:

`skills/dev-mobile-licensing/SKILL.md`

The skill remains product-agnostic. Product-specific license formats, business rules, customer data, currencies and distribution details stay in the consumer repository.

## Machine-readable contracts

Promoted to stable 0.5.3:

- `schemas/project.schema.json`;
- `schemas/status.schema.json`;
- `schemas/mobile-licensing.schema.json`;
- `templates/project.example.yaml`;
- `templates/status.example.yaml`;
- `templates/mobile-licensing.example.yaml`;
- `catalog/checks.yaml`;
- `catalog/gates.yaml`;
- `catalog/skills.yaml`;
- `workflows/greenfield.yaml`;
- `workflows/brownfield.yaml`;
- `skills/dev-mobile-licensing/SKILL.md`.

The release validators include dedicated positive and negative validation for the mobile licensing profile and its project applicability rules.

## Preserved provenance

0.5.3 does not mechanically relabel unchanged contracts.

The CI Execution Portability contract remains compatible with its stable 0.5.2 provenance. Architecture Implementation Conformance remains compatible with its stable 0.5.1 provenance. Unchanged phases, reference-pilot contracts and experience schemas remain compatible with their 0.5.0 provenance.

Historical manifests for 0.4.0, 0.5.0, 0.5.1 and 0.5.2 remain historical truth.

## Scope intentionally not included

This release does not solve the broader API-less/local-authoritative Android applicability gap. A local-authoritative offline consumer may document a compatibility exception until that capability is generalized in a separate Blueprint hardening boundary.

This release also does not create a consumer's issuer application, define a universal signature algorithm, force a payment provider, or automatically retrofit licensing into existing products.

## Consumer adoption

There is **no automatic consumer upgrade**.

A consumer remains on its declared Blueprint version until it performs a dedicated Compliance Review, classifies changes as KEEP / ADOPT / MIGRATE / DEFER / N/A, receives explicit human approval, changes its own versioned contracts and performs impact-appropriate revalidation.

In particular, publishing 0.5.3 does not mutate GestioApp, CUSA-Digital or any other consumer.

## Release integrity

The stable tag will be `v0.5.3`.

It is created only after the release PR is explicitly approved and merged, the approved tree is verified on `main`, and post-merge CI succeeds on that exact stable commit. CI evidence never substitutes for human merge authorization.
