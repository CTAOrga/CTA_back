from fastapi import APIRouter
from app.api.v1.endpoints import ping, items

api_router = APIRouter()
api_router.include_router(ping.router, tags=["ping"])
api_router.include_router(items.router, prefix="/items", tags=["items"])
