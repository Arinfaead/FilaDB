"""
Printer model
"""

from sqlalchemy import Column, String, DateTime, ForeignKey, Enum, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

from ..database import Base


class PrinterStatus(str, enum.Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    PRINTING = "printing"
    PAUSED = "paused"
    ERROR = "error"


class Printer(Base):
    __tablename__ = "printers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    type = Column(String(100))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    status = Column(Enum(PrinterStatus), default=PrinterStatus.OFFLINE, nullable=False)
    location = Column(String(255))
    notes = Column(Text)
    settings = Column(JSONB, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", backref="printers")

    def __repr__(self):
        return f"<Printer(id={self.id}, name='{self.name}', status='{self.status}')>"
