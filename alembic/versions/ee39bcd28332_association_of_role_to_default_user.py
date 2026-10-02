"""association of role to default user

Revision ID: ee39bcd28332
Revises: 07e8988fb1a5
Create Date: 2026-10-02 10:12:27.976265

"""

from collections.abc import Sequence
from typing import Final

import sqlalchemy as sa

from alembic import op
from src.api.v1.config import settings

# revision identifiers, used by Alembic.
revision: str = "ee39bcd28332"
down_revision: str | Sequence[str] | None = "07e8988fb1a5"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


DEFAULT_ROLE_CODE: Final[str] = "toolbox_administrador"


def upgrade() -> None:
    op.execute(
        sa.text("""
            INSERT INTO users_roles (user_id, role_id)
            SELECT u.id, r.id
            FROM users u
            CROSS JOIN roles r
            WHERE u.email = :email
              AND r.code = :role_code
              AND NOT EXISTS (
                  SELECT 1
                  FROM users_roles ur
                  WHERE ur.user_id = u.id
                    AND ur.role_id = r.id
              )
        """).bindparams(
            email=settings.default_user_email,
            role_code=DEFAULT_ROLE_CODE,
        )
    )


def downgrade() -> None:
    op.execute(
        sa.text("""
            DELETE FROM users_roles
            WHERE user_id = (
                SELECT id FROM users WHERE email = :email
            )
            AND role_id = (
                SELECT id FROM roles WHERE code = :role_code
            )
        """).bindparams(
            email=settings.default_user_email,
            role_code=DEFAULT_ROLE_CODE,
        )
    )
