# Contracts.md — Reglas de Colaboración SDD

Este archivo define los contratos que todos los integrantes del equipo y los agentes de IA deben respetar al trabajar en este repositorio. Su objetivo es garantizar consistencia, trazabilidad y calidad en un entorno de desarrollo colaborativo con asistencia de IA.

---

## 1. Reglas Generales para Agentes

- **Leer siempre** `Project.md` y la spec del módulo correspondiente antes de generar cualquier código.
- **No agregar dependencias** (librerías, paquetes) que no estén especificadas en la spec o en `Project.md` sin aprobación explícita de un integrante del equipo.
- **No modificar** archivos fuera del módulo asignado salvo que la spec lo indique explícitamente.
- **No generar** datos sensibles reales (contraseñas, tokens, DNIs) en seeds o tests; usar datos ficticios.
- Ante cualquier ambigüedad en la spec, **detener la ejecución** y reportar la duda antes de asumir un comportamiento.

## 2. Convenciones de Git

### Ramas
```
feature/<nombre-modulo>       # nueva funcionalidad
fix/<descripcion-corta>       # corrección de bug
chore/<descripcion-corta>     # tareas de mantenimiento
```

### Commits (formato obligatorio)
```
<tipo>(<módulo>): <descripción en infinitivo>

Ejemplos:
feat(events): agregar endpoint de creación de evento
fix(inscripcion): corregir validación de cupo máximo
test(events): agregar tests para filtrado por fecha
docs(specs): actualizar criterios de aceptación de gestión de eventos
```

Tipos válidos: `feat`, `fix`, `test`, `docs`, `refactor`, `chore`

### Pull Requests
- El título debe indicar el módulo y la funcionalidad: `[Eventos] Gestión de eventos - CRUD completo`
- La descripción debe referenciar la spec: `Implementa las tareas 1-3 de /specs/gestion_eventos.md`
- No se hace merge sin revisión de al menos un integrante del equipo

## 3. Contratos de API

- Todos los endpoints requieren autenticación JWT salvo que la spec indique explícitamente que son públicos.
- El formato de respuesta de error es siempre:
```json
{
  "detail": "Descripción del error"
}
```
- Las listas paginadas responden con:
```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "size": 20
}
```
- Las fechas siempre en formato ISO 8601 (UTC): `"2026-08-15T10:00:00Z"`

## 4. Contratos de Base de Datos

- Toda tabla debe tener los campos: `id` (UUID), `created_at`, `updated_at`.
- Los campos `created_at` y `updated_at` se gestionan automáticamente por el ORM; ningún agente los escribe manualmente.
- Las migraciones se generan con Alembic. Nunca modificar la base de datos directamente.
- Los nombres de tablas en `snake_case` y plural: `events`, `participants`, `inscriptions`.
- No usar `CASCADE DELETE` sin que esté explícitamente indicado en la spec del módulo.

## 5. Contratos de Testing

- Todo endpoint nuevo debe tener al menos un test de camino feliz y uno de camino de error.
- Los tests no deben depender de datos externos; usar fixtures o factories.
- La cobertura mínima esperada por módulo es del 70%.
- Los tests se ejecutan en una base de datos separada (variable `TEST_DATABASE_URL`).

## 6. Contratos de Seguridad

- Nunca loguear contraseñas, tokens ni datos personales sensibles.
- Los tokens JWT no se almacenan en la base de datos.
- Las contraseñas se hashean con bcrypt antes de persistir.
- Los endpoints de administración (`/admin/*`) requieren rol `admin` validado en el middleware.

## 7. Lo que está fuera de alcance (NO implementar sin autorización)

- Integración con pasarelas de pago
- Envío de emails (reservado para una fase posterior)
- Panel de administración con interfaz gráfica avanzada
- Autenticación con redes sociales (OAuth)
