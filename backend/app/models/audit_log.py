from sqlmodel import SQLModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class AuditLogBase(SQLModel):
    user_id: Optional[int] = Field(foreign_key="user.id", index=True)
    action: str = Field(index=True)  # e.g., 'CREATE_SPOOL', 'UPDATE_FILE', 'DELETE_USER'
    resource_type: str = Field(index=True)  # e.g., 'spool', 'file', 'user'
    resource_id: Optional[int] = None  # ID of the affected resource
    details: Optional[Dict[str, Any]] = Field(default=None)  # JSON details of the change
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class AuditLog(AuditLogBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    timestamp: datetime = Field(default_factory=datetime.utcnow, index=True)


class AuditLogCreate(AuditLogBase):
    pass


class AuditLogRead(AuditLogBase):
    id: int
    timestamp: datetime
