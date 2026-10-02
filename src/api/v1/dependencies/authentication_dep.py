from collections.abc import Awaitable, Callable
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .. import database, models, services

bearer_security = HTTPBearer()

DatabaseDependency = Annotated[AsyncSession, Depends(database.get_db)]


async def get_current_user(
    db: DatabaseDependency,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_security)],
) -> models.UserModel:
    """
    Summary.

    Args:
        db (Annotated[AsyncSession, Depends(db.get_db)]): Description.
        credentials (Annotated[HTTPAuthorizationCredentials, Depends(bearer_security)]): Description.

    Returns:
        models.UserModel: Description.

    Raises:
        HTTPException: Description.
    """
    user = await services.AuthenticationService.verify_access_token(
        db=db, access_token=credentials.credentials
    )
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is invalid or user is not found",
        )
    return user


def has_permission(
    required_permission: str,
) -> Callable[..., Awaitable[None]]:
    """
    Build a dependency that requires the current user to have a permission.

    Args:
        required_permission (str): Permission code that the current user must possess.

    Returns:
        Callable[..., Awaitable[None]]: An async dependency that enforces the required permission.
    """

    async def check_permission(
        db: DatabaseDependency,
        current_user: Annotated[models.UserModel, Depends(get_current_user)],
    ) -> None:
        """
        Ensure the current user has the required permission.

        Args:
            db (DatabaseDependency): Async database session used to query permissions.
            current_user (Annotated[models.UserModel, Depends(get_current_user)]): Authenticated user resolved by get_current_user.

        Raises:
            HTTPException: If the current user does not have the required permission.
        """
        stmt = (
            select(models.PermissionModel.id)
            .select_from(models.PermissionModel)
            .join(models.PermissionModel.roles)
            .join(models.RoleModel.users)
            .where(
                models.UserModel.id == current_user.id,
                models.PermissionModel.code == required_permission,
                models.PermissionModel.is_active.is_(True),
                models.RoleModel.is_active.is_(True),
            )
            .limit(1)
        )

        result = await db.execute(stmt)
        if result.scalar_one_or_none() is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required permission: '{required_permission}'.",
            )

    return check_permission
