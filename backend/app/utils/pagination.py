"""Simple pagination utility."""
from __future__ import annotations

from typing import Generic, TypeVar
from pydantic import BaseModel

T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int

    @property
    def has_next(self) -> bool:
        return (self.page * self.page_size) < self.total

    @property
    def total_pages(self) -> int:
        if self.page_size == 0:
            return 0
        import math
        return math.ceil(self.total / self.page_size)
