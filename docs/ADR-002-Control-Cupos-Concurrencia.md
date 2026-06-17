# ADR-002: Control de Concurrencia para Inscripciones con Cupo

**Estado:** Propuesto  
**Fecha:** 2026-06-17  
**Decisores:** Safrán Lautaro Javier  
**Relacionado:** `specs/inscripcion_participantes.md`, `Contracts.md`

---

## Contexto

### ¿Qué problema se está resolviendo?
Se ha identificado una potencial **condición de carrera** en el módulo de inscripciones. Para un evento con alta demanda (ej: congreso), múltiples participantes podrían intentar inscribirse simultáneamente cuando solo queda 1 lugar disponible.

Si la verificación de cupo disponible y la creación de la inscripción no se manejan de forma atómica, podría resultar en **sobre-inscripción** (más participantes que el cupo máximo), violando la **RN-03** del sistema.

Además, la consulta constante de `cupo_maximo` vs `COUNT(*)` en la tabla `inscriptions` para cada solicitud puede generar alta carga en la base de datos.

### ¿Qué restricciones aplican?
- **Técnicas:** El sistema debe ser capaz de manejar picos de tráfico (ej: apertura de inscripciones). La solución no debe introducir un punto único de falla. La consistencia de datos es prioritaria.
- **Negocio:** El evento define un cupo máximo. La experiencia del usuario debe ser fluida, sin largos tiempos de espera.

### ¿Qué datos de proyecto sustentan la decisión?
La spec de `inscripcion_participantes.md` menciona específicamente el cálculo de cupo en **CA-22** y **RN-07**, y en el **Plan de Tareas** se indica que la validación de duplicados debe implementarse a nivel de servicio. Esto implica que la lógica de cupo está en el código, no en la BD, haciéndola susceptible a condiciones de carrera si no se sincroniza.

---

## Decisión

Se decide implementar un **Lock Optimista a nivel de Base de Datos** usando `SELECT ... FOR UPDATE` para manejar el conteo de cupos de manera atómica.

**Alcance:**
- ✅ Este mecanismo se aplicará específicamente en el servicio de inscripciones (`inscription_service.py`).
- ✅ Se usará para inscripciones autónomas y manuales.

**Lo que NO cubre:**
- ❌ No se implementará cache distribuido (Redis) en esta fase.
- ❌ No se cambiará el modelo de datos ni la estructura de la tabla `inscriptions`.

---

## Alternativas Consideradas

### Opción A: Redis con operaciones atómicas (DECR/INCR)

| Pros | Contras |
|------|---------|
| Extremadamente rápido (< 1ms por operación) | Introduce un nuevo componente en la infraestructura |
| Elimina la carga de la BD | Requiere sincronización inicial y manejo de caídas |
| Escalable horizontalmente | Aumenta la complejidad del sistema |

### Opción B: Optimistic Locking con campo `version`

| Pros | Contras |
|------|---------|
| No requiere infraestructura extra | Aumenta latencia por reintentos en alta concurrencia |
| Es una solución nativa de SQLAlchemy | En picos de demanda, los conflictos disparan el tiempo de respuesta |

### Opción C: Función/Trigger en la base de datos

| Pros | Contras |
|------|---------|
| La lógica se ejecuta cerca de los datos | Acopla la lógica de negocio al motor de BD |
| Garantiza consistencia | Hace el código menos portable y difícil de testear |
| | No se alinea con la arquitectura de servicios definida |

---

## Consecuencias

### Beneficios esperados
- **Consistencia de datos:** Al ser una operación atómica a nivel de transacción, se elimina la condición de carrera. El participante solo obtiene el lugar si la transacción se completa exitosamente.
- **Simplicidad:** No se agregan nuevas dependencias ni infraestructura. Se usa lo que ya está disponible en PostgreSQL.
- **Control total:** El desarrollador tiene control explícito sobre el momento del bloqueo y la liberación.

### Costos o riesgos que se aceptan
- **Bloqueo de filas:** Durante la transacción, la fila del evento queda bloqueada. Si la transacción es lenta (ej: por validaciones externas), puede generar cuellos de botella.
- **Deadlocks potenciales:** En escenarios complejos, podría haber deadlocks si no se ordenan correctamente las operaciones.

### Impacto en operación y equipo
- El servicio `inscription_service.py` debe usar una sesión de SQLAlchemy con `with_for_update()`.
- Se debe garantizar que las transacciones sean cortas (solo la verificación + creación de inscripción).
- Se deben agregar logs para monitorear la duración de las transacciones bloqueantes.

---

## Plan de Implementación

1. Modificar `inscription_service.py` para obtener el evento con `with_for_update()`.
2. Calcular el cupo disponible contando las inscripciones activas (`pendiente` o `confirmada`).
3. Si hay cupo, crear la inscripción dentro de la misma transacción.
4. Si no hay cupo, hacer rollback y lanzar excepción (HTTP 400).
5. Asegurar que todas las validaciones se realicen ANTES de bloquear la fila.

### Dependencias
- SQLAlchemy 2.x
- PostgreSQL 16 (soporta `SELECT ... FOR UPDATE`)

### Métrica de éxito
- Cero sobre-inscripciones en pruebas de carga con 100 usuarios concurrentes.
- Tiempo de respuesta del endpoint `POST /inscriptions` < 500ms en escenarios de alta concurrencia.

---

## Triggers de Revisión

### Condiciones que obligan a reabrir esta ADR
- Detección de que las transacciones bloqueantes están degradando el rendimiento general.
- Crecimiento del sistema que requiere escalabilidad horizontal y Redis se vuelve necesario.

### Fecha sugerida de revisión
2026-08-17 (durante la fase de pruebas de carga antes del lanzamiento)