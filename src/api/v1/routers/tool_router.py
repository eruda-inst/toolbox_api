from typing import Annotated

from fastapi import APIRouter, Path, Query, status
from fastapi.params import Body, Depends

from .. import cruds, dependencies, schemas, utilities

tool_router = APIRouter(prefix="/tools", tags=["Tools"])


@tool_router.post(
    path="/", status_code=status.HTTP_201_CREATED, summary="Create a new tool."
)
async def create(
    db: utilities.DatabaseDependency,
    _: Annotated[
        None, Depends(dependencies.has_permission("toolbox:ferramentas:criar"))
    ],
    data: Annotated[schemas.ToolInSchema, Body(description="Data of the tool.")],
) -> schemas.ToolOutSchema:
    """
    Create a new tool with the provided data and return the created record.

    Persists a new tool to the database using the supplied input schema and returns the newly created tool, including its generated ID.
    """
    created_tool = await cruds.ToolCRUD.create(db=db, data=data)
    return schemas.ToolOutSchema.model_validate(created_tool)


@tool_router.get(path="/", summary="List tools with filters and pagination.")
async def read_all_by(
    db: utilities.DatabaseDependency,
    _: Annotated[None, Depends(dependencies.has_permission("toolbox:ferramentas:ver"))],
    page: utilities.PageQueryParameter = 1,
    limit: utilities.LimitQueryParameter = 10,
    name: Annotated[
        str | None,
        Query(description="Partial filter by name.", examples=["Toolbox"]),
    ] = None,
    category_name: Annotated[
        str | None,
        Query(
            description="Partial filter by the name of the category.",
            examples=["My Category"],
        ),
    ] = None,
    is_active: Annotated[
        bool | None, Query(description="Filter by status.", examples=[True])
    ] = None,
) -> schemas.ListOutSchema[schemas.ToolOutSchema]:
    """
    Retrieve a paginated list of tools, optionally filtered.

    Supports partial matching on `name` and `category_name`, and exact matching on `is_active`. Results are paginated using `page` and `limit`, and the response includes metadata with the total item count.
    """
    item_count, tools = await cruds.ToolCRUD.read_all_by(
        db=db,
        page=page,
        limit=limit,
        name=name,
        category_name=category_name,
        is_active=is_active,
    )
    return schemas.ListOutSchema[schemas.ToolOutSchema](
        data=[schemas.ToolOutSchema.model_validate(tool) for tool in tools],
        meta=schemas.MetaOutSchema(page=page, item_count=item_count, limit=limit),
    )


@tool_router.patch(path="/id/{id}", summary="Update an existing tool.")
async def update(
    db: utilities.DatabaseDependency,
    _: Annotated[
        None, Depends(dependencies.has_permission("toolbox:ferramentas:editar"))
    ],
    id: Annotated[int, Path(ge=1, description="ID of the tool.", examples=[1])],
    data: Annotated[schemas.ToolUpdateSchema, Body(description="Data of the tool.")],
) -> schemas.ToolOutSchema:
    """
    Partially update a tool identified by its ID.

    Applies the provided fields from the update schema to the tool with the given ID and returns the updated tool record.
    """
    updated_tool = await cruds.ToolCRUD.update(db=db, id=id, data=data)
    return schemas.ToolOutSchema.model_validate(updated_tool)


@tool_router.delete(
    path="/id/{id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a tool."
)
async def delete(
    db: utilities.DatabaseDependency,
    _: Annotated[None, Depends(dependencies.has_permission("toolbox:perfis:excluir"))],
    id: Annotated[int, Path(ge=1, description="ID of the tool.", examples=[1])],
) -> None:
    """
    Delete a tool identified by its ID.

    Removes the tool with the given ID from the database. Returns no content on success (HTTP 204).
    """
    await cruds.ToolCRUD.delete(db=db, id=id)
