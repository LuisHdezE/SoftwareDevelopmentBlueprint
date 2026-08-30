# Software Development Blueprint - Current State

> CURRENT CHECKPOINT / DERIVED SUMMARY  
> Fecha de cierre representada: **2026-08-29 America/Montevideo**.  
> Release representada: **0.5.2**.

Este documento es un resumen humano. No sustituye a `BLUEPRINT.md`, `VERSION`, `catalog/`, `workflows/`, `schemas/`, `templates/`, `skills/` ni a la evidencia de los repositorios consumidores.

## 1. Autoridad

Cuando exista contradicción:

1. contratos/evidencia del consumidor para su versión declarada;
2. Blueprint canónico de esa versión;
3. este Current State;
4. reference pilots;
5. chat/historial.

GitHub versionado prevalece sobre handoffs conversacionales.

## 2. Blueprint estable

Repositorio: `LuisHdezE/SoftwareDevelopmentBlueprint`

Versión estable representada: **0.5.2**

Conteos del núcleo:

- **28 fases**;
- **135 checks**;
- **18 gates**;
- **14 skills materializadas**;
- **25 skills planificadas**.

0.5.2 no altera estos conteos respecto de 0.5.1.

## 3. Cambio central de 0.5.2: CI Execution Portability

Un piloto privado demostró que la semántica de evidencia CI no puede depender de la disponibilidad comercial de GitHub-hosted runners.

Invariantes:

`CI evidence semantics != runner ownership`

`pre-execution infrastructure failure != test failure`

0.5.2 estabiliza el contrato machine-readable:

`schemas/ci-runtime.schema.json`

con estrategias:

- `github_hosted`;
- `self_hosted`;
- `hybrid`.

El artifact CI runtime es CONDITIONAL. Un consumidor debe materializar `.blueprint/ci-runtime.yaml` cuando gestione o sobrescriba explícitamente la estrategia de ejecución, especialmente para `self_hosted` o `hybrid`.

## 4. Evidencia y exact-head

La portabilidad del runner no relaja gobernanza.

Continúa siendo obligatorio, cuando aplique:

- workflow/check sobre el SHA exacto candidato;
- workflow versionado por el repositorio;
- scope esperado de validación;
- logs/artifacts exigidos por el gate;
- decisión humana separada de CI.

Un job que termina antes de asignar runner o antes de ejecutar pasos es evidencia de infraestructura. No se clasifica como fallo de producto/test y tampoco como PASS.

## 5. Frontera self-hosted

Para Linux/x64 el selector canónico es:

`[self-hosted, linux, x64, blueprint]`

Un runner persistente self-hosted debe:

- ejecutar código confiable;
- excluir forks del lane persistente o enviarlos a hosted en estrategia híbrida;
- no persistir secretos del repositorio;
- usar permisos least-privilege;
- limpiar workspace;
- mantener política de actualización del runner.

El Blueprint Master usa un runner repository-scoped como primer adopter probado.

## 6. Docker del runner versus Docker del proyecto

`capabilities.docker` continúa describiendo la solución/proyecto.

No describe la infraestructura interna del runner.

Por tanto es válido:

```text
project capabilities.docker = false
runner service_containers = true
runner container_engine = docker
```

Docker usado solo para GitHub Actions `services:` no convierte Docker en requisito de la aplicación.

El perfil del Blueprint Master no necesita service containers y declara `container_engine: none`.

## 7. Architecture Implementation Conformance

0.5.2 conserva sin cambio el hardening estable de 0.5.1:

`api.architecture_implementation_conformance`

Invariante:

`architecture design acceptance != architecture implementation conformance`

El check pertenece a `api_implementation` y continúa siendo REQUIRED tanto por `api_implemented` como por `api_gate`.

Tests funcionales/API verdes no sustituyen esta evidencia.

## 8. Pipeline canónico

```text
Discovery / Brownfield Inspection + AS-IS + Gap Analysis
  -> Target Definition
  -> Requirements Ready
  -> Interface Scope Baseline Ready
  -> Architecture / Security / Data Ready
  -> API Contract Ready
  -> API Implementation + Architecture Implementation Conformance
  -> OpenAPI Valid
  -> Postman Ready
  -> API QA Pass
  -> API Gate
  -> Interface Inventory Ready
  -> Design System Ready
  -> Client Architecture Ready [slice + platform]
  -> Functional Slice Ready [slice + platform]
  -> Visual & Functional Review Pass [slice + platform]
  -> Integration QA Pass [slice + platform]
  -> Release Gate
  -> Operations
```

Visual Identity y Mockups/Prototypes son condicionales.

## 9. Functional Interface Slice

Unidad canónica de ejecución cliente: `interface_slice + platform`.

Lifecycle:

`INVENTORIED -> READY -> IN_PROGRESS -> FUNCTIONAL -> ACCEPTED`

Visual & Functional Review e Integration QA son gates independientes, no estados lifecycle.

`ACCEPTED` requiere Functional DoD PASS, VFR PASS con revisión humana completa, Integration QA PASS, aceptación humana explícita y ausencia de blockers abiertos.

