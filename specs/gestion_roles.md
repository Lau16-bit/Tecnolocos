# Spec: Gestión de Roles

**Archivo:** `specs/gestion_roles.md`  
**Módulo:** `roles`  
**Responsable:** Aquino Lucas Orlando  
**Rama de trabajo:** `feature/roles`  
**Ruta base:** `/api/v1`  
**Estado:** Draft

---

## 1. Objetivo y Contexto

Este módulo gestiona la asignación y administración de roles de los usuarios dentro de la plataforma y, de forma específica, dentro de cada evento. Existen dos niveles de rol:

1. **Rol global (plataforma):** define el nivel de acceso general del usuario. Se establece en el registro y puede ser modificado únicamente por un `admin`. Los valores posibles son: `participante`, `organizador`, `disertante`, `admin`.

2. **Rol por evento:** dentro de un evento específico, un usuario puede tener un rol distinto a su rol global. Por ejemplo, un usuario con rol global `participante` puede ser `disertante` en un evento particular. Este rol es manejado a través del campo `rol_inscripcion` de la tabla `inscriptions` (ver spec de Inscripción), pero su asignación y modificación explícita es responsabilidad de este módulo.

El módulo de Gestión de Roles depende de:
- `auth` (módulo de autenticación): para identificar al usuario autenticado.
- `inscriptions` (módulo de inscripciones): porque el rol por evento se almacena junto a la inscripción.

Este módulo no crea ni elimina usuarios. Solo modifica roles. Tampoco gestiona permisos de acceso a endpoints: eso lo hace el middleware de autenticación basado en los roles ya establecidos.

---

## 2. Historias de Usuario y Criterios de Aceptación

### HU-09: Cambiar rol global de un usuario

**Como** administrador del sistema  
**quiero** cambiar el rol global de un usuario registrado  
**para** otorgarle o revocarle permisos de organizador, disertante u otros niveles de acceso

**Criterios de aceptación:**

| # | Criterio |
|---|----------|
| CA-39 | El endpoint solo es accesible por usuarios con rol `admin`. Cualquier otro rol recibe HTTP 403. |
| CA-40 | Si el usuario objetivo no existe → HTTP 404: `"Usuario no encontrado"`. |
| CA-41 | Si el nuevo rol no es uno de los valores válidos (`participante`, `organizador`, `disertante`, `admin`) → HTTP 422: error de validación. |
| CA-42 | Si el nuevo rol es igual al rol actual del usuario → HTTP 400: `"El usuario ya tiene ese rol asignado"`. |
| CA-43 | Si la operación es válida → HTTP 200, retorna los datos actualizados del usuario (sin `password_hash`). |
| CA-44 | Un admin no puede cambiarse a sí mismo el rol. Recibe HTTP 400: `"No podés modificar tu propio rol"`. |

---

### HU-10: Cambiar rol de un participante dentro de un evento

**Como** organizador de un evento  
**quiero** cambiar el rol de un inscripto en mi evento (de `participante` a `disertante` o viceversa)  
**para** reflejar correctamente la participación de cada persona en el evento

**Criterios de aceptación:**

| # | Criterio |
|---|----------|
| CA-45 | Solo el organizador del evento o un `admin` puede usar este endpoint. Cualquier otro rol recibe HTTP 403. |
| CA-46 | Si el evento no existe → HTTP 404: `"Evento no encontrado"`. |
| CA-47 | Si la inscripción no existe o no pertenece al evento indicado → HTTP 404: `"Inscripción no encontrada"`. |
| CA-48 | Si la inscripción está en estado `cancelada` → HTTP 400: `"No se puede modificar el rol de una inscripción cancelada"`. |
| CA-49 | Si el nuevo `rol_inscripcion` no es `participante` ni `disertante` → HTTP 422: error de validación. |
| CA-50 | Si el nuevo rol es igual al rol actual de la inscripción → HTTP 400: `"El inscripto ya tiene ese rol en el evento"`. |
| CA-51 | Si la operación es válida → HTTP 200, retorna la inscripción actualizada con el nuevo `rol_inscripcion`. |

---

### HU-11: Consultar usuarios por rol global

**Como** administrador  
**quiero** listar todos los usuarios que tienen un determinado rol global  
**para** tener visibilidad de quiénes son organizadores, disertantes u otros perfiles

**Criterios de aceptación:**

| # | Criterio |
|---|----------|
| CA-52 | Solo un `admin` puede acceder a este endpoint. Cualquier otro rol recibe HTTP 403. |
| CA-53 | Si no se especifica filtro de rol, se devuelven todos los usuarios. |
| CA-54 | Si se especifica un rol inválido como filtro → HTTP 422: error de validación. |
| CA-55 | La respuesta está paginada con tamaño por defecto de 20 elementos, siguiendo el contrato de paginación de `Contracts.md`. |
| CA-56 | Cada ítem de la lista muestra: `id`, `nombre`, `apellido`, `email`, `rol`, `activo`. |

---

### HU-12: Ver el propio perfil con rol actual

