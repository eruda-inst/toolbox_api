from .. import db
from sqlalchemy import Column, Integer, String, TIMESTAMP


class TokenBlacklist(db.Base):
    __tablename__ = "token_blacklist"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    jti = Column(String, unique=True, index=True, nullable=False)
    expiracao = Column(TIMESTAMP(timezone=True), nullable=False)
