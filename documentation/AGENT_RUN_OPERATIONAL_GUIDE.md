# Agent Run Operational Guide

## Purpose

This guide turns the proposal-stage multi-agent protocol into a reusable execution bundle.

A governed run is a directory with this minimum shape:

```text
agent-run/
├── task-packet.yaml
├── orchestration.yaml
└── handoffs/
    ├── 01-...
    ├── 02-...
    └── 03-...
```

Validate it with:

```bash
python scripts/validate-agent-run.py path/to/agent-run
```

The command reuses the canonical Blueprint schemas and protocol validator. A project does not need a task-specific Python validator.

## Required semantics

- `task-packet.yaml` describes the bounded approved work.
- `orchestration.yaml` owns participant applicability, execution order, state, candidate HEAD and handoff ledger.
- `handoffs/*.yaml` contains only executed evidence-backed handoffs.
- planned future handoffs belong in `expected_handoffs`, not in the executed ledger.
- when `evidence_plane.mode = DETACHED`, the candidate HEAD must be concrete and frozen.
- if candidate and evidence share a repository, the evidence ref must differ from the candidate working branch.
- every handoff document in the bundle must be declared by `orchestration.handoffs`.
- every declared executed handoff must have exactly one corresponding document in the bundle.
- human merge approval remains outside automated validation.

## Lifecycle

A typical run evolves without replacing the directory:

```text
RECEIVED
→ ANALYZING
→ PLANNING
→ TASK_PACKET_BOUNDARY
→ IMPLEMENTING
→ VALIDATING
→ AUDITING
→ READY_FOR_HUMAN_DECISION
→ CLOSED
```

At each transition:

1. update orchestration state;
2. add the role-owned handoff that actually occurred;
3. keep future transitions only in `expected_handoffs`;
4. rerun `validate-agent-run.py`;
5. stop on validation failure instead of advancing optimistically.

## Candidate freeze

Before independent verification and final audit, freeze the delivery candidate:

```text
working branch + pull request + exact HEAD
```

QA, Security, Documentation, specialist evidence and Auditor evidence must refer to the governed candidate HEAD when the protocol requires exact-head evidence.

Evidence records created after candidate freeze must not mutate the candidate branch they certify.

## Consumer adoption

The canonical implementation lives in SoftwareDevelopmentBlueprint, but each consumer chooses whether and when to adopt it.

A consumer may copy the bundle shape and run the validator from its adopted Blueprint tooling. That does not automatically upgrade the consumer's Blueprint version or enable every agent.

## Canonical example

`templates/agent-run.example/` is the continuously validated reference bundle.

It demonstrates:

```text
Orchestrator
→ Analyst
→ Planner
→ TASK_PACKET_BOUNDARY
→ Frontend
→ QA
```

at the `VALIDATING` state. Auditor-to-human remains future intent until audit actually occurs.

## Master rule

```text
ONE REUSABLE BUNDLE
+
CANONICAL VALIDATOR
+
EXACT EVIDENCE
!=
ONE-OFF PILOT SCRIPT
```
