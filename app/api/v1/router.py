from fastapi import APIRouter
from app.api.v1.endpoints import (
    ping,
    items,
    auth,
    agencies,
    listings,
    favorites,
    purchases,
    reviews,
)

api_router = APIRouter()
api_router.include_router(ping.router, tags=["ping"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(agencies.router, prefix="/agencies", tags=["agencies"])
api_router.include_router(items.router, prefix="/items", tags=["items"])
api_router.include_router(listings.router, prefix="/listings", tags=["listings"])
api_router.include_router(favorites.router, prefix="/favorites", tags=["favorites"])
api_router.include_router(purchases.router, prefix="/purchases", tags=["purchases"])
api_router.include_router(reviews.router, prefix="/reviews", tags=["reviews"])
