"""populando grupos

Revision ID: 23fedb328fb0
Revises: 29d056207da7
Create Date: 2026-06-05 08:50:25.137059

"""

from typing import Sequence, Union

from alembic import op
from app.api.v1.utils.enums.group_names_enum import GroupNames

# revision identifiers, used by Alembic.
revision: str = "23fedb328fb0"
down_revision: Union[str, Sequence[str], None] = "29d056207da7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(f"""
            INSERT INTO grupos (nome, criado_em)
            SELECT
                '{GroupNames.ADMIN}',
                timezone('America/Bahia', now())
            WHERE NOT EXISTS (
                SELECT 1
                FROM grupos
                WHERE nome = '{GroupNames.ADMIN}'
            );
        """)
    op.execute(f"""
            INSERT INTO grupos (nome, criado_em)
            SELECT
                '{GroupNames.USER}',
                timezone('America/Bahia', now())
            WHERE NOT EXISTS (
                SELECT 1
                FROM grupos
                WHERE nome = '{GroupNames.USER}'
            );
        """)


def downgrade() -> None:
    op.execute(f"""
        DELETE FROM grupos_permissoes
        WHERE id_grupo IN (SELECT id FROM grupos WHERE nome IN ('{GroupNames.ADMIN}', '{GroupNames.USER}'));
    """)
    op.execute(f"""
        DELETE FROM grupos
        WHERE nome IN ('{GroupNames.ADMIN}', '{GroupNames.USER}');
    """)
