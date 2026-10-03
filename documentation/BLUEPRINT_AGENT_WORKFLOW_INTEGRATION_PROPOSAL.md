# Blueprint Agent Workflow Integration Proposal

## Status

This document defines a **proposal-stage integration overlay** between the Blueprint multi-agent protocol and the existing Blueprint workflow/gate model.

It does not modify stable Blueprint 0.5.4 semantics and does not modify the frozen 0.5.5-dev release candidate.

Protocol provenance:

`agent-protocol-proposal-1`

Integration provenance:

`agent-workflow-integration-proposal-1`

## Problem

The repository now has:

- canonical agent role contracts;
- machine-readable Task Packets;
- machine-readable Handoffs;
- machine-readable Orchestration State;
- fail-closed protocol validation.

What is still missing is a governed relationship between those artifacts and Blueprint's existing:

- Greenfield workflow;
- Brownfield workflow;
- phase/check/gate state;
- consumer-local `.blueprint/` artifacts.

Without an explicit integration boundary, two dangerous interpretations are possible:

1. agent completion status accidentally replaces Blueprint gate evidence;
2. Blueprint phase state is duplicated independently inside orchestration state.

This proposal forbids both.

## Core state rule

```text
.blueprint/status.yaml
        =
authoritative Blueprint phase/check/gate state
```

while:

```text
.blueprint/agents/orchestration.yaml
        =
task-routing and agent-coordination state
```

Therefore:

```text
AGENT STATUS != BLUEPRINT GATE STATUS
```

and:

```text
ORCHESTRATION STATE != BLUEPRINT STATUS
```

## Stable workflow preservation

The overlay inherits the stable Greenfield/Brownfield sequences.

It does not insert new stable phases.

Planner and Orchestrator are cross-cutting roles rather than new stable workflow phases.

Documentation and Auditor may also operate across phase boundaries.

## Gate relationship

Agent evidence is **additional traceability**, never a substitute for the checks already required by a stable gate.

Example:

```text
architecture_ready
    requires stable architecture checks
    +
    may require Architect handoff evidence

Architect ARCHITECTURE_READY
    alone
    does NOT make architecture_ready PASS
```

Likewise:

```text
Auditor READY_FOR_MERGE
    !=
release_gate PASS
    !=
human merge/release approval
```

These remain separate facts.

## Consumer opt-in

A consumer may adopt the proposal only through an explicit repository-owned decision.

Suggested artifact locations:

```text
.blueprint/
├── status.yaml                    # existing Blueprint authority
└── agents/
    ├── orchestration.yaml         # task routing state
    ├── task-packets/
    ├── handoffs/
    └── evidence/
```

The canonical role contracts remain in `SoftwareDevelopmentBlueprint/agents/`.

Consumers store only their own task state, handoffs and evidence.

## No automatic adoption

Publishing or merging these proposal artifacts in the canonical repository never modifies a consumer.

Adoption requires an explicit consumer decision and repository-owned changes.

## Human boundary

The proposal preserves:

```text
Auditor READY_FOR_MERGE
        ↓
Human approval
        ↓
Merge
```

The Auditor never gains merge authority.

## Future promotion

A later governed release lane may decide to:

- promote the protocol into a numbered Blueprint development version;
- integrate agent artifact locations into the canonical project manifest;
- add agent evidence types to the stable evidence registry;
- add machine-readable workflow/gate agent bindings to stable artifacts;
- expose orchestration state to Blueprint-ControlCenter.

None of those promotion steps are implied by this proposal alone.
