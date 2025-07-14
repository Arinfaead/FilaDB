"""
Materials API routes
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from uuid import UUID
from decimal import Decimal

from ..database import get_db
from ..models.material import Material
from ..models.user import User
from ..auth.auth import get_current_active_user

router = APIRouter()


class MaterialBase(BaseModel):
    name: str
    density: Decimal
    extruder_temp_min: int | None = None
    extruder_temp_max: int | None = None
    bed_temp_min: int | None = None
    bed_temp_max: int | None = None
    properties: dict = {}


class MaterialCreate(MaterialBase):
    pass


class MaterialUpdate(BaseModel):
    name: str | None = None
    density: Decimal | None = None
    extruder_temp_min: int | None = None
    extruder_temp_max: int | None = None
    bed_temp_min: int | None = None
    bed_temp_max: int | None = None
    properties: dict | None = None


class MaterialResponse(MaterialBase):
    id: UUID
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


@router.get("/", response_model=List[MaterialResponse])
async def read_materials(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all materials"""
    result = await db.execute(select(Material).offset(skip).limit(limit))
    materials = result.scalars().all()
    return materials


@router.post("/", response_model=MaterialResponse)
async def create_material(
    material: MaterialCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new material"""
    # Check if material already exists
    result = await db.execute(select(Material).where(Material.name == material.name))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Material already exists"
        )
    
    db_material = Material(**material.dict())
    db.add(db_material)
    await db.commit()
    await db.refresh(db_material)
    
    return db_material


@router.get("/{material_id}", response_model=MaterialResponse)
async def read_material(
    material_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific material"""
    result = await db.execute(select(Material).where(Material.id == material_id))
    material = result.scalar_one_or_none()
    
    if material is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Material not found"
        )
    
    return material


@router.put("/{material_id}", response_model=MaterialResponse)
async def update_material(
    material_id: UUID,
    material_update: MaterialUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a material"""
    result = await db.execute(select(Material).where(Material.id == material_id))
    material = result.scalar_one_or_none()
    
    if material is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Material not found"
        )
    
    # Update material fields
    update_data = material_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(material, field, value)
    
    await db.commit()
    await db.refresh(material)
    
    return material


@router.delete("/{material_id}")
async def delete_material(
    material_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a material"""
    result = await db.execute(select(Material).where(Material.id == material_id))
    material = result.scalar_one_or_none()
    
    if material is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Material not found"
        )
    
    await db.delete(material)
    await db.commit()
    
    return {"message": "Material deleted successfully"}
