---
id: dev-mobile-licensing
title: Mobile Trial and Offline License Activation
version: 0.5.3-dev
status: materialized
category: mobile_licensing
applies_to:
  - greenfield
  - brownfield
phases:
  - discovery
  - requirements_domain
  - architecture_security_data
  - client_architecture
  - functional_interface_slice
  - integration_qa
  - release_gate
canonical_references:
  - BLUEPRINT.md
  - documentation/BLUEPRINT_V0_5_3_MOBILE_LICENSING.md
  - schemas/mobile-licensing.schema.json
  - templates/mobile-licensing.example.yaml
  - catalog/checks.yaml
  - catalog/gates.yaml
---

# Mobile Trial and Offline License Activation

## Purpose

Apply Blueprint's optional mobile licensing capability safely and consistently. Every Android project must explicitly decide whether licensing applies. When it does, this skill provides the default device-bound offline trial/activation mechanism and its mandatory test/security obligations without leaking product-specific assumptions into Blueprint Core.

## When to Use

Use when the target includes Android and `capabilities.mobile_licensing = true`. During Discovery/Requirements, use it to close the licensing decision and user journey. During Architecture and implementation, use it to define and verify the entitlement boundary. During QA/Release, use it to enforce the negative-path and private-key-isolation evidence.

Do not use it when `capabilities.mobile_licensing = false`; in that case licensing artifacts/checks/gate are N/A.

## Inputs

- Approved product/commercial model and distribution channels.
- Trial duration and expiration behavior.
- Android package/signing/device-binding constraints.
- Client Architecture and backup/restore policy.
- Security architecture, threat assumptions and release build configuration.
- Issuer/admin boundary and signing-key custody/recovery plan.
- `schemas/mobile-licensing.schema.json` and project licensing profile.

## Procedure

1. Ask explicitly whether the Android application requires a commercial license/activation. Record `capabilities.mobile_licensing` as `true` or `false`; do not infer the answer from monetization language alone.
2. If false, mark the licensing branch N/A and continue normal Blueprint delivery.
3. If true, start from `strategy: offline_signed_device_bound_trial` unless an approved ADR documents a justified alternative.
4. Define the trial duration, start condition, visible status, expiration boundary and post-expiration access. Preserve user-owned data: expiration may block protected mutations, but it must not delete/encrypt business data or block backup/export.
5. Define a privacy-safe Request Code derived from an approved app/device binding. Do not require privileged hardware identifiers and do not expose raw identifiers as commercial codes when a derived representation suffices.
6. Define a versioned canonical license payload containing at least product/domain identity, device binding, entitlement type, license serial/ID, issued-at value and signing-key ID/version.
7. Use asymmetric digital signatures. Ship only public verification material in the customer application. Never embed a private signing key or symmetric generation secret capable of minting production licenses in the customer app.
8. Keep production and test/debug signing namespaces and key material separate.
9. Define the issuer/admin boundary separately. It may be another private application or protected operator tool. It validates Request Codes, constructs canonical payloads, signs them, returns copy/share/QR-friendly activation data and records sanitized issuance history.
10. Define signing-key custody, recovery and rotation before production release. A phone-local non-exportable key with no recovery plan is not sufficient for a long-lived commercial product.
11. Keep portable business backup independent from entitlement. Restoring business data to another device must not silently clone a device-bound license.
12. Treat fully offline trial anti-tamper as best-effort. Define clock rollback/reinstall/rooted-device behavior without claiming that a device owner can be made cryptographically powerless without an external authority.
13. Keep distribution policy explicit. Direct/sideload distribution may use the manual offline mechanism; store-distributed paid unlocks must use the payment/entitlement path required by applicable store policy.
14. Implement licensing behind an entitlement boundary so domain/business logic does not depend directly on cryptography, store APIs or issuer transport.
15. Implement and automate every mandatory licensing test in the canonical contract: configurable trial, exact expiration, state transitions, valid signature, tampered payload/signature, wrong device/product, unsupported version, prod/test separation, persistence, backup non-cloning, expired read-only safety, issuer interoperability, release build, clock rollback and malformed activation.
16. Add static/repository/release evidence proving the production private signing key is absent from the customer application and repository.
17. Run the licensing profile validator and project test suite on the exact final candidate SHA. Treat missing negative-path evidence as incomplete, not PASS.
18. Evaluate `mobile_licensing_ready` only when the capability is enabled and only after requirements, architecture/security, issuer boundary, automated tests and release-build verification are evidenced.

## Outputs

- Explicit `mobile_licensing` applicability decision.
- Schema-valid mobile licensing profile when enabled.
- Approved trial/activation requirements and UI journey.
- Device-binding/request-code and signed-license architecture.
- Separate issuer/admin boundary with key custody/recovery/rotation policy.
- Automated positive, negative, tamper, interoperability and release-build tests.
- Evidence that customer artifacts contain no production private signing key.
- Conditional `mobile_licensing_ready` result.

## Stop Conditions

- Android licensing applicability has not been explicitly decided.
- A production private signing key or minting-capable shared secret would ship in the customer application.
- Trial expiration would delete, encrypt or make user-owned data/backup inaccessible.
- A backup can clone a device-bound entitlement to another device.
- Signing-key recovery/rotation is undefined for a production release.
- Issuer/customer canonical payloads are not covered by interoperability fixtures.
- Negative-path tests for tampering, wrong device/product or unsupported version are missing.
- The project claims perfect offline anti-tamper against a device owner.
- Store policy requirements are bypassed by hardwiring manual activation into every distribution channel.

## Guardrails

- Licensing is CONDITIONAL, never universal.
- The applicability question is mandatory for Android projects even when the answer is no.
- The canonical mechanism is DEFAULT, so an approved ADR may replace it; security/data-safety and test coverage may not be weakened silently.
- Asymmetric verification material in the customer application is acceptable; private production signing material is not.
- Licensing state is not business-data authority and must not contaminate domain records or portable backups.
- Trial expiration is a commercial state transition, not permission to hold user data hostage.
- Generated activation data, test fixtures and issuer history must not expose private keys or unnecessary personal/business data.

## Canonical References

- `BLUEPRINT.md`
- `documentation/BLUEPRINT_V0_5_3_MOBILE_LICENSING.md`
- `schemas/mobile-licensing.schema.json`
- `templates/mobile-licensing.example.yaml`
- `catalog/checks.yaml`
- `catalog/gates.yaml`

## Completion Signal

Complete only when Android licensing applicability is explicit and, if enabled, the project has a schema-valid profile, approved requirements and architecture, a separate protected issuer/signing boundary, recoverable/rotatable production key custody, business-data/license separation, the complete automated licensing test matrix on the exact release candidate, private-key absence evidence for the customer artifact, and a truthful `mobile_licensing_ready = PASS`.