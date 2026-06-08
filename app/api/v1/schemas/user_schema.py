from datetime import datetime
from passlib.context import CryptContext
from pydantic import BaseModel, Field, PositiveInt, EmailStr, ConfigDict, SecretStr

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class LoginCreds(BaseModel):
    email: EmailStr = Field(
        description="E-mail do usuário", examples=["exemplo@exemplo.com"]
    )
    senha: SecretStr = Field(
        min_length=8, description="Senha do usuário", examples=["12345678"]
    )

    def verify_senha(self, plain_senha: str, hashed_senha: str) -> bool:
        return pwd_context.verify(secret=plain_senha, hash=hashed_senha)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: PositiveInt = Field(description="ID do usuário", ge=1, examples=[1])
    nome: str = Field(
        description="Nome completo do usuário", examples=["Nome Completo"]
    )
    email: EmailStr = Field(
        description="E-mail do usuário", examples=["exemplo@exemplo.com"]
    )
    ativo: bool = Field(description="Status do usuário", examples=[True])
    criado_em: datetime = Field(
        description="Data de criação do usuário",
        examples=["AAAA-MM-DD HH:MM:SS.ffffff"],
    )
    atualizado_em: datetime | None = Field(
        description="Data de atualização do usuário",
        examples=["AAAA-MM-DD HH:MM:SS.ffffff"],
    )
    id_grupo: PositiveInt = Field(
        description="ID do grupo do usuário", ge=1, examples=[1]
    )
