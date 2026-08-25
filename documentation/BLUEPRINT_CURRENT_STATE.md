# Software Development Blueprint — Current State

> CURRENT CHECKPOINT / DERIVED SUMMARY  
> Verificación de release: 2026-08-25 America/Montevideo.  
> Release representada: **0.4.0**.

Este documento es un resumen humano. No sustituye a `BLUEPRINT.md`, `VERSION`, `catalog/`, `workflows/`, `schemas/`, `skills/`, `templates/` ni a la evidencia de los repositorios consumidores.

## 1. Autoridad de fuentes

Cuando exista contradicción, usar este orden:

1. Definiciones canónicas versionadas de `LuisHdezE/SoftwareDevelopmentBlueprint`.
2. Estado/evidencia machine-readable del repositorio consumidor (`.blueprint/`).
3. Este Current State.
4. Hallazgos de pilotos aún no promovidos.
5. Historial conversacional/archivos históricos.

El chat nunca prevalece sobre evidencia más reciente versionada en GitHub.

## 2. Blueprint estable

Repositorio maestro:

`LuisHdezE/SoftwareDevelopmentBlueprint`

Versión estable:

`0.4.0`

La release 0.4.0 consolida un proceso reutilizable y verificable para Greenfield y Brownfield, desde entrada/discovery hasta release/operations, con contratos machine-readable para API, experiencia visual y arquitectura cliente.

## 3. Tamaño del núcleo 0.4.0

- **25 fases** canónicas.
- **92 checks**.
- **14 gates**.
- **13 skills materializadas**.
- **25 skills planificadas**.
- Greenfield y Brownfield comparten el mismo pipeline post-API.
- Los consumidores no se actualizan automáticamente.

## 4. Pipeline canónico

```text
Greenfield Discovery
        o
Brownfield Inspection → AS-IS → Gap Analysis
        ↓
Target Definition
        ↓
Requirements & Domain
        ↓
Architecture / Security / Data
        ↓
API Scope & Contract
        ↓
API Implementation
        ↓
OpenAPI Validation
        ↓
Postman Contract
        ↓
API QA
        ↓
API Gate
        ↓
Interface Inventory
        ↓
Visual Identity
        ↓
Design System
        ↓
Mockup Planning
        ↓
Mockup Generation
        ↓
Visual Review Gate
        ↓
Client Architecture
        ↓
React Web / Kotlin Android
        ↓
Integration QA
        ↓
Release Gate
        ↓
Operations
```

## 5. Gates 0.4.0

Gates de proyecto/API:

- `brownfield_baseline`
- `requirements_ready`
- `architecture_ready`
- `api_contract_ready`
- `api_implemented`
- `openapi_valid`
- `postman_ready`
- `api_qa_pass`
- `api_gate`
- `interface_inventory_ready`
- `design_system_ready`
- `release_gate`

Gates scoped:

- `visual_review_pass` → `interface_slice`
- `client_architecture_ready` → `interface_slice + platform`

Un PASS scoped no autoriza otro slice o plataforma.

## 6. Pipeline visual y continuidad de IA

La release 0.4.0 formaliza:

- inventario `WEB-###` / `APP-###`;
- identidad y Design System separados;
- tokens machine-readable;
- batches de mockups de máximo 10 vistas;
- assets visuales versionados;
- estados separados de generación, revisión contractual, accesibilidad y aprobación;
- referencias visuales aprobadas como entradas de futuras IAs;
- manifests/evidencia en el repositorio, no únicamente en chats.

Regla central:

`GENERATED ≠ REVIEWED ≠ APPROVED`

## 7. Client Architecture

Antes de implementar React o Kotlin para un slice aprobado debe existir un contrato validable que cubra:

- auth/session lifecycle;
- API client y OpenAPI/operation IDs;
- presentación de permisos manteniendo la API como enforcement;
- routing/navigation;
- server state/local UI state;
- cache/invalidation;
- forms y errores 409/422/429;
- loading/empty/error/401/403/404/offline;
- idempotencia de mutaciones de riesgo;
- request correlation y redacción de secretos/PII;
- accesibilidad;
- testing;
- offline cuando aplique;
- decisiones React o Kotlin/Android;
- coexistencia/cutover/rollback Brownfield.

