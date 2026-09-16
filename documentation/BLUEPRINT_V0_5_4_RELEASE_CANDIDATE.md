# Software Development Blueprint 0.5.4 Release Candidate

## Status

This document closes the governed `0.5.4-dev` hardening work and prepares the repository for a separate final release PR.

It does **not** declare Blueprint 0.5.4 stable. During this checkpoint:

- root `VERSION` remains `0.5.3`;
- `DEVELOPMENT_VERSION` remains `0.5.4-dev`;
- no stable `documentation/BLUEPRINT_V0_5_4_RELEASE.json` exists;
- no `v0.5.4` tag is authorized or created.

The hardening feature boundary is complete through `main@965e2c060e2193d50d0937fd425802fb1b193c60`, the real merge SHA of PR #37.

## Candidate counts

The governed 0.5.4-dev candidate contains:

- **29 phases**;
- **146 checks**;
- **19 gates**;
- **16 materialized skills**;
- **25 planned skills**.

These counts are validated from the active catalogs and are recorded in the release-candidate manifest rather than copied only as prose.

## Hardening lineage

The feature hardening was split into independently approved increments:

1. PR #31 opened the governed 0.5.4-dev lane.
2. PR #32 added the platform capability model with explicit iOS and `mobile.strategy`.
3. PR #33 added technology-neutral iOS Client Architecture contracts.
4. PR #34 added iOS workflow, catalog, check and skill support.
5. PR #35 enforced cross-artifact platform coherence and exact namespace/evidence isolation.
6. PR #36 added the governed platform matrix and dedicated CI validation.
7. PR #37 locked the Mobile Licensing applicability regression boundary.

The exact merge SHAs for all seven increments are frozen in `documentation/BLUEPRINT_V0_5_4_RELEASE_CANDIDATE.json`.

## Platform contract

0.5.4 formalizes three explicit client targets:

- Web with `WEB-###` inventory namespace;
- Android with the existing `APP-###` namespace;
- iOS with `IOS-###`.

`APP-###` remains Android-specific for compatibility and must never be reinterpreted as a generic mobile namespace.

Mobile projects declare `mobile.strategy` as either `native` or `cross_platform`. The strategy describes implementation/code organization only. It does not enable a target that is not explicitly declared and cannot collapse platform-scoped architecture acceptance, evidence, QA, gates or functional acceptance.

## Independent platform acceptance

The composed client architecture contract remains:

`Platform Baseline + Slice Architecture Binding/Override = Effective Client Architecture Contract`

The following gates remain independently evaluated for each applicable `interface_slice + platform`:

- `client_architecture_ready`;
- `functional_slice_ready`;
- `visual_functional_review_pass`;
- `integration_qa_pass`.

A Web PASS cannot satisfy Android or iOS. Android evidence cannot satisfy iOS, and shared cross-platform implementation cannot be used to manufacture shared acceptance.

## iOS support

The candidate adds iOS to the project capability model, client architecture baselines/bindings, executable inventory namespaces, functional slices, evidence scopes, status/gate/blocker/API-impact artifacts, workflows, implementation phase mapping, inventory checks and reusable skills.

Framework and language choices remain consumer-owned. Blueprint does not mandate SwiftUI, Flutter, React Native, Kotlin Multiplatform or another universal implementation technology.

## Offline boundary

The 0.5.4 candidate formalizes only **API-backed offline mobile**. Cache, queue, retry and temporary disconnected/degraded operation are valid while the API remains the authoritative business/security boundary.

API-less/local-authoritative mobile remains deferred. Solving it would require a separate hardening of API Gate, OpenAPI applicability, Definition of Done and QA semantics. No consumer should invent an API merely to satisfy the current Blueprint.

## Mobile Licensing compatibility

Mobile Licensing keeps its stable 0.5.3 provenance and Android applicability boundary:

- Web-only does not require a licensing decision;
- iOS-only does not require a licensing decision;
- Android requires an explicit `capabilities.mobile_licensing: true|false` decision;
- Android+iOS requires the decision because Android is enabled;
- `cross_platform` does not change applicability;
- when enabled, the existing licensing profile and `mobile_licensing_ready` evidence contract remain applicable.

This candidate does not generalize Mobile Licensing to iOS.

## Regression coverage

The hardening includes a governed platform matrix covering positive and negative combinations for Web, Android, iOS, multi-target, native/cross-platform and API-backed offline semantics.

A dedicated Mobile Licensing regression matrix separately proves the Android-only decision boundary, including legacy-compatible Android manifests.

The matrices are CI-enforced. They complement, rather than replace, human review and exact-SHA merge governance.

## Provenance

During this candidate stage:

- stable root identity remains 0.5.3 until promotion;
- development platform-bearing contracts use 0.5.4-dev provenance;
- Mobile Licensing remains 0.5.3-compatible;
- CI Runtime remains 0.5.2-compatible;
- Architecture Implementation Conformance remains 0.5.1-compatible;
- unchanged historical reference/compliance/design contracts retain their prior compatible provenance.

Historical stable release manifests are immutable and are not rewritten to pretend later adoption.

## Consumer adoption

There is no automatic consumer upgrade.

A consumer adopts a future stable 0.5.4 only through Compliance Review, explicit KEEP / ADOPT / MIGRATE / DEFER / N/A classification, human approval, repository-owned changes and impact-appropriate revalidation.

The existence of this candidate changes no consumer by itself.

## Final release PR requirements

The next increment is a distinct release promotion. It must:

1. start from the exact approved post-closure `main` SHA;
2. promote active 0.5.4-dev contracts to stable `0.5.4` provenance where semantically appropriate;
3. set root `VERSION` to `0.5.4`;
4. remove the development marker;
5. create stable `BLUEPRINT_V0_5_4_RELEASE.json` and release notes;
6. update the normative `BLUEPRINT.md` and active human documentation to stable 0.5.4 identity;
7. pass stable validation on the exact release PR head;
8. merge only after explicit human approval;
9. capture the real merge SHA returned by GitHub and rerun stable validation on that exact `main` commit;
10. create `v0.5.4` only after a separate explicit human approval.

A prospective `merge_commit_sha` shown for an open PR is never accepted as release evidence.

## Deferred work

The following remain outside 0.5.4:

- API-less/local-authoritative mobile semantics;
- generalizing Mobile Licensing to iOS;
- mandating one cross-platform framework;
- automatic consumer migration;
- forced materialization of every planned skill.
