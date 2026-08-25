# Software Development Blueprint - Current State

> CURRENT CHECKPOINT / DERIVED SUMMARY
>
> Última verificación: 2026-08-24 23:39 America/Montevideo.
>
> Este documento resume el estado vigente del Blueprint y de su piloto Brownfield. No sustituye a los artefactos canónicos versionados del repositorio ni a los archivos `.blueprint/` del proyecto piloto.

## 1. Autoridad de las fuentes

Cuando exista contradicción entre fuentes, utilizar este orden de autoridad:

1. Definiciones canónicas versionadas de `LuisHdezE/SoftwareDevelopmentBlueprint`: `BLUEPRINT.md`, `VERSION`, `catalog/`, `workflows/`, `schemas/`, `skills/` y `templates/`.
2. Estado y evidencia machine-readable del repositorio consumidor, especialmente `.blueprint/`.
3. Este archivo `documentation/BLUEPRINT_CURRENT_STATE.md`, como checkpoint humano de navegación.
4. Hallazgos de pilotos aún no promovidos a norma Blueprint.
5. `documentation/BLUEPRINT_CHAT_HISTORY.md`, archivo histórico no canónico.

El historial conversacional nunca debe prevalecer sobre una definición o evidencia más reciente en GitHub.

## 2. Proyecto principal

**Software Development Blueprint** es el proyecto principal.

Repositorio maestro:

`LuisHdezE/SoftwareDevelopmentBlueprint`

Versión actual verificada:

`0.3.0`

El Blueprint define un estándar reutilizable, versionado y machine-readable para construir, recuperar, alinear, validar y mantener soluciones de software asistidas por IA.

CareShift_Manager es el primer piloto Brownfield. Su objetivo no es únicamente terminar CareShift, sino validar el Blueprint bajo condiciones reales y producir hallazgos generalizables.

## 3. Principios fundamentales

- El Blueprint es independiente del producto.
- Soporta Greenfield y Brownfield.
- Brownfield sigue `ALIGN, DO NOT REWRITE`.
- No se inventan requisitos ausentes ni se reemplazan silenciosamente decisiones existentes.
- Cada concepto importante debe tener una fuente canónica y los demás artefactos deben referenciarla.
- Las reglas se clasifican como `REQUIRED`, `DEFAULT`, `CONDITIONAL`, `GENERATED` o `BROWNFIELD`.
- La evidencia debe ser verificable: archivo, commit, CI, test, reporte, OpenAPI, Postman u otro artefacto auditable.
- Los proyectos declaran qué versión del Blueprint consumen.
- Una nueva versión del Blueprint no modifica automáticamente proyectos existentes; primero se hace Compliance Review.

Regla de trazabilidad central:

`Need → Business Rule → Requirement → Use Case → Acceptance Criteria → Entity → Endpoint → View → Test`

## 4. Stack por defecto

Cuando no exista una razón documentada para otra decisión:

- Backend/API: Laravel estable actual al iniciar o actualizar el proyecto.
- API: REST versionada, normalmente `/api/v1`.
- Base de datos: MySQL.
- Web: React + TypeScript + Vite + Tailwind CSS.
- Android: Kotlin nativo + Jetpack Compose.
- Contrato API: OpenAPI.
- QA operativo API: Postman.
- Control de versiones e integración: GitHub.

En Brownfield estos son defaults, no justificación para reescribir un sistema funcional.

## 5. Fases v0.3

Cadena machine-readable actual:

1. `discovery` para Greenfield.
2. `brownfield_inspection` para Brownfield.
3. `as_is`.
4. `gap_analysis`.
5. `target_definition`.
6. `requirements_domain`.
7. `architecture_security_data`.
8. `api_contract_design`.
9. `api_implementation`.
10. `openapi_validation`.
11. `postman_contract`.
12. `api_qa`.
13. `api_gate`.
14. `interface_inventory`.
15. `visual_identity`.
16. `mockups`.
17. `web_implementation`.
18. `android_implementation`.
19. `integration_qa`.
20. `release_gate`.
21. `operations`.

