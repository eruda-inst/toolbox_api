"""criação de tabelas user, group, perm e group_perm

Revision ID: 29d056207da7
Revises:
Create Date: 2026-06-03 14:44:57.085761

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "29d056207da7"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "grupos",
        sa.Column("id", sa.Integer(), autoincrement=True, primary_key=True, index=True),
        sa.Column("nome", sa.String(), nullable=False, unique=True),
        sa.Column(
            "criado_em",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.func.timezone("America/Bahia", sa.func.now()),
        ),
        if_not_exists=True,
    )
    op.create_table(
        "permissoes",
        sa.Column("id", sa.Integer(), autoincrement=True, primary_key=True, index=True),
        sa.Column("nome", sa.String(), nullable=False, unique=True),
        sa.Column("codigo", sa.String(), nullable=False, unique=True),
        sa.Column(
            "criado_em",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.func.timezone("America/Bahia", sa.func.now()),
        ),
        if_not_exists=True,
    )
    op.create_table(
        "grupos_permissoes",
        sa.Column(
            "id_grupo",
            sa.Integer,
            sa.ForeignKey("grupos.id"),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "id_permissao",
            sa.Integer,
            sa.ForeignKey("permissoes.id"),
            primary_key=True,
            nullable=False,
        ),
        if_not_exists=True,
    )
    op.create_table(
        "usuarios",
        sa.Column("id", sa.Integer(), autoincrement=True, primary_key=True, index=True),
        sa.Column("nome", sa.String(), nullable=False, unique=True),
        sa.Column("email", sa.String(), nullable=False, unique=True),
        sa.Column("senha", sa.String(), nullable=False),
        sa.Column("ativo", sa.Boolean(), default=True),
        sa.Column(
            "criado_em",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.func.timezone("America/Bahia", sa.func.now()),
        ),
        sa.Column(
            "atualizado_em",
            sa.TIMESTAMP(timezone=True),
            onupdate=sa.func.timezone("America/Bahia", sa.func.now()),
            nullable=True,
        ),
        sa.Column(
            "id_grupo",
            sa.Integer,
            sa.ForeignKey("grupos.id", onupdate="CASCADE", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        if_not_exists=True,
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS grupos CASCADE;")
    op.execute("DROP TABLE IF EXISTS permissoes CASCADE;")
    op.execute("DROP TABLE IF EXISTS grupos_permissoes;")
    op.execute("DROP TABLE IF EXISTS usuarios;")
