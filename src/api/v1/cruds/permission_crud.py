from collections.abc import Sequence

from fastapi import HTTPException, status
from pydantic import NonNegativeInt, PositiveInt
from sqlalchemy import func, select
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
            HTTPException: 409 if a permission with the same unique field (e.g., code) already exists.
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

    @staticmethod
    async def read_all_by(
        db: AsyncSession,
        page: PositiveInt,
        limit: PositiveInt,
        code: str | None,
        is_active: bool | None,
    ) -> tuple[NonNegativeInt, Sequence[models.PermissionModel]]:
        """
        Retrieve a paginated list of permissions, optionally filtered by the given criteria.

        Args:
            db (AsyncSession): The async database session.
            page (PositiveInt): The page number to retrieve (1-based).
            limit (PositiveInt): The maximum number of permissions per page.
            name (str | None): Filter permissions whose name contains this substring (case-insensitive).
            is_active (bool | None): Filter permissions by their active status.

        Returns:
            tuple[NonNegativeInt, Sequence[models.PermissionModel]]: The total number of permissions matching the filters, and the page of permissions ordered by descending ID.
        """
        stmt = select(models.PermissionModel)
        count_stmt = select(func.count(models.PermissionModel.id))

        if code is not None:
            stmt = stmt.where(models.PermissionModel.code.ilike(f"%{code}%"))
            count_stmt = count_stmt.where(
                models.PermissionModel.code.ilike(f"%{code}%")
            )
        if is_active is not None:
            stmt = stmt.where(models.PermissionModel.is_active == is_active)
            count_stmt = count_stmt.where(models.PermissionModel.is_active == is_active)

        item_count = (await db.execute(count_stmt)).scalar()
        item_count = item_count if item_count is not None else 0

        stmt = stmt.order_by(models.PermissionModel.id.desc())

        offset = (page - 1) * item_count
        stmt = stmt.offset(offset).limit(limit)

        permissions = (await db.execute(stmt)).scalars().all()
        return item_count, permissions

    @staticmethod
    async def update(
        db: AsyncSession, id: PositiveInt, data: schemas.PermissionUpdateSchema
    ) -> models.PermissionModel:
        """
        Update an existing permission with the provided fields.

        Only fields that are not None in `data` are applied to the permission.

        Args:
            db (AsyncSession): The async database session.
            id (PositiveInt): The ID of the permission to update.
            data (schemas.PermissionUpdateSchema): The fields to update.

        Returns:
            models.PermissionModel: The updated permission.

        Raises:
            HTTPException: 404 if no permission with the given ID exists;
                409 if the update violates a uniqueness constraint (e.g., duplicate name).
        """
        stmt = select(models.PermissionModel).where(models.PermissionModel.id == id)
        permission = (await db.execute(stmt)).scalar_one_or_none()

        if permission is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Permission not found."
            )

        update_data = data.model_dump(exclude_none=True)

        for field, value in update_data.items():
            setattr(permission, field, value)

        db.add(permission)

        try:
            await db.commit()
        except IntegrityError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Permission already exists.",
            )

        await db.refresh(permission)

        return permission
