# Spec: Gestión de Eventos

**Archivo:** `specs/gestion_eventos.md`  
**Módulo:** Eventos  
**Responsable:** 'Safrán Lautaro Javier'  
**Estado:** Draft

---

## 1. Objetivo y Contexto

El módulo de Gestión de Eventos es el núcleo de la plataforma. Permite a los organizadores crear, configurar y administrar eventos académicos (cursos, jornadas, congresos, charlas, talleres, etc.).

Un evento es la entidad central del sistema: todo lo demás (inscripciones, certificados, acreditación) depende de que un evento exista y esté correctamente configurado. Por eso este módulo debe estar implementado antes que cualquier otro.

El listado público de eventos es el punto de entrada para los participantes; no requiere autenticación.

---

## 2. Historias de Usuario y Criterios de Aceptación

### HU-01: Crear un evento    

**Como** organizador registrado en la plataforma  
**quiero** crear un nuevo evento académico con sus datos básicos y opcionales  
**para** publicarlo y permitir que los participantes se inscriban

**Criterios de aceptación:**

- CA-01: Si el organizador envía un formulario con nombre, tipo, fecha de inicio y fecha de fin válidas, el sistema crea el evento con estado `borrador` y devuelve HTTP 201.
- CA-02: Si la fecha de inicio es posterior a la fecha de fin, el sistema rechaza la operación con HTTP 422 y un mensaje descriptivo.
- CA-03: Si el cupo máximo se define, debe ser un número entero positivo mayor a cero. De lo contrario se rechaza con HTTP 422.
- CA-04: Si el cupo mínimo se define, debe ser menor o igual al cupo máximo. De lo contrario se rechaza con HTTP 422.
- CA-05: Si la fecha límite de inscripción se define, debe ser anterior a la fecha de inicio del evento. De lo contrario se rechaza con HTTP 422.
- CA-06: Un usuario con rol `participante` que intente crear un evento recibe HTTP 403.
- **CA-07**: Si el organizador ingresa datos inválidos o potencialmente maliciosos, el sistema rechaza la solicitud con HTTP 422.
- **CA-08**: El sistema debe registrar en logs la creación de cada evento, incluyendo usuario, fecha y hora.
- **CA-09**: El campo descripción no debe permitir la ejecución de código HTML o JavaScript.
- **CA-10**: Si el usuario no posee un JWT válido, el sistema rechaza la operación con HTTP 401.
- **CA-11**: El sistema debe verificar que el usuario posea permisos suficientes antes de procesar la solicitud.
- **CA-12**: Los errores internos del servidor no deben exponer información sensible sobre la infraestructura o la base de datos.

---

### HU-02: Publicar un evento

**Como** organizador  
**quiero** publicar un evento que estaba en borrador  
**para** que aparezca en el listado público y los participantes puedan inscribirse

**Criterios de aceptación:**

- CA-07: Solo el organizador creador del evento puede publicarlo. Otro usuario recibe HTTP 403.
- CA-08: Un evento en estado `borrador` con todos los campos obligatorios completos puede pasar a estado `publicado`. El sistema responde HTTP 200.
- CA-09: Un evento ya `publicado` no puede volver a estado `borrador`. El sistema responde HTTP 400.
- CA-10: Un evento `cancelado` no puede publicarse. El sistema responde HTTP 400.

---

### HU-03: Listar eventos (vista pública)

**Como** visitante del sitio (sin autenticación)  
**quiero** ver el listado de eventos disponibles con filtros  
**para** encontrar eventos de mi interés

**Criterios de aceptación:**

- CA-11: El endpoint `/events` es público (no requiere JWT) y devuelve solo eventos en estado `publicado`.
- CA-12: Se puede filtrar por tipo de evento (ej: `curso`, `congreso`).
- CA-13: Se puede filtrar por estado temporal: `proximos` (fecha de inicio futura) o `pasados` (fecha de inicio pasada).
- CA-14: La respuesta está paginada con tamaño de página por defecto de 20 elementos.
- CA-15: Cada evento en el listado muestra: nombre, tipo, fecha de inicio, fecha de fin, cupo disponible (si aplica) y estado de inscripción (abierta/cerrada).

---

### HU-04: Editar y cancelar un evento

