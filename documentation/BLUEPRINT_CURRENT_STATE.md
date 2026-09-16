# Software Development Blueprint - Current State

> CURRENT CHECKPOINT / DERIVED SUMMARY  
> Fecha de cierre representada: **2026-09-16 America/Montevideo**.  
> Release representada: **0.5.3**.  
> Carril de desarrollo actual: **0.5.4-dev release candidate**.

Este documento es un resumen humano. No sustituye a `BLUEPRINT.md`, `VERSION`, `DEVELOPMENT_VERSION`, `catalog/`, `workflows/`, `schemas/`, `templates/`, `skills/` ni a la evidencia de los repositorios consumidores.

## 1. Autoridad

Cuando exista contradicción, prevalecen: contratos/evidencia del consumidor para su versión declarada, Blueprint canónico de esa versión, materialized skills, contratos locales aprobados, reference pilots y finalmente chat/historial.

GitHub versionado prevalece sobre handoffs conversacionales.

## 2. Release estable vigente

Repositorio: `LuisHdezE/SoftwareDevelopmentBlueprint`

Versión estable representada: **0.5.3**

Conteos del núcleo estable:

- **28 fases**;
- **145 checks**;
- **19 gates**;
- **15 skills materializadas**;
- **25 skills planificadas**.

0.5.3 añadió Optional Mobile Licensing mediante PR #25. Su publicación estable posterior permanece como historia inmutable y `VERSION` continúa en `0.5.3` durante todo el hardening 0.5.4-dev.

## 3. Estado actual de 0.5.4-dev

`DEVELOPMENT_VERSION = 0.5.4-dev` identifica el carril de hardening. No es una release estable y no constituye adopción automática para consumidores.

El hardening funcional planificado de 0.5.4 está completo a través de `main@965e2c060e2193d50d0937fd425802fb1b193c60`, merge de PR #37. El siguiente paso permitido es el PR final de promoción, después de cerrar y aprobar este checkpoint de Release Closure.

Conteos actuales del candidato:

- **29 fases**;
- **146 checks**;
- **19 gates**;
- **16 skills materializadas**;
- **25 skills planificadas**.

El snapshot machine-readable vive en `documentation/BLUEPRINT_V0_5_4_RELEASE_CANDIDATE.json` y las notas de cierre en `documentation/BLUEPRINT_V0_5_4_RELEASE_CANDIDATE.md`.

## 4. Línea de hardening 0.5.4-dev

Los incrementos aceptados hasta el cierre funcional son:

| Incremento | PR | Merge SHA | Alcance |
| --- | ---: | --- | --- |
| 0 | #31 | `25b74c2cd92ad7aa4171196df3cc52cc3c58954d` | carril gobernado 0.5.4-dev |
| 1 | #32 | `408880be8536828dfe12de98c2ea511e8bdcc5a8` | capability model iOS/mobile.strategy |
| 2 | #33 | `8207c23ccf6ab519431a26ad564a42d960033d3f` | iOS Client Architecture |
| 3 | #34 | `fad8eef654cb7825b03e77f5eb3dae6fbf7698e0` | workflows, catalogs y skills iOS |
| 4 | #35 | `e18eda4d2676f47cdee1f9eed68f9f1a63941b1d` | integridad semántica cross-artifact |
| 5 | #36 | `fc4446f869f9f903b1ef1bc3761e2ec222ac602c` | governed platform matrix + CI |
| 6 | #37 | `965e2c060e2193d50d0937fd425802fb1b193c60` | Mobile Licensing regression boundary |

Cada incremento fue integrado únicamente después de aprobación humana explícita y validado nuevamente sobre su merge SHA real en `main`.

## 5. Modelo de plataformas del candidato

Targets explícitos:

- Web -> namespace `WEB-###`;
- Android -> namespace histórico `APP-###`;
- iOS -> namespace `IOS-###`.

`mobile.strategy` admite:

- `native`: implementaciones independientes para los targets habilitados;
- `cross_platform`: estrategia compartida de implementación/código para los targets habilitados.

`cross_platform` no habilita targets automáticamente y no fusiona arquitectura aceptada, evidencia, gate PASS, QA ni aceptación entre plataformas.

La unidad de ejecución sigue siendo `interface_slice + platform`.

## 6. Client Architecture e iOS

El contrato efectivo continúa siendo:

`Platform Client Architecture Baseline + Slice Architecture Binding/Override = Effective Client Architecture Contract`

