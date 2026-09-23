# Software Development Blueprint - Current State

> CURRENT CHECKPOINT / DERIVED SUMMARY  
> Fecha de cierre representada: **2026-09-23 America/Montevideo**.  
> Release estable representada: **0.5.4**.  
> Release candidate activa: **0.5.5-dev**.

Este documento es un resumen humano. No sustituye a `BLUEPRINT.md`, `VERSION`, `DEVELOPMENT_VERSION`, `catalog/`, `workflows/`, `schemas/`, `templates/`, `skills/` ni a la evidencia de los repositorios consumidores.

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

`VERSION` permanece en **0.5.4** durante el cierre de la release candidate 0.5.5-dev.

## 3. Release candidate 0.5.5-dev

El hardening 0.5.5-dev está cerrado funcionalmente hasta:

`main@d7ca0ff1cd0615445c3015c9d9b3a18983e573b7`

La rama de release closure convierte ese estado en **release candidate**, pero no promueve todavía 0.5.5 a estable.

Durante este checkpoint deben permanecer verdaderas simultáneamente estas condiciones:

- `VERSION = 0.5.4`;
- `DEVELOPMENT_VERSION = 0.5.5-dev`;
- no existe release estable 0.5.5;
- no existe autorización para tag `v0.5.5`;
- WebBlueprint no es modificado ni auto-adoptado.

## 4. Línea de hardening 0.5.5

El carril 0.5.5-dev fue construido y aceptado incrementalmente:

| Incremento | PR | Merge SHA | Alcance |
| --- | ---: | --- | --- |
| 0 | #42 | `e316c31a04d7a7f8e7c746a3dd36d0cdb1d24ebe` | carril gobernado 0.5.5-dev |
| 1 | #43 | `45ebc94c4ddacac00ebece1fe052400a25c2b060` | API Authority Capability Model |
| 2 | #44 | `a07cf874a214d300daab5bd8214d708bffafe464` | Workflow & Gate Applicability |
| 3 | #45 | `ef8dbde3af3d786cf96b26d9938a27715b8e5f43` | Client Architecture & Slice Authority |
| 4 | #46 | `1b2d29ad43d7e6f30bad2b54ac972bb24704d1e4` | Integration QA Authority Matrix |
| 5 | #47 | `828e182659975da325093e06afa84de238aef2a8` | Generic Compliance Doctor |
| 6 | #48 | `d7ca0ff1cd0615445c3015c9d9b3a18983e573b7` | template provenance + WebBlueprint pilot |

La release candidate congela esta lineage. La futura promoción estable debe ser un PR separado.

## 5. Origen del hardening 0.5.5

El carril nace de la Compliance Review de:

- Blueprint estable 0.5.4;
- `LuisHdezE/WebBlueprint@12cc52dabfe05ec9902f0ea6d73c7da6a19e1a74`.

La revisión encontró que un consumidor legítimamente frontend-only/local/static/non-authoritative-mock no podía satisfacer 0.5.4 honestamente porque fases, gates, Client Architecture, Functional Slice e Integration QA seguían exigiendo API/OpenAPI/database/real API transport.

La decisión fue endurecer Blueprint, no inventar backend para el consumidor.

## 6. Authority model 0.5.5-dev

La autoridad API debe declararse explícitamente como:

- `api_backed`;
- `api_optional`.

`api_backed` conserva la estricta semántica API-backed de 0.5.4.

`api_optional` solo es válido para comportamiento local, estático o mock/provider no autoritativo. No puede declarar remote authoritative business data, server authentication/authorization, permission enforcement, remote persistent mutation o backend-only invariants.

No se permite fabricar OpenAPI, base de datos o permisos para satisfacer gates.

## 7. Workflow y Gate Applicability

Para `api_optional`, las fases/checks/gates exclusivamente API pueden ser N/A de forma estructural. Los checks de base de datos dependen de si realmente existe una base de datos autoritativa.

Para `api_backed`, el workflow estable 0.5.4 se conserva sin debilitamiento.

La proyección de aplicabilidad compone también las decisiones de Client/Slice Authority: la ausencia legítima de API no puede reaparecer como requisito artificial en Client Architecture, Functional Slice o Visual/Functional Review.

## 8. Client Architecture y Functional Slice

El contrato efectivo continúa siendo:

`Platform Client Architecture Baseline + Slice Architecture Binding/Override = Effective Client Architecture Contract`

Para API-backed permanecen los bindings API/OpenAPI/operation/permission.

Para API-optional, el slice puede enlazarse a provider/application contracts y adapters locales o mock no autoritativos.

Son representables honestamente:

- `real_api = N/A`;
- `server_auth_rbac = N/A`;
- provider contract boundary = PASS.

No se relajan las prohibiciones contra hardcoded authoritative business data ni invented capabilities.

## 9. Integration QA Authority

Regla congelada:

> API transport puede ser N/A. Integration QA no puede convertirse en N/A solo porque API transport sea N/A.

API-backed exige real API transport QA.

API-optional sustituye únicamente ese requisito de transporte por provider/runtime transport QA. Permanecen las obligaciones comunes de functional, integration, security, responsive, accessibility, E2E y los prerequisitos de revisión/aceptación humana.

## 10. Generic Compliance Doctor

El Generic Compliance Doctor elimina la dependencia del antiguo validator CareShift-specific como autoridad genérica.

Modelo de resultado:

