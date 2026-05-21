# Spec: Registro y Autenticación de Usuarios

**Responsable:** Aquino Lucas Orlando  
**Módulo:** `auth`  
**Rama de trabajo:** `feature/auth`  
**Ruta base:** `/api/v1/auth`  
**Archivo de spec:** `/specs/spec-02-autenticacion.md`

---

## 1. Objetivo y Contexto

Este módulo gestiona el registro de nuevos usuarios y la autenticación de usuarios existentes en la plataforma de gestión de eventos académicos. Es el módulo base del sistema: todos los demás módulos dependen de él para identificar quién está realizando cada acción y con qué permisos.

Un usuario no autenticado puede ver el listado público de eventos, pero para inscribirse, comentar, recibir certificados o gestionar eventos, debe estar registrado e identificado mediante un token JWT.

El sistema usa **JWT con doble token**: un `access_token` de corta duración (1 hora) y un `refresh_token` de larga duración (7 días), tal como define el `Project.md`. Cuando el access token expira, el frontend usa el refresh token para obtener uno nuevo sin que el usuario tenga que volver a iniciar sesión.

---

## 2. Historias de Usuario y Criterios de Aceptación

### HU-01: Registro de nuevo usuario

**Como** visitante sin cuenta,  
**quiero** registrarme con mi nombre, apellido, email y contraseña,  
**para** poder acceder a las funcionalidades de la plataforma.

**Criterios de aceptación:**

| # | Criterio |
|---|----------|
| CA-01 | El sistema acepta los campos: `nombre`, `apellido`, `email`, `password` |
| CA-02 | Si el email ya está registrado → HTTP 400: `"El email ya se encuentra registrado"` |
| CA-03 | Si la contraseña tiene menos de 8 caracteres → HTTP 422: error de validación |
| CA-04 | Si el email no tiene formato válido → HTTP 422: error de validación |
| CA-05 | Si todos los datos son válidos → HTTP 201, retorna datos del usuario sin `password` |
| CA-06 | La contraseña se almacena hasheada con bcrypt, nunca en texto plano |
| CA-07 | El rol por defecto del nuevo usuario es `participante` |
| CA-08 | Los campos `created_at` y `updated_at` se asignan automáticamente |

---

### HU-02: Inicio de sesión

**Como** usuario registrado,  
**quiero** iniciar sesión con mi email y contraseña,  
**para** acceder a mi cuenta y operar en la plataforma.

**Criterios de aceptación:**

| # | Criterio |
|---|----------|
| CA-01 | El sistema acepta los campos: `email`, `password` |
| CA-02 | Si el email no existe o la contraseña es incorrecta → HTTP 401: `"Credenciales incorrectas"` (no se especifica cuál falló, por seguridad) |
| CA-03 | Si las credenciales son válidas → HTTP 200, retorna `access_token` (1h), `refresh_token` (7d) y datos básicos del usuario |
| CA-04 | El `access_token` es un JWT firmado con `SECRET_KEY` usando el algoritmo `HS256` |
| CA-05 | El `refresh_token` es un JWT firmado con `SECRET_KEY` con expiración de 7 días |

---

### HU-03: Renovar access token

**Como** usuario autenticado cuyo access token expiró,  
**quiero** obtener un nuevo access token usando mi refresh token,  
**para** no tener que iniciar sesión nuevamente.

**Criterios de aceptación:**

| # | Criterio |
|---|----------|
| CA-01 | Si el refresh token es válido → HTTP 200, retorna un nuevo `access_token` |
| CA-02 | Si el refresh token es inválido o expiró → HTTP 401: `"Token inválido o expirado"` |

---

### HU-04: Obtener datos del usuario autenticado

**Como** usuario autenticado,  
**quiero** consultar mis datos de perfil,  
**para** verificar mi información registrada en la plataforma.

**Criterios de aceptación:**

| # | Criterio |
|---|----------|
| CA-01 | Si el access token es válido → HTTP 200, retorna `id`, `nombre`, `apellido`, `email`, `rol` |
| CA-02 | Si no hay token o es inválido → HTTP 401: `"No autenticado"` |
| CA-03 | La contraseña nunca aparece en la respuesta |