**Como** usuario autenticado  
**quiero** ver mi perfil incluyendo mi rol actual en la plataforma  
**para** conocer mis permisos y nivel de acceso

**Criterios de aceptación:**

| # | Criterio |
|---|----------|
| CA-57 | Si el access token es válido → HTTP 200, retorna `id`, `nombre`, `apellido`, `email`, `rol`, `activo`. |
| CA-58 | Si el token es inválido o ausente → HTTP 401. |
| CA-59 | La contraseña nunca aparece en la respuesta. |

> **Nota:** Este endpoint puede reutilizar `GET /auth/me` ya implementado en el módulo `auth`. Si ya está disponible, no duplicar; solo documentarlo aquí como dependencia.

---

## 3. Requisitos Funcionales y Reglas de Negocio

**RF-10:** Los valores válidos para el rol global son: `participante`, `organizador`, `disertante`, `admin`. Cualquier otro valor es rechazado por Pydantic en la capa de schemas.

**RF-11:** Solo un usuario con rol `admin` puede modificar el rol global de otro usuario. Los organizadores no pueden cambiar roles globales.

**RF-12:** Un admin no puede modificar su propio rol global, para evitar que el sistema quede sin administradores por error.

**RF-13:** El rol por evento (`rol_inscripcion`) solo puede tomar los valores `participante` o `disertante`. El rol `organizador` no se asigna como `rol_inscripcion` en inscripciones: el organizador es quien crea el evento (campo `organizador_id` en la tabla `events`).

**RF-14:** Modificar el `rol_inscripcion` de una inscripción no modifica el rol global del usuario. Son campos independientes.

**RF-15:** El historial de cambios de roles no se almacena en esta fase (fuera de alcance). Solo se persiste el estado actual.

**RF-16:** Al listar usuarios por rol, se incluyen usuarios con `activo = FALSE` para que el admin tenga visibilidad completa. El campo `activo` se expone en la respuesta.

---

## 4. Restricciones Técnicas Específicas de este Módulo

- El router se ubica en `backend/app/routers/roles.py`.
- Los schemas Pydantic específicos de este módulo se ubican en `backend/app/schemas/roles.py`.
- La lógica de negocio se implementa en `backend/app/services/role_service.py`. El router solo llama al servicio.
- Este módulo **no define modelos nuevos**: opera sobre los modelos `User` (de `auth`) e `Inscription` (de `inscriptions`). Importa los modelos desde sus respectivos archivos.
- El servicio importa la dependencia `get_current_user` desde `app.core.security` para verificar autenticación y rol del usuario que hace la solicitud.
- Todos los endpoints de este módulo requieren JWT (`Authorization: Bearer <token>`).
- El endpoint de listado de usuarios por rol (`GET /users`) requiere además rol `admin`.
- El endpoint de cambio de rol por evento (`PATCH /events/{event_id}/inscriptions/{inscription_id}/role`) requiere rol `organizador` o `admin`.
- **Variables de entorno requeridas:** las mismas que el módulo `auth` (no agrega nuevas).
- **Ubicación de archivos:**
  - Router: `backend/app/routers/roles.py`
  - Schemas: `backend/app/schemas/roles.py`
  - Servicio: `backend/app/services/role_service.py`

---

## 5. Modelo de Datos de este Módulo

Este módulo no crea tablas nuevas. Opera sobre las tablas existentes:

### Tabla `users` (definida en spec `auth`)

Campo relevante modificado por este módulo:

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `rol` | VARCHAR(50) | Rol global del usuario. Valores: `participante`, `organizador`, `disertante`, `admin` |

### Tabla `inscriptions` (definida en spec `inscripcion_participantes`)

Campo relevante modificado por este módulo:

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `rol_inscripcion` | VARCHAR(20) | Rol del usuario en el contexto del evento. Valores: `participante`, `disertante` |

### Schemas Pydantic (`backend/app/schemas/roles.py`)

```python
from pydantic import BaseModel, ConfigDict
from uuid import UUID
from enum import Enum

class RolGlobal(str, Enum):
    participante = "participante"
    organizador = "organizador"
    disertante = "disertante"
    admin = "admin"

class RolInscripcion(str, Enum):
    participante = "participante"
    disertante = "disertante"

class CambiarRolGlobalRequest(BaseModel):
    rol: RolGlobal

class CambiarRolInscripcionRequest(BaseModel):
    rol_inscripcion: RolInscripcion

class UsuarioRolResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    nombre: str
    apellido: str
    email: str
    rol: str
    activo: bool

class InscripcionRolResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    event_id: UUID
    usuario_id: UUID | None
    nombre_completo: str
    email: str
    rol_inscripcion: str
    estado: str
```

---

## 6. Plan de Tareas

