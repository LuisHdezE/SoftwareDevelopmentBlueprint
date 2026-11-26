# Cross-Cutting Agent Lifecycle

Status: proposal for post-0.5.5 multi-agent governance.

## Purpose

The protocol separates governance participation from bounded Task Packet execution so cross-cutting roles do not masquerade as implementation agents.

## Participant classes

### Lifecycle governance

These roles shape, route, and govern work before or across Task Packet execution:

- `orchestrator`: cross-cutting from intake through the human decision boundary.
- `analyst`: establishes governed problem understanding and requirements before bounded execution.
- `planner`: converts approved understanding into an executable plan and Task Packets.

Analyst and Planner may complete their lifecycle work before a Task Packet enters execution. They are therefore not automatically members of `task_packet.required_agents`.

### Task execution

A Task Packet declares only the agents and specialists required to execute and independently verify that bounded task. Typical participants include:

- architect
- database
- backend
- frontend
- qa
- security
- documentation
- auditor
- `specialist:<slug>`

Applicability decides which of these are REQUIRED, OPTIONAL, or NOT_APPLICABLE.

### Human authority

`human` is a decision boundary, not an agent and never an execution-order participant.

Only Auditor may emit the terminal governed handoff to `human` with `READY_FOR_MERGE`. That recommendation never grants merge authority.

## Lifecycle

```text
USER
  -> Orchestrator
  -> Analyst
  -> Planner
  -> Task Packet boundary
  -> applicable execution / verification agents
  -> Auditor
  -> Human approval
```

The Orchestrator coordinates the complete lifecycle but does not absorb the responsibilities or verification authority of another role.

## Protocol consequences

1. Analyst -> Planner is a lifecycle-governance handoff.
2. Planner -> first Task Packet executor is the boundary handoff from planning into bounded execution.
3. Handoffs inside Task Packet execution require participants declared by Task Packet applicability.
4. Orchestrator may coordinate across the boundary without becoming the producer of another agent's evidence.
5. Human must never appear in `execution_order`.
6. Completion of Analyst or Planner does not certify implementation, QA, Security, specialist, Documentation, or Audit gates.
7. Auditor remains independently responsible for the terminal recommendation to the human decision boundary.

## Fail-closed rule

A validator must reject a protocol chain that uses an undeclared implementation participant while allowing explicitly classified lifecycle-governance participants to operate outside Task Packet applicability only within their governed lifecycle scope.
