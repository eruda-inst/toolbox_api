"""criação de tabela token_blacklist

Revision ID: 101f4014ca7f
Revises: bc700f91941b
Create Date: 2026-06-09 08:29:04.207024

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "101f4014ca7f"
down_revision: Union[str, Sequence[str], None] = "bc700f91941b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "token_blacklist",
        sa.Column("id", sa.Integer(), primary_key=True, index=True, autoincrement=True),
        sa.Column("jti", sa.String(), unique=True, index=True, nullable=False),
        sa.Column("expiracao", sa.TIMESTAMP(timezone=True), nullable=False),
        if_not_exists=True,
    )


def downgrade() -> None:
    op.drop_table("token_blacklist", if_exists=True)
