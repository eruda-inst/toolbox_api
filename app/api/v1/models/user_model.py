from .. import db
from sqlalchemy.orm import relationship
from sqlalchemy import Integer, Column, String, TIMESTAMP, func, ForeignKey, Boolean


class User(db.Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nome = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=False, unique=True)
    senha = Column(String, nullable=False)
    ativo = Column(Boolean, default=True)

    criado_em = Column(
        TIMESTAMP(timezone=True),
        server_default=func.timezone("America/Bahia", func.now()),
    )
    atualizado_em = Column(
        TIMESTAMP(timezone=True),
        onupdate=func.timezone("America/Bahia", func.now()),
        nullable=True,
    )

    id_grupo = Column(
        Integer,
        ForeignKey("grupos.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    grupo = relationship("Group", back_populates="usuarios")
