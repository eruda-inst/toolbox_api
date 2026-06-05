"""populando permissões

Revision ID: ba191e30aa82
Revises: 23fedb328fb0
Create Date: 2026-06-05 10:04:55.889121

"""

from alembic import op
import sqlalchemy as sa
from typing import Sequence, Union
from app.api.v1.utils.enums.perm_names_enum import PermNames
from app.api.v1.utils.enums.perm_codes_enum import PermCodes

# revision identifiers, used by Alembic.
revision: str = "ba191e30aa82"
down_revision: Union[str, Sequence[str], None] = "23fedb328fb0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

CREATE_USERS_PERM_NAME = PermNames.CREATE_USERS
READ_USERS_PERM_NAME = PermNames.READ_USERS
UPDATE_USERS_PERM_NAME = PermNames.UPDATE_USERS
DEL_USERS_PERM_NAME = PermNames.DEL_USERS

CREATE_USERS_PERM_CODE = PermCodes.CREATE_USERS
READ_USERS_PERM_CODE = PermCodes.READ_USERS
UPDATE_USERS_PERM_CODE = PermCodes.UPDATE_USERS
DEL_USERS_PERM_CODE = PermCodes.DEL_USERS


def upgrade() -> None:
    op.execute(
        sa.text("""
            INSERT INTO permissoes (nome, codigo, criado_em)
            SELECT
                :create_users_perm_name,
                :create_users_perm_code,
                timezone('America/Bahia', now())
            WHERE
                NOT EXISTS (SELECT 1 FROM permissoes WHERE nome = :create_users_perm_name)
                AND NOT EXISTS (SELECT 1 FROM permissoes WHERE codigo = :create_users_perm_code);
        """).bindparams(
            create_users_perm_name=CREATE_USERS_PERM_NAME,
            create_users_perm_code=CREATE_USERS_PERM_CODE,
        )
    )
    op.execute(
        sa.text("""
            INSERT INTO permissoes (nome, codigo, criado_em)
            SELECT
                :read_users_perm_name,
                :read_users_perm_code,
                timezone('America/Bahia', now())
            WHERE
                NOT EXISTS (SELECT 1 FROM permissoes WHERE nome = :read_users_perm_name)
                AND NOT EXISTS (SELECT 1 FROM permissoes WHERE codigo = :read_users_perm_code);
        """).bindparams(
            read_users_perm_name=READ_USERS_PERM_NAME,
            read_users_perm_code=READ_USERS_PERM_CODE,
        )
    )
    op.execute(
        sa.text("""
            INSERT INTO permissoes (nome, codigo, criado_em)
            SELECT
                :update_users_perm_name,
                :update_users_perm_code,
                timezone('America/Bahia', now())
            WHERE
                NOT EXISTS (SELECT 1 FROM permissoes WHERE nome = :update_users_perm_name)
                AND NOT EXISTS (SELECT 1 FROM permissoes WHERE codigo = :update_users_perm_code);
        """).bindparams(
            update_users_perm_name=UPDATE_USERS_PERM_NAME,
            update_users_perm_code=UPDATE_USERS_PERM_CODE,
        )
    )
    op.execute(
        sa.text("""
            INSERT INTO permissoes (nome, codigo, criado_em)
            SELECT
                :del_users_perm_name,
                :del_users_perm_code,
                timezone('America/Bahia', now())
            WHERE
                NOT EXISTS (SELECT 1 FROM permissoes WHERE nome = :del_users_perm_name)
                AND NOT EXISTS (SELECT 1 FROM permissoes WHERE codigo = :del_users_perm_code);
        """).bindparams(
            del_users_perm_name=DEL_USERS_PERM_NAME,
            del_users_perm_code=DEL_USERS_PERM_CODE,
        )
    )


def downgrade() -> None:
    op.execute(
        sa.text("""
            DELETE FROM grupos_permissoes
            WHERE id_permissao IN (
                SELECT id FROM permissoes
                WHERE codigo IN (
                    :create_users_perm_code,
                    :read_users_perm_code,
                    :update_users_perm_code,
                    :del_users_perm_code
                )
            );
        """).bindparams(
            create_users_perm_code=CREATE_USERS_PERM_CODE,
            read_users_perm_code=READ_USERS_PERM_CODE,
            update_users_perm_code=UPDATE_USERS_PERM_CODE,
            del_users_perm_code=DEL_USERS_PERM_CODE,
        )
    )
    op.execute(
        sa.text("""
            DELETE FROM permissoes
            WHERE codigo IN (
                :create_users_perm_code,
                :read_users_perm_code,
                :update_users_perm_code,
                :del_users_perm_code
            );
        """).bindparams(
            create_users_perm_code=CREATE_USERS_PERM_CODE,
            read_users_perm_code=READ_USERS_PERM_CODE,
            update_users_perm_code=UPDATE_USERS_PERM_CODE,
            del_users_perm_code=DEL_USERS_PERM_CODE,
        )
    )