## 10. BLOCKED_BY_API y evolución API

`BLOCKED_BY_API` continúa siendo overlay sobre el lifecycle y solo aplica ante una carencia/incompatibilidad autoritativa de API.

El primer `api_gate` sigue siendo project-scoped.

Cambios posteriores usan `schemas/api-impact.schema.json` y revalidación basada en impacto. Evidencia aceptada no relacionada se preserva por defecto.

## 11. Client Architecture y experiencia visual

Modelo efectivo:

```text
Platform Client Architecture Baseline
  + Slice Architecture Binding/Override
  = Effective Client Architecture Contract
```

Design System es requerido para client delivery. Visual Identity es condicional.

Mockups/prototypes son condicionales y, cuando se usan:

`GENERATED != REVIEWED != APPROVED`

El review final se realiza sobre el cliente funcional real.

## 12. Cross-Artifact Semantic Integrity

Los validadores comprueban la cadena real:

`requirement -> interface -> permission -> operationId -> slice -> client architecture -> evidence/test -> review/QA -> acceptance`.

Se rechazan IDs ficticios, operationIds inexistentes, namespaces incompatibles, permisos inventados, evidencias inexistentes, acceptance sin gates y blockers ocultos.

Validadores principales incluyen:

- `scripts/validate-artifact-graph.py`;
- `scripts/validate-experience-artifacts.py`;
- `scripts/validate-client-architecture.py`;
- `scripts/validate-skills.py`;
- `scripts/validate-reference-pilot-compliance.py`;
- `scripts/validate-architecture-conformance.py`;
- `scripts/validate-ci-runtime.py`;
- `scripts/validate-release.py`.

## 13. Versionado de componentes

`VERSION = 0.5.2` identifica la release raíz.

Componentes promovidos a 0.5.2:

- `schemas/ci-runtime.schema.json`;
- `templates/ci-runtime.example.yaml`;
- `ci/blueprint-master.runtime.yaml`;
- `schemas/project.schema.json`;
- `schemas/status.schema.json`;
- templates canónicos project/status;
- documentación y validación activa de release.

Componentes reutilizados:

- checks/gates: provenance 0.5.1;
- phases/workflows/skills/experience schemas: provenance compatible 0.5.0.

Los validadores hacen explícita esta matriz. No se re-etiquetan contratos sin cambio semántico.

## 14. Consumidores y adopción

No existe automatic consumer upgrade.

Una release estable del Master no cambia `.blueprint/status.yaml`, código, workflows ni comportamiento de un consumidor. La adopción requiere:

1. verificación live del Master y consumidor;
2. Compliance Review entre versión declarada y objetivo;
3. clasificación KEEP / ADOPT / MIGRATE / DEFER / N/A;
4. aprobación explícita;
5. PR de adopción separada;
6. revalidación según impacto real.

## 15. CUSA-Digital al cierre de 0.5.2

CUSA-Digital consume Blueprint 0.5.1 y permanece separado de esta release.

Estado live verificado al preparar el cierre:

- `main = e9d80ec90b0076d637e742516df0da6a51354a47`;
- CUSA-Digital PR #46 permanece OPEN y mergeable;
- head de PR #46: `9cfdc930c5e6c323858b2c1cf8371aa0332cb63d`;
- boundary: `public-marketplace + web / WEB-003 + WEB-004`;
- Functional Slice Ready = PASS;
- Visual & Functional Review = PASS;
- Integration QA = PASS y human-approved;
- lifecycle = FUNCTIONAL;
- final human acceptance = PENDING;
- Release Gate no se inicia por esta decisión.

El último intento exact-head con GitHub-hosted runners privados terminaba antes de ejecutar pasos, sin runner asignado. Ese hallazgo originó el hardening 0.5.2.

La publicación de 0.5.2 **no modifica PR #46 ni adopta automáticamente el runner en CUSA**. Después de la release estable, CUSA requiere Compliance Review `0.5.1 -> 0.5.2` y una frontera de adopción separada antes de revalidar/mergear PR #46.

## 16. Release closure y tag

El manifest machine-readable es `documentation/BLUEPRINT_V0_5_2_RELEASE.json` y las notas están en `documentation/BLUEPRINT_V0_5_2_RELEASE_NOTES.md`.

El hardening semántico fue aceptado mediante PR #22 y mergeado en `c043bead93e9c4ad6c806576623f228dae239216` después de seis workflows exact-head SUCCESS sobre un runner self-hosted real.

La etiqueta `v0.5.2` se crea únicamente después de fusionar el PR de release, verificar el árbol aprobado en `main` y confirmar CI post-merge sobre ese SHA exacto.

Los manifests/tags anteriores permanecen historia verificable y no se reescriben.

## 17. Fuera de 0.5.2

No forma parte de la release:

- mutar automáticamente consumidores;
- fusionar o cerrar CUSA-Digital PR #46;
- convertir Docker en requisito universal;
- debilitar exact-head CI;
- exponer repositorios privados para obtener hosted runners gratuitos;
- materializar las 25 skills todavía planned;
- construir Blueprint Control Center;
- declarar Blueprint 1.0.
