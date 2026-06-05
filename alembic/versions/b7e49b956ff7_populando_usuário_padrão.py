"""populando usuário padrão

Revision ID: b7e49b956ff7
Revises: ba191e30aa82
Create Date: 2026-06-05 10:35:17.377030

"""

from alembic import op
import sqlalchemy as sa
from typing import Sequence, Union
from app.api.v1.cores.config_core import settings
from app.api.v1.utils.enums.group_names_enum import GroupNames

# revision identifiers, used by Alembic.
revision: str = "b7e49b956ff7"
down_revision: Union[str, Sequence[str], None] = "ba191e30aa82"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

DEFAULT_USER_NAME = settings.default_user_full_name
DEFAULT_USER_EMAIL = settings.default_user_email
DEFAULT_USER_PASSWORD = settings.default_user_password.get_secret_value()
DEFAULT_USER_ACTIVE = True
DEFAULT_USER_GROUP_NAME = GroupNames.ADMIN


def upgrade() -> None:
    op.execute(
        sa.text(f"""
            INSERT INTO usuarios (nome, email, senha, ativo, criado_em, atualizado_em, id_grupo)
            SELECT
                :nome,
                :email,
                :senha,
                :ativo,
                timezone('America/Bahia', now()),
                timezone('America/Bahia', now()),
                (SELECT id FROM grupos WHERE nome = :group_name)
            WHERE NOT EXISTS (
                SELECT 1 FROM usuarios WHERE nome = :nome)
                AND NOT EXISTS (SELECT 1 FROM usuarios WHERE email = :email)
        """).bindparams(
            nome=DEFAULT_USER_NAME,
            email=DEFAULT_USER_EMAIL,
            senha=DEFAULT_USER_PASSWORD,
            ativo=DEFAULT_USER_ACTIVE,
            group_name=DEFAULT_USER_GROUP_NAME,
        )
    )


def downgrade() -> None:
    op.execute(
        sa.text(f"""
            DELETE FROM usuarios
            WHERE nome = :nome AND email = :email;
        """).bindparams(
            nome=DEFAULT_USER_NAME,
            email=DEFAULT_USER_EMAIL,
        )
    )