---

## 3. Requisitos Funcionales y Reglas de Negocio

**RF-01:** El email debe tener formato válido. La validación la realiza Pydantic con `EmailStr`.

**RF-02:** No pueden existir dos usuarios con el mismo email. La restricción debe aplicarse tanto en la capa de servicio como en la base de datos (campo `UNIQUE`).

**RF-03:** Las contraseñas se hashean con `bcrypt` antes de persistir. Nunca se almacena la contraseña en texto plano.

**RF-04:** El `access_token` JWT contiene en su payload: `sub` (UUID del usuario como string), `exp` (timestamp de expiración).

**RF-05:** El `refresh_token` JWT contiene en su payload: `sub` (UUID del usuario), `exp`, `type: "refresh"`.

**RF-06:** El tiempo de expiración es configurable mediante variables de entorno: `ACCESS_TOKEN_EXPIRE_MINUTES` (default: 60) y `REFRESH_TOKEN_EXPIRE_DAYS` (default: 7).

**RF-07:** Los tokens JWT **no se almacenan en la base de datos**, tal como indica `Contracts.md` sección 6.

**RF-08:** El rol global por defecto de todo usuario nuevo es `participante`. Los valores válidos son: `participante`, `organizador`, `disertante`, `admin`.

**RF-09:** Todo endpoint protegido del sistema recibe el token en el header `Authorization: Bearer <access_token>` y responde HTTP 401 si es inválido o expiró.

---

## 4. Restricciones Técnicas

- **Lenguaje:** Python 3.12
- **Framework:** FastAPI
- **ORM:** SQLAlchemy 2.x con sesiones asíncronas (`AsyncSession`)
- **Validación:** Pydantic v2 (usar `model_config = ConfigDict(from_attributes=True)` en schemas de respuesta)
- **Hash de contraseñas:** `passlib[bcrypt]`
- **JWT:** `python-jose[cryptography]`
- **Base de datos:** PostgreSQL 16
- **Migraciones:** Alembic (nunca modificar la DB directamente)
- **Testing:** Pytest con base de datos separada (`TEST_DATABASE_URL`)
- **IDs:** UUID (no enteros), generados automáticamente por el ORM
- **Nombres de tablas:** `snake_case` y en inglés plural (ej: `users`)
- **Variables de entorno requeridas:**
  ```
  SECRET_KEY=<mínimo 32 caracteres>
  ALGORITHM=HS256
  ACCESS_TOKEN_EXPIRE_MINUTES=60
  REFRESH_TOKEN_EXPIRE_DAYS=7
  DATABASE_URL=postgresql://user:password@localhost:5432/eventos_db
  ```
- **Ubicación de archivos:**
  - Modelo: `backend/app/models/users.py`
  - Schemas: `backend/app/schemas/users.py`
  - Router: `backend/app/routers/auth.py`
  - Servicio: `backend/app/services/auth_service.py`
  - Seguridad: `backend/app/core/security.py`

---

## 5. Modelo de Datos

### Tabla: `users`

| Campo | Tipo | Restricciones | Descripción |
|-------|------|--------------|-------------|
| `id` | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | Identificador único |
| `nombre` | VARCHAR(100) | NOT NULL | Nombre del usuario |
| `apellido` | VARCHAR(100) | NOT NULL | Apellido del usuario |
| `email` | VARCHAR(255) | NOT NULL, UNIQUE | Email del usuario |
| `password_hash` | VARCHAR(255) | NOT NULL | Contraseña hasheada con bcrypt |
| `rol` | VARCHAR(50) | NOT NULL, DEFAULT 'participante' | Rol global en la plataforma |
| `activo` | BOOLEAN | NOT NULL, DEFAULT TRUE | Si la cuenta está activa |
| `created_at` | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | Gestionado automáticamente por el ORM |
| `updated_at` | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | Gestionado automáticamente por el ORM |

