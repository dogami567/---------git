from math import ceil
from typing import List, TypeVar
from backend.app.schemas.params import Page, Params

T = TypeVar("T")


def paginate(items: List[T], params: Params) -> Page[T]:
    """
    对项目列表进行分页
    """
    start = (params.page - 1) * params.size
    end = start + params.size
    total = len(items)
    
    paginated_items = items[start:end]
    
    return Page(
        items=paginated_items,
        total=total,
        page=params.page,
        size=params.size,
        pages=ceil(total / params.size) if total > 0 else 1
    ) 