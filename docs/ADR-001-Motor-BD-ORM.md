# ADR-001: Elección de Motor de Base de Datos y ORM

**Estado:** Aceptado  
**Fecha:** 2026-06-17  
**Decisores:** Safrán Lautaro Javier  
**Relacionado:** `Project.md`, `Contracts.md`

---

## Contexto

### ¿Qué problema se está resolviendo?
Se necesita definir el sistema de persistencia de datos para la plataforma de gestión de eventos académicos. Este debe soportar un modelo de datos complejo con relaciones entre eventos, usuarios, inscripciones y roles, así como consultas de listado con filtros y paginación.

### ¿Qué restricciones aplican?
- **Técnicas:** El equipo tiene experiencia previa con bases de datos SQL. Se requiere una herramienta que facilite la evolución del esquema (migraciones) y el mapeo objeto-relacional. El sistema debe ser escalable para soportar la concurrencia de múltiples usuarios.
- **Legales/Negocio:** Los datos de los usuarios (incluyendo emails y contraseñas hasheadas) deben almacenarse de manera segura.

### ¿Qué datos de proyecto sustentan la decisión?
En `Project.md` se establece el uso de PostgreSQL y SQLAlchemy. La estructura de las specs muestra que los modelos de datos tienen restricciones como `UNIQUE`, `FOREIGN KEY` y campos `UUID`.

---

## Decisión

Se decide utilizar **PostgreSQL 16** como motor de base de datos y **SQLAlchemy 2.x (con AsyncSession)** como ORM para el backend en Python.

**Alcance:**
- ✅ Definición de todos los modelos SQLAlchemy
- ✅ Creación de tablas mediante Alembic
- ✅ Acceso a datos para todos los módulos del sistema

**Lo que NO cubre:**
- ❌ Cache de datos (se abordará en ADR-002)
- ❌ Búsqueda full-text avanzada (fuera de alcance inicial)

---

## Alternativas Consideradas

### Opción A: MySQL + SQLAlchemy
| Pros | Contras |
|------|---------|
| Similar a PostgreSQL en funcionalidad | Menos soporte nativo para tipos como `UUID` y `TIMESTAMPTZ` |
| Ampliamente conocido por el equipo | Funciones de búsqueda avanzada inferiores |

### Opción B: MongoDB (NoSQL) + Motor
| Pros | Contras |
|------|---------|
| Alta flexibilidad en el esquema | No garantiza integridad referencial (FK) de forma nativa |
| Fácil escalabilidad horizontal | Consultas con múltiples filtros son menos eficientes |
| | Consistencia ACID más difícil de asegurar |

### Opción C: SQLite + SQLAlchemy
| Pros | Contras |
|------|---------|
| Ligero, sin servidor aparte | No apto para producción con alta concurrencia |
| Ideal para entornos de desarrollo | Carece de funciones robustas de manejo de fechas |
| | No soporta nativamente tipos como `UUID` |

---

## Consecuencias

### Beneficios esperados
- **Integridad:** Se aprovechan las restricciones de la BD para garantizar que no haya duplicados de email o inscripciones inconsistentes, siguiendo las reglas de negocio del sistema.
- **Rendimiento:** Optimización de consultas con `JOIN` para listar inscriptos y calcular cupos disponibles.
- **Mantenibilidad:** SQLAlchemy simplifica el cambio entre bases de datos en el futuro si fuera necesario.

### Costos o riesgos que se aceptan
- Mayor complejidad en la configuración y administración del servidor de BD en producción.
- Dependencia de una librería externa (Alembic) para manejar los cambios de esquema.

### Impacto en operación y equipo
- Todos los módulos deben usar SQLAlchemy.
- Los desarrolladores deben aprender el dialecto Async de SQLAlchemy para no bloquear el servidor.

---

## Plan de Implementación

1. Levantar el contenedor de PostgreSQL definido en `docker-compose.yml`
2. Configurar la variable `DATABASE_URL` en el entorno de desarrollo
3. Inicializar Alembic en el proyecto (`alembic init`)
4. Crear la primera migración a partir del modelo `User` (auth)
5. Agregar sucesivamente las migraciones para eventos, inscripciones, etc.

### Dependencias
- Docker y Docker Compose
- PostgreSQL 16
- Python 3.12+ con `psycopg2-binary`

### Métrica de éxito
La conexión a la BD se establece correctamente y las migraciones corren sin errores en el entorno de CI.

---

## Triggers de Revisión

### Condiciones que obligan a reabrir esta ADR
- Detección de cuellos de botella en las consultas de listado de eventos/participantes.
- Necesidad de integrar un motor de búsqueda más avanzado (ej: Elasticsearch).

### Fecha sugerida de revisión
2026-10-17 (tras la implementación de los módulos de reportes)