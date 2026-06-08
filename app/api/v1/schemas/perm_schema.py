from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, PositiveInt


class PermOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: PositiveInt = Field(description="ID da permissão", ge=1, examples=[1])
    nome: str = Field(description="Nome da permissão", examples=["Lorem ipsum"])
    codigo: str = Field(description="Código da permissão", examples=["lorem:ipsum"])
    criado_em: datetime = Field(
        description="Data de criação da permissão",
        examples=["AAAA-MM-DD HH:MM:SS.ffffff"],
    )
