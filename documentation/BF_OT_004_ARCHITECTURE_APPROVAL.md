# BF-OT-004 — Architecture approval proposal

Status: PROPOSED. Depends on BF-OT-003 and PR #77. No stable release or automatic consumer adoption.

Initialize an empty project ledger (137 PENDING decisions, no preselection):
`python scripts/validate-architecture-approval.py --init architecture-approval.json --repository owner/repo --owner "Owner identity" --mode GREENFIELD`

Validate:
`python scripts/validate-architecture-approval.py --validate architecture-approval.json`

Exit 1 means BLOCKED. Exit 0 for validation means READY_FOR_HUMAN_REVIEW only, never implementation authorization. Exit 0 for initialization means file generation only. Owner must authenticate each decision evidence, confirm actual applicability and compatibility, and approve the exact ledger in a governed review. A hash is integrity binding, not a digital signature. Evidence identifiers must be distinct per decision; a single conversation may contain multiple individually identified approvals. Never fabricate evidence. The validator does not independently retrieve or authenticate it.

All 137 catalog entries must exist in order. PENDING, PROPOSED, REJECTED, REOPENED block. APPROVED needs selection, recommendation, rationale, verified compatibility and owner evidence; NOT_APPLICABLE needs explicit rationale and owner evidence. Changes to a record invalidate its approval digest. Reopen affected decisions, increment revision, invalidate dependent evidence and re-review. Scope/dependency impact analysis is still manual. Catalog hash and source commit are pinned. Alternative architecture requires bounded BF-P01 exception; BF-P02 exceptions are permitted by schema, QA/security waivers forbidden. Exceptions require identity, project, decision revision, scope, rationale, risk, mitigation, evidence, expiration, tests. Review trigger evaluation and evidence authenticity require human review.

Initial conditional checks cover explicit Web, Android/iOS, REST/GraphQL and public-indexable selections. They are illustrative guards, not a complete applicability or compatibility engine: custom option labels, composite platform choices, cross-decision contradictions, provider compatibility, exception content and project-mode consistency require independent semantic review. BF-OT-005/006 must wire the readiness report into agents and existing architecture gates; no automatic implementation permission today. Synthetic fixtures do not represent actual project approvals.

Use repository-owned decision ledger alongside existing ADRs, architecture_ready and client_architecture_ready. Keep existing approved Brownfield scope until explicitly adopting the proposal. No mutation of consumer repositories.
