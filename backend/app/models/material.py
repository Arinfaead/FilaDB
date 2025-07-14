"""
Material model
"""

from sqlalchemy import Column, String, DateTime, Integer, DECIMAL
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid

from ..database import Base


class Material(Base):
    __tablename__ = "materials"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False)
    density = Column(DECIMAL(5, 3), nullable=False)  # g/cm³
    extruder_temp_min = Column(Integer)
    extruder_temp_max = Column(Integer)
    bed_temp_min = Column(Integer)
    bed_temp_max = Column(Integer)
    properties = Column(JSONB, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Material(id={self.id}, name='{self.name}', density={self.density})>"
