# Software Development Blueprint

> Development target: `0.5.0-dev`  
> Stable release remains the value declared in `VERSION` until release closure.

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
- `CONDITIONAL`: se activa por características o riesgo real del proyecto.
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

La cadena objetivo de Blueprint 0.5 conserva los gates de producto/API y convierte la entrega cliente en un flujo funcional, trazable y scoped:

`Brownfield Baseline → Requirements Ready → Interface Scope Baseline Ready → Architecture Ready → API Contract Ready → API Implemented → OpenAPI Valid → Postman Ready → API QA Pass → API Gate → Interface Inventory Ready → Design System Ready → Client Architecture Ready → Functional Slice Ready → Visual & Functional Review Pass → Integration QA Pass → Release Gate`

Los mockups/prototipos dejan de formar parte de esta cadena principal. Cuando aplican, usan un gate condicional independiente: `mockup_review_pass`.

### Brownfield Baseline

Exige inventario técnico, reconstrucción funcional, Gap Analysis, TO-BE y roadmap antes de tratar propuestas como requisitos.

### Requirements Ready

Exige actores/autorización, requisitos funcionales y no funcionales, reglas de negocio, casos de uso, criterios de aceptación y trazabilidad.

### Interface Scope Baseline Ready

Es un gate de planificación temprano, previo a Architecture/API Design.

Su objetivo es registrar **qué interfaces existen o se prevé que existan** sin fingir todavía que el contrato API autoritativo ya está resuelto.

- En Brownfield parte de interfaces `OBSERVED` reconstruidas desde AS-IS y de los requisitos reconciliados.
- En Greenfield deriva del producto, requisitos, casos de uso, journeys y criterios de aceptación aprobados.
- Puede declarar necesidades de datos/acciones todavía no vinculadas a `operationId`.
- No es un backlog ejecutable.
- No autoriza diseño de comportamiento de negocio en cliente ni implementación UI.
- No sustituye `Interface Inventory Ready`.

Esta separación evita dos extremos: diseñar el API a ciegas respecto del cliente real y, al mismo tiempo, diseñar el backend únicamente desde pantallas prematuras.

### Architecture Ready

Exige decisiones explícitas sobre arquitectura, seguridad, datos, base de datos autoritativa, auditoría, autenticación API, contrato de errores y versionado.

### API Contract Ready

Exige alcance API, inventario de endpoints, contrato de autenticación, permisos, mapeo de eventos, idempotencia y trazabilidad antes de escribir endpoints.

Cuando ya existe un API baseline consumido por clientes, un cambio de contrato que pueda afectar consumidores debe incluir `api.change_impact_analysis`: operationIds afectados, slices/plataformas dependientes y posible escalamiento de impacto.

### API Implemented

Exige endpoints implementados, autorización, auditoría y pruebas backend. No equivale al API Gate.

### OpenAPI Valid

Exige que el contrato OpenAPI cubra la API implementada y valide correctamente.

### Postman Ready

Exige colección, entornos y cobertura operacional completa de los endpoints implementados.

### API QA Pass

Exige QA positivo, negativo, seguridad, auditoría y validación de contrato. Cuando el entorno lo permita, la evidencia debe distinguir pruebas de aplicación de verificación HTTP/runtime contra la base autoritativa.

Para cambios posteriores al baseline, la revalidación de consumidores es **impact-based**. Un cambio acotado a ciertos `operationId` revalida los slices/plataformas que dependen de ellos. Cambios transversales de auth, autorización, seguridad, error contract u otra semántica global pueden escalar a plataforma o proyecto.

### API Gate

`api_gate` conserva alcance de proyecto y certifica el **baseline API inicial** antes del delivery cliente ejecutable.

Solo cuando los artefactos API anteriores pasan se desbloquea `Interface Inventory Ready`, Design System, Client Architecture e implementación funcional.

Un cambio API posterior no convierte automáticamente todo el producto en inválido. Debe existir análisis de impacto y revalidación proporcional a las dependencias reales. Evidencia no relacionada permanece válida salvo que un cambio transversal demuestre lo contrario.

La API continúa siendo la fuente autoritativa de autorización, reglas de negocio, transiciones y datos de negocio. El cliente no puede convertirse en una segunda autoridad porque resulte más cómodo para la UI.

