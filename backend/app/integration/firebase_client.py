from datetime import datetime, timezone

from firebase_admin import auth, firestore as fb_firestore
from google.cloud.firestore_v1.base_query import FieldFilter

from app.schemas.user import UserResponse
from app.schemas.history import HistoryEntry

_COLLECTION = "classifications"


# ── Auth ──────────────────────────────────────────────────────────────────────

def create_user(email: str, password: str, display_name: str | None) -> UserResponse:
    user = auth.create_user(
        email=email,
        password=password,
        display_name=display_name,
    )
    return _to_user_response(user)


def get_user_by_id(uid: str) -> UserResponse:
    user = auth.get_user(uid)
    return _to_user_response(user)


def list_users() -> list[UserResponse]:
    page = auth.list_users()
    result: list[UserResponse] = []
    while page:
        for user in page.users:
            result.append(_to_user_response(user))
        page = page.get_next_page()
    return result


def verify_token(id_token: str) -> dict:
    return auth.verify_id_token(id_token)


# ── Firestore ─────────────────────────────────────────────────────────────────

def save_classification(
    user_id: str,
    waste_type: str,
    confidence: float,
    predictions: list[dict],
    location: str | None,
) -> str:
    db = fb_firestore.client()
    doc_ref = db.collection(_COLLECTION).document()
    doc_ref.set({
        "user_id": user_id,
        "waste_type": waste_type,
        "confidence": confidence,
        "predictions": predictions,
        "location": location,
        "timestamp": datetime.now(timezone.utc),
    })
    return doc_ref.id


def get_history_by_user(user_id: str) -> list[HistoryEntry]:
    db = fb_firestore.client()
    docs = (
        db.collection(_COLLECTION)
        .where(filter=FieldFilter("user_id", "==", user_id))
        .order_by("timestamp", direction=fb_firestore.Query.DESCENDING)
        .stream()
    )
    return [_to_history_entry(doc) for doc in docs]


# ── Helpers ───────────────────────────────────────────────────────────────────

def _to_user_response(user: auth.UserRecord) -> UserResponse:
    created = None
    if user.user_metadata and user.user_metadata.creation_timestamp:
        created = datetime.fromtimestamp(
            user.user_metadata.creation_timestamp / 1000, tz=timezone.utc
        ).isoformat()
    return UserResponse(
        uid=user.uid,
        email=user.email or "",
        display_name=user.display_name,
        email_verified=user.email_verified,
        disabled=user.disabled,
        created_at=created,
    )


def _to_history_entry(doc) -> HistoryEntry:
    data = doc.to_dict()
    ts = data.get("timestamp")
    timestamp_str = ts.isoformat() if hasattr(ts, "isoformat") else str(ts)
    return HistoryEntry(
        id=doc.id,
        user_id=data.get("user_id", ""),
        waste_type=data.get("waste_type", ""),
        confidence=float(data.get("confidence", 0.0)),
        location=data.get("location"),
        timestamp=timestamp_str,
    )
