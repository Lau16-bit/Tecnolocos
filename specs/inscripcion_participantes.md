# Spec: Inscripción de Participantes

**Archivo:** `specs/inscripcion_participantes.md`  
**Módulo:** Inscripciones  
**Responsable:** 'Safrán Lautaro Javier' 
**Estado:** Draft

---

## 1. Objetivo y Contexto

El módulo de Inscripción de Participantes permite que los usuarios se registren en los eventos publicados en la plataforma. Existen dos vías de inscripción:

1. **Autónoma:** el participante se inscribe por cuenta propia desde la plataforma web.
2. **Por personal:** un organizador inscribe manualmente a una persona (por ejemplo, cuando la inscripción se realizó por otro medio o cuando el participante no tiene cuenta en la plataforma).

Este módulo depende de que el módulo de Gestión de Eventos (`gestion_eventos.md`) esté implementado, ya que las inscripciones siempre referencian a un evento existente y publicado.

---

## 2. Historias de Usuario y Criterios de Aceptación

### HU-05: Inscripción autónoma de participante

**Como** usuario registrado en la plataforma con rol `participante`  
**quiero** inscribirme a un evento publicado  
**para** reservar mi lugar y poder asistir

**Criterios de aceptación:**

- CA-20: Si el evento está `publicado` y tiene cupo disponible (o sin límite de cupo), la inscripción se crea con estado `pendiente` y el sistema devuelve HTTP 201.
- CA-21: Si el evento está `cancelado`, `finalizado` o en `borrador`, el sistema rechaza la inscripción con HTTP 400 y mensaje "El evento no está disponible para inscripciones".
- CA-22: Si el evento tiene cupo máximo y ya fue alcanzado, el sistema rechaza la inscripción con HTTP 400 y mensaje "El evento no tiene lugares disponibles".
- CA-23: Si la fecha límite de inscripción fue superada, el sistema rechaza la inscripción con HTTP 400 y mensaje "El período de inscripción ha cerrado".
- CA-24: Si el usuario ya está inscripto en el evento (cualquier estado de inscripción excepto `cancelada`), el sistema rechaza la operación con HTTP 409 y mensaje "Ya estás inscripto en este evento".
- CA-25: Un usuario con rol `organizador` no puede inscribirse como participante usando este endpoint. Recibe HTTP 403.

---

### HU-06: Inscripción manual por personal del evento

**Como** organizador de un evento  
**quiero** inscribir manualmente a una persona en el evento  
**para** registrar participantes que se anotaron por fuera de la plataforma

**Criterios de aceptación:**

- CA-26: El organizador puede inscribir a una persona indicando nombre completo, email y tipo de participación. Si el email corresponde a un usuario registrado, la inscripción se vincula a esa cuenta.
- CA-27: Si el email no corresponde a ningún usuario registrado, la inscripción se crea igualmente como "invitado" (sin `usuario_id`).
- CA-28: Solo el organizador del evento o un admin puede usar este endpoint. Cualquier otro rol recibe HTTP 403.
- CA-29: Se respetan las mismas validaciones de cupo y fecha límite que en la inscripción autónoma (CA-22 y CA-23).
- CA-30: El organizador puede indicar el rol de la persona inscripta: `participante` o `disertante`.

---

### HU-07: Cancelar inscripción

**Como** participante registrado  
**quiero** cancelar mi inscripción a un evento  
**para** liberar mi lugar si no voy a poder asistir

**Criterios de aceptación:**

- CA-31: Un participante puede cancelar su propia inscripción si el evento aún no comenzó (fecha de inicio futura). El sistema devuelve HTTP 200 y la inscripción pasa a estado `cancelada`.
- CA-32: Si el evento ya comenzó (fecha de inicio pasada), el sistema rechaza la cancelación con HTTP 400 y mensaje "No es posible cancelar una inscripción de un evento ya iniciado".
- CA-33: Un organizador puede cancelar la inscripción de cualquier participante de su evento en cualquier momento.
- CA-34: Una inscripción ya en estado `cancelada` no puede cancelarse de nuevo. El sistema devuelve HTTP 400.

---

### HU-08: Ver inscriptos de un evento