- PASS;
- FAIL;
- N/A;
- BLOCKED.

Los PASS requieren evidencia válida. Missing evidence, stale evidence, version mismatch, blocked prerequisites y contract violations permanecen fail-closed.

CareShift histórico puede mantenerse como regression fixture, pero no define verdad de producto para consumidores arbitrarios.

## 11. WebBlueprint pilot

El pilot no normativo se ejecutó contra:

`LuisHdezE/WebBlueprint@12cc52dabfe05ec9902f0ea6d73c7da6a19e1a74`

Resultado sobre 35 checks seleccionados:

- PASS: **18**;
- FAIL: **7**;
- N/A: **10**;
- BLOCKED: **0**;
- overall: **FAIL**.

La salida confirma que 0.5.5-dev ya puede representar honestamente ausencia de API/DB/real transport sin declarar Compliance PASS artificial.

Los siete debts que permanecen en WebBlueprint son:

1. requirements traceability gobernada;
2. Interface Inventory proyectado a `WEB-###`;
3. inventory-to-requirements links;
4. Client Architecture artifact gobernado;
5. Functional Slice inventory binding;
6. Functional Slice end-to-end traceability;
7. dedicated Integration QA security evidence.

WebBlueprint permanece `UNMANAGED`. El pilot no es adopción y no muta el consumidor.

## 12. Template Status provenance

El active `templates/status.example.yaml` fue reconciliado a provenance 0.5.4, coherente con el Status schema activo.

Esto corrige provenance del ejemplo sin reescribir manifests históricos.

## 13. Modelo de plataformas estable 0.5.4

Targets explícitos:

- Web -> namespace `WEB-###`;
- Android -> namespace histórico `APP-###`;
- iOS -> namespace `IOS-###`.

`APP-###` continúa siendo Android-specific y nunca significa mobile genérico.

`mobile.strategy` admite `native` y `cross_platform`. La estrategia no habilita targets automáticamente y no fusiona arquitectura aceptada, evidencia, gate PASS, QA ni aceptación entre plataformas.

La unidad de ejecución sigue siendo `interface_slice + platform`.

## 14. Offline y Mobile Licensing

La release estable 0.5.4 formaliza offline mobile API-backed. La semántica API-optional introducida en 0.5.5-dev no autoriza por sí sola un modelo mobile local-authoritative distinto sin contrato explícito.

Mobile Licensing conserva provenance **0.5.3-compatible** y frontera Android:

- Web-only -> no exige decisión;
- iOS-only -> no exige decisión;
- Android -> exige `capabilities.mobile_licensing: true|false`;
- Android+iOS -> exige decisión porque Android está habilitado;
- cross-platform no altera aplicabilidad.

## 15. Provenance de componentes

Durante release-candidate closure:

- root stable release: `0.5.4`;
- development lane: `0.5.5-dev`;
- stable core catalogs/workflows: `0.5.4-compatible`;
- API authority overlay: `0.5.5-dev`;
- Workflow/Gate Applicability overlay: `0.5.5-dev`;
- Client/Slice Authority overlay: `0.5.5-dev`;
- Integration QA Authority overlay: `0.5.5-dev`;
- Generic Compliance Doctor: `0.5.5-dev`;
- WebBlueprint pilot: `0.5.5-dev-non-normative`;
- Status template: `0.5.4` active provenance;
- Mobile Licensing: `0.5.3-compatible`;
- CI Runtime: `0.5.2-compatible`;
- Architecture Implementation Conformance: `0.5.1-compatible`;
- componentes históricos sin cambio conservan su provenance previa.

## 16. Consumidores y adopción

No existe automatic consumer upgrade.

Una futura publicación estable 0.5.5 no cambiará por sí misma `.blueprint/status.yaml`, código, workflows ni comportamiento de un consumidor.

La adopción requiere verificación live del Blueprint/consumidor, Compliance Review, clasificación KEEP / ADOPT / MIGRATE / DEFER / N/A, aprobación explícita, PR de adopción y revalidación según impacto real.

WebBlueprint solo podrá entrar en ese carril después de existir 0.5.5 estable.

## 17. Release candidate y promoción estable

Artifacts de release candidate:

- `documentation/BLUEPRINT_V0_5_5_RELEASE_CANDIDATE.json`;
- `documentation/BLUEPRINT_V0_5_5_RELEASE_CANDIDATE.md`.

La release candidate no crea el manifest estable 0.5.5 ni el tag.

La promoción estable requiere un PR separado que:

1. cambie `VERSION` a 0.5.5;
2. elimine `DEVELOPMENT_VERSION`;
3. promueva los contratos de desarrollo que correspondan;
4. cree release manifest y release notes estables;
5. actualice documentación normativa/activa;
6. pase exact-head CI;
7. reciba aprobación humana explícita;
8. se fusione y capture el SHA real;
9. pase stable post-merge CI sobre ese SHA exacto.

El tag `v0.5.5` requiere aprobación humana separada después de ese cierre.

Un `merge_commit_sha` prospectivo de una PR abierta nunca es release evidence.

## 18. Historia 0.5.4 preservada

El carril 0.5.4 fue construido mediante PR #31 a #38 y promovido estable posteriormente. Sus manifests de Development, Release Candidate, Release y Release Notes permanecen inmutables como historia.

El tag `v0.5.4` sigue apuntando al commit estable `8d29ba4c6caf0a382b80310dc0e88c8f1e7fb3c4`.
