from fastapi import APIRouter, File, Form, Request, UploadFile

from app.schemas.common import ApiResponse
from app.services import classification_service

router = APIRouter(prefix="/classification", tags=["Clasificación de Residuos"])


@router.post(
    "",
    summary="Clasificación de residuo",
    description=(
        "Recibe una imagen del residuo en formato `multipart/form-data`, "
        "la clasifica mediante la API de Roboflow y guarda el resultado en el historial del usuario. "
        "Retorna la categoría detectada, nivel de confianza y recomendaciones de reciclaje."
    ),
)
async def classify(
    request: Request,
    file: UploadFile = File(..., description="Imagen del residuo (jpg, png, webp)"),
    location: str | None = Form(default=None, description="Ubicación opcional del contenedor"),
):
    image_bytes = await file.read()
    uid: str = request.state.uid
    result = classification_service.classify_and_save(uid, image_bytes, location)
    return ApiResponse.ok(result.model_dump())