### Interface Inventory Ready

Después de API Gate, el `Interface Scope Baseline` se reconcilia con el contrato autoritativo para producir el backlog cliente ejecutable del alcance comprometido.

Cada interfaz debe tener identidad estable y suficiente trazabilidad hacia:

- propósito y módulo;
- requisitos, casos de uso o criterios de aceptación cuando apliquen;
- roles y permisos;
- datos y fuente autoritativa;
- acciones;
- `operationId` canónico cuando exista operación API;
- estados y errores;
- navegación;
- dependencias;
- agrupación/orden de Functional Interface Slices;
- responsive y accesibilidad aplicables.

Una capacidad legítimamente local o estática puede declarar que no requiere operación API. Eso no autoriza a inventar una operación ficticia ni a ocultar una brecha de contrato.

### Design System Ready

Exige un sistema de diseño reutilizable por clientes funcionales y, cuando existan, mockups/prototipos: tokens, tipografía, color, componentes, estados semánticos, responsive y accesibilidad.

Visual Identity es `CONDITIONAL`. Se usa cuando existe una necesidad real de marca/identidad o cuando un Brownfield requiere preservar, normalizar o cambiar deliberadamente su identidad. Un logo personalizado no es obligatorio.

### Client Architecture Ready

Se evalúa por **interface slice + plataforma**.

Exige un contrato efectivo previo a implementación que defina:

- IDs de inventario del slice;
- Design System/tokens;
- OpenAPI y `operationId` consumidos;
- auth/session lifecycle;
- API client y contrato de errores;
- permisos y presentación RBAC;
- routing/navegación;
- server state, estado local, cache e invalidación;
- formularios y errores 422/409/429/globales;
- estados async/offline;
- idempotencia;
- observabilidad/request correlation;
- accesibilidad;
- testing;
- decisiones React o Kotlin/Android;
- coexistencia/cutover/rollback Brownfield cuando aplique.

Las referencias visuales estáticas aprobadas son entradas `CONDITIONAL`, no un prerrequisito universal. Cuando existen, deben estar versionadas y aprobadas. Un PASS para web no autoriza Android ni otro slice.

Para evitar duplicación, V5-3 puede representar el contrato efectivo como composición de un **Platform Client Architecture Baseline** reutilizable más un **Slice Architecture Binding/Override**. La estructura física puede cambiar, pero `client_architecture_ready` sigue evaluando el contrato efectivo del slice + plataforma.

### Functional Slice Ready

Se evalúa por **interface slice + plataforma**.

Un PASS permite declarar el slice `FUNCTIONAL` solamente cuando el Definition of Done funcional está evidenciado. Debe existir integración real con las fuentes autoritativas, no datos de negocio hardcodeados usados para simular funcionalidad.

Si falta una capacidad autoritativa de API, se activa la condición `BLOCKED_BY_API`; no se inventa el comportamiento en el cliente y no se pierde el lifecycle state válido previo.

### Visual & Functional Review Pass

Se evalúa sobre el **cliente funcional real** que se pretende entregar.

La revisión comprueba fidelidad al inventario, Design System, permisos, API, datos, estados, responsive, accesibilidad, interacción y referencias visuales aprobadas cuando existan. La aceptación humana es explícita.

### Integration QA Pass

Se evalúa por slice + plataforma. Incluye QA funcional, transporte/API real, integración, seguridad, responsive, accesibilidad, E2E e idempotencia/offline cuando apliquen.

Un PASS de un slice no desbloquea por sí solo la release completa. El Release Gate agrega todos los slices comprometidos.

### Release Gate

No se libera una solución hasta que todos los Functional Interface Slices comprometidos estén aceptados, la seguridad de release esté evidenciada, la documentación esté actualizada y backup/restore haya sido validado cuando aplique.

La documentación de release incluye actualizar `README.md` y el checkpoint humano `documentation/BLUEPRINT_CURRENT_STATE.md` cuando corresponda al propio Blueprint Master.

## 6. Pipeline de Frontend & Experience

Existe una separación explícita entre **scope descriptivo temprano** y **backlog ejecutable post-API**.

Antes del API contract se produce:

`requirements_domain → interface_scope_baseline → architecture_security_data → api_contract_design`

