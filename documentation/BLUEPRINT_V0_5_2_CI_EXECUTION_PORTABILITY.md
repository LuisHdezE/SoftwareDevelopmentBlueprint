# Blueprint 0.5.2 CI Execution Portability Hardening

## Status

Development hardening candidate for the stable `0.5.1` line.

- stable base: `0.5.1`
- candidate line: `0.5.2-dev`
- source finding: private-repository GitHub-hosted runners became unavailable when billable Actions usage was blocked
- consumer auto-adoption: **disabled**
- phases added: **0**
- gates added: **0**
- checks added: **0**
- new machine-readable contract: `schemas/ci-runtime.schema.json`

This boundary does not rewrite the stable `v0.5.1` release. It adds a provider-execution portability contract so exact-head CI evidence can remain mandatory without forcing consumers to buy GitHub-hosted minutes.

## 1. Problem

Blueprint already requires:

`verified main -> short-lived branch -> exact-head validation -> PR -> human decision -> verified merge`

That governance rule is correct, but stable 0.5.1 does not distinguish the semantic requirement for CI evidence from the commercial/runtime mechanism that executes it.

A real private-repository pilot exposed the gap. GitHub-hosted jobs can fail before executing any step because no billable hosted runner is available. Such a failure says nothing about product correctness, while skipping exact-head CI would weaken Blueprint governance.

Therefore:

`CI evidence semantics != runner ownership`

and:

`pre-execution infrastructure failure != test failure`

Blueprint must preserve the evidence requirement while allowing the execution runtime to be GitHub-hosted, self-hosted or hybrid.

## 2. Canonical CI runtime contract

Blueprint 0.5.2-dev introduces:

`schemas/ci-runtime.schema.json`

with a canonical example:

`templates/ci-runtime.example.yaml`

The artifact is CONDITIONAL. A consumer SHOULD materialize `.blueprint/ci-runtime.yaml` when it explicitly manages or overrides CI execution strategy, especially for `self_hosted` or `hybrid` execution.

Supported strategies:

- `github_hosted`: workflow jobs use provider-hosted runners.
- `self_hosted`: workflow jobs use trusted project-controlled runners.
- `hybrid`: trusted/self-hosted execution is combined with provider-hosted execution by documented policy.

The development contract currently targets GitHub Actions orchestration because that is the observed boundary. The evidence invariants are intentionally more general and may later be mapped to other CI orchestrators.

## 3. Self-hosted runner baseline

For the canonical Linux/x64 GitHub Actions profile:

```text
runs-on: [self-hosted, linux, x64, blueprint]
```

The custom `blueprint` label distinguishes machines intentionally prepared for Blueprint CI from arbitrary self-hosted runners.

A persistent self-hosted runner MUST:

- execute trusted repository code only;
- deny fork pull requests on the self-hosted lane;
- avoid persistent repository secrets on disk;
- keep workflow token permissions least-privilege;
- clean working state between jobs;
- stay updated through GitHub automatic runner updates or an explicit operator-managed update policy;
- preserve exact-head check-run evidence in GitHub.

Repository-scoped runners are the preferred baseline for personal/private repositories because they reduce blast radius.

## 4. Docker is runner infrastructure, not project capability

The existing consumer capability:

`capabilities.docker`

describes whether Docker is part of the project/development solution contract.

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

No consumer is forced to ship, develop or deploy the application with Docker merely because CI uses service containers.

## 5. Evidence equivalence

Self-hosted CI is acceptable only when it preserves the same governance semantics as hosted CI.

PASS evidence still requires, as applicable:

- workflow/check execution attached to the exact candidate commit SHA;
- repository-owned workflow definition;
- expected test/validation scope;
- logs and artifacts required by the gate;
- no substitution of local untracked commands for required check evidence;
- human approval kept separate from CI success.

A self-hosted PASS is not weaker evidence merely because the machine is project-controlled.

Conversely, a job that terminates before a runner is assigned or before any step executes is infrastructure evidence, not a product/test failure and not a PASS.

## 6. Security boundary

Self-hosted runners execute repository workflow code on a persistent machine. The trust boundary is therefore stricter than for disposable provider-hosted VMs.

Blueprint 0.5.2-dev requires the self-hosted lane to be restricted to trusted code. Public/fork PR execution must be denied or routed to a provider-hosted lane in a hybrid strategy.

Secrets MUST be provided ephemerally by the CI orchestrator and MUST NOT be baked into the runner image, shell profile, repository checkout or persistent work directory.

Administrative/root privileges SHOULD NOT be granted to arbitrary workflow steps. Dependencies that require privilege SHOULD be provisioned as part of runner bootstrap where practical.

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

## 8. Brownfield and consumer adoption

This hardening does not mutate any consumer automatically.

Existing consumers on 0.5.1 or earlier remain valid. They may continue using GitHub-hosted runners.

After a stable 0.5.2 release, a consumer that needs self-hosted execution adopts it through a separate boundary that:

1. verifies its current Blueprint version and repository state;
2. performs the required Compliance Review when changing Blueprint version;
3. adds its CI runtime artifact;
4. changes only the affected workflow runner selectors/runtime assumptions;
5. validates the exact candidate head on the new runner;
6. preserves unrelated accepted evidence.

## 9. Master bootstrap

The Blueprint Master is the first development adopter of this boundary.

Its validation workflows move from provider-hosted Ubuntu labels to:

`[self-hosted, linux, x64, blueprint]`

so this PR can prove the portability contract using real GitHub check runs without billable hosted-runner minutes.

The Master runner is repository-scoped. CUSA-Digital is not modified by this PR and will require its own separately registered runner/adoption boundary after 0.5.2 is stable.

## 10. Release boundary

Stable `VERSION = 0.5.1` intentionally remains unchanged in this hardening PR.

After this candidate is explicitly reviewed, receives green exact-head self-hosted CI and is merged, a separate release-closure PR may promote the coherent repository state to `0.5.2`.

No release, consumer upgrade, CUSA workflow mutation or downstream slice state transition is implied by this development boundary.
