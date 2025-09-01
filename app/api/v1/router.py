from fastapi import APIRouter
from app.api.v1.endpoints import ping, items, auth, agencies

api_router = APIRouter()
api_router.include_router(ping.router, tags=["ping"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(agencies.router, prefix="/agencies", tags=["agencies"])
api_router.include_router(items.router, prefix="/items", tags=["items"])
