"""populando grupos

Revision ID: 23fedb328fb0
Revises: 29d056207da7
Create Date: 2026-06-05 08:50:25.137059

"""

from alembic import op
import sqlalchemy as sa
from typing import Sequence, Union
from app.api.v1.utils.enums.group_names_enum import GroupNames

# revision identifiers, used by Alembic.
revision: str = "23fedb328fb0"
down_revision: Union[str, Sequence[str], None] = "29d056207da7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

ADMIN_GROUP_NAME = GroupNames.ADMIN
USER_GROUP_NAME = GroupNames.USER


def upgrade() -> None:
    op.execute(
        sa.text("""
            INSERT INTO grupos (nome, criado_em)
            SELECT
                :admin_group_name,
                timezone('America/Bahia', now())
            WHERE NOT EXISTS (
                SELECT 1
                FROM grupos
                WHERE nome = :admin_group_name
            );
        """).bindparams(
            admin_group_name=ADMIN_GROUP_NAME,
        )
    )
    op.execute(
        sa.text("""
            INSERT INTO grupos (nome, criado_em)
            SELECT
                :user_group_name,
                timezone('America/Bahia', now())
            WHERE NOT EXISTS (
                SELECT 1
                FROM grupos
                WHERE nome = :user_group_name
            );
        """).bindparams(
            user_group_name=USER_GROUP_NAME,
        )
    )


def downgrade() -> None:
    op.execute(
        sa.text("""
            DELETE FROM grupos_permissoes
            WHERE id_grupo IN (SELECT id FROM grupos WHERE nome IN (:admin_group_name, :user_group_name));
        """).bindparams(
            admin_group_name=ADMIN_GROUP_NAME,
            user_group_name=USER_GROUP_NAME,
        )
    )
    op.execute(
        sa.text("""
            DELETE FROM grupos
            WHERE nome IN (:admin_group_name, :user_group_name);
        """).bindparams(
            admin_group_name=ADMIN_GROUP_NAME,
            user_group_name=USER_GROUP_NAME,
        )
    )
