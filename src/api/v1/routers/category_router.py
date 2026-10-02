from typing import Annotated

from fastapi import APIRouter, status
from fastapi.params import Body, Depends

from .. import cruds, dependencies, schemas, utilities

category_router = APIRouter(prefix="/categories", tags=["Categories"])


@category_router.post(
    path="/", status_code=status.HTTP_201_CREATED, summary="Create a new category."
)
async def create(
    db: utilities.DatabaseDependency,
    _: Annotated[
        None, Depends(dependencies.has_permission("toolbox:categorias:criar"))
    ],
    data: Annotated[
        schemas.CategoryInSchema, Body(description="Data of the category.")
    ],
) -> schemas.CategoryOutSchema:
    """
    Create a new category with the provided data and return the created record.

    Persists a new category to the database using the supplied input schema and returns the newly created category, including its generated ID.
    """
    created_category = await cruds.CategoryCRUD.create(db=db, data=data)
    return schemas.CategoryOutSchema.model_validate(created_category)
