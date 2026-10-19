from collections.abc import Awaitable, Callable
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select

from .. import models, services, utilities

bearer_security = HTTPBearer()


async def get_current_user(
    db: utilities.DatabaseDependency,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_security)],
) -> models.UserModel:
    """
    Resolve the authenticated user from the provided bearer access token.

    Args:
        db (utilities.DatabaseDependency): Database session dependency used to verify the access token.
        credentials (Annotated[HTTPAuthorizationCredentials, Depends(bearer_security)]): HTTP Bearer credentials containing the access token.

    Returns:
        models.UserModel: The user associated with a valid access token.

    Raises:
        HTTPException: If the access token is invalid or the user is not found (401 Unauthorized).
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
        db: utilities.DatabaseDependency,
        current_user: Annotated[models.UserModel, Depends(get_current_user)],
    ) -> None:
        """
        Ensure the current user has the required permission.

        Args:
            db (utilities.DatabaseDependency): Async database session used to query permissions.
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
