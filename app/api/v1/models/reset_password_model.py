from .. import db
from sqlalchemy import Column, Integer, String, TIMESTAMP, Boolean, func


class ResetPassword(db.Base):
    __tablename__ = "reset_password"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String, nullable=False, index=True)
    otp_hash = Column(String, nullable=False)
    expires_at = Column(TIMESTAMP(timezone=True), nullable=False)
    used = Column(Boolean, default=False)
    reset_token_jti = Column(String, nullable=True)
    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.timezone("America/Bahia", func.now()),
    )
