from typing import TypeVar

from pydantic import BaseModel, Field, NonNegativeInt, PositiveInt, computed_field

T = TypeVar("T")


class MetaOutSchema(BaseModel):
    page: PositiveInt = Field(ge=1, description="Current page.", examples=[1])
    limit: PositiveInt = Field(ge=1, description="Total items per page.", examples=[10])
    item_count: NonNegativeInt = Field(ge=0, description="Total items.", examples=[100])

    @computed_field(description="Total pages.", examples=[10])
    @property
    def page_count(self) -> int:
        if self.item_count == 0:
            return 0
        return (self.item_count + self.limit - 1) // self.limit


class ListOutSchema[T](BaseModel):
    data: list[T]
    meta: MetaOutSchema
