from .. import db
from sqlalchemy.orm import relationship
from .group_perm_model import group_perm
from sqlalchemy import Integer, Column, String, TIMESTAMP, func


class Group(db.Base):
    __tablename__ = "grupos"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nome = Column(String, nullable=False, unique=True)

    criado_em = Column(
        TIMESTAMP(timezone=True),
        server_default=func.timezone("America/Bahia", func.now()),
    )

    usuarios = relationship("User", back_populates="grupo")
    permissoes = relationship("Perm", back_populates="grupos", secondary=group_perm)
