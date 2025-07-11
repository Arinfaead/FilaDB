from sqlmodel import SQLModel, Field
from typing import Optional, List
from enum import Enum


class SpoolType(str, Enum):
    PLASTIC = "plastic"
    CARDBOARD = "cardboard"
    METAL = "metal"


class Fill(str, Enum):
    GLASS_FIBER = "glass fiber"
    CARBON_FIBER = "carbon fiber"
    WOOD = "wood"


class Finish(str, Enum):
    MATTE = "matte"
    GLOSSY = "glossy"


class MultiColorDirection(str, Enum):
    COAXIAL = "coaxial"
    LONGITUDINAL = "longitudinal"


class Pattern(str, Enum):
    MARBLE = "marble"
    SPARKLE = "sparkle"


class FilamentBase(SQLModel):
    manufacturer: str = Field(index=True)
    name: str = Field(index=True)  # Should contain {color_name}
    material: str = Field(index=True)  # UPPERCASE, may include +/- and optional -CF or -GF suffix
    density: float  # g/cm³
    weight_g: float  # spool gross weight
    spool_weight_g: Optional[float] = None  # empty spool weight
    spool_type: Optional[SpoolType] = None
    diameter_mm: float  # supports multiple diameters – store one row per combination
    
    # Temperature settings
    extruder_temp: Optional[int] = None  # °C
    extruder_temp_min: Optional[int] = None  # °C
    extruder_temp_max: Optional[int] = None  # °C
    bed_temp: Optional[int] = None  # °C
    bed_temp_min: Optional[int] = None  # °C
    bed_temp_max: Optional[int] = None  # °C
    
    # Material properties
    fill: Optional[Fill] = None
    finish: Optional[Finish] = None
    multi_color_direction: Optional[MultiColorDirection] = None
    pattern: Optional[Pattern] = None
    translucent: bool = Field(default=False)
    glow: bool = Field(default=False)
    
    # Color information
    color_name: str = Field(index=True)
    color_hex: str  # #RRGGBB[AA]
    color_hexes: Optional[List[str]] = Field(default=None)  # for multi-colour filaments
    
    # Metadata
    is_custom: bool = Field(default=False)  # True for manually added filaments
    spoolmandb_id: Optional[str] = None  # Original ID from SpoolmanDB


class Filament(FilamentBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class FilamentCreate(FilamentBase):
    pass


class FilamentRead(FilamentBase):
    id: int


class FilamentUpdate(SQLModel):
    manufacturer: Optional[str] = None
    name: Optional[str] = None
    material: Optional[str] = None
    density: Optional[float] = None
    weight_g: Optional[float] = None
    spool_weight_g: Optional[float] = None
    spool_type: Optional[SpoolType] = None
    diameter_mm: Optional[float] = None
    extruder_temp: Optional[int] = None
    extruder_temp_min: Optional[int] = None
    extruder_temp_max: Optional[int] = None
    bed_temp: Optional[int] = None
    bed_temp_min: Optional[int] = None
    bed_temp_max: Optional[int] = None
    fill: Optional[Fill] = None
    finish: Optional[Finish] = None
    multi_color_direction: Optional[MultiColorDirection] = None
    pattern: Optional[Pattern] = None
    translucent: Optional[bool] = None
    glow: Optional[bool] = None
    color_name: Optional[str] = None
    color_hex: Optional[str] = None
    color_hexes: Optional[List[str]] = None
