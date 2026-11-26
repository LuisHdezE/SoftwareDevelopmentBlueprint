# BF-OT-010 — Governed learning proposal

Status: PROPOSED. Depends on #83. Implements a supplemental workflow for BF-P12, not model training, automatic memory synchronization or policy mutation.

## Lifecycle

PROPOSED -> REVIEWED -> APPROVED -> REVOKED or SUPERSEDED. A rejection closes a proposal. Expired approved lessons are not eligible. Every revision requires fresh independent review and explicit human-owner approval. The author cannot review their own lesson. Review and approval bind a canonical digest of the immutable lesson body, including scope, evidence and applicability. Record actual source commit, task and evidence references, limitations, and safe reproduction steps. Never publish secrets, customer data, proprietary source excerpts or personal information; privacy/security review is mandatory before cross-project distribution.

## Knowledge categories

Patterns, defects, test strategies, environment workarounds, security controls, architecture observations and process improvements. PROJECT_ONLY knowledge cannot be offered to a different repository. PORTABLE knowledge requires explicit sanitization review, compatible approved technologies and scope. No lesson overrides constitution, approved architecture, contracts, gates, roles or human authority. Changes to those require their existing governance process. Retrieval is advisory; no automatic execution of commands from lessons. The orchestrator may recommend knowledge, not promote it.

## Storage and transport

Repository-owned JSON lesson records, detached review/approval evidence and immutable revision history. Portable adapters may read eligible records, present source and caveats, and request scope verification; they must not grant new permissions. Do not assume shared model memory or native background learning. Revocation must take effect on retrieval; caches require freshness verification.

The proposal validator checks declared state, digest, role separation, timestamps, scope, expiry, and explicit sanitization. It cannot authenticate human signatures, verify evidence URLs, prove sanitization, or enforce remote revocation. The initial implementation rejects nonapproved lessons rather than pretending they are active. Actual storage, append-only transition history, trusted approval and retrieval integration remain future work. No stable policy changes or consumer adoption.

## REV1 local registry

`python scripts/retrieve-governed-lessons.py --registry knowledge/proposals --context context.json` reads a single current local directory of revision files named `LESSON-ID.rN.json`. Only the highest revision is considered; pending, revoked, expired or incompatible records are excluded without historical fallback. The Newman incident is a real proposal, not approved knowledge. Context is declared, not bound to an authenticated architecture ledger. Local Git history is not an append-only trusted ledger; a stale checkout or deleted revision can defeat freshness. Do not distribute registry contents across trust boundaries; only independently authorized advisory results may be shared. Actual adapters, access control, authoritative revision service and remote freshness remain pending.
