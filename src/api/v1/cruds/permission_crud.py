from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from .. import models, schemas


class PermissionCRUD:
    @staticmethod
    async def create(
        db: AsyncSession, data: schemas.PermissionInSchema
    ) -> models.PermissionModel:
        """
        Create a new permission.

        Args:
            db (AsyncSession): The async database session.
            data (schemas.PermissionInSchema): The data for the new permission.

        Returns:
            models.PermissionModel: The newly created permission.

        Raises:
            HTTPException: 409 if a permission with the same unique field (e.g., name) already exists.
        """
        permission_data = data.model_dump()
        new_permission = models.PermissionModel(**permission_data)

        db.add(new_permission)

        try:
            await db.commit()
        except IntegrityError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Permission already exists.",
            )

        await db.refresh(new_permission)

        return new_permission
