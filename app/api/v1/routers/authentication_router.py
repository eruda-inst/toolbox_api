from typing import Annotated
from .. import schemas, db, services
from fastapi import APIRouter, Body, Depends
from sqlalchemy.ext.asyncio import AsyncSession

authentication_router = APIRouter(tags=["Autenticação"], prefix="/autenticacao")


db_dep = Annotated[AsyncSession, Depends(dependency=db.get_db)]


@authentication_router.post(path="/login", summary="Autenticação de usuário")
async def login(
    db: db_dep,
    credenciais: Annotated[
        schemas.LoginCreds, Body(description="Credenciais de login")
    ],
) -> schemas.AccessTokenOut:
    """
    Autenticação de usuário para acessar o sistema
    """
    return await services.AuthenticationService.login(creds=credenciais, db=db)


@authentication_router.post(path="/refresh-token", summary="Renova token de acesso")
async def refresh_token(
    db: db_dep,
    token_req: Annotated[
        schemas.RefreshTokenReq, Body(description="O refresh token atual do usuário")
    ],
) -> schemas.AccessTokenOut:
    """
    Renova token de acesso do usuário através de um Refresh Token válido. O token utilizado será invalidado para requisições futuras (Refresh Token Rotation)
    """
    return await services.AuthenticationService.refresh_token(
        db=db, token_req=token_req
    )