### Modelo SQLAlchemy (`backend/app/models/users.py`):
```python
import uuid
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    rol = Column(String(50), nullable=False, default="participante")
    activo = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
```

### Schemas Pydantic (`backend/app/schemas/users.py`):
```python
from pydantic import BaseModel, EmailStr, ConfigDict
from uuid import UUID

class UserCreate(BaseModel):
    nombre: str
    apellido: str
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    nombre: str
    apellido: str
    email: str
    rol: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    usuario: UserResponse

class RefreshRequest(BaseModel):
    refresh_token: str
```

---

## 6. Plan de Tareas

| # | Tarea | Archivo | Descripción |
|---|-------|---------|-------------|
| T-01 | Crear modelo `User` | `models/users.py` | Definir modelo SQLAlchemy con UUID, campos requeridos y timestamps automáticos |
| T-02 | Crear migración Alembic | `alembic/versions/` | Generar y aplicar migración para tabla `users` |
| T-03 | Crear schemas Pydantic | `schemas/users.py` | Definir `UserCreate`, `UserResponse`, `LoginRequest`, `TokenResponse`, `RefreshRequest` |
| T-04 | Implementar seguridad | `core/security.py` | Funciones: `hash_password`, `verify_password`, `create_access_token`, `create_refresh_token`, `decode_token` |
| T-05 | Implementar servicio | `services/auth_service.py` | Lógica de `registrar_usuario`, `autenticar_usuario`, `renovar_token` |
| T-06 | Implementar router | `routers/auth.py` | Endpoints: `POST /register`, `POST /login`, `POST /refresh`, `GET /me` |
| T-07 | Crear dependencia reutilizable | `core/security.py` | Función `get_current_user` como FastAPI Depends, usable por todos los módulos |
| T-08 | Registrar router | `main.py` | Incluir router de auth con prefijo `/api/v1/auth` |
| T-09 | Escribir tests | `tests/test_auth.py` | Tests para cada endpoint: camino feliz y camino de error |

---

## 7. Estrategia de Verificación

### `POST /api/v1/auth/register`

| Caso | Input | Resultado esperado |
|------|-------|--------------------|
| Registro exitoso | Datos válidos, email nuevo | HTTP 201, objeto usuario sin `password_hash` |
| Email duplicado | Email ya registrado | HTTP 400, `"El email ya se encuentra registrado"` |
| Contraseña corta | `password` de 5 caracteres | HTTP 422, error de validación Pydantic |
| Email inválido | `"no-es-un-email"` | HTTP 422, error de validación Pydantic |
| Campo faltante | Sin campo `nombre` | HTTP 422, error de validación Pydantic |

### `POST /api/v1/auth/login`

| Caso | Input | Resultado esperado |
|------|-------|--------------------|
| Login exitoso | Credenciales correctas | HTTP 200, `access_token` + `refresh_token` + datos usuario |
| Email inexistente | Email no registrado | HTTP 401, `"Credenciales incorrectas"` |
| Contraseña incorrecta | Password erróneo | HTTP 401, `"Credenciales incorrectas"` |

### `POST /api/v1/auth/refresh`

| Caso | Input | Resultado esperado |
|------|-------|--------------------|
| Refresh válido | `refresh_token` vigente | HTTP 200, nuevo `access_token` |
| Refresh expirado | Token vencido | HTTP 401, `"Token inválido o expirado"` |
| Refresh inválido | Token mal formado | HTTP 401, `"Token inválido o expirado"` |

### `GET /api/v1/auth/me`

| Caso | Input | Resultado esperado |
|------|-------|--------------------|
| Token válido | Header con JWT vigente | HTTP 200, datos del usuario |
| Sin token | Sin header `Authorization` | HTTP 401, `"No autenticado"` |
| Token expirado | JWT vencido | HTTP 401, `"No autenticado"` |

### Verificaciones de seguridad
- La contraseña **nunca** aparece en ninguna respuesta de la API
- En la DB, `password_hash` empieza con `$2b$` (bcrypt)
- Dos usuarios con el mismo email no pueden crearse
- Los tokens no se almacenan en ninguna tabla de la DB
