"""criação de tabela password_reset_tokens

Revision ID: 4973df7a231a
Revises: 101f4014ca7f
Create Date: 2026-06-11 14:16:01.817380

"""

from alembic import op
import sqlalchemy as sa
from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = "4973df7a231a"
down_revision: Union[str, Sequence[str], None] = "101f4014ca7f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "reset_password",
        sa.Column("id", sa.Integer(), primary_key=True, index=True, autoincrement=True),
        sa.Column("email", sa.String(), nullable=False, index=True),
        sa.Column("otp_hash", sa.String(), nullable=True),
        sa.Column("expires_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("used", sa.Boolean(), default=False),
        sa.Column("reset_token_jti", sa.String(), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.func.timezone("America/Bahia", sa.func.now()),
        ),
        if_not_exists=True,
    )


def downgrade() -> None:
    op.drop_table("reset_password", if_exists=True)
