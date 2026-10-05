from collections.abc import Sequence

from fastapi import HTTPException, status
from pydantic import NonNegativeInt, PositiveInt
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
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
        user_id: PositiveInt | None,
    ) -> tuple[NonNegativeInt, Sequence[models.PermissionModel]]:
        """
        Retrieve a paginated list of permissions, optionally filtered by the given criteria.

        Args:
            db (AsyncSession): The async database session.
            page (PositiveInt): The page number to retrieve (1-based).
            limit (PositiveInt): The maximum number of permissions per page.
            code (str | None): Filter permissions whose code contains this substring (case-insensitive).
            is_active (bool | None): Filter permissions by their active status.
            user_id (PositiveInt | None): Filter permissions by ID of the user.

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
        if user_id is not None:
            user_filter = models.PermissionModel.roles.any(
                models.RoleModel.users.any(models.UserModel.id == user_id)
            )
            stmt = stmt.where(user_filter)
            count_stmt = count_stmt.where(user_filter)

        item_count = (await db.execute(count_stmt)).scalar()
        item_count = item_count if item_count is not None else 0

        stmt = stmt.order_by(models.PermissionModel.id.desc())

        offset = (page - 1) * limit
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
                409 if the update violates a uniqueness constraint (e.g., duplicate code).
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

    @staticmethod
    async def delete(db: AsyncSession, id: PositiveInt) -> None:
        """
        Delete a permission by ID.

        Args:
            db (AsyncSession): The async database session.
            id (PositiveInt): The ID of the permission to delete.

        Raises:
            HTTPException: 404 if no permission with the given ID exists;
                500 if the deletion fails at the database level.
        """
        stmt = select(models.PermissionModel).where(models.PermissionModel.id == id)
        permission = (await db.execute(stmt)).scalar_one_or_none()

        if permission is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Permission not found."
            )

        await db.delete(permission)

        try:
            await db.commit()
        except SQLAlchemyError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete permission.",
            )
