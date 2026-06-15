from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    slug: str | None = Field(default=None, max_length=255)
    image_url: str | None = Field(default=None, max_length=500)


class CategoryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    slug: str | None = Field(default=None, max_length=255)
    image_url: str | None = Field(default=None, max_length=500)


class CategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    slug: str | None
    image_url: str | None


class ProductVariantCreate(BaseModel):
    size: str | None = Field(default=None, max_length=50)
    color: str | None = Field(default=None, max_length=50)
    stock: int = Field(default=0, ge=0)
    price_modifier: Decimal = Field(default=Decimal("0.00"))


class ProductVariantOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    product_id: UUID
    size: str | None
    color: str | None
    stock: int
    price_modifier: Decimal


class ProductImageCreate(BaseModel):
    url: str = Field(min_length=1, max_length=500)
    sort_order: int = 0


class ProductImageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    product_id: UUID
    url: str
    sort_order: int


class ProductCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    price: Decimal = Field(gt=0)
    compare_price: Decimal | None = Field(default=None, gt=0)
    status: str | None = "active"
    inventory: int = Field(default=0, ge=0)
    category_id: UUID | None = None
    variants: list[ProductVariantCreate] = []
    images: list[ProductImageCreate] = []


class ProductUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    price: Decimal | None = Field(default=None, gt=0)
    compare_price: Decimal | None = Field(default=None, gt=0)
    status: str | None = None
    inventory: int | None = Field(default=None, ge=0)
    category_id: UUID | None = None


class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    description: str | None
    price: Decimal
    compare_price: Decimal | None
    status: str | None
    inventory: int
    category_id: UUID | None
    created_at: datetime
    variants: list[ProductVariantOut] = []
    images: list[ProductImageOut] = []
    category: CategoryOut | None = None


class ProductListOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    price: Decimal
    compare_price: Decimal | None
    status: str | None
    inventory: int
    created_at: datetime
    images: list[ProductImageOut] = []


class ReviewCreate(BaseModel):
    rating: int = Field(ge=1, le=5)
    title: str | None = Field(default=None, max_length=255)
    body: str | None = None


class ReviewOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    product_id: UUID
    user_id: UUID
    rating: int
    title: str | None
    body: str | None
    created_at: datetime
