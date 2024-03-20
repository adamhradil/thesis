from enum import Enum


class PropertyStatus(Enum):
    NEW = "Novostavba"
    VERY_GOOD = "Velmi dobrý"
    GOOD = "Dobrý"
    WRONG = "Špatný"
    FOR_DEMOLITION = "K demolici"
    UNDER_CONSTRUCTION = "Ve výstavbě"
    RENOVATED = "Po rekonstrukci"
    FOR_RENOVATION = "Před rekonstrukcí"
    IN_RENOVATION = "V rekonstrukci"
    PROJECT = "Projekt"
