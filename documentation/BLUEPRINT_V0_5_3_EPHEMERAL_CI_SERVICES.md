# Blueprint 0.5.3-dev - Ephemeral CI Service Containers

> Development hardening boundary over stable Blueprint 0.5.2.  
> This document is normative only inside the `0.5.3-dev` proposal until a separate stable release closure is explicitly approved.

## 1. Problem

Self-hosted runners may need MySQL, PostgreSQL, Redis or similar infrastructure during CI. A runner is an execution agent; it is not a database installation boundary.

Two anti-patterns are forbidden for CI service dependencies:

1. installing a dedicated persistent database/cache instance for every runner;
2. sharing one mutable persistent database/cache runtime across unrelated jobs or projects.

Both approaches create hidden coupling, port conflicts, state leakage and concurrency hazards.

## 2. Canonical model

The canonical runtime model is:

```text
self-hosted host
  -> one container engine
  -> reusable/pull-through image cache
  -> isolated ephemeral service containers per job
```

The invariants are:

```text
runner != service instance
shared image cache != shared mutable runtime
CI service lifecycle = ephemeral per job
host port allocation = dynamic
```

A new runner does not imply a new MySQL/PostgreSQL/Redis installation. A job requests only the services it needs.

## 3. Service isolation

When `runner.service_containers = true`:

- `runner.container_engine` MUST be `docker`;
- the runner OS MUST be Linux for this contract;
- `services.isolation` MUST be `per_job`;
- `services.lifecycle` MUST be `ephemeral`;
- `services.shared_runtime_instances` MUST be `false`;
- service health checks are REQUIRED;
- repository/project data MUST NOT depend on residual state from a previous job.

A container may be removed at job completion without affecting later jobs.

## 4. Dynamic host ports

Workflows MUST NOT require a fixed host port for CI service containers when GitHub Actions can allocate one dynamically.

Forbidden pattern:

```yaml
services:
  mysql:
    image: mysql:8.4
    ports:
      - 3306:3306
```

Canonical pattern:

```yaml
services:
  mysql:
    image: mysql:8.4
    ports:
      - 3306
```

The workflow discovers the assigned host port from the GitHub Actions service context:

```yaml
env:
  DB_HOST: 127.0.0.1
  DB_PORT: ${{ job.services.mysql.ports[3306] }}
```

Equivalent rules apply to PostgreSQL `5432`, Redis `6379` and other declared service-container ports.

This permits concurrent jobs to map, for example:

```text
job A mysql:3306 -> host:32771
job B mysql:3306 -> host:32772
job C redis:6379 -> host:32773
```

without requiring global port coordination.

## 5. Shared images, isolated runtimes

Container images MAY be shared/cacheable on the self-hosted machine. Runtime instances MUST NOT be shared across unrelated jobs.

The canonical development catalog is:

| Service | Image | Container port |
| --- | --- | ---: |
| MySQL | `mysql:8.4` | 3306 |
| PostgreSQL | `postgres:16` | 5432 |
| Redis | `redis:8.10.1` | 6379 |

The catalog represents approved reference images available to workflows. A project activates only the subset it actually requires.

Floating `:latest` tags are forbidden. Image changes require an explicit versioned change so CI behavior does not silently drift.

## 6. Project Docker independence

This policy governs CI runner infrastructure only.

It does not change the product capability contract:

```text
project capabilities.docker = false
runner service_containers = true
runner container_engine = docker
```

remains valid.

## 7. Databases and caches for local development

Persistent local-development services are a separate concern. A developer MAY intentionally run a persistent MySQL, PostgreSQL or Redis instance for local development, but CI MUST NOT require that local instance when the workflow declares service containers.

The distinction is explicit:

```text
local development service != CI service container
```

A local development service must not reserve a fixed host port that an existing workflow incorrectly assumes it owns. Dynamic CI port assignment removes that dependency.

## 8. Security and evidence

The existing 0.5.2 CI execution-portability rules remain unchanged:

- trusted code only on persistent self-hosted lanes;
- no persistent repository secrets;
- least-privilege permissions;
- workspace cleanup;
- runner update policy;
- exact-head CI evidence;
- pre-execution infrastructure failures distinct from test failures;
- human approval separate from CI.

Service-container isolation complements these rules; it does not replace them.

## 9. Consumer adoption

This hardening does not auto-upgrade any consumer.

After a stable 0.5.3 release exists, consumers may adopt it through the normal Compliance Review process. A project may independently fix a hard-coded CI host-port conflict before full Blueprint adoption when that fix preserves its existing product contracts and governance boundary.

## 10. Stable-release boundary

This hardening PR MUST NOT:

- change root `VERSION` from stable `0.5.2`;
- create or move a stable tag;
- merge without exact-head CI and explicit human approval;
- mutate consumer repositories automatically.

A separate release-closure boundary is required to publish stable `0.5.3`.
