from collections.abc import Sequence

from fastapi import HTTPException, status
from pydantic import EmailStr, NonNegativeInt, PositiveInt
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from .. import models, schemas


class UserCRUD:
    @staticmethod
    async def create(db: AsyncSession, data: schemas.UserInSchema) -> models.UserModel:
        """
        Create a new user.

        The password is already hashed by `UserInSchema`'s field validator,
        so it must not be hashed again here.

        Args:
            db (AsyncSession): The async database session.
            data (schemas.UserInSchema): The data for the new user.

        Returns:
            models.UserModel: The newly created user.

        Raises:
            HTTPException: 409 if a user with the same unique field (e.g., email) already exists.
        """
        user_data = data.model_dump()
        new_user = models.UserModel(**user_data)

        db.add(new_user)

        try:
            await db.commit()
        except IntegrityError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="User already exists."
            )

        await db.refresh(new_user)

        return new_user

    @staticmethod
    async def read_all_by(
        db: AsyncSession,
        page: PositiveInt,
        limit: PositiveInt,
        full_name: str | None,
        email: str | None,
        is_active: bool | None,
    ) -> tuple[NonNegativeInt, Sequence[models.UserModel]]:
        """
        Retrieve a paginated list of users, optionally filtered by the given criteria.

        Args:
            db (AsyncSession): The async database session.
            page (PositiveInt): The page number to retrieve (1-based).
            limit (PositiveInt): The maximum number of users per page.
            full_name (str | None): Filter users whose full name contains this substring (case-insensitive).
            email (str | None): Filter users whose email contains this substring (case-insensitive).
            is_active (bool | None): Filter users by their active status.

        Returns:
            tuple[NonNegativeInt, Sequence[models.UserModel]]: The total number of users matching the filters, and the page of users ordered by descending ID.
        """
        stmt = select(models.UserModel)
        count_stmt = select(func.count(models.UserModel.id))

        if full_name is not None:
            stmt = stmt.where(models.UserModel.full_name.ilike(f"%{full_name}%"))
            count_stmt = count_stmt.where(
                models.UserModel.full_name.ilike(f"%{full_name}%")
            )
        if email is not None:
            stmt = stmt.where(models.UserModel.email.ilike(f"%{email}%"))
            count_stmt = count_stmt.where(models.UserModel.email.ilike(f"%{email}%"))
        if is_active is not None:
            stmt = stmt.where(models.UserModel.is_active == is_active)
            count_stmt = count_stmt.where(models.UserModel.is_active == is_active)

        item_count = (await db.execute(count_stmt)).scalar()
        item_count = item_count if item_count is not None else 0

        stmt = stmt.order_by(models.UserModel.id.desc())

        offset = (page - 1) * limit
        stmt = stmt.offset(offset).limit(limit)

        users = (await db.execute(stmt)).scalars().all()
        return item_count, users

    @staticmethod
    async def read_by(
        db: AsyncSession, id: PositiveInt | None = None, email: EmailStr | None = None
    ) -> models.UserModel:
        """
        Retrieve a single user by ID or email.

        If both are provided, the ID takes precedence.

        Args:
            db (AsyncSession): The async database session.
            id (PositiveInt | None): The ID of the user to retrieve, optional (default: None).
            email (EmailStr | None): The email of the user to retrieve, optional (default: None).

        Returns:
            models.UserModel: The matching user.

        Raises:
            HTTPException: 400 if neither `id` nor `email` is provided;
                404 if no matching user exists.
        """
        if id is not None:
            stmt = select(models.UserModel).where(models.UserModel.id == id)
        elif email is not None:
            stmt = select(models.UserModel).where(models.UserModel.email == email)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Provide either user ID or E-mail.",
            )

        user = (await db.execute(stmt)).scalar_one_or_none()

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Incorrect credentials."
            )

        return user

    @staticmethod
    async def update(
        db: AsyncSession, id: PositiveInt, data: schemas.UserUpdateSchema
    ) -> models.UserModel:
        """
        Update an existing user with the provided fields.

        Only fields that are not None in `data` are applied to the user.
        Password, if provided, is already hashed by `UserUpdateSchema`'s
        field validator and must not be hashed again here.

        Args:
            db (AsyncSession): The async database session.
            id (PositiveInt): The ID of the user to update.
            data (schemas.UserUpdateSchema): The fields to update.

        Returns:
            models.UserModel: The updated user.

        Raises:
            HTTPException: 404 if no user with the given ID exists;
                409 if the update violates a uniqueness constraint (e.g., duplicate email).
        """
        stmt = select(models.UserModel).where(models.UserModel.id == id)
        user = (await db.execute(stmt)).scalar_one_or_none()

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found."
            )

        update_data = data.model_dump(exclude_none=True)

        for field, value in update_data.items():
            setattr(user, field, value)

        db.add(user)

        try:
            await db.commit()
        except IntegrityError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="User already exists."
            )

        await db.refresh(user)

        return user

    @staticmethod
    async def delete(db: AsyncSession, id: PositiveInt) -> None:
        """
        Delete a user by ID.

        Args:
            db (AsyncSession): The async database session.
            id (PositiveInt): The ID of the user to delete.

        Raises:
            HTTPException: 404 if no user with the given ID exists;
                500 if the deletion fails at the database level.
        """
        stmt = select(models.UserModel).where(models.UserModel.id == id)
        user = (await db.execute(stmt)).scalar_one_or_none()

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found."
            )

        await db.delete(user)

        try:
            await db.commit()
        except SQLAlchemyError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete user.",
            )
