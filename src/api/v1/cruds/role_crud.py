from collections.abc import Sequence

from fastapi import HTTPException, status
from pydantic import NonNegativeInt, PositiveInt
from sqlalchemy import func, select
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

    @staticmethod
    async def read_all_by(
        db: AsyncSession,
        page: PositiveInt,
        limit: PositiveInt,
        code: str | None,
        title: str | None,
        is_active: bool | None,
    ) -> tuple[NonNegativeInt, Sequence[models.RoleModel]]:
        """
        Retrieve a paginated list of roles, optionally filtered by the given criteria.

        Args:
            db (AsyncSession): The async database session.
            page (PositiveInt): The page number to retrieve (1-based).
            limit (PositiveInt): The maximum number of roles per page.
            code (str | None): Filter roles whose code contains this substring (case-insensitive).
            title (str | None): Filter roles whose title contains this substring (case-insensitive).
            is_active (bool | None): Filter roles by their active status.

        Returns:
            tuple[NonNegativeInt, Sequence[models.RoleModel]]: The total number of roles matching the filters, and the page of roles ordered by descending ID.
        """
        stmt = select(models.RoleModel)
        count_stmt = select(func.count(models.RoleModel.id))

        if code is not None:
            stmt = stmt.where(models.RoleModel.code.ilike(f"%{code}%"))
            count_stmt = count_stmt.where(models.RoleModel.code.ilike(f"%{code}%"))
        if title is not None:
            stmt = stmt.where(models.RoleModel.title.ilike(f"%{title}%"))
            count_stmt = count_stmt.where(models.RoleModel.title.ilike(f"%{title}%"))
        if is_active is not None:
            stmt = stmt.where(models.RoleModel.is_active == is_active)
            count_stmt = count_stmt.where(models.RoleModel.is_active == is_active)

        item_count = (await db.execute(count_stmt)).scalar()
        item_count = item_count if item_count is not None else 0

        stmt = stmt.order_by(models.RoleModel.id.desc())

        offset = (page - 1) * item_count
        stmt = stmt.offset(offset).limit(limit)

        roles = (await db.execute(stmt)).scalars().all()
        return item_count, roles

    @staticmethod
    async def update(
        db: AsyncSession, id: PositiveInt, data: schemas.RoleUpdateSchema
    ) -> models.RoleModel:
        """
        Update an existing role with the provided fields.

        Only fields that are not None in `data` are applied to the role.

        Args:
            db (AsyncSession): The async database session.
            id (PositiveInt): The ID of the role to update.
            data (schemas.RoleUpdateSchema): The fields to update.

        Returns:
            models.RoleModel: The updated role.

        Raises:
            HTTPException: 404 if no role with the given ID exists;
                409 if the update violates a uniqueness constraint (e.g., duplicate code).
        """
        stmt = select(models.RoleModel).where(models.RoleModel.id == id)
        role = (await db.execute(stmt)).scalar_one_or_none()

        if role is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Role not found."
            )

        update_data = data.model_dump(exclude_none=True)

        for field, value in update_data.items():
            setattr(role, field, value)

        db.add(role)

        try:
            await db.commit()
        except IntegrityError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Role already exists.",
            )

        await db.refresh(role)

        return role
