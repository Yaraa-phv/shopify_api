from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_admin
from app.db.session import get_db
from app.models import User
from app.schemas.collection import CollectionCreate, CollectionDetailOut, CollectionOut, CollectionUpdate
from app.schemas.product import ProductListOut
from app.services.collection_service import (
    create_collection,
    delete_collection,
    get_collection,
    get_collection_by_slug,
    list_collections,
    update_collection,
)

router = APIRouter(prefix="/collections", tags=["Collections"])


def _collection_detail(collection) -> CollectionDetailOut:
    products = [link.product for link in collection.product_links]
    return CollectionDetailOut(
        id=collection.id,
        title=collection.title,
        slug=collection.slug,
        image_url=collection.image_url,
        sort_order=collection.sort_order,
        products=[ProductListOut.model_validate(p) for p in products],
    )


@router.get("", response_model=list[CollectionOut])
async def get_collections(db: AsyncSession = Depends(get_db)):
    return await list_collections(db)


@router.get("/slug/{slug}", response_model=CollectionDetailOut)
async def get_collection_by_slug_endpoint(slug: str, db: AsyncSession = Depends(get_db)):
    collection = await get_collection_by_slug(db, slug)
    return _collection_detail(collection)


@router.get("/{collection_id}", response_model=CollectionDetailOut)
async def get_collection_by_id(collection_id: UUID, db: AsyncSession = Depends(get_db)):
    collection = await get_collection(db, collection_id)
    return _collection_detail(collection)


@router.post("", response_model=CollectionDetailOut, status_code=status.HTTP_201_CREATED)
async def create_collection_endpoint(
    data: CollectionCreate,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    collection = await create_collection(db, data)
    return _collection_detail(collection)


@router.put("/{collection_id}", response_model=CollectionDetailOut)
async def update_collection_endpoint(
    collection_id: UUID,
    data: CollectionUpdate,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    collection = await update_collection(db, collection_id, data)
    return _collection_detail(collection)


@router.delete("/{collection_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_collection_endpoint(
    collection_id: UUID,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    await delete_collection(db, collection_id)
