import uuid
import random
from typing import Any
from zoneinfo import ZoneInfo
from fastapi.logger import logger
from sqlalchemy import select, update
from datetime import datetime, timedelta
from passlib.context import CryptContext
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from .. import cores, cruds, models, schemas, utils
from jose import jwt, JWTError, ExpiredSignatureError

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ALGORITHM = "HS256"
SECRET_KEY = cores.settings.secret_key.get_secret_value()
OTP_EXPIRE_MINUTES = 10


class ResetPasswordService:
    @staticmethod
    def _generate_otp() -> str:
        return f"{random.randint(0, 9999):04d}"

    @staticmethod
    async def _invalidate_previous_otps(db: AsyncSession, email: str) -> None:
        stmt = (
            update(models.ResetPassword)
            .where(
                models.ResetPassword.email == email, models.ResetPassword.used == False
            )
            .values(used=True)
        )
        await db.execute(stmt)

    @staticmethod
    def _create_reset_token_with_jti(email: str) -> tuple[str, str]:
        jti = str(uuid.uuid4())
        expire = datetime.now(ZoneInfo("America/Bahia")) + timedelta(minutes=5)
        payload: dict[str, Any] = {
            "sub": email,
            "exp": expire,
            "type": "reset",
            "jti": jti,
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        return token, jti

    @classmethod
    async def request_otp(cls, db: AsyncSession, req: schemas.RequestOtpIn) -> None:
        try:
            user = await cruds.UserCrud.get_by_email(
                db=db, email=req.email, load_perms=False
            )

            if not user:
                logger.info(
                    f"Solicitação de OTP para e-mail não cadastrado: {req.email}"
                )
                return

            if not bool(user.ativo):
                logger.warning(f"Usuário inativo solicitou OTP: {req.email}")
                return

            otp = cls._generate_otp()
            otp_hash = pwd_context.hash(otp)
            expires_at = datetime.now(ZoneInfo("America/Bahia")) + timedelta(
                minutes=OTP_EXPIRE_MINUTES
            )

            try:
                await utils.EmailSender.send(otp=otp, to_name=user.nome, to_email=user.email)  # type: ignore
                logger.info(f"OTP enviado para {user.email}")
            except Exception as e:
                logger.error(f"Falha ao enviar e-mail para {user.email}: {e}")
                return

            await cls._invalidate_previous_otps(db, req.email)

            reset_entry = models.ResetPassword(
                email=req.email,
                otp_hash=otp_hash,
                expires_at=expires_at,
                used=False,
            )
            db.add(reset_entry)
            await db.commit()

        except HTTPException:
            await db.rollback()
            raise
        except Exception as e:
            await db.rollback()
            logger.error(f"Erro inesperado ao solicitar OTP: {e}")

    @classmethod
    async def verify_otp(
        cls, db: AsyncSession, req: schemas.VerifyOtpIn
    ) -> schemas.VerifyOtpOut:
        try:
            stmt = (
                select(models.ResetPassword)
                .where(
                    models.ResetPassword.email == req.email,
                    models.ResetPassword.used == False,
                    models.ResetPassword.expires_at
                    > datetime.now(ZoneInfo("America/Bahia")),
                    models.ResetPassword.otp_hash.isnot(None),
                )
                .order_by(models.ResetPassword.created_at.desc())
            )
            result = await db.execute(stmt)
            otp_entry = result.scalar_one_or_none()

            if not otp_entry:
                logger.warning(
                    f"Tentativa de verificação sem OTP válido para {req.email}"
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Código inválido ou expirado",
                )

            if not pwd_context.verify(secret=req.otp, hash=otp_entry.otp_hash):  # type: ignore
                logger.warning(f"OTP incorreto para {req.email}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="Código inválido"
                )

            otp_entry.used = True  # type: ignore
            db.add(otp_entry)

            reset_token, jti = cls._create_reset_token_with_jti(email=req.email)
            reset_token_entry = models.ResetPassword(
                email=req.email,
                otp_hash=None,
                expires_at=datetime.now(ZoneInfo("America/Bahia"))
                + timedelta(minutes=10),
                used=False,
                reset_token_jti=jti,
            )
            db.add(reset_token_entry)

            await db.commit()

            return schemas.VerifyOtpOut(reset_token=reset_token)
        except HTTPException:
            await db.rollback()
            raise
        except Exception as e:
            await db.rollback()
            logger.error(f"Erro ao verificar OTP: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro interno"
            )

    @staticmethod
    async def _get_email_from_reset_token(token: str) -> str:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            email = payload.get("sub")
            token_type = payload.get("type")
            if not email or token_type != "reset":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="Token inválido"
                )
            return email
        except ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Token expirado"
            )
        except JWTError as e:
            logger.warning(f"Erro ao decodificar reset token: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Token inválido"
            )

    @classmethod
    async def reset_password(
        cls, db: AsyncSession, req: schemas.ResetPasswordIn
    ) -> None:
        try:
            try:
                payload = jwt.decode(
                    req.reset_token, SECRET_KEY, algorithms=[ALGORITHM]
                )
                email = payload.get("sub")
                jti = payload.get("jti")
                token_type = payload.get("type")

                if not email or not jti or token_type != "reset":
                    logger.warning("Reset token inválido: campos ausentes")
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Token inválido",
                    )
            except ExpiredSignatureError:
                logger.warning("Reset token expirado")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Token expirado",
                )
            except JWTError as e:
                logger.warning(f"Erro ao decodificar reset token: {e}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Token inválido",
                )

            stmt = select(models.ResetPassword).where(
                models.ResetPassword.reset_token_jti == jti,
                models.ResetPassword.used == False,
                models.ResetPassword.expires_at
                > datetime.now(ZoneInfo("America/Bahia")),
                models.ResetPassword.otp_hash.is_(None),
            )
            result = await db.execute(stmt)
            reset_entry = result.scalar_one_or_none()

            if not reset_entry:
                logger.warning(
                    f"Reset token com jti {jti} não encontrado ou já utilizado/expirado"
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Token inválido",
                )

            user = await cruds.UserCrud.get_by_email(db=db, email=email)
            if not user or not bool(user.ativo):
                logger.warning(
                    f"Tentativa de reset para usuário inválido/inativo: {email}"
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Usuário não encontrado ou inativo",
                )

            new_password_hash = pwd_context.hash(req.nova_senha.get_secret_value())
            user.senha = new_password_hash  # type: ignore
            user.versao_token += 1  # type: ignore

            reset_entry.used = True  # type: ignore

            db.add(reset_entry)
            db.add(user)

            await db.commit()
            logger.info(
                f"Senha redefinida com sucesso para {email} (versao_token agora = {user.versao_token})"
            )

        except HTTPException:
            await db.rollback()
            raise
        except Exception as e:
            await db.rollback()
            logger.error(f"Erro inesperado ao redefinir senha: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro interno ao redefinir senha",
            )
