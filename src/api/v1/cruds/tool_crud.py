from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from .. import models, schemas


class ToolCRUD:
    @staticmethod
    async def create(db: AsyncSession, data: schemas.ToolInSchema) -> models.ToolModel:
        """
        Create a new tool.

        Args:
            db (AsyncSession): The async database session.
            data (schemas.ToolInSchema): The data for the new tool.

        Returns:
            models.ToolModel: The newly created tool.

        Raises:
            HTTPException: 409 if a tool with the same unique field (e.g., name) already exists.
        """
        tool_data = data.model_dump()
        new_tool = models.ToolModel(**tool_data)

        db.add(new_tool)

        try:
            await db.commit()
        except IntegrityError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Tool already exists."
            )

        await db.refresh(new_tool)

        return new_tool
