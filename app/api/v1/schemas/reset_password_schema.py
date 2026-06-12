from pydantic import BaseModel, EmailStr, Field, SecretStr


class RequestOtpIn(BaseModel):
    email: EmailStr = Field(
        description="E-mail do usuário que solicita redefinição",
        examples=["exemplo@exemplo.com"],
    )


class VerifyOtpIn(BaseModel):
    email: EmailStr = Field(
        description="E-mail do usuário", examples=["exemplo@exemplo.com"]
    )
    otp: str = Field(
        description="Código OTP de 4 dígitos",
        min_length=4,
        max_length=4,
        examples=["9999"],
    )


class VerifyOtpOut(BaseModel):
    reset_token: str = Field(
        description="Token temporário para redefinir a senha", examples=["$2b$12$..."]
    )


class ResetPasswordIn(BaseModel):
    reset_token: str = Field(
        description="Token obtido na verificação do OTP", examples=["$2b$12$..."]
    )
    nova_senha: SecretStr = Field(
        description="Nova senha", min_length=8, examples=["12345678"]
    )
