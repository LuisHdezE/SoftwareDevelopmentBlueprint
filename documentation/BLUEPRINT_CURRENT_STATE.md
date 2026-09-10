# Software Development Blueprint - Current State

> CURRENT CHECKPOINT / DERIVED SUMMARY  
> Fecha de cierre representada: **2026-09-10 America/Montevideo**.  
> Release representada: **0.5.3**.

Este documento es un resumen humano. No sustituye a `BLUEPRINT.md`, `VERSION`, `catalog/`, `workflows/`, `schemas/`, `templates/`, `skills/` ni a la evidencia de los repositorios consumidores.

## 1. Autoridad

Cuando exista contradicción, prevalecen: contratos/evidencia del consumidor para su versión declarada, Blueprint canónico de esa versión, este Current State, reference pilots y finalmente chat/historial.

GitHub versionado prevalece sobre handoffs conversacionales.

## 2. Blueprint estable

Repositorio: `LuisHdezE/SoftwareDevelopmentBlueprint`

Versión estable representada: **0.5.3**

Conteos del núcleo:

- **28 fases**;
- **145 checks**;
- **19 gates**;
- **15 skills materializadas**;
- **25 skills planificadas**.

0.5.3 añade 10 checks, 1 gate y 1 skill materializada sobre 0.5.2. No añade fases.

## 3. Cambio central de 0.5.3: Optional Mobile Licensing

El hardening se originó en un consumidor Android real y fue generalizado mediante PR #25. El PR fue fusionado a `main` como `5524f9b34f8328e3e6a9c88852fc8df70d9e437e` después de validación exact-head y posteriormente validado nuevamente en `main`.

Todo proyecto Android debe responder explícitamente:

`capabilities.mobile_licensing: true|false`

El valor `false` vuelve N/A los contratos/gates de licensing. El valor `true` activa el perfil machine-readable y el gate condicional `mobile_licensing_ready`.

## 4. Default licensing contract

La estrategia DEFAULT es:

`configurable trial -> expired read-only safety mode -> device-bound signed activation -> perpetual offline entitlement`

Invariantes principales:

- el trial default es 7 días pero configurable;
- la verificación de la licencia no requiere backend;
- expirar el trial no elimina, cifra ni bloquea los datos del usuario;
- read/view/backup/export y activation/help permanecen disponibles tras expiración;
- el cliente usa verificación asimétrica y nunca contiene la private production signing key;
- business backup y entitlement permanecen separados;
- issuer/admin es una frontera protegida separada;
- recuperación y rotación de claves se definen antes de release;
- anti-tamper totalmente offline es best-effort, no garantía absoluta.

## 5. Mandatory licensing evidence

Cuando licensing está habilitado, el contrato exige 17 pruebas automatizadas que cubren duración/expiración del trial, transiciones, firmas válidas, manipulación de payload/firma, wrong-device, wrong-product, versión no soportada, separación prod/test, persistencia, backup sin clonación, read-only safety, interoperabilidad issuer/customer, release build, clock rollback y activación malformada.

La ausencia de production private signing key en el cliente/repo requiere evidencia adicional de inspección/static analysis.

## 6. Gate model

`mobile_licensing_ready` es project-scoped y CONDITIONAL. Solo se evalúa cuando `mobile_licensing=true`.

Cuando aplica, agrega requirements, profile contract, security architecture, private-key isolation, backup separation, issuer boundary, key lifecycle, automated tests, interoperability y exact release-build verification.

`release_gate` depende de `mobile_licensing_ready` únicamente cuando la capacidad está habilitada.

## 7. Pipeline conservado

El pipeline principal sigue siendo:

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

Visual Identity y Mockups/Prototypes siguen siendo condicionales. Mobile Licensing se integra como otra rama condicional, no como fase principal universal.

## 8. CI Execution Portability

0.5.3 conserva la semántica estable 0.5.2:

`CI evidence semantics != runner ownership`

`pre-execution infrastructure failure != test failure`

El contrato `schemas/ci-runtime.schema.json` mantiene provenance 0.5.2-compatible. Exact-head, check runs, logs/artifacts y decisión humana siguen siendo obligaciones separadas.

## 9. Architecture Implementation Conformance

0.5.3 conserva el hardening 0.5.1:

`architecture design acceptance != architecture implementation conformance`

`api.architecture_implementation_conformance` continúa REQUIRED por `api_implemented` y `api_gate`.

## 10. Functional Interface Slice

Lifecycle:

`INVENTORIED -> READY -> IN_PROGRESS -> FUNCTIONAL -> ACCEPTED`

Visual & Functional Review e Integration QA son gates independientes. `BLOCKED_BY_API` sigue siendo overlay y no un estado lifecycle.

## 11. Versionado de componentes

`VERSION = 0.5.3` identifica la release raíz.

Promovidos a 0.5.3: project/status/mobile-licensing schemas y templates, checks/gates/skills/workflows, `dev-mobile-licensing`, documentación y validadores activos de release/licensing.

Reutilizados con provenance compatible: CI Runtime 0.5.2, Architecture Implementation Conformance 0.5.1, phases/reference-pilots/experience contracts 0.5.0.

No se re-etiquetan contratos sin cambio semántico.

## 12. Consumidores y adopción

No existe automatic consumer upgrade.

Una release estable del Master no cambia `.blueprint/status.yaml`, código, workflows ni comportamiento de un consumidor. La adopción requiere verificación live del Master/consumidor, Compliance Review, clasificación KEEP / ADOPT / MIGRATE / DEFER / N/A, aprobación explícita, PR de adopción y revalidación según impacto real.

GestioApp no queda automáticamente migrado a 0.5.3 por esta release. La misma regla aplica a CUSA-Digital y a cualquier otro consumidor.

## 13. Release closure

El manifest machine-readable es `documentation/BLUEPRINT_V0_5_3_RELEASE.json` y las notas están en `documentation/BLUEPRINT_V0_5_3_RELEASE_NOTES.md`.

La frontera de hardening fue PR #25 y su merge exacto es `5524f9b34f8328e3e6a9c88852fc8df70d9e437e`.

La etiqueta `v0.5.3` se crea únicamente después de fusionar el PR de release, verificar el árbol aprobado en `main` y confirmar CI post-merge sobre ese SHA exacto.

## 14. Fuera de 0.5.3

No forma parte de esta release generalizar el modelo API-less/local-authoritative Android. Ese gap permanece separado y no debe resolverse inventando una API para satisfacer el Blueprint.

Tampoco forma parte de esta release crear automáticamente issuer apps, elegir un algoritmo criptográfico universal, imponer un store/payment provider, mutar consumidores, materializar las 25 skills todavía planned o construir Blueprint Control Center.
