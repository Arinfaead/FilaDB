from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlmodel import Session, select
from ..core.database import get_session
from ..core.deps import require_admin
from ..models.user import User, UserRead
from ..models.bambu_part import BambuPart, BambuPartCreate, BambuPartRead, BambuPartUpdate
from ..services.spoolmandb import sync_spoolmandb_sync

router = APIRouter()


@router.post("/sync/spoolmandb")
async def trigger_spoolmandb_sync(
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_admin)
):
    """Trigger SpoolmanDB synchronization (admin only)"""
    background_tasks.add_task(sync_spoolmandb_sync, session)
    return {"message": "SpoolmanDB sync started in background"}


@router.get("/users", response_model=List[UserRead])
async def list_all_users(
    session: Session = Depends(get_session),
    current_user: User = Depends(require_admin)
):
    """List all users (admin only)"""
    statement = select(User)
    users = session.exec(statement).all()
    return users


# Bambu Parts management
@router.get("/bambu-parts", response_model=List[BambuPartRead])
async def list_bambu_parts(
    session: Session = Depends(get_session),
    current_user: User = Depends(require_admin)
):
    """List all Bambu Lab parts"""
    statement = select(BambuPart)
    parts = session.exec(statement).all()
    return parts


@router.post("/bambu-parts", response_model=BambuPartRead)
async def create_bambu_part(
    part_data: BambuPartCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_admin)
):
    """Create a new Bambu Lab part entry"""
    db_part = BambuPart(**part_data.dict())
    session.add(db_part)
    session.commit()
    session.refresh(db_part)
    return db_part


@router.get("/bambu-parts/{part_id}", response_model=BambuPartRead)
async def get_bambu_part(
    part_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_admin)
):
    """Get a specific Bambu Lab part"""
    statement = select(BambuPart).where(BambuPart.id == part_id)
    part = session.exec(statement).first()
    
    if not part:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bambu part not found"
        )
    
    return part


@router.patch("/bambu-parts/{part_id}", response_model=BambuPartRead)
async def update_bambu_part(
    part_id: int,
    part_update: BambuPartUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_admin)
):
    """Update a Bambu Lab part"""
    statement = select(BambuPart).where(BambuPart.id == part_id)
    part = session.exec(statement).first()
    
    if not part:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bambu part not found"
        )
    
    # Update fields
    update_data = part_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(part, field, value)
    
    session.add(part)
    session.commit()
    session.refresh(part)
    
    return part


@router.delete("/bambu-parts/{part_id}")
async def delete_bambu_part(
    part_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_admin)
):
    """Delete a Bambu Lab part"""
    statement = select(BambuPart).where(BambuPart.id == part_id)
    part = session.exec(statement).first()
    
    if not part:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bambu part not found"
        )
    
    session.delete(part)
    session.commit()
    
    return {"message": "Bambu part deleted successfully"}