**Como** organizador  
**quiero** poder editar los datos de un evento o cancelarlo  
**para** mantener la información actualizada o dar de baja un evento que no se realizará

**Criterios de aceptación:**

- CA-16: Un evento `publicado` puede editarse solo en campos no estructurales (descripción, lugar, fecha límite de inscripción). Los campos nombre, tipo y fechas de inicio/fin no pueden modificarse una vez publicado.
- CA-17: Un evento `borrador` puede editarse en todos sus campos.
- CA-18: Al cancelar un evento, su estado cambia a `cancelado` y el sistema devuelve HTTP 200. No se elimina de la base de datos.
- CA-19: No se puede cancelar un evento que ya fue `cancelado`. El sistema devuelve HTTP 400.

---

## 3. Requisitos Funcionales y Reglas de Negocio

### Datos del evento

| Campo | Tipo | Obligatorio | Descripción |
|---|---|---|---|
| `nombre` | string (max 200) | Sí | Nombre del evento |
| `tipo` | enum | Sí | `curso`, `jornada`, `congreso`, `charla`, `taller`, `otro` |
| `descripcion` | text | No | Descripción larga del evento |
| `fecha_inicio` | datetime (UTC) | Sí | Fecha y hora de inicio |
| `fecha_fin` | datetime (UTC) | Sí | Fecha y hora de fin |
| `lugar` | string (max 300) | No | Lugar físico o URL si es virtual |
| `cupo_minimo` | integer | No | Cupo mínimo para que el evento se realice |
| `cupo_maximo` | integer | No | Cupo máximo de inscriptos |
| `fecha_limite_inscripcion` | datetime (UTC) | No | Fecha límite para inscribirse |
| `estado` | enum | Auto | `borrador`, `publicado`, `cancelado`, `finalizado` |

### Reglas de negocio

- RN-01: El estado inicial de todo evento creado es `borrador`.
- RN-02: El sistema cambia automáticamente el estado a `finalizado` cuando la fecha de fin es superada y el evento estaba `publicado`. Esto se evalúa en cada consulta (no requiere tarea programada en esta fase).
- RN-03: Si un evento tiene cupo máximo, el sistema debe trackear los inscriptos confirmados y bloquear nuevas inscripciones cuando se alcance el límite.
- RN-04: Si la fecha límite de inscripción es alcanzada, el sistema cierra automáticamente las inscripciones (evaluado en cada consulta).
- RN-05: Solo el organizador que creó el evento puede editarlo o cancelarlo. Un admin puede hacerlo sobre cualquier evento.

---

## 4. Restricciones Técnicas Específicas de este Módulo

- El router de eventos se ubica en `backend/app/routers/events.py`.
- El modelo SQLAlchemy se ubica en `backend/app/models/event.py`.
- El schema Pydantic se ubica en `backend/app/schemas/event.py`.
- La lógica de negocio (validaciones de estado, cupo, fechas) se implementa en `backend/app/services/event_service.py`. El router solo llama al servicio.
- El endpoint de listado público (`GET /events`) NO requiere autenticación JWT.
- Los demás endpoints de este módulo (`POST`, `PUT`, `PATCH /cancel`) SÍ requieren JWT.
- No implementar soft-delete: los eventos cancelados permanecen en la base con estado `cancelado`.

---

## 5. Modelo de Datos de este Módulo

### Tabla: `events`

