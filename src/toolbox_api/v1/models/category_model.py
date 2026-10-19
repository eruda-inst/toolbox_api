from sqlalchemy import TIMESTAMP, Boolean, Column, Integer, String, func, text
from sqlalchemy.orm import relationship

from .. import database


class CategoryModel(database.Base):
    __tablename__ = "categories"

    id = Column(type_=Integer, primary_key=True)
    name = Column(type_=String, nullable=False, unique=True)
    is_active = Column(
        type_=Boolean, server_default=text("true"), index=True, nullable=False
    )
    created_at = Column(
        type_=TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(type_=TIMESTAMP(timezone=True), onupdate=func.now())

    tools = relationship(
        argument="ToolModel", back_populates="category", passive_deletes=True
    )
