from typing import Annotated

from fastapi import APIRouter, status
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
