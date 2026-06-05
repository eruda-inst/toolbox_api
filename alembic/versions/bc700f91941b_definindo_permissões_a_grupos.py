"""definindo permissões a grupos

Revision ID: bc700f91941b
Revises: b7e49b956ff7
Create Date: 2026-06-05 14:17:00.174420

"""

from alembic import op
import sqlalchemy as sa
from typing import Sequence, Union
from app.api.v1.utils.enums.perm_codes_enum import PermCodes
from app.api.v1.utils.enums.group_names_enum import GroupNames

# revision identifiers, used by Alembic.
revision: str = "bc700f91941b"
down_revision: Union[str, Sequence[str], None] = "b7e49b956ff7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


ADMIN_GROUP_NAME = GroupNames.ADMIN
CREATE_USERS_PERM_CODE = PermCodes.CREATE_USERS
READ_USERS_PERM_CODE = PermCodes.READ_USERS
UPDATE_USERS_PERM_CODE = PermCodes.UPDATE_USERS
DEL_USERS_PERM_CODE = PermCodes.DEL_USERS


def upgrade() -> None:
    op.execute(
        sa.text("""
            INSERT INTO grupos_permissoes (id_grupo, id_permissao)
            SELECT g.id, p.id
            FROM grupos g, permissoes p
            WHERE g.nome = :admin_group_name
            AND p.codigo = :create_users_perm_code
            AND NOT EXISTS (
                SELECT 1
                FROM grupos_permissoes gp
                WHERE gp.id_grupo = g.id
                AND gp.id_permissao = p.id
            );
        """).bindparams(
            admin_group_name=ADMIN_GROUP_NAME,
            create_users_perm_code=CREATE_USERS_PERM_CODE,
        )
    )
    op.execute(
        sa.text("""
            INSERT INTO grupos_permissoes (id_grupo, id_permissao)
            SELECT g.id, p.id
            FROM grupos g, permissoes p
            WHERE g.nome = :admin_group_name
            AND p.codigo = :read_users_perm_code
            AND NOT EXISTS (
                SELECT 1
                FROM grupos_permissoes gp
                WHERE gp.id_grupo = g.id
                AND gp.id_permissao = p.id
            );
        """).bindparams(
            admin_group_name=ADMIN_GROUP_NAME,
            read_users_perm_code=READ_USERS_PERM_CODE,
        )
    )
    op.execute(
        sa.text("""
            INSERT INTO grupos_permissoes (id_grupo, id_permissao)
            SELECT g.id, p.id
            FROM grupos g, permissoes p
            WHERE g.nome = :admin_group_name
            AND p.codigo = :update_users_perm_code
            AND NOT EXISTS (
                SELECT 1
                FROM grupos_permissoes gp
                WHERE gp.id_grupo = g.id
                AND gp.id_permissao = p.id
            );
        """).bindparams(
            admin_group_name=ADMIN_GROUP_NAME,
            update_users_perm_code=UPDATE_USERS_PERM_CODE,
        )
    )
    op.execute(
        sa.text("""
            INSERT INTO grupos_permissoes (id_grupo, id_permissao)
            SELECT g.id, p.id
            FROM grupos g, permissoes p
            WHERE g.nome = :admin_group_name
            AND p.codigo = :del_users_perm_code
            AND NOT EXISTS (
                SELECT 1
                FROM grupos_permissoes gp
                WHERE gp.id_grupo = g.id
                AND gp.id_permissao = p.id
            );
        """).bindparams(
            admin_group_name=ADMIN_GROUP_NAME,
            del_users_perm_code=DEL_USERS_PERM_CODE,
        )
    )


def downgrade() -> None:
    op.execute(
        sa.text("""
            DELETE FROM grupos_permissoes
            WHERE id_grupo = (
                SELECT id
                FROM grupos
                WHERE nome = :admin_group_name
            )
            AND id_permissao IN (
                SELECT id FROM permissoes
                WHERE codigo IN (
                    :create_users_perm_code,
                    :read_users_perm_code,
                    :update_users_perm_code,
                    :del_users_perm_code
                )
            );
        """).bindparams(
            admin_group_name=ADMIN_GROUP_NAME,
            create_users_perm_code=CREATE_USERS_PERM_CODE,
            read_users_perm_code=READ_USERS_PERM_CODE,
            update_users_perm_code=UPDATE_USERS_PERM_CODE,
            del_users_perm_code=DEL_USERS_PERM_CODE,
        )
    )
