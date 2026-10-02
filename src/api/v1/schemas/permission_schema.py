import datetime as dt
from zoneinfo import ZoneInfo

from pydantic import BaseModel, ConfigDict, Field, PositiveInt, field_serializer

from .. import config


class PermissionInSchema(BaseModel):
    code: str = Field(
        description="Code of the permission.", examples=["tool:resource:action"]
    )
    description: str | None = Field(
        default=None,
        description="Description of the permission.",
        examples=["This permission does stuff."],
    )
    is_active: bool | None = Field(
        default=True,
        description="Whether the permission is active.",
        examples=[True],
    )


class PermissionUpdateSchema(BaseModel):
    code: str | None = Field(
        default=None,
        description="Code of the permission.",
        examples=["tool:resource:action"],
    )
    description: str | None = Field(
        default=None,
        description="Description of the permission.",
        examples=["This permission does stuff."],
    )
    is_active: bool | None = Field(
        default=None,
        description="Whether the permission is active.",
        examples=[True],
    )


class PermissionOutSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: PositiveInt = Field(ge=1, description="ID of the permission.", examples=[1])
    code: str = Field(
        description="Code of the permission.", examples=["tool:resource:action"]
    )
    description: str | None = Field(
        default=None,
        description="Description of the permission.",
        examples=["tool:resource:action"],
    )
    is_active: bool | None = Field(
        default=True,
        description="Whether the permission is active.",
        examples=[True],
    )
    created_at: dt.datetime = Field(
        description="Timestamp when the permission was created.",
        examples=["YYYY-MM-DDTHH:mm:ssZ"],
    )
    updated_at: dt.datetime | None = Field(
        default=None,
        description="Timestamp when the permission was last updated.",
        examples=["YYYY-MM-DDTHH:mm:ssZ"],
    )

    @field_serializer("created_at", "updated_at")
    def serialize_timestamps(self, value: dt.datetime | None) -> dt.datetime | None:
        if value is not None:
            return value.astimezone(tz=ZoneInfo(config.settings.timezone))
        return value
