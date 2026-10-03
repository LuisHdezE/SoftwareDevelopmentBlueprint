# Blueprint Agents

Status: PROPOSAL FOUNDATION
Canonical repository: `LuisHdezE/SoftwareDevelopmentBlueprint`

This directory defines specialized AI-assisted engineering roles that may participate in Blueprint-governed delivery.

These files are repository-owned methodology contracts. They are not per-project runtime state.

## Governance boundary

This proposal is based on:

`main@fcd92a52596db5ddd070002eb3f7f2ce2eef0bbf`

At this baseline:

- stable Blueprint remains `0.5.4`;
- `0.5.5-dev` is already closed as a release candidate;
- this proposal does not modify `VERSION` or `DEVELOPMENT_VERSION`;
- this proposal does not alter the frozen 0.5.5 release-candidate scope;
- no consumer repository auto-adopts these roles;
- no merge is authorized without an explicit governed lane and human approval.

## Core agent model

The intended core model contains eleven roles:

1. Orchestrator
2. Analyst
3. Planner
4. Architect
5. Database
6. Backend
7. Frontend
8. QA
9. Security
10. Documentation
11. Auditor

This first increment materializes only:

- `analyst.md`
- `planner.md`

The remaining roles must be introduced through later governed increments.

## Responsibility chain

```text
User / Request
      ↓
Orchestrator
      ↓
Analyst
      ↓
Planner
      ↓
Architect
      ↓
Database / Backend / Frontend
      ↓
QA / Security / Documentation
      ↓
Auditor
      ↓
Human approval where required
```

## Separation rules

- Analyst defines what must be achieved and what correct behavior means.
- Planner converts approved analysis into traceable executable work.
- Planner must not invent missing business behavior.
- Implementers must not certify their own work as final QA.
- QA, Security and Auditor remain independent validation authorities.
- Frontend and Backend exchange behavior through explicit contracts.
- Project-local state belongs in the consumer repository, typically under its own `.blueprint/` state area, not in this canonical directory.

## Status semantics

Materializing an agent contract in this repository does not by itself mean that the role is part of a stable Blueprint release.

`PRESENT != STABLE != ADOPTED`

Promotion into a stable release requires the normal Blueprint governance, validation, release and consumer-adoption process.
