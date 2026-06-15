from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Collection, CollectionProduct, Product
from app.schemas.collection import CollectionCreate, CollectionUpdate


async def list_collections(db: AsyncSession) -> list[Collection]:
    result = await db.execute(select(Collection).order_by(Collection.sort_order, Collection.title))
    return list(result.scalars().all())


async def get_collection_by_slug(db: AsyncSession, slug: str) -> Collection:
    result = await db.execute(
        select(Collection)
        .options(
            selectinload(Collection.product_links).selectinload(CollectionProduct.product).selectinload(Product.images)
        )
        .where(Collection.slug == slug)
    )
    collection = result.scalar_one_or_none()
    if not collection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collection not found")
    return collection


async def get_collection(db: AsyncSession, collection_id: UUID) -> Collection:
    result = await db.execute(
        select(Collection)
        .options(
            selectinload(Collection.product_links).selectinload(CollectionProduct.product).selectinload(Product.images)
        )
        .where(Collection.id == collection_id)
    )
    collection = result.scalar_one_or_none()
    if not collection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collection not found")
    return collection


async def create_collection(db: AsyncSession, data: CollectionCreate) -> Collection:
    collection = Collection(
        title=data.title,
        slug=data.slug,
        image_url=data.image_url,
        sort_order=data.sort_order,
    )
    db.add(collection)
    await db.flush()

    for product_id in data.product_ids:
        db.add(CollectionProduct(collection_id=collection.id, product_id=product_id))

    await db.flush()
    return await get_collection(db, collection.id)


async def update_collection(db: AsyncSession, collection_id: UUID, data: CollectionUpdate) -> Collection:
    collection = await get_collection(db, collection_id)
    updates = data.model_dump(exclude_unset=True, exclude={"product_ids"})
    for key, value in updates.items():
        setattr(collection, key, value)

    if data.product_ids is not None:
        for link in list(collection.product_links):
            await db.delete(link)
        for product_id in data.product_ids:
            db.add(CollectionProduct(collection_id=collection.id, product_id=product_id))

    await db.flush()
    return await get_collection(db, collection_id)


async def delete_collection(db: AsyncSession, collection_id: UUID) -> None:
    collection = await get_collection(db, collection_id)
    await db.delete(collection)