`interface_inventory` y `visual_identity` permanecen bloqueados por `api_gate`. Los mockups se generan en lotes de máximo 10 imágenes.

## 6. Gates vigentes

Blueprint v0.3 formaliza esta cadena:

`Brownfield Baseline → Requirements Ready → Architecture Ready → API Contract Ready → API Implemented → OpenAPI Valid → Postman Ready → API QA Pass → API Gate → UI/Clients → Release Gate`

### Brownfield Baseline

Requiere inventario técnico, reconstrucción funcional, Gap Analysis, TO-BE y roadmap.

### Requirements Ready

Requiere actores/autorización, RF, RNF, reglas de negocio, casos de uso, criterios de aceptación y trazabilidad.

### Architecture Ready

Requiere decisiones de arquitectura, seguridad, datos, base autoritativa, auditoría, autenticación API, contrato de errores y versionado.

### API Contract Ready

Debe existir antes de implementar endpoints. Exige alcance, inventario de endpoints, contrato de autenticación, permisos, eventos, idempotencia y trazabilidad.

### API Implemented

Exige endpoints, autorización, auditoría y pruebas backend. No equivale a `API_GATE`.

### OpenAPI Valid

Formaliza y valida el contrato de la API implementada.

### Postman Ready

Exige colección, environments y cobertura operacional de endpoints implementados.

### API QA Pass

Exige QA positivo, negativo, contrato, seguridad y auditoría.

### API Gate

Solo con este gate en `PASS` se desbloquean inventarios UI, identidad visual, mockups y clientes React/Kotlin.

### Release Gate

Exige QA de integración, QA de seguridad, documentación de release y backup/restore cuando aplique.

Estados de gate utilizados:

`READY_FOR_REVIEW | PASS | FAIL | BLOCKED`

## 7. Workflow Brownfield

Flujo vigente:

`Repository Inspection → AS-IS → Technical Inventory → Functional Reconstruction → Gap Analysis → TO-BE → Requirements → Architecture/Security/Data → API Contract → API Implementation → OpenAPI → Postman → API QA → API Gate → Interface Inventory → Identity → Mockups → Clients → Integration QA → Release`

Reglas aprendidas y mantenidas:

- separar `observed`, `inferred` y `proposed`;
- usar disposiciones `KEEP`, `IMPROVE`, `ADD`, `DECIDE`, `N/A`;
- distinguir `DECLARED_ONLY` de comportamiento realmente implementado;
- distinguir `DEFECT_CANDIDATE` de una regla de negocio;
- no confundir permisos declarados con enforcement efectivo;
- preservar tests existentes como evidencia de comportamiento;
- no promover configuración histórica a requisito sin evidencia;
- no hacer reescrituras estéticas;
- estabilizar la API antes de alinear nuevos clientes.

## 8. Estrategia API-first

Secuencia obligatoria de trabajo:

`API → OpenAPI → Postman → QA API → Contract Validation → API Gate PASS → Inventarios UX → Identidad/Design System → Mockups → React/Kotlin`

OpenAPI es el contrato formal.

Postman es la verificación operacional.

Artefactos Postman canónicos previstos en proyectos consumidores:

```text
/postman/project-api.postman_collection.json
/postman/local.postman_environment.json
/postman/staging.postman_environment.json
/postman/README.md
```

Variables típicas:

- `base_url`
- `access_token`
- `refresh_token`
- IDs dinámicos

La cobertura QA debe considerar casos positivos y negativos, auth, token expirado, RBAC, validación, conflictos, paginación, filtros, orden, búsqueda, rate limits, headers y respuestas controladas `401/403/404/409/422/429/500` cuando apliquen.

## 9. UI, identidad y mockups

Antes de generar imágenes debe existir un inventario numerado de vistas web y Android.

IDs recomendados:

- `WEB-001...`
- `APP-001...`

Cada vista debe declarar al menos:

- ID y nombre;
- plataforma y módulo;
- propósito;
- roles;
- datos;
- acciones;
- componentes;
- estados loading/empty/error/success;
- endpoints relacionados;
- navegación;
- comportamiento responsive cuando aplique.

