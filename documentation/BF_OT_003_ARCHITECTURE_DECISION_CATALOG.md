# BF-OT-003 — Architecture decision catalog proposal

Status: PROPOSED; dependent on BF-OT-002 / PR #76. The catalog preserves ARC-001..137 from the owner discussion. No project technology is chosen by this artifact, no consumer upgrade, no stable version mutation.

## Interview
For every entry ask the Spanish question, describe alternatives in context, verify actual version/platform compatibility, explain tradeoffs, recommend with reasons, obtain explicit individual owner resolution and record it in the consumer repository. Options may be combined when compatible or extended with a new choice. No default selection is permitted. Related decisions are compatibility review links, not hard dependency ordering; revisit earlier answers if later answers conflict. Applicability must be evaluated for each entry; justified owner-approved N/A is not a waiver of applicable constitution policies. For example, lack of a backend can justify N/A for a server framework; a web application with relevant UI changes cannot use N/A to skip Browser QA. Clean Architecture is mandatory default, alternative requires explicit exception. API HTTP contracts use OpenAPI and Postman operational QA where applicable. Never infer approval from silence or a broad approval of this catalog.

## Categories
project (8), backend (8), data (11), api (11), web (13), admin (9), client (13), security (12), features (11), operations (13), quality (13), discoverability (7), api_qa (8). Total 137.

ARC-045 means server-state queries (loading, cache, refetch, errors), distinct from ARC-044 client state. ARC-046 means responsive design priority and actual layout across devices. ARC-123..129 cover search and AI discoverability, including separate crawler search/training permissions; indexing/citation is not guaranteed. ARC-130..137 cover importable executable Postman collections and API QA, not just a list of requests.

## Relationship to existing Blueprint
Retain architecture_ready and client_architecture_ready gates, ADRs, platform-specific baselines, API authority model, versioned consumer opt-in and Brownfield ALIGN, DO NOT REWRITE. Catalog records will supplement these, not replace them. WebBlueprint and ApiBlueprint are candidate reuse sources only when the owner selects compatible stacks. The catalog is a question registry with inline illustrative option labels, not a verified technology/version compatibility database. BF-OT-004 implements the individual ledger, applicability/exception checks, evidence binding and blocking semantics; BF-OT-005/006 wire agents. A separate technology registry with stable option IDs and verified version facts remains a follow-up. No runtime compliance claim.

## Validation
Schema enforces structure and owner approval semantics. Validator pins the original ID/category map, detects duplicate JSON keys, missing or duplicate decisions, invalid/self links, preselected options, prohibited auto-approval and missing policy anchors. Validation does not certify factual compatibility or correctness of every natural-language question; independent review required. New questions may be added only via versioned catalog evolution, not by silently dropping existing IDs.
