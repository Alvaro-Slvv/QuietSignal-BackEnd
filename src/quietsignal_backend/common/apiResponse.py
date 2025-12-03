from typing import Any, Optional
from fastapi import status
from pydantic import BaseModel


class APIResponse(BaseModel):
    code: int
    message: str
    data: Optional[Any] = None

    @staticmethod
    def success(data: Any = None, message: str = "Success", code: int = status.HTTP_200_OK):
        return APIResponse(code=code, message=message, data=data)

    @staticmethod
    def error(message: str, code: int):
        return APIResponse(code=code, message=message, data=None)
