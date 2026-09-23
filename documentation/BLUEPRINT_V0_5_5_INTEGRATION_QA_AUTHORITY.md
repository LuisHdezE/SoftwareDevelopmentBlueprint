# Blueprint 0.5.5-dev · Integration QA Authority Matrix

## Purpose

Increment 4 resolves the remaining Integration QA contradiction exposed by the
WebBlueprint compliance pilot.

Stable 0.5.4 correctly requires Integration QA for every committed client slice,
but `integration_qa_pass` always requires `qa.real_api_transport`. That is truthful
for an API-backed slice and false for a legitimate API-optional slice whose runtime
boundary is an application/provider contract with local, static or non-authoritative
mock adapters.

The 0.5.5-dev rule is therefore:

> API transport may be N/A. Integration QA may not be N/A merely because API transport is N/A.

Stable 0.5.4 catalogs remain unchanged during hardening. This increment adds a
development overlay and validates both authority profiles.

## Authority matrix

| Obligation | `api_backed` | `api_optional` |
| --- | --- | --- |
| `qa.functional` | REQUIRED | REQUIRED |
| transport-specific QA | `qa.real_api_transport` | `qa.provider_runtime_transport` |
| `qa.integration` | REQUIRED | REQUIRED |
| `qa.security` | REQUIRED | REQUIRED |
| `qa.responsive` | REQUIRED | REQUIRED |
| `qa.accessibility` | REQUIRED | REQUIRED |
| `qa.e2e` | REQUIRED | REQUIRED |
| `qa.idempotency` | conditional | conditional |
| `qa.offline` | conditional | conditional |
| `functional_slice_ready` prerequisite | PASS | PASS |
| `visual_functional_review_pass` prerequisite | PASS | PASS |

The human visual/functional review remains a prerequisite. CI, transport tests or
browser automation do not synthesize human acceptance.

## API-backed profile

`api_backed` preserves stable 0.5.4 `integration_qa_pass` exactly:

- `qa.real_api_transport` remains required;
- OpenAPI binding remains required;
- operation IDs remain bound to the client slice;
- the remote authority and server security boundary remain explicit;
- the common functional/security/responsive/accessibility/E2E checks are unchanged.

No 0.5.5-dev consumer may use provider-runtime QA to bypass a real API authority
boundary.

## API-optional profile

`api_optional` replaces only the transport-specific check:

- `qa.real_api_transport` becomes inapplicable;
- `qa.provider_runtime_transport` becomes required;
- provider/application contract references are explicit;
- at least one runtime surface is exercised;
- adapter modes are explicit;
- remote authority is `false`;
- remote mutations are `false`;
- server-security claims are `false`.

Permitted runtime surfaces include browser preview, browser production, local/device
runtime and dedicated test harnesses. These are runtime evidence, not claims that a
server API exists.

The WebBlueprint Sign In slice is the motivating case: its contract/provider boundary,
Browser QA and production runtime can be validated truthfully without inventing
OpenAPI or calling local/demo authentication a server security boundary.

## Fail-closed guarantees

The validator rejects at least these cases:

1. `api_optional` claims remote authority.
2. `api_optional` claims server security.
3. `api_optional` uses `qa.real_api_transport`.
4. `api_optional` drops security QA.
5. `api_optional` drops the human-review prerequisite.
6. `api_backed` replaces real API transport with provider runtime.
7. `api_backed` weakens remote authority.
8. `api_backed` omits OpenAPI transport binding.
9. A client/slice authority profile remains marked `DEFERRED_TO_INCREMENT_4`.
10. Integration QA itself is marked N/A by the workflow applicability profile.

## Stable catalog boundary

During `0.5.5-dev` hardening:

- `catalog/checks.yaml` stays version `0.5.4`;
- `catalog/gates.yaml` stays version `0.5.4`;
- `qa.provider_runtime_transport` is a development-only check expressed by this overlay;
- release closure will decide how the new conditional transport check is promoted into
  the stable 0.5.5 catalogs/status contracts.

This prevents a development lane from pretending that an unreleased contract is already
stable.

## Client/Slice continuity

Increment 3 previously carried `integration_qa_scope = DEFERRED_TO_INCREMENT_4`.
Increment 4 resolves that boundary.

The two Client/Slice Authority examples now point explicitly to the corresponding
Integration QA Authority profile:

- API-backed slice → API-backed Integration QA profile;
- API-optional slice → provider-runtime Integration QA profile.

The authority mode must agree end to end:

```text
project authority
    ↓
client platform
    ↓
client slice
    ↓
Integration QA transport
```

A mismatch is a validation failure.

## Scope boundary

This increment does not:

- promote 0.5.5 to stable;
- change root `VERSION`;
- mutate WebBlueprint;
- weaken API-backed semantics;
- generalize the CareShift-specific Compliance Review validator.

The next increment is **Increment 5 · Generic Compliance Doctor**.
