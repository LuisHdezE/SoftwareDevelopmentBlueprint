# Blueprint 0.5.1-dev — Architecture Implementation Conformance Hardening

## 1. Status and boundary

This document defines the corrective hardening boundary that follows stable Blueprint **0.5.0**.

- latest stable release remains: `0.5.0`;
- root `VERSION` remains `0.5.0` during this development boundary;
- active hardening catalogs/workflows use: `0.5.1-dev`;
- no consumer is upgraded automatically;
- stable `0.5.1` publication/tagging is a separate release-closure boundary.

The purpose is narrow: prevent a functionally correct backend implementation from passing Blueprint API gates while violating the architecture that the project previously approved.

## 2. Pilot finding that triggered the hardening

The CUSA-Digital Greenfield pilot exposed a real gap after adopting Blueprint 0.5.0.

CUSA's approved architecture described modular/Clean Architecture-style boundaries, including separation of Domain/Application from HTTP/framework persistence concerns. The implemented Laravel API nevertheless placed business rules, Eloquent access, transactions and framework concerns in controllers/services while still satisfying the existing functional G5/G8/API checks.

This produced the contradictory but truthful state:

```text
Architecture design                         PASS
API endpoints/auth/audit/backend tests      PASS
OpenAPI/Postman/runtime API QA              PASS
Implementation matches architecture         NOT VERIFIED
```

CUSA corrected the drift in a dedicated Architecture Conformance Remediation boundary, preserved its 45-operation API contract and added an executable architecture guard. That consumer result is **pilot evidence**, not a hidden normative dependency of the Master.

The reusable Blueprint defect was that stable 0.5.0 never asked the missing question.

## 3. Corrective model

Blueprint 0.5.1-dev introduces three REQUIRED checks.

### 3.1 `architecture.implementation_constraints`

Phase: `architecture_security_data`.

Architecture Ready must define implementation constraints precisely enough to verify later. Depending on the approved architecture, this includes applicable rules for:

- dependency direction;
- framework boundaries;
- persistence boundaries;
- presentation responsibilities;
- module/context boundaries;
- ports/adapters or equivalent abstractions.

A statement such as `Clean Architecture`, `Hexagonal`, `Layered` or `Modular Monolith` without testable constraints is insufficient.

### 3.2 `architecture.implementation_conformance`

Phase: `api_implementation`.

The exact reviewed implementation revision must be checked against the approved constraints.

The invariant is:

```text
functional correctness != architecture implementation conformance
```

Passing endpoint tests, OpenAPI, Postman or runtime API QA does not prove dependency direction or separation of responsibilities.

### 3.3 `architecture.conformance_guard`

Phase: `api_implementation`.

At least one executable architecture guard must be required in CI and PASS on the reviewed revision. Valid guard implementations include architecture tests, static-analysis dependency rules or project-specific validators.

Manual prose review alone cannot satisfy this check.

## 4. Gate changes

No new phase and no new gate are introduced.

The existing gates are hardened:

- `architecture_ready` now requires `architecture.implementation_constraints`;
- `api_implemented` now requires `architecture.implementation_conformance` and `architecture.conformance_guard`;
- project-scoped `api_gate` rechecks all three before executable client delivery.

Therefore a backend may be functionally correct and still be blocked at API Implemented when it violates the approved architecture.

## 5. Machine-readable conformance artifact

New contract:

`schemas/architecture-conformance.schema.json`

Example:

`templates/architecture-conformance.example.json`

The artifact records:

- exact `implementation_revision`;
- approved architecture references;
- declared architecture style;
- individual implementation constraints;
- verification method/evidence per constraint;
- executable guards and whether each is required in CI;
- unresolved violations;
- local decision `READY_FOR_REVIEW | PASS | FAIL | BLOCKED`.

Semantic validation additionally enforces that `PASS` cannot coexist with:

- a failed REQUIRED constraint;
- an unresolved violation;
- zero required-in-CI guards;
- a failed required-in-CI guard;
- a violation referencing an undeclared constraint.

## 6. Reusable skill

New materialized skill:

`dev-architecture-conformance`

The skill does **not** make Clean Architecture mandatory for every project. It requires conformance to the architecture the project actually approved.

When Clean/Hexagonal boundaries are approved, typical checks include framework-independent Domain, inward Application dependencies, Presentation without direct persistence/business-rule ownership and Infrastructure implementing ports/adapters. Other approved architectures use equivalent project-specific constraints.

A directory layout by itself is never sufficient evidence.

## 7. Brownfield safety

`ALIGN, DO NOT REWRITE` remains mandatory.

For Brownfield systems:

- conformance is evaluated against the approved TO-BE/alignment decision;
- existing working behavior is not rewritten solely for architectural aesthetics;
- accepted legacy exceptions must be explicit when the approved target permits them;
- a conformance remediation that changes the authoritative API contract must use the normal API impact/revalidation boundary.

Architecture conformance therefore strengthens correctness without becoming a license for destructive modernization.

## 8. Executable Blueprint validation

New validator:

`scripts/validate-architecture-conformance.py`

New CI workflow:

`.github/workflows/blueprint-architecture-conformance-validation.yml`

The validator includes one positive schema/semantic example and negative guards proving that hidden violations, failed required constraints, absent CI guards, failed CI guards and dangling violation references are rejected.

`validate-release.py` also includes this validator in the 0.5.1 development line.

## 9. Development counts

Stable 0.5.0 remains historical truth:

- 28 phases;
- 134 checks;
- 18 gates;
- 14 materialized skills;
- 25 planned skills.

The 0.5.1-dev hardening candidate has:

- 28 phases;
- **137 checks**;
- 18 gates;
- **15 materialized skills**;
- 25 planned skills.

The delta is exactly three checks and one materialized skill. No phase/gate proliferation is required.

## 10. Consumer compatibility

This Master hardening does not mutate CUSA-Digital or any other consumer.

CUSA remains a Blueprint `0.5.0` consumer after its own architecture remediation. It does not become `0.5.1` merely because this Master branch exists or later merges.

After stable 0.5.1 publication, a consumer that wishes to adopt it must use the normal sequence:

1. live Master/consumer verification;
2. Compliance Review `0.5.0 -> 0.5.1`;
3. KEEP / ADOPT / MIGRATE / DEFER / N/A classification;
4. explicit human approval;
5. dedicated consumer adoption PR;
6. proportionate revalidation.

Existing evidence is not retroactively falsified. The patch adds the missing guard for future progression/adoption.

## 11. Deferred release closure

This boundary does **not** publish stable 0.5.1.

A later release-closure boundary must reconcile stable version identity, schemas/templates/skill frontmatter, README/current state/release notes/manifest, full validation and tag creation before `v0.5.1` can be declared stable.

Until that happens, stable Blueprint remains 0.5.0 and 0.5.1 is an explicitly reviewed development line.
