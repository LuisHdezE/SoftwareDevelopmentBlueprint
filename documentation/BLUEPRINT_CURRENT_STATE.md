# Software Development Blueprint - Current State

> CURRENT CHECKPOINT / DERIVED SUMMARY  
> Fecha de cierre representada: **2026-09-16 America/Montevideo**.  
> Release representada: **0.5.4**.

Este documento es un resumen humano. No sustituye a `BLUEPRINT.md`, `VERSION`, `catalog/`, `workflows/`, `schemas/`, `templates/`, `skills/` ni a la evidencia de los repositorios consumidores.

## 1. Autoridad

Cuando exista contradicción, prevalecen: contratos/evidencia del consumidor para su versión declarada, Blueprint canónico de esa versión, materialized skills, contratos locales aprobados, reference pilots y finalmente chat/historial.

GitHub versionado prevalece sobre handoffs conversacionales.

## 2. Blueprint estable

Repositorio: `LuisHdezE/SoftwareDevelopmentBlueprint`

Versión estable representada: **0.5.4**

Conteos del núcleo:

- **29 fases**;
- **146 checks**;
- **19 gates**;
- **16 skills materializadas**;
- **25 skills planificadas**.

0.5.4 promueve el hardening multiplataforma completado mediante los incrementos PR #31 a #38. No existe automatic consumer upgrade.

## 3. Línea de hardening y release closure

El carril 0.5.4 fue construido y aceptado incrementalmente:

| Incremento | PR | Merge SHA | Alcance |
| --- | ---: | --- | --- |
| 0 | #31 | `25b74c2cd92ad7aa4171196df3cc52cc3c58954d` | carril gobernado 0.5.4-dev |
| 1 | #32 | `408880be8536828dfe12de98c2ea511e8bdcc5a8` | capability model iOS/mobile.strategy |
| 2 | #33 | `8207c23ccf6ab519431a26ad564a42d960033d3f` | iOS Client Architecture |
| 3 | #34 | `fad8eef654cb7825b03e77f5eb3dae6fbf7698e0` | workflows, catalogs y skills iOS |
| 4 | #35 | `e18eda4d2676f47cdee1f9eed68f9f1a63941b1d` | integridad semántica cross-artifact |
| 5 | #36 | `fc4446f869f9f903b1ef1bc3761e2ec222ac602c` | governed platform matrix + CI |
| 6 | #37 | `965e2c060e2193d50d0937fd425802fb1b193c60` | Mobile Licensing regression boundary |
| 7 | #38 | `1f852ad831f6cb16b92c697fa97c46ac0e71049a` | release closure / release candidate |

PR #38 dejó el árbol listo para promoción estable. El PR final de release parte exactamente de `main@1f852ad831f6cb16b92c697fa97c46ac0e71049a`.

Los manifests `BLUEPRINT_V0_5_4_DEVELOPMENT.json` y `BLUEPRINT_V0_5_4_RELEASE_CANDIDATE.*` permanecen como historia del proceso previo a la release estable.

## 4. Modelo de plataformas 0.5.4

Targets explícitos:

- Web -> namespace `WEB-###`;
- Android -> namespace histórico `APP-###`;
- iOS -> namespace `IOS-###`.

`APP-###` continúa siendo Android-specific y nunca significa “mobile genérico”.

`mobile.strategy` admite:

- `native`: implementaciones independientes para los targets habilitados;
- `cross_platform`: estrategia compartida de implementación/código para los targets habilitados.

`cross_platform` no habilita targets automáticamente y no fusiona arquitectura aceptada, evidencia, gate PASS, QA ni aceptación entre plataformas.

La unidad de ejecución sigue siendo `interface_slice + platform`.

## 5. Client Architecture e iOS

El contrato efectivo continúa siendo:

`Platform Client Architecture Baseline + Slice Architecture Binding/Override = Effective Client Architecture Contract`

Web, Android e iOS conservan baseline, binding, evidencia y aceptación independientes. Las tecnologías concretas del cliente son decisión del consumidor; Blueprint no impone SwiftUI, Flutter, React Native, Kotlin Multiplatform ni otro framework universal.

