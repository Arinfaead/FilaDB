"""
Printers API routes
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from pydantic import BaseModel
from uuid import UUID

from ..database import get_db
from ..models.printer import Printer, PrinterStatus
from ..models.user import User, UserRole
from ..auth.auth import get_current_active_user

router = APIRouter()


class PrinterBase(BaseModel):
    name: str
    type: str | None = None
    location: str | None = None
    notes: str | None = None
    settings: dict = {}


class PrinterCreate(PrinterBase):
    pass


class PrinterUpdate(BaseModel):
    name: str | None = None
    type: str | None = None
    status: PrinterStatus | None = None
    location: str | None = None
    notes: str | None = None
    settings: dict | None = None


class PrinterResponse(PrinterBase):
    id: UUID
    user_id: UUID
    status: PrinterStatus
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


@router.get("/", response_model=List[PrinterResponse])
async def read_printers(
    skip: int = 0,
    limit: int = 100,
    status: PrinterStatus | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all printers with optional filtering"""
    query = select(Printer).options(selectinload(Printer.user))
    
    # Non-admin users can only see their own printers
    if current_user.role != UserRole.ADMIN:
        query = query.where(Printer.user_id == current_user.id)
    
    if status:
        query = query.where(Printer.status == status)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    printers = result.scalars().all()
    return printers


@router.post("/", response_model=PrinterResponse)
async def create_printer(
    printer: PrinterCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new printer"""
    db_printer = Printer(**printer.dict(), user_id=current_user.id)
    db.add(db_printer)
    await db.commit()
    await db.refresh(db_printer)
    
    return db_printer


@router.get("/{printer_id}", response_model=PrinterResponse)
async def read_printer(
    printer_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific printer"""
    result = await db.execute(
        select(Printer)
        .options(selectinload(Printer.user))
        .where(Printer.id == printer_id)
    )
    printer = result.scalar_one_or_none()
    
    if printer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Printer not found"
        )
    
    # Non-admin users can only see their own printers
    if current_user.role != UserRole.ADMIN and printer.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return printer


@router.put("/{printer_id}", response_model=PrinterResponse)
async def update_printer(
    printer_id: UUID,
    printer_update: PrinterUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a printer"""
    result = await db.execute(select(Printer).where(Printer.id == printer_id))
    printer = result.scalar_one_or_none()
    
    if printer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Printer not found"
        )
    
    # Non-admin users can only update their own printers
    if current_user.role != UserRole.ADMIN and printer.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Update printer fields
    update_data = printer_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(printer, field, value)
    
    await db.commit()
    await db.refresh(printer)
    
    return printer


@router.delete("/{printer_id}")
async def delete_printer(
    printer_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a printer"""
    result = await db.execute(select(Printer).where(Printer.id == printer_id))
    printer = result.scalar_one_or_none()
    
    if printer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Printer not found"
        )
    
    # Non-admin users can only delete their own printers
    if current_user.role != UserRole.ADMIN and printer.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    await db.delete(printer)
    await db.commit()
    
    return {"message": "Printer deleted successfully"}


@router.post("/{printer_id}/status")
async def update_printer_status(
    printer_id: UUID,
    status: PrinterStatus,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update printer status"""
    result = await db.execute(select(Printer).where(Printer.id == printer_id))
    printer = result.scalar_one_or_none()
    
    if printer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Printer not found"
        )
    
    # Non-admin users can only update their own printers
    if current_user.role != UserRole.ADMIN and printer.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    printer.status = status
    await db.commit()
    await db.refresh(printer)
    
    return {"message": f"Printer status updated to {status}"}
