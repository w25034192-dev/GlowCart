from fastapi import APIRouter

from app.api.v1 import (
    addresses,
    analytics,
    auth,
    cart_wishlist,
    catalog,
    inventory,
    orders,
    payments,
    promotions,
    reviews,
    super_admin,
    support,
)

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(addresses.router)
api_router.include_router(catalog.router)
api_router.include_router(inventory.router)
api_router.include_router(cart_wishlist.router)
api_router.include_router(promotions.router)
api_router.include_router(orders.router)
api_router.include_router(payments.router)
api_router.include_router(reviews.router)
api_router.include_router(support.router)
api_router.include_router(analytics.router)
api_router.include_router(super_admin.router)
