# Skills Library

Las skills del Blueprint enseñan a los agentes **cómo trabajar**, no duplican la documentación completa del proyecto.

## Tipos

### Core
Conocimiento reutilizable transversal: Git, revisión, debugging, refactorización, seguridad base, testing, auditoría y documentación.

### Technology / Capability
Se activan según el manifiesto del proyecto: Laravel, React, Tailwind, Kotlin, SaaS, multi-tenancy, Docker, etc.

### Project Skills
Viven en el repositorio consumidor, normalmente bajo `.agents/skills/`, y encapsulan conocimiento específico del dominio, roles, reglas, módulos o decisiones del producto.

## Reglas

1. Una skill debe declarar claramente cuándo debe utilizarse.
2. Debe ser pequeña y orientada a una tarea o contexto concreto.
3. Debe enlazar a la fuente canónica cuando necesite detalle, no copiar documentos completos.
4. Nunca mezclar una skill `dev-*` genérica con nombres, rutas o reglas de un producto concreto.
5. Las skills específicas del proyecto pueden referenciar documentos locales del proyecto.
6. El agente debe cargar solo las skills relevantes para la fase/tarea actual.
7. El Blueprint versiona las skills genéricas; el proyecto versiona sus skills específicas.

## Fuente inicial

`LuisHdezE/VolquetasManager/.agents/skills` será auditado como cantera inicial.

- Las skills `dev-*` se revisarán y generalizarán antes de ser incorporadas.
- Las skills `vm-*` servirán de patrón para definir cómo generar skills específicas de cada proyecto.
- Ninguna referencia específica de Volquetas Manager debe filtrarse a una skill core reutilizable.
