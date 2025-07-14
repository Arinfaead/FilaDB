"""
Manufacturers API routes
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from uuid import UUID

from ..database import get_db
from ..models.manufacturer import Manufacturer
from ..models.user import User
from ..auth.auth import get_current_active_user

router = APIRouter()


class ManufacturerBase(BaseModel):
    name: str
    website: str | None = None
    logo_url: str | None = None


class ManufacturerCreate(ManufacturerBase):
    pass


class ManufacturerUpdate(BaseModel):
    name: str | None = None
    website: str | None = None
    logo_url: str | None = None


class ManufacturerResponse(ManufacturerBase):
    id: UUID
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


@router.get("/", response_model=List[ManufacturerResponse])
async def read_manufacturers(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all manufacturers"""
    result = await db.execute(select(Manufacturer).offset(skip).limit(limit))
    manufacturers = result.scalars().all()
    return manufacturers


@router.post("/", response_model=ManufacturerResponse)
async def create_manufacturer(
    manufacturer: ManufacturerCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new manufacturer"""
    # Check if manufacturer already exists
    result = await db.execute(select(Manufacturer).where(Manufacturer.name == manufacturer.name))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Manufacturer already exists"
        )
    
    db_manufacturer = Manufacturer(**manufacturer.dict())
    db.add(db_manufacturer)
    await db.commit()
    await db.refresh(db_manufacturer)
    
    return db_manufacturer


@router.get("/{manufacturer_id}", response_model=ManufacturerResponse)
async def read_manufacturer(
    manufacturer_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific manufacturer"""
    result = await db.execute(select(Manufacturer).where(Manufacturer.id == manufacturer_id))
    manufacturer = result.scalar_one_or_none()
    
    if manufacturer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Manufacturer not found"
        )
    
    return manufacturer


@router.put("/{manufacturer_id}", response_model=ManufacturerResponse)
async def update_manufacturer(
    manufacturer_id: UUID,
    manufacturer_update: ManufacturerUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a manufacturer"""
    result = await db.execute(select(Manufacturer).where(Manufacturer.id == manufacturer_id))
    manufacturer = result.scalar_one_or_none()
    
    if manufacturer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Manufacturer not found"
        )
    
    # Update manufacturer fields
    update_data = manufacturer_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(manufacturer, field, value)
    
    await db.commit()
    await db.refresh(manufacturer)
    
    return manufacturer


@router.delete("/{manufacturer_id}")
async def delete_manufacturer(
    manufacturer_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a manufacturer"""
    result = await db.execute(select(Manufacturer).where(Manufacturer.id == manufacturer_id))
    manufacturer = result.scalar_one_or_none()
    
    if manufacturer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Manufacturer not found"
        )
    
    await db.delete(manufacturer)
    await db.commit()
    
    return {"message": "Manufacturer deleted successfully"}
