# Contracts.md — Tecnolocos

Este archivo define los contratos entre módulos del sistema. Un contrato especifica cómo se comunican los distintos módulos entre sí: qué datos envían, qué datos reciben y qué comportamiento se espera. Todo agente de IA que implemente un módulo debe respetar estos contratos para garantizar la integración correcta del sistema.

---

## Convenciones Generales

- Todas las comunicaciones entre frontend y backend se realizan via **HTTP/REST** en formato **JSON**
- El prefijo base de todas las rutas es `/api/v1/`
- Las rutas protegidas requieren el header: `Authorization: Bearer <access_token>`
- Los errores siguen siempre el formato:
```json
{
  "detail": "Mensaje de error descriptivo"
}
```
- Las fechas se manejan en formato **ISO 8601**: `YYYY-MM-DDTHH:MM:SSZ`

---

## Contrato 1: Módulo de Autenticación (`/api/v1/auth`)

**Responsable:** Aquino Lucas Orlando

### Registro de usuario
```
POST /api/v1/auth/register
```
**Body:**
```json
{
  "nombre": "string",
  "apellido": "string",
  "email": "string (único, formato email válido)",
  "password": "string (mínimo 8 caracteres)"
}
```
**Respuesta exitosa (201):**
```json
{
  "id": "integer",
  "nombre": "string",
  "apellido": "string",
  "email": "string",
  "rol_global": "participante"
}
```

### Login
```
POST /api/v1/auth/login
```
**Body:**
```json
{
  "email": "string",
  "password": "string"
}
```
**Respuesta exitosa (200):**
```json
{
  "access_token": "string (JWT)",
  "token_type": "bearer",
  "usuario": {
    "id": "integer",
    "nombre": "string",
    "apellido": "string",
    "email": "string",
    "rol_global": "string"
  }
}
```

### Obtener usuario autenticado
```
GET /api/v1/auth/me
```
**Header requerido:** `Authorization: Bearer <token>`

**Respuesta exitosa (200):**
```json
{
  "id": "integer",
  "nombre": "string",
  "apellido": "string",
  "email": "string",
  "rol_global": "string"
}
```

**Contrato con otros módulos:** Todos los módulos que requieran identificar al usuario deben llamar internamente a `/api/v1/auth/me` o validar el JWT para obtener el `usuario_id`.

---

## Contrato 2: Módulo de Gestión de Eventos (`/api/v1/eventos`)

**Responsable:** Safrán Lautaro Javier

### Listar eventos (público)
```
GET /api/v1/eventos
```
**Query params opcionales:**
- `tipo`: string (curso, jornada, congreso, charla)
- `estado`: string (futuro, pasado)

**Respuesta exitosa (200):**
```json
[
  {
    "id": "integer",
    "nombre": "string",
    "tipo": "string",
    "descripcion": "string",
    "fecha_inicio": "datetime",
    "fecha_fin": "datetime",
    "cupo_minimo": "integer | null",
    "cupo_maximo": "integer | null",
    "fecha_limite_inscripcion": "datetime | null",
    "organizador_id": "integer"
  }
]
```

### Obtener evento por ID (público)
```
GET /api/v1/eventos/{evento_id}
```
**Respuesta exitosa (200):** mismo objeto que arriba.

### Crear evento (requiere auth, rol: organizador)
```
POST /api/v1/eventos
```
**Body:**
```json
{
  "nombre": "string",
  "tipo": "string",
  "descripcion": "string",
  "fecha_inicio": "datetime",
  "fecha_fin": "datetime",
  "cupo_minimo": "integer | null",
  "cupo_maximo": "integer | null",
  "fecha_limite_inscripcion": "datetime | null"
}
```
**Respuesta exitosa (201):** objeto evento completo.

**Contrato con otros módulos:** El `evento_id` generado aquí es utilizado por los módulos de Inscripción, Certificados y Encuestas.

---

## Contrato 3: Módulo de Inscripción (`/api/v1/inscripciones`)

**Responsable:** Safrán Lautaro Javier

