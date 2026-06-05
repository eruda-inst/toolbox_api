"""populando permissões

Revision ID: ba191e30aa82
Revises: 23fedb328fb0
Create Date: 2026-06-05 10:04:55.889121

"""

from alembic import op
from typing import Sequence, Union
from app.api.v1.utils.enums.perm_names_enum import PermNames
from app.api.v1.utils.enums.perm_codes_enum import PermCodes

# revision identifiers, used by Alembic.
revision: str = "ba191e30aa82"
down_revision: Union[str, Sequence[str], None] = "23fedb328fb0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(f"""
        INSERT INTO permissoes (nome, codigo, criado_em)
        SELECT
            '{PermNames.CREATE_USERS}',
            '{PermCodes.CREATE_USERS}',
            timezone('America/Bahia', now())
        WHERE NOT EXISTS (
            SELECT 1
            FROM permissoes
            WHERE codigo = '{PermCodes.CREATE_USERS}' AND nome = '{PermNames.CREATE_USERS}'
        );
        """)
    op.execute(f"""
        INSERT INTO permissoes (nome, codigo, criado_em)
        SELECT
            '{PermNames.READ_USERS}',
            '{PermCodes.READ_USERS}',
            timezone('America/Bahia', now())
        WHERE NOT EXISTS (
            SELECT 1
            FROM permissoes
            WHERE codigo = '{PermCodes.READ_USERS}' AND nome = '{PermNames.READ_USERS}'
        );
        """)
    op.execute(f"""
        INSERT INTO permissoes (nome, codigo, criado_em)
        SELECT
            '{PermNames.UPDATE_USERS}',
            '{PermCodes.UPDATE_USERS}',
            timezone('America/Bahia', now())
        WHERE NOT EXISTS (
            SELECT 1
            FROM permissoes
            WHERE codigo = '{PermCodes.UPDATE_USERS}' AND nome = '{PermNames.UPDATE_USERS}'
        );
        """)
    op.execute(f"""
        INSERT INTO permissoes (nome, codigo, criado_em)
        SELECT
            '{PermNames.DEL_USERS}',
            '{PermCodes.DEL_USERS}',
            timezone('America/Bahia', now())
        WHERE NOT EXISTS (
            SELECT 1
            FROM permissoes
            WHERE codigo = '{PermCodes.DEL_USERS}' AND nome = '{PermNames.DEL_USERS}'
        );
        """)


def downgrade() -> None:
    op.execute(f"""
        DELETE FROM grupos_permissoes
        WHERE id_permissao IN (
            SELECT id FROM permissoes
            WHERE codigo IN ('{PermCodes.CREATE_USERS}', '{PermCodes.READ_USERS}', '{PermCodes.UPDATE_USERS}', '{PermCodes.DEL_USERS}')
        );
    """)
    op.execute(f"""
        DELETE FROM permissoes
        WHERE codigo IN ('{PermCodes.CREATE_USERS}', '{PermCodes.READ_USERS}', '{PermCodes.UPDATE_USERS}', '{PermCodes.DEL_USERS}')
    """)
