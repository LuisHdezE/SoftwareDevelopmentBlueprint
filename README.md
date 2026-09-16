# Software Development Blueprint

Repositorio maestro, versionado y machine-readable para gobernar el desarrollo de soluciones de software asistidas por IA.

El Blueprint define **cómo** descubrir, reconstruir, documentar, diseñar, implementar, validar, entregar y mantener una solución. Cada proyecto declara qué versión consume y conserva su propio estado, evidencia y decisiones.

## Release estable

**Blueprint 0.5.3**

0.5.3 es la release estable vigente y está enfocada en **Optional Mobile Licensing** sobre 0.5.2. Mantiene CI Execution Portability, Architecture Implementation Conformance y el pipeline funcional existente, y añade una capacidad reusable de trial/activación para Android sin convertirla en requisito universal.

Para Android, el proyecto debe responder explícitamente:

`capabilities.mobile_licensing: true|false`

Si es `false`, la rama de licenciamiento es N/A. Si es `true`, el contrato por defecto usa trial configurable, expiración segura en modo read-only, activación firmada y ligada al dispositivo, verificación offline, separación de backup/licencia, issuer protegido, recuperación/rotación de claves y un gate condicional `mobile_licensing_ready`.

El núcleo estable 0.5.3 conserva **28 fases, 145 checks, 19 gates, 15 skills materializadas y 25 planificadas**.

## Carril de desarrollo 0.5.4-dev

El repositorio mantiene en paralelo un candidato de hardening **0.5.4-dev**. No es todavía una release estable y no cambia `VERSION=0.5.3` ni autoriza por sí solo la creación del tag `v0.5.4`.

El cierre de hardening 0.5.4-dev está preparado como release candidate con:

- **29 fases**;
- **146 checks**;
- **19 gates**;
- **16 skills materializadas**;
- **25 skills planificadas**.

El candidato formaliza iOS como target explícito, conserva `APP-###` para Android e introduce `IOS-###` para iOS, define `mobile.strategy: native|cross_platform`, mantiene aceptación/evidencia/gates independientes por plataforma, limita offline mobile a clientes API-backed y preserva Mobile Licensing como decisión obligatoria únicamente cuando Android está habilitado.

`cross_platform` significa compartir estrategia de implementación/código entre targets habilitados. No habilita targets automáticamente y no comparte PASS, evidencia, QA ni aceptación entre Web, Android e iOS.

La trazabilidad del candidato y el cierre previo al PR final viven en:

- `documentation/BLUEPRINT_V0_5_4_RELEASE_CANDIDATE.json`;
- `documentation/BLUEPRINT_V0_5_4_RELEASE_CANDIDATE.md`;
- `documentation/BLUEPRINT_V0_5_4_DEVELOPMENT.json`.

## Cadena principal

```text
Discovery / Brownfield
  -> Requirements
  -> Interface Scope Baseline
  -> Architecture / Security / Data
  -> API Contract
  -> API Implementation + Architecture Implementation Conformance
  -> OpenAPI / Postman / API QA
  -> API Gate
  -> Executable Interface Inventory
  -> Design System
  -> Client Architecture
  -> Functional Interface Slice
  -> Visual & Functional Review
  -> Integration QA
  -> Release Gate
  -> Operations
```

`Visual Identity`, `Mockups / Prototypes` y `Mobile Licensing` son capacidades condicionales según su propia aplicabilidad.

## Principios clave

1. **Single Source of Truth** en el repositorio.
2. **Evidence before PASS**.
3. La API es la frontera autoritativa de seguridad y reglas de negocio para clientes API-backed.
4. OpenAPI es el contrato formal machine-readable cuando existe API; `operationId` es clave canónica de enlace cliente.
5. Existe un Interface Scope Baseline temprano, pero el cliente API-backed ejecutable no comienza antes de `api_gate = PASS`.
6. `EXECUTABLE_INVENTORY` es el backlog cliente comprometido.
7. Functional Interface Slice es la unidad de ejecución por `slice + platform`.
8. Lifecycle: `INVENTORIED -> READY -> IN_PROGRESS -> FUNCTIONAL -> ACCEPTED`.
9. `BLOCKED_BY_API` es un overlay, no un estado lifecycle.
10. No se permite hardcodear datos autoritativos de negocio para simular funcionalidad.
11. Client Architecture = Platform Baseline + Slice Binding.
12. Los mockups son condicionales; `GENERATED != REVIEWED != APPROVED`.
13. Visual & Functional Review revisa el cliente real.
14. Un PASS de una plataforma no autoriza otra plataforma ni otro slice.
15. Cambios API posteriores al baseline usan impact-based revalidation.
16. Brownfield aplica **ALIGN, DO NOT REWRITE**.
17. Arquitectura aprobada debe verificarse también contra la implementación real.
18. Una nueva versión del Blueprint no actualiza consumidores automáticamente.
19. CI no sustituye decisiones humanas de review/merge/acceptance.
20. La semántica de evidencia CI es independiente de quién posee el runner.
21. Un fallo pre-ejecución de infraestructura no se falsifica como fallo de producto.
22. Android debe responder explícitamente si Mobile Licensing aplica.
23. iOS por sí solo no implica Mobile Licensing.
24. `cross_platform` no cambia la aplicabilidad de Mobile Licensing.
25. Offline mobile 0.5.4 permanece dentro de la frontera API-backed.
26. API-less/local-authoritative permanece diferido a un hardening separado.

