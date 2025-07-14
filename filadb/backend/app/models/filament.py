"""
Filament model
"""

from sqlalchemy import Column, String, DateTime, Integer, DECIMAL, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from ..database import Base


class Filament(Base):
    __tablename__ = "filaments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    manufacturer_id = Column(UUID(as_uuid=True), ForeignKey("manufacturers.id", ondelete="CASCADE"))
    material_id = Column(UUID(as_uuid=True), ForeignKey("materials.id", ondelete="CASCADE"))
    name = Column(String(255), nullable=False)
    density = Column(DECIMAL(5, 3))
    extruder_temp_min = Column(Integer)
    extruder_temp_max = Column(Integer)
    bed_temp_min = Column(Integer)
    bed_temp_max = Column(Integer)
    colors = Column(JSONB, default=[])  # Array of color objects
    weights = Column(JSONB, default=[])  # Array of weight options
    diameters = Column(JSONB, default=[])  # Array of diameter options
    settings = Column(JSONB, default={})  # Additional settings
    spoolman_db_id = Column(String(255))  # Reference to SpoolmanDB
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    manufacturer = relationship("Manufacturer", backref="filaments")
    material = relationship("Material", backref="filaments")

    def __repr__(self):
        return f"<Filament(id={self.id}, name='{self.name}')>"