### Inscribirse a un evento (requiere auth)
```
POST /api/v1/inscripciones
```
**Body:**
```json
{
  "evento_id": "integer"
}
```
**Respuesta exitosa (201):**
```json
{
  "id": "integer",
  "usuario_id": "integer",
  "evento_id": "integer",
  "estado": "pendiente",
  "fecha_inscripcion": "datetime"
}
```

### Listar inscripciones de un evento (requiere auth, rol: organizador)
```
GET /api/v1/inscripciones/evento/{evento_id}
```
**Respuesta exitosa (200):**
```json
[
  {
    "id": "integer",
    "usuario_id": "integer",
    "nombre_usuario": "string",
    "email_usuario": "string",
    "estado": "string",
    "fecha_inscripcion": "datetime"
  }
]
```

**Contrato con otros módulos:** El módulo de Acreditación y Certificados consume el `estado` de la inscripción para determinar si corresponde emitir un certificado.

---

## Contrato 4: Módulo de Gestión de Roles (`/api/v1/roles`)

**Responsable:** Aquino Lucas Orlando

### Asignar rol a usuario en un evento (requiere auth, rol: organizador)
```
POST /api/v1/roles/asignar
```
**Body:**
```json
{
  "usuario_id": "integer",
  "evento_id": "integer",
  "rol": "string (organizador | participante | disertante)"
}
```
**Respuesta exitosa (200):**
```json
{
  "usuario_id": "integer",
  "evento_id": "integer",
  "rol": "string"
}
```

### Obtener rol de usuario en evento
```
GET /api/v1/roles/{evento_id}/{usuario_id}
```
**Respuesta exitosa (200):**
```json
{
  "usuario_id": "integer",
  "evento_id": "integer",
  "rol": "string"
}
```

**Contrato con otros módulos:** Todos los módulos que requieran verificar permisos deben consultar este endpoint para obtener el rol del usuario dentro de un evento específico.

---

## Contrato 5: Módulo de Certificados (`/api/v1/certificados`)

**Responsable:** Rivas Matías

### Generar certificado (requiere auth, rol: organizador)
```
POST /api/v1/certificados
```
**Body:**
```json
{
  "usuario_id": "integer",
  "evento_id": "integer",
  "tipo": "string (asistencia | aprobacion | expositor | autor)"
}
```
**Respuesta exitosa (201):**
```json
{
  "id": "integer",
  "usuario_id": "integer",
  "evento_id": "integer",
  "tipo": "string",
  "codigo_verificacion": "string (UUID único)",
  "fecha_emision": "datetime",
  "url_descarga": "string"
}
```

**Contrato con otros módulos:** Requiere que el usuario tenga una inscripción con estado `acreditado` en el módulo de Inscripción.

---

## Contrato 6: Módulo de Encuestas (`/api/v1/encuestas`)

**Responsable:** Rivas Matías

### Crear encuesta para un evento (requiere auth, rol: organizador)
```
POST /api/v1/encuestas
```
**Body:**
```json
{
  "evento_id": "integer",
  "preguntas": [
    {
      "texto": "string",
      "tipo": "string (texto_libre | escala_1_5 | opcion_multiple)",
      "opciones": ["string"] 
    }
  ]
}
```
**Respuesta exitosa (201):**
```json
{
  "id": "integer",
  "evento_id": "integer",
  "preguntas": [...]
}
```

### Responder encuesta (requiere auth)
```
POST /api/v1/encuestas/{encuesta_id}/responder
```
**Body:**
```json
{
  "respuestas": [
    {
      "pregunta_id": "integer",
      "valor": "string"
    }
  ]
}
```
**Respuesta exitosa (201):** confirmación de respuesta registrada.

---

## Resumen de Dependencias entre Módulos

```
Autenticación
    └── Es usado por TODOS los módulos (validación de identidad)

Gestión de Eventos
    └── Es usado por: Inscripción, Certificados, Encuestas (evento_id)

Gestión de Roles
    └── Es usado por: Inscripción, Certificados, Encuestas (verificación de permisos)

Inscripción
    └── Es usado por: Certificados (verifica estado del participante)
```