La identidad visual se define antes de los mockups e incluye nombre, concepto de marca, personalidad, paleta, tipografía, iconografía, estilo de componentes, light/dark y logo.

Los mockups se generan mediante:

`Generate → Review → Correct → Approve → Next batch`

Nunca más de 10 imágenes por lote.

## 10. Event Logging & Audit

El Blueprint distingue tres conceptos:

1. logs técnicos/operativos;
2. auditoría persistente;
3. eventos de negocio.

Todo sistema debe poder reconstruir quién hizo qué, cuándo, sobre qué recurso y con qué resultado para acciones relevantes de negocio, seguridad y administración.

Campos objetivo comunes:

- `id`
- `event_type` o código canónico de evento
- `actor_id`
- `actor_type`
- `tenant_id` cuando aplique
- `entity_type`
- `entity_id`
- `action`
- `old_values` seleccionados
- `new_values` seleccionados
- `result`
- `request_id` / correlation ID
- IP y user-agent cuando corresponda
- metadata segura
- `created_at`

Nunca almacenar passwords, JWT, refresh tokens, secretos ni PII innecesaria. La auditoría debe comportarse como append-only a través de las interfaces normales. Cada proyecto debe definir retención, acceso, privacidad y tenant scoping cuando aplique.

Los eventos críticos deben verificarse también durante API QA.

## 11. SaaS / Multi-tenancy

Discovery o Brownfield debe clasificar el producto como single-user, single-company, multi-user, multi-company, SaaS o multi-tenant SaaS.

Cuando SaaS/multi-tenant aplique se deben resolver explícitamente:

- tenant model e aislamiento;
- estrategia de base de datos;
- RBAC;
- onboarding;
- planes y suscripciones;
- billing/webhooks;
- límites de features;
- suspensión/reactivación;
- auditoría por tenant.

## 12. Skills

El Blueprint utiliza skills versionadas y cargadas bajo demanda.

Principios actuales:

- las skills se versionan con el Blueprint;
- cargar únicamente las relevantes a la tarea;
- conocimiento específico permanece en el proyecto consumidor;
- las skills referencian documentación canónica en lugar de duplicarla.

Categorías actuales:

- core;
- backend;
- web;
- android;
- saas;
- brownfield;
- devops.

La auditoría inicial de skills tomó como referencia conocimiento reutilizable de `VolquetasManager/.agents/skills`, eliminando contaminación específica del proyecto.

Nota de mantenimiento: `catalog/skills.yaml` conserva actualmente `version: 0.1.0` aunque el Blueprint Master está en `0.3.0`. Debe evaluarse si esta versión es intencionalmente independiente o si necesita sincronización en una futura revisión.

## 13. Machine-readable Blueprint y Control Center

El Blueprint no debe ser únicamente una colección de Markdown. Sus fases, checks, gates, skills, capacidades y evidencias deben poder ser consumidos por herramientas.

Arquitectura objetivo:

```text
BLUEPRINT MASTER
      |
      v
machine-readable specification
      |
      +-- phases
      +-- checks
      +-- gates
      +-- skills
      +-- capabilities
      +-- evidence
             |
             v
       PROJECT REPOS
             |
             v
    BLUEPRINT CONTROL CENTER
```

El futuro Blueprint Control Center deberá leer GitHub como fuente de verdad y visualizar proyectos, versión Blueprint, progreso, health, fases, checks, gates, evidencias, blockers, compliance y próximas acciones.

El Control Center no debe hardcodear el proceso: debe leerlo del Blueprint versionado.

## 14. Proyecto piloto CareShift_Manager

Repositorio:

`LuisHdezE/CareShift_Manager`

Modo:

`brownfield`

Objetivo del piloto:

validar el Blueprint con un sistema existente antes de cerrar Blueprint v1.0.

Estado verificado en `main`:

