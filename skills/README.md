# Skills Library

Las skills del Blueprint enseñan a los agentes **cómo trabajar**. No duplican la documentación completa del proyecto ni sustituyen los contratos canónicos.

## Contrato ejecutable v0.4

Una skill materializada vive en:

```text
skills/<skill-id>/SKILL.md
```

Cada `SKILL.md` debe incluir frontmatter con:

- `id`
- `title`
- `version`
- `status`
- `category`
- `applies_to`
- `phases`
- `canonical_references`

Y debe contener las secciones:

1. Purpose
2. When to Use
3. Inputs
4. Procedure
5. Outputs
6. Stop Conditions
7. Guardrails
8. Canonical References
9. Completion Signal

El catálogo `catalog/skills.yaml` es el índice machine-readable. Una skill con `status: materialized` debe resolver a un archivo real y pasar `scripts/validate-skills.py`.

## Cómo las consume una IA

1. Leer el manifiesto del proyecto y la fase actual.
2. Consultar `catalog/skills.yaml`.
3. Cargar solo las skills materializadas relevantes para la tarea.
4. Leer sus `canonical_references` desde el repositorio.
5. Ejecutar el procedimiento y producir los outputs en el proyecto.
6. Detenerse si se cumple una `Stop Condition`.
7. Actualizar evidencia/checks/gates únicamente cuando los outputs permiten verificarlos.

Las skills **no autorizan saltarse gates**. Si una skill y un contrato canónico entran en conflicto, manda el contrato canónico del Blueprint declarado por el proyecto.

## Tipos

### Core

Conocimiento reutilizable transversal: Git, revisión, debugging, refactorización, seguridad base, testing, auditoría y documentación.

### Technology / Capability

Se activan según el manifiesto: Laravel, React, Tailwind, Kotlin, SaaS, multi-tenancy, Docker, etc.

### Project Skills

Viven en el repositorio consumidor, normalmente bajo `.agents/skills/`, y encapsulan conocimiento específico del dominio, roles, reglas, módulos o decisiones del producto.

## Reglas

1. Una skill declara claramente cuándo debe utilizarse y cuándo debe detenerse.
2. Debe ser pequeña y orientada a una tarea o contexto concreto.
3. Debe enlazar a la fuente canónica cuando necesite detalle, no copiar documentos completos.
4. Nunca mezclar una skill `dev-*` genérica con nombres, rutas o reglas de un producto concreto.
5. Las skills específicas del proyecto pueden referenciar documentos locales del proyecto.
6. El agente carga solo las skills relevantes para la fase/tarea actual.
7. El Blueprint versiona skills genéricas; el proyecto versiona sus skills específicas.
8. `materialized` significa que existe un archivo ejecutable validado. `planned` significa que el nombre está reservado en el catálogo, pero todavía no debe cargarse como una skill disponible.
9. Las decisiones importantes y outputs deben quedar en el repositorio consumidor; una skill no convierte el historial del chat en evidencia.

## Set materializado inicial de v0.4

- `dev-git-workflow`
- `dev-brownfield-analysis`
- `dev-api-design`
- `dev-openapi`
- `dev-postman-qa`
- `dev-contract-testing`
- `dev-web-view-inventory`
- `dev-design-system`
- `dev-mockup-planning`
- `dev-accessibility`
- `dev-react-client-architecture`
- `dev-event-logging-audit`

El resto del catálogo permanece explícitamente `planned` hasta una revisión posterior.

## Fuente inicial

`LuisHdezE/VolquetasManager/.agents/skills` se usa como cantera histórica de patrones.

- Se reutiliza únicamente conocimiento genérico después de eliminar referencias específicas.
- Las skills de proyecto sirven de patrón, no de norma.
- Ninguna referencia de producto debe filtrarse a una skill `dev-*` reutilizable.
