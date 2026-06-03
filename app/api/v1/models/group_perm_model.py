from .. import db
from sqlalchemy import Column, ForeignKey, Integer, Table

group_perm = Table(
    "grupos_permissoes",
    db.Base.metadata,
    Column("id_grupo", Integer, ForeignKey("grupos.id"), primary_key=True),
    Column("id_permissao", Integer, ForeignKey("permissoes.id"), primary_key=True),
)
