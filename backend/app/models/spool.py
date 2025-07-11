from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime


class SpoolBase(SQLModel):
    filament_id: int = Field(foreign_key="filament.id", index=True)
    remaining_weight_g: float  # Current remaining weight
    location: Optional[str] = None  # Where the spool is stored
    lot_number: Optional[str] = None  # Batch/lot number from manufacturer
    purchase_date: Optional[datetime] = None
    first_used: Optional[datetime] = None
    last_used: Optional[datetime] = None
    notes: Optional[str] = None


class Spool(SpoolBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
    
    # Relationship to filament
    # filament: Optional["Filament"] = Relationship(back_populates="spools")


class SpoolCreate(SpoolBase):
    pass


class SpoolRead(SpoolBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None


class SpoolUpdate(SQLModel):
    remaining_weight_g: Optional[float] = None
    location: Optional[str] = None
    lot_number: Optional[str] = None
    purchase_date: Optional[datetime] = None
    first_used: Optional[datetime] = None
    last_used: Optional[datetime] = None
    notes: Optional[str] = None
