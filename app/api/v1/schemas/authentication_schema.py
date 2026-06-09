from .. import cores
from pydantic import BaseModel, Field, NonNegativeInt

TOKEN_EXPIRE_SECONDS = cores.settings.token_expire_seconds


class AccessTokenOut(BaseModel):
    access_token: str = Field(description="Token de acesso", examples=["$2b$12$..."])
    refresh_token: str = Field(
        description="Token de atualização", examples=["$2b$12$..."]
    )
    token_type: str | None = Field(
        default="Bearer", description="Tipo de token", examples=["Bearer"]
    )
    expires_in: NonNegativeInt | None = Field(
        default=TOKEN_EXPIRE_SECONDS,
        description="Tempo de expiração (em segundos)",
        examples=[TOKEN_EXPIRE_SECONDS],
    )


class RefreshTokenReq(BaseModel):
    refresh_token: str = Field(description="Token de atualização atual do usuário")
