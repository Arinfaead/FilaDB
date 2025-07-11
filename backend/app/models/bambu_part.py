from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class BambuPartBase(SQLModel):
    item_type: str = Field(index=True)  # e.g., "nozzle", "hotend", "belt", etc.
    part_number: str = Field(index=True)  # Manufacturer part number
    printer_compatibility: str  # Compatible printer models (comma-separated)
    stock: int = Field(default=0)  # Current stock quantity
    supplier_url: Optional[str] = None  # URL to purchase the part
    notes: Optional[str] = None


class BambuPart(BambuPartBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)


class BambuPartCreate(BambuPartBase):
    pass


class BambuPartRead(BambuPartBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None


class BambuPartUpdate(SQLModel):
    item_type: Optional[str] = None
    part_number: Optional[str] = None
    printer_compatibility: Optional[str] = None
    stock: Optional[int] = None
    supplier_url: Optional[str] = None
    notes: Optional[str] = None
