# Software Development Blueprint

## 1. Propósito

Este repositorio define el estándar maestro para construir, recuperar, alinear, validar y mantener soluciones de software asistidas por IA.

El Blueprint es independiente del producto. Cada solución declara qué versión consume y mantiene su propia documentación, estado, evidencias y skills específicas.

## 2. Modos de entrada

### Greenfield
Para soluciones nuevas. El trabajo comienza por Discovery y definición del producto antes de implementar.

### Brownfield
Para soluciones existentes. El trabajo comienza con inspección verificable del repositorio, reconstrucción AS-IS, análisis de brechas y definición TO-BE. No se deben inventar requisitos ausentes ni sustituir silenciosamente decisiones existentes.

## 3. Clasificación de reglas

- `REQUIRED`: obligatoria cuando la fase/capacidad aplica.
- `DEFAULT`: decisión recomendada salvo justificación documentada.
- `CONDITIONAL`: se activa por características del proyecto.
- `GENERATED`: artefacto producido automáticamente o derivado.
- `BROWNFIELD`: exigencia específica para sistemas existentes.

## 4. Stack por defecto

Cuando no exista una razón documentada para otra decisión:

- Backend/API: Laravel, versión estable actual al iniciar o actualizar el proyecto.
- API: REST versionada.
- Base de datos: MySQL.
- Web: React + TypeScript + Tailwind CSS.
- Android: Kotlin nativo + Jetpack Compose.
- Contrato API: OpenAPI.
- QA operativo API: Postman.
- Control de versiones e integración: GitHub.

Estas decisiones son defaults, no excusa para reescribir un Brownfield funcional sin beneficio demostrado.

## 5. Gates de ingeniería

Blueprint v0.3 formaliza la cadena completa de gates previos al trabajo de clientes:

`Brownfield Baseline → Requirements Ready → Architecture Ready → API Contract Ready → API Implemented → OpenAPI Valid → Postman Ready → API QA Pass → API Gate → UI/Clients → Release Gate`

### Brownfield Baseline

Exige inventario técnico, reconstrucción funcional, Gap Analysis, TO-BE y roadmap antes de tratar propuestas como requisitos.

### Requirements Ready

Exige actores/autorización, requisitos funcionales y no funcionales, reglas de negocio, casos de uso, criterios de aceptación y trazabilidad.

### Architecture Ready

Exige decisiones explícitas sobre arquitectura, seguridad, datos, base de datos autoritativa, auditoría, autenticación API, contrato de errores y versionado.

### API Contract Ready

Exige alcance API, inventario de endpoints, contrato de autenticación, permisos, mapeo de eventos, idempotencia y trazabilidad antes de escribir endpoints.

### API Implemented

Exige endpoints implementados, autorización, auditoría y pruebas backend. No equivale al API Gate.

### OpenAPI Valid

Exige que el contrato OpenAPI cubra la API implementada y valide correctamente.

### Postman Ready

Exige colección, entornos y cobertura operacional completa de los endpoints implementados.

### API QA Pass

Exige QA positivo, negativo, seguridad, auditoría y validación de contrato.

### API Gate

Solo cuando todos los artefactos anteriores pasan se desbloquean inventarios de interfaces, diseño visual y clientes React/Kotlin.

### Release Gate

No se libera una solución sin QA de integración, QA de seguridad, documentación de release y backup/restore cuando aplique.

## 6. UI y mockups

Antes de generar imágenes debe existir un inventario numerado de vistas web y Android con propósito, rol, datos, acciones, estados y endpoints relacionados.

Los mockups se generan en paquetes relacionados de máximo 10 vistas por tanda. Nunca se solicita una generación de más de 10 vistas.

## 7. Auditoría y eventos

Todo sistema debe registrar de forma persistente los eventos relevantes de negocio, seguridad y administración que permitan reconstruir quién hizo qué, cuándo, sobre qué recurso y con qué resultado.

Se distinguen:

- logs técnicos/operativos;
- auditoría persistente;
- eventos de negocio.

No deben registrarse contraseñas, tokens, secretos ni PII innecesaria. La política completa tendrá una especificación canónica propia y será referenciada por seguridad, API, SaaS y QA sin duplicación.

## 8. Skills

Las skills forman parte del Blueprint y se clasifican en:

1. core reutilizables;
2. específicas por tecnología/capacidad;
3. específicas del proyecto, generadas o mantenidas dentro del repositorio consumidor.

Las skills deben ser pequeñas, indicar cuándo usarlas y enlazar a documentación canónica en lugar de duplicarla.

## 9. Single Source of Truth

Cada concepto importante tiene un documento o catálogo propietario. Otros artefactos deben referenciarlo, no redefinirlo.

## 10. Evidencias

Un check automático o un gate debe poder asociarse a evidencia verificable: archivo, commit, reporte, ejecución CI, resultado Postman, OpenAPI, test u otro artefacto auditable.

## 11. Versionado

El Blueprint usa versionado semántico. Los proyectos declaran la versión adoptada. Una nueva versión del Blueprint no modifica automáticamente proyectos existentes; primero se realiza un Compliance Review y se decide qué adoptar.

## 12. Proyecto piloto

`LuisHdezE/CareShift_Manager` valida el flujo Brownfield y los formatos machine-readable antes de cerrar Blueprint v1.0. Los hallazgos del piloto se incorporan al Blueprint mediante cambios versionados y PRs separados.
