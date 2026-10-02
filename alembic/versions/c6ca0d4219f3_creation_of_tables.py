"""creation of tables

Revision ID: c6ca0d4219f3
Revises:
Create Date: 2026-10-02 10:03:29.377218

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c6ca0d4219f3"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Users
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("full_name", sa.String, index=True, nullable=False),
        sa.Column("email", sa.String, nullable=False, unique=True),
        sa.Column("password", sa.String, nullable=False),
        sa.Column(
            "is_active",
            sa.Boolean,
            server_default=sa.text("true"),
            index=True,
            nullable=False,
        ),
        sa.Column(
            "token_version",
            sa.Integer,
            default=1,
            server_default=sa.text("1"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), onupdate=sa.func.now()),
        if_not_exists=True,
    )
    # Permissions
    op.create_table(
        "permissions",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("code", sa.String, nullable=False, unique=True),
        sa.Column("description", sa.String),
        sa.Column(
            "is_active",
            sa.Boolean,
            server_default=sa.text("true"),
            index=True,
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), onupdate=sa.func.now()),
        if_not_exists=True,
    )
    # Roles
    op.create_table(
        "roles",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("code", sa.String, unique=True),
        sa.Column("title", sa.String, nullable=False),
        sa.Column("description", sa.String),
        sa.Column(
            "is_active",
            sa.Boolean,
            server_default=sa.text("true"),
            index=True,
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), onupdate=sa.func.now()),
        if_not_exists=True,
    )
    # Categories
    op.create_table(
        "categories",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String, nullable=False, unique=True),
        sa.Column(
            "is_active",
            sa.Boolean,
            server_default=sa.text("true"),
            index=True,
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), onupdate=sa.func.now()),
        if_not_exists=True,
    )
    # Tools
    op.create_table(
        "tools",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String, nullable=False, unique=True),
        sa.Column("description", sa.String),
        sa.Column(
            "is_active",
            sa.Boolean,
            server_default=sa.text("true"),
            index=True,
            nullable=False,
        ),
        sa.Column("url", sa.String),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), onupdate=sa.func.now()),
        sa.Column(
            "category_id",
            sa.Integer,
            sa.ForeignKey(
                column="categories.id", onupdate="CASCADE", ondelete="SET NULL"
            ),
        ),
        if_not_exists=True,
    )
    # Roles Permissions
    op.create_table(
        "roles_permissions",
        sa.Column("role_id", sa.Integer, sa.ForeignKey("roles.id"), primary_key=True),
        sa.Column(
            "permission_id",
            sa.Integer,
            sa.ForeignKey("permissions.id"),
            primary_key=True,
        ),
        if_not_exists=True,
    )
    # User Roles
    op.create_table(
        "users_roles",
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), primary_key=True),
        sa.Column("role_id", sa.Integer, sa.ForeignKey("roles.id"), primary_key=True),
        if_not_exists=True,
    )


def downgrade() -> None:
    op.drop_table(table_name="users_roles", if_exists=True)
    op.drop_table(table_name="roles_permissions", if_exists=True)
    op.drop_table(table_name="tools", if_exists=True)
    op.drop_table(table_name="categories", if_exists=True)
    op.drop_table(table_name="roles", if_exists=True)
    op.drop_table(table_name="permissions", if_exists=True)
    op.drop_table(table_name="users", if_exists=True)
