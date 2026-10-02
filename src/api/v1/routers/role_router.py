from typing import Annotated

from fastapi import APIRouter, Path, Query, status
from fastapi.params import Body, Depends

from .. import cruds, dependencies, schemas, utilities

role_router = APIRouter(prefix="/roles", tags=["Roles"])


@role_router.post(
    path="/", status_code=status.HTTP_201_CREATED, summary="Create a new role."
)
async def create(
    db: utilities.DatabaseDependency,
    _: Annotated[None, Depends(dependencies.has_permission("toolbox:perfis:criar"))],
    data: Annotated[schemas.RoleInSchema, Body(description="Data of the role.")],
) -> schemas.RoleOutSchema:
    """
    Create a new role with the provided data and return the created record.

    Persists a new role to the database using the supplied input schema and returns the newly created role, including its generated ID.
    """
    created_role = await cruds.RoleCRUD.create(db=db, data=data)
    return schemas.RoleOutSchema.model_validate(created_role)


@role_router.get(path="/", summary="List roles with filters and pagination.")
async def read_all_by(
    db: utilities.DatabaseDependency,
    _: Annotated[None, Depends(dependencies.has_permission("toolbox:perfis:ver"))],
    page: utilities.PageQueryParameter = 1,
    limit: utilities.LimitQueryParameter = 10,
    code: Annotated[
        str | None,
        Query(description="Partial filter by code.", examples=["tool_resource_role"]),
    ] = None,
    title: Annotated[
        str | None,
        Query(description="Partial filter by title.", examples=["Manager of users"]),
    ] = None,
    is_active: Annotated[
        bool | None, Query(description="Filter by status.", examples=[True])
    ] = None,
) -> schemas.ListOutSchema[schemas.RoleOutSchema]:
    """
    Retrieve a paginated list of roles, optionally filtered.

    Supports partial matching on `code` and `title`, and exact matching on `is_active`. Results are paginated using `page` and `limit`, and the response includes metadata with the total item count.
    """
    item_count, roles = await cruds.RoleCRUD.read_all_by(
        db=db, page=page, limit=limit, code=code, title=title, is_active=is_active
    )
    return schemas.ListOutSchema[schemas.RoleOutSchema](
        data=[schemas.RoleOutSchema.model_validate(role) for role in roles],
        meta=schemas.MetaOutSchema(page=page, item_count=item_count, limit=limit),
    )


@role_router.patch(path="/id/{id}", summary="Update an existing role.")
async def update(
    db: utilities.DatabaseDependency,
    _: Annotated[None, Depends(dependencies.has_permission("toolbox:perfis:editar"))],
    id: Annotated[int, Path(ge=1, description="ID of the role.", examples=[1])],
    data: Annotated[schemas.RoleUpdateSchema, Body(description="Data of the role.")],
) -> schemas.RoleOutSchema:
    """
    Partially update a role identified by its ID.

    Applies the provided fields from the update schema to the role with the given ID and returns the updated role record.
    """
    updated_role = await cruds.RoleCRUD.update(db=db, id=id, data=data)
    return schemas.RoleOutSchema.model_validate(updated_role)


@role_router.delete(
    path="/id/{id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a role."
)
async def delete(
    db: utilities.DatabaseDependency,
    _: Annotated[None, Depends(dependencies.has_permission("toolbox:perfis:excluir"))],
    id: Annotated[int, Path(ge=1, description="ID of the role.", examples=[1])],
) -> None:
    """
    Delete a role identified by its ID.

    Removes the role with the given ID from the database. Returns no content on success (HTTP 204).
    """
    await cruds.RoleCRUD.delete(db=db, id=id)
