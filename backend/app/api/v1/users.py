from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.schemas.user import UserCreateRequest
from app.schemas.common import ApiResponse
from app.services import user_service

router = APIRouter(prefix="/users", tags=["Usuarios"])


@router.post(
    "",
    summary="Registro de usuario",
    description="Crea una nueva cuenta de usuario con correo y contraseña en Firebase Auth.",
    status_code=201,
)
def register_user(payload: UserCreateRequest):
    user = user_service.register_user(payload)
    return JSONResponse(
        status_code=201,
        content=ApiResponse.ok(user.model_dump()).model_dump(),
    )


@router.get(
    "",
    summary="Listado de usuarios",
    description="Retorna todos los usuarios registrados en Firebase Auth. Requiere autenticación.",
)
def list_users():
    users = user_service.list_all_users()
    return ApiResponse.ok([u.model_dump() for u in users])


@router.get(
    "/{uid}",
    summary="Consulta de usuario",
    description="Retorna el perfil de un usuario autenticado por su UID de Firebase.",
)
def get_user(uid: str):
    user = user_service.get_user(uid)
    return ApiResponse.ok(user.model_dump())
