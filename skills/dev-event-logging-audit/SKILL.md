---
id: dev-event-logging-audit
title: Technical Logging and Business/Security Audit
version: 0.5.0-dev
status: materialized
category: core
applies_to:
  - greenfield
  - brownfield
phases:
  - architecture_security_data
  - api_implementation
  - api_qa
  - functional_interface_slice
  - integration_qa
  - operations
canonical_references:
  - BLUEPRINT.md
  - catalog/checks.yaml
  - catalog/gates.yaml
  - schemas/evidence.schema.json
  - schemas/functional-interface-slice.schema.json
---

# Technical Logging and Business/Security Audit

## Purpose

Implement observability with a strict distinction between technical/operational logs and durable business/security audit records. Client request correlation supports diagnosis and traceability, but it must not become a second competing audit authority.

## When to Use

Use during architecture, backend implementation, API QA, functional client delivery, integrations, administration, SaaS/tenant design and operations whenever events must be diagnosable or accountable.

## Inputs

- Security/data architecture.
- Identity/actor model and request/correlation strategy.
- Business workflows and sensitive state changes.
- Retention/privacy requirements.
- Integration and administrative operations.
- Client Architecture/Functional Slice observability requirements when client delivery applies.

## Procedure

1. Classify events into technical/operational logging versus durable audit. Logs diagnose software; audit proves who/what/when/outcome for business or security-significant actions.
2. Define an audit event taxonomy with stable event codes for authentication, role/permission changes, sensitive CRUD, meaningful state transitions, financial/administrative actions, integrations, critical security/errors and tenant/SaaS events when applicable.
3. Persist durable audit records with timestamp, actor/subject, action/event code, target entity, outcome, request/correlation ID, tenant context where applicable and only the minimum sanitized before/after metadata justified by the event.
4. Sanitize recursively. Passwords, hashes, tokens, reset secrets, API keys, authorization headers and sensitive payload fields must never be persisted merely because they appeared in a request.
5. Keep durable audit append-oriented and protected from ordinary application update/delete flows. Define retention, access, export/search and tamper/administrative override policy appropriate to risk.
6. Propagate request/correlation IDs through transport, logs, audit, jobs and integrations so one operation can be reconstructed across layers.
7. In client architecture/functional implementation, surface request IDs in sanitized support/error context when useful, but do not persist client-side business/security events as an undocumented parallel audit store. Server/API audit remains authoritative unless architecture explicitly defines otherwise.
8. Ensure client telemetry redacts secrets/PII and distinguishes diagnostic errors from durable business evidence.
9. Test audit during API QA with real operations: assert event code, actor, target/outcome, correlation ID and absence of secrets.
10. During Integration QA, verify correlation continuity across the client/API boundary and confirm UI observability does not weaken backend audit guarantees.
11. For Brownfield, inventory existing logging and audit separately, preserving working infrastructure while closing demonstrated gaps rather than rewriting for style.

## Outputs

- Technical logging strategy.
- Durable business/security audit catalog and persistence rules.
- Sanitization/retention/access policy.
- End-to-end request/correlation propagation.
- Client observability boundary that does not duplicate durable audit.
- QA evidence for critical audit events and correlation continuity.

## Stop Conditions

- Technical logs are being treated as sufficient audit evidence for critical actions.
- Secrets/credentials can enter logs, telemetry or audit.
- Critical events lack actor/outcome/correlation context.
- Durable audit can be casually mutated/deleted by normal application flows.
- Client code is becoming a second authority for durable business/security audit without an explicit architecture decision.
- Retention/access controls are undefined for sensitive audit data.

## Guardrails

- Logs and audit serve different purposes and may use different stores/retention.
- Durable audit is a required cross-cutting capability for critical events.
- Request IDs support traceability but are not authentication/authorization.
- Client telemetry/correlation supports diagnosis; authoritative durable audit remains server-side by default.
- Record enough to prove significant events without creating a secondary data leak.

## Canonical References

- `BLUEPRINT.md`
- `catalog/checks.yaml`
- `catalog/gates.yaml`
- `schemas/evidence.schema.json`
- `schemas/functional-interface-slice.schema.json`

## Completion Signal

Complete only when logging and audit responsibilities are explicitly separated, critical server-side events are durably/safely evidenced, correlation can be followed through client/API/runtime where applicable, secrets are excluded, and no undocumented client-side audit authority competes with the canonical backend record.
