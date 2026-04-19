from app.integration import firebase_client
from app.schemas.user import UserCreateRequest, UserResponse


def register_user(payload: UserCreateRequest) -> UserResponse:
    return firebase_client.create_user(
        email=payload.email,
        password=payload.password,
        display_name=payload.display_name,
    )


def get_user(uid: str) -> UserResponse:
    return firebase_client.get_user_by_id(uid)


def list_all_users() -> list[UserResponse]:
    return firebase_client.list_users()
