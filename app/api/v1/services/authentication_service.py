from fastapi.logger import logger
from .. import cores, models, cruds
from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from jose import ExpiredSignatureError, JWTError, jwt

ALGORITHM = "HS256"
SECRET_KEY = cores.settings.secret_key.get_secret_value()


class AuthenticationService:
    @staticmethod
    async def verify_access_token(db: AsyncSession, access_token: str) -> models.User:
        try:
            payload = jwt.decode(
                token=access_token,
                key=SECRET_KEY,
                algorithms=[ALGORITHM],
            )
            email: str | None = payload.get("sub")
            if not email:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token inválido",
                )
        except ExpiredSignatureError:
            logger.warning("Token expirado recebido")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expirado",
            )
        except JWTError as e:
            logger.warning(f"Token inválido: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido",
            )
        try:
            user = await cruds.UserCrud.get_by_email(db=db, email=email)
        except SQLAlchemyError as e:
            logger.error(f"Erro no banco de dados durante verificação de token: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro interno ao validar usuário",
            )
        if user is None:
            logger.warning(f"Usuário do token não encontrado: {email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciais inválidas",
            )
        if not bool(user.ativo):
            logger.warning(f"Usuário inativo tentou acesso: {email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuário inativo. Contate o administrador.",
            )
        return user
