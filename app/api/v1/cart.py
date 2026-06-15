from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user
from app.db.session import get_db
from app.models import User
from app.schemas.cart import CartItemCreate, CartItemUpdate, CartOut
from app.services.cart_service import add_cart_item, clear_cart, get_cart, remove_cart_item, update_cart_item

router = APIRouter(prefix="/cart", tags=["Cart"])


@router.get("", response_model=CartOut)
async def read_cart(current_user: User = Depends(get_current_active_user), db: AsyncSession = Depends(get_db)):
    return await get_cart(db, current_user.id)


@router.post("/items", response_model=CartOut, status_code=status.HTTP_201_CREATED)
async def add_item(
    data: CartItemCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    return await add_cart_item(db, current_user.id, data)


@router.put("/items/{item_id}", response_model=CartOut)
async def update_item(
    item_id: UUID,
    data: CartItemUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    return await update_cart_item(db, current_user.id, item_id, data)


@router.delete("/items/{item_id}", response_model=CartOut)
async def delete_item(
    item_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    return await remove_cart_item(db, current_user.id, item_id)


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def empty_cart(current_user: User = Depends(get_current_active_user), db: AsyncSession = Depends(get_db)):
    await clear_cart(db, current_user.id)
