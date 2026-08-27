---
id: dev-architecture-conformance
title: Architecture Implementation Conformance
version: 0.5.1-dev
status: materialized
category: core
applies_to:
  - greenfield
  - brownfield
phases:
  - architecture_security_data
  - api_implementation
canonical_references:
  - BLUEPRINT.md
  - catalog/phases.yaml
  - catalog/checks.yaml
  - catalog/gates.yaml
  - schemas/architecture-conformance.schema.json
  - templates/architecture-conformance.example.json
  - workflows/greenfield.yaml
  - workflows/brownfield.yaml
---

# Architecture Implementation Conformance

## Purpose

Turn approved architecture from descriptive prose into verifiable implementation constraints, then prove that the reviewed code revision satisfies those constraints with an executable guard in CI. Functional correctness, endpoint coverage and passing contract tests do not substitute architecture conformance.

## When to Use

Use during Architecture / Security / Data to make implementation boundaries explicit, during API Implementation to verify the actual code against those boundaries, and whenever a later refactor can alter dependency direction or framework/persistence boundaries without intentionally changing the external API contract.

## Inputs

- Approved architecture overview, ADRs and module/context boundaries.
- Domain, application, infrastructure and presentation responsibilities when those layers exist.
- Approved dependency-direction, persistence, framework and port/adapter decisions.
- Current implementation revision/commit SHA.
- Existing architecture/static-analysis tests or CI rules when present.
- Brownfield AS-IS and approved TO-BE decisions when aligning an existing system.
- API contract and regression evidence when a post-baseline remediation is being performed.

## Procedure

1. Read the approved architecture artifacts before inspecting conformance. Do not substitute a preferred pattern for the project's accepted architecture.
2. Extract concrete implementation constraints. At minimum consider dependency direction, framework coupling, persistence access, presentation responsibilities, module boundaries and port/adapter bindings when they apply.
3. Reject vague declarations such as “uses Clean Architecture” when the repository does not state what dependencies are permitted or forbidden. Convert the approved intent into testable rules first.
4. Map the implementation to the approved boundaries. Identify where business rules, orchestration, persistence, framework adapters and HTTP/UI concerns actually live.
5. When the approved model is Clean Architecture or Hexagonal Architecture, verify inward dependency direction. Typical constraints include framework-independent Domain, Application depending inward rather than on concrete Infrastructure, Presentation avoiding direct persistence/business-rule ownership, and Infrastructure implementing ports/adapters. Apply only constraints that are part of the approved project contract.
6. For other approved architectures, encode equivalent project-specific boundary rules rather than forcing Clean Architecture terminology.
7. Create or update the architecture conformance artifact using `schemas/architecture-conformance.schema.json`. Pin it to the exact implementation revision being reviewed and reference the approved architecture sources.
8. Add at least one executable guard that is required in CI. Suitable guards include architecture tests, dependency rules, static analysis or custom scripts. A manual review alone cannot satisfy `architecture.conformance_guard`.
9. Make the guard fail on prohibited dependencies/boundary violations. Include negative cases where practical so the guard is proven capable of detecting drift, not merely capable of passing.
10. Run normal backend tests as a separate dimension. Record architecture conformance and functional regression independently: `functional PASS != architecture PASS`.
11. If conformance work changes the authoritative API contract, stop the architecture-only remediation and route the contract change through the normal API impact/revalidation process.
12. For Brownfield, evaluate against the approved TO-BE/alignment decision. Do not rewrite working code solely for architectural aesthetics; record accepted legacy exceptions explicitly when the target architecture permits them.
13. Do not mark the conformance artifact `PASS` while required constraints fail, violations remain open, or no required-in-CI guard passes on the reviewed revision.

## Outputs

- Verifiable architecture implementation constraints referenced from approved architecture decisions.
- Machine-readable architecture conformance artifact pinned to the reviewed revision.
- Executable architecture guard required in CI.
- Evidence for `architecture.implementation_constraints`.
- Evidence for `architecture.implementation_conformance`.
- Automatic evidence for `architecture.conformance_guard`.
- Explicit violations/remediation notes when conformance is not yet achieved.

## Stop Conditions

- The architecture itself is not approved or is too vague to derive testable constraints.
- The implementation revision cannot be pinned.
- A required architecture constraint is failing.
- No architecture guard is actually required in CI.
- The proposed “fix” changes API behavior but no API contract/impact boundary has been opened.
- Brownfield refactoring is justified only by pattern preference rather than an approved target or concrete risk.
- Evidence describes a different commit than the code being reviewed.

## Guardrails

- Conformance is against the approved architecture, not the agent's favorite architecture.
- Clean Architecture terminology is enforced only when Clean/Hexagonal-style boundaries are part of the approved contract.
- Functional tests, OpenAPI validation and Postman/runtime QA remain necessary but are not evidence of dependency direction.
- A directory layout alone is not conformance; dependencies and responsibilities matter.
- A passing architecture guard must be able to fail on real prohibited drift.
- Framework, ORM and transport technologies belong only where the approved architecture permits them.
- Preserve `ALIGN, DO NOT REWRITE` in Brownfield systems.
- Never change the external contract silently while performing an internal architecture remediation.

## Canonical References

- `BLUEPRINT.md`
- `catalog/phases.yaml`
- `catalog/checks.yaml`
- `catalog/gates.yaml`
- `schemas/architecture-conformance.schema.json`
- `templates/architecture-conformance.example.json`
- `workflows/greenfield.yaml`
- `workflows/brownfield.yaml`

## Completion Signal

Complete only when approved implementation constraints are explicit, the conformance artifact is pinned to the reviewed code revision, every required constraint passes, unresolved violations are zero, at least one executable architecture guard is required in CI and passes on that revision, and normal functional/API regression remains independently valid.
