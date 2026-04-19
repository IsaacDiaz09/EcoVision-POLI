from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from firebase_admin import auth

from app.schemas.common import ApiErrorResponse

_PUBLIC_PATHS = {"/api/v1/users": ["POST"], "/docs": None, "/openapi.json": None, "/redoc": None}


class FirebaseAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if self._is_public(request):
            return await call_next(request)

        authorization = request.headers.get("Authorization", "")
        if not authorization.startswith("Bearer "):
            return JSONResponse(
                status_code=401,
                content=ApiErrorResponse.error("Token de autenticación no proporcionado.", "MISSING_TOKEN").model_dump(),
            )

        token = authorization.removeprefix("Bearer ").strip()
        try:
            decoded = auth.verify_id_token(token)
            request.state.uid = decoded["uid"]
            request.state.token_claims = decoded
        except auth.ExpiredIdTokenError:
            return JSONResponse(
                status_code=401,
                content=ApiErrorResponse.error("El token de autenticación ha expirado.", "TOKEN_EXPIRED").model_dump(),
            )
        except auth.InvalidIdTokenError:
            return JSONResponse(
                status_code=401,
                content=ApiErrorResponse.error("Token de autenticación inválido.", "INVALID_TOKEN").model_dump(),
            )

        return await call_next(request)

    def _is_public(self, request: Request) -> bool:
        path = request.url.path
        allowed_methods = _PUBLIC_PATHS.get(path)
        if allowed_methods is None and path in _PUBLIC_PATHS:
            return True
        if allowed_methods is not None and request.method in allowed_methods:
            return True
        for public_path in _PUBLIC_PATHS:
            if path.startswith(public_path) and _PUBLIC_PATHS[public_path] is None:
                return True
        return False
