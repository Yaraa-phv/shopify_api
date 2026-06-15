from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user
from app.db.session import get_db
from app.models import User
from app.schemas.order import OrderCreate, OrderOut
from app.services.order_service import create_order_from_cart, get_order, list_orders

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.get("", response_model=list[OrderOut])
async def get_orders(current_user: User = Depends(get_current_active_user), db: AsyncSession = Depends(get_db)):
    return await list_orders(db, current_user.id)


@router.get("/{order_id}", response_model=OrderOut)
async def get_order_by_id(
    order_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    return await get_order(db, current_user.id, order_id)


@router.post("", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
async def checkout(
    data: OrderCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    return await create_order_from_cart(db, current_user.id, data)
