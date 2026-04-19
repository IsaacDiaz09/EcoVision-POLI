from pydantic import BaseModel


class Prediction(BaseModel):
    class_name: str
    confidence: float
    x: float | None = None
    y: float | None = None
    width: float | None = None
    height: float | None = None


class ClassificationResponse(BaseModel):
    waste_type: str
    confidence: float
    recommendations: list[str]
    predictions: list[Prediction]
    history_id: str
