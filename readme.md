# Proyecto Docs

SaaS para **gestión, procesamiento y análisis de documentos** con una arquitectura moderna basada en **FastAPI, Angular y PostgreSQL**.

El sistema permitirá:

- gestión multiempresa (multi-tenant)
- autenticación segura con JWT
- almacenamiento y procesamiento de documentos
- extracción de datos
- gestión de trabajos y estados
- registro de auditoría

---

# Arquitectura

El proyecto sigue una arquitectura **full-stack separada**:

```
proyecto-docs
│
├── backend        → API (FastAPI)
├── frontend       → Aplicación web (Angular)
└── database       → PostgreSQL
```

### Tecnologías principales

| Capa | Tecnología |
|-----|-------------|
Backend | FastAPI |
Frontend | Angular |
Base de datos | PostgreSQL |
ORM | SQLAlchemy |
Migraciones | Alembic |
Autenticación | JWT |
Gestión dependencias | pip / npm |

---

# Estructura del proyecto

```
backend
│
├── alembic                → migraciones de base de datos
│
├── app
│   ├── api                → endpoints de la API
│   │   └── v1
│   │       └── endpoints
│   │
│   ├── core               → configuración y seguridad
│   │
│   ├── db                 → base SQLAlchemy
│   │
│   ├── models             → modelos de base de datos
│   │
│   ├── schemas            → modelos Pydantic
│   │
│   ├── repositories       → acceso a datos
│   │
│   ├── services           → lógica de negocio
│   │
│   └── main.py            → entrada de FastAPI
│
└── requirements.txt
```

---

# Instalación

## 1. Clonar repositorio

```bash
git clone https://github.com/roldaan04/proyecto-docs.git
cd proyecto-docs
```

---

# Backend

## Crear entorno virtual

```bash
cd backend
python -m venv venv
```

Activar entorno virtual:

Windows

```bash
venv\Scripts\activate
```

Linux / Mac

```bash
source venv/bin/activate
```

---

## Instalar dependencias

```bash
pip install -r requirements.txt
```

---

## Variables de entorno

Crear archivo `.env` en la carpeta `backend`.

Ejemplo:

```
DATABASE_URL=postgresql://usuario:password@localhost:5432/saas_web
SECRET_KEY=supersecretkey
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

---

# Base de datos

El proyecto utiliza **PostgreSQL**.

Aplicar migraciones:

```bash
alembic upgrade head
```

Comprobar migración actual:

```bash
alembic current
```

---

# Ejecutar backend

```bash
uvicorn app.main:app --reload
```

API disponible en:

```
http://127.0.0.1:8000
```

Documentación automática (Swagger):

```
http://127.0.0.1:8000/docs
```

---

# Frontend

## Instalar dependencias

```bash
cd frontend
npm install
```

---

## Ejecutar Angular

```bash
ng serve
```

Aplicación disponible en:

```
http://localhost:4200
```

---

# Endpoints principales

| Endpoint | Descripción |
|--------|-------------|
POST /auth/register | registro de usuario |
POST /auth/login | login |
GET /auth/me | usuario autenticado |

---

# Flujo básico de autenticación

1️⃣ Registrar empresa y usuario

```
POST /auth/register
```

2️⃣ Obtener token JWT

```
POST /auth/login
```

3️⃣ Usar token en la API

```
Authorization: Bearer TOKEN
```

---

# Estado del proyecto

MVP inicial en desarrollo.

Funcionalidades actuales:

- autenticación JWT
- arquitectura multi-tenant
- modelos base de datos
- migraciones con Alembic
- estructura de servicios

Próximas funcionalidades:

- subida de documentos
- procesamiento de datos
- gestión de trabajos
- panel de administración
- sistema de auditoría

---

# Licencia

Proyecto privado.