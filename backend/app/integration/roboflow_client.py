import base64
import httpx

from app.core.config import settings

_RECOMMENDATIONS: dict[str, list[str]] = {
    "plastic": [
        "Deposita en el contenedor amarillo.",
        "Retira tapas y etiquetas antes de reciclar.",
        "Aplana las botellas para ahorrar espacio.",
    ],
    "glass": [
        "Deposita en el contenedor verde.",
        "No mezcles con vidrio roto.",
        "Retira tapas metálicas.",
    ],
    "metal": [
        "Deposita en el contenedor amarillo.",
        "Aplana las latas para ahorrar espacio.",
    ],
    "paper": [
        "Deposita en el contenedor azul.",
        "Asegúrate de que esté seco y limpio.",
    ],
    "cardboard": [
        "Deposita en el contenedor azul.",
        "Desdóblalo para ocupar menos espacio.",
    ],
    "organic": [
        "Deposita en el contenedor marrón.",
        "Ideal para compostaje doméstico.",
    ],
    "hazardous": [
        "No lo mezcles con residuos ordinarios.",
        "Llévalo a un punto limpio autorizado.",
        "Consulta la normativa local de residuos peligrosos.",
    ],
    "default": [
        "Consulta el punto de reciclaje más cercano.",
        "Separa los residuos por tipo antes de desecharlos.",
    ],
}


def classify_image(image_bytes: bytes) -> dict:
    image_b64 = base64.b64encode(image_bytes).decode("utf-8")

    url = (
        f"https://detect.roboflow.com/{settings.roboflow_project}"
        f"/{settings.roboflow_version}"
        f"?api_key={settings.roboflow_api_key}"
    )

    response = httpx.post(
        url,
        content=image_b64,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=30.0,
    )
    response.raise_for_status()

    raw = response.json()
    predictions = raw.get("predictions", [])

    if not predictions:
        return {
            "waste_type": "unknown",
            "confidence": 0.0,
            "predictions": [],
            "recommendations": _RECOMMENDATIONS["default"],
        }

    top = max(predictions, key=lambda p: p.get("confidence", 0))
    waste_type = top.get("class", "unknown").lower()

    normalized = [
        {
            "class_name": p.get("class", ""),
            "confidence": float(p.get("confidence", 0)),
            "x": p.get("x"),
            "y": p.get("y"),
            "width": p.get("width"),
            "height": p.get("height"),
        }
        for p in predictions
    ]

    recommendations = _RECOMMENDATIONS.get(waste_type, _RECOMMENDATIONS["default"])

    return {
        "waste_type": waste_type,
        "confidence": float(top.get("confidence", 0)),
        "predictions": normalized,
        "recommendations": recommendations,
    }
