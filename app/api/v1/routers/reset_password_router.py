from typing import Annotated
from .. import db, schemas, services
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

reset_password_router = APIRouter(prefix="/redefinir-senha", tags=["Redefinir Senha"])

db_dep = Annotated[AsyncSession, Depends(db.get_db)]


@reset_password_router.post(
    path="/solicitar-otp",
    summary="Solicitar código OTP",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def request_otp(db: db_dep, req: schemas.RequestOtpIn):
    """
    Envia um código OTP para o e-mail do usuário, se ele estiver cadastrado e ativo
    """
    await services.ResetPasswordService.request_otp(db=db, req=req)


@reset_password_router.post(path="/verificar-otp", summary="Verificar OTP")
async def verify_otp(db: db_dep, req: schemas.VerifyOtpIn) -> schemas.VerifyOtpOut:
    """
    Verifica o código OTP e retorna um token temporário para redefinir a senha
    """
    return await services.ResetPasswordService.verify_otp(db=db, req=req)


@reset_password_router.post(
    path="/", status_code=status.HTTP_204_NO_CONTENT, summary="Redefinir senha"
)
async def reset_password(db: db_dep, req: schemas.ResetPasswordIn):
    """
    Redefine a senha do usuário usando o token obtido na verificação do OTP
    """
    await services.ResetPasswordService.reset_password(db=db, req=req)
