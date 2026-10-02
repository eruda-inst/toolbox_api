"""initialization of default user

Revision ID: 9207e731b5a4
Revises: 4947b9f62392
Create Date: 2026-10-02 10:09:06.428014

"""

from collections.abc import Sequence
from typing import Final, TypedDict

import sqlalchemy as sa
from argon2 import PasswordHasher
from pydantic import EmailStr

from alembic import op
from src.api.v1.config import settings

# revision identifiers, used by Alembic.
revision: str = "9207e731b5a4"
down_revision: str | Sequence[str] | None = "4947b9f62392"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


ph = PasswordHasher()

DefaultUser = TypedDict(
    "DefaultUser", {"email": EmailStr, "full_name": str, "hashed_password": str}
)

DEFAULT_USER: Final[DefaultUser] = {
    "email": settings.default_user_email,
    "full_name": settings.default_user_full_name,
    "hashed_password": ph.hash(
        password=settings.default_user_password.get_secret_value()
    ),
}


def upgrade() -> None:
    op.execute(
        sa.text("""
            INSERT INTO users (full_name, email, password)
            SELECT :full_name, :email, :password
            WHERE NOT EXISTS (SELECT 1 FROM users WHERE email = :email)
        """).bindparams(
            full_name=DEFAULT_USER["full_name"],
            email=DEFAULT_USER["email"],
            password=DEFAULT_USER["hashed_password"],
        )
    )


def downgrade() -> None:
    op.execute(
        sa.text("""
            DELETE FROM users WHERE email = :email
        """).bindparams(
            email=DEFAULT_USER["email"],
        )
    )
