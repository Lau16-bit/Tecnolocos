# Spec — Acreditación de Participantes

## 1. Objetivo y Contexto

Permitir registrar la asistencia real de los participantes a un evento académico mediante un proceso de acreditación.

Este módulo es utilizado por los organizadores durante el evento y es condición necesaria para la emisión de certificados.

---

## 2. Historias de Usuario y Criterios de Aceptación

### HU1: Acreditar participante

Como organizador, quiero acreditar a los participantes para registrar su asistencia al evento.

Criterios de aceptación:
- El usuario debe estar autenticado
- Debe tener rol `organizador` o `admin`
- El participante debe estar inscripto al evento
- No debe existir una acreditación previa
- Se registra la fecha y hora automáticamente

---

### HU2: Ver participantes acreditados

Como organizador, quiero ver la lista de participantes acreditados para controlar la asistencia.

Criterios de aceptación:
- Se debe poder filtrar por evento
- Debe mostrar nombre, email y fecha de acreditación
- Solo accesible para organizadores o admin

---

## 3. Requisitos Funcionales y Reglas de Negocio

### Requisitos Funcionales

- RF1: Registrar acreditación de participante
- RF2: Listar participantes acreditados por evento
- RF3: Validar que el participante esté inscripto
- RF4: Evitar acreditaciones duplicadas

### Reglas de Negocio

- RN1: Solo organizadores o admin pueden acreditar participantes
- RN2: Solo participantes inscriptos pueden ser acreditados
- RN3: Un participante solo puede acreditarse una vez por evento

---

## 4. Restricciones Técnicas

- Endpoint protegido con JWT
- Validación de roles en backend
- Operación optimizada para uso en tiempo real

---

## 5. Modelo de Datos

Tabla: accreditations

- id (UUID)
- event_id (UUID)
- user_id (UUID)
- accredited_at (timestamp)

---

## 6. Plan de Tareas

1. Crear modelo de acreditación en SQLAlchemy
2. Crear schema en Pydantic
3. Implementar endpoint POST /accreditations
4. Validar inscripción del usuario
5. Validar duplicados
6. Implementar endpoint GET /accreditations?event_id=
7. Crear tests

---

## 7. Estrategia de Verificación

- Test acreditación correcta
- Test intento de acreditación sin inscripción
- Test acreditación duplicada
- Test acceso sin permisos