Después de `API_GATE = PASS`, la secuencia de delivery cliente ejecutable es:

`interface_inventory → design_system → client_architecture → functional_interface_slice → visual_functional_review → integration_qa`

Capacidades condicionales:

- `visual_identity`, cuando la identidad visual necesita definición, preservación o normalización;
- `mockup_planning → mockups → mockup_review`, cuando mockups/prototipos reducen riesgo o se requiere aprobación visual previa.

### 6.1 Interface Scope Baseline e Interface Inventory

Son dos niveles de madurez distintos.

#### Interface Scope Baseline

Describe intención/realidad de interfaces temprano:

- identidad preliminar o estable cuando ya existe;
- plataforma/módulo;
- propósito;
- requisitos/journeys;
- roles relevantes;
- datos/acciones necesarios aunque el contrato API todavía no exista;
- clasificación `OBSERVED`, `INFERRED` o `PROPOSED` cuando aplique.

No autoriza implementation y no exige inventar `operationId` inexistentes.

#### Interface Inventory Ready

Convierte ese alcance en backlog ejecutable después del API Gate:

- qué interfaces están comprometidas;
- qué requisitos satisfacen;
- quién puede acceder;
- qué permisos aplican;
- qué datos autoritativos muestran;
- qué acciones realizan;
- qué `operationId` consumen;
- qué estados deben soportar;
- qué dependencias tienen;
- a qué Functional Interface Slice pertenecen;
- cuál es su estado de implementación, review, QA y aceptación.

Los IDs de inventario son estables. Una interfaz referenciada downstream se depreca o migra explícitamente, no se renumera casualmente.

V5-2 debe decidir si ambos niveles usan un único schema con `maturity` explícito o contratos relacionados separados. Debe existir un único owner semántico para cada dato, sin duplicación silenciosa.

### 6.2 Functional Interface Slice

Un `functional_interface_slice` es la unidad canónica de ejecución de cliente.

Agrupa interfaces inventariadas que forman una capacidad, módulo o flujo coherente. La identidad lógica del slice puede compartirse entre plataformas, pero ejecución, arquitectura, review y QA permanecen scoped por plataforma cuando corresponde.

Ejemplo:

`tariffs + web ≠ tariffs + android`

Perfiles técnicos:

- Web se implementa mediante `web_implementation` con React.
- Android se implementa mediante `android_implementation` con Kotlin.

El perfil técnico no sustituye al slice. El slice es el propietario del lifecycle, DoD, evidencia, review, QA y aceptación.

### 6.3 Lifecycle funcional y quality gates

Lifecycle canónico del producto:

`INVENTORIED → READY → IN_PROGRESS → FUNCTIONAL → ACCEPTED`

Los estados expresan madurez del slice. **Visual & Functional Review** e **Integration QA** son quality gates/actividades, no lifecycle states duplicados.

#### INVENTORIED

El slice tiene identidad e interfaces vinculadas al inventario ejecutable.

#### READY

Las dependencias para implementar están disponibles: Design System, Client Architecture efectivo, API contract, permisos, `operationId` y prerequisitos aplicables.

#### IN_PROGRESS

La implementación funcional ha comenzado.

#### FUNCTIONAL

El Definition of Done funcional pasa para el slice + plataforma. Todavía no significa aceptación.

#### ACCEPTED

Requiere, como mínimo cuando aplica:

- `functional_slice_ready = PASS`;
- `visual_functional_review_pass = PASS`;
- `integration_qa_pass = PASS`;
- aceptación humana explícita.

El lifecycle no duplica el estado de esos gates.

### 6.4 BLOCKED_BY_API como condición superpuesta

`BLOCKED_BY_API` **no es un lifecycle state**. Es una condición/blocker overlay sobre el estado real del slice.

Ejemplo:

```text
lifecycle: IN_PROGRESS
blocker: BLOCKED_BY_API
```

Esto preserva el punto de progreso. Cuando el blocker se resuelve no hay que adivinar a qué estado regresar.

`BLOCKED_BY_API` significa que falta una capacidad autoritativa necesaria para continuar, por ejemplo:

- datos requeridos que la API no expone;
- operación ausente;
- semántica de permisos insuficiente;
- transición/estado de negocio no definido;
- contrato de error o mutación necesario no disponible.

Procedimiento:

