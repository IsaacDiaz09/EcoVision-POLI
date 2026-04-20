# EcoVision — Backend API

Backend de **EcoVision** desarrollado con **FastAPI**. Clasifica residuos mediante visión por computadora implementando una arquitectura SOA.

---

## Arquitectura

| Patrón | Implementación |
|--------|---------------|
| **Layered Architecture** | `api/` → `services/` → `integration/` |
| **API Gateway** | `FirebaseAuthMiddleware` centraliza la autenticación |
| **Service Facade** | `integration/` es el único punto de contacto con Firebase y Roboflow |
| **Client-Server** | Lógica de negocio y credenciales exclusivamente en el servidor |

```
Cliente
   │
   ▼
FirebaseAuthMiddleware  ← valida token en cada request
ExceptionMiddleware     ← manejo centralizado de errores
   │
   ├── api/v1/          ← Presentación
   ├── services/        ← Negocio
   └── integration/     ← Integración (Firebase + Roboflow)
```

## Tecnologías

- **[FastAPI](https://fastapi.tiangolo.com)** + Uvicorn — REST API con OpenAPI/Swagger
- **[Firebase Admin SDK](https://firebase.google.com/docs/admin/setup)** — Auth y Firestore
- **[Roboflow](https://docs.roboflow.com)** — clasificación de imágenes por IA
- **Google ADC** — autenticación con Google Cloud sin credenciales explícitas
- **[secure](https://github.com/TypeError/secure)** — cabeceras de seguridad HTTP
- **Pydantic v2** — validación de datos y schemas

## Estructura

```
backend/
├── app/
│   ├── main.py
│   ├── core/
│   │   ├── config.py              # Variables de entorno (pydantic-settings)
│   │   └── firebase.py            # Inicialización Firebase con ADC
│   ├── middleware/
│   │   ├── auth_middleware.py     # Verificación de token Firebase
│   │   └── exception_middleware.py
│   ├── api/v1/
│   │   ├── router.py
│   │   ├── users.py
│   │   ├── classification.py
│   │   └── history.py
│   ├── services/
│   │   ├── user_service.py
│   │   ├── classification_service.py
│   │   └── history_service.py
│   ├── integration/
│   │   ├── firebase_client.py     # Auth + Firestore
│   │   └── roboflow_client.py
│   └── schemas/
│       ├── common.py              # ApiResponse, ApiErrorResponse
│       ├── user.py
│       ├── classification.py
│       └── history.py
├── app.yaml.example
├── .env.example
├── .gcloudignore
└── requirements.txt
```

## Endpoints

**Autenticación:** `Authorization: Bearer <firebase_id_token>` en todos los endpoints excepto `POST /api/v1/users`.

**Respuesta exitosa:** `{ "data": { ... } }`  
**Respuesta de error:** `{ "message": "...", "error_code": "..." }`

| Método | Ruta | Auth | Descripción |
|--------|------|:----:|-------------|
| `POST` | `/api/v1/users` | No | Registro de usuario en Firebase Auth |
| `GET` | `/api/v1/users` | Sí | Lista todos los usuarios |
| `GET` | `/api/v1/users/{uid}` | Sí | Perfil de un usuario |
| `POST` | `/api/v1/classification` | Sí | Clasifica imagen y guarda en Firestore |
| `GET` | `/api/v1/history/{id_user}` | Sí | Historial de clasificaciones |

### POST /api/v1/classification

Recibe `multipart/form-data`:

| Campo | Tipo | Requerido |
|-------|------|:---------:|
| `file` | imagen (jpg/png/webp) | ✓ |
| `location` | string | — |

```json
{
  "data": {
    "waste_type": "metal",
    "confidence": 0.977,
    "recommendations": ["Deposita en el contenedor amarillo.", "Aplana las latas para ahorrar espacio."]
  }
}
```

### GET /api/v1/history/{id_user}

```json
{
  "data": {
    "user_id": "abc123",
    "total": 1,
    "entries": [
      { "id": "He5tGYrOXHcF0wZkDP9X", "waste_type": "metal", "confidence": 0.977, "location": "Bogotá", "timestamp": "2026-04-19T23:53:30+00:00" }
    ]
  }
}
```

## Requisitos previos

- Python 3.11+
- Proyecto Firebase con **Authentication** y **Firestore** habilitados
- Índice compuesto en Firestore: colección `classifications`, campos `user_id` (ASC) y `timestamp` (DESC)
- Cuenta en [Roboflow](https://roboflow.com) con un modelo de clasificación de residuos
- [Google Cloud CLI](https://cloud.google.com/sdk/docs/install)

## Configuración

```bash
cp .env.example .env
# Editar .env con los valores reales
```

```env
FIREBASE_PROJECT_ID=tu-firebase-project-id
ROBOFLOW_API_KEY=tu_api_key
ROBOFLOW_PROJECT=nombre-del-proyecto
ROBOFLOW_VERSION=1
```

**ADC (desarrollo local):**
```bash
gcloud auth application-default login --project=tu-firebase-project-id
```

En producción las credenciales se resuelven automáticamente desde el Service Account del host.

## Ejecución local

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # completar con credenciales
gcloud auth application-default login --project=tu-firebase-project-id
uvicorn app.main:app --reload
```

Swagger UI: **http://localhost:8000/docs**

## Despliegue en App Engine

```bash
cp app.yaml.example app.yaml
# Editar app.yaml con ROBOFLOW_API_KEY y ROBOFLOW_PROJECT

gcloud app deploy --project=ecovision-poli
gcloud app browse --project=ecovision-poli
```

URL: `https://ecovision-poli.uc.r.appspot.com`
