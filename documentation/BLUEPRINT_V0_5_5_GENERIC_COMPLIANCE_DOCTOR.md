# Blueprint 0.5.5-dev · Generic Compliance Doctor

## Purpose

Increment 5 removes product-specific truth from Compliance Review execution. The Doctor evaluates a consumer from an explicit manifest plus Blueprint-owned catalogs and authority overlays. CareShift, WebBlueprint, routes, operation IDs, screenshots, permissions and repository SHAs are consumer facts and MUST NOT be embedded in the generic engine.

Stable `0.5.4` semantics remain unchanged during this hardening lane. The Doctor is a `0.5.5-dev` overlay and does not auto-upgrade any consumer.

## Inputs

A consumer manifest declares only the facts needed to evaluate applicability and evidence:

- consumer identity and repository;
- adopted Blueprint version and evaluation version;
- greenfield or brownfield workflow mode;
- API authority mode: `api_backed` or `api_optional`;
- capabilities, including whether an authoritative database exists;
- optional conditional-check decisions;
- evaluation scope: `full` or an explicit set of check IDs;
- evidence registry;
- consumer assessments bound to evidence IDs.

Schema:

`schemas/generic-compliance-manifest-v055-dev.schema.json`

Reference examples:

- `templates/generic-compliance.api-backed-v055-dev.example.json`
- `templates/generic-compliance.api-optional-v055-dev.example.json`

## Authority and applicability

The Doctor does not invent a second applicability model. It reads the stable check catalog and the existing `0.5.5-dev` workflow applicability overlay.

For `api_backed`, stable `0.5.4` API strictness is preserved.

For `api_optional`:

- API-only phases/checks declared N/A by the authority overlay are genuinely N/A;
- database checks may be N/A only when the consumer explicitly declares no authoritative database;
- `qa.real_api_transport` is N/A;
- `qa.provider_runtime_transport` becomes the development transport obligation;
- common QA such as security, responsive, accessibility and E2E does not disappear;
- a consumer cannot claim server authority merely to satisfy compliance.

Brownfield-only and capability-bound checks are evaluated from the manifest. Conditional checks without a capability binding require an explicit consumer condition decision. Missing that decision yields `BLOCKED`, not an invented PASS or N/A.

## Result model

Every evaluated check becomes exactly one of:

- `PASS`
- `FAIL`
- `N/A`
- `BLOCKED`

The machine-readable report records a reason code:

- `PASS`
- `CONTRACT_VIOLATION`
- `MISSING_EVIDENCE`
- `STALE_EVIDENCE`
- `VERSION_MISMATCH`
- `PREREQUISITE_BLOCKED`
- `NOT_APPLICABLE`

Schema:

`schemas/generic-compliance-report-v055-dev.schema.json`

Overall status is fail-closed:

1. any `FAIL` => overall `FAIL`;
2. otherwise any `BLOCKED` => overall `BLOCKED`;
3. otherwise => overall `PASS`.

`N/A` never counts as PASS, and an applicable check cannot be declared N/A.

## Evidence semantics

A declared PASS requires at least one evidence reference.

The Doctor rejects or downgrades PASS when:

- an evidence ID is absent;
- evidence is explicitly `MISSING`;
- evidence is `STALE`;
- evidence belongs to an incompatible Blueprint version and is neither grandfathered nor explicitly accepted for the evaluation version.

Existing accepted consumer evidence may be marked `grandfathered: true`. This preserves the frozen `0.5.5-dev` decision that accepted evidence is not automatically discarded during hardening.

## Selected and full audits

`scope.mode = selected` evaluates only the declared check IDs. This supports focused incremental reviews.

`scope.mode = full` evaluates every stable Blueprint check plus the development-only provider/runtime transport check. Missing applicable assessments then fail closed.

This separation lets Increment 6 run a complete WebBlueprint pilot review without making WebBlueprint normative.

## CLI

Self-test, including positive and negative generic fixtures:

```bash
python scripts/validate-generic-compliance-v055-dev.py
```

Audit an arbitrary consumer manifest:

```bash
python scripts/validate-generic-compliance-v055-dev.py \
  --manifest path/to/consumer-compliance.json \
  --report-json out/compliance-report.json \
  --report-md out/compliance-report.md
```

A compliant run exits `0`. `FAIL` or `BLOCKED` exits non-zero.

## Negative fixtures

The Doctor currently proves fail-closed behavior for:

- missing evidence;
- stale evidence;
- evidence version mismatch;
- an API-optional consumer attempting to PASS an API-only check;
- a blocked prerequisite.

Fixtures live under `tests/fixtures/generic-compliance/` and contain no product-specific truth.

## Relationship to the historical pilot validator

`scripts/validate-reference-pilot-compliance.py` remains a historical regression validator for the old CareShift compliance snapshot. It is not the generic authority for new consumer reviews.

The Generic Compliance Doctor must not import that script, its repository constants, protected finding IDs, fixed SHAs or fixed recommendation.

## Increment 6 boundary

This increment does not mutate WebBlueprint.

After Increment 5 is merged and post-merge validation is green, Increment 6 may create a WebBlueprint consumer manifest from the previously frozen review evidence, run the Doctor as a non-normative pilot, reconcile template provenance, and decide whether WebBlueprint can honestly adopt the resulting stable Blueprint release.
