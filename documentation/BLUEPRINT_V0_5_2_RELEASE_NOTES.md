# Software Development Blueprint 0.5.2 Release Notes

## Summary

Blueprint 0.5.2 is a focused execution-portability patch over 0.5.1.

It does not add a phase, check, gate, client lifecycle state or product-specific rule. It closes a governance/runtime gap exposed by a real private-repository consumer: exact-head CI evidence must remain mandatory even when GitHub-hosted runners are commercially or operationally unavailable.

The release introduces the canonical machine-readable CI runtime contract:

`schemas/ci-runtime.schema.json`

with supported strategies:

- `github_hosted`;
- `self_hosted`;
- `hybrid`.

Core invariants:

`CI evidence semantics != runner ownership`

`pre-execution infrastructure failure != test failure`

## Why this patch exists

CUSA-Digital PR #46 reached an approved Integration QA boundary and required a final exact-head regression before merge. New private-repository GitHub-hosted jobs terminated before any workflow step with no assigned runner, while public-repository GitHub-hosted execution remained available.

The failure was infrastructure/billing execution evidence, not product-test evidence. Waiving exact-head CI would weaken Blueprint governance, and making a private consumer public would expose project code merely to obtain free hosted execution.

The generalized solution is execution portability: preserve the same GitHub check/evidence semantics while allowing trusted project-controlled runners.

## Canonical CI runtime contract

0.5.2 stabilizes:

- `schemas/ci-runtime.schema.json`;
- `templates/ci-runtime.example.yaml`;
- `ci/blueprint-master.runtime.yaml`;
- `scripts/validate-ci-runtime.py`;
- `.github/workflows/blueprint-ci-runtime-validation.yml`.

The CI runtime artifact is CONDITIONAL. A consumer should materialize `.blueprint/ci-runtime.yaml` when it explicitly manages or overrides CI execution strategy, especially for `self_hosted` or `hybrid` execution.

## Evidence equivalence

Runner ownership does not weaken or strengthen a PASS by itself.

A valid CI PASS still requires, as applicable:

- workflow/check execution attached to the exact candidate commit SHA;
- repository-owned workflow definition;
- expected test/validation scope;
- required logs/artifacts;
- no substitution of untracked local commands for required GitHub check evidence;
- human review/merge/acceptance kept separate from CI success.

A job that fails before runner assignment or before any step executes is infrastructure evidence. It is neither a product/test failure nor a PASS.

## Self-hosted security boundary

A persistent self-hosted lane must execute trusted code only.

The stable contract requires or constrains:

- self-hosted selector labels including `self-hosted` and `blueprint`;
- fork pull requests denied or routed away from the self-hosted lane;
- no persistent repository secrets;
- least-privilege workflow permissions;
- workspace cleanup;
- automatic or explicitly operator-managed runner updates.

Repository-scoped runners remain the preferred baseline for personal/private repositories because they reduce blast radius.

## Docker independence

`capabilities.docker` continues to describe the consumer project/development solution contract.

It is not the runner infrastructure contract.

Therefore this is valid:

```text
project capabilities.docker = false
runner service_containers = true
runner container_engine = docker
```

Docker used by GitHub Actions service containers does not make Docker an application requirement.

The Blueprint Master itself uses a self-hosted profile without service containers or Docker.

## Proven execution

Hardening PR #22 moved the Blueprint Master validation workflows to:

`[self-hosted, linux, x64, blueprint]`

The exact approved hardening head `53e47858cb3b3a46a5801bfaee10e846909316be` executed six real GitHub Actions workflow families successfully on the registered self-hosted runner before merge.

The hardening merged to `main` as `c043bead93e9c4ad6c806576623f228dae239216`, which is the pre-release baseline for 0.5.2.

## Counts

Stable 0.5.2 contains:

- **28 phases**;
- **135 checks**;
- **18 gates**;
- **14 materialized skills**;
- **25 planned skills**.

No catalog count changes from 0.5.1.

## Component provenance

Promoted to 0.5.2:

- root `VERSION`;
- CI runtime schema/template;
- Blueprint Master runtime profile;
- project/status consumer schemas;
- canonical project/status examples;
- active release documentation and validation rules.

Reused from 0.5.1 without semantic modification:

- checks catalog;
- gates catalog;
- Architecture Implementation Conformance semantics.

Reused from 0.5.0 without semantic modification:

- phases catalog;
- Greenfield/Brownfield workflows;
- materialized skills and skill catalog;
- experience artifact schemas/contracts;
- reference-pilot registry contract.

Component provenance is preserved rather than mechanically relabeled.

## Historical evidence

0.5.2 does not rewrite 0.5.1, 0.5.0 or 0.4.0 history.

Existing accepted evidence remains valid when its claims remain true. Changing CI execution provider does not invalidate product evidence merely because runner ownership changes.

## Brownfield

Brownfield continues to use **ALIGN, DO NOT REWRITE**.

CI portability changes execution infrastructure, not application architecture or product behavior. Brownfield consumers do not gain authorization to containerize, rewrite or otherwise restructure a working system merely to adopt a runner strategy.

## Consumer adoption

There is **no automatic consumer upgrade**.

A consumer on 0.5.1 remains on 0.5.1 after publication of 0.5.2. Adoption requires:

1. live verification of Master and consumer;
2. Compliance Review `0.5.1 -> 0.5.2`;
3. KEEP / ADOPT / MIGRATE / DEFER / N/A classification;
4. explicit human approval;
5. dedicated adoption PR;
6. impact-appropriate revalidation.

CUSA-Digital is not modified by this release closure. Its PR #46 remains a separate consumer boundary.

## Release integrity

The stable tag is `v0.5.2`.

It must be created only after:

1. the release PR is explicitly approved and merged;
2. `main` is verified at the accepted merge commit;
3. post-merge CI passes on that exact commit.

CI evidence never substitutes for human merge authorization.
