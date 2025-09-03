from typing import Any, Optional
from typing import Generic, TypeVar

from fastapi import status
from pydantic import BaseModel
from starlette.responses import JSONResponse

T = TypeVar("T")


class GeneralResponse(BaseModel, Generic[T]):
    code: int
    message: str
    data: T | None = None


def success_response(data: Optional[Any] = None, message: str = "Success", code: int = status.HTTP_200_OK):
    return GeneralResponse(code=code, message=message, data=data )


def error_response(message: str = "An error occurred", data: Optional[Any] = [],
        code: int = status.HTTP_500_INTERNAL_SERVER_ERROR):
    # raise HTTPException(
    #     status_code=code,
    #     detail=BaseResponse(code=code, message=message, data=data).model_dump()
    # )
    return JSONResponse(content=GeneralResponse(code=code, message=message, data=data).model_dump(), status_code=code)
