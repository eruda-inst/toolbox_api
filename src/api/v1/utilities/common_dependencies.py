from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .. import database

DatabaseDependency = Annotated[AsyncSession, Depends(database.get_db)]