```sql
CREATE TABLE events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre VARCHAR(200) NOT NULL,
    tipo VARCHAR(50) NOT NULL,          -- enum: curso, jornada, congreso, charla, taller, otro
    descripcion TEXT,
    fecha_inicio TIMESTAMPTZ NOT NULL,
    fecha_fin TIMESTAMPTZ NOT NULL,
    lugar VARCHAR(300),
    cupo_minimo INTEGER,
    cupo_maximo INTEGER,
    fecha_limite_inscripcion TIMESTAMPTZ,
    estado VARCHAR(20) NOT NULL DEFAULT 'borrador',  -- borrador, publicado, cancelado, finalizado
    organizador_id UUID NOT NULL REFERENCES users(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### Relaciones

- `organizador_id` → `users.id` (FK, el usuario que creó el evento)
- Un evento tiene muchas inscripciones (`inscriptions.event_id`) — definida en la spec de Inscripción

---

## 6. Plan de Tareas

Las tareas están ordenadas para que cada una pueda ser ejecutada y validada de forma independiente antes de pasar a la siguiente.

### Tarea 1 — Modelo y migración
- Crear el modelo SQLAlchemy `Event` en `backend/app/models/event.py`
- Generar la migración Alembic correspondiente
- Verificar que la tabla se crea correctamente en la base de datos
- **Commit:** `feat(events): agregar modelo Event y migración`

### Tarea 2 — Schemas Pydantic
- Crear `EventCreate`, `EventUpdate`, `EventResponse` y `EventListItem` en `backend/app/schemas/event.py`
- `EventListItem` incluye solo los campos necesarios para el listado público
- **Commit:** `feat(events): agregar schemas Pydantic para eventos`

### Tarea 3 — Servicio y lógica de negocio
- Implementar `event_service.py` con las funciones: `create_event`, `publish_event`, `update_event`, `cancel_event`, `list_events`, `get_event_by_id`
- Incluir todas las validaciones de RN-01 a RN-05 y los criterios de aceptación
- **Commit:** `feat(events): implementar servicio de eventos con validaciones`

### Tarea 4 — Router y endpoints
- Implementar el router en `backend/app/routers/events.py` con los siguientes endpoints:
  - `GET /events` — listado público con filtros y paginación
  - `GET /events/{id}` — detalle de evento (público)
  - `POST /events` — crear evento (requiere JWT, rol organizador o admin)
  - `PUT /events/{id}` — editar evento (requiere JWT)
  - `PATCH /events/{id}/publish` — publicar evento (requiere JWT)
  - `PATCH /events/{id}/cancel` — cancelar evento (requiere JWT)
- **Commit:** `feat(events): implementar router de eventos`

### Tarea 5 — Tests
- Escribir tests en `backend/tests/test_events.py`
- Cubrir al menos: creación válida, creación con fechas inválidas, publicación, cancelación, listado público con filtros, acceso sin permisos
- **Commit:** `test(events): agregar tests del módulo de eventos`

---

## 7. Estrategia de Verificación

### Tests automáticos (Pytest)

| Test | Descripción | Resultado esperado |
|---|---|---|
| `test_create_event_ok` | POST con datos válidos | HTTP 201, estado `borrador` |
| `test_create_event_invalid_dates` | fecha_inicio > fecha_fin | HTTP 422 |
| `test_create_event_invalid_cupo` | cupo_minimo > cupo_maximo | HTTP 422 |
| `test_publish_event_ok` | Publicar evento en borrador | HTTP 200, estado `publicado` |
| `test_publish_already_published` | Publicar evento ya publicado | HTTP 400 |
| `test_cancel_event_ok` | Cancelar evento publicado | HTTP 200, estado `cancelado` |
| `test_list_events_public` | GET /events sin JWT | HTTP 200, solo publicados |
| `test_list_events_filter_type` | Filtrar por tipo | Solo eventos del tipo pedido |
| `test_create_event_forbidden` | Participante intenta crear | HTTP 403 |
| `test_edit_published_event_name` | Editar nombre de publicado | HTTP 400 |

### Verificación manual (Postman / curl)

1. Crear un evento como organizador → verificar estado `borrador`
2. Publicarlo → verificar que aparece en `GET /events`
3. Intentar publicarlo de nuevo → verificar HTTP 400
4. Cancelarlo → verificar que no aparece en listado público
5. Acceder a `GET /events` sin token → verificar que responde correctamente

---

## 8. Enriquecimiento de Seguridad (OWASP)

### Historia de Usuario enriquecida

HU-01: Crear un evento

### Riesgo mitigado

Manipulación de datos del sistema mediante entradas maliciosas, acceso no autorizado a funcionalidades administrativas y exposición de información sensible.

### Controles OWASP incorporados

- Broken Access Control
- Injection
- Security Logging and Monitoring Failures
- Identification and Authentication Failures
- Security Misconfiguration

### Justificación

Se incorporan controles para validar los datos de entrada, prevenir ataques de inyección, asegurar que únicamente usuarios autorizados puedan crear eventos y registrar las acciones realizadas para facilitar la auditoría y detección de incidentes de seguridad.
