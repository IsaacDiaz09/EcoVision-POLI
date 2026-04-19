from app.integration import firebase_client
from app.schemas.history import HistoryResponse


def get_user_history(user_id: str) -> HistoryResponse:
    entries = firebase_client.get_history_by_user(user_id)
    return HistoryResponse(
        user_id=user_id,
        total=len(entries),
        entries=entries,
    )
