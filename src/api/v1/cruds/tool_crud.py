from collections.abc import Sequence

from fastapi import HTTPException, status
from pydantic import NonNegativeInt, PositiveInt
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from .. import models, schemas


class ToolCRUD:
    @staticmethod
    async def create(db: AsyncSession, data: schemas.ToolInSchema) -> models.ToolModel:
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

        offset = (page - 1) * item_count
        stmt = stmt.offset(offset).limit(limit)

        roles = (await db.execute(stmt)).scalars().all()
        return item_count, roles
