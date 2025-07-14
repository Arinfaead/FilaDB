"""
Spool model
"""

from sqlalchemy import Column, String, DateTime, ForeignKey, DECIMAL, Boolean, Date, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from ..database import Base


class Spool(Base):
    __tablename__ = "spools"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filament_id = Column(UUID(as_uuid=True), ForeignKey("filaments.id", ondelete="CASCADE"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    printer_id = Column(UUID(as_uuid=True), ForeignKey("printers.id", ondelete="SET NULL"), nullable=True)
    weight = Column(DECIMAL(8, 2), nullable=False)  # Total weight in grams
    remaining_weight = Column(DECIMAL(8, 2), nullable=False)  # Remaining weight in grams
    spool_weight = Column(DECIMAL(8, 2))  # Empty spool weight in grams
    color = Column(String(100))
    hex_color = Column(String(7))  # Hex color code
    diameter = Column(DECIMAL(4, 2), nullable=False)  # Diameter in mm
    purchase_date = Column(Date)
    purchase_price = Column(DECIMAL(10, 2))
    location = Column(String(255))
    nfc_tag_id = Column(String(255), unique=True)
    qr_code = Column(String(255), unique=True)
    notes = Column(Text)
    custom_fields = Column(JSONB, default={})
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    filament = relationship("Filament", backref="spools")
    user = relationship("User", backref="spools")
    printer = relationship("Printer", backref="spools")

    @property
    def filament_used(self):
        """Calculate filament used in grams"""
        if self.spool_weight:
            return self.weight - self.remaining_weight
        return None

    @property
    def usage_percentage(self):
        """Calculate usage percentage"""
        if self.spool_weight:
            filament_weight = self.weight - self.spool_weight
            used_weight = self.weight - self.remaining_weight
            if filament_weight > 0:
                return (used_weight / filament_weight) * 100
        return None

    def __repr__(self):
        return f"<Spool(id={self.id}, color='{self.color}', remaining={self.remaining_weight}g)>"