| # | Tarea | Archivo | Descripción |
|---|-------|---------|-------------|
| T-01 | Crear schemas Pydantic | `schemas/roles.py` | Definir enums `RolGlobal`, `RolInscripcion` y schemas de request/response |
| T-02 | Implementar servicio | `services/role_service.py` | Funciones: `cambiar_rol_global`, `cambiar_rol_inscripcion`, `listar_usuarios_por_rol` |
| T-03 | Implementar router | `routers/roles.py` | Endpoints: `PATCH /users/{user_id}/role`, `PATCH /events/{event_id}/inscriptions/{inscription_id}/role`, `GET /users` |
| T-04 | Registrar router | `main.py` | Incluir router con prefijo `/api/v1` |
| T-05 | Escribir tests | `tests/test_roles.py` | Tests para cada endpoint: camino feliz y camino de error |

### Detalle de cada tarea

**T-01 — Schemas Pydantic**
- Crear `backend/app/schemas/roles.py` con los enums y schemas detallados en la sección 5.
- Commit: `feat(roles): agregar schemas Pydantic para gestión de roles`

**T-02 — Servicio**
- Implementar `role_service.py` con las tres funciones principales:
  - `cambiar_rol_global(db, admin_user, user_id, nuevo_rol)`: valida que el admin no se modifique a sí mismo, que el usuario exista, que el rol sea diferente al actual, y actualiza el campo `rol` en `users`.
  - `cambiar_rol_inscripcion(db, solicitante, event_id, inscription_id, nuevo_rol)`: verifica que el solicitante sea organizador del evento o admin, que la inscripción exista y esté activa, y actualiza `rol_inscripcion` en `inscriptions`.
  - `listar_usuarios_por_rol(db, rol_filtro, page, size)`: consulta paginada sobre la tabla `users` con filtro opcional por `rol`.
- Commit: `feat(roles): implementar servicio de gestión de roles`

**T-03 — Router**
- Implementar los tres endpoints en `routers/roles.py`:
  - `PATCH /users/{user_id}/role` — requiere JWT con rol `admin`
  - `PATCH /events/{event_id}/inscriptions/{inscription_id}/role` — requiere JWT con rol `organizador` o `admin`
  - `GET /users` — requiere JWT con rol `admin`
- Commit: `feat(roles): implementar router de roles`

**T-04 — Registro del router**
- En `backend/app/main.py`, incluir el router:
  ```python
  from app.routers import roles
  app.include_router(roles.router, prefix="/api/v1", tags=["roles"])
  ```
- Commit: `chore(roles): registrar router de roles en main.py`

**T-05 — Tests**
- Cubrir los casos indicados en la sección 7.
- Commit: `test(roles): agregar tests del módulo de gestión de roles`

---

## 7. Estrategia de Verificación

### Tests automáticos (Pytest)

| Test | Descripción | Resultado esperado |
|---|---|---|
| `test_cambiar_rol_global_ok` | Admin cambia rol de un participante a organizador | HTTP 200, `rol` actualizado |
| `test_cambiar_rol_global_sin_permiso` | Organizador intenta cambiar rol global | HTTP 403 |
| `test_cambiar_rol_global_usuario_inexistente` | Admin cambia rol de ID inexistente | HTTP 404 |
| `test_cambiar_rol_global_mismo_rol` | Admin asigna rol que el usuario ya tiene | HTTP 400 |
| `test_cambiar_rol_global_a_si_mismo` | Admin intenta modificar su propio rol | HTTP 400 |
| `test_cambiar_rol_inscripcion_ok` | Organizador cambia participante a disertante | HTTP 200, `rol_inscripcion` actualizado |
| `test_cambiar_rol_inscripcion_sin_permiso` | Participante intenta cambiar rol de inscripción | HTTP 403 |
| `test_cambiar_rol_inscripcion_cancelada` | Intento de cambiar rol en inscripción cancelada | HTTP 400 |
| `test_cambiar_rol_inscripcion_inexistente` | Inscripción ID inválido | HTTP 404 |
| `test_listar_usuarios_por_rol_ok` | Admin lista usuarios con rol `organizador` | HTTP 200, solo organizadores |
| `test_listar_usuarios_sin_filtro` | Admin lista todos los usuarios | HTTP 200, lista paginada completa |
| `test_listar_usuarios_rol_invalido` | Filtro con rol no válido | HTTP 422 |
| `test_listar_usuarios_sin_permiso` | Participante intenta listar usuarios | HTTP 403 |

### Verificación manual (Postman / curl)

1. Registrar dos usuarios (A y B) con rol por defecto `participante`.
2. Crear un usuario con rol `admin` directamente en la base (seed de desarrollo).
3. Como admin, cambiar el rol de A a `organizador` → verificar HTTP 200.
4. Intentar que A (organizador) cambie el rol de B → verificar HTTP 403.
5. Como admin, intentar cambiarse a sí mismo el rol → verificar HTTP 400.
6. Crear un evento como organizador A e inscribir a B.
7. Como A, cambiar el `rol_inscripcion` de B de `participante` a `disertante` → verificar HTTP 200.
8. Cancelar la inscripción de B e intentar cambiar su rol nuevamente → verificar HTTP 400.
9. Como admin, listar usuarios con filtro `?rol=organizador` → verificar que solo aparece A.
