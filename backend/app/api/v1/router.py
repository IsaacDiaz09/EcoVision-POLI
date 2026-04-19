from fastapi import APIRouter

from app.api.v1 import users, classification, history

router = APIRouter(prefix="/api/v1")

router.include_router(users.router)
router.include_router(classification.router)
router.include_router(history.router)
