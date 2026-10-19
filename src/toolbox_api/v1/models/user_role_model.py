from sqlalchemy import Column, ForeignKey, Integer, Table

from .. import database

user_role = Table(
    "users_roles",
    database.Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("role_id", Integer, ForeignKey("roles.id"), primary_key=True),
)
