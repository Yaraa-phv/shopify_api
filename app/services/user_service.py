from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash, verify_password
from app.models import Address, User
from app.schemas.address import AddressCreate, AddressUpdate
from app.schemas.auth import PasswordChange, UserUpdate


async def update_profile(db: AsyncSession, user: User, data: UserUpdate) -> User:
    if data.email and data.email != user.email:
        existing = await db.execute(select(User).where(User.email == data.email))
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already in use")
        user.email = data.email
    if data.full_name is not None:
        user.full_name = data.full_name
    await db.flush()
    await db.refresh(user)
    return user


async def change_password(db: AsyncSession, user: User, data: PasswordChange) -> None:
    if not verify_password(data.current_password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect")
    user.password_hash = get_password_hash(data.new_password)
    await db.flush()


async def list_addresses(db: AsyncSession, user_id: UUID) -> list[Address]:
    result = await db.execute(select(Address).where(Address.user_id == user_id).order_by(Address.is_default.desc()))
    return list(result.scalars().all())


async def create_address(db: AsyncSession, user_id: UUID, data: AddressCreate) -> Address:
    if data.is_default:
        result = await db.execute(select(Address).where(Address.user_id == user_id, Address.is_default.is_(True)))
        for addr in result.scalars().all():
            addr.is_default = False

    address = Address(user_id=user_id, **data.model_dump())
    db.add(address)
    await db.flush()
    await db.refresh(address)
    return address


async def update_address(db: AsyncSession, user_id: UUID, address_id: UUID, data: AddressUpdate) -> Address:
    result = await db.execute(select(Address).where(Address.id == address_id, Address.user_id == user_id))
    address = result.scalar_one_or_none()
    if not address:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address not found")

    updates = data.model_dump(exclude_unset=True)
    if updates.get("is_default"):
        others = await db.execute(select(Address).where(Address.user_id == user_id, Address.id != address_id))
        for addr in others.scalars().all():
            addr.is_default = False

    for key, value in updates.items():
        setattr(address, key, value)
    await db.flush()
    await db.refresh(address)
    return address


async def delete_address(db: AsyncSession, user_id: UUID, address_id: UUID) -> None:
    result = await db.execute(select(Address).where(Address.id == address_id, Address.user_id == user_id))
    address = result.scalar_one_or_none()
    if not address:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address not found")
    await db.delete(address)
