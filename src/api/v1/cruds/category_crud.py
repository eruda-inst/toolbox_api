from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from .. import models, schemas


class CategoryCRUD:
    @staticmethod
    async def create(
        db: AsyncSession, data: schemas.CategoryInSchema
    ) -> models.CategoryModel:
        """
        Summary.

        Args:
            db (AsyncSession): Description.
            data (schemas.CategoryInSchema): Description.

        Returns:
            models.CategoryModel: Description.

        Raises:
            HTTPException: Description.
        """
        category_data = data.model_dump()
        new_category = models.CategoryModel(**category_data)

        db.add(new_category)

        try:
            await db.commit()
        except IntegrityError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Category already exists"
            )

        await db.refresh(new_category)

        return new_category
