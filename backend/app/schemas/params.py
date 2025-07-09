from fastapi import Query
from pydantic import BaseModel
from typing import List, TypeVar, Generic

T = TypeVar('T')


class Params(BaseModel):
    page: int = Query(1, ge=1, description="Page number")
    size: int = Query(10, ge=1, le=100, description="Page size")


class Page(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    size: int
    pages: int 