1. detener únicamente el boundary cliente afectado;
2. registrar blocker, lifecycle preservado, interfaces/slice/plataforma afectados;
3. describir capacidad faltante y evidencia;
4. identificar `operationId` o ausencia contractual relacionada;
5. abrir una frontera API/backend separada si la brecha es válida y está en alcance;
6. actualizar primero el contrato autoritativo;
7. ejecutar impact analysis del cambio API;
8. resolver y evidenciar el blocker;
9. revalidar dependencias afectadas;
10. reanudar desde el lifecycle state preservado.

`BLOCKED_BY_API` no se usa para bugs ordinarios de frontend ni para incertidumbre estética.

### 6.5 Evolución del API e invalidación por impacto

El API Gate inicial es project-scoped porque certifica un baseline coherente de implementación, OpenAPI, Postman, seguridad, auditoría y QA antes de client delivery.

Después del baseline, el Blueprint evita dos errores:

1. **invalidación insuficiente**: conservar PASS aunque cambió una dependencia real;
2. **invalidación explosiva**: poner todo el producto en PENDING por cambiar un endpoint aislado.

Regla de impacto:

- todo cambio contractual posterior al baseline identifica los `operationId` afectados;
- el grafo de trazabilidad determina interfaces/slices/plataformas consumidoras;
- solo esas dependencias pierden vigencia o requieren revalidación por defecto;
- cambios de auth, autorización, seguridad, Problem Details/error contract, versionado o semántica transversal pueden escalar el alcance a plataforma/proyecto;
- un slice no afectado conserva su evidencia previa;
- un slice afectado no puede continuar o conservar `ACCEPTED` sin la revalidación requerida;
- no existe invalidación silenciosa ni PASS perpetuo frente a contrato cambiado.

V5-2/V5-3 deben hacer esta relación machine-readable y verificable, no dejarla únicamente en prosa.

### 6.6 Definition of Done funcional

Un slice no puede ser `FUNCTIONAL` solo porque renderiza o se parece al diseño esperado.

Cuando apliquen, deben estar implementados y evidenciados:

- routing/navegación real;
- componentes reales;
- Design System/tokens;
- API/fuente autoritativa real;
- auth/session;
- presentación RBAC;
- API como enforcement autoritativo;
- forms y feedback;
- mapeo de validación servidor;
- Problem Details o contrato de error aprobado;
- loading/empty/error;
- 401/403/404/409/422/429;
- offline/degraded;
- idempotencia de mutaciones de riesgo;
- request correlation;
- responsive;
- accesibilidad;
- pruebas mínimas;
- trazabilidad inventario → requisitos → permisos → `operationId` → tests;
- ausencia de capacidades de negocio inventadas;
- ausencia de datos de negocio autoritativos hardcodeados.

`FUNCTIONAL` significa comportamiento real y verificable. No significa que el slice ya haya pasado review visual/funcional ni Integration QA.

### 6.7 Regla de datos de negocio hardcodeados

Un cliente no puede recibir estado `FUNCTIONAL` si usa datos hardcodeados para representar verdad de negocio que debería provenir de una fuente autoritativa.

Ejemplos no válidos cuando la API es la autoridad:

- tarifas runtime hardcodeadas;
- usuarios/roles ficticios usados como comportamiento real;
- registros operativos o de auditoría hardcodeados;
- marketplace o catálogos de negocio fingidos;
- transiciones que muestran éxito sin confirmación del servidor.

Sí pueden existir:

- copy estático;
- labels e iconografía;
- tokens/constantes de presentación;
- fixtures de tests;
- Storybook/component examples;
- mockups/prototipos;
- fixtures aisladas de desarrollo claramente marcadas como no funcionales/no productivas.

JSON Schema no puede demostrar por sí solo esta regla. La evidencia combina contrato, validators donde sea posible, tests y revisión del código.

### 6.8 Visual Identity y Design System

Visual Identity es condicional. Design System es el contrato reutilizable obligatorio cuando existe cliente visual.

El Design System debe definir al menos:

- tokens de color, tipografía, espacios, radios y tamaños;
- jerarquía visual;
- componentes base;
- estados semánticos y de dominio;
- loading/empty/error/offline/forbidden y otros estados relevantes;
- responsive;
- accesibilidad;
- reglas de presentación RBAC sin sustituir el enforcement API.

