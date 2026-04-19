import logging
import traceback

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from firebase_admin import auth
from firebase_admin.exceptions import FirebaseError
import httpx

logger = logging.getLogger(__name__)


class ExceptionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except auth.UserNotFoundError:
            return self._json_error(404, "Usuario no encontrado.", "USER_NOT_FOUND")
        except auth.EmailAlreadyExistsError:
            return self._json_error(409, "El correo electrónico ya está registrado.", "EMAIL_EXISTS")
        except FirebaseError as exc:
            logger.error("Firebase error: %s", exc)
            return self._json_error(502, f"Error de Firebase: {exc.code}", "FIREBASE_ERROR")
        except httpx.HTTPStatusError as exc:
            logger.error("Roboflow HTTP error: %s", exc)
            return self._json_error(
                502,
                f"Error al comunicarse con Roboflow: {exc.response.status_code}",
                "ROBOFLOW_HTTP_ERROR",
            )
        except httpx.RequestError as exc:
            logger.error("Roboflow connection error: %s", exc)
            return self._json_error(503, "No se pudo conectar con Roboflow.", "ROBOFLOW_CONNECTION_ERROR")
        except Exception as exc:
            logger.error("Unhandled exception:\n%s", traceback.format_exc())
            return self._json_error(500, "Error interno del servidor.", "INTERNAL_SERVER_ERROR")

    @staticmethod
    def _json_error(status: int, message: str, error_code: str) -> JSONResponse:
        from app.schemas.common import ApiErrorResponse
        return JSONResponse(
            status_code=status,
            content=ApiErrorResponse.error(message, error_code).model_dump(),
        )
