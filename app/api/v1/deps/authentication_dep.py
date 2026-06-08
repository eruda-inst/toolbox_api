from fastapi import Depends
from typing import Annotated
from .. import models, db, services
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

db_dep = Annotated[AsyncSession, Depends(db.get_db)]
creds_dep = Annotated[HTTPAuthorizationCredentials, Depends(security)]


async def get_current_user(db: db_dep, creds: creds_dep) -> models.User:
    access_token = creds.credentials
    user = await services.AuthenticationService.verify_access_token(
        db=db, access_token=access_token
    )
    return user
