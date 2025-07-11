import httpx
import logging
from typing import Dict, Any, List
from sqlmodel import Session, select
from ..core.config import settings
from ..models.filament import Filament, FilamentCreate

logger = logging.getLogger(__name__)


async def fetch_spoolmandb_data() -> Dict[str, Any]:
    """Fetch filament data from SpoolmanDB"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(settings.spoolmandb_url)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        logger.error(f"Failed to fetch SpoolmanDB data: {e}")
        raise


def flatten_spoolmandb_entry(entry: Dict[str, Any]) -> List[FilamentCreate]:
    """
    Flatten a SpoolmanDB entry into multiple FilamentCreate objects
    Each combination of weight, color, and diameter becomes a separate entry
    """
    filaments = []
    
    # Extract base information
    manufacturer = entry.get("manufacturer", "")
    name = entry.get("name", "")
    material = entry.get("material", "").upper()
    density = entry.get("density", 0.0)
    
    # Temperature settings
    extruder_temp = entry.get("extruder_temp")
    extruder_temp_min = entry.get("extruder_temp_min")
    extruder_temp_max = entry.get("extruder_temp_max")
    bed_temp = entry.get("bed_temp")
    bed_temp_min = entry.get("bed_temp_min")
    bed_temp_max = entry.get("bed_temp_max")
    
    # Material properties
    finish = entry.get("finish")
    multi_color_direction = entry.get("multi_color_direction")
    pattern = entry.get("pattern")
    translucent = entry.get("translucent", False)
    glow = entry.get("glow", False)
    
    # Get weights, diameters, and colors
    weights = entry.get("weights", [])
    diameters = entry.get("diameters", [])
    colors = entry.get("colors", [])
    
    # Create combinations
    for weight_info in weights:
        weight_g = weight_info.get("weight", 0.0)
        spool_weight_g = weight_info.get("spool_weight")
        spool_type = weight_info.get("spool_type")
        
        for diameter in diameters:
            for color in colors:
                color_name = color.get("name", "")
                color_hex = color.get("hex", "#000000")
                color_hexes = color.get("hexes")  # For multi-color filaments
                
                # Color-specific properties can override base properties
                color_finish = color.get("finish", finish)
                color_multi_color_direction = color.get("multi_color_direction", multi_color_direction)
                color_pattern = color.get("pattern", pattern)
                color_translucent = color.get("translucent", translucent)
                color_glow = color.get("glow", glow)
                
                # Create the filament name with color
                filament_name = name.replace("{color_name}", color_name) if "{color_name}" in name else f"{name} {color_name}"
                
                filament = FilamentCreate(
                    manufacturer=manufacturer,
                    name=filament_name,
                    material=material,
                    density=density,
                    weight_g=weight_g,
                    spool_weight_g=spool_weight_g,
                    spool_type=spool_type,
                    diameter_mm=diameter,
                    extruder_temp=extruder_temp,
                    extruder_temp_min=extruder_temp_min,
                    extruder_temp_max=extruder_temp_max,
                    bed_temp=bed_temp,
                    bed_temp_min=bed_temp_min,
                    bed_temp_max=bed_temp_max,
                    finish=color_finish,
                    multi_color_direction=color_multi_color_direction,
                    pattern=color_pattern,
                    translucent=color_translucent,
                    glow=color_glow,
                    color_name=color_name,
                    color_hex=color_hex,
                    color_hexes=color_hexes,
                    is_custom=False,
                    spoolmandb_id=entry.get("id")
                )
                
                filaments.append(filament)
    
    return filaments


async def sync_spoolmandb(session: Session):
    """Synchronize filament data from SpoolmanDB"""
    try:
        logger.info("Starting SpoolmanDB synchronization")
        
        # Fetch data from SpoolmanDB
        data = await fetch_spoolmandb_data()
        
        # Clear existing SpoolmanDB entries (keep custom ones)
        statement = select(Filament).where(Filament.is_custom == False)
        existing_filaments = session.exec(statement).all()
        
        for filament in existing_filaments:
            session.delete(filament)
        
        session.commit()
        
        # Process and insert new data
        total_inserted = 0
        
        for entry in data:
            try:
                flattened_filaments = flatten_spoolmandb_entry(entry)
                
                for filament_data in flattened_filaments:
                    db_filament = Filament(**filament_data.dict())
                    session.add(db_filament)
                    total_inserted += 1
                
            except Exception as e:
                logger.error(f"Error processing SpoolmanDB entry {entry.get('id', 'unknown')}: {e}")
                continue
        
        session.commit()
        logger.info(f"SpoolmanDB sync completed. Inserted {total_inserted} filament entries")
        
    except Exception as e:
        logger.error(f"SpoolmanDB sync failed: {e}")
        session.rollback()
        raise


def sync_spoolmandb_sync(session: Session):
    """Synchronous wrapper for SpoolmanDB sync (for background tasks)"""
    import asyncio
    asyncio.run(sync_spoolmandb(session))
