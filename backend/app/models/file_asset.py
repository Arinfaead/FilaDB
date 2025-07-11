from sqlmodel import SQLModel, Field
from typing import Optional, List
from datetime import datetime


class FileAssetBase(SQLModel):
    name: str = Field(index=True)
    description: Optional[str] = None
    tags: Optional[List[str]] = Field(default=None)  # JSON array of tags
    current_version_hash: Optional[str] = None  # SHA256 of current version
    created_by_id: int = Field(foreign_key="user.id", index=True)


class FileAsset(FileAssetBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)


class FileAssetCreate(FileAssetBase):
    pass


class FileAssetRead(FileAssetBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None


class FileAssetUpdate(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
