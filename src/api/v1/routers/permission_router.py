from typing import Annotated

from fastapi import APIRouter, status
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
