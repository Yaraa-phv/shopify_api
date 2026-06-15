from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Category, Product, ProductImage, ProductVariant, Review
from app.schemas.product import (
    CategoryCreate,
    CategoryUpdate,
    ProductCreate,
    ProductUpdate,
    ReviewCreate,
)


async def list_categories(db: AsyncSession) -> list[Category]:
    result = await db.execute(select(Category).order_by(Category.name))
    return list(result.scalars().all())


async def get_category(db: AsyncSession, category_id: UUID) -> Category:
    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return category


async def create_category(db: AsyncSession, data: CategoryCreate) -> Category:
    category = Category(**data.model_dump())
    db.add(category)
    await db.flush()
    await db.refresh(category)
    return category


async def update_category(db: AsyncSession, category_id: UUID, data: CategoryUpdate) -> Category:
    category = await get_category(db, category_id)
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(category, key, value)
    await db.flush()
    await db.refresh(category)
    return category


async def list_products(
    db: AsyncSession,
    *,
    skip: int = 0,
    limit: int = 20,
    category_id: UUID | None = None,
    search: str | None = None,
    status: str | None = "active",
) -> list[Product]:
    query = select(Product).options(selectinload(Product.images)).order_by(Product.created_at.desc())
    if status:
        query = query.where(Product.status == status)
    if category_id:
        query = query.where(Product.category_id == category_id)
    if search:
        query = query.where(or_(Product.title.ilike(f"%{search}%"), Product.description.ilike(f"%{search}%")))
    result = await db.execute(query.offset(skip).limit(limit))
    return list(result.scalars().unique().all())


async def get_product(db: AsyncSession, product_id: UUID) -> Product:
    result = await db.execute(
        select(Product)
        .options(
            selectinload(Product.images),
            selectinload(Product.variants),
            selectinload(Product.category),
        )
        .where(Product.id == product_id)
    )
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product


async def create_product(db: AsyncSession, data: ProductCreate) -> Product:
    product_data = data.model_dump(exclude={"variants", "images"})
    product = Product(**product_data)
    db.add(product)
    await db.flush()

    for variant in data.variants:
        db.add(ProductVariant(product_id=product.id, **variant.model_dump()))
    for image in data.images:
        db.add(ProductImage(product_id=product.id, **image.model_dump()))

    await db.flush()
    return await get_product(db, product.id)


async def update_product(db: AsyncSession, product_id: UUID, data: ProductUpdate) -> Product:
    product = await get_product(db, product_id)
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(product, key, value)
    await db.flush()
    return await get_product(db, product_id)


async def delete_product(db: AsyncSession, product_id: UUID) -> None:
    product = await get_product(db, product_id)
    await db.delete(product)


async def list_reviews(db: AsyncSession, product_id: UUID) -> list[Review]:
    await get_product(db, product_id)
    result = await db.execute(
        select(Review).where(Review.product_id == product_id).order_by(Review.created_at.desc())
    )
    return list(result.scalars().all())


async def create_review(db: AsyncSession, product_id: UUID, user_id: UUID, data: ReviewCreate) -> Review:
    await get_product(db, product_id)
    existing = await db.execute(
        select(Review).where(Review.product_id == product_id, Review.user_id == user_id)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You already reviewed this product")

    review = Review(product_id=product_id, user_id=user_id, **data.model_dump())
    db.add(review)
    await db.flush()
    await db.refresh(review)
    return review


async def get_product_rating(db: AsyncSession, product_id: UUID) -> dict:
    result = await db.execute(
        select(func.avg(Review.rating), func.count(Review.id)).where(Review.product_id == product_id)
    )
    avg_rating, count = result.one()
    return {"average_rating": float(avg_rating) if avg_rating else None, "review_count": count or 0}