## 8. Skills

Materializadas en 0.4.0:

1. `dev-git-workflow`
2. `dev-brownfield-analysis`
3. `dev-api-design`
4. `dev-openapi`
5. `dev-postman-qa`
6. `dev-contract-testing`
7. `dev-web-view-inventory`
8. `dev-design-system`
9. `dev-mockup-planning`
10. `dev-accessibility`
11. `dev-react-client-architecture`
12. `dev-android-client-architecture`
13. `dev-event-logging-audit`

Las 25 restantes permanecen `planned`; su presencia en el catálogo no debe interpretarse como implementación disponible.

## 9. Evidencia y validadores del Blueprint

Validadores versionados:

- `scripts/validate-experience-artifacts.py`
- `scripts/validate-skills.py`
- `scripts/validate-client-architecture.py`
- `scripts/validate-reference-pilot-compliance.py`
- `scripts/validate-release.py`

El release validator ejecuta las familias anteriores y comprueba identidad/versionado de 0.4.0, conteos canónicos, templates, workflows y manifest de release.

## 10. Reference Pilot: CareShift Manager

Repositorio:

`LuisHdezE/CareShift_Manager`

Modo:

`brownfield`

Versión Blueprint declarada por el consumidor:

`0.3.0`

Estado relevante verificado antes del cierre 0.4.0:

- Brownfield Baseline: PASS.
- Requirements: PASS.
- Architecture/Security/Data: PASS.
- API Contract: PASS.
- API Implementation: COMPLETE.
- OpenAPI Validation: PASS.
- Postman Contract: PASS.
- API QA runtime: PASS.
- API Gate: PASS.
- Interface Inventory: COMPLETE, 30 vistas web; Android N/A.
- Visual Identity: COMPLETE.
- Design System: COMPLETE.
- Rama `blueprint/mockups-batch-01`: 13 commits ahead / 0 behind de CareShift `main` al Compliance Review.
- Batch Operational Core: 10 vistas planificadas, 4 assets SVG generados y 6 pendientes.
- Los 4 SVG generados siguen `GENERATED`, no se consideran aprobados por existencia.
- React/client architecture: DEFERRED hasta `visual_review_pass` del slice correspondiente.
- Cliente Livewire/Blade actual: preservado.

## 11. Compliance Review del piloto

Resultado formal V4-5:

- `KEEP`: 8
- `ADOPT`: 9
- `MIGRATE`: 1
- `DEFER`: 4
- `N/A`: 2

Recomendación:

`ADOPT_INCREMENTALLY`

La única migración identificada fue la representación del manifest de mockups. No se autorizó regenerar imágenes, reescribir la UI existente ni cambiar automáticamente la versión declarada del consumidor.

El review histórico se realizó contra el snapshot prerelease `0.4.0-dev`. La release 0.4.0 no introduce cambios normativos posteriores al review; el cierre solo estabiliza versionado, documentación y validación. CareShift requiere todavía una PR separada de adopción antes de declarar 0.4.0.

## 12. Compatibilidad 0.4.0

0.4.0 es una release minor backward-aware:

- evidencia v0.3 de consumidores no se invalida automáticamente;
- path migrations son opcionales cuando `artifact_locations` puede declarar rutas existentes;
- Brownfield sigue `ALIGN, DO NOT REWRITE`;
- un cliente existente puede coexistir mientras un cliente nuevo se construye;
- la aprobación visual y arquitectura cliente se realizan por slice;
- pilotos son no normativos.

## 13. Trabajo deliberadamente fuera del release

No forma parte del cierre 0.4.0:

- completar las seis imágenes pendientes de CareShift;
- implementar React en CareShift;
- migrar CareShift automáticamente a Blueprint 0.4.0;
- materializar las 25 skills todavía planificadas;
- construir el Blueprint Control Center;
- declarar Blueprint 1.0.

## 14. Próxima acción después del release

Una vez fusionado y etiquetado `v0.4.0`, el Blueprint puede usarse como baseline estable para:

1. nuevas soluciones Greenfield;
2. nuevos análisis Brownfield;
3. Compliance Review/adopción de consumidores existentes;
4. continuar CareShift desde su trabajo visual pendiente sin alterar la evidencia ya validada.
