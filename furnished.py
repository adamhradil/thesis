from enum import Enum


class Furnished(Enum):
    """
    Enum representing the level of furnishing for a property.
    """
    YES = "Vybaveno"
    NO = "Nevybaveno"
    PARTIALY = "Částečně"
