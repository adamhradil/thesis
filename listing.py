from enum import Enum
import scrapy
from user_preferences import UserPreferences


attributes = [
    "id",
    "address",
    "area",
    "available_from",
    "description",
    "disposition",
    "floor",
    "furnished",
    "rent",
    "security_deposit",
    "service_fees",
    "status",
    "type",
    "url",
    "balcony",
    "cellar",
    "garden",
    "terrace",
    "elevator",
    "parking",
    "garage",
    "pets",
    "loggie",
    "public_transport",
    "gps_lat",
    "gps_lon",
    "created",
    "updated",
    "last_seen",
]


class Listing:
    def __init__(self, data=None):
        attributes.sort()

        if data is None:
            for attr in attributes:
                setattr(self, attr, None)
        if isinstance(data, tuple):
            for i, attr in enumerate(attributes):
                setattr(self, attr, data[i])
        elif isinstance(data, scrapy.Item) or isinstance(data, dict):
            for attr in attributes:
                setattr(self, attr, data.get(attr, ""))

    def __eq__(self, other):
        if isinstance(other, Listing):
            excluded_attributes = ["last_seen", "updated", "created"]
            return all(
                getattr(self, attr) == getattr(other, attr)
                for attr in attributes
                if attr not in excluded_attributes
            )
        return False

    def __str__(self):
        return str(self.__dict__)

    def is_relevant(self, user_preferences: UserPreferences):
        if (
            user_preferences.dispositions
            and self.disposition not in user_preferences.dispositions
        ):
            return False
        if user_preferences.min_area and self.area < user_preferences.min_area:
            return False
        if user_preferences.max_area and self.area > user_preferences.max_area:
            return False
        if user_preferences.min_price and self.rent < user_preferences.min_price:
            return False
        if user_preferences.max_price and self.rent > user_preferences.max_price:
            return False
        if (
            user_preferences.ownership_type
            and self.type not in user_preferences.ownership_type
        ):
            return False
        if user_preferences.state and self.status not in user_preferences.state:
            return False
        if (
            user_preferences.property_material
            and self.penb not in user_preferences.property_material
        ):
            return False
        if user_preferences.furnished and self.furnished != user_preferences.furnished:
            return False
        if (
            user_preferences.balcony is not None
            and self.balcony != user_preferences.balcony
        ):
            return False
        if (
            user_preferences.terrace is not None
            and self.terrace != user_preferences.terrace
        ):
            return False
        if (
            user_preferences.loggia is not None
            and self.loggie != user_preferences.loggia
        ):
            return False
        if (
            user_preferences.cellar is not None
            and self.cellar != user_preferences.cellar
        ):
            return False
        if (
            user_preferences.garden is not None
            and self.garden != user_preferences.garden
        ):
            return False
        return True

    def calculate_score(self, user_preferences: UserPreferences):
        pass


class Disposition(Enum):
    ONE_PLUS_KK = "1+kk"
    ONE_PLUS_ONE = "1+1"
    TWO_PLUS_KK = "2+kk"
    TWO_PLUS_ONE = "2+1"
    THREE_PLUS_KK = "3+kk"
    THREE_PLUS_ONE = "3+1"
    FOUR_PLUS_KK = "4+kk"
    FOUR_PLUS_ONE = "4+1"
    FIVE_PLUS_KK = "5+kk"
    FIVE_PLUS_ONE = "5+1"
    OTHER = "Ostatní"


class OwnershipType(Enum):
    PERSONAL = "Osobní"
    COOPERATIVE = "Družstevní"
    OTHER = "Ostatní"


class PropertyState(Enum):
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


class PropertyMaterial(Enum):
    CONCRETE = "Panel"
    BRICK = "Cihla"
    OTHER = "Ostatní"


class Furnished(Enum):
    YES = "Vybaveno"
    NO = "Nevybaveno"
    PARTIALY = "Částečně"
