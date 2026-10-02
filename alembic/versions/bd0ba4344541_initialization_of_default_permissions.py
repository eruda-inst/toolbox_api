"""initialization of default permissions

Revision ID: bd0ba4344541
Revises: c6ca0d4219f3
Create Date: 2026-10-02 10:05:38.635076

"""

from collections.abc import Sequence
from typing import Final, TypedDict

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "bd0ba4344541"
down_revision: str | Sequence[str] | None = "c6ca0d4219f3"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


DefaultPermission = TypedDict("DefaultPermission", {"code": str, "description": str})

DEFAULT_PERMISSIONS: Final[list[DefaultPermission]] = [
    # User
    {
        "code": "toolbox:usuarios:criar",
        "description": "Permite criar usuários no Toolbox.",
    },
    {
        "code": "toolbox:usuarios:ver",
        "description": "Permite ver usuários no Toolbox.",
    },
    {
        "code": "toolbox:usuarios:editar",
        "description": "Permite editar usuários no Toolbox.",
    },
    {
        "code": "toolbox:usuarios:excluir",
        "description": "Permite excluir usuários no Toolbox.",
    },
    # Permission
    {
        "code": "toolbox:permissoes:criar",
        "description": "Permite criar permissões no Toolbox.",
    },
    {
        "code": "toolbox:permissoes:ver",
        "description": "Permite ver permissões no Toolbox.",
    },
    {
        "code": "toolbox:permissoes:editar",
        "description": "Permite editar permissões no Toolbox.",
    },
    {
        "code": "toolbox:permissoes:excluir",
        "description": "Permite excluir permissões no Toolbox.",
    },
    # Role
    {
        "code": "toolbox:perfis:criar",
        "description": "Permite criar perfis no Toolbox.",
    },
    {
        "code": "toolbox:perfis:ver",
        "description": "Permite ver perfis no Toolbox.",
    },
    {
        "code": "toolbox:perfis:editar",
        "description": "Permite editar perfis no Toolbox.",
    },
    {
        "code": "toolbox:perfis:excluir",
        "description": "Permite excluir perfis no Toolbox.",
    },
    # Category
    {
        "code": "toolbox:categorias:criar",
        "description": "Permite criar categorias no Toolbox.",
    },
    {
        "code": "toolbox:categorias:ver",
        "description": "Permite ver categorias no Toolbox.",
    },
    {
        "code": "toolbox:categorias:editar",
        "description": "Permite editar categorias no Toolbox.",
    },
    {
        "code": "toolbox:categorias:excluir",
        "description": "Permite excluir categorias no Toolbox.",
    },
    # Tool
    {
        "code": "toolbox:ferramentas:criar",
        "description": "Permite criar ferramentas no Toolbox.",
    },
    {
        "code": "toolbox:ferramentas:ver",
        "description": "Permite ver ferramentas no Toolbox.",
    },
    {
        "code": "toolbox:ferramentas:editar",
        "description": "Permite editar ferramentas no Toolbox.",
    },
    {
        "code": "toolbox:ferramentas:excluir",
        "description": "Permite excluir ferramentas no Toolbox.",
    },
]


def upgrade() -> None:
    for permission in DEFAULT_PERMISSIONS:
        op.execute(
            sa.text("""
                INSERT INTO permissions (code, description)
                SELECT :code, :description
                WHERE NOT EXISTS (SELECT 1 FROM permissions WHERE code = :code)
            """).bindparams(
                code=permission["code"],
                description=permission["description"],
            )
        )


def downgrade() -> None:
    for permission in DEFAULT_PERMISSIONS:
        op.execute(
            sa.text("""
                DELETE FROM permissions WHERE code = :code
            """).bindparams(
                code=permission["code"],
            )
        )
