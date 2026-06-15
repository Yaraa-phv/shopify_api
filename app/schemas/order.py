from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.product import ProductListOut, ProductVariantOut


class OrderItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    product_id: UUID
    variant_id: UUID | None
    quantity: int
    unit_price: Decimal | None
    total_price: Decimal | None
    product: ProductListOut | None = None
    variant: ProductVariantOut | None = None


class OrderCreate(BaseModel):
    shipping_cost: Decimal | None = Field(default=None, ge=0)


class OrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    order_number: str
    user_id: UUID
    status: str | None
    payment_status: str | None
    subtotal: Decimal | None
    shipping_cost: Decimal | None
    total: Decimal | None
    created_at: datetime
    items: list[OrderItemOut] = []
