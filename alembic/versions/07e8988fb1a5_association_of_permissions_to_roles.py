"""association of permissions to roles

Revision ID: 07e8988fb1a5
Revises: 9207e731b5a4
Create Date: 2026-10-02 10:11:03.430976

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "07e8988fb1a5"
down_revision: str | Sequence[str] | None = "9207e731b5a4"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

ROLE_PERMISSIONS: dict[str, list[str]] = {
    # User
    "toolbox_usuarios_gestor": [
        "toolbox:usuarios:criar",
        "toolbox:usuarios:ver",
        "toolbox:usuarios:editar",
        "toolbox:usuarios:excluir",
    ],
    # Permissions
    "toolbox_permissoes_gestor": [
        "toolbox:permissoes:criar",
        "toolbox:permissoes:ver",
        "toolbox:permissoes:editar",
        "toolbox:permissoes:excluir",
    ],
    # Roles
    "toolbox_perfis_gestor": [
        "toolbox:perfis:criar",
        "toolbox:perfis:ver",
        "toolbox:perfis:editar",
        "toolbox:perfis:excluir",
    ],
    # Categories
    "toolbox_categorias_gestor": [
        "toolbox:categorias:criar",
        "toolbox:categorias:ver",
        "toolbox:categorias:editar",
        "toolbox:categorias:excluir",
    ],
    # Tools
    "toolbox_ferramentas_gestor": [
        "toolbox:ferramentas:criar",
        "toolbox:ferramentas:ver",
        "toolbox:ferramentas:editar",
        "toolbox:ferramentas:excluir",
    ],
    "toolbox_administrador": [
        # User
        "toolbox:usuarios:criar",
        "toolbox:usuarios:ver",
        "toolbox:usuarios:editar",
        "toolbox:usuarios:excluir",
        # Permission
        "toolbox:permissoes:criar",
        "toolbox:permissoes:ver",
        "toolbox:permissoes:editar",
        "toolbox:permissoes:excluir",
        # Role
        "toolbox:perfis:criar",
        "toolbox:perfis:ver",
        "toolbox:perfis:editar",
        "toolbox:perfis:excluir",
        # Category
        "toolbox:categorias:criar",
        "toolbox:categorias:ver",
        "toolbox:categorias:editar",
        "toolbox:categorias:excluir",
        # Tool
        "toolbox:ferramentas:criar",
        "toolbox:ferramentas:ver",
        "toolbox:ferramentas:editar",
        "toolbox:ferramentas:excluir",
    ],
}


def upgrade() -> None:
    for role_code, permission_codes in ROLE_PERMISSIONS.items():
        for permission_code in permission_codes:
            op.execute(
                sa.text("""
                    INSERT INTO roles_permissions (role_id, permission_id)
                    SELECT r.id, p.id
                    FROM roles r, permissions p
                    WHERE r.code = :role_code
                      AND p.code = :permission_code
                      AND NOT EXISTS (
                          SELECT 1
                          FROM roles_permissions rp
                          WHERE rp.role_id = r.id
                            AND rp.permission_id = p.id
                      )
                """).bindparams(
                    role_code=role_code,
                    permission_code=permission_code,
                )
            )


def downgrade() -> None:
    for role_code, permission_codes in ROLE_PERMISSIONS.items():
        for permission_code in permission_codes:
            op.execute(
                sa.text("""
                    DELETE FROM roles_permissions
                    WHERE role_id = (
                        SELECT id FROM roles WHERE code = :role_code
                    )
                    AND permission_id = (
                        SELECT id FROM permissions WHERE code = :permission_code
                    )
                """).bindparams(
                    role_code=role_code,
                    permission_code=permission_code,
                )
            )
