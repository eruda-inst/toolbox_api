from .. import db
from sqlalchemy import Column, ForeignKey, Integer, Table

group_perm = Table(
    "grupos_permissoes",
    db.Base.metadata,
    Column("group_id", Integer, ForeignKey("grupos.id"), primary_key=True),
    Column("permission_id", Integer, ForeignKey("permissoes.id"), primary_key=True),
)
