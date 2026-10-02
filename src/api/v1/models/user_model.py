from sqlalchemy import TIMESTAMP, Boolean, Column, Integer, String, func, text
from sqlalchemy.orm import relationship

from .. import database
from .user_role_model import user_role


class UserModel(database.Base):
    __tablename__ = "users"

    id = Column(type_=Integer, primary_key=True)
    full_name = Column(type_=String, index=True, nullable=False)
    email = Column(type_=String, nullable=False, unique=True)
    password = Column(type_=String, nullable=False)
    is_active = Column(
        type_=Boolean, server_default=text("true"), index=True, nullable=False
    )
    token_version = Column(
        type_=Integer, default=1, server_default=text("1"), nullable=False
    )
    created_at = Column(
        type_=TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(type_=TIMESTAMP(timezone=True), onupdate=func.now())

    roles = relationship(
        argument="RoleModel", secondary="users_roles", back_populates="users"
    )
