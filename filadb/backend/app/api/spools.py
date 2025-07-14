"""
Spools API routes
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from pydantic import BaseModel
from uuid import UUID
from decimal import Decimal
from datetime import date

from ..database import get_db
from ..models.spool import Spool
from ..models.user import User, UserRole
from ..auth.auth import get_current_active_user

router = APIRouter()


class SpoolBase(BaseModel):
    filament_id: UUID
    weight: Decimal
    remaining_weight: Decimal
    spool_weight: Decimal | None = None
    color: str | None = None
    hex_color: str | None = None
    diameter: Decimal
    purchase_date: date | None = None
    purchase_price: Decimal | None = None
    location: str | None = None
    nfc_tag_id: str | None = None
    qr_code: str | None = None
    notes: str | None = None
    custom_fields: dict = {}
    is_active: bool = True


class SpoolCreate(SpoolBase):
    pass


class SpoolUpdate(BaseModel):
    filament_id: UUID | None = None
    printer_id: UUID | None = None
    weight: Decimal | None = None
    remaining_weight: Decimal | None = None
    spool_weight: Decimal | None = None
    color: str | None = None
    hex_color: str | None = None
    diameter: Decimal | None = None
    purchase_date: date | None = None
    purchase_price: Decimal | None = None
    location: str | None = None
    nfc_tag_id: str | None = None
    qr_code: str | None = None
    notes: str | None = None
    custom_fields: dict | None = None
    is_active: bool | None = None


class SpoolResponse(SpoolBase):
    id: UUID
    user_id: UUID
    printer_id: UUID | None = None
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


@router.get("/", response_model=List[SpoolResponse])
async def read_spools(
    skip: int = 0,
    limit: int = 100,
    filament_id: UUID | None = None,
    printer_id: UUID | None = None,
    is_active: bool | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all spools with optional filtering"""
    query = select(Spool).options(
        selectinload(Spool.filament),
        selectinload(Spool.user),
        selectinload(Spool.printer)
    )
    
    # Non-admin users can only see their own spools
    if current_user.role != UserRole.ADMIN:
        query = query.where(Spool.user_id == current_user.id)
    
    if filament_id:
        query = query.where(Spool.filament_id == filament_id)
    if printer_id:
        query = query.where(Spool.printer_id == printer_id)
    if is_active is not None:
        query = query.where(Spool.is_active == is_active)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    spools = result.scalars().all()
    return spools


@router.post("/", response_model=SpoolResponse)
async def create_spool(
    spool: SpoolCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new spool"""
    # Check for duplicate NFC tag or QR code
    if spool.nfc_tag_id:
        result = await db.execute(select(Spool).where(Spool.nfc_tag_id == spool.nfc_tag_id))
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="NFC tag ID already exists"
            )
    
    if spool.qr_code:
        result = await db.execute(select(Spool).where(Spool.qr_code == spool.qr_code))
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="QR code already exists"
            )
    
    db_spool = Spool(**spool.dict(), user_id=current_user.id)
    db.add(db_spool)
    await db.commit()
    await db.refresh(db_spool)
    
    return db_spool


@router.get("/{spool_id}", response_model=SpoolResponse)
async def read_spool(
    spool_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific spool"""
    result = await db.execute(
        select(Spool)
        .options(
            selectinload(Spool.filament),
            selectinload(Spool.user),
            selectinload(Spool.printer)
        )
        .where(Spool.id == spool_id)
    )
    spool = result.scalar_one_or_none()
    
    if spool is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Spool not found"
        )
    
    # Non-admin users can only see their own spools
    if current_user.role != UserRole.ADMIN and spool.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return spool


@router.put("/{spool_id}", response_model=SpoolResponse)
async def update_spool(
    spool_id: UUID,
    spool_update: SpoolUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a spool"""
    result = await db.execute(select(Spool).where(Spool.id == spool_id))
    spool = result.scalar_one_or_none()
    
    if spool is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Spool not found"
        )
    
    # Non-admin users can only update their own spools
    if current_user.role != UserRole.ADMIN and spool.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Update spool fields
    update_data = spool_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(spool, field, value)
    
    await db.commit()
    await db.refresh(spool)
    
    return spool


@router.delete("/{spool_id}")
async def delete_spool(
    spool_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a spool"""
    result = await db.execute(select(Spool).where(Spool.id == spool_id))
    spool = result.scalar_one_or_none()
    
    if spool is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Spool not found"
        )
    
    # Non-admin users can only delete their own spools
    if current_user.role != UserRole.ADMIN and spool.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    await db.delete(spool)
    await db.commit()
    
    return {"message": "Spool deleted successfully"}


@router.get("/nfc/{nfc_tag_id}", response_model=SpoolResponse)
async def read_spool_by_nfc(
    nfc_tag_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a spool by NFC tag ID"""
    result = await db.execute(
        select(Spool)
        .options(
            selectinload(Spool.filament),
            selectinload(Spool.user),
            selectinload(Spool.printer)
        )
        .where(Spool.nfc_tag_id == nfc_tag_id)
    )
    spool = result.scalar_one_or_none()
    
    if spool is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Spool not found"
        )
    
    # Non-admin users can only see their own spools
    if current_user.role != UserRole.ADMIN and spool.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return spool
