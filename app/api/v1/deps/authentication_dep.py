from fastapi import Depends
from .. import models, db, services
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()


async def get_current_user(
    db: AsyncSession = Depends(db.get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> models.User:
    access_token = credentials.credentials
    user = await services.AuthenticationService.verify_access_token(
        db=db, access_token=access_token
    )
    return user
