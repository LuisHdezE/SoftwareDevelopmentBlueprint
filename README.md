# Software Development Blueprint

Repositorio maestro y versionado para gobernar el desarrollo de soluciones de software con IA.

El Blueprint define **cómo** se descubre, documenta, diseña, implementa, valida, entrega y mantiene una solución. No pertenece a un producto concreto: los proyectos consumen una versión del Blueprint mediante un manifiesto propio.

## Objetivos

- Unificar el proceso de desarrollo Greenfield y Brownfield.
- Mantener una única fuente de verdad para fases, checks, gates, skills y evidencias.
- Hacer el proceso legible por humanos y por herramientas.
- Evitar avanzar de fase sin cumplir controles obligatorios.
- Permitir medir cumplimiento y progreso desde un futuro Blueprint Control Center.
- Reutilizar skills de agentes sin duplicar instrucciones proyecto a proyecto.

## Estado actual

**Blueprint Core v0.1.0 — en construcción.**

La versión 0.1 define el núcleo machine-readable necesario para probar el modelo con `CareShift_Manager` antes de completar el catálogo documental definitivo.

## Principios iniciales

1. Blueprint first, UI later.
2. Single Source of Truth documental.
3. Evidencia antes que checks manuales cuando sea posible.
4. Gates verificables antes de avanzar.
5. API validada antes del diseño e implementación de clientes web/móvil.
6. Skills pequeñas, reutilizables y cargadas según tarea/fase.
7. Brownfield describe primero el estado real antes de proponer cambios.
8. No refactorizar por estética arquitectónica.
9. Seguridad, auditoría y trazabilidad son requisitos transversales.
10. Los mockups se generan solo después del inventario de vistas y en lotes de máximo 10.

## Estructura del Core

```text
SoftwareDevelopmentBlueprint/
├── BLUEPRINT.md
├── VERSION
├── catalog/
│   ├── phases.yaml
│   ├── checks.yaml
│   ├── gates.yaml
│   └── skills.yaml
├── workflows/
│   ├── greenfield.yaml
│   └── brownfield.yaml
├── schemas/
│   ├── project.schema.json
│   └── status.schema.json
└── skills/
    └── README.md
```

## Proyecto piloto

El primer proyecto usado para validar este modelo será `LuisHdezE/CareShift_Manager` mediante el flujo Brownfield/Alignment.

Las skills genéricas existentes en `LuisHdezE/VolquetasManager/.agents/skills` se usarán como cantera de análisis, separando conocimiento reutilizable de conocimiento específico del dominio.