**Como** organizador  
**quiero** ver el listado de personas inscriptas en mi evento  
**para** gestionar la logística y controlar el cupo

**Criterios de aceptación:**

- CA-35: El organizador puede obtener el listado completo de inscriptos de su evento, incluyendo nombre, email, rol asignado, estado de la inscripción y fecha de inscripción.
- CA-36: El listado puede filtrarse por estado de inscripción (`pendiente`, `confirmada`, `cancelada`).
- CA-37: La respuesta está paginada con tamaño por defecto de 20 elementos.
- CA-38: Un participante que intenta ver el listado de otro participante recibe HTTP 403.

---

## 3. Requisitos Funcionales y Reglas de Negocio

### Datos de la inscripción

| Campo | Tipo | Obligatorio | Descripción |
|---|---|---|---|
| `event_id` | UUID | Sí | Referencia al evento |
| `usuario_id` | UUID | No | Referencia al usuario (null si es invitado) |
| `nombre_completo` | string (max 200) | Sí | Nombre del inscripto |
| `email` | string | Sí | Email de contacto |
| `rol_inscripcion` | enum | Sí | `participante`, `disertante` |
| `estado` | enum | Auto | `pendiente`, `confirmada`, `cancelada` |
| `es_invitado` | boolean | Auto | True si no tiene cuenta en la plataforma |
| `inscripto_por` | UUID | No | ID del organizador si fue inscripción manual |

### Reglas de negocio

- RN-06: El estado inicial de toda inscripción es `pendiente`. La confirmación es un proceso separado (acreditación), fuera del alcance de este módulo.
- RN-07: Para el cálculo del cupo disponible, solo cuentan las inscripciones en estado `pendiente` o `confirmada`. Las canceladas liberan el cupo.
- RN-08: No puede haber dos inscripciones activas (estado `pendiente` o `confirmada`) del mismo email para el mismo evento.
- RN-09: Al cancelarse un evento, todas sus inscripciones activas se mantienen en la base de datos pero no impiden nuevas inscripciones (por ser un evento cancelado, éstas ya no son posibles por CA-21).
- RN-10: El campo `inscripto_por` registra el ID del organizador cuando la inscripción es manual; es `null` en inscripciones autónomas.

---

## 4. Restricciones Técnicas Específicas de este Módulo

- El router se ubica en `backend/app/routers/inscriptions.py`.
- El modelo SQLAlchemy en `backend/app/models/inscription.py`.
- Los schemas Pydantic en `backend/app/schemas/inscription.py`.
- La lógica de negocio en `backend/app/services/inscription_service.py`.
- Este módulo **importa** `event_service.py` para verificar el estado del evento; no accede directamente al modelo de eventos.
- El endpoint de inscripción autónoma (`POST /events/{event_id}/inscriptions`) requiere JWT con rol `participante`.
- El endpoint de inscripción manual (`POST /events/{event_id}/inscriptions/manual`) requiere JWT con rol `organizador` o `admin`.
- No implementar el envío de emails de confirmación en esta fase (está fuera de alcance según `Contracts.md`).

---

## 5. Modelo de Datos de este Módulo

### Tabla: `inscriptions`

```sql
CREATE TABLE inscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_id UUID NOT NULL REFERENCES events(id),
    usuario_id UUID REFERENCES users(id),       -- null si es invitado
    nombre_completo VARCHAR(200) NOT NULL,
    email VARCHAR(255) NOT NULL,
    rol_inscripcion VARCHAR(20) NOT NULL DEFAULT 'participante',  -- participante, disertante
    estado VARCHAR(20) NOT NULL DEFAULT 'pendiente',              -- pendiente, confirmada, cancelada
    es_invitado BOOLEAN NOT NULL DEFAULT FALSE,
    inscripto_por UUID REFERENCES users(id),    -- null si fue autónoma
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (event_id, email, estado)            -- unicidad por evento+email para estados activos (ver RN-08)
);
```

> **Nota sobre la unicidad (RN-08):** La restricción `UNIQUE(event_id, email, estado)` no es suficiente por sí sola para RN-08. La validación definitiva de duplicados debe implementarse a nivel de servicio en `inscription_service.py`, consultando inscripciones con estado `pendiente` o `confirmada` antes de crear una nueva.

