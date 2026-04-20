from pydantic import BaseModel


class HistoryEntry(BaseModel):
    id: str
    waste_type: str
    confidence: float
    location: str | None
    timestamp: str


class HistoryResponse(BaseModel):
    user_id: str
    total: int
    entries: list[HistoryEntry]
