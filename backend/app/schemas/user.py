from pydantic import BaseModel, EmailStr


class UserCreateRequest(BaseModel):
    email: EmailStr
    password: str
    display_name: str | None = None


class UserResponse(BaseModel):
    uid: str
    email: str
    display_name: str | None
    email_verified: bool
    disabled: bool
    created_at: str | None = None
