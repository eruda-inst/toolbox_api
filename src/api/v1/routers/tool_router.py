from typing import Annotated

from fastapi import APIRouter, status
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
