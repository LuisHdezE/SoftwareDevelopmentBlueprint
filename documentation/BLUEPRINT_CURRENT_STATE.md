# Software Development Blueprint - Current State

> CURRENT CHECKPOINT / DERIVED SUMMARY  
> Fecha representada: **2026-08-27 America/Montevideo**.  
> Última release estable: **0.5.0**.  
> Línea activa de hardening: **0.5.1-dev**.

Este documento es un resumen humano. No sustituye a `BLUEPRINT.md`, `VERSION`, `catalog/`, `workflows/`, `schemas/`, `templates/`, `skills/` ni a la evidencia de los repositorios consumidores.

## 1. Autoridad

Cuando exista contradicción:

1. contratos/evidencia del consumidor para su versión declarada;
2. Blueprint canónico de esa versión;
3. este Current State;
4. reference pilots;
5. chat/historial.

GitHub versionado prevalece sobre handoffs conversacionales.

## 2. Blueprint estable y desarrollo activo

Repositorio: `LuisHdezE/SoftwareDevelopmentBlueprint`

Última versión estable: **0.5.0**.

`VERSION` permanece en **0.5.0** durante el hardening de patch. No se publica una nueva versión estable por modificar una rama de desarrollo.

Conteos estables 0.5.0:

- **28 fases**;
- **134 checks**;
- **18 gates**;
- **14 skills materializadas**;
- **25 skills planificadas**.

Candidata 0.5.1-dev de Architecture Implementation Conformance:

- **28 fases**;
- **137 checks**;
- **18 gates**;
- **15 skills materializadas**;
- **25 skills planificadas**.

El delta es deliberadamente pequeño: tres checks REQUIRED y una nueva skill, sin crear fases ni gates artificiales.

## 3. Cambio central de 0.5.0

0.5 separa dos momentos que 0.4 trataba demasiado tarde:

```text
Requirements Ready
  -> Interface Scope Baseline
  -> Architecture/API design
  ...
  -> API Gate
  -> Executable Interface Inventory
```

El baseline temprano describe interfaces observadas/intencionadas y puede registrar necesidades API sin inventar bindings. El inventario ejecutable posterior al API Gate reconcilia el alcance con permisos, dependencias y `operationId` autoritativos.

## 4. Hardening 0.5.1-dev: Architecture Implementation Conformance

El piloto CUSA-Digital demostró una brecha del Core 0.5.0: era posible tener Architecture Ready, API Implemented y API QA en PASS mientras nadie comprobaba que la implementación real respetara las fronteras arquitectónicas aprobadas.

La corrección introduce tres checks canónicos:

1. `architecture.implementation_constraints` en `architecture_security_data`;
2. `architecture.implementation_conformance` en `api_implementation`;
3. `architecture.conformance_guard` en `api_implementation`, con verificación `automatic`.

La nueva regla es:

```text
functional correctness != architecture implementation conformance
```

`architecture_ready` exige restricciones implementables y verificables. `api_implemented` exige conformidad de la revisión exacta y un guard ejecutable requerido en CI. `api_gate` vuelve a exigir las tres comprobaciones antes de client delivery.

El contrato machine-readable es `schemas/architecture-conformance.schema.json`, con ejemplo en `templates/architecture-conformance.example.json`.

La skill reusable es `dev-architecture-conformance`.

La validación automática está en `scripts/validate-architecture-conformance.py` y `.github/workflows/blueprint-architecture-conformance-validation.yml`.

Clean Architecture no se convierte en un dogma universal. El Blueprint exige conformidad con la arquitectura aprobada por cada proyecto. Si el proyecto aprueba Clean/Hexagonal, entonces se validan sus restricciones de dependencia y separación; si aprueba otra arquitectura, se validan las restricciones equivalentes de ese contrato.

## 5. Pipeline canónico

La forma de la secuencia permanece estable:

```text
Discovery / Brownfield Inspection + AS-IS + Gap Analysis
  -> Target Definition
  -> Requirements Ready
  -> Interface Scope Baseline Ready
  -> Architecture / Security / Data Ready
  -> API Contract Ready
  -> API Implementation
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

La diferencia 0.5.1-dev es que Architecture Ready, API Implemented y API Gate tienen ahora obligaciones explícitas de conformidad de implementación.

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

Un refactor de conformidad arquitectónica que no cambia contrato puede preservar la API baseline, pero debe probar por separado regresión funcional y conformidad arquitectónica. Si el refactor cambia el contrato autoritativo, vuelve al flujo normal de API impact.

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

El hardening 0.5.1 añade una cadena previa de ingeniería del servidor:

`approved architecture -> verifiable constraints -> implementation revision -> CI conformance guard -> api_implemented/api_gate`.

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

Estables en 0.5.0: **14** materializadas.

Candidata 0.5.1-dev: **15** materializadas, añadiendo `dev-architecture-conformance`.

Las 25 restantes siguen `planned`; catalogarlas no equivale a materializarlas.

## 13. Brownfield y reference pilots

Brownfield mantiene **ALIGN, DO NOT REWRITE** y la separación `OBSERVED / INFERRED / PROPOSED`.

Architecture Conformance en Brownfield se evalúa contra el TO-BE aprobado. No autoriza reescrituras solo por estética arquitectónica y puede registrar excepciones legacy aceptadas cuando el contrato objetivo lo permita.

CareShift sigue siendo un reference pilot no normativo. CUSA-Digital aportó la evidencia que reveló la brecha de conformidad, pero tampoco es una dependencia normativa del Master.

## 14. Consumidores y adopción

No existe automatic consumer upgrade.

Una release estable del Master no cambia `.blueprint/status.yaml`, código, schemas o comportamiento de un consumidor. La adopción se realiza mediante:

1. verificación live del Master y del consumidor;
2. Compliance Review entre versión declarada y versión objetivo;
3. clasificación KEEP / ADOPT / MIGRATE / DEFER / N/A;
4. aprobación explícita;
5. PR de adopción separada;
6. revalidación según el impacto real.

CUSA-Digital sigue declarando Blueprint **0.5.0** después de su propia remediación de Clean Architecture. El desarrollo o eventual merge de 0.5.1-dev no lo actualiza automáticamente.

Solo después de publicar una release estable 0.5.1 podrá evaluarse una Compliance Review `0.5.0 -> 0.5.1` separada.

## 15. Release closure 0.5.1

Este hardening no publica 0.5.1.

La futura frontera de release debe:

- promover identidad estable `0.5.1`;
- reconciliar schemas/templates/skills activos;
- actualizar `VERSION`, README, Current State, release notes y manifest;
- ejecutar validación completa sobre el head exacto;
- requerir aprobación humana;
- mergear y verificar `main`;
- crear `v0.5.1` solo después de la validación post-merge.

Hasta entonces, 0.5.0 sigue siendo la última release estable.

## 16. Fuera de esta frontera

No forma parte del hardening 0.5.1-dev actual:

- mutar automáticamente consumidores;
- reabrir o cambiar el contrato API de CUSA;
- iniciar Design System de CUSA desde el Master;
- materializar otras skills planned;
- construir Blueprint Control Center;
- declarar Blueprint 1.0.
