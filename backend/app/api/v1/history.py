from fastapi import APIRouter

from app.schemas.common import ApiResponse
from app.services import history_service

router = APIRouter(prefix="/history", tags=["Historial de Clasificaciones"])


@router.get(
    "/{id_user}",
    summary="Historial de clasificaciones",
    description="Retorna el historial cronológico de clasificaciones realizadas por un usuario.",
)
def get_history(id_user: str):
    history = history_service.get_user_history(id_user)
    return ApiResponse.ok(history.model_dump())
