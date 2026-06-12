"""adicionada coluna versao_token à tabela usuários

Revision ID: eae931bd818b
Revises: 4973df7a231a
Create Date: 2026-06-12 14:04:25.021063

"""

from alembic import op
import sqlalchemy as sa
from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = "eae931bd818b"
down_revision: Union[str, Sequence[str], None] = "4973df7a231a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "usuarios",
        sa.Column("versao_token", sa.Integer(), nullable=False, server_default="1"),
        if_not_exists=True,
    )


def downgrade() -> None:
    op.drop_column("usuarios", "versao_token", if_exists=True)
