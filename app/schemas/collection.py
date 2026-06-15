from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.product import ProductListOut


class CollectionCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    slug: str | None = Field(default=None, max_length=255)
    image_url: str | None = Field(default=None, max_length=500)
    sort_order: int = 0
    product_ids: list[UUID] = []


class CollectionUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    slug: str | None = Field(default=None, max_length=255)
    image_url: str | None = Field(default=None, max_length=500)
    sort_order: int | None = None
    product_ids: list[UUID] | None = None


class CollectionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    slug: str | None
    image_url: str | None
    sort_order: int


class CollectionDetailOut(CollectionOut):
    products: list[ProductListOut] = []
