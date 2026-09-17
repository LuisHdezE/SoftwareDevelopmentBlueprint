# Software Development Blueprint

Repositorio maestro, versionado y machine-readable para gobernar el desarrollo de soluciones de software asistidas por IA.

El Blueprint define **cómo** descubrir, reconstruir, documentar, diseñar, implementar, validar, entregar y mantener una solución. Cada proyecto declara qué versión consume y conserva su propio estado, evidencia y decisiones.

## Release estable

**Blueprint 0.5.4**

0.5.4 formaliza soporte multiplataforma explícito para **Web, Android e iOS** sin mezclar la aceptación de una plataforma con otra. Mantiene los hardenings anteriores de Architecture Implementation Conformance, CI Execution Portability y Optional Mobile Licensing, y añade un modelo gobernado de capacidades móviles, estrategia `native|cross_platform`, iOS Client Architecture, integridad cross-artifact y matrices de regresión de plataformas.

El núcleo estable contiene:

- **29 fases**;
- **146 checks**;
- **19 gates**;
- **16 skills materializadas**;
- **25 skills planificadas**.

## Modelo de plataformas

Los targets de cliente son explícitos:

- Web: namespace `WEB-###`;
- Android: namespace histórico `APP-###`;
- iOS: namespace `IOS-###`.

`mobile.strategy` puede ser:

- `native`: implementaciones independientes para los targets habilitados;
- `cross_platform`: estrategia compartida de implementación/código para los targets habilitados.

`cross_platform` **no habilita targets automáticamente** y no comparte arquitectura aceptada, gate PASS, evidencia, QA ni aceptación entre Web, Android e iOS.

La unidad de ejecución continúa siendo `interface_slice + platform`.

## Offline mobile

Blueprint 0.5.4 formaliza únicamente offline móvil **API-backed**. Cache, queue, retry y operación temporal disconnected/degraded son válidos cuando la API continúa siendo la autoridad de negocio y seguridad.

El modelo API-less/local-authoritative permanece diferido a un hardening separado. No debe inventarse una API para satisfacer artificialmente el Blueprint.

## Mobile Licensing

Mobile Licensing conserva provenance **0.5.3-compatible** y su frontera Android:

- Web-only no exige decisión de licensing;
- iOS-only no exige decisión de licensing;
- Android exige `capabilities.mobile_licensing: true|false`;
- Android+iOS exige la decisión porque Android está habilitado;
- `cross_platform` no modifica la aplicabilidad;
- cuando licensing está habilitado, el perfil machine-readable y `mobile_licensing_ready` siguen siendo obligatorios.

0.5.4 no generaliza Mobile Licensing a iOS.

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
11. Client Architecture = Platform Baseline + Slice Binding/Override.
12. Los mockups son condicionales; `GENERATED != REVIEWED != APPROVED`.
13. Visual & Functional Review revisa el cliente real.
14. Un PASS de una plataforma no autoriza otra plataforma ni otro slice.
15. Cambios API posteriores al baseline usan impact-based revalidation.
16. Brownfield aplica **ALIGN, DO NOT REWRITE**.
17. Arquitectura aprobada debe verificarse también contra la implementación real.
18. Una nueva versión del Blueprint no actualiza consumidores automáticamente.
19. CI no sustituye decisiones humanas de review, merge o acceptance.
20. La semántica de evidencia CI es independiente de quién posee el runner.
21. Un fallo pre-ejecución de infraestructura no se falsifica como fallo de producto.
22. Android debe responder explícitamente si Mobile Licensing aplica.
23. iOS por sí solo no implica Mobile Licensing.
24. `cross_platform` no cambia la aplicabilidad de Mobile Licensing.
25. Offline mobile 0.5.4 permanece dentro de la frontera API-backed.
26. API-less/local-authoritative permanece diferido.

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

Son defaults. La tecnología concreta de iOS y la estrategia móvil pertenecen al consumidor; el Blueprint no impone SwiftUI, Flutter, React Native, Kotlin Multiplatform ni otro framework universal. Brownfield no recibe autorización para reescribir funcionalidad existente por estilo.

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

- `BLUEPRINT.md`: estándar normativo de la release estable vigente.
- `documentation/BLUEPRINT_CURRENT_STATE.md`: checkpoint humano derivado.
- `documentation/BLUEPRINT_V0_5_4_RELEASE.json`: manifest machine-readable estable 0.5.4.
- `documentation/BLUEPRINT_V0_5_4_RELEASE_NOTES.md`: alcance, compatibilidad y provenance de 0.5.4.
- `documentation/BLUEPRINT_V0_5_4_RELEASE_CANDIDATE.json` y `.md`: historia del release candidate previo a promoción.
- `documentation/BLUEPRINT_V0_5_4_DEVELOPMENT.json`: historia del carril gobernado de hardening.
- `documentation/BLUEPRINT_V0_5_3_MOBILE_LICENSING.md`: contrato histórico de Mobile Licensing, conservado como componente 0.5.3-compatible.
- `documentation/CLIENT_ARCHITECTURE_CONTRACT.md` y `documentation/SKILL_MODEL.md`: contratos complementarios activos.

Los manifests y notas de releases anteriores permanecen inmutables como historia.

## Consumidores y Compliance Review

No existe **automatic consumer upgrade**. Un consumidor permanece en su versión declarada hasta completar un Compliance Review y una adopción explícita.

La adopción de 0.5.4 debe clasificar cambios como KEEP / ADOPT / MIGRATE / DEFER / N/A, obtener aprobación humana, aplicar cambios repository-owned y ejecutar revalidación según impacto real.

## Versionado y provenance

`VERSION = 0.5.4` identifica la release estable vigente.

Los contratos de plataforma y experiencia modificados por este hardening usan provenance 0.5.4. Mobile Licensing permanece 0.5.3-compatible; CI Runtime permanece 0.5.2-compatible; Architecture Implementation Conformance conserva origen 0.5.1-compatible; componentes históricos no modificados conservan su provenance anterior.

El tag `v0.5.4` se crea únicamente después de fusionar el PR de release, verificar el SHA real resultante en `main`, confirmar CI estable post-merge sobre ese SHA exacto y recibir aprobación humana separada para el tag.
