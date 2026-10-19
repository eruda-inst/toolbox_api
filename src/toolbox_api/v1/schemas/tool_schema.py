import datetime as dt
from zoneinfo import ZoneInfo

from pydantic import BaseModel, ConfigDict, Field, PositiveInt, field_serializer

from .. import config


class ToolInSchema(BaseModel):
    name: str = Field(description="Name of the tool.", examples=["Toolbox"])
    description: str | None = Field(
        default=None,
        description="Description of the tool.",
        examples=["This tool does stuff"],
    )
    is_active: bool | None = Field(
        default=True, description="Whether the tool is active.", examples=[True]
    )
    url: str | None = Field(
        default=None,
        description="URL of the tool.",
        examples=["http://localhost:3000/tool"],
    )
    category_id: PositiveInt | None = Field(
        default=None, description="ID of the category of the tool.", examples=[1]
    )


class ToolUpdateSchema(BaseModel):
    name: str | None = Field(
        default=None, description="Name of the tool.", examples=["Toolbox"]
    )
    description: str | None = Field(
        default=None,
        description="Description of the tool.",
        examples=["This tool does stuff"],
    )
    is_active: bool | None = Field(
        default=None, description="Whether the tool is active.", examples=[True]
    )
    url: str | None = Field(
        default=None,
        description="URL of the tool.",
        examples=["http://localhost:3000/tool"],
    )
    category_id: PositiveInt | None = Field(
        default=None, description="ID of the category of the tool.", examples=[1]
    )


class ToolOutSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: PositiveInt = Field(description="ID of the tool.", examples=[1])
    name: str = Field(description="Name of the tool.", examples=["Toolbox"])
    description: str | None = Field(
        default=None,
        description="Description of the tool.",
        examples=["This tool does stuff"],
    )
    is_active: bool | None = Field(
        default=True, description="Whether the tool is active.", examples=[True]
    )
    url: str | None = Field(
        default=None,
        description="URL of the tool.",
        examples=["http://localhost:3000/tool"],
    )
    category_id: PositiveInt | None = Field(
        default=None, description="ID of the category of the tool.", examples=[1]
    )
    category_name: str | None = Field(
        default=None,
        description="Name of the category of the tool.",
        examples=["My Category"],
    )
    created_at: dt.datetime = Field(
        description="Timestamp when the tool was created.",
        examples=["2024-01-15T10:30:00Z"],
    )
    updated_at: dt.datetime | None = Field(
        default=None,
        description="Timestamp when the tool was last updated.",
        examples=["2024-01-15T10:30:00Z"],
    )

    @field_serializer("created_at", "updated_at")
    def serialize_timestamps(self, value: dt.datetime | None) -> dt.datetime | None:
        if value is not None:
            return value.astimezone(tz=ZoneInfo(config.settings.timezone))
        return value
