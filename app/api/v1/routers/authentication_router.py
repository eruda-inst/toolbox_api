from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from .. import schemas, db, services, models, deps
from fastapi import APIRouter, Body, Depends, status

authentication_router = APIRouter(tags=["Autenticação"], prefix="/autenticacao")


db_dep = Annotated[AsyncSession, Depends(db.get_db)]
current_user_dep = Annotated[models.User, Depends(deps.get_current_user)]


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


@authentication_router.get(path="/mim", summary="Usuário atual")
async def me(current_user: current_user_dep) -> schemas.UserOut:
    """
    Usuário atual logado
    """
    return schemas.UserOut.model_validate(current_user)


@authentication_router.post(
    path="/logout",
    summary="Invalida refresh token",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def logout(
    db: db_dep,
    current_user: current_user_dep,
    logout_req: Annotated[
        schemas.LogoutReq, Body(description="Refresh token a ser invalidado")
    ],
) -> None:
    """
    Invalida o refresh token fornecido, impedindo sua reutilização. Requer autenticação (token de acesso válido) e o token deve pertencer ao usuário logado
    """
    await services.AuthenticationService.logout(
        db=db, refresh_token=logout_req.refresh_token, current_user=current_user
    )
