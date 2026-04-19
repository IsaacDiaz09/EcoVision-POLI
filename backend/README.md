# EcoVision — Backend API

Servicio backend de la aplicación **EcoVision**, desarrollado con **FastAPI** (Python 3). Implementa una arquitectura orientada a servicios (SOA) para la clasificación inteligente de residuos mediante visión por computadora.

---

## Tabla de contenidos

- [Arquitectura](#arquitectura)
- [Tecnologías](#tecnologías)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Endpoints](#endpoints)
- [Requisitos previos](#requisitos-previos)
- [Configuración](#configuración)
- [Ejecución local](#ejecución-local)
- [Despliegue en Google Cloud](#despliegue-en-google-cloud)

---

## Arquitectura

El servicio implementa los siguientes patrones SOA:

| Patrón | Implementación |
|--------|---------------|
| **Layered Architecture** | `api/` → `services/` → `integration/` — cada capa solo conoce la inmediatamente inferior |
| **API Gateway** | `FirebaseAuthMiddleware` centraliza la autenticación en todos los endpoints |
| **Service Facade** | `integration/` es el único módulo que conoce los contratos externos (Firebase y Roboflow) |
| **Client-Server** | La lógica de negocio y las credenciales residen exclusivamente en el servidor |

```
Cliente (Angular / móvil)
        │
        ▼
┌─────────────────────────────┐
│     FirebaseAuthMiddleware  │  ← API Gateway: valida token en cada request
│     ExceptionMiddleware     │  ← Manejo centralizado de excepciones
├─────────────────────────────┤
│        api/v1/              │  ← Capa de Presentación
├─────────────────────────────┤
│        services/            │  ← Capa de Negocio
├─────────────────────────────┤
│       integration/          │  ← Capa de Integración (Service Facade)
│   firebase_client.py        │      Firebase Auth + Firestore
│   roboflow_client.py        │      API de clasificación de imágenes
└─────────────────────────────┘
```

---

## Tecnologías

- **[FastAPI](https://fastapi.tiangolo.com)** — framework REST con generación automática de OpenAPI/Swagger
- **[Firebase Admin SDK](https://firebase.google.com/docs/admin/setup)** — autenticación (Auth) y base de datos (Firestore)
- **[Roboflow](https://docs.roboflow.com)** — API de visión por computadora para clasificación de residuos
- **Google Application Default Credentials (ADC)** — autenticación con Google Cloud sin credenciales explícitas
- **Pydantic v2** — validación de datos y schemas de request/response
- **Uvicorn** — servidor ASGI de alto rendimiento

---

## Estructura del proyecto

```
backend/
├── app/
│   ├── main.py                        # Punto de entrada: app FastAPI, middlewares y routers
│   ├── core/
│   │   ├── config.py                  # Variables de entorno con pydantic-settings
│   │   └── firebase.py                # Inicialización de Firebase con ADC
│   ├── middleware/
│   │   ├── auth_middleware.py         # Interceptor: verifica token Firebase (todos los endpoints)
│   │   └── exception_middleware.py   # Interceptor: manejo global de excepciones → JSON uniforme
│   ├── api/
│   │   └── v1/
│   │       ├── router.py              # Agrega los routers con prefijo /api/v1
│   │       ├── users.py               # Endpoints de usuarios
│   │       ├── classification.py      # Endpoint de clasificación de residuos
│   │       └── history.py             # Endpoint de historial
│   ├── services/                      # Capa de Negocio
│   │   ├── user_service.py
│   │   ├── classification_service.py
│   │   └── history_service.py
│   ├── integration/                   # Capa de Integración (Service Facade)
│   │   ├── firebase_client.py         # Auth + Firestore
│   │   └── roboflow_client.py         # API de clasificación
│   └── schemas/                       # Modelos Pydantic
│       ├── common.py                  # Envelope ApiResponse uniforme
│       ├── user.py
│       ├── classification.py
│       └── history.py
├── .env.example                       # Plantilla de variables de entorno
├── requirements.txt
└── README.md
```

---

## Endpoints

> Todos los endpoints retornan JSON con el siguiente envelope:
> ```json
> { "success": true, "data": { ... }, "message": "OK" }
> ```

| Método | Ruta | Auth | Descripción |
|--------|------|:----:|-------------|
| `POST` | `/api/v1/users` | — | Registra un nuevo usuario en Firebase Auth |
| `GET` | `/api/v1/users` | ✓ | Lista todos los usuarios registrados |
| `GET` | `/api/v1/users/{uid}` | ✓ | Retorna el perfil de un usuario por UID |
| `POST` | `/api/v1/classification` | ✓ | Clasifica un residuo y guarda el resultado en Firestore |
| `GET` | `/api/v1/history/{id_user}` | ✓ | Retorna el historial cronológico de clasificaciones |

**Autenticación:** header `Authorization: Bearer <firebase_id_token>` (excepto `POST /api/v1/users`).

**`POST /api/v1/classification`** recibe `multipart/form-data`:
| Campo | Tipo | Requerido | Descripción |
|-------|------|:---------:|-------------|
| `file` | imagen (jpg/png/webp) | ✓ | Foto del residuo |
| `location` | string | — | Ubicación opcional del contenedor |

**Documentación interactiva:** `http://localhost:8000/docs`

---

## Requisitos previos

- Python 3.11+
- Proyecto en [Firebase](https://console.firebase.google.com) con **Authentication** y **Firestore** habilitados
- Cuenta en [Roboflow](https://roboflow.com) con un modelo de detección de residuos
- [Google Cloud CLI](https://cloud.google.com/sdk/docs/install) (para desarrollo local con ADC)

---

## Configuración

### 1. Variables de entorno

```bash
cp .env.example .env
```

Edita `.env` con tus valores:

```env
FIREBASE_PROJECT_ID=tu-firebase-project-id

ROBOFLOW_API_KEY=tu_api_key
ROBOFLOW_PROJECT=nombre-del-proyecto
ROBOFLOW_VERSION=1
```

### 2. Application Default Credentials (ADC)

El servicio usa **Google ADC** para autenticarse con Firebase sin archivos de credenciales.

**Desarrollo local:**
```bash
gcloud auth application-default login --project=tu-firebase-project-id
```

**Producción (Google Cloud):** las credenciales se resuelven automáticamente desde el Service Account del host. No se requiere configuración adicional.

---

## Ejecución local

```bash
# 1. Crear y activar entorno virtual
python -m venv .venv
source .venv/bin/activate        # macOS/Linux
# .venv\Scripts\activate         # Windows

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar variables de entorno
cp .env.example .env
# editar .env con tus credenciales

# 4. Autenticar con Google Cloud (ADC)
gcloud auth application-default login --project=tu-firebase-project-id

# 5. Levantar el servidor
uvicorn app.main:app --reload
```

Swagger UI disponible en: **http://localhost:8000/docs**

---

## Despliegue en Google Cloud

### Cloud Run

```bash
# Desde la raíz del proyecto backend
gcloud run deploy ecovision-api \
  --source . \
  --project=tu-firebase-project-id \
  --region=us-central1 \
  --allow-unauthenticated \
  --set-env-vars FIREBASE_PROJECT_ID=tu-firebase-project-id,ROBOFLOW_API_KEY=...,ROBOFLOW_PROJECT=...,ROBOFLOW_VERSION=1
```

El Service Account de Cloud Run hereda automáticamente los permisos de Firebase y Firestore asignados al proyecto — no se requiere `serviceAccountKey.json`.
