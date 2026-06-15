from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user
from app.db.session import get_db
from app.models import User
from app.schemas.address import AddressCreate, AddressOut, AddressUpdate
from app.schemas.auth import PasswordChange, UserOut, UserUpdate
from app.services.user_service import (
    change_password,
    create_address,
    delete_address,
    list_addresses,
    update_address,
    update_profile,
)

router = APIRouter(prefix="/users", tags=["User Profile"])


@router.get("/me", response_model=UserOut)
async def get_profile(current_user: User = Depends(get_current_active_user)):
    return current_user


@router.put("/me", response_model=UserOut)
async def update_user_profile(
    data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    return await update_profile(db, current_user, data)


@router.put("/me/password", status_code=status.HTTP_204_NO_CONTENT)
async def update_password(
    data: PasswordChange,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    await change_password(db, current_user, data)


@router.get("/me/addresses", response_model=list[AddressOut])
async def get_addresses(current_user: User = Depends(get_current_active_user), db: AsyncSession = Depends(get_db)):
    return await list_addresses(db, current_user.id)


@router.post("/me/addresses", response_model=AddressOut, status_code=status.HTTP_201_CREATED)
async def add_address(
    data: AddressCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    return await create_address(db, current_user.id, data)


@router.put("/me/addresses/{address_id}", response_model=AddressOut)
async def edit_address(
    address_id: UUID,
    data: AddressUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    return await update_address(db, current_user.id, address_id, data)


@router.delete("/me/addresses/{address_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_address(
    address_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    await delete_address(db, current_user.id, address_id)
