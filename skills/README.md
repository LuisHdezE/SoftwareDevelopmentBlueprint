# Skills Library

Las skills del Blueprint enseñan a los agentes **cómo trabajar**. No sustituyen contratos canónicos ni documentación específica del producto.

## Contrato ejecutable v0.5

Una skill materializada vive en:

`skills/<skill-id>/SKILL.md`

Su frontmatter contiene `id`, `title`, `version`, `status`, `category`, `applies_to`, `phases` y `canonical_references`.

Secciones obligatorias:

1. Purpose
2. When to Use
3. Inputs
4. Procedure
5. Outputs
6. Stop Conditions
7. Guardrails
8. Canonical References
9. Completion Signal

`catalog/skills.yaml` es el índice machine-readable y `scripts/validate-skills.py` valida el contrato.

## Cómo las consume una IA

1. Leer la versión Blueprint adoptada por el consumidor y su estado actual.
2. Consultar el catálogo de esa versión.
3. Cargar solo las skills `materialized` relevantes.
4. Leer `canonical_references` desde el repositorio.
5. Ejecutar el procedimiento y producir outputs/evidencia.
6. Detenerse ante una Stop Condition.
7. Cambiar checks/gates solo cuando existe evidencia suficiente.

Una skill no puede saltarse un gate, inventar product truth ni convertir CI en aprobación humana.

## Skills materializadas en 0.5.0

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
- `dev-android-client-architecture`
- `dev-functional-interface-slice`
- `dev-event-logging-audit`

Total: **14 materializadas**. Las **25 restantes** siguen `planned` y no deben cargarse como procedimientos disponibles.

## Reglas de neutralidad

- Las skills genéricas no contienen nombres/reglas privadas de productos.
- Skills de proyecto viven en el consumidor y pueden añadir contexto de dominio.
- Reference pilots son cantera de patrones, no fuente normativa.
- `dev-functional-interface-slice` implementa el slice real usando inventario ejecutable, Client Architecture y API autoritativa; no autoriza datos de negocio hardcodeados ni capacidades inventadas.
- `dev-mockup-planning` es condicional y no crea una dependencia universal de imágenes.
