# ADR-003: Autenticación y Autorización con JWT

**Estado:** Aceptado  
**Fecha:** 2026-06-17  
**Decisores:** [Tu nombre y apellido]  
**Relacionado:** `Project.md`, `Contracts.md` (sección 3 y 6)

---

## Contexto

### ¿Qué problema se está resolviendo?
El sistema requiere un mecanismo de autenticación que permita a los usuarios iniciar sesión y acceder a recursos protegidos según su rol (`organizador`, `participante`, `disertante`, `admin`). Además, debe mantener la sesión activa durante un tiempo determinado sin necesidad de que el usuario se autentique en cada solicitud.

El sistema debe cumplir con:
- Autenticación stateless (sin almacenar sesiones en el servidor)
- Soporte para roles y permisos diferenciados
- Renovación de sesión sin pedir credenciales nuevamente

### ¿Qué restricciones aplican?
- **Técnicas:** El backend está desarrollado en FastAPI (Python). Se requiere que el mecanismo sea compatible con el ecosistema actual y no genere sobrecarga en la base de datos.
- **Seguridad:** Las contraseñas deben almacenarse de forma segura (hasheadas). Los tokens no deben ser vulnerables a ataques de intercepción (MITM) ni de falsificación (CSRF).
- **Negocio:** El sistema maneja datos sensibles de usuarios, por lo que la seguridad es prioritaria.

### ¿Qué datos de proyecto sustentan la decisión?
En `Project.md` se establece:
> **Autenticación:** JWT (access token 1h / refresh token 7d)

En `Contracts.md` se define:
> Todos los endpoints requieren autenticación JWT salvo que la spec indique explícitamente que son públicos.
> Los tokens JWT no se almacenan en la base de datos.
> Las contraseñas se hashean con bcrypt antes de persistir.

---

## Decisión

Se implementa un sistema de autenticación basado en **JWT (JSON Web Tokens)** con la siguiente configuración:

| Componente | Configuración |
|------------|---------------|
| **Access Token** | Expiración: 1 hora. Se envía en el header `Authorization: Bearer <token>` |
| **Refresh Token** | Expiración: 7 días. Se almacena en cookie HTTP-only (segura) |
| **Algoritmo de firma** | HS256 (simétrico) |
| **Hashing de contraseñas** | bcrypt (costo 12) |
| **Endpoint de login** | `POST /auth/login` → devuelve access + refresh token |
| **Endpoint de refresh** | `POST /auth/refresh` → renueva access token |

**Alcance:**
- ✅ Autenticación de usuarios con email + contraseña
- ✅ Generación y validación de access tokens
- ✅ Renovación de access tokens mediante refresh token
- ✅ Validación de roles en endpoints protegidos (`admin`, `organizador`, etc.)
- ✅ Logout (el cliente descarta el token localmente)

**Lo que NO cubre:**
- ❌ Autenticación con OAuth2 (Google, GitHub) → fuera de alcance inicial
- ❌ Autenticación biométrica o 2FA → no requerido en esta fase

---

## Alternativas Consideradas

### Opción A: Sesiones con cookies (almacenamiento en servidor)

| Pros | Contras |
|------|---------|
| Mecanismo tradicional y ampliamente conocido | Requiere almacenamiento en servidor (memoria/BD) |
| Fácil de invalidar (borrar la sesión) | Escala mal en sistemas distribuidos |
| Seguro si se usa con cookies HTTP-only y Secure | Aumenta la carga en la base de datos por cada solicitud |

### Opción B: JWT (seleccionada)

| Pros | Contras |
|------|---------|
| Stateless: no requiere almacenamiento en servidor | Una vez emitido, no se puede invalidar fácilmente (hasta que expire) |
| Escalable horizontalmente sin compartir estado | Tamaño del token mayor que una cookie de sesión |
| Contiene claims (roles, usuario) que evitan consultas extra a la BD | Requiere gestión de refresh tokens para no pedir login cada hora |
| Compatible con arquitectura de microservicios | |

