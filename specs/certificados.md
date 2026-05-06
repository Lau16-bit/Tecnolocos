# Spec — Generación de Certificados

## 1. Objetivo y Contexto

Permitir la generación y descarga de certificados para participantes y disertantes de eventos académicos.

Los certificados validan la participación en el evento y dependen de la acreditación previa del usuario.

---

## 2. Historias de Usuario y Criterios de Aceptación

### HU1: Descargar certificado

Como participante, quiero descargar mi certificado para poder validar mi asistencia al evento.

Criterios de aceptación:
- El usuario debe estar autenticado
- Debe estar acreditado en el evento
- El certificado debe generarse en formato PDF
- Debe incluir nombre del participante, nombre del evento y fecha

---

### HU2: Generar certificados

Como organizador, quiero generar certificados para los participantes acreditados.

Criterios de aceptación:
- Solo usuarios con rol `organizador` o `admin` pueden generar certificados
- Solo se generan certificados para participantes acreditados
- Se debe poder especificar el tipo de certificado

---

## 3. Requisitos Funcionales y Reglas de Negocio

### Requisitos Funcionales

- RF1: Generar certificado en formato PDF
- RF2: Permitir descarga del certificado
- RF3: Validar acreditación del usuario
- RF4: Permitir distintos tipos de certificados (asistencia, participación, expositor)

### Reglas de Negocio

- RN1: Solo usuarios acreditados pueden obtener certificados
- RN2: Un usuario solo puede tener un certificado por evento y tipo
- RN3: El certificado debe contener datos válidos del evento y del usuario

---

## 4. Restricciones Técnicas

- La generación del certificado se realiza en el backend
- Los endpoints deben estar protegidos con JWT
- No se deben almacenar archivos PDF en la base de datos
- El certificado se genera dinámicamente al momento de la solicitud

---

## 5. Modelo de Datos

Tabla: certificates

- id (UUID)
- user_id (UUID)
- event_id (UUID)
- type (string)
- issued_at (timestamp)

---

## 6. Plan de Tareas

1. Crear modelo de certificado en SQLAlchemy
2. Crear schema en Pydantic
3. Implementar lógica de generación de PDF
4. Crear endpoint GET /certificates/{id}
5. Validar acreditación del usuario
6. Implementar tests

---

## 7. Estrategia de Verificación

- Test generación de certificado para usuario acreditado
- Test intento de generación sin acreditación
- Test descarga del certificado
- Test validación de contenido del certificado
