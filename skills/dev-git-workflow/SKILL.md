---
id: dev-git-workflow
title: Git Workflow and Review Boundaries
version: 0.5.0
status: materialized
category: core
applies_to:
  - greenfield
  - brownfield
phases:
  - all
canonical_references:
  - BLUEPRINT.md
  - documentation/BLUEPRINT_V0_5_ROADMAP.md
  - schemas/status.schema.json
  - schemas/evidence.schema.json
---

# Git Workflow and Review Boundaries

## Purpose

Keep changes reviewable, reversible and attributable. Git is part of the Blueprint evidence model, not merely transport. Every implementation boundary must be reconstructable from verified base SHA through final-head CI, pull request, human decision and post-merge verification.

## When to Use

Use for every implementation or documentation change that alters a consumer project or the Blueprint itself, especially when creating branches, commits, pull requests, resolving drift, reacting to API-impact changes or advancing a Functional Interface Slice.

## Inputs

- Current authoritative `main`/default-branch head and repository status.
- Current Blueprint version and active review boundary.
- Existing open pull requests and unmerged branches relevant to the same chain.
- Required checks, scoped gates and evidence for the change.
- Human merge/acceptance authority defined by project governance.

## Procedure

1. Verify the authoritative base branch live before editing. Chat summaries, handoffs and local assumptions are checkpoints only; repository state wins when they disagree.
2. Confirm the previous boundary is merged and post-merge validation is green before branching for the next dependent boundary.
3. Create a short-lived branch from the exact verified base SHA. Do not stack a dependent implementation branch on an unmerged sibling unless the workflow explicitly allows it.
4. Keep one logical review boundary per PR. Separate unrelated refactors, dependency upgrades, formatting sweeps and product behavior changes.
5. Commit coherent checkpoints and preserve enough history/evidence to reconstruct why the boundary changed. Connector-generated micro-commits may exist, but the effective diff must remain reviewable.
6. Run every check required by the phase on the exact final head. A green run on an earlier SHA is not evidence for a moved branch.
7. Compare final branch to base and record ahead/behind state, changed files and unexpected drift before opening the PR.
8. Open the PR with scope, evidence, compatibility impact, known debt and explicit next boundary. Human review/merge authority is never inferred merely from CI unless governance explicitly delegates that authority.
9. For API changes after an initial API Gate, preserve the API-impact artifact and revalidation evidence for affected slices rather than globally invalidating unrelated work.
10. After merge, verify the merge commit on the authoritative branch and confirm its own CI before beginning the next dependent boundary.
11. For release boundaries, verify VERSION, catalogs, schemas, docs, release manifest and tag from the exact merged commit before declaring the release complete.

## Outputs

- Branch scoped to one review boundary.
- Reviewable commits and exact-head validation evidence.
- PR with clear scope/evidence/next step.
- Human review/merge decision when required.
- Verified post-merge main head before downstream work.
- Release/tag evidence when the boundary is a release.

## Stop Conditions

- Previous dependent PR is still open or its merge has not been verified.
- Branch is behind `main` in a way that changes the review baseline.
- Required CI has not passed on the exact final head.
- Diff contains unrelated or unexplained files.
- A required human approval/merge decision has not occurred.
- A downstream boundary is being started from an unverified merge commit.

## Guardrails

- Never claim a merge occurred until verified on the target branch.
- Never use a green check from another SHA as final-head evidence.
- Never equate CI success with human approval when the gate is manual.
- Do not rewrite shared review history without revalidation.
- Repository history and evidence must make gate transitions explainable.
- Consumer repositories do not silently adopt a new Blueprint version because the Blueprint Master released one.

## Canonical References

- `BLUEPRINT.md`
- `documentation/BLUEPRINT_V0_5_ROADMAP.md`
- `schemas/status.schema.json`
- `schemas/evidence.schema.json`

## Completion Signal

Complete only when the boundary has a verified base, exact final head, required checks/evidence, a reviewable PR and the required human decision, and when any merge is confirmed on the authoritative branch with downstream work starting only from that verified state.