### Relaciones

- `event_id` → `events.id` (FK)
- `usuario_id` → `users.id` (FK, nullable)
- `inscripto_por` → `users.id` (FK, nullable)

---

## 6. Plan de Tareas

### Tarea 1 — Modelo y migración
- Crear el modelo SQLAlchemy `Inscription` en `backend/app/models/inscription.py`
- Generar la migración Alembic (depende de que la migración de `events` ya exista)
- **Commit:** `feat(inscripcion): agregar modelo Inscription y migración`

### Tarea 2 — Schemas Pydantic
- Crear `InscriptionCreate`, `InscriptionManualCreate`, `InscriptionResponse`, `InscriptionListItem` en `backend/app/schemas/inscription.py`
- **Commit:** `feat(inscripcion): agregar schemas Pydantic para inscripciones`

### Tarea 3 — Servicio y lógica de negocio
- Implementar `inscription_service.py` con: `inscribir_participante`, `inscribir_manual`, `cancelar_inscripcion`, `listar_inscriptos`
- Incluir todas las validaciones de RN-06 a RN-10 y criterios de aceptación
- Usar `event_service.get_event_by_id()` para obtener el estado del evento
- **Commit:** `feat(inscripcion): implementar servicio de inscripciones con validaciones`

### Tarea 4 — Router y endpoints
- Implementar el router con los siguientes endpoints:
  - `POST /events/{event_id}/inscriptions` — inscripción autónoma (JWT, rol participante)
  - `POST /events/{event_id}/inscriptions/manual` — inscripción manual (JWT, rol organizador/admin)
  - `DELETE /events/{event_id}/inscriptions/{inscription_id}` — cancelar inscripción (JWT)
  - `GET /events/{event_id}/inscriptions` — listar inscriptos (JWT, rol organizador/admin)
- **Commit:** `feat(inscripcion): implementar router de inscripciones`

### Tarea 5 — Tests
- Escribir tests en `backend/tests/test_inscriptions.py`
- **Commit:** `test(inscripcion): agregar tests del módulo de inscripciones`

---

## 7. Estrategia de Verificación

### Tests automáticos (Pytest)

| Test | Descripción | Resultado esperado |
|---|---|---|
| `test_inscripcion_autonoma_ok` | Participante se inscribe a evento publicado con cupo | HTTP 201, estado `pendiente` |
| `test_inscripcion_evento_no_publicado` | Inscripción a evento en borrador | HTTP 400 |
| `test_inscripcion_sin_cupo` | Inscripción cuando cupo máximo alcanzado | HTTP 400 |
| `test_inscripcion_fecha_vencida` | Inscripción luego de fecha límite | HTTP 400 |
| `test_inscripcion_duplicada` | Mismo email se inscribe dos veces | HTTP 409 |
| `test_inscripcion_manual_ok` | Organizador inscribe invitado | HTTP 201, `es_invitado=True` |
| `test_inscripcion_manual_usuario_existente` | Organizador inscribe email de usuario registrado | HTTP 201, `usuario_id` no nulo |
| `test_inscripcion_manual_sin_permiso` | Participante intenta inscripción manual | HTTP 403 |
| `test_cancelar_inscripcion_antes_evento` | Participante cancela antes de inicio | HTTP 200, estado `cancelada` |
| `test_cancelar_inscripcion_evento_iniciado` | Participante cancela luego de inicio | HTTP 400 |
| `test_listar_inscriptos_ok` | Organizador lista inscriptos de su evento | HTTP 200, lista paginada |
| `test_listar_inscriptos_sin_permiso` | Participante intenta listar inscriptos | HTTP 403 |

### Verificación manual

1. Crear y publicar un evento con cupo máximo 2
2. Inscribir dos participantes → verificar HTTP 201
3. Intentar un tercer inscripto → verificar HTTP 400 "sin lugares"
4. Inscribir el mismo email dos veces → verificar HTTP 409
5. Usar endpoint manual para inscribir un invitado → verificar `es_invitado=True`
6. Cancelar una inscripción → verificar que el cupo se libera y un nuevo participante puede inscribirse
