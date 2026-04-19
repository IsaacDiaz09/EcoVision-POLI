from app.integration import firebase_client, roboflow_client
from app.schemas.classification import ClassificationResponse, Prediction


def classify_and_save(
    user_id: str,
    image_bytes: bytes,
    location: str | None,
) -> ClassificationResponse:
    result = roboflow_client.classify_image(image_bytes)

    history_id = firebase_client.save_classification(
        user_id=user_id,
        waste_type=result["waste_type"],
        confidence=result["confidence"],
        predictions=result["predictions"],
        location=location,
    )

    predictions = [Prediction(**p) for p in result["predictions"]]

    return ClassificationResponse(
        waste_type=result["waste_type"],
        confidence=result["confidence"],
        recommendations=result["recommendations"],
        predictions=predictions,
        history_id=history_id,
    )
