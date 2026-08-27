# Software Development Blueprint - Current State

> CURRENT CHECKPOINT / DERIVED SUMMARY  
> Fecha de cierre representada: **2026-08-27 America/Montevideo**.  
> Release representada: **0.5.1**.

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

Versión estable: **0.5.1**

Conteos del núcleo:

- **28 fases**;
- **135 checks**;
- **18 gates**;
- **14 skills materializadas**;
- **25 skills planificadas**.

El único incremento de catálogo respecto de 0.5.0 es un check REQUIRED de Architecture Implementation Conformance.

## 3. Cambio central de 0.5.1

El piloto CUSA-Digital demostró una brecha real: una arquitectura puede estar correctamente diseñada y aprobada y, al mismo tiempo, la implementación puede desviarse de ella aunque endpoints, OpenAPI, Postman y QA funcional estén verdes.

0.5.1 añade:

`api.architecture_implementation_conformance`

Invariante:

`architecture design acceptance != architecture implementation conformance`

El check pertenece a `api_implementation` y es requerido tanto por `api_implemented` como por `api_gate`.

La evidencia debe verificar el contrato arquitectónico realmente aprobado. Cuando sea viable, se prefieren assertions ejecutables: dependency rules, architecture fitness functions, module-boundary tests, layer isolation tests o bindings de ports/adapters. El Blueprint no prescribe una arquitectura o framework universal.

## 4. Pipeline canónico

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

## 5. Interface Scope e Interface Inventory

El modelo 0.5.x separa:

```text
Requirements Ready
  -> Interface Scope Baseline
  -> Architecture/API design
  ...
  -> API Gate
  -> Executable Interface Inventory
```

El baseline temprano describe interfaces observadas/intencionadas sin inventar bindings. El inventario ejecutable posterior al API Gate reconcilia el alcance con permisos, dependencias y `operationId` autoritativos.

## 6. Functional Interface Slice

Unidad canónica de ejecución cliente: `interface_slice + platform`.

Lifecycle:

`INVENTORIED -> READY -> IN_PROGRESS -> FUNCTIONAL -> ACCEPTED`

Visual & Functional Review e Integration QA son gates independientes, no estados lifecycle.

`FUNCTIONAL` requiere DoD con API real, auth/RBAC, forms/errors, observabilidad/correlation, responsive, accesibilidad, tests, traceability, ausencia de hardcoded authoritative business data y ausencia de capacidades inventadas.

`ACCEPTED` añade Review PASS, Integration QA PASS, aceptación humana explícita y cero blockers abiertos.

## 7. BLOCKED_BY_API

`BLOCKED_BY_API` es un overlay sobre el lifecycle. Se usa solo ante una carencia o incompatibilidad autoritativa de API: data, operation, permission, state, transition o contract capability.

Conserva el último lifecycle válido. La solución se realiza en una frontera API/backend separada y el slice solo reanuda con evidencia de resolución/revalidación.

Errores normales de frontend o incertidumbre visual no se etiquetan como `BLOCKED_BY_API`.

## 8. Evolución API

El primer `api_gate` continúa siendo project-scoped.

Cambios posteriores usan `schemas/api-impact.schema.json`:

- `operationId` local -> revalidación de consumidores afectados;
- auth/authorization/security/error/versioning u otros cambios cross-cutting -> posible escalado a plataforma/proyecto;
- evidencia aceptada no relacionada se preserva por defecto.

Una remediación puramente arquitectónica no fabrica un API impact si el contrato externo no cambió.

## 9. Client Architecture

Modelo efectivo:

```text
Platform Client Architecture Baseline
  + Slice Architecture Binding/Override
  = Effective Client Architecture Contract
```

La baseline concentra decisiones reutilizables de plataforma. El binding declara inventario, rutas, permisos, API revision/operationIds, estados, idempotencia y overrides específicos del slice.

`visual_references.mode = none` es válido. Mockups no son una dependencia universal.

