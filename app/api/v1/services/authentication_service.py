import uuid
from typing import Any
from zoneinfo import ZoneInfo
from fastapi.logger import logger
from sqlalchemy.future import select
from datetime import datetime, timedelta
from fastapi import HTTPException, status
from .. import cores, models, cruds, schemas
from sqlalchemy.ext.asyncio import AsyncSession
from jose import ExpiredSignatureError, JWTError, jwt
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

ALGORITHM = "HS256"
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
            token_type: str | None = payload.get("type")
            token_version: int | None = payload.get("ver")

            if not email or token_type != "access":
                msg = "Token inválido"
                logger.warning(msg)
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail=msg
                )

            if token_version is None:
                msg = "Token sem versão - versão desatualizada"
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

            if user is None:
                msg = "Usuário do token não encontrado"
                logger.warning(msg)
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail=msg
                )

            if not bool(user.ativo):
                msg = "Usuário inativo tentou acesso"
                logger.warning(msg)
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail=msg
                )

            if user.versao_token != token_version:  # type: ignore
                msg = "Token desatualizado (versão incorreta)"
                logger.warning(
                    f"{msg} - user: {user.email}, token_ver: {token_version}, db_ver: {user.versao_token}"
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token inválido ou expirado",
                )

            return user

        except SQLAlchemyError as e:
            msg = "Erro no banco de dados durante verificação de token"
            logger.error(f"{msg}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=msg
            )

    @classmethod
    def _create_token(
        cls,
        data: dict[str, Any],
        expires_delta: timedelta,
        token_type: str,
        user_token_version: int = 1,
    ) -> str:
        to_encode = data.copy()
        expire = datetime.now(ZoneInfo("America/Bahia")) + expires_delta
        to_encode.update(
            {
                "exp": expire,
                "type": token_type,
                "jti": str(uuid.uuid4()),
                "ver": user_token_version,
            }
        )
        return jwt.encode(claims=to_encode, key=SECRET_KEY, algorithm=ALGORITHM)

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
                data=data,
                expires_delta=timedelta(seconds=TOKEN_EXPIRE_SECONDS),
                token_type="access",
                user_token_version=user.versao_token,  # type: ignore
            )
            refresh_token = cls._create_token(
                data=data,
                expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
                token_type="refresh",
                user_token_version=user.versao_token,  # type: ignore
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

    @classmethod
    async def refresh_token(
        cls, db: AsyncSession, token_req: schemas.RefreshTokenReq
    ) -> schemas.AccessTokenOut:
        token = token_req.refresh_token

        try:
            payload = jwt.decode(token=token, key=SECRET_KEY, algorithms=[ALGORITHM])
            email: str | None = payload.get("sub")
            jti: str | None = payload.get("jti")
            token_type: str | None = payload.get("type")
            exp_timestamp = payload.get("exp")
            token_version: int | None = payload.get("ver")

            if not exp_timestamp or not isinstance(exp_timestamp, (int, float)):
                msg = "Refresh token inválido: expiração ausente ou mal formatada"
                logger.warning(msg)
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail=msg
                )

            if not email or not jti or token_type != "refresh":
                msg = "Refresh token inválido"
                logger.warning(msg)
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail=msg
                )

            if token_version is None:
                msg = "Refresh token sem versão"
                logger.warning(msg)
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail=msg
                )

        except ExpiredSignatureError:
            msg = "Refresh token expirado"
            logger.warning(msg)
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=msg)
        except JWTError:
            msg = "Refresh token inválido"
            logger.warning(msg)
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=msg)

        try:
            stmt = select(models.TokenBlacklist).where(models.TokenBlacklist.jti == jti)
            result = await db.execute(stmt)
            blacklisted_token = result.scalar_one_or_none()

            if blacklisted_token:
                msg = "Tentativa de reuso de refresh token na blacklist"
                logger.warning(msg)
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail=msg
                )

            user = await cruds.UserCrud.get_by_email(db=db, email=email)
            if user is None or not bool(user.ativo):
                msg = "Usuário inválido ou inativo"
                logger.warning(msg)
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail=msg
                )

            if bool(token_version < user.versao_token):
                msg = "Refresh token desatualizado (versão antiga)"
                logger.warning(
                    f"{msg} - token_ver: {token_version}, user_ver: {user.versao_token}"
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido"
                )

            exp_datetime = datetime.fromtimestamp(
                exp_timestamp, tz=ZoneInfo("America/Bahia")
            )
            new_blacklist_entry = models.TokenBlacklist(jti=jti, expiracao=exp_datetime)
            db.add(new_blacklist_entry)

            data = {"sub": email}
            new_access_token = cls._create_token(
                data=data,
                expires_delta=timedelta(seconds=TOKEN_EXPIRE_SECONDS),
                token_type="access",
                user_token_version=user.versao_token,  # type: ignore
            )
            new_refresh_token = cls._create_token(
                data=data,
                expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
                token_type="refresh",
                user_token_version=user.versao_token,  # type: ignore
            )

            await db.commit()

            return schemas.AccessTokenOut(
                access_token=new_access_token,
                refresh_token=new_refresh_token,
                expires_in=TOKEN_EXPIRE_SECONDS,
            )

        except HTTPException:
            await db.rollback()
            raise
        except Exception as e:
            await db.rollback()
            msg = "Erro inesperado ao atualizar refresh token"
            logger.error(f"{msg}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=msg
            )

    @staticmethod
    async def logout(
        db: AsyncSession, refresh_token: str, current_user: models.User
    ) -> None:
        """
        Invalida o refresh token fornecido, mas somente se ele pertencer ao usuário autenticado
        """
        try:
            payload = jwt.decode(
                token=refresh_token,
                key=SECRET_KEY,
                algorithms=[ALGORITHM],
            )
            email = payload.get("sub")
            jti = payload.get("jti")
            token_type = payload.get("type")
            exp_timestamp = payload.get("exp")

            if not email or not jti or token_type != "refresh":
                msg = "Refresh token inválido para logout"
                logger.warning(msg)
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail=msg
                )

            if not exp_timestamp or not isinstance(exp_timestamp, (int, float)):
                msg = "Refresh token mal formatado"
                logger.warning(msg)
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail=msg
                )

            if email != current_user.email:
                msg = "Refresh token não pertence ao usuário autenticado"
                logger.warning(
                    f"{msg} - token sub: {email}, usuário: {current_user.email}"
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Você não pode invalidar um token que não lhe pertence",
                )

            stmt = select(models.TokenBlacklist).where(models.TokenBlacklist.jti == jti)
            result = await db.execute(stmt)
            if result.scalar_one_or_none():
                msg = "Refresh token já está na blacklist"
                logger.warning(msg)
                return

            user = await cruds.UserCrud.get_by_email(db=db, email=email)
            if not user or not bool(user.ativo):
                msg = "Usuário inválido ou inativo"
                logger.warning(msg)
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail=msg
                )

            exp_datetime = datetime.fromtimestamp(
                exp_timestamp, tz=ZoneInfo("America/Bahia")
            )
            blacklist_entry = models.TokenBlacklist(jti=jti, expiracao=exp_datetime)
            db.add(blacklist_entry)
            await db.commit()

        except ExpiredSignatureError:
            msg = "Refresh token expirado"
            logger.warning(msg)
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=msg)
        except JWTError as e:
            msg = "Refresh token inválido"
            logger.warning(f"{msg}: {e}")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=msg)
        except IntegrityError as e:
            await db.rollback()
            msg = "Refresh token já foi invalidado anteriormente"
            logger.warning(f"{msg}: {e}")
            return
        except HTTPException:
            await db.rollback()
            raise
        except Exception as e:
            await db.rollback()
            msg = "Erro inesperado ao invalidar refresh token"
            logger.error(f"{msg}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=msg
            )
