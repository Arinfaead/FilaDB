"""
Print Job model
"""

from sqlalchemy import Column, String, DateTime, ForeignKey, DECIMAL, Text, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

from ..database import Base


class PrintJobStatus(str, enum.Enum):
    QUEUED = "queued"
    PRINTING = "printing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class PrintJob(Base):
    __tablename__ = "print_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    printer_id = Column(UUID(as_uuid=True), ForeignKey("printers.id", ondelete="CASCADE"))
    spool_id = Column(UUID(as_uuid=True), ForeignKey("spools.id", ondelete="SET NULL"), nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    job_name = Column(String(255))
    start_time = Column(DateTime(timezone=True))
    end_time = Column(DateTime(timezone=True))
    filament_used = Column(DECIMAL(8, 2))  # Filament used in grams
    status = Column(Enum(PrintJobStatus), default=PrintJobStatus.QUEUED, nullable=False)
    notes = Column(Text)
    metadata = Column(JSONB, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    printer = relationship("Printer", backref="print_jobs")
    spool = relationship("Spool", backref="print_jobs")
    user = relationship("User", backref="print_jobs")

    @property
    def duration(self):
        """Calculate print duration"""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None

    def __repr__(self):
        return f"<PrintJob(id={self.id}, job_name='{self.job_name}', status='{self.status}')>"