## 10. Experiencia visual

Design System es requerido para client delivery. Visual Identity es condicional.

Mockups/prototypes son condicionales y, cuando se usan:

`GENERATED != REVIEWED != APPROVED`

El review final se realiza sobre el cliente funcional real, no solo sobre imágenes.

## 11. Cross-Artifact Semantic Integrity

Los validadores comprueban la cadena real:

`requirement -> interface -> permission -> operationId -> slice -> client architecture -> evidence/test -> review/QA -> acceptance`.

Se rechazan IDs ficticios, operationIds inexistentes, namespaces de plataforma incompatibles, permisos inventados, evidencias inexistentes, acceptance sin gates y blockers ocultos.

Validadores principales:

- `scripts/validate-artifact-graph.py`
- `scripts/validate-experience-artifacts.py`
- `scripts/validate-client-architecture.py`
- `scripts/validate-skills.py`
- `scripts/validate-reference-pilot-compliance.py`
- `scripts/validate-architecture-conformance.py`
- `scripts/validate-release.py`

## 12. Skills

Se mantienen **14 skills materializadas** y **25 planned**.

0.5.1 no modifica el procedimiento de ninguna skill materializada, por lo que el componente `catalog/skills.yaml` y sus frontmatters conservan provenance 0.5.0 y se reutilizan de forma compatible.

Catalogar no equivale a materializar.

## 13. Versionado de componentes

`VERSION = 0.5.1` identifica la release raíz.

Componentes modificados en este patch:

- `catalog/checks.yaml`: 0.5.1;
- `catalog/gates.yaml`: 0.5.1;
- `schemas/project.schema.json`: consumer declaration 0.5.1;
- `schemas/status.schema.json`: consumer declaration 0.5.1;
- templates canónicos project/status: 0.5.1.

Los componentes cuyo contrato no cambió pueden conservar provenance 0.5.0, incluidos phases, workflows, skills y schemas de experiencia. Los validadores hacen explícita esta matriz de compatibilidad.

## 14. Consumidores y adopción

No existe automatic consumer upgrade.

Una release estable del Master no cambia `.blueprint/status.yaml`, código, schemas o comportamiento de un consumidor. La adopción se realiza mediante:

1. verificación live del Master y del consumidor;
2. Compliance Review entre versión declarada y versión objetivo;
3. clasificación KEEP / ADOPT / MIGRATE / DEFER / N/A;
4. aprobación explícita;
5. PR de adopción separada;
6. revalidación según el impacto real.

CUSA-Digital consume actualmente Blueprint 0.5.0. Su `main` fue verificado en `95309161db3522f61b636b705b183b62e6395ede` tras PR #31, donde la implementación fue remediada para conformar con la arquitectura G3 sin cambiar las 45 operaciones API aceptadas.

Ese hallazgo originó el hardening 0.5.1, pero **CUSA no adopta 0.5.1 automáticamente**. Design System permanece fuera de autorización hasta un Compliance Review 0.5.0 -> 0.5.1 y una adopción explícita posterior al cierre estable de esta release.

## 15. Release closure y tag

El manifest machine-readable es `documentation/BLUEPRINT_V0_5_1_RELEASE.json` y las notas están en `documentation/BLUEPRINT_V0_5_1_RELEASE_NOTES.md`.

La etiqueta `v0.5.1` se crea únicamente después de fusionar el PR de release, verificar el árbol aprobado en `main` y confirmar CI post-merge.

Los manifests/tags de 0.4.0 y 0.5.0 permanecen historia verificable y no se reescriben.

## 16. Fuera de 0.5.1

No forma parte de la release:

- mutar automáticamente consumidores;
- iniciar Design System o UI de CUSA desde el Master release PR;
- imponer Clean Architecture, Laravel o un layout de carpetas universal;
- materializar las 25 skills todavía planned;
- construir Blueprint Control Center;
- declarar Blueprint 1.0.
