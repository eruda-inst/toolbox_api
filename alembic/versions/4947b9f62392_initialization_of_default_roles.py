"""initialization of default roles

Revision ID: 4947b9f62392
Revises: bd0ba4344541
Create Date: 2026-10-02 10:07:50.180486

"""

from collections.abc import Sequence
from typing import Final, TypedDict

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "4947b9f62392"
down_revision: str | Sequence[str] | None = "bd0ba4344541"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


DefaultRole = TypedDict("DefaultRole", {"code": str, "title": str, "description": str})

DEFAULT_ROLES: Final[list[DefaultRole]] = [
    {
        "code": "toolbox_usuarios_gestor",
        "title": "Gestor de usuários",
        "description": "Permite criar, ver, editar e excluir usuários no Toolbox.",
    },
    {
        "code": "toolbox_permissoes_gestor",
        "title": "Gestor de permissões",
        "description": "Permite criar, ver, editar e excluir permissões no Toolbox.",
    },
    {
        "code": "toolbox_perfis_gestor",
        "title": "Gestor de perfis",
        "description": "Permite criar, ver, editar e excluir perfis no Toolbox.",
    },
    {
        "code": "toolbox_categorias_gestor",
        "title": "Gestor de categorias",
        "description": "Permite criar, ver, editar e excluir categorias no Toolbox.",
    },
    {
        "code": "toolbox_ferramentas_gestor",
        "title": "Gestor de ferramentas",
        "description": "Permite criar, ver, editar e excluir ferramentas no Toolbox.",
    },
    {
        "code": "toolbox_administrador",
        "title": "Administrador do Toolbox",
        "description": "Permite acesso total a todos os recursos e operações no Toolbox, incluindo usuários, permissões, perfis, categorias e ferramentas.",
    },
]


def upgrade() -> None:
    for role in DEFAULT_ROLES:
        op.execute(
            sa.text("""
                INSERT INTO roles (code, title, description)
                SELECT :code, :title, :description
                WHERE NOT EXISTS (SELECT 1 FROM roles WHERE code = :code)
            """).bindparams(
                code=role["code"],
                title=role["title"],
                description=role["description"],
            )
        )


def downgrade() -> None:
    for role in DEFAULT_ROLES:
        op.execute(
            sa.text("""
                DELETE FROM roles WHERE code = :code
            """).bindparams(
                code=role["code"],
            )
        )
