# Software Development Blueprint 0.5.1 Release Notes

## Summary

Blueprint 0.5.1 is a focused hardening patch over 0.5.0.

It does not add a phase, gate, client lifecycle state, platform capability or product-specific rule. It adds one missing verification obligation discovered through real consumer evidence:

`api.architecture_implementation_conformance`

The release makes explicit that an architecture can be correctly designed and approved while the implementation still violates that architecture. Functional/API correctness and architecture implementation conformance are separate facts and both must be evidenced.

## Why this patch exists

CUSA-Digital completed its API lifecycle and later exposed implementation drift against its previously approved G3 architecture. The external API remained behaviorally correct, but controllers/services had absorbed responsibilities that the architecture assigned elsewhere.

A dedicated CUSA remediation restored conformance without changing the authoritative API contract. The lesson generalized cleanly:

`architecture design acceptance != architecture implementation conformance`

CUSA remains reference evidence for the rule. Its Laravel/Clean Architecture structure is not copied into Blueprint as a universal requirement.

## Canonical change

0.5.1 adds exactly one REQUIRED check under `api_implementation`:

`api.architecture_implementation_conformance`

The check requires evidence that the implementation conforms to the approved architecture contract.

Where applicable, evidence should cover:

- dependency direction;
- module/context/layer boundaries;
- Presentation/Application/Domain/Infrastructure responsibilities or equivalent project-defined boundaries;
- ports/adapters and dependency bindings;
- framework/persistence isolation rules;
- architecture fitness functions or automated/static assertions where feasible;
- explicit manual review for constraints that cannot reasonably be automated.

Blueprint does not prescribe Laravel, Clean Architecture, DDD, hexagonal architecture or a specific directory layout universally.

## Gate impact

`api_implemented` now requires the new conformance check.

`api_gate` also requires it.

Therefore:

`runtime/API PASS cannot substitute for architecture implementation conformance`

This closes the verification gap between Architecture Ready and API Gate without introducing a new phase or gate.

## Counts

Stable 0.5.1 contains:

- **28 phases**;
- **135 checks**;
- **18 gates**;
- **14 materialized skills**;
- **25 planned skills**.

Compared with 0.5.0, only the check count changes: `134 -> 135`.

## Component provenance

0.5.1 uses explicit component provenance instead of mechanically relabeling unchanged contracts.

Updated to 0.5.1:

- root `VERSION`;
- checks catalog;
- gates catalog;
- project manifest schema;
- status schema;
- canonical project/status templates;
- active release documentation and validation rules.

Reused from 0.5.0 without semantic modification:

- phases catalog;
- Greenfield/Brownfield workflows;
- materialized skills and skill catalog;
- experience artifact schemas such as Interface Inventory, Functional Slice, Evidence, Client Architecture, Design System/Tokens and API Impact;
- reference-pilot registry contract.

The root release can therefore be `0.5.1` while unchanged components retain `0.5.0` provenance. Validators enforce the allowed compatibility matrix explicitly.

## Historical evidence

0.5.1 does not rewrite 0.5.0 history.

Earlier functional/API evidence remains valid when its claims remain true. A later architecture-conformance failure is handled as a dedicated remediation boundary and does not automatically erase unrelated historical evidence.

API impact is classified independently. Internal structural remediation with an unchanged authoritative API contract does not fabricate an API-impact artifact merely because implementation files changed.

## Brownfield

Brownfield continues to use **ALIGN, DO NOT REWRITE**.

Architecture implementation conformance is evaluated against the approved TO-BE/coexistence/cutover contract. It may therefore prove migration seams, adapter boundaries, containment or controlled coexistence rather than immediate structural replacement.

## Consumer adoption

There is **no automatic consumer upgrade**.

A consumer on 0.5.0 remains on 0.5.0 after publication of 0.5.1. Adoption requires:

1. live verification of Master and consumer;
2. Compliance Review `0.5.0 -> 0.5.1`;
3. KEEP / ADOPT / MIGRATE / DEFER / N/A classification;
4. explicit human approval;
5. dedicated adoption PR;
6. impact-appropriate revalidation.

CUSA-Digital is not modified by this release closure. Its Design System/client work remains outside this Master PR.

## Release integrity

The stable tag is `v0.5.1`.

It must be created only after:

1. the release PR is explicitly approved and merged;
2. `main` is verified at the accepted merge commit;
3. post-merge CI passes on that exact commit.

CI evidence never substitutes for human merge authorization.
