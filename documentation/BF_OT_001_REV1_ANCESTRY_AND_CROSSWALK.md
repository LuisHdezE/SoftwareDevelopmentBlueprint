# BF-OT-001 — REV1: ancestry, CI and policy crosswalk

Status: PARTIAL AUDIT; proposal only. Date: 2026-11-25 America/Montevideo.

## Verified ancestry
GitHub compare API:
- main fcd92a52596db5ddd070002eb3f7f2ce2eef0bbf -> consumer-agent-adoption 6683bd5e06bab6c53188f7e7a93caf6e7d678879: ahead 200, behind 0; merge base is main; 69 listed changed paths (count not used as acceptance criterion). Changes are agent definitions, proposal catalogs, schemas, validators, fixtures, workflows and README; no VERSION/DEVELOPMENT_VERSION change in compare.
- agent-system-validation 514520a7ade4914b6318fbcc063391958f764df9 -> consumer-agent-adoption: ahead 12, behind 0, 13 changed paths.
- consumer-agent-adoption -> BF-OT-001 initial db237b185c8a9964054165e8f3782996428d2c64: ahead 1, behind 0, one new document.
- PR #74 is draft, mergeable=true at inspection; no merge authorized.

Open chain #50–#61, #73, #74. PRs #62,63,64,65,67,68,69,70,72 merged into agent-system-validation; #71 closed unmerged. Inspect #71 detached evidence separately if needed. No automatic closure or merging of stacked PRs.

## Historical CI observed by exact head query
| PR | HEAD | Returned workflows | Result |
|---|---|---|---|
| 50 | 6c658ac9bb2eb231f61fd9f1d0e59d9dc142e983 | none returned | UNKNOWN |
| 55 | b3de0bd59b71e5284028a6d0d1e68cbe7d4c976d | Agent Protocol | success |
| 60 | c7f7783b638bef45f8c9db9cb91e8cb01ba666e9 | Public Discoverability, Agent Protocol | success |
| 61 | 514520a7ade4914b6318fbcc063391958f764df9 | Agent System, Planner Boundary, Agent Protocol | success |
| 73 | 6683bd5e06bab6c53188f7e7a93caf6e7d678879 | Agent Workflow Integration, Agent Protocol | success |
| 74 initial | db237b185c8a9964054165e8f3782996428d2c64 | none returned | UNKNOWN |

Queries are historical PR-triggered runs, not fresh execution. Missing runs do not imply failure or PASS.

## Canonical crosswalk at candidate SHA
| Owner requirement | Existing authority | Disposition |
|---|---|---|
| Clean Architecture mandatory default | BLUEPRINT.md §9.1 explicitly does not universally prescribe it; agents/architect.md §6–7 allows approved alternatives | CHANGE in future governed release; explicit exception approval; preserve brownfield alignment and existing consumers |
| Individual architecture approval | catalog/gates.yaml architecture_ready already requires ADRs, security/data architecture, API policy | EXTEND existing gate with per-decision approval ledger; apply also to API-optional paths; do not add duplicate gate without need |
| Early endpoint inventory | api_contract_ready before implementation; OpenAPI unique operationId canonical | EXTEND traceability and explicit early catalog; do not duplicate formal contract |
| Postman import and automated QA | postman_ready, api_qa_pass; skills/dev-postman-qa/SKILL.md steps 1–11 already require versioned collection, environments, auth workflows, assertions, negative scenarios, operationId coverage, pinned CLI and reports | KEEP; verify actual execution, add explicit chained flow/cleanup and stronger coverage checks as gaps warrant |
| Browser QA | agents/qa.md independent authority, visual/functional review; existing platform-specific QA | EXTEND explicit browser runtime evidence and fail-closed behavior; verify existing checks before changes |
| SEO/GEO/AEO | specialist:search-ai-discoverability and discoverability_ready proposal | KEEP and validate integration; mandatory when PUBLIC_INDEXABLE |
| Learning | not fully inventoried | INVESTIGATE; propose reviewed versioned knowledge |
| Cross-platform adapters | canonical contract and consumer run bundles; ControlCenter adapter ADR located | INVESTIGATE native adapter support and reuse |
| Orchestrator | agents/orchestrator.md minimum-agent principle and handoffs | KEEP; no superagent |

## Recommended integration route
Keep the candidate branch lineage intact. After full local validation, propose a single consolidated review against main of the exact candidate tree (rather than merging twelve stacked PRs blindly). Compare all files and run all inherited validators plus negative cases on the consolidated HEAD. Review any existing open PR overlap. Human approval for merge/release remains required. No release version choice or promotion yet; 0.5.5 RC scope remains frozen.

## Remaining before BF-OT-001 acceptance
Full content inventory of WebBlueprint, ApiBlueprint, ControlCenter, Dashboard; branch/PR evidence coverage beyond sampled heads; inspect existing architecture templates and browser checks; full validation on exact candidate and independent review. No new tests executed in this revision.
