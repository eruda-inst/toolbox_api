from fastapi import APIRouter

from . import routers

api_v1_router = APIRouter(prefix="/api/v1")


api_v1_router.include_router(router=routers.authentication_router)
api_v1_router.include_router(router=routers.category_router)
api_v1_router.include_router(router=routers.user_router)
