from typing import Any
from pydantic import BaseModel


class ApiResponse(BaseModel):
    data: Any

    @classmethod
    def ok(cls, data: Any) -> "ApiResponse":
        return cls(data=data)


class ApiErrorResponse(BaseModel):
    message: str
    error_code: str | None = None

    @classmethod
    def error(cls, message: str, error_code: str | None = None) -> "ApiErrorResponse":
        return cls(message=message, error_code=error_code)
