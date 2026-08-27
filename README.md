# Software Development Blueprint

Repositorio maestro, versionado y machine-readable para gobernar el desarrollo de soluciones de software asistidas por IA.

El Blueprint define **cómo** descubrir, reconstruir, documentar, diseñar, implementar, validar, entregar y mantener una solución. Cada proyecto declara qué versión consume y conserva su propio estado, evidencia y decisiones.

## Release estable

**Blueprint 0.5.1**

0.5.1 es un patch de hardening sobre 0.5.0. Mantiene el flujo funcional post-API introducido en 0.5.0 y añade una obligación que el piloto CUSA-Digital reveló como faltante: la implementación debe demostrar que **conforma con la arquitectura previamente aprobada**.

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

`Visual Identity` y `Mockups / Prototypes` son capacidades condicionales.

## Qué cambia en 0.5.1

Se incorpora el check REQUIRED:

`api.architecture_implementation_conformance`

Ahora `api_implemented` y `api_gate` exigen evidencia de que el código respeta el contrato arquitectónico aprobado, incluyendo, cuando aplique:

- dirección de dependencias;
- límites de módulos/capas/contextos;
- ownership de Presentation, Application, Domain e Infrastructure;
- puertos/adaptadores y bindings;
- aislamiento de framework/persistencia según la arquitectura aceptada;
- architecture fitness functions, reglas estáticas o tests ejecutables cuando sea viable.

Invariante:

`architecture design acceptance != architecture implementation conformance`

Tests funcionales/API verdes no sustituyen esta evidencia.

## Principios clave

1. **Single Source of Truth** en el repositorio.
2. **Evidence before PASS**.
3. La API es la frontera autoritativa de seguridad y reglas de negocio.
4. OpenAPI es el contrato formal machine-readable; `operationId` es clave canónica de enlace cliente.
5. Existe un **Interface Scope Baseline** temprano, pero el cliente ejecutable no comienza antes de `api_gate = PASS`.
6. `EXECUTABLE_INVENTORY` es el backlog cliente comprometido.
7. **Functional Interface Slice** es la unidad de ejecución por `slice + platform`.
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

## Núcleo 0.5.1

- **28 fases** canónicas.
- **135 checks**.
- **18 gates**.
- **14 skills materializadas** y **25 planificadas**.
- Interface Scope Baseline + Executable Interface Inventory.
- Functional Interface Slice machine-readable.
- `BLOCKED_BY_API` con estado preservado y resolución evidenciada.
- API impact graph por `operationId` y contratos cross-cutting.
- Cross-Artifact Semantic Integrity con fixtures positivos/negativos.
- Client Architecture compuesta y sin dependencia obligatoria de mockups.
- Architecture Implementation Conformance como obligación del API Implementation/API Gate.

## Modos

**Greenfield** comienza por Discovery y requirements verificables.

**Brownfield** comienza por inspección, AS-IS, Gap Analysis y TO-BE. Se distingue siempre `OBSERVED`, `INFERRED` y `PROPOSED`; la diferencia arquitectónica por sí sola no justifica una reescritura.

## Stack por defecto

Cuando no exista una decisión documentada que justifique otra opción:

- Backend/API: Laravel estable actual.
- Base de datos: MySQL.
- Web: React + TypeScript + Vite + Tailwind CSS.
- Android: Kotlin + Jetpack Compose.
- Contrato API: OpenAPI.
- QA operacional API: Postman.
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
├── documentation/
└── .github/workflows/
```

## Documentación clave

- `BLUEPRINT.md`: estándar normativo.
- `documentation/BLUEPRINT_CURRENT_STATE.md`: checkpoint humano derivado.
- `documentation/BLUEPRINT_V0_5_1_ARCHITECTURE_CONFORMANCE_HARDENING.md`: decisión y evidencia del hardening.
- `documentation/BLUEPRINT_V0_5_1_RELEASE_NOTES.md`: alcance y compatibilidad de 0.5.1.
- `documentation/BLUEPRINT_V0_5_1_RELEASE.json`: manifest machine-readable de la release.
- `documentation/EXPERIENCE_ARTIFACT_MODEL.md`: contratos de experiencia, slices, blockers y evidencia.
- `documentation/CLIENT_ARCHITECTURE_CONTRACT.md`: arquitectura cliente compuesta.
- `documentation/SKILL_MODEL.md`: contrato de skills.

Los documentos y manifests de 0.4 y 0.5.0 se conservan como historia de release y no se reescriben para aparentar adopción posterior.

## Reference pilots y consumidores

Los reference pilots son no normativos. Sus hallazgos pueden promover reglas al Blueprint solo mediante una frontera explícita.

CUSA-Digital expuso el gap de Architecture Implementation Conformance mientras consumía 0.5.0. El Blueprint generaliza esa lección sin convertir la estructura específica de CUSA en estándar universal.

Un consumidor permanece en su versión declarada hasta un **Compliance Review** y una adopción explícita. La publicación de 0.5.1 no modifica CUSA-Digital ni ningún otro repositorio consumidor.

## Versionado y provenance

Blueprint usa SemVer. `VERSION` identifica la release raíz estable.

En un patch, los componentes cuyo contrato no cambia pueden conservar su versión anterior. En 0.5.1 se actualizan checks/gates y los schemas/templates que declaran la versión del consumidor; los workflows, skills y schemas de experiencia sin cambio conservan provenance 0.5.0 y son reutilizados de forma explícitamente compatible.

La etiqueta de esta release será `v0.5.1`; por política se crea únicamente después de fusionar el PR de release, verificar el árbol aprobado en `main` y confirmar su validación post-merge.