Web, Android e iOS conservan baseline, binding, evidencia y aceptación independientes. Las tecnologías concretas del cliente son decisión del consumidor; el Blueprint no impone Flutter, React Native, Kotlin Multiplatform ni otro framework universal.

## 7. Functional Interface Slice

Lifecycle:

`INVENTORIED -> READY -> IN_PROGRESS -> FUNCTIONAL -> ACCEPTED`

Visual & Functional Review e Integration QA son gates independientes. `BLOCKED_BY_API` sigue siendo overlay y no un estado lifecycle.

Los gates `client_architecture_ready`, `functional_slice_ready`, `visual_functional_review_pass` e `integration_qa_pass` permanecen scoped por `interface_slice + platform`.

## 8. Mobile Licensing boundary

El contrato estable de `mobile_licensing` conserva provenance 0.5.3.

La frontera validada para 0.5.4-dev es:

- Web-only -> no exige decisión Mobile Licensing;
- iOS-only -> no exige decisión Mobile Licensing;
- Android -> exige `capabilities.mobile_licensing: true|false`;
- Android+iOS -> exige la decisión porque Android está habilitado;
- `cross_platform` no altera aplicabilidad;
- si licensing está habilitado, el perfil machine-readable sigue siendo obligatorio.

No se generaliza Mobile Licensing a iOS.

## 9. Offline boundary

0.5.4-dev formaliza únicamente offline mobile **API-backed**: cache, queue, retry y degraded/disconnected operation temporal con la API como autoridad de negocio.

API-less/local-authoritative permanece fuera de este hardening porque alteraría API Gate, OpenAPI, DoD y QA. No debe inventarse una API solo para satisfacer el Blueprint.

## 10. Platform matrix y CI

El candidato contiene una matriz gobernada de plataformas con casos positivos y negativos para Web, Android, iOS, multi-target, `native`, `cross_platform` y API-backed offline.

Existe además una matriz dedicada de regresión de Mobile Licensing que congela la aplicabilidad Android-only.

Los workflows especializados y Release Validation forman evidencia automatizada, pero CI no sustituye aprobación humana de review, merge, aceptación ni tag.

## 11. Provenance de componentes

Durante el release candidate:

- root estable: `0.5.3` hasta promoción;
- carril de desarrollo: `0.5.4-dev`;
- project/status y contratos platform-bearing modificados: `0.5.4-dev`;
- catalogs/workflows modificados: `0.5.4-dev`;
- skills iOS/client architecture/functional slice modificadas: `0.5.4-dev`;
- Mobile Licensing schema/template/skill: `0.5.3-compatible`;
- CI Runtime: `0.5.2-compatible`;
- Architecture Implementation Conformance: `0.5.1-compatible`;
- contratos históricos no modificados conservan su provenance anterior.

No se re-etiquetan componentes sin cambio semántico.

## 12. Consumidores y adopción

No existe automatic consumer upgrade.

Una futura release estable 0.5.4 no cambia por sí misma `.blueprint/status.yaml`, código, workflows ni comportamiento de un consumidor. La adopción requiere verificación live del Master/consumidor, Compliance Review, clasificación KEEP / ADOPT / MIGRATE / DEFER / N/A, aprobación explícita, PR de adopción y revalidación según impacto real.

## 13. Release closure y siguiente frontera

Este checkpoint no publica 0.5.4. Mantiene:

- `VERSION = 0.5.3`;
- `DEVELOPMENT_VERSION = 0.5.4-dev`;
- ausencia de `documentation/BLUEPRINT_V0_5_4_RELEASE.json` estable;
- ausencia de tag `v0.5.4`.

El PR final de release debe, como una frontera separada:

1. promover contratos activos de desarrollo a `0.5.4` estable;
2. establecer `VERSION = 0.5.4`;
3. retirar `DEVELOPMENT_VERSION`;
4. crear manifest y release notes estables 0.5.4;
5. actualizar `BLUEPRINT.md`, README y Current State a identidad estable;
6. ejecutar validación estable sobre el SHA real resultante en `main`;
7. pedir aprobación humana separada antes de crear `v0.5.4`.

Un `merge_commit_sha` prospectivo mostrado mientras un PR está abierto nunca sustituye al SHA real devuelto por la operación de merge.

## 14. Fuera de 0.5.4

Permanece diferido el modelo API-less/local-authoritative mobile. Tampoco se impone un framework móvil universal, se generaliza Mobile Licensing a iOS, se mutan consumidores automáticamente ni se materializan por obligación todas las skills todavía planned.
