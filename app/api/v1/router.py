from fastapi import APIRouter
from app.api.v1.endpoints import (
    inventory,
    ping,
    items,
    auth,
    agencies,
    listings,
    favorites,
    purchases,
    reviews,
    car_models,
    admin_reports,
    admin_users,
    admin_favorites,
    admin_reviews,
    admin_purchases,
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
api_router.include_router(inventory.router, prefix="/inventory", tags=["Inventory"])
api_router.include_router(car_models.router, prefix="/car-models", tags=["car-models"])
api_router.include_router(
    admin_reports.router, prefix="/admin/reports", tags=["admin-reports"]
)
api_router.include_router(
    admin_users.router, prefix="/admin/users", tags=["admin-users"]
)
api_router.include_router(
    admin_favorites.router, prefix="/admin/favorites", tags=["admin-favorites"]
)
api_router.include_router(
    admin_reviews.router, prefix="/admin/reviews", tags=["admin-reviews"]
)
api_router.include_router(
    admin_purchases.router, prefix="/admin/purchases", tags=["admin-purchases"]
)
