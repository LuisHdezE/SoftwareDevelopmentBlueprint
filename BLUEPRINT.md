# Software Development Blueprint

## 1. Propósito

Este repositorio define el estándar maestro para construir, recuperar, alinear, validar y mantener soluciones de software asistidas por IA.

El Blueprint es independiente del producto. Cada solución declara qué versión consume y mantiene su propia documentación, estado, evidencias, referencias visuales y skills específicas.

## 2. Modos de entrada

### Greenfield
Para soluciones nuevas. El trabajo comienza por Discovery y definición del producto antes de implementar.

### Brownfield
Para soluciones existentes. El trabajo comienza con inspección verificable del repositorio, reconstrucción AS-IS, análisis de brechas y definición TO-BE. No se deben inventar requisitos ausentes ni sustituir silenciosamente decisiones existentes.

Regla Brownfield: **ALIGN, DO NOT REWRITE**.

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
- Web: React + TypeScript + Vite + Tailwind CSS.
- Android: Kotlin nativo + Jetpack Compose.
- Contrato API: OpenAPI.
- QA operativo API: Postman.
- Control de versiones e integración: GitHub.

Estas decisiones son defaults, no excusa para reescribir un Brownfield funcional sin beneficio demostrado.

## 5. Gates de ingeniería

La cadena objetivo de Blueprint v0.4 extiende los gates API de v0.3 con una entrega visual y de clientes verificable:

`Brownfield Baseline → Requirements Ready → Architecture Ready → API Contract Ready → API Implemented → OpenAPI Valid → Postman Ready → API QA Pass → API Gate → Interface Inventory Ready → Design System Ready → Visual Review Pass → Client Architecture Ready → Client Implementation → Integration QA → Release Gate`

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
Exige QA positivo, negativo, seguridad, auditoría y validación de contrato. Cuando el entorno lo permita, la evidencia debe distinguir pruebas de aplicación de verificación HTTP/runtime contra la base autoritativa.

### API Gate
Solo cuando todos los artefactos API anteriores pasan se desbloquea el pipeline de experiencia y clientes.

### Interface Inventory Ready
Exige inventario numerado y trazable de las interfaces que aplican al proyecto. Cada vista debe declarar propósito, roles, datos, acciones, estados, navegación y responsabilidades API cuando correspondan. En Brownfield debe distinguirse lo observado de lo inferido y propuesto.

### Design System Ready
Exige identidad visual documentada y un sistema de diseño utilizable por mockups e implementación: tokens, tipografía, color, componentes, estados semánticos, responsive y accesibilidad. Un logo es condicional; no se debe fabricar uno solo para satisfacer el gate.

### Visual Review Pass
Se evalúa por **interface slice**. Una imagen generada no equivale a una vista revisada ni a una vista aprobada. El gate exige assets versionados, trazabilidad al inventario, revisión de contrato/accesibilidad y aprobación explícita. Las referencias visuales aprobadas se convierten en entradas para IAs posteriores.

### Client Architecture Ready
Se evalúa por **interface slice + plataforma**. Exige un contrato de arquitectura cliente suficiente para implementar el slice sin inventar auth, permisos, endpoints, estados, estrategia de errores o pruebas. La API sigue siendo el límite autoritativo de seguridad.

### Release Gate
No se libera una solución sin QA de integración, QA de seguridad, documentación de release y backup/restore cuando aplique.

## 6. Pipeline de Frontend & Experience

Después de `API_GATE = PASS`, la secuencia canónica es:

`interface_inventory → visual_identity → design_system → mockup_planning → mockups → visual_review_gate → client_architecture → web_implementation / android_implementation → integration_qa`

### 6.1 Slice de interfaz

Un `interface_slice` es un conjunto coherente de interfaces inventariadas que puede revisarse e implementarse como unidad. Puede ser un módulo, flujo o lote de vistas relacionadas.

Reglas:

- una interfaz pertenece a un inventario canónico (`WEB-###`, `APP-###` u otro esquema aprobado);
- un slice no puede saltarse el Design System;
- cada slice mantiene trazabilidad hacia requisitos, permisos y API cuando apliquen;
- `visual_review_pass` se evalúa por slice;
- `client_architecture_ready` se evalúa por slice y plataforma;
- un slice aprobado puede progresar sin esperar a que todos los demás slices del producto estén diseñados;
- una interfaz no aprobada no puede colarse en implementación solo porque otra interfaz del mismo producto fue aprobada.

