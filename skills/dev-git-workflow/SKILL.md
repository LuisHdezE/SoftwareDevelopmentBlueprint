---
id: dev-git-workflow
title: Git Workflow and Review Boundaries
version: 0.4.0-dev
status: materialized
category: core
applies_to:
  - greenfield
  - brownfield
phases:
  - all
canonical_references:
  - BLUEPRINT.md
  - documentation/BLUEPRINT_V0_4_ROADMAP.md
  - schemas/status.schema.json
---

# Git Workflow and Review Boundaries

## Purpose

Keep changes reviewable, reversible, and attributable. Git is part of the Blueprint evidence model, not merely a transport mechanism.

## When to Use

Use for every implementation or documentation change that will alter a consumer project or the Blueprint itself, especially when creating branches, commits, pull requests, resolving drift, or defining review boundaries.

## Inputs

- Current `main`/default-branch head and repository status.
- The phase/slice being changed and its governing gate.
- Existing open pull requests and unmerged branches relevant to the same review boundary.
- Required CI/evidence for the change.

## Procedure

1. Confirm the authoritative base branch and verify whether the previous review boundary is already merged. Do not stack a new implementation PR unless the Blueprint explicitly allows it.
2. Create a short-lived branch named for the review boundary or slice. Branch from the verified base commit, not from an unmerged sibling branch.
3. Keep the diff limited to one logical boundary. Separate unrelated refactors, formatting sweeps, dependency upgrades, and product behavior changes.
4. Commit at coherent checkpoints. Before closing a branch, prefer a clean logical history; squash connector-generated micro-commits when that improves reviewability without losing evidence.
5. Run the checks required by the phase and verify them on the exact final head commit. A green run on an earlier commit is not sufficient evidence.
6. Compare the final branch to the base and record ahead/behind counts and changed files. Investigate unexpected files or drift before opening the PR.
7. Open the PR with scope, evidence, known debt, and explicit next phase. The human reviewer owns merge authorization unless a repository policy explicitly delegates it.
8. After merge, verify the merge on the authoritative branch before beginning the next review boundary.

## Outputs

- A branch scoped to one review boundary.
- Atomic or intentionally squashed commits.
- A PR whose body states scope, evidence, known debt, and next step.
- Post-merge verification before downstream work starts.

## Stop Conditions

- The previous implementation PR for the same chain is still open.
- The branch is behind `main` in a way that changes the review baseline.
- Required CI has not passed on the exact final head.
- The diff contains unrelated or unexplained files.
- Merge authorization is required from a human and has not been given.

## Guardrails

- Never claim a merge occurred until it is verified on the target branch.
- Never use a green check from a different SHA as evidence for the final head.
- Do not rewrite shared history after review has started unless the PR is explicitly updated and revalidated.
- Repository history must make it possible to reconstruct why a gate changed state.

## Canonical References

- `BLUEPRINT.md`
- `documentation/BLUEPRINT_V0_4_ROADMAP.md`
- `schemas/status.schema.json`

## Completion Signal

The skill is complete only when its required outputs exist in the repository, the relevant Blueprint checks/gates can be evaluated from evidence, and no stop condition remains unresolved.
