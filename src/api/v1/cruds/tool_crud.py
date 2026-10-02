from collections.abc import Sequence

from fastapi import HTTPException, status
from pydantic import NonNegativeInt, PositiveInt
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
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
            HTTPException: 409 if a tool with the same unique field already exists.
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

    @staticmethod
    async def read_all_by(
        db: AsyncSession,
        page: PositiveInt,
        limit: PositiveInt,
        name: str | None,
        category_name: str | None,
        is_active: bool | None,
    ) -> tuple[NonNegativeInt, Sequence[models.ToolModel]]:
        """
        Retrieve a paginated list of tools, optionally filtered by the given criteria.

        Args:
            db (AsyncSession): The async database session.
            page (PositiveInt): The page number to retrieve (1-based).
            limit (PositiveInt): The maximum number of tools per page.
            name (str | None): Filter tools whose name contains this substring (case-insensitive).
            category_name (str | None): Filter tools by the name of their category (case-insensitive).
            is_active (bool | None): Filter tools by their active status.

        Returns:
            tuple[NonNegativeInt, Sequence[models.ToolModel]]: The total number of tools matching the filters, and the page of tools ordered by descending ID.
        """
        stmt = select(models.ToolModel)
        count_stmt = select(func.count(models.ToolModel.id))

        if name is not None:
            stmt = stmt.where(models.ToolModel.name.ilike(f"%{name}%"))
            count_stmt = count_stmt.where(models.ToolModel.name.ilike(f"%{name}%"))
        if category_name is not None:
            stmt = stmt.join(models.ToolModel.category).where(
                models.CategoryModel.name.ilike(f"%{category_name}%")
            )
            count_stmt = count_stmt.join(models.ToolModel.category).where(
                models.CategoryModel.name.ilike(f"%{category_name}%")
            )
        if is_active is not None:
            stmt = stmt.where(models.ToolModel.is_active == is_active)
            count_stmt = count_stmt.where(models.ToolModel.is_active == is_active)

        item_count = (await db.execute(count_stmt)).scalar()
        item_count = item_count if item_count is not None else 0

        stmt = stmt.order_by(models.ToolModel.id.desc())

        offset = (page - 1) * limit
        stmt = stmt.offset(offset).limit(limit)

        tools = (await db.execute(stmt)).scalars().all()
        return item_count, tools

    @staticmethod
    async def update(
        db: AsyncSession, id: PositiveInt, data: schemas.ToolUpdateSchema
    ) -> models.ToolModel:
        """
        Update an existing tool with the provided fields.

        Only fields that are not None in `data` are applied to the tool.

        Args:
            db (AsyncSession): The async database session.
            id (PositiveInt): The ID of the tool to update.
            data (schemas.ToolUpdateSchema): The fields to update.

        Returns:
            models.ToolModel: The updated tool.

        Raises:
            HTTPException: 404 if no tool with the given ID exists;
                409 if the update violates a uniqueness constraint.
        """
        stmt = select(models.ToolModel).where(models.ToolModel.id == id)
        tool = (await db.execute(stmt)).scalar_one_or_none()

        if tool is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Tool not found."
            )

        update_data = data.model_dump(exclude_none=True)

        for field, value in update_data.items():
            setattr(tool, field, value)

        db.add(tool)

        try:
            await db.commit()
        except IntegrityError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Tool already exists.",
            )

        await db.refresh(tool)

        return tool

    @staticmethod
    async def delete(db: AsyncSession, id: PositiveInt) -> None:
        """
        Delete a tool by ID.

        Args:
            db (AsyncSession): The async database session.
            id (PositiveInt): The ID of the tool to delete.

        Raises:
            HTTPException: 404 if no tool with the given ID exists;
                500 if the deletion fails at the database level.
        """
        stmt = select(models.ToolModel).where(models.ToolModel.id == id)
        tool = (await db.execute(stmt)).scalar_one_or_none()

        if tool is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Tool not found."
            )

        await db.delete(tool)

        try:
            await db.commit()
        except SQLAlchemyError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete tool.",
            )
