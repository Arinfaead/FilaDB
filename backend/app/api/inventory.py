from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select, or_
from ..core.database import get_session
from ..core.deps import get_current_active_user, require_editor_or_admin
from ..models.user import User
from ..models.filament import Filament, FilamentCreate, FilamentRead, FilamentUpdate
from ..models.spool import Spool, SpoolCreate, SpoolRead, SpoolUpdate

router = APIRouter()


# Filament endpoints
@router.get("/filaments", response_model=List[FilamentRead])
async def list_filaments(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None),
    manufacturer: Optional[str] = Query(None),
    material: Optional[str] = Query(None)
):
    """List filaments with optional filtering"""
    statement = select(Filament)
    
    # Apply filters
    if search:
        statement = statement.where(
            or_(
                Filament.name.ilike(f"%{search}%"),
                Filament.manufacturer.ilike(f"%{search}%"),
                Filament.color_name.ilike(f"%{search}%")
            )
        )
    
    if manufacturer:
        statement = statement.where(Filament.manufacturer.ilike(f"%{manufacturer}%"))
    
    if material:
        statement = statement.where(Filament.material.ilike(f"%{material}%"))
    
    statement = statement.offset(skip).limit(limit)
    filaments = session.exec(statement).all()
    return filaments


@router.post("/filaments", response_model=FilamentRead)
async def create_filament(
    filament_data: FilamentCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_editor_or_admin)
):
    """Create a new custom filament"""
    # Mark as custom filament
    filament_data.is_custom = True
    
    db_filament = Filament(**filament_data.dict())
    session.add(db_filament)
    session.commit()
    session.refresh(db_filament)
    
    return db_filament


@router.get("/filaments/{filament_id}", response_model=FilamentRead)
async def get_filament(
    filament_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific filament"""
    statement = select(Filament).where(Filament.id == filament_id)
    filament = session.exec(statement).first()
    
    if not filament:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Filament not found"
        )
    
    return filament


@router.patch("/filaments/{filament_id}", response_model=FilamentRead)
async def update_filament(
    filament_id: int,
    filament_update: FilamentUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_editor_or_admin)
):
    """Update a filament (only custom filaments can be updated)"""
    statement = select(Filament).where(Filament.id == filament_id)
    filament = session.exec(statement).first()
    
    if not filament:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Filament not found"
        )
    
    if not filament.is_custom:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update SpoolmanDB filaments"
        )
    
    # Update fields
    update_data = filament_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(filament, field, value)
    
    session.add(filament)
    session.commit()
    session.refresh(filament)
    
    return filament


# Spool endpoints
@router.get("/spools", response_model=List[SpoolRead])
async def list_spools(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    location: Optional[str] = Query(None)
):
    """List spools with optional filtering"""
    statement = select(Spool)
    
    if location:
        statement = statement.where(Spool.location.ilike(f"%{location}%"))
    
    statement = statement.offset(skip).limit(limit)
    spools = session.exec(statement).all()
    return spools


@router.post("/spools", response_model=SpoolRead)
async def create_spool(
    spool_data: SpoolCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_editor_or_admin)
):
    """Add a new spool to inventory"""
    # Verify filament exists
    statement = select(Filament).where(Filament.id == spool_data.filament_id)
    filament = session.exec(statement).first()
    
    if not filament:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Filament not found"
        )
    
    db_spool = Spool(**spool_data.dict())
    session.add(db_spool)
    session.commit()
    session.refresh(db_spool)
    
    return db_spool


@router.get("/spools/{spool_id}", response_model=SpoolRead)
async def get_spool(
    spool_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific spool"""
    statement = select(Spool).where(Spool.id == spool_id)
    spool = session.exec(statement).first()
    
    if not spool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Spool not found"
        )
    
    return spool


@router.patch("/spools/{spool_id}", response_model=SpoolRead)
async def update_spool(
    spool_id: int,
    spool_update: SpoolUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_editor_or_admin)
):
    """Update a spool (e.g., remaining weight after printing)"""
    statement = select(Spool).where(Spool.id == spool_id)
    spool = session.exec(statement).first()
    
    if not spool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Spool not found"
        )
    
    # Update fields
    update_data = spool_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(spool, field, value)
    
    session.add(spool)
    session.commit()
    session.refresh(spool)
    
    return spool


@router.delete("/spools/{spool_id}")
async def delete_spool(
    spool_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_editor_or_admin)
):
    """Delete a spool from inventory"""
    statement = select(Spool).where(Spool.id == spool_id)
    spool = session.exec(statement).first()
    
    if not spool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Spool not found"
        )
    
    session.delete(spool)
    session.commit()
    
    return {"message": "Spool deleted successfully"}