### 6.9 Mockups y prototipos

Los mockups/prototipos son una capacidad `CONDITIONAL`.

Se recomiendan cuando:

- existe riesgo visual/UX material;
- se comparan varias direcciones visuales;
- se requiere aprobación humana antes de código;
- un flow complejo se beneficia de prototipado temprano;
- una referencia versionada reduce ambigüedad para futuras IAs.

No son obligatorios por el simple hecho de que exista una interfaz.

Cuando se usan, mantienen las reglas de 0.4:

- máximo 10 vistas relacionadas por generación;
- trazabilidad a inventario;
- assets versionados cuando se convierten en referencias aprobadas;
- prompts/especificación necesarios para continuidad;
- revisión de contrato y accesibilidad;
- aprobación explícita.

Regla crítica:

`GENERATED ≠ REVIEWED ≠ APPROVED`

Un consumidor puede declarar que `mockup_review_pass` sea obligatorio para un slice específico. Esa decisión debe ser explícita y justificada por riesgo/aprobación, no asumida universalmente por Blueprint.

### 6.10 Client Architecture

Antes de implementar un slice web o Android debe existir un contrato efectivo de arquitectura cliente para el slice + plataforma.

Reglas normativas:

1. `interface_inventory_ready` y `design_system_ready` deben estar PASS.
2. `client_architecture_ready` se evalúa por interface slice + plataforma.
3. Web acepta únicamente inventario web; Android acepta únicamente inventario Android.
4. Un cliente no crea endpoints, permisos, estados de negocio ni transiciones no presentes en contratos autoritativos.
5. La UI puede ocultar o deshabilitar acciones por permisos, pero la API autoriza o rechaza la operación.
6. Mutaciones de alto riesgo respetan idempotencia API y evitan duplicar efectos locales ante replay.
7. Request IDs se preservan para diagnóstico sin convertir telemetría cliente en un segundo sistema de auditoría.
8. Cache/offline no se convierte silenciosamente en fuente de verdad de negocio.
9. Brownfield conserva cliente existente hasta que el reemplazo pase QA/cutover aprobado.
10. Cambiar decisiones de arquitectura durante implementación requiere actualizar el artefacto efectivo y reevaluar el gate.
11. Mockups/referencias visuales aprobadas se consumen cuando existen, pero su ausencia no debe obligar a fabricar imágenes estáticas para validar arquitectura.
12. Una decisión compartida por toda una plataforma debe poder declararse una vez y ser referenciada por slices, evitando contratos repetitivos que solo cambian IDs.

La especificación completa se encuentra en `documentation/CLIENT_ARCHITECTURE_CONTRACT.md` y su schema canónico es `schemas/client-architecture.schema.json`. V5-3 realizará la migración estructural sin falsear el estado 0.4 histórico.

### 6.11 Visual & Functional Review

La revisión se realiza sobre el cliente funcional real.

Debe validar como mínimo, cuando aplique:

- fidelidad al Interface Inventory;
- Design System/tokens;
- requisitos/casos de uso;
- permisos y acciones;
- bindings de API/`operationId`;
- datos y estados reales;
- ausencia de capacidades inventadas;
- ausencia de datos de negocio autoritativos hardcodeados;
- forms y feedback de validación;
- responsive;
- accesibilidad;
- consistencia de interacción;
- comparación con referencias visuales aprobadas cuando existan.

Un mockup aprobado no reemplaza este review.

### 6.12 Integration QA

Integration QA produce evidencia scoped por slice + plataforma para:

- comportamiento funcional;
- transporte/API real;
- auth/session;
- RBAC y 401/403;
- errores/422/409/429;
- idempotencia/replay cuando aplique;
- loading/empty/error/offline;
- navegación cross-interface;
- responsive;
- accesibilidad automática más checks manuales apropiados al riesgo;
- journeys E2E críticos.

El Release Gate agrega todos los slices comprometidos y no asume que el PASS de un slice representa a los demás.

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

Blueprint 0.5 incorpora Functional Interface Slice como unidad de ejecución. Su skill ejecutable se materializa en la frontera de skills de la versión, no se considera disponible solo por aparecer mencionada en documentación.

## 9. Single Source of Truth e integridad semántica

