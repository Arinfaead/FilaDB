"""
Filaments API routes
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from pydantic import BaseModel
from uuid import UUID
from decimal import Decimal

from ..database import get_db
from ..models.filament import Filament
from ..models.user import User
from ..auth.auth import get_current_active_user

router = APIRouter()


class FilamentBase(BaseModel):
    manufacturer_id: UUID
    material_id: UUID
    name: str
    density: Decimal | None = None
    extruder_temp_min: int | None = None
    extruder_temp_max: int | None = None
    bed_temp_min: int | None = None
    bed_temp_max: int | None = None
    colors: list = []
    weights: list = []
    diameters: list = []
    settings: dict = {}
    spoolman_db_id: str | None = None


class FilamentCreate(FilamentBase):
    pass


class FilamentUpdate(BaseModel):
    manufacturer_id: UUID | None = None
    material_id: UUID | None = None
    name: str | None = None
    density: Decimal | None = None
    extruder_temp_min: int | None = None
    extruder_temp_max: int | None = None
    bed_temp_min: int | None = None
    bed_temp_max: int | None = None
    colors: list | None = None
    weights: list | None = None
    diameters: list | None = None
    settings: dict | None = None
    spoolman_db_id: str | None = None


class FilamentResponse(FilamentBase):
    id: UUID
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


@router.get("/", response_model=List[FilamentResponse])
async def read_filaments(
    skip: int = 0,
    limit: int = 100,
    manufacturer_id: UUID | None = None,
    material_id: UUID | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all filaments with optional filtering"""
    query = select(Filament).options(
        selectinload(Filament.manufacturer),
        selectinload(Filament.material)
    )
    
    if manufacturer_id:
        query = query.where(Filament.manufacturer_id == manufacturer_id)
    if material_id:
        query = query.where(Filament.material_id == material_id)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    filaments = result.scalars().all()
    return filaments


@router.post("/", response_model=FilamentResponse)
async def create_filament(
    filament: FilamentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new filament"""
    # Check if filament already exists for this manufacturer
    result = await db.execute(
        select(Filament).where(
            Filament.manufacturer_id == filament.manufacturer_id,
            Filament.name == filament.name
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filament already exists for this manufacturer"
        )
    
    db_filament = Filament(**filament.dict())
    db.add(db_filament)
    await db.commit()
    await db.refresh(db_filament)
    
    return db_filament


@router.get("/{filament_id}", response_model=FilamentResponse)
async def read_filament(
    filament_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific filament"""
    result = await db.execute(
        select(Filament)
        .options(
            selectinload(Filament.manufacturer),
            selectinload(Filament.material)
        )
        .where(Filament.id == filament_id)
    )
    filament = result.scalar_one_or_none()
    
    if filament is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Filament not found"
        )
    
    return filament


@router.put("/{filament_id}", response_model=FilamentResponse)
async def update_filament(
    filament_id: UUID,
    filament_update: FilamentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a filament"""
    result = await db.execute(select(Filament).where(Filament.id == filament_id))
    filament = result.scalar_one_or_none()
    
    if filament is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Filament not found"
        )
    
    # Update filament fields
    update_data = filament_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(filament, field, value)
    
    await db.commit()
    await db.refresh(filament)
    
    return filament


@router.delete("/{filament_id}")
async def delete_filament(
    filament_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a filament"""
    result = await db.execute(select(Filament).where(Filament.id == filament_id))
    filament = result.scalar_one_or_none()
    
    if filament is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Filament not found"
        )
    
    await db.delete(filament)
    await db.commit()
    
    return {"message": "Filament deleted successfully"}