- B0 Brownfield Baseline: `PASS`.
- B1 Requirements reconstruction: `PASS`.
- B2 Architecture/Security/Data: `PASS`.
- B3 API Scope & Contract Design: `PASS`.
- B4 API Implementation: `IN_PROGRESS`, 57%.
- `API_IMPLEMENTED`: `BLOCKED` hasta completar Slices 4-6.
- OpenAPI: `BLOCKED` por `API_IMPLEMENTED`.
- Postman: `BLOCKED`.
- API QA: `BLOCKED`.
- API Gate: `BLOCKED`.
- UI inventory, visual identity y mockups: `BLOCKED` por API Gate.

Slices mergeados y CI-verificados:

- Slice 0: API Foundation + Auth.
- Slice 1: Caregivers.
- Slice 2: Patients + Availability.
- Slice 3: Shifts + Attendance.

PRs B4 mergeados:

- PR #6: Foundation/Auth + Caregivers.
- PR #7: Patients + Availability.
- PR #8: Shifts + Attendance.

Cada incremento fue validado con la batería acumulativa que incluye:

- Composer install/validate;
- Vite build;
- Pint sobre alcance relevante;
- `migrate:fresh` SQLite;
- suite completa SQLite;
- `migrate:fresh` MySQL 8.4;
- suite completa MySQL 8.4;
- Composer security audit;
- enforcement final;
- evidencia CI Blueprint.

## 15. CareShift Slice 4 - estado actual

Siguiente slice aprobado:

**Users + Roles + Settings**

Rama existente:

`blueprint/api-implementation-slice-4`

Trabajo ya iniciado y verificado por inspección de la rama:

- `ManagedUserResource`;
- `StoreUserRequest`;
- `UpdateUserRequest`;
- `UserController`;
- `RoleResource`;
- `StoreRoleRequest`;
- `UpdateRoleRequest`;
- `RoleController`;
- `UpdateSettingsRequest`;
- `SettingsController`.

Decisiones de Slice 4 ya establecidas:

- la API Users no expone passwords, hashes ni secretos;
- no exponer `module_permissions` hardcodeados del Brownfield como contrato API;
- no exponer internals de auditoría antigua desde `GetUserByIdUseCase`;
- Roles API utiliza permisos canónicos `resource.action` y no nombres internos de Filament Shield como `ViewAny:Role`;
- reset password reutiliza el mecanismo Laravel existente y nunca devuelve una contraseña;
- Settings se basa en las claves Brownfield verificadas: `company_name`, `company_tax_id`, `company_phone`, `company_address`, `company_email`, `currency`, `timezone`, `date_format`, `language`.

### Riesgo operativo actual

Después del merge de PR #8, la rama Slice 4 está **divergida respecto a `main`**:

- 11 commits ahead;
- 3 commits behind;
- merge-base: head final previo de Slice 3.

Antes de continuar Slice 4 se debe alinear cuidadosamente la rama con el `main` actual, preservar sus cambios y volver a validar el diff. No abrir PR #9 hasta que esa alineación esté resuelta y el CI del Slice 4 esté verde.

## 16. Próximos pasos CareShift

Orden inmediato:

1. Alinear `blueprint/api-implementation-slice-4` con `main` después del merge de #8.
2. Verificar diff resultante para confirmar que contiene únicamente Slice 4.
3. Completar rutas `/users`, `/roles` y `/settings`.
4. Incorporar permisos canónicos `settings.view` y `settings.edit` con estrategia Brownfield idempotente.
5. Actualizar seeder correspondiente.
6. Mapear excepciones de Users/Roles/Settings a Problem Details sin exponer internals.
7. Completar tests Feature API para Users, Roles y Settings.
8. Ejecutar CI acumulativo en SQLite y MySQL 8.4.
9. Resolver únicamente causas verificadas por CI.
10. Crear `.blueprint/evidence/B4_SLICE_4_CI.md`.
11. Actualizar `.blueprint/status.yaml` a 71% solo si Slice 4 queda PASS.
12. Crear PR #9 directamente contra `main` y mantener un único PR activo por slice.
13. Después: Slice 5 Dashboard + Alerts + Reports.
14. Después: Slice 6 Payroll.
15. Solo entonces evaluar `API_IMPLEMENTED = PASS`.
16. Continuar OpenAPI → Postman → API QA → API Gate.

## 17. Findings generalizables del piloto