Los gates `client_architecture_ready`, `functional_slice_ready`, `visual_functional_review_pass` e `integration_qa_pass` permanecen scoped por `interface_slice + platform`.

## 6. Functional Interface Slice

Lifecycle:

`INVENTORIED -> READY -> IN_PROGRESS -> FUNCTIONAL -> ACCEPTED`

Visual & Functional Review e Integration QA son gates independientes. `BLOCKED_BY_API` sigue siendo overlay y no un estado lifecycle.

## 7. Offline boundary

0.5.4 formaliza únicamente offline mobile **API-backed**: cache, queue, retry y operación temporal disconnected/degraded con la API como autoridad de negocio y seguridad.

API-less/local-authoritative permanece fuera de 0.5.4 porque alteraría API Gate, OpenAPI, Definition of Done y QA. No debe inventarse una API solo para satisfacer el Blueprint.

## 8. Mobile Licensing boundary

El contrato `mobile_licensing` conserva provenance **0.5.3-compatible**.

La frontera estable es:

- Web-only -> no exige decisión Mobile Licensing;
- iOS-only -> no exige decisión Mobile Licensing;
- Android -> exige `capabilities.mobile_licensing: true|false`;
- Android+iOS -> exige la decisión porque Android está habilitado;
- `cross_platform` no altera aplicabilidad;
- si licensing está habilitado, el perfil machine-readable y `mobile_licensing_ready` siguen siendo obligatorios.

0.5.4 no generaliza Mobile Licensing a iOS.

## 9. Platform matrix y CI

0.5.4 contiene una matriz gobernada de plataformas con casos positivos y negativos para Web, Android, iOS, multi-target, `native`, `cross_platform` y API-backed offline.

Existe además una matriz dedicada de regresión de Mobile Licensing que congela la aplicabilidad Android-only, incluyendo compatibilidad con manifests Android heredados.

Los workflows especializados y Release Validation forman evidencia automatizada, pero CI no sustituye aprobación humana de review, merge, aceptación ni tag.

## 10. Provenance de componentes

- root release: `0.5.4`;
- project/status y contratos platform-bearing modificados: `0.5.4`;
- catalogs/workflows modificados: `0.5.4`;
- `dev-android-client-architecture`, `dev-ios-client-architecture` y `dev-functional-interface-slice`: `0.5.4`;
- Mobile Licensing schema/template/skill: `0.5.3-compatible`;
- CI Runtime: `0.5.2-compatible`;
- Architecture Implementation Conformance: `0.5.1-compatible`;
- componentes históricos no modificados conservan su provenance anterior.

No se re-etiquetan componentes sin cambio semántico.

## 11. Consumidores y adopción

No existe automatic consumer upgrade.

La publicación de 0.5.4 no cambia por sí misma `.blueprint/status.yaml`, código, workflows ni comportamiento de un consumidor. La adopción requiere verificación live del Master/consumidor, Compliance Review, clasificación KEEP / ADOPT / MIGRATE / DEFER / N/A, aprobación explícita, PR de adopción y revalidación según impacto real.

## 12. Release manifest y tag

El manifest estable es `documentation/BLUEPRINT_V0_5_4_RELEASE.json` y las notas están en `documentation/BLUEPRINT_V0_5_4_RELEASE_NOTES.md`.

El tag esperado es `v0.5.4`, pero **no se crea como parte del PR de release**. Solo puede crearse después de:

1. aprobación humana explícita del merge del PR final;
2. merge y captura del SHA real devuelto por GitHub;
3. verificación del árbol aprobado en `main`;
4. CI estable post-merge sobre ese SHA exacto;
5. aprobación humana separada para crear el tag.

Un `merge_commit_sha` prospectivo mostrado mientras un PR está abierto nunca sustituye al SHA real devuelto por la operación de merge.

## 13. Fuera de 0.5.4

Permanece diferido el modelo API-less/local-authoritative mobile. Tampoco se impone un framework móvil universal, se generaliza Mobile Licensing a iOS, se mutan consumidores automáticamente ni se materializan por obligación todas las skills todavía planned.
