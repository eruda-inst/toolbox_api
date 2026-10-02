from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from .. import models, schemas


class RoleCRUD:
    @staticmethod
    async def create(db: AsyncSession, data: schemas.RoleInSchema) -> models.RoleModel:
        """
        Create a new role.

        Args:
            db (AsyncSession): The async database session.
            data (schemas.RoleInSchema): The data for the new role.

        Returns:
            models.RoleModel: The newly created role.

        Raises:
            HTTPException: 409 if a role with the same unique field (e.g., code) already exists.
        """
        role_data = data.model_dump()
        new_role = models.RoleModel(**role_data)

        db.add(new_role)

        try:
            await db.commit()
        except IntegrityError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Role already exists."
            )

        await db.refresh(new_role)

        return new_role
