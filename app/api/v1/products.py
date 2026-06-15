from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user, require_admin
from app.db.session import get_db
from app.models import User
from app.schemas.product import (
    CategoryCreate,
    CategoryOut,
    CategoryUpdate,
    ProductCreate,
    ProductListOut,
    ProductOut,
    ProductUpdate,
    ReviewCreate,
    ReviewOut,
)
from app.services.product_service import (
    create_category,
    create_product,
    create_review,
    delete_product,
    get_category,
    get_product,
    get_product_rating,
    list_categories,
    list_products,
    list_reviews,
    update_category,
    update_product,
)

router = APIRouter(tags=["Products & Categories"])


@router.get("/categories", response_model=list[CategoryOut])
async def get_categories(db: AsyncSession = Depends(get_db)):
    return await list_categories(db)


@router.get("/categories/{category_id}", response_model=CategoryOut)
async def get_category_by_id(category_id: UUID, db: AsyncSession = Depends(get_db)):
    return await get_category(db, category_id)


@router.post("/categories", response_model=CategoryOut, status_code=status.HTTP_201_CREATED)
async def create_category_endpoint(
    data: CategoryCreate,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    return await create_category(db, data)


@router.put("/categories/{category_id}", response_model=CategoryOut)
async def update_category_endpoint(
    category_id: UUID,
    data: CategoryUpdate,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    return await update_category(db, category_id, data)


@router.get("/products", response_model=list[ProductListOut])
async def get_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    category_id: UUID | None = None,
    search: str | None = None,
    status_filter: str | None = Query("active", alias="status"),
    db: AsyncSession = Depends(get_db),
):
    return await list_products(db, skip=skip, limit=limit, category_id=category_id, search=search, status=status_filter)


@router.get("/products/{product_id}", response_model=ProductOut)
async def get_product_by_id(product_id: UUID, db: AsyncSession = Depends(get_db)):
    return await get_product(db, product_id)


@router.post("/products", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
async def create_product_endpoint(
    data: ProductCreate,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    return await create_product(db, data)


@router.put("/products/{product_id}", response_model=ProductOut)
async def update_product_endpoint(
    product_id: UUID,
    data: ProductUpdate,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    return await update_product(db, product_id, data)


@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product_endpoint(
    product_id: UUID,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    await delete_product(db, product_id)


@router.get("/products/{product_id}/reviews", response_model=list[ReviewOut])
async def get_product_reviews(product_id: UUID, db: AsyncSession = Depends(get_db)):
    return await list_reviews(db, product_id)


@router.get("/products/{product_id}/rating")
async def get_product_rating_summary(product_id: UUID, db: AsyncSession = Depends(get_db)):
    return await get_product_rating(db, product_id)


@router.post("/products/{product_id}/reviews", response_model=ReviewOut, status_code=status.HTTP_201_CREATED)
async def add_product_review(
    product_id: UUID,
    data: ReviewCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    return await create_review(db, product_id, current_user.id, data)
