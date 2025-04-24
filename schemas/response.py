from typing import TypeVar, Generic

from pydantic import BaseModel

from schemas.errors import ErrorResponse

DataType = TypeVar("DataType")
T = TypeVar("T")


class ResponseBase(BaseModel, Generic[T]):
    status_code: int
    data: T | None = None
    errors: list[ErrorResponse] | None = []
    request_id: str
