from collections.abc import Sequence

from fastapi import HTTPException, status
from pydantic import NonNegativeInt, PositiveInt
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from .. import models, schemas


class CategoryCRUD:
    @staticmethod
    async def create(
        db: AsyncSession, data: schemas.CategoryInSchema
    ) -> models.CategoryModel:
        """
        Create a new category.

        Args:
            db (AsyncSession): The async database session.
            data (schemas.CategoryInSchema): The data for the new category.

        Returns:
            models.CategoryModel: The newly created category.

        Raises:
            HTTPException: 409 if a category with the same unique field (e.g., name) already exists.
        """
        category_data = data.model_dump()
        new_category = models.CategoryModel(**category_data)

        db.add(new_category)

        try:
            await db.commit()
        except IntegrityError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Category already exists."
            )

        await db.refresh(new_category)

        return new_category

    @staticmethod
    async def read_all_by(
        db: AsyncSession,
        page: PositiveInt,
        limit: PositiveInt,
        name: str | None,
        is_active: bool | None,
    ) -> tuple[NonNegativeInt, Sequence[models.CategoryModel]]:
        """
        Retrieve a paginated list of categories, optionally filtered by the given criteria.

        Args:
            db (AsyncSession): The async database session.
            page (PositiveInt): The page number to retrieve (1-based).
            limit (PositiveInt): The maximum number of categories per page.
            name (str | None): Filter categories whose name contains this substring (case-insensitive).
            is_active (bool | None): Filter categories by their active status.

        Returns:
            tuple[NonNegativeInt, Sequence[models.CategoryModel]]: The total number of categories matching the filters, and the page of categories ordered by descending ID.
        """
        stmt = select(models.CategoryModel)
        count_stmt = select(func.count(models.CategoryModel.id))

        if name is not None:
            stmt = stmt.where(models.CategoryModel.name.ilike(f"%{name}%"))
            count_stmt = count_stmt.where(models.CategoryModel.name.ilike(f"%{name}%"))
        if is_active is not None:
            stmt = stmt.where(models.CategoryModel.is_active == is_active)
            count_stmt = count_stmt.where(models.CategoryModel.is_active == is_active)

        item_count = (await db.execute(count_stmt)).scalar()
        item_count = item_count if item_count is not None else 0

        stmt = stmt.order_by(models.CategoryModel.id.desc())

        offset = (page - 1) * item_count
        stmt = stmt.offset(offset).limit(limit)

        categories = (await db.execute(stmt)).scalars().all()
        return item_count, categories

    @staticmethod
    async def update(
        db: AsyncSession, id: PositiveInt, data: schemas.CategoryUpdateSchema
    ) -> models.CategoryModel:
        """
        Update an existing category with the provided fields.

        Only fields that are not None in `data` are applied to the category.

        Args:
            db (AsyncSession): The async database session.
            id (PositiveInt): The ID of the category to update.
            data (schemas.CategoryUpdateSchema): The fields to update.

        Returns:
            models.CategoryModel: The updated category.

        Raises:
            HTTPException: 404 if no category with the given ID exists;
                409 if the update violates a uniqueness constraint (e.g., duplicate name).
        """
        stmt = select(models.CategoryModel).where(models.CategoryModel.id == id)
        category = (await db.execute(stmt)).scalar_one_or_none()

        if category is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Category not found."
            )

        update_data = data.model_dump(exclude_none=True)

        for field, value in update_data.items():
            setattr(category, field, value)

        db.add(category)

        try:
            await db.commit()
        except IntegrityError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Category already exists."
            )

        await db.refresh(category)

        return category

    @staticmethod
    async def delete(db: AsyncSession, id: PositiveInt) -> None:
        """
        Delete a category by ID.

        Args:
            db (AsyncSession): The async database session.
            id (PositiveInt): The ID of the category to delete.

        Raises:
            HTTPException: 404 if no category with the given ID exists;
                500 if the deletion fails at the database level.
        """
        stmt = select(models.CategoryModel).where(models.CategoryModel.id == id)
        category = (await db.execute(stmt)).scalar_one_or_none()

        if category is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Category not found."
            )

        await db.delete(category)

        try:
            await db.commit()
        except SQLAlchemyError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete category.",
            )
