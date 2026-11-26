# BF-OT-005 — Agent policy integration and capability gaps

Status: PROPOSED; dependent on PR #78. Twelve existing role documents updated, no new role authority or stable release. The registry is a projection of existing canonical roles; it does not replace agent-contract.schema.json, specialist-agents.proposal.yaml or workflow integration. Version proposal-2 describes role instructions only; protocol remains agent-protocol-proposal-1. Pin the exact source commit on adoption. Aliases are portable names, not runtime commands.

## Gap review
| Candidate | Existing coverage | Decision |
|---|---|---|
| mobile | frontend + platform architecture/QA skills | candidate conditional specialist; investigate Android/iOS native capability gap in platform pilot |
| desktop | frontend + architect + QA | candidate conditional specialist; verify distinct toolkit/runtime needs |
| legacy | analyst brownfield + architect | candidate conditional specialist for recovery/migration, no independent requirement approval |
| api | architect + backend + QA | retain existing split; no duplicate API authority |
| ux | analyst + frontend + QA | retain existing split; consider design skill before new role |
| admin | backend + frontend + architect | Filament/admin skill first |
| devops | architect + documentation + implementation + security | candidate conditional specialist for deployment and CI; human production authorization retained |
| learning | documentation + relevant specialist + auditor | implement governed learning workflow BF-OT-010 before deciding new role |
| integration | architect + backend + QA | skill first, no duplicate contract authority |
| data | database + analyst + backend | skill first; evaluate ETL/migration gap on actual tasks |

These are provisional decisions from role/skill inventory, not proof of runtime competence. No new specialists activated. Before adding one, establish a concrete capability gap, independent outputs, activation conditions, allowed statuses, fixtures and workflow impact. Do not duplicate QA/security/audit or human approval.

## Boundaries
The 12 role overlays apply only to explicitly adopted constitution scope. Existing stable consumer decisions stay authoritative; conflict blocks. The registry and validation check mappings and document presence, not semantic obedience. BF-OT-006 must implement runtime preconditions; BF-OT-004 ledger readiness does not authenticate owner evidence. Independent audit, actual IDE invocation and consumer adoption remain pending.
