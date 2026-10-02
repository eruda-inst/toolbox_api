from typing import Annotated

from fastapi import Query

PageQueryParameter = Annotated[
    int, Query(ge=1, description="Current page.", examples=[1])
]
LimitQueryParameter = Annotated[
    int, Query(ge=1, description="Total items per page.", examples=[10])
]
