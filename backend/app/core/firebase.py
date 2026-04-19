import firebase_admin

from app.core.config import settings


def initialize_firebase() -> None:
    if firebase_admin._apps:
        return
    firebase_admin.initialize_app(options={"projectId": settings.firebase_project_id})
