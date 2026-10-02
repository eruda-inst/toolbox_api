from typing import Annotated

from fastapi import APIRouter, Query, status
from fastapi.params import Body, Depends

from .. import cruds, dependencies, schemas, utilities

permission_router = APIRouter(prefix="/permissions", tags=["Permissions"])


@permission_router.post(
    path="/", status_code=status.HTTP_201_CREATED, summary="Create a new permission."
)
async def create(
    db: utilities.DatabaseDependency,
    _: Annotated[
        None, Depends(dependencies.has_permission("toolbox:permissoes:criar"))
    ],
    data: Annotated[
        schemas.PermissionInSchema, Body(description="Data of the permission.")
    ],
) -> schemas.PermissionOutSchema:
    """
    Create a new permission with the provided data and return the created record.

    Persists a new permission to the database using the supplied input schema and returns the newly created permission, including its generated ID.
    """
    created_permission = await cruds.PermissionCRUD.create(db=db, data=data)
    return schemas.PermissionOutSchema.model_validate(created_permission)


@permission_router.get(
    path="/", summary="List permissions with filters and pagination."
)
async def read_all_by(
    db: utilities.DatabaseDependency,
    _: Annotated[None, Depends(dependencies.has_permission("toolbox:permissoes:ver"))],
    page: utilities.PageQueryParameter = 1,
    limit: utilities.LimitQueryParameter = 10,
    code: Annotated[
        str | None,
        Query(description="Partial filter by code.", examples=["tool:resource:action"]),
    ] = None,
    is_active: Annotated[
        bool | None, Query(description="Filter by status.", examples=[True])
    ] = None,
) -> schemas.ListOutSchema[schemas.PermissionOutSchema]:
    """
    Retrieve a paginated list of permissions, optionally filtered.

    Supports partial matching on `code`, and exact matching on `is_active`. Results are paginated using `page` and `limit`, and the response includes metadata with the total item count.
    """
    item_count, permissions = await cruds.PermissionCRUD.read_all_by(
        db=db, page=page, limit=limit, code=code, is_active=is_active
    )
    return schemas.ListOutSchema[schemas.PermissionOutSchema](
        data=[
            schemas.PermissionOutSchema.model_validate(permission)
            for permission in permissions
        ],
        meta=schemas.MetaOutSchema(page=page, item_count=item_count, limit=limit),
    )
