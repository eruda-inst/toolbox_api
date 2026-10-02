from typing import Annotated

from fastapi import APIRouter, Body, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from .. import database, dependencies, models, schemas, services

authentication_router = APIRouter(prefix="/authentication", tags=["Authentication"])

DatabaseDependency = Annotated[AsyncSession, Depends(database.get_db)]
CurrentUserDependency = Annotated[
    models.UserModel, Depends(dependencies.get_current_user)
]


@authentication_router.get(path="/me", summary="Get current user profile.")
async def me(current_user: CurrentUserDependency) -> schemas.UserOutSchema:
    """
    Return the profile information of the currently authenticated user.
    """
    return schemas.UserOutSchema.model_validate(current_user)


@authentication_router.post(
    path="/login", summary="Authenticate user and issue tokens."
)
async def login(
    db: DatabaseDependency,
    email: Annotated[
        str,
        Body(
            description="Registered e-mail address of the user.",
            examples=["email@email.com"],
        ),
    ],
    password: Annotated[
        str,
        Body(
            description="Plain-text password associated with the e-mail address.",
            examples=["12345678"],
        ),
    ],
) -> schemas.TokenOutSchema:
    """
    Validate the provided credentials and return an access/refresh token pair.
    """
    return await services.AuthenticationService.login(
        db=db, email=email, password=password
    )


@authentication_router.post(
    path="/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Invalidate current session tokens.",
)
async def logout(db: DatabaseDependency, current_user: CurrentUserDependency) -> None:
    """
    Increment the token version of the user so all previously issued tokens become invalid.
    """
    current_user.token_version += 1  # type: ignore
    await db.commit()


@authentication_router.post(
    path="/refresh-token",
    summary="Exchange refresh token for a new access/refresh token pair.",
)
async def refresh(
    db: DatabaseDependency,
    refresh_token: Annotated[
        str,
        Body(
            embed=True,
            description="Valid refresh token previously issued by the login endpoint.",
            examples=["eyJ..."],
        ),
    ],
) -> schemas.TokenOutSchema:
    """
    Verify the refresh token and issue a fresh access/refresh token pair.
    """
    return await services.AuthenticationService.refresh_token(
        db=db, refresh_token=refresh_token
    )
