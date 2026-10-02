import datetime as dt

from pydantic import BaseModel, Field, NonNegativeInt


class TokenOutSchema(BaseModel):
    expires_in: NonNegativeInt | None = Field(
        default=3600, description="Expiration time in seconds.", examples=[3600]
    )
    expires_at: dt.datetime = Field(
        description="Expected expiration token date.", examples=["2024-01-15T10:30:00Z"]
    )
    token_type: str | None = Field(
        default="Bearer", description="Token type.", examples=["Bearer"]
    )
    access_token: str = Field(description="Token used to access.", examples=["eyJ..."])
    refresh_token: str = Field(
        description="Token used to refresh.", examples=["eyJ..."]
    )
