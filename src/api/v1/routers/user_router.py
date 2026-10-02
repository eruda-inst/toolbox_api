from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from .. import cruds, database, dependencies, schemas, utilities

user_router = APIRouter(prefix="/users", tags=["Users"])

DatabaseDependency = Annotated[AsyncSession, Depends(database.get_db)]


@user_router.post(path="/", summary="Create a new user.")
async def create(
    db: DatabaseDependency,
    _: Annotated[None, Depends(dependencies.has_permission("toolbox:usuarios:criar"))],
    data: schemas.UserInSchema,
) -> schemas.UserOutSchema:
    """
    Create a new user with the provided data and return the created record.

    Persists a new user to the database using the supplied input schema
    and returns the newly created user, including its generated ID.
    """
    created_user = await cruds.UserCRUD.create(db=db, data=data)
    return schemas.UserOutSchema.model_validate(created_user)


@user_router.get(path="/", summary="List users with filters and pagination.")
async def get_all_by(
    db: DatabaseDependency,
    _: Annotated[None, Depends(dependencies.has_permission("toolbox:usuarios:ver"))],
    page: utilities.PageQueryParameter = 1,
    limit: utilities.LimitQueryParameter = 10,
    full_name: Annotated[
        str | None,
        Query(description="Partial filter by full name.", examples=["John Doe"]),
    ] = None,
    email: Annotated[
        str | None,
        Query(description="Partial filter by e-mail.", examples=["email@email.com"]),
    ] = None,
    is_active: Annotated[
        bool | None,
        Query(description="Filter by status.", examples=[True]),
    ] = None,
) -> schemas.ListOutSchema[schemas.UserOutSchema]:
    """
    Retrieve a paginated list of users, optionally filtered.

    Supports partial matching on `full_name` and `email`, and exact
    matching on `is_active`. Results are paginated using `page` and
    `limit`, and the response includes metadata with the total item count.
    """
    item_count, users = await cruds.UserCRUD.get_all_by(
        db=db,
        page=page,
        limit=limit,
        full_name=full_name,
        email=email,
        is_active=is_active,
    )
    return schemas.ListOutSchema[schemas.UserOutSchema](
        data=[schemas.UserOutSchema.model_validate(user) for user in users],
        meta=schemas.MetaOutSchema(page=page, item_count=item_count, limit=limit),
    )


@user_router.patch(path="/id/{id}", summary="Update an existing user.")
async def update(
    db: DatabaseDependency,
    _: Annotated[None, Depends(dependencies.has_permission("toolbox:usuarios:editar"))],
    id: Annotated[int, Path(ge=1, description="ID of the user.", examples=[1])],
    data: schemas.UserUpdateSchema,
) -> schemas.UserOutSchema:
    """
    Partially update a user identified by its ID.

    Applies the provided fields from the update schema to the user with
    the given ID and returns the updated user record.
    """
    updated_user = await cruds.UserCRUD.update(db=db, id=id, data=data)
    return schemas.UserOutSchema.model_validate(updated_user)


@user_router.delete(
    path="/id/{id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a user."
)
async def delete(
    db: DatabaseDependency,
    _: Annotated[
        None, Depends(dependencies.has_permission("toolbox:usuarios:excluir"))
    ],
    id: Annotated[int, Path(ge=1, description="ID of the user.", examples=[1])],
) -> None:
    """
    Delete a user identified by its ID.

    Removes the user with the given ID from the database. Returns no
    content on success (HTTP 204).
    """
    await cruds.UserCRUD.delete(db=db, id=id)
