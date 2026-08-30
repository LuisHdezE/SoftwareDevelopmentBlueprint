# Blueprint 0.5.2 CI Execution Portability Hardening

## Status

Accepted hardening boundary promoted into stable Blueprint `0.5.2`.

- stable base before hardening: `0.5.1`
- promoted release: `0.5.2`
- hardening PR: #22
- hardening merge: `c043bead93e9c4ad6c806576623f228dae239216`
- approved hardening head: `53e47858cb3b3a46a5801bfaee10e846909316be`
- source finding: private-repository GitHub-hosted runners became unavailable before workflow execution while exact-head CI remained mandatory
- consumer auto-adoption: **disabled**
- phases added: **0**
- gates added: **0**
- checks added: **0**
- new machine-readable contract: `schemas/ci-runtime.schema.json`

This boundary does not rewrite stable `v0.5.1` history. It adds provider-execution portability so exact-head CI evidence remains mandatory without coupling Blueprint governance to paid GitHub-hosted runner availability.

## 1. Problem

Blueprint requires:

`verified main -> short-lived branch -> exact-head validation -> PR -> human decision -> verified merge`

That governance rule is preserved. The missing distinction was between the semantic requirement for CI evidence and the commercial/runtime mechanism that executes it.

CUSA-Digital PR #46 exposed the gap. Its private-repository hosted jobs terminated before any workflow step and without runner assignment after the hosted allowance became unavailable. Such an event says nothing about product correctness, but it also cannot be treated as PASS.

Therefore:

`CI evidence semantics != runner ownership`

and:

`pre-execution infrastructure failure != test failure`

## 2. Canonical CI runtime contract

Stable 0.5.2 defines:

`schemas/ci-runtime.schema.json`

with canonical example:

`templates/ci-runtime.example.yaml`

The artifact is CONDITIONAL. A consumer SHOULD materialize `.blueprint/ci-runtime.yaml` when it explicitly manages or overrides CI execution strategy, especially for `self_hosted` or `hybrid` execution.

Supported strategies:

- `github_hosted`: provider-hosted workflow execution;
- `self_hosted`: trusted project-controlled workflow execution;
- `hybrid`: a documented combination of provider-hosted and trusted self-hosted lanes.

The current stable contract targets GitHub Actions orchestration. The evidence invariants remain conceptually portable to future orchestrators.

## 3. Self-hosted runner baseline

For the canonical Linux/x64 GitHub Actions profile:

```text
runs-on: [self-hosted, linux, x64, blueprint]
```

The `blueprint` label distinguishes intentionally prepared Blueprint CI machines from arbitrary self-hosted runners.

A persistent self-hosted runner MUST:

- execute trusted repository code only;
- deny fork pull requests on the self-hosted lane or route them to a provider-hosted lane in a hybrid strategy;
- avoid persistent repository secrets on disk;
- keep workflow token permissions least-privilege;
- clean working state between jobs;
- stay updated through GitHub automatic runner updates or explicit operator-managed updates;
- preserve exact-head check-run evidence in GitHub.

Repository-scoped runners are the preferred baseline for personal/private repositories because they reduce blast radius.

## 4. Docker is runner infrastructure, not project capability

The existing consumer capability:

`capabilities.docker`

describes whether Docker belongs to the project/development solution contract.

It MUST NOT be overloaded to describe CI host infrastructure.

A self-hosted Linux runner MAY require Docker Engine solely because GitHub Actions `services:` use containers. In that case:

```text
project capabilities.docker = false
runner service_containers = true
runner container_engine = docker
```

is valid and non-contradictory.

Invariant:

`runner container engine != application Docker requirement`

## 5. Evidence equivalence

Self-hosted CI is acceptable only when it preserves the same governance semantics as hosted CI.

PASS evidence still requires, as applicable:

- workflow/check execution attached to the exact candidate commit SHA;
- repository-owned workflow definition;
- expected test/validation scope;
- required logs and artifacts;
- no substitution of local untracked commands for required GitHub check evidence;
- human approval kept separate from CI success.

A self-hosted PASS is not weaker evidence merely because the machine is project-controlled.

Conversely, a job that terminates before a runner is assigned or before any step executes is infrastructure evidence, not a product/test failure and not a PASS.

## 6. Security boundary

Self-hosted runners execute repository workflow code on a persistent machine, so their trust boundary is stricter than disposable provider-hosted VMs.

Stable 0.5.2 requires trusted-code-only self-hosted execution, ephemeral orchestrator-provided secrets, least-privilege permissions and workspace hygiene.

Administrative/root privileges SHOULD NOT be granted to arbitrary workflow steps. Dependencies requiring privilege SHOULD be provisioned during runner bootstrap where practical.

## 7. Runtime reproducibility

A self-hosted runner is an execution substrate, not undocumented snowflake state.

The project-owned CI runtime contract records at minimum:

- orchestrator and strategy;
- runner scope;
- OS and architecture;
- selector labels;
- persistence model;
- service-container requirement and container engine;
- security policy;
- evidence invariants;
- cleanup/update policy.

Workflows SHOULD verify critical runtime assumptions before expensive test execution.

## 8. Proven hardening execution

The Blueprint Master was the first adopter.

Its validation workflows moved to:

`[self-hosted, linux, x64, blueprint]`

The exact approved head `53e47858cb3b3a46a5801bfaee10e846909316be` ran six real workflow families successfully on the registered self-hosted runner:

- Blueprint CI Runtime Validation;
- Blueprint Schema Validation;
- Blueprint Release Validation;
- Blueprint Skill Validation;
- Blueprint Pilot Compliance Validation;
- Blueprint Client Architecture Validation.

Only after that exact-head evidence and explicit human approval did PR #22 merge as `c043bead93e9c4ad6c806576623f228dae239216`.

## 9. Brownfield and consumer adoption

This hardening does not mutate any consumer automatically.

Existing consumers remain valid on their declared Blueprint version. Adoption of stable 0.5.2 requires a separate Compliance Review, explicit approval and consumer PR.

CI portability changes execution infrastructure. It does not authorize application rewrites, invented Docker requirements, weakened gates or erased historical evidence.

## 10. Release boundary

PR #22 was the semantic hardening boundary. The subsequent release-closure boundary promotes the coherent repository state to root `VERSION = 0.5.2`, stable project/status consumer declarations, stable CI runtime identity and release documentation.

The stable tag `v0.5.2` is created only after the release PR is approved and merged, `main` is reverified and post-merge CI passes on the exact stable SHA.