Cada concepto importante tiene un documento, catálogo o schema propietario. Otros artefactos deben referenciarlo, no redefinirlo.

Las decisiones necesarias para continuidad de IA deben vivir en el repositorio: contratos, estado, prompts relevantes, manifests, evidencias y referencias visuales aprobadas.

El cumplimiento estructural no es suficiente. Blueprint 0.5 debe poder comprobar progresivamente **Cross-Artifact Semantic Integrity**:

`requirement → interface → permission → operationId → functional slice → client architecture → implementation/test → evidence → review/QA → acceptance`

Un ID sintácticamente válido pero inexistente en su fuente canónica no constituye trazabilidad. V5-2/V5-3 deben introducir validación semántica cruzada y fixtures negativos para impedir compliance theater.

Los pilotos son evidencia. Nunca modifican silenciosamente la norma maestra.

## 10. Evidencias

Un check automático o un gate debe poder asociarse a evidencia verificable: archivo, commit, reporte, ejecución CI, resultado Postman, OpenAPI, test, asset visual, aprobación u otro artefacto auditable.

La mera existencia de un archivo vacío o una referencia no verificable no debe bastar para un PASS cuando el check exige comportamiento real.

La etiqueta verde de un workflow no sustituye al resultado real de los comandos. Los pipelines deben propagar correctamente códigos de salida y diferenciar pruebas unitarias/feature de verificaciones runtime/integración cuando corresponda.

Los estados `FUNCTIONAL`, `ACCEPTED` y los gates scoped no se infieren por existencia de archivos. Requieren evidencia acorde al contrato y aceptación humana cuando esté definida.

## 11. Versionado

El Blueprint usa versionado semántico. Los proyectos declaran la versión adoptada. Una nueva versión del Blueprint no modifica automáticamente proyectos existentes; primero se realiza un Compliance Review y se decide qué adoptar.

Durante la construcción de una versión futura, los catálogos/workflows de rama o `main` de desarrollo pueden declarar una versión prerelease como `0.5.0-dev`; el archivo `VERSION` conserva la última release estable hasta el cierre de la versión.

Una release estable no se declara terminada hasta que schemas, templates, workflows, catalogs, validators, skills, documentación y release validation sean coherentes con la nueva versión.

Los schemas de consumidores deben validarse contra artefactos versionados/fijados por la versión adoptada. Los `$id` y mecanismos de resolución se revisan en V5-2 para evitar ambigüedad de provenance; no se asume resolución remota mutable como mecanismo de upgrade.

Al cerrar una release del Blueprint Master deben actualizarse, como mínimo cuando aplique:

- `README.md`;
- `documentation/BLUEPRINT_CURRENT_STATE.md`;
- release notes/manifest;
- `VERSION`;
- validadores y workflows de release.

## 12. Proyecto piloto y referencias

Los Reference Pilots prueban y desafían el Blueprint en condiciones reales Greenfield/Brownfield.

Reglas:

- son evidencia, no norma oculta;
- no introducen reglas específicas del producto en el estándar;
- no cambian de versión Blueprint automáticamente;
- se revisan mediante Compliance Review antes de adoptar una nueva versión;
- sus hallazgos entran al Master mediante cambios versionados y PRs separados;
- un piloto puede quedar deliberadamente congelado mientras evoluciona el Master.

`LuisHdezE/CareShift_Manager` continúa como Reference Pilot Brownfield registrado. `LuisHdezE/CUSA-Digital` es la evidencia Greenfield que motivó la evolución post-API de 0.5.0, pero no recibe cambios de cliente ni adopción automática durante la construcción del Master.

## 13. Blueprint Control Center

El Blueprint Control Center permanece como deuda estratégica visible, no como alcance de Blueprint 0.5.0.

Secuencia estratégica:

`Blueprint Core → pilotos CareShift/CUSA → hardening → Blueprint Control Center`

Los contratos del Blueprint deben exponer naturalmente metadata útil para ese futuro Control Center, como versiones adoptadas, fases, checks, gates, evidencia, compliance/drift, progreso de Functional Interface Slices, blockers `BLOCKED_BY_API`, QA, invalidación por impacto y release.

No se construye ahora un dashboard, base de datos de control o servicio de control-plane únicamente para anticipar esa etapa.
