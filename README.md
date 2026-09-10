# Software Development Blueprint

Repositorio maestro, versionado y machine-readable para gobernar el desarrollo de soluciones de software asistidas por IA.

El Blueprint define **cómo** descubrir, reconstruir, documentar, diseñar, implementar, validar, entregar y mantener una solución. Cada proyecto declara qué versión consume y conserva su propio estado, evidencia y decisiones.

## Release estable

**Blueprint 0.5.3**

0.5.3 es un hardening enfocado en **Optional Mobile Licensing** sobre 0.5.2. Mantiene CI Execution Portability, Architecture Implementation Conformance y el pipeline funcional existente, y añade una capacidad reusable de trial/activación para Android sin convertirla en requisito universal.

Para Android, el proyecto debe responder explícitamente:

`capabilities.mobile_licensing: true|false`

Si es `false`, la rama de licenciamiento es N/A. Si es `true`, el contrato por defecto usa trial configurable, expiración segura en modo read-only, activación firmada y ligada al dispositivo, verificación offline, separación de backup/licencia, issuer protegido, recuperación/rotación de claves y un gate condicional `mobile_licensing_ready`.

Cadena principal:

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

## Qué cambia en 0.5.3

La release estabiliza:

- `schemas/mobile-licensing.schema.json`;
- `templates/mobile-licensing.example.yaml`;
- el capability `mobile_licensing` en project schema/template;
- 10 checks de licensing distribuidos entre Requirements, Architecture, Integration QA y Release;
- el gate project-scoped `mobile_licensing_ready`;
- el skill `skills/dev-mobile-licensing/SKILL.md`;
- validación dedicada de casos positivos, negativos y de manipulación.

El contrato exige 17 pruebas cuando licensing está habilitado. También exige que la clave privada de producción no exista en la aplicación cliente, que la expiración no bloquee los datos del usuario y que un backup portable no clone una licencia device-bound.

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
14. Web PASS no autoriza Android ni otro slice.
15. Cambios API posteriores al baseline usan impact-based revalidation.
16. Brownfield aplica **ALIGN, DO NOT REWRITE**.
17. Arquitectura aprobada debe verificarse también contra la implementación real.
18. Una nueva versión del Blueprint no actualiza consumidores automáticamente.
19. CI no sustituye decisiones humanas de review/merge/acceptance.
20. La semántica de evidencia CI es independiente de quién posee el runner.
21. Un fallo pre-ejecución de infraestructura no se falsifica como fallo de producto.
22. Android debe responder explícitamente si Mobile Licensing aplica.
23. Licensing habilitado no puede enviar una production private signing key en el cliente.
24. Expirar un trial no autoriza a secuestrar datos del usuario.
25. Un backup portable no puede clonar una licencia ligada al dispositivo.

## Núcleo 0.5.3

- **28 fases** canónicas.
- **145 checks**.
- **19 gates**.
- **15 skills materializadas** y **25 planificadas**.
- Interface Scope Baseline + Executable Interface Inventory.
- Functional Interface Slice machine-readable.
- Architecture Implementation Conformance.
- CI Execution Portability con `github_hosted`, `self_hosted` y `hybrid`.
- Mobile Licensing condicional con signed offline activation por defecto.

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

Son defaults. Brownfield no recibe autorización para reescribir funcionalidad existente por estilo.

## Estructura

```text
SoftwareDevelopmentBlueprint/
├── BLUEPRINT.md
├── VERSION
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

- `BLUEPRINT.md`: estándar normativo.
- `documentation/BLUEPRINT_CURRENT_STATE.md`: checkpoint humano derivado.
- `documentation/BLUEPRINT_V0_5_3_MOBILE_LICENSING.md`: contrato de Mobile Licensing.
- `documentation/BLUEPRINT_V0_5_3_RELEASE_NOTES.md`: alcance y compatibilidad de 0.5.3.
- `documentation/BLUEPRINT_V0_5_3_RELEASE.json`: manifest machine-readable de la release.
- `documentation/BLUEPRINT_V0_5_2_CI_EXECUTION_PORTABILITY.md`: historia del hardening CI 0.5.2.
- `documentation/BLUEPRINT_V0_5_1_ARCHITECTURE_CONFORMANCE_HARDENING.md`: historia del hardening arquitectónico 0.5.1.
- `documentation/EXPERIENCE_ARTIFACT_MODEL.md`, `documentation/CLIENT_ARCHITECTURE_CONTRACT.md` y `documentation/SKILL_MODEL.md`: contratos complementarios.

Los documentos/manifests anteriores se conservan como historia y no se reescriben para aparentar adopción posterior.

## Consumidores y Compliance Review

Un consumidor permanece en su versión declarada hasta un **Compliance Review** y una adopción explícita. La publicación de Blueprint 0.5.3 no modifica GestioApp, CUSA-Digital ni ningún otro repositorio consumidor.

La adopción debe clasificar cambios como KEEP / ADOPT / MIGRATE / DEFER / N/A, obtener aprobación humana y revalidar el impacto real.

## Versionado y provenance

`VERSION = 0.5.3` identifica la release raíz. Los nuevos contratos de licensing y los checks/gates/workflows asociados son 0.5.3. CI Runtime conserva provenance compatible 0.5.2; Architecture Implementation Conformance conserva 0.5.1; phases y contratos de experiencia sin cambio conservan 0.5.0.

La etiqueta de esta release será `v0.5.3`; se crea únicamente después de fusionar el PR de release, verificar el árbol aprobado en `main` y confirmar validación post-merge sobre ese SHA exacto.
