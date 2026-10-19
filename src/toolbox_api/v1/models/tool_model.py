from sqlalchemy import (
    TIMESTAMP,
    Boolean,
    Column,
    ForeignKey,
    Integer,
    String,
    func,
    text,
)
from sqlalchemy.orm import relationship

from .. import database


class ToolModel(database.Base):
    __tablename__ = "tools"

    id = Column(type_=Integer, primary_key=True)
    name = Column(type_=String, nullable=False, unique=True)
    description = Column(type_=String)
    is_active = Column(
        type_=Boolean, server_default=text("true"), index=True, nullable=False
    )
    url = Column(type_=String)
    created_at = Column(
        type_=TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(type_=TIMESTAMP(timezone=True), onupdate=func.now())
    category_id = Column(
        Integer,
        ForeignKey(column="categories.id", onupdate="CASCADE", ondelete="SET NULL"),
    )

    category = relationship(argument="CategoryModel", back_populates="tools")

    @property
    def category_name(self) -> str | None:
        return self.category.name if self.category else None