### 6.2 Inventario de interfaces

Antes de generar imágenes debe existir un inventario numerado de vistas web/Android aplicables. Cada entrada declara como mínimo:

- ID estable y nombre;
- plataforma/módulo;
- propósito;
- roles/permisos;
- datos;
- acciones;
- estados;
- navegación;
- endpoints/responsabilidades API cuando apliquen;
- comportamiento responsive cuando aplique.

### 6.3 Identidad y Design System

La identidad precede al sistema de diseño y el sistema de diseño precede a mockups.

El sistema debe definir al menos:

- tokens de color, tipografía, espacios, radios y tamaños;
- jerarquía visual;
- componentes base;
- estados semánticos y de dominio;
- loading/empty/error/offline/forbidden y otros estados relevantes;
- responsive;
- accesibilidad;
- reglas de presentación RBAC sin sustituir el enforcement de API.

### 6.4 Mockup Planning y Mockups

Los mockups se generan en paquetes relacionados de máximo **10 vistas por tanda**.

Cada batch debe preservar:

- inventario objetivo;
- IDs de mockup;
- plataforma;
- responsabilidades API cuando apliquen;
- prompts/especificación necesarios para continuidad;
- rutas de assets visuales;
- estado de revisión separado del estado de generación.

Regla crítica:

`GENERATED ≠ REVIEWED ≠ APPROVED`

Los assets visuales aprobados deben permanecer versionados dentro del repositorio consumidor o en un almacén versionado explícitamente referenciado por el proyecto. No pueden existir únicamente en el historial del chat.

### 6.5 Visual Review

La revisión valida, como mínimo:

- coherencia con inventario y Design System;
- ausencia de capacidades de negocio inventadas;
- permisos/acciones compatibles con contratos;
- estados y errores;
- responsive;
- accesibilidad;
- consistencia con referencias previamente aprobadas.

### 6.6 Client Architecture

Antes de implementar un slice debe existir un contrato de cliente que cubra, como mínimo:

- auth/session lifecycle;
- API client y contrato;
- permisos/presentación RBAC;
- routing/navegación;
- estrategia de datos/estado;
- formularios y errores de validación;
- estados async/error/offline;
- mutaciones de riesgo/idempotencia cuando apliquen;
- observabilidad/request correlation;
- pruebas;
- coexistencia/migración Brownfield cuando aplique.

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

Una entrada declarada en el catálogo no se considera operativa hasta que resuelva a un artefacto versionado real.

## 9. Single Source of Truth

Cada concepto importante tiene un documento o catálogo propietario. Otros artefactos deben referenciarlo, no redefinirlo.

Las decisiones necesarias para continuidad de IA deben vivir en el repositorio: contratos, estado, prompts relevantes, manifests, evidencias y referencias visuales aprobadas.

## 10. Evidencias

Un check automático o un gate debe poder asociarse a evidencia verificable: archivo, commit, reporte, ejecución CI, resultado Postman, OpenAPI, test, asset visual, aprobación u otro artefacto auditable.

La etiqueta verde de un workflow no sustituye al resultado real de los comandos. Los pipelines deben propagar correctamente códigos de salida y diferenciar pruebas unitarias/feature de verificaciones runtime/integración cuando corresponda.

## 11. Versionado

El Blueprint usa versionado semántico. Los proyectos declaran la versión adoptada. Una nueva versión del Blueprint no modifica automáticamente proyectos existentes; primero se realiza un Compliance Review y se decide qué adoptar.

Durante la construcción de una versión futura, los catálogos/workflows de rama pueden declarar una versión prerelease como `0.4.0-dev`; el archivo `VERSION` conserva la última release estable hasta el cierre de la versión.

## 12. Proyecto piloto y referencias

`LuisHdezE/CareShift_Manager` es el Reference Pilot #1 para validar el flujo Brownfield y los formatos machine-readable antes de cerrar Blueprint v1.0.

Los pilotos:

- son evidencia, no norma oculta;
- pueden probar o cuestionar el Blueprint;
- no introducen reglas específicas del producto en el estándar;
- se revisan mediante Compliance Review antes de adoptar una nueva versión;
- preservan trabajo pendiente mientras el estándar evoluciona.

Los hallazgos del piloto se incorporan al Blueprint mediante cambios versionados y PRs separados.
