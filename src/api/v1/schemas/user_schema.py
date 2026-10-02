import datetime as dt
from zoneinfo import ZoneInfo

from argon2 import PasswordHasher
from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_serializer,
    field_validator,
)
from pydantic.types import PositiveInt

from .. import config

ph = PasswordHasher()


class UserInSchema(BaseModel):
    full_name: str = Field(description="Full name of the user.", examples=["John Doe"])
    email: EmailStr = Field(
        description="E-mail address of the user.", examples=["email@email.com"]
    )
    password: str = Field(
        description="Plain-text password associated with the e-mail address.",
        examples=["12345678"],
    )
    is_active: bool | None = Field(
        default=True,
        description="Whether the account of the user is active.",
        examples=[True],
    )

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        return ph.hash(password=value)


class UserOutSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: PositiveInt = Field(ge=1, description="ID of the user.", examples=[1])
    full_name: str = Field(description="Full name of the user.", examples=["John Doe"])
    email: EmailStr = Field(
        description="E-mail address of the user.", examples=["email@email.com"]
    )
    is_active: bool | None = Field(
        default=True,
        description="Whether the account of the user is active.",
        examples=[True],
    )
    created_at: dt.datetime = Field(
        description="Timestamp when the user was created.",
        examples=["YYYY-MM-DDTHH:mm:ssZ"],
    )
    updated_at: dt.datetime | None = Field(
        default=None,
        description="Timestamp when the user was last updated.",
        examples=["YYYY-MM-DDTHH:mm:ssZ"],
    )

    @field_serializer("created_at", "updated_at")
    def serialize_timestamps(self, value: dt.datetime | None) -> dt.datetime | None:
        if value is not None:
            return value.astimezone(tz=ZoneInfo(config.settings.timezone))
        return value


class UserUpdateSchema(BaseModel):
    full_name: str | None = Field(
        default=None, description="Full name of the user.", examples=["John Doe"]
    )
    email: EmailStr | None = Field(
        default=None,
        description="E-mail address of the user.",
        examples=["email@email.com"],
    )
    password: str | None = Field(
        default=None,
        description="Plain-text password associated with the e-mail address.",
        examples=["12345678"],
    )
    is_active: bool | None = Field(
        default=None,
        description="Whether the account of the user is active.",
        examples=[True],
    )

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str | None) -> str | None:
        if value is None:
            return value
        return ph.hash(password=value)
