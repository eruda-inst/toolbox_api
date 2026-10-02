import datetime as dt
from typing import Any, Final
from zoneinfo import ZoneInfo

from argon2 import PasswordHasher
from fastapi import HTTPException, status
from jose import ExpiredSignatureError, JWTError, jwt
from pydantic import EmailStr, NonNegativeInt, PositiveInt
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from .. import config, cruds, models, schemas

JWT_ACCESS_TOKEN_EXPIRE_MINUTES: Final[NonNegativeInt] = (
    config.settings.jwt_access_token_expire_minutes
)
JWT_ALGORITHM: Final[str] = config.settings.jwt_algorithm
JWT_REFRESH_TOKEN_EXPIRE_DAYS: Final[NonNegativeInt] = (
    config.settings.jwt_refresh_token_expire_days
)
JWT_SECRET_KEY: Final[str] = config.settings.jwt_secret_key.get_secret_value()
JWT_TOKEN_EXPIRE_SECONDS: Final[NonNegativeInt] = (
    config.settings.jwt_token_expire_seconds
)

ph = PasswordHasher()


class AuthenticationService:
    @staticmethod
    def _create_token(
        data: dict[str, Any], expires_delta: dt.timedelta, version: PositiveInt
    ) -> str:
        """
        Create a signed JWT token with the given claims and expiration.

        Encodes the provided data dictionary into a JWT, adding the token version
        ('ver') and expiration ('exp') claims, then signs it with the configured
        secret key and algorithm.

        Args:
            data (dict[str, Any]): Claims to include in the token payload (e.g., subject).
            expires_delta (dt.timedelta): Time duration until the token expires.
            version (PositiveInt): Current token version of the user to embed for invalidation.

        Returns:
            str: Encoded JWT string.
        """
        to_encode = data.copy()
        to_encode["ver"] = version
        expire = dt.datetime.now(ZoneInfo(config.settings.timezone)) + expires_delta
        to_encode.update({"exp": expire})
        return jwt.encode(claims=to_encode, key=JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

    @staticmethod
    async def verify_access_token(
        db: AsyncSession, access_token: str
    ) -> models.UserModel:
        """
        Verify an access token and return the associated user.

        Decodes the JWT, validates the signature and expiration, checks the token
        version against the user's current version, ensures the user exists and is
        active, and returns the user model.

        Args:
            db (AsyncSession): Database session for querying the user.
            access_token (str): JWT access token to verify.

        Returns:
            models.UserModel: The authenticated user.

        Raises:
            HTTPException: 401 if token is invalid, expired, missing email/version,
                user not found, or version mismatch; 403 if user is inactive;
                500 on database error.
        """
        try:
            payload = jwt.decode(
                token=access_token, key=JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM]
            )
            email = payload.get("sub")
            if not email:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token payload is missing the 'sub' claim.",
                )
            version_from_token = payload.get("ver")
            if version_from_token is None:
                raise HTTPException(
                    status.HTTP_401_UNAUTHORIZED,
                    detail="Token payload is missing the 'ver' claim.",
                )

            user = await cruds.UserCRUD.read_by(db=db, email=email)
            if not user:
                raise HTTPException(
                    status.HTTP_401_UNAUTHORIZED, detail="User not found."
                )

            if user.token_version != version_from_token:
                raise HTTPException(
                    status.HTTP_401_UNAUTHORIZED,
                    detail="Token has been revoked or is no longer valid.",
                )
            if not bool(user.is_active):
                raise HTTPException(
                    status.HTTP_403_FORBIDDEN, detail="User account is inactive."
                )

            return user
        except ExpiredSignatureError:
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED, detail="Access token has expired."
            )
        except JWTError:
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED, detail="Invalid access token."
            )
        except SQLAlchemyError:
            raise HTTPException(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred while verifying token.",
            )

    @classmethod
    async def login(
        cls, db: AsyncSession, email: EmailStr, password: str
    ) -> schemas.TokenOutSchema:
        """
        Authenticate a user and issue access and refresh tokens.

        Verifies the provided email and password against the stored credentials.
        If valid and the account is active, generates a new access token and refresh
        token, both embedding the user's current token version. Returns the tokens
        along with expiration details.

        Args:
            db (AsyncSession): Database session.
            email (EmailStr): User's email address.
            password (str): User's plain-text password.

        Returns:
            schemas.TokenOutSchema: Contains access_token, refresh_token,
                expires_in, expires_at.

        Raises:
            HTTPException: 401 if credentials are invalid; 403 if account is inactive;
                500 on database error.
        """
        try:
            user = await cruds.UserCRUD.read_by(db=db, email=email)
            if not user:
                raise HTTPException(
                    status.HTTP_401_UNAUTHORIZED, detail="User not found."
                )

            if not ph.verify(password=password, hash=user.password):  # type: ignore
                raise HTTPException(
                    status.HTTP_401_UNAUTHORIZED, detail="Incorrect password."
                )

            if not bool(user.is_active):
                raise HTTPException(
                    status.HTTP_403_FORBIDDEN, detail="User account is inactive."
                )

            data = {"sub": email}
            access_token_timedelta = dt.timedelta(
                minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES
            )
            access_token = cls._create_token(
                data=data,
                expires_delta=access_token_timedelta,
                version=user.token_version,  # type: ignore
            )
            refresh_token_timedelta = dt.timedelta(days=JWT_REFRESH_TOKEN_EXPIRE_DAYS)
            refresh_token = cls._create_token(
                data=data,
                expires_delta=refresh_token_timedelta,
                version=user.token_version,  # type: ignore
            )
            now = dt.datetime.now(tz=ZoneInfo(config.settings.timezone))
            expires_at = now + access_token_timedelta
            return schemas.TokenOutSchema(
                expires_in=JWT_TOKEN_EXPIRE_SECONDS,
                expires_at=expires_at,
                access_token=access_token,
                refresh_token=refresh_token,
            )

        except SQLAlchemyError:
            raise HTTPException(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred during login.",
            )
        except HTTPException:
            raise

    @classmethod
    async def refresh_token(
        cls, db: AsyncSession, refresh_token: str
    ) -> schemas.TokenOutSchema:
        """
        Refresh an access token using a valid refresh token.

        Decodes and validates the provided refresh token, checks the user's existence,
        token version, and active status. If valid, issues a new pair of access and
        refresh tokens with updated expiration times.

        Args:
            db (AsyncSession): Database session.
            refresh_token (str): The refresh token to validate.

        Returns:
            schemas.TokenOutSchema: New access_token, refresh_token, expires_in,
                expires_at.

        Raises:
            HTTPException: 401 if refresh token is invalid, expired, missing email/
                version, user not found, or version mismatch; 403 if user inactive.
        """
        try:
            payload = jwt.decode(
                token=refresh_token, key=JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM]
            )
            email = payload.get("sub")
            if not email:
                raise HTTPException(
                    status.HTTP_401_UNAUTHORIZED,
                    detail="Refresh token payload is missing the 'sub' claim.",
                )
            version_from_token = payload.get("ver")
            if version_from_token is None:
                raise HTTPException(
                    status.HTTP_401_UNAUTHORIZED,
                    detail="Refresh token payload is missing the 'ver' claim.",
                )

            user = await cruds.UserCRUD.read_by(db=db, email=email)
            if not user:
                raise HTTPException(
                    status.HTTP_401_UNAUTHORIZED, detail="User not found."
                )

            if user.token_version != version_from_token:
                raise HTTPException(
                    status.HTTP_401_UNAUTHORIZED,
                    detail="Refresh token has been revoked or is no longer valid.",
                )
            if not bool(user.is_active):
                raise HTTPException(
                    status.HTTP_403_FORBIDDEN, detail="User account is inactive."
                )

        except ExpiredSignatureError:
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED, detail="Refresh token has expired."
            )
        except JWTError:
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token."
            )

        data = {"sub": email}
        access_token_timedelta = dt.timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        new_access_token = cls._create_token(
            data=data,
            expires_delta=access_token_timedelta,
            version=user.token_version,  # type: ignore
        )
        refresh_token_timedelta = dt.timedelta(days=JWT_REFRESH_TOKEN_EXPIRE_DAYS)
        new_refresh_token = cls._create_token(
            data=data,
            expires_delta=refresh_token_timedelta,
            version=user.token_version,  # type: ignore
        )
        now = dt.datetime.now(tz=ZoneInfo(config.settings.timezone))
        expires_at = now + access_token_timedelta
        return schemas.TokenOutSchema(
            expires_at=expires_at,
            expires_in=JWT_TOKEN_EXPIRE_SECONDS,
            access_token=new_access_token,
            refresh_token=new_refresh_token,
        )
