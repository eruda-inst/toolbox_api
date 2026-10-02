import datetime as dt
from zoneinfo import ZoneInfo

from pydantic import BaseModel, ConfigDict, Field, PositiveInt, field_serializer

from .. import config


class CategoryInSchema(BaseModel):
    name: str = Field(description="Name of the category.", examples=["My Category"])
    is_active: bool | None = Field(
        default=True,
        description="Whether the category is active.",
        examples=[True],
    )


class CategoryUpdateSchema(BaseModel):
    name: str | None = Field(
        default=None, description="Name of the category.", examples=["My Category"]
    )
    is_active: bool | None = Field(
        default=None, description="Whether the category is active.", examples=[True]
    )


class CategoryOutSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: PositiveInt = Field(description="ID of the category.", examples=[1])
    name: str = Field(description="Name of the category.", examples=["My Category"])
    is_active: bool | None = Field(
        default=True,
        description="Whether the category is active.",
        examples=[True],
    )
    created_at: dt.datetime = Field(
        description="Timestamp when the category was created.",
        examples=["YYYY-MM-DDTHH:mm:ssZ"],
    )
    updated_at: dt.datetime | None = Field(
        default=None,
        description="Timestamp when the category was last updated.",
        examples=["YYYY-MM-DDTHH:mm:ssZ"],
    )

    @field_serializer("created_at", "updated_at")
    def serialize_timestamps(self, value: dt.datetime | None) -> dt.datetime | None:
        if value is not None:
            return value.astimezone(tz=ZoneInfo(config.settings.timezone))
        return value