## Modos

**Greenfield** comienza por Discovery y requirements verificables.

**Brownfield** comienza por inspección, AS-IS, Gap Analysis y TO-BE. Se distingue `OBSERVED`, `INFERRED` y `PROPOSED`; una diferencia arquitectónica por sí sola no justifica reescritura.

## Stack por defecto

Cuando no exista una decisión documentada que justifique otra opción:

- Backend/API: Laravel estable actual.
- Base de datos: MySQL.
- Web: React + TypeScript + Vite + Tailwind CSS.
- Android: Kotlin + Jetpack Compose.
- Contrato API: OpenAPI cuando la solución incluye API.
- QA operacional API: Postman cuando aplica.
- Repositorio/CI: GitHub.

Son defaults. La estrategia móvil y la tecnología concreta del cliente son decisiones del consumidor; el Blueprint no impone un framework cross-platform universal. Brownfield no recibe autorización para reescribir funcionalidad existente por estilo.

## Estructura

```text
SoftwareDevelopmentBlueprint/
├── BLUEPRINT.md
├── VERSION
├── DEVELOPMENT_VERSION
├── catalog/
├── workflows/
├── schemas/
├── templates/
├── skills/
├── scripts/
├── tests/
├── ci/
├── documentation/
└── .github/workflows/
```

## Documentación clave

- `BLUEPRINT.md`: estándar normativo de la release estable vigente.
- `documentation/BLUEPRINT_CURRENT_STATE.md`: checkpoint humano derivado que distingue estable y candidato.
- `documentation/BLUEPRINT_V0_5_4_RELEASE_CANDIDATE.json`: snapshot machine-readable del candidato 0.5.4.
- `documentation/BLUEPRINT_V0_5_4_RELEASE_CANDIDATE.md`: alcance y reglas de promoción del candidato.
- `documentation/BLUEPRINT_V0_5_4_DEVELOPMENT.json`: gobernanza del carril 0.5.4-dev.
- `documentation/BLUEPRINT_V0_5_3_MOBILE_LICENSING.md`: contrato histórico estable de Mobile Licensing.
- `documentation/BLUEPRINT_V0_5_3_RELEASE_NOTES.md`: alcance y compatibilidad de 0.5.3.
- `documentation/BLUEPRINT_V0_5_3_RELEASE.json`: manifest machine-readable de la release estable actual.
- `documentation/EXPERIENCE_ARTIFACT_MODEL.md`, `documentation/CLIENT_ARCHITECTURE_CONTRACT.md` y `documentation/SKILL_MODEL.md`: contratos complementarios.

Los documentos/manifests anteriores se conservan como historia y no se reescriben para aparentar adopción posterior.

## Consumidores y Compliance Review

Un consumidor permanece en su versión declarada hasta un **Compliance Review** y una adopción explícita. Ni la existencia de 0.5.4-dev ni una futura publicación estable modifican automáticamente repositorios consumidores.

La adopción debe clasificar cambios como KEEP / ADOPT / MIGRATE / DEFER / N/A, obtener aprobación humana y revalidar el impacto real.

## Versionado y provenance

`VERSION = 0.5.3` identifica la release estable vigente. `DEVELOPMENT_VERSION = 0.5.4-dev` identifica exclusivamente el carril de hardening previo a promoción.

Los contratos nuevos o modificados por 0.5.4-dev conservan provenance explícita de desarrollo. Mobile Licensing permanece 0.5.3-compatible; CI Runtime permanece 0.5.2-compatible; Architecture Implementation Conformance conserva origen 0.5.1-compatible; contratos históricos sin cambio semántico conservan su provenance anterior.

La promoción final a 0.5.4 requiere un PR de release separado, validación estable post-merge sobre el SHA real de `main` y aprobación humana separada antes de crear `v0.5.4`.
