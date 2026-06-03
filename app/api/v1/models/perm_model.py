from .. import db
from sqlalchemy.orm import relationship
from .group_perm_model import group_perm
from sqlalchemy import Integer, Column, String, TIMESTAMP, func


class Perm(db.Base):
    __tablename__ = "permissoes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nome = Column(String, nullable=False, unique=True)
    codigo = Column(String, nullable=False, unique=True)

    criado_em = Column(
        TIMESTAMP(timezone=True),
        server_default=func.timezone("America/Bahia", func.now()),
    )

    grupos = relationship("Group", back_populates="permissoes", secondary=group_perm)
