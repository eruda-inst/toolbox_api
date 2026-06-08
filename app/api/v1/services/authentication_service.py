from typing import Any
from zoneinfo import ZoneInfo
from fastapi.logger import logger
from datetime import datetime, timedelta
from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from .. import cores, models, cruds, schemas
from sqlalchemy.ext.asyncio import AsyncSession
from jose import ExpiredSignatureError, JWTError, jwt

ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = cores.settings.token_expire_minutes
REFRESH_TOKEN_EXPIRE_DAYS = cores.settings.refresh_token_expire_days
TOKEN_EXPIRE_SECONDS = cores.settings.token_expire_seconds
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
                msg = "Token inválido"
                logger.warning(msg)
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail=msg
                )
        except ExpiredSignatureError:
            msg = "Token expirado"
            logger.warning(msg)
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=msg)
        except JWTError as e:
            msg = "Token inválido"
            logger.warning(f"{msg}: {e}")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=msg)
        try:
            user = await cruds.UserCrud.get_by_email(db=db, email=email)
        except SQLAlchemyError as e:
            msg = "Erro no banco de dados durante verificação de token"
            logger.error(f"{msg}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=msg
            )
        if user is None:
            msg = "Usuário do token, não encontrado"
            logger.warning(f"{msg}")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=msg)
        if not bool(user.ativo):
            msg = "Usuário inativo tentou acesso"
            logger.warning(msg)
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=msg)
        return user

    @staticmethod
    def _create_token(data: dict[str, Any], expires_delta: timedelta) -> str:
        try:
            to_encode = data.copy()
            expire = datetime.now(ZoneInfo("America/Bahia")) + expires_delta
            to_encode.update({"exp": expire})
            encoded_jwt = jwt.encode(
                claims=to_encode, key=SECRET_KEY, algorithm=ALGORITHM
            )
            return encoded_jwt
        except Exception as e:
            msg = "Erro inesperado durante criação de token"
            logger.error(f"{msg}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=msg
            )

    @classmethod
    async def login(
        cls, db: AsyncSession, creds: schemas.LoginCreds
    ) -> schemas.AccessTokenOut:
        try:
            email = creds.email
            plain_senha = creds.senha.get_secret_value()

            user = await cruds.UserCrud.get_by_email(db=db, email=email)

            if not user:
                msg = "Credenciais inválidas"
                logger.warning(msg)
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail=msg
                )

            is_valid_password = creds.verify_senha(
                plain_senha=plain_senha, hashed_senha=str(user.senha)
            )

            if not is_valid_password:
                msg = "Credenciais inválidas"
                logger.warning(msg)
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail=msg
                )

            if not bool(user.ativo):
                msg = "Usuário inativo tentou login"
                logger.warning(msg)
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail=msg
                )

            data = {"sub": email}

            access_token = cls._create_token(
                data=data, expires_delta=timedelta(minutes=TOKEN_EXPIRE_MINUTES)
            )
            refresh_token = cls._create_token(
                data=data, expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
            )

            return schemas.AccessTokenOut(
                access_token=access_token,
                refresh_token=refresh_token,
                expires_in=TOKEN_EXPIRE_SECONDS,
            )
        except HTTPException:
            raise
        except SQLAlchemyError as e:
            msg = "Erro no banco de dados durante login"
            logger.error(f"{msg}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=msg
            )
        except Exception as e:
            msg = "Erro inesperado durante login"
            logger.error(f"{msg}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=msg
            )
