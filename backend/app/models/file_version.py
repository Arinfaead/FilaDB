from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class FileVersionBase(SQLModel):
    file_asset_id: int = Field(foreign_key="fileasset.id", index=True)
    file_hash: str = Field(index=True)  # SHA256 hash for deduplication
    file_path: str  # Path to the actual file on disk
    file_size: int  # File size in bytes
    original_filename: str  # Original filename when uploaded
    mime_type: Optional[str] = None
    notes: Optional[str] = None
    created_by_id: int = Field(foreign_key="user.id", index=True)


class FileVersion(FileVersionBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class FileVersionCreate(FileVersionBase):
    pass


class FileVersionRead(FileVersionBase):
    id: int
    created_at: datetime


class FileVersionUpdate(SQLModel):
    notes: Optional[str] = None
