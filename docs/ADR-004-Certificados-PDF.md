# ADR-004 Generación de certificados en PDF

Estado: Aceptado

Fecha: 2026-06-17

Decisores: Matías Rivas

Relacionado: Issue ADR-004

## Contexto

El sistema debe emitir certificados para participantes, disertantes y organizadores de eventos académicos. Se necesita una solución que permita generar documentos PDF de forma automática y mantener un formato uniforme.

## Decisión

Se utilizará generación automática de certificados en formato PDF desde el backend mediante plantillas predefinidas.

## Alternativas consideradas

### Certificados manuales

Pros:

* Implementación sencilla.

Contras:

* Requiere trabajo manual.

### Generación automática PDF (seleccionada)

Pros:

* Automatización completa.
* Formato uniforme.

Contras:

* Mayor complejidad de implementación.

### Servicios externos

Pros:

* Menor desarrollo propio.

Contras:

* Dependencia de terceros.

## Consecuencias

Beneficios:

* Reducción del trabajo administrativo.
* Menor cantidad de errores.

Riesgos:

* Necesidad de mantener las plantillas.

## Plan de implementación

1. Crear plantilla de certificado.
2. Generar PDF desde el backend.
3. Asociar certificados a participantes.
4. Permitir descarga desde el sistema.

## Triggers de revisión

* Nuevos formatos de certificados.
* Firma digital obligatoria.
* Cambios en requisitos institucionales.
