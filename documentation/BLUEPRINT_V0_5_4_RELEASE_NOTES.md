# Software Development Blueprint 0.5.4 Release Notes

## Release summary

Blueprint **0.5.4** is the stable promotion of the governed 0.5.4-dev hardening lane. It adds explicit iOS support and a cross-platform mobile strategy model while preserving platform isolation, API authority and the Android-only applicability boundary of Optional Mobile Licensing.

Stable counts:

- **29 phases**;
- **146 checks**;
- **19 gates**;
- **16 materialized skills**;
- **25 planned skills**.

Previous stable: **0.5.3**.

Pre-release `main`: `1f852ad831f6cb16b92c697fa97c46ac0e71049a`, the real merge SHA of PR #38 release closure.

## What becomes stable

### Explicit platform targets

Blueprint now models Web, Android and iOS as explicit client targets.

Namespaces remain platform-specific:

- `WEB-###` for Web;
- `APP-###` for Android;
- `IOS-###` for iOS.

`APP-###` remains the historical Android namespace and is not redefined as generic mobile.

### Mobile strategy

Projects may declare:

`mobile.strategy: native|cross_platform`

The strategy describes implementation/code organization only. It never enables Android or iOS implicitly and never allows one platform to reuse another platform's architecture acceptance, gate PASS, evidence, QA or human acceptance.

### iOS Client Architecture

0.5.4 adds technology-neutral iOS support to:

- project capabilities;
- Platform Client Architecture Baselines;
- Slice Architecture Bindings;
- executable interface namespaces;
- Functional Interface Slice and evidence scopes;
- status, blocker and API-impact artifacts;
- workflows, phase/check mappings and reusable skills.

Blueprint does not mandate SwiftUI, Flutter, React Native, Kotlin Multiplatform or another universal client framework.

### API-backed offline mobile

0.5.4 formalizes only **API-backed offline mobile**. Cache, queue, retry and temporary disconnected/degraded operation are supported while the API remains the authoritative business/security boundary.

API-less/local-authoritative mobile remains deferred because it requires a distinct hardening of API Gate, OpenAPI applicability, Functional DoD and QA semantics.

### Cross-artifact integrity and regression matrices

The release validates platform consistency across inventory, Client Architecture, Functional Interface Slice, evidence, status, blockers, API impacts and scoped gates.

A governed platform matrix covers positive and negative Web/Android/iOS, multi-target, native/cross-platform and API-backed offline combinations.

A separate Mobile Licensing regression matrix freezes its applicability boundary.

## Mobile Licensing compatibility

Optional Mobile Licensing remains **0.5.3-compatible** and Android-scoped:

- Web-only does not require a licensing decision;
- iOS-only does not require a licensing decision;
- Android requires `capabilities.mobile_licensing: true|false`;
- Android+iOS requires that decision because Android is enabled;
- `cross_platform` does not change applicability;
- when enabled, the existing licensing profile and `mobile_licensing_ready` contract remain applicable.

This release does **not** generalize Mobile Licensing to iOS.

## Platform acceptance remains independent

These gates continue to be evaluated for the exact `interface_slice + platform`:

- `client_architecture_ready`;
- `functional_slice_ready`;
- `visual_functional_review_pass`;
- `integration_qa_pass`.

A PASS for one platform never authorizes another platform, even when code is shared.

## Skills

0.5.4 contains **16 materialized skills**.

The release adds `dev-ios-client-architecture` and promotes changed client-execution skills to stable 0.5.4 provenance:

- `dev-android-client-architecture`;
- `dev-ios-client-architecture`;
- `dev-functional-interface-slice`.

Unchanged skills retain truthful compatible historical provenance. `dev-mobile-licensing` remains 0.5.3-compatible.

## Component provenance

Stable component provenance is intentionally mixed where contracts were not semantically changed:

- root release: `0.5.4`;
- project/status and platform-bearing client/experience contracts: `0.5.4`;
- catalogs/workflows changed by the hardening: `0.5.4`;
- changed Android/iOS client architecture and Functional Slice skills: `0.5.4`;
- Mobile Licensing: `0.5.3-compatible`;
- CI Runtime: `0.5.2-compatible`;
- Architecture Implementation Conformance: `0.5.1-compatible`;
- unchanged reference/compliance/design contracts retain prior compatible provenance.

Historical release manifests are not rewritten.

## Hardening lineage

The governed path to 0.5.4 was:

1. PR #31: governed 0.5.4-dev lane;
2. PR #32: platform capability model;
3. PR #33: iOS Client Architecture contracts;
4. PR #34: iOS workflows/catalogs/skills;
5. PR #35: cross-artifact iOS/platform integrity;
6. PR #36: governed platform matrix CI;
7. PR #37: Mobile Licensing regression boundary;
8. PR #38: release-candidate closure.

Exact merge SHAs are preserved in `documentation/BLUEPRINT_V0_5_4_RELEASE.json` and the historical release-candidate manifest.

## Consumer compatibility

There is **no automatic consumer upgrade**.

Every consumer remains on its explicitly declared Blueprint version until a separate Compliance Review classifies changes as KEEP / ADOPT / MIGRATE / DEFER / N/A, obtains human approval, applies repository-owned changes and performs impact-appropriate revalidation.

Publishing 0.5.4 does not mutate consumer repositories.

## Deferred scope

0.5.4 intentionally does not:

- define API-less/local-authoritative mobile semantics;
- generalize Mobile Licensing to iOS;
- mandate one cross-platform framework;
- automatically migrate consumers;
- force materialization of every planned skill.

## Release and tag governance

This release PR promotes the repository to `VERSION=0.5.4` and removes the development marker.

The tag `v0.5.4` is **not** authorized merely by opening or merging the release PR. It may be created only after:

1. exact-head CI succeeds for the release PR;
2. explicit human merge approval is given;
3. the PR is merged;
4. the real merge SHA returned by GitHub is verified on `main`;
5. stable post-merge CI succeeds on that exact SHA;
6. separate explicit human approval authorizes creation of `v0.5.4`.

A prospective `merge_commit_sha` shown for an open PR is never release evidence.
