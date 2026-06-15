import secrets
from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.models import Cart, CartItem, Order, OrderItem, Product, ProductVariant
from app.schemas.order import OrderCreate
from app.services.cart_service import _get_or_create_cart, _line_price, clear_cart


def _generate_order_number() -> str:
    return f"ORD-{secrets.token_hex(4).upper()}"


async def list_orders(db: AsyncSession, user_id: UUID) -> list[Order]:
    result = await db.execute(
        select(Order)
        .options(
            selectinload(Order.items).selectinload(OrderItem.product).selectinload(Product.images),
            selectinload(Order.items).selectinload(OrderItem.variant),
        )
        .where(Order.user_id == user_id)
        .order_by(Order.created_at.desc())
    )
    return list(result.scalars().unique().all())


async def get_order(db: AsyncSession, user_id: UUID, order_id: UUID) -> Order:
    result = await db.execute(
        select(Order)
        .options(
            selectinload(Order.items).selectinload(OrderItem.product).selectinload(Product.images),
            selectinload(Order.items).selectinload(OrderItem.variant),
        )
        .where(Order.id == order_id, Order.user_id == user_id)
    )
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return order


async def create_order_from_cart(db: AsyncSession, user_id: UUID, data: OrderCreate) -> Order:
    cart = await _get_or_create_cart(db, user_id)
    if not cart.items:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cart is empty")

    subtotal = Decimal("0")
    for item in cart.items:
        product = item.product
        variant = item.variant
        if not product or product.status != "active":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A product in your cart is unavailable")
        if variant and variant.stock < item.quantity:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Insufficient stock for {product.title}")
        if not variant and product.inventory < item.quantity:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Insufficient stock for {product.title}")
        subtotal += _line_price(product, variant, item.quantity)

    shipping_cost = data.shipping_cost if data.shipping_cost is not None else Decimal(str(settings.DEFAULT_SHIPPING_COST))
    total = subtotal + shipping_cost

    order = Order(
        order_number=_generate_order_number(),
        user_id=user_id,
        status="pending",
        payment_status="unpaid",
        subtotal=subtotal,
        shipping_cost=shipping_cost,
        total=total,
    )
    db.add(order)
    await db.flush()

    for item in cart.items:
        unit_price = item.product.price + (item.variant.price_modifier if item.variant else Decimal("0"))
        db.add(
            OrderItem(
                order_id=order.id,
                product_id=item.product_id,
                variant_id=item.variant_id,
                quantity=item.quantity,
                unit_price=unit_price,
                total_price=unit_price * item.quantity,
            )
        )
        if item.variant:
            item.variant.stock -= item.quantity
        else:
            item.product.inventory -= item.quantity

    await clear_cart(db, user_id)
    await db.flush()
    return await get_order(db, user_id, order.id)
