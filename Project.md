# Project.md — Tecnolocos

## 1. Descripción General del Proyecto

**Nombre del proyecto:** EventoAcadémico  
**Tipo:** Aplicación web para la organización y gestión de eventos académicos  
**Contexto:** Plataforma que permite a grupos de personas organizar eventos de tipo académico (cursos, jornadas, congresos, charlas, etc.) y gestionar la participación de asistentes, disertantes y organizadores.

---

## 2. Integrantes del Equipo

| Nombre | Usuario GitHub | Módulos asignados |
|--------|---------------|-------------------|
| Safrán Lautaro Javier | Lau16-bit | Gestión de Eventos, Inscripción de Participantes |
| Aquino Lucas Orlando | (usuario GitHub) | Registro y Autenticación de Usuarios, Gestión de Roles |
| Rivas Matías | (usuario GitHub) | Generación de Certificados, Encuestas post-evento |

---

## 3. Stack Tecnológico

### Backend
- **Lenguaje:** Python 3.11+
- **Framework:** FastAPI
- **ORM:** SQLAlchemy
- **Autenticación:** JWT (JSON Web Tokens) con `python-jose`
- **Validación:** Pydantic v2

### Base de Datos
- **Motor:** PostgreSQL 15
- **Migraciones:** Alembic

### Frontend
- **Framework:** Next.js 14 (React)
- **Estilos:** Tailwind CSS
- **Cliente HTTP:** Axios

### Infraestructura
- **Contenedores:** Docker + Docker Compose (para desarrollo local)
- **Variables de entorno:** `.env` (nunca subir al repo)

---

## 4. Arquitectura General

```
┌─────────────────────────────────────┐
│           FRONTEND (Next.js)        │
│         Puerto: 3000                │
└────────────────┬────────────────────┘
                 │ HTTP/REST (JSON)
                 ▼
┌─────────────────────────────────────┐
│           BACKEND (FastAPI)         │
│         Puerto: 8000                │
│  /api/v1/auth                       │
│  /api/v1/eventos                    │
│  /api/v1/inscripciones              │
│  /api/v1/roles                      │
│  /api/v1/certificados               │
│  /api/v1/encuestas                  │
└────────────────┬────────────────────┘
                 │ SQLAlchemy ORM
                 ▼
┌─────────────────────────────────────┐
│         BASE DE DATOS               │
│         PostgreSQL                  │
│         Puerto: 5432                │
└─────────────────────────────────────┘
```

---

## 5. Estructura del Repositorio

```
/
├── README.md
├── Project.md
├── Contracts.md
├── docker-compose.yml
│
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py
│   ├── alembic/
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── auth.py
│   │   │       ├── eventos.py
│   │   │       ├── inscripciones.py
│   │   │       ├── roles.py
│   │   │       ├── certificados.py
│   │   │       └── encuestas.py
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── core/
│   │       ├── config.py
│   │       └── security.py
│
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   ├── next.config.js
│   └── src/
│       ├── app/
│       ├── components/
│       └── lib/
│
└── specs/
    ├── spec-01-gestion-eventos.md
    ├── spec-02-autenticacion.md
    ├── spec-03-inscripcion-participantes.md
    ├── spec-04-gestion-roles.md
    ├── spec-05-certificados.md
    └── spec-06-encuestas.md
```

---

## 6. Convenciones Generales

### Commits
- Usar mensajes descriptivos en español o inglés
- Formato: `tipo: descripción corta`
- Tipos: `feat`, `fix`, `docs`, `refactor`, `test`
- Ejemplo: `feat: agregar endpoint de inscripción a eventos`

### Ramas
- `main` → rama principal, siempre estable
- `dev` → rama de desarrollo
- `feature/nombre-feature` → una rama por feature

### API REST
- Todas las rutas bajo `/api/v1/`
- Respuestas en JSON
- Códigos HTTP estándar: 200, 201, 400, 401, 403, 404, 422, 500
- Autenticación mediante header: `Authorization: Bearer <token>`

### Variables de entorno (`.env`)
```
DATABASE_URL=postgresql://user:password@db:5432/eventoacademico
SECRET_KEY=clave_secreta_jwt
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

---

## 7. Instrucciones para Levantar el Proyecto en Local

```bash
# 1. Clonar el repositorio
git clone https://github.com/Lau16-bit/Tecnolocos.git
cd Tecnolocos

# 2. Copiar variables de entorno
cp .env.example .env

# 3. Levantar los contenedores
docker-compose up --build

# 4. Acceder a la aplicación
# Frontend: http://localhost:3000
# Backend (docs): http://localhost:8000/docs
```

---

## 8. Lineamientos para las Specs

Cada spec del directorio `/specs/` debe seguir la estructura definida en el TP:

1. Objetivo y Contexto
2. Historias de Usuario y Criterios de Aceptación
3. Requisitos Funcionales y Reglas de Negocio
4. Restricciones Técnicas específicas del módulo
5. Modelo de Datos del módulo
6. Plan de Tareas
7. Estrategia de Verificación

