# Blueprint 0.5.3 - Optional Mobile Licensing

## Purpose

This stable 0.5.3 capability generalizes a reusable mobile licensing pattern discovered through a consumer pilot. It is product-agnostic and does not copy consumer-specific names, currencies, UI or business rules.

For every Android consumer, Blueprint discovery/requirements must explicitly answer:

> **Will this mobile application require a commercial license/activation?**

The answer is recorded as `capabilities.mobile_licensing: true|false`. Silence is not an answer for an Android project.

When `mobile_licensing = false`, no licensing profile is required, licensing checks may be projected as `N/A`, and `mobile_licensing_ready` is not instantiated/evaluated. It cannot block release.

When `mobile_licensing = true`, the default Blueprint mechanism is the profile defined here unless an approved Architecture Decision Record explicitly justifies another licensing strategy.

## Default licensing mechanism

The DEFAULT profile is:

`configurable trial -> expired read-only safety mode -> device-bound signed activation -> perpetual offline entitlement`

Core invariants:

1. Trial duration is configurable; the template default is 7 days.
2. Trial state evaluation and subsequent license verification work without a required backend.
3. Trial expiration never deletes, encrypts or makes existing user-owned business data inaccessible.
4. Expired users retain read-only access plus backup/export and activation/help flows.
5. A privacy-safe request code is derived from an approved device/application binding. Raw privileged hardware identifiers are not required.
6. The customer application verifies an asymmetric digital signature using public verification material only.
7. The private production signing key never ships in the customer application, source control, logs, screenshots or ordinary application backups.
8. A production activation is bound to the intended product and device binding and cannot activate another device/product.
9. Portable business-data backup does not clone or transfer a device-bound license.
10. Production and test/debug keys/namespaces are separated.
11. Signing-key recovery and rotation are designed before production release.
12. A separate issuer/admin boundary signs licenses. It may be another private mobile app or protected operator tool, but it is not hidden inside the customer application.
13. Distribution-channel policy is respected. Store-distributed builds use the entitlement/payment mechanism required by applicable store policy; direct distribution may use manual offline activation.
14. Fully offline trial enforcement is treated as best-effort anti-tamper, not an impossible-to-reset DRM guarantee.

## Default states

The minimum entitlement state model is:

- `TRIAL_ACTIVE`
- `TRIAL_EXPIRED_READ_ONLY`
- `LICENSED_PERPETUAL`
- `LICENSE_INVALID`

A project may add grace, subscription or time-limited states only through approved requirements/architecture.

## Required project decisions when enabled

Requirements must define trial duration and start condition, exact post-expiry functionality, activation/support journey, device replacement/reactivation policy, paid entitlement model, distribution channels and user-facing license status/activation interfaces.

Architecture/Security must define the canonical request code, signed payload/version, product/domain separation, device-binding derivation, signature algorithm and verification-key representation, key ID/version, recovery/rotation, local entitlement persistence, clock rollback policy, backup separation and issuer/customer interoperability fixtures.

The default cryptographic shape is asymmetric signing. A concrete algorithm is an Architecture decision based on supported platforms and current security guidance. A symmetric secret embedded in the customer app is not an acceptable production license-generation authority.

## Issuer boundary

When the default mechanism is used, the solution must have a **separate protected issuer**/admin boundary able to receive/paste/scan a request code, validate its format/version, create a canonical payload, sign it with protected production signing material, return activation as copy/share text and preferably QR-compatible data, record sanitized issuance history, separate test and production keys, and preserve an approved recovery/rotation path.

The issuer may be modeled as a separate Blueprint consumer when it is a separately deployed application.

## Mandatory test contract when enabled

The licensing capability is not release-ready until automated evidence covers, at minimum:

1. configurable trial duration;
2. exact trial-expiry boundary;
3. entitlement state transitions;
4. valid signed license acceptance;
5. modified payload rejection;
6. modified signature rejection;
7. wrong-device rejection;
8. wrong-product rejection;
9. unsupported license-version rejection;
10. production/test key separation;
11. license persistence across restart and supported upgrade with app data preserved;
12. backup/restore does not clone entitlement;
13. expired mode preserves read/view/backup/export while blocking protected mutations;
14. issuer-to-customer interoperability using canonical fixtures;
15. release/minified build verification;
16. best-effort clock rollback behavior according to the approved architecture;
17. malformed/corrupt activation handling without crash or unlock.

Security review must additionally prove by inspection/static evidence that the production private signing key is absent from the customer application artifact/repository.

## Conditional gate

`mobile_licensing_ready` applies only when `capabilities.mobile_licensing = true`.

It requires approved licensing requirements, architecture/security, private-key isolation, backup separation, issuer boundary, automated licensing tests, interoperability evidence and release-build verification.

The project Release Gate requires `mobile_licensing_ready` only when this capability applies. When licensing is disabled, the gate is omitted from the consumer status projection rather than recorded with an unsupported gate state.

## Consumer override

The default mechanism may be replaced only when the product/store/business model requires a different entitlement model, the alternative is explicitly documented in Requirements and Architecture, an ADR explains the deviation, security/data-safety invariants remain at least equivalent, and the alternative has equivalent automated negative/abuse-path tests.

`DEFAULT` therefore means strong starting policy, not architectural imprisonment.

## Release treatment

This document is part of stable Blueprint 0.5.3. The hardening semantics were accepted in PR #25 and promoted only through the separate 0.5.3 release boundary. Stable 0.5.2 and earlier release manifests remain immutable historical truth, and no consumer is automatically upgraded by this promotion.
