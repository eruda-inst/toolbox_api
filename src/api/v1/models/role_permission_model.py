from sqlalchemy import Column, ForeignKey, Integer, Table

from .. import database

role_permission = Table(
    "roles_permissions",
    database.Base.metadata,
    Column("role_id", Integer, ForeignKey("roles.id"), primary_key=True),
    Column("permission_id", Integer, ForeignKey("permissions.id"), primary_key=True),
)
