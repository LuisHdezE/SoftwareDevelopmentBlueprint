# Software Development Blueprint

Repositorio maestro, versionado y machine-readable para gobernar el desarrollo de soluciones de software asistidas por IA.

El Blueprint define **cómo** descubrir, reconstruir, documentar, diseñar, implementar, validar, entregar y mantener una solución. No pertenece a un producto concreto: cada proyecto declara qué versión consume y conserva su propio estado, evidencia y decisiones.

## Release estable

**Blueprint 0.4.0**

La release 0.4.0 completa el pipeline desde Discovery/Brownfield hasta diseño y arquitectura cliente con gates verificables, schemas, templates, skills reutilizables y evidencia versionada.

Cadena principal:

```text
Discovery / Brownfield
  → Requirements
  → Architecture / Security / Data
  → API Contract
  → API Implementation
  → OpenAPI
  → Postman
  → API QA
  → API Gate
  → Interface Inventory
  → Visual Identity
  → Design System
  → Mockup Planning
  → Mockups
  → Visual Review
  → Client Architecture
  → Web / Android Implementation
  → Integration QA
  → Release Gate
  → Operations
```

## Principios

1. **Single Source of Truth** en el repositorio.
2. **Evidence before PASS**: gates y checks deben poder demostrarse.
3. **API first**: OpenAPI es contrato formal y Postman es verificación operacional.
4. **No UI antes de API Gate**.
5. **GENERATED ≠ REVIEWED ≠ APPROVED** para referencias visuales.
6. Los assets visuales aprobados se versionan y son contexto para futuras IAs.
7. `visual_review_pass` se evalúa por `interface_slice`.
8. `client_architecture_ready` se evalúa por `interface_slice + platform`.
9. La API sigue siendo el límite de autorización.
10. Brownfield aplica **ALIGN, DO NOT REWRITE**.
11. Una nueva versión del Blueprint no actualiza consumidores automáticamente: primero se realiza Compliance Review.
12. Una sola PR activa por boundary de implementación, salvo justificación explícita.

## Modos

### Greenfield

Para soluciones nuevas. Comienza por Discovery y definición verificable del producto.

### Brownfield

Para sistemas existentes. Comienza por inspección del repositorio, reconstrucción AS-IS, Gap Analysis y TO-BE. Se separa siempre `observed`, `inferred` y `proposed`.

## Stack por defecto

Cuando no exista una decisión documentada que justifique otra opción:

- Backend/API: Laravel estable actual.
- Base de datos: MySQL.
- Web: React + TypeScript + Vite + Tailwind CSS.
- Android: Kotlin + Jetpack Compose.
- Contrato API: OpenAPI.
- QA operacional API: Postman.
- Repositorio/CI: GitHub.

En Brownfield son defaults, no autorización para reescribir funcionalidad existente.

## Estructura

```text
SoftwareDevelopmentBlueprint/
├── BLUEPRINT.md
├── VERSION
├── catalog/
│   ├── phases.yaml
│   ├── checks.yaml
│   ├── gates.yaml
│   ├── skills.yaml
│   └── reference-pilots.yaml
├── workflows/
│   ├── greenfield.yaml
│   └── brownfield.yaml
├── schemas/
├── templates/
├── skills/
├── scripts/
├── tests/
├── documentation/
└── .github/workflows/
```

## Núcleo 0.4.0

- 25 fases canónicas.
- 92 checks.
- 14 gates.
- 13 skills materializadas y 25 planificadas.
- schemas para proyecto, estado, inventario de interfaces, Design System/tokens, mockups, evidencia, arquitectura cliente, pilotos y Compliance Review.
- validación automática de schemas/evidencia, skills, client architecture y reference-pilot compliance.
- pipeline visual/cliente scoped, que permite progresar por slices sin aprobar todo el producto de una vez.

## Reference Pilot

`LuisHdezE/CareShift_Manager` es el primer piloto Brownfield y permanece **no normativo**.

El Compliance Review de v0.4 concluyó `ADOPT_INCREMENTALLY`: su evidencia v0.3 se conserva; no se reescribe el sistema para parecer un proyecto nuevo. El proyecto consumidor continúa declarando Blueprint 0.3.0 hasta una adopción explícita posterior.

## Documentación clave

- `BLUEPRINT.md`: estándar normativo.
- `documentation/BLUEPRINT_CURRENT_STATE.md`: checkpoint humano derivado.
- `documentation/BLUEPRINT_V0_4_RELEASE_NOTES.md`: alcance y compatibilidad de 0.4.0.
- `documentation/BLUEPRINT_V0_4_RELEASE.json`: manifest machine-readable de la release.
- `documentation/EXPERIENCE_ARTIFACT_MODEL.md`: modelo de artefactos UI/visual.
- `documentation/CLIENT_ARCHITECTURE_CONTRACT.md`: contrato pre-implementación React/Kotlin.
- `documentation/SKILL_MODEL.md`: contrato de skills.

## Versionado

El Blueprint usa SemVer. Los consumidores permanecen en su versión declarada hasta que un Compliance Review aprueba qué conservar, adoptar, migrar o diferir.

La etiqueta prevista para esta release es `v0.4.0`, creada únicamente después de fusionar y verificar el PR de release sobre `main`.
