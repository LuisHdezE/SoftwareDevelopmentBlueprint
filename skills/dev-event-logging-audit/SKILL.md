---
id: dev-event-logging-audit
title: Technical Logging and Business/Security Audit
version: 0.4.0-dev
status: materialized
category: core
applies_to:
  - greenfield
  - brownfield
phases:
  - architecture_security_data
  - api_implementation
  - api_qa
  - integration_qa
  - operations
canonical_references:
  - BLUEPRINT.md
  - catalog/checks.yaml
  - catalog/gates.yaml
  - schemas/evidence.schema.json
---

# Technical Logging and Business/Security Audit

## Purpose

Implement event observability with a strict distinction between technical/operational logs and durable business/security audit records.

## When to Use

Use during architecture, backend implementation, API QA, integrations, administration, SaaS/tenant design, and operations whenever events must be diagnosable or accountable.

## Inputs

- Security/data architecture.
- Identity/actor model and request/correlation strategy.
- Business workflows and sensitive state changes.
- Retention/privacy requirements.
- Integration and administrative operations.

## Procedure

1. Classify events into technical/operational logging versus durable audit. Technical logs diagnose software; audit proves who/what/when/outcome for business or security-significant actions.
2. Define an audit event taxonomy with stable event codes. Include authentication events, role/permission changes, sensitive CRUD, meaningful state transitions, financial actions, administrative actions, integrations, critical errors/security events, and tenant/SaaS events where applicable.
3. Persist audit records with timestamp, actor/subject, action/event code, target entity, outcome, request/correlation ID, tenant context when applicable, and sanitized before/after or metadata only when justified.
4. Sanitize recursively. Passwords, hashes, tokens, reset secrets, API keys, authorization headers, and sensitive payload fields must never be persisted in logs/audit merely because they appeared in a request.
5. Make durable audit append-oriented and protect it from ordinary application update/delete flows. Define retention, access controls, export/search needs, and tamper-detection/administrative override policy appropriate to risk.
6. Propagate request/correlation IDs from transport through logs, audit, jobs, and integration calls so one operation can be reconstructed across layers.
7. Test audit during API QA with real operations: assert event code, actor, target/outcome, correlation ID, and absence of secrets.
8. For Brownfield, inventory existing logging/audit separately and close gaps without rewriting working logging infrastructure solely for style.

## Outputs

- Technical logging strategy.
- Audit event catalog/taxonomy.
- Durable sanitized audit persistence rules.
- Request/correlation propagation.
- QA evidence for critical audit events.

## Stop Conditions

- Technical logs are being treated as sufficient audit evidence for critical actions.
- Secrets or credentials can enter logs/audit.
- Critical events lack actor/outcome/correlation context.
- Audit can be casually mutated/deleted by normal application flows.
- Retention/access controls are undefined for sensitive audit data.

## Guardrails

- Logs and audit serve different purposes and may have different stores/retention.
- Audit is a required cross-cutting capability for critical events.
- Do not over-log sensitive business payloads; record enough to prove the event without creating a secondary data leak.
- Correlation IDs support traceability but are not authentication or authorization.

## Canonical References

- `BLUEPRINT.md`
- `catalog/checks.yaml`
- `catalog/gates.yaml`
- `schemas/evidence.schema.json`

## Completion Signal

The skill is complete only when its required outputs exist in the repository, the relevant Blueprint checks/gates can be evaluated from evidence, and no stop condition remains unresolved.
