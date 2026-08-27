# Blueprint 0.5.1 Architecture Implementation Conformance Hardening

## Status

Accepted hardening for stable Blueprint `0.5.1`.

- stable base: `0.5.0`
- stable target: `0.5.1`
- source finding: CUSA-Digital Architecture Conformance Remediation, PR #31
- Blueprint hardening PR: #19
- consumer auto-adoption: **disabled**
- phases added: **0**
- gates added: **0**
- checks added: **1**

This boundary does not rewrite the historical stable `v0.5.0` release. It promotes one verified lesson into a patch release that consumers may adopt only through a separate Compliance Review.

## 1. Problem

Blueprint 0.5.0 distinguished architecture design from API implementation, but the API implementation gate proved endpoints, authorization, durable audit and backend tests without an explicit assertion that the implementation actually conformed to the previously approved architecture.

A real pilot exposed the gap. A system can simultaneously have:

- an accepted architecture contract;
- green functional/API tests;
- correct OpenAPI/Postman behavior;
- and a materially incorrect implementation structure.

Therefore:

`architecture design acceptance != architecture implementation conformance`

Both are required.

## 2. Canonical check

Blueprint 0.5.1 adds:

`api.architecture_implementation_conformance`

Classification:

- phase: `api_implementation`
- type: `REQUIRED`
- verification: `evidence`

The check proves that the implemented backend follows the approved architecture contract, especially where that contract defines dependency direction, layer/module ownership or ports/adapters.

## 3. What must be evidenced

The evidence is architecture-specific and technology-neutral. It SHOULD be executable wherever practical and MUST not be reduced to a prose declaration when enforceable invariants exist.

Typical evidence includes:

- allowed and forbidden dependency direction;
- module/context boundaries;
- framework/persistence isolation rules;
- business-rule ownership;
- Presentation adapter responsibilities;
- Application orchestration boundaries;
- Domain framework-independence when required by the approved architecture;
- Infrastructure implementation of declared ports/adapters;
- dependency-injection/binding correctness;
- architecture fitness functions, static rules or automated tests;
- explicit manual review only for constraints that cannot reasonably be automated.

The Blueprint does **not** prescribe Laravel, Clean Architecture, DDD or a particular directory tree universally. The executable assertions must reflect the architecture the project actually approved.

## 4. Reference pattern, not universal code

The CUSA pilot used this effective responsibility split:

```text
Presentation
    -> Application
        -> Domain

Infrastructure -> implements Application ports
```

Its architecture fitness test rejected forbidden framework/persistence dependencies from Domain/Application, direct persistence access from HTTP adapters and missing Application-port to Infrastructure-adapter bindings.

That implementation is reference evidence only. The Blueprint requirement is the general invariant: implementation must conform to the project's approved architecture.

## 5. Gate integration

`api_implemented` now requires `api.architecture_implementation_conformance` in addition to endpoint/auth/audit/test evidence.

`api_gate` also aggregates the same check because client delivery must not be unlocked by an API that is behaviorally correct but structurally inconsistent with its approved architecture.

Invariant:

`runtime/API PASS cannot substitute for architecture implementation conformance`

## 6. Historical evidence and later findings

A later architecture-conformance failure does not automatically erase earlier functional/API evidence. It means that a missing conformance obligation has been discovered or a previously conforming implementation has drifted.

Handle remediation as a dedicated boundary:

1. freeze the current consumer baseline;
2. record the architecture-conformance finding;
3. remediate the implementation without silently changing API/product behavior;
4. run executable architecture assertions and applicable regression suites;
5. classify API impact separately;
6. preserve valid historical evidence that remains true;
7. require explicit human review before downstream work resumes when that work was intentionally blocked by the remediation.

If the remediation changes the API contract, normal API impact/revalidation rules apply. If it changes only internal structure and the authoritative API remains identical, an API-impact artifact is not fabricated merely because files changed.

## 7. Brownfield

For Brownfield systems, `ALIGN, DO NOT REWRITE` remains authoritative. Architecture implementation conformance is evaluated against the approved TO-BE/coexistence/cutover contract, not against an idealized greenfield rewrite.

The check may therefore prove controlled coexistence, dependency containment, strangler boundaries, adapter isolation or agreed migration seams rather than immediate full structural replacement.

## 8. Human governance

Architecture fitness tests produce evidence; they do not create human approval.

`GENERATED != REVIEWED != APPROVED` remains applicable to generated evidence/artifacts, and CI success never authorizes merge by itself.

## 9. Release and adoption

The semantic hardening boundary was reviewed and merged before release closure. Stable `0.5.1` promotes the new check, the affected gates and the consumer declaration schemas/templates while preserving provenance for unchanged 0.5.0 components.

No consumer auto-adoption occurs. CUSA-Digital or any other consumer remains on its explicitly declared Blueprint version until a Compliance Review authorizes a version change.
