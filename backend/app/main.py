import logging
from typing import Any

import secure
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from app.core.firebase import initialize_firebase
from app.middleware.exception_middleware import ExceptionMiddleware
from app.middleware.auth_middleware import FirebaseAuthMiddleware
from app.api.v1.router import router

logging.basicConfig(level=logging.INFO)

initialize_firebase()

app = FastAPI(
    title="EcoVision API",
    description=(
        "Backend SOA para la clasificación inteligente de residuos.\n\n"
        "**Patrones implementados:** Layered Architecture · API Gateway · Client-Server · Service Facade.\n\n"
        "**Autenticación:** Bearer token de Firebase (excepto `POST /api/v1/users`).\n\n"
        "**Integración externa:** Roboflow (visión por computadora).\n\n"
        "**Persistencia:** Firebase Firestore (historial de clasificaciones)."
    ),
    version="1.0.0",
    contact={"name": "EcoVision Team", "email": "idiazppe@poligran.edu.co"},
    license_info={"name": "MIT"},
)


def custom_openapi() -> dict[str, Any]:
    if app.openapi_schema:
        return app.openapi_schema

    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        contact=app.contact,
        license_info=app.license_info,
        routes=app.routes,
    )

    schema.setdefault("components", {})
    schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "Firebase JWT",
            "description": "ID token obtenido desde Firebase Authentication.",
        }
    }
    schema["security"] = [{"BearerAuth": []}]

    app.openapi_schema = schema
    return schema


app.openapi = custom_openapi

# ── Secure headers ────────────────────────────────────────────────────────────
_secure_headers = secure.Secure(
    hsts=secure.StrictTransportSecurity(),
    xfo=secure.XFrameOptions(),
    xcto=secure.XContentTypeOptions(),
    referrer=secure.ReferrerPolicy(),
    csp=secure.ContentSecurityPolicy(),
    permissions=secure.PermissionsPolicy(),
    server=secure.Server(),
)


@app.middleware("http")
async def set_secure_headers(request: Request, call_next):
    response = await call_next(request)
    _secure_headers.set_headers(response)
    return response


# ── Middlewares (se ejecutan en orden inverso al de registro) ─────────────────
# 1. CORS (más externo)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# 2. Manejo centralizado de excepciones
app.add_middleware(ExceptionMiddleware)
# 3. Autenticación Firebase (API Gateway)
app.add_middleware(FirebaseAuthMiddleware)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(router)


@app.get("/", include_in_schema=False)
def health_check():
    return {"status": "ok", "service": "EcoVision API", "version": "1.0.0"}
