from pydantic import BaseModel, ConfigDict
from typing import Any, Generic, TypeVar

T = TypeVar("T")


def to_camel(s: str) -> str:
    """Convert snake_case to camelCase for Pydantic alias generator."""
    parts = s.split("_")
    return parts[0] + "".join(p.capitalize() for p in parts[1:])


class CommonBase(BaseModel):
    """Base model with camelCase alias generation for all schemas."""
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )


class Result(BaseModel, Generic[T]):
    """Standard API response wrapper matching the Java backend's Result<T>."""
    code: int = 200
    msg: str = "success"
    data: T | None = None

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

    @classmethod
    def success(cls, data: T = None, msg: str = "success") -> "Result[T]":
        return cls(code=200, msg=msg, data=data)

    @classmethod
    def error(cls, msg: str = "error", code: int = 500) -> "Result[T]":
        return cls(code=code, msg=msg, data=None)


class PageResult(BaseModel):
    """Paginated response matching the original Java Page<T> structure."""
    records: list = []
    total: int = 0
    size: int = 20
    current: int = 1
    pages: int = 0

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )
