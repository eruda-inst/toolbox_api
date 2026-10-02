import datetime as dt
from zoneinfo import ZoneInfo

from pydantic import BaseModel, ConfigDict, Field, PositiveInt, field_serializer

from .. import config


class RoleInSchema(BaseModel):
    code: str = Field(description="Code of the role.", examples=["tool_resource_role"])
    title: str = Field(description="Title of the role.", examples=["Manager of users"])
    description: str | None = Field(
        default=None,
        description="Description of the role.",
        examples=["This role does stuff"],
    )
    is_active: bool | None = Field(
        default=True,
        description="Whether the role is active.",
        examples=[True],
    )


class RoleUpdateSchema(BaseModel):
    code: str | None = Field(
        default=None, description="Code of the role.", examples=["tool_resource_role"]
    )
    title: str | None = Field(
        default=None, description="Title of the role.", examples=["Manager of users"]
    )
    description: str | None = Field(
        default=None,
        description="Description of the role.",
        examples=["This role does stuff"],
    )
    is_active: bool | None = Field(
        default=None,
        description="Whether the role is active.",
        examples=[True],
    )


class RoleOutSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: PositiveInt = Field(description="ID of the role.", examples=[1])
    code: str = Field(description="Code of the role.", examples=["tool_resource_role"])
    title: str = Field(description="Title of the role.", examples=["Manager of users"])
    description: str | None = Field(
        default=None,
        description="Description of the role.",
        examples=["This role does stuff"],
    )
    is_active: bool | None = Field(
        default=True, description="Whether the role is active.", examples=[True]
    )
    created_at: dt.datetime = Field(
        description="Timestamp when the role was created.",
        examples=["2024-01-15T10:30:00Z"],
    )
    updated_at: dt.datetime | None = Field(
        default=None,
        description="Timestamp when the role was last updated.",
        examples=["2024-01-15T10:30:00Z"],
    )

    @field_serializer("created_at", "updated_at")
    def serialize_timestamps(self, value: dt.datetime | None) -> dt.datetime | None:
        if value is not None:
            return value.astimezone(tz=ZoneInfo(config.settings.timezone))
        return value
