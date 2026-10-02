from sqlalchemy import TIMESTAMP, Boolean, Column, Integer, String, func, text
from sqlalchemy.orm import relationship

from .. import database
from .role_permission_model import role_permission


class PermissionModel(database.Base):
    __tablename__ = "permissions"

    id = Column(type_=Integer, primary_key=True)
    code = Column(type_=String, nullable=False, unique=True)
    description = Column(type_=String)
    is_active = Column(
        type_=Boolean, server_default=text("true"), index=True, nullable=False
    )
    created_at = Column(
        type_=TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(type_=TIMESTAMP(timezone=True), onupdate=func.now())

    roles = relationship(
        argument="RoleModel",
        secondary="roles_permissions",
        back_populates="permissions",
    )