CareShift ya reveló temas que deben evaluarse para futuras versiones del Blueprint, sin promoverlos automáticamente:

1. Estado de capacidades Brownfield debe distinguir unknown/current/target.
2. Separar stack actual de stack objetivo.
3. `architecture.domain_model` no debe pasar únicamente por existencia de carpetas.
4. Clarificar perfiles/categorías/IDs y versionado de skills.
5. Formalizar extracción incremental de API desde aplicaciones server-rendered.
6. Distinguir HTTP existente de REST versionada implementada.
7. Persistencia de audit logs no equivale a cumplimiento completo de auditoría.
8. Definir niveles/calidad de evidencia y verification modes.
9. Consolidar máquina de estados/gates Brownfield y `READY_FOR_REVIEW`.
10. Formalizar `KEEP/IMPROVE/ADD/DECIDE/N/A`.
11. Tratar tests existentes como preservation evidence.
12. Formalizar semánticas `DECLARED_ONLY` y `DEFECT_CANDIDATE`.
13. Separar permiso declarado de runtime authorization enforcement.
14. Detectar mismatches semánticos de campos de negocio, como `base_rate` vs `hourly_rate`.
15. Extender trazabilidad con endpoint/OpenAPI/Postman/contract test de forma incremental.
16. Formalizar estrategia de CI Brownfield para no convertir deuda cosmética histórica en cambios fuera de alcance.
17. Formalizar verificación multi-engine cuando la base autoritativa y la de test difieren.
18. Registrar correcciones Brownfield descubiertas por nuevos vertical slices como findings verificables.
19. Evitar cadenas largas de stacked PRs; preferir un PR activo por slice e integrar temprano cuando el incremento esté verde.
20. Separar workflows de remediación temporal de workflows estrictos de verificación reproducible.

El ciclo de promoción debe ser:

`Pilot finding → evaluate → generalize → Blueprint change → versioned PR`

## 18. Estrategia de PR aprendida

Durante B4 se apilaron PRs #6, #7 y #8 para mantener diffs de slices aislados mientras la base anterior aún no estaba mergeada. Funcionó, pero aumentó retargeting, reruns y complejidad operacional.

Regla de trabajo vigente para los próximos slices:

> Preferir un único PR activo por slice. Integrar un slice verde antes de abrir una cadena larga de dependencias, salvo que exista una razón explícita para usar stacked PRs.

## 19. Pendientes de evolución del Blueprint Master

No incrementar versión únicamente porque CareShift avance. Cambiar Blueprint Master cuando exista una mejora generalizable y documentada.

Candidatos próximos:

- crear `documentation/pilot-findings/` con findings numerados `PF-*`;
- decidir versionado de `catalog/skills.yaml` frente a `VERSION`;
- formalizar niveles de evidencia;
- incorporar la política de PR/branching derivada del piloto;
- revisar si CI multi-database debe ser DEFAULT o CONDITIONAL;
- enriquecer checks para runtime permission enforcement;
- enriquecer checks para auditoría completa frente a mera existencia de tabla;
- diseñar el contrato machine-readable que consumirá Blueprint Control Center.

## 20. Regla para continuar en nuevos chats

Al iniciar una conversación nueva dentro del proyecto:

1. leer primero `documentation/BLUEPRINT_CURRENT_STATE.md`;
2. consultar las definiciones canónicas del Blueprint cuando una decisión dependa de ellas;
3. verificar en GitHub el estado actual del repositorio piloto antes de afirmar PRs, ramas, CI o gates;
4. usar `documentation/BLUEPRINT_CHAT_HISTORY.md` únicamente para recuperar contexto histórico o razonamiento previo;
5. mantener siempre dos carriles de trabajo:

```text
SoftwareDevelopmentBlueprint
        |
        v
     estándar
        |
        v
 CareShift_Manager
        |
        v
 pilot findings
        |
        v
Blueprint evolution
```

El objetivo final no es solamente terminar CareShift. El objetivo es obtener un Blueprint reutilizable, verificable y suficientemente sólido para gobernar futuros proyectos y alimentar Blueprint Control Center.
