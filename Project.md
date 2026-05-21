# Project.md — Gestión de Eventos Académicos

## 1. Descripción General

Aplicación web para que grupos de personas puedan organizar y gestionar eventos de tipo académico (cursos, jornadas, congresos, charlas, etc.). Permite la inscripción de participantes, gestión de roles, acreditación, emisión de certificados y generación de informes.

## 2. Stack Tecnológico

| Capa | Tecnología |
|---|---|
| Backend | Python 3.12 + FastAPI |
| ORM | SQLAlchemy 2.x |
| Base de datos | PostgreSQL 16 |
| Migraciones | Alembic |
| Frontend | Next.js 14 (App Router) + TypeScript |
| Estilos | Tailwind CSS |
| Autenticación | JWT (access token 1h / refresh token 7d) |
| Contenedores | Docker + Docker Compose |
| Testing backend | Pytest |
| Testing frontend | Jest + React Testing Library |

## 3. Estructura del Repositorio

```
/
├── backend/
│   ├── app/
│   │   ├── models/         # Modelos SQLAlchemy
│   │   ├── schemas/        # Schemas Pydantic
│   │   ├── routers/        # Endpoints FastAPI
│   │   ├── services/       # Lógica de negocio
│   │   └── core/           # Config, seguridad, DB
│   ├── tests/
│   └── alembic/
├── frontend/
│   ├── app/                # App Router de Next.js
│   ├── components/
│   └── lib/
├── specs/                  # Specs de cada módulo
├── Project.md
├── Contracts.md
└── docker-compose.yml
```

## 4. Convenciones de Código

### Backend
- Nombres de archivos y variables: `snake_case`
- Clases: `PascalCase`
- Endpoints REST: sustantivos en plural (`/events`, `/participants`)
- Respuestas HTTP estándar: 200, 201, 400, 401, 403, 404, 422, 500
- Toda la lógica de negocio va en `services/`, nunca directamente en los routers

### Frontend
- Componentes: `PascalCase`
- Variables y funciones: `camelCase`
- Archivos de componentes: `PascalCase.tsx`
- Páginas (App Router): `page.tsx` dentro de la carpeta correspondiente

## 5. Variables de Entorno

Deben definirse en un archivo `.env` en la raíz (nunca commitearlo). Se provee `.env.example` como referencia:

```
DATABASE_URL=postgresql://user:password@localhost:5432/eventos_db
SECRET_KEY=changeme
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 6. Flujo de Desarrollo

1. Leer la spec del módulo en `/specs/`
2. Crear la rama: `feature/<nombre-del-modulo>`
3. Implementar siguiendo el Plan de Tareas de la spec
4. Ejecutar tests antes de hacer PR
5. El PR debe referenciar la spec correspondiente en la descripción

## 7. Roles del Sistema

| Rol | Descripción |
|---|---|
| `organizador` | Crea y administra eventos, inscribe participantes manualmente |
| `participante` | Se inscribe a eventos, recibe certificados |
| `disertante` | Participa como expositor, puede tener certificado de autor |
| `admin` | Acceso total al sistema |
