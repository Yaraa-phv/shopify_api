from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Cart, CartItem, Product, ProductVariant
from app.schemas.cart import CartItemCreate, CartItemUpdate, CartOut


async def _get_or_create_cart(db: AsyncSession, user_id: UUID) -> Cart:
    result = await db.execute(
        select(Cart)
        .options(
            selectinload(Cart.items).selectinload(CartItem.product).selectinload(Product.images),
            selectinload(Cart.items).selectinload(CartItem.variant),
        )
        .where(Cart.user_id == user_id)
    )
    cart = result.scalar_one_or_none()
    if cart:
        return cart

    cart = Cart(user_id=user_id)
    db.add(cart)
    await db.flush()
    await db.refresh(cart)
    return cart


def _line_price(product: Product, variant: ProductVariant | None, quantity: int) -> Decimal:
    unit = product.price + (variant.price_modifier if variant else Decimal("0"))
    return unit * quantity


async def get_cart(db: AsyncSession, user_id: UUID) -> CartOut:
    cart = await _get_or_create_cart(db, user_id)
    subtotal = Decimal("0")
    item_count = 0
    for item in cart.items:
        subtotal += _line_price(item.product, item.variant, item.quantity)
        item_count += item.quantity

    cart_out = CartOut.model_validate(cart)
    cart_out.subtotal = subtotal
    cart_out.item_count = item_count
    return cart_out


async def add_cart_item(db: AsyncSession, user_id: UUID, data: CartItemCreate) -> CartOut:
    product_result = await db.execute(select(Product).where(Product.id == data.product_id))
    product = product_result.scalar_one_or_none()
    if not product or product.status != "active":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    variant = None
    if data.variant_id:
        variant_result = await db.execute(
            select(ProductVariant).where(
                ProductVariant.id == data.variant_id,
                ProductVariant.product_id == data.product_id,
            )
        )
        variant = variant_result.scalar_one_or_none()
        if not variant:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Variant not found")
        if variant.stock < data.quantity:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient variant stock")
    elif product.inventory < data.quantity:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient stock")

    cart = await _get_or_create_cart(db, user_id)
    existing = await db.execute(
        select(CartItem).where(
            CartItem.cart_id == cart.id,
            CartItem.product_id == data.product_id,
            CartItem.variant_id == data.variant_id,
        )
    )
    item = existing.scalar_one_or_none()
    if item:
        item.quantity += data.quantity
    else:
        db.add(
            CartItem(
                cart_id=cart.id,
                product_id=data.product_id,
                variant_id=data.variant_id,
                quantity=data.quantity,
            )
        )
    await db.flush()
    return await get_cart(db, user_id)


async def update_cart_item(db: AsyncSession, user_id: UUID, item_id: UUID, data: CartItemUpdate) -> CartOut:
    cart = await _get_or_create_cart(db, user_id)
    result = await db.execute(select(CartItem).where(CartItem.id == item_id, CartItem.cart_id == cart.id))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart item not found")
    item.quantity = data.quantity
    await db.flush()
    return await get_cart(db, user_id)


async def remove_cart_item(db: AsyncSession, user_id: UUID, item_id: UUID) -> CartOut:
    cart = await _get_or_create_cart(db, user_id)
    result = await db.execute(select(CartItem).where(CartItem.id == item_id, CartItem.cart_id == cart.id))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart item not found")
    await db.delete(item)
    await db.flush()
    return await get_cart(db, user_id)


async def clear_cart(db: AsyncSession, user_id: UUID) -> None:
    cart = await _get_or_create_cart(db, user_id)
    for item in list(cart.items):
        await db.delete(item)
    await db.flush()
