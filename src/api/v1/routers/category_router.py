from typing import Annotated

from fastapi import APIRouter, Path, Query, status
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


@category_router.get(path="/", summary="List categories with filters and pagination.")
async def read_all_by(
    db: utilities.DatabaseDependency,
    _: Annotated[None, Depends(dependencies.has_permission("toolbox:categorias:ver"))],
    page: utilities.PageQueryParameter = 1,
    limit: utilities.LimitQueryParameter = 10,
    name: Annotated[
        str | None,
        Query(description="Partial filter by name.", examples=["My Category"]),
    ] = None,
    is_active: Annotated[
        bool | None,
        Query(description="Filter by status.", examples=[True]),
    ] = None,
) -> schemas.ListOutSchema[schemas.CategoryOutSchema]:
    """
    Retrieve a paginated list of categories, optionally filtered.

    Supports partial matching on `name`, and exact matching on `is_active`. Results are paginated using `page` and `limit`, and the response includes metadata with the total item count.
    """
    item_count, categories = await cruds.CategoryCRUD.read_all_by(
        db=db,
        page=page,
        limit=limit,
        name=name,
        is_active=is_active,
    )
    return schemas.ListOutSchema[schemas.CategoryOutSchema](
        data=[
            schemas.CategoryOutSchema.model_validate(category)
            for category in categories
        ],
        meta=schemas.MetaOutSchema(page=page, item_count=item_count, limit=limit),
    )


@category_router.patch(path="/id/{id}", summary="Update an existing category.")
async def update(
    db: utilities.DatabaseDependency,
    _: Annotated[
        None, Depends(dependencies.has_permission("toolbox:categorias:editar"))
    ],
    id: Annotated[int, Path(ge=1, description="ID of the category.", examples=[1])],
    data: Annotated[
        schemas.CategoryUpdateSchema, Body(description="Data of the category.")
    ],
) -> schemas.CategoryOutSchema:
    """
    Partially update a category identified by its ID.

    Applies the provided fields from the update schema to the category with the given ID and returns the updated category record.
    """
    updated_category = await cruds.CategoryCRUD.update(db=db, id=id, data=data)
    return schemas.CategoryOutSchema.model_validate(updated_category)


@category_router.delete(
    path="/id/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a category.",
)
async def delete(
    db: utilities.DatabaseDependency,
    _: Annotated[
        None, Depends(dependencies.has_permission("toolbox:categorias:excluir"))
    ],
    id: Annotated[int, Path(ge=1, description="ID of the category.", examples=[1])],
) -> None:
    """
    Delete a category identified by its ID.

    Removes the category with the given ID from the database. Returns no content on success (HTTP 204).
    """
    await cruds.CategoryCRUD.delete(db=db, id=id)