### Opción C: OAuth2 con terceros (Google, GitHub)

| Pros | Contras |
|------|---------|
| Delega la seguridad en proveedores externos | El sistema debe depender de un servicio externo |
| Usuarios no necesitan crear nueva cuenta | Requiere configuración adicional (client ID, secret) |
| Menos contraseñas para almacenar | Curva de aprendizaje más compleja |
| | No todos los usuarios tienen cuenta en estos servicios |

---

## Consecuencias

### Beneficios esperados
- **Escalabilidad:** Al ser stateless, cualquier instancia del backend puede validar tokens sin compartir información de sesión.
- **Seguridad:** Las contraseñas se hashean con bcrypt (costo 12), haciendo inviable un ataque de fuerza bruta.
- **Experiencia de usuario:** El refresh token permite sesiones largas (7 días) sin pedir credenciales cada hora.
- **Simplicidad:** FastAPI tiene soporte nativo para JWT a través de `python-jose` y `passlib`.
- **Roles integrados:** Los claims del token incluyen el rol del usuario, evitando consultas adicionales a la BD para autorización.

### Costos o riesgos que se aceptan
- **Invalidación de tokens:** Si un token se ve comprometido, no se puede revocar hasta su expiración (1 hora). Como mitigación, se usarán access tokens de corta duración (1h).
- **Almacenamiento seguro de refresh tokens:** Si bien no se almacenan en BD, deben transmitirse de forma segura (cookie HTTP-only, Secure, SameSite=Strict).
- **Complejidad de renovación:** El cliente debe implementar lógica para detectar expiración de access token y renovarlo automáticamente.

### Impacto en operación y equipo
- Todos los endpoints (salvo login y registros) deben incluir el middleware de validación de JWT.
- Los tests deben incluir casos de autenticación válida e inválida.
- El frontend debe almacenar el access token en memoria (y opcionalmente en localStorage con precauciones) y refrescarlo automáticamente.

---

## Plan de Implementación

1. Instalar dependencias en el backend:
pip install python-jose[cryptography] passlib[bcrypt] python-multipart

text

2. Crear módulo `app/core/security.py` con funciones:
- `hash_password(password)` → hashea con bcrypt
- `verify_password(plain, hashed)` → verifica contraseña
- `create_access_token(data, expires_delta)` → genera access token (1h)
- `create_refresh_token(data)` → genera refresh token (7d)
- `decode_token(token)` → decodifica y valida firma

3. Crear endpoint `POST /auth/login`:
- Recibe email + password
- Busca usuario en BD y verifica contraseña
- Genera access + refresh token
- Devuelve access token en body y refresh token en cookie HTTP-only

4. Crear endpoint `POST /auth/refresh`:
- Lee refresh token de la cookie
- Valida el token y genera un nuevo access token
- Devuelve nuevo access token en body

5. Agregar dependencia `get_current_user` en FastAPI para proteger endpoints:
@app.get("/events")
def get_events(current_user = Depends(get_current_user)):
...

text

6. Agregar validación de roles con `get_current_user_with_roles(["admin"])`

### Dependencias
- `python-jose[cryptography]` → para JWT
- `passlib[bcrypt]` → para hashing de contraseñas
- `python-multipart` → para formularios (login)

### Métrica de éxito
- El login y refresh funcionan correctamente en entorno local.
- Los endpoints protegidos retornan 401 si no se envía token válido.
- Los endpoints con roles retornan 403 si el usuario no tiene el rol requerido.
- La autenticación es probada en al menos 5 tests de integración.

---

## Triggers de Revisión

### Condiciones que obligan a reabrir esta ADR
- Detección de vulnerabilidad en el algoritmo de firma (HS256) que requiera migración a RS256 (asimétrico).
- Necesidad de integrar OAuth2 con proveedores externos (Google, GitHub) para autenticación social.
- Cambio en los requisitos de seguridad que requiera 2FA o autenticación biométrica.

### Fecha sugerida de revisión
2026-12-17 (previo a la puesta en producción)
