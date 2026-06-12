from . import routers
from fastapi import APIRouter

api_v1_router = APIRouter(prefix="/api/v1")

api_v1_router.include_router(router=routers.authentication_router)
api_v1_router.include_router(router=routers.perm_router)
api_v1_router.include_router(router=routers.reset_password_router)
