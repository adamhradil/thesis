from enum import Enum


class PropertyType(Enum):
    """
    Enum representing different property types.
    """
    CONCRETE = "Panel"
    BRICK = "Cihla"
    OTHER = "Ostatní"
