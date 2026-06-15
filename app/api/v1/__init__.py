from fastapi import APIRouter

from app.api.v1 import auth, cart, collections, orders, products, users

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(products.router)
api_router.include_router(collections.router)
api_router.include_router(cart.router)
api_router.include_router(orders.router)
