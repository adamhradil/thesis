from enum import Enum


class UserPreferences:
    def __init__(
        self,
        dispositions=None,
        weight_area=None,
        weight_rent=None,
        weight_location=None,
        min_area=None,
        max_area=None,
        min_price=None,
        max_price=None,
        ownership_type=None,
        state=None,
        property_material=None,
        furnished=None,
        balcony=None,
        terrace=None,
        loggia=None,
        cellar=None,
        front_garden=None,
    ) -> None:
        self.dispositions: list[Disposition] | None = dispositions
        self.weight_area: float | None = weight_area
        self.weight_rent: float | None = weight_rent
        self.weight_location: float | None = weight_location
        self.min_area: int | None = min_area
        self.max_area: int | None = max_area
        self.min_price: int | None = min_price
        self.max_price: int | None = max_price
        self.ownership_type: list[OwnershipType] | None = ownership_type
        self.state: list[PropertyState] | None = state
        self.property_material: list[PropertyMaterial] | None = property_material
        self.furnished: Furnished | None = furnished
        self.balcony: bool | None = balcony
        self.terrace: bool | None = terrace
        self.loggia: bool | None = loggia
        self.cellar: bool | None = cellar
        self.front_garden: bool | None = front_garden


class Listing:
    def __init__(self, data: dict):
        self.address: str = data.get("address", "")
        self.area: int = data.get("area", "")
        self.available_from: str = data.get("available_from", "")
        self.description: str = data.get("description", "")
        self.disposition: str = data.get("disposition", "")
        self.floor = data.get("floor", "")
        self.furnished = data.get("furnished", "")
        self.id = data.get("id", "")
        self.penb = data.get("penb", "")
        self.rent = data.get("rent", "")
        self.security_deposit = data.get("security_deposit", "")
        self.service_fees = data.get("service_fees", "")
        self.status = data.get("status", "")
        self.type = data.get("type", "")
        self.url = data.get("url", "")
        self.balcony = data.get("balcony", "")
        self.cellar = data.get("cellar", "")
        self.front_garden = data.get("front_garden", "")
        self.terrace = data.get("terrace", "")
        self.elevator = data.get("elevator", "")
        self.parking = data.get("parking", "")
        self.garage = data.get("garage", "")
        self.pets = data.get("pets", "")
        self.loggie = data.get("loggie", "")
        self.public_transport = data.get("public_transport", "")

    def __eq__(self, other):
        if isinstance(other, Listing):
            return self.__dict__ == other.__dict__
        return False

    def __str__(self):
        return f"""Room Offer ID: {self.id}
                Address: {self.address}
                Area: {self.area} sq.m
                Available from: {self.available_from}
                Description: {self.description}
                Disposition: {self.disposition}
                Floor: {self.floor}
                Furnished: {self.furnished}
                Rent: {self.rent}
                Security Deposit: {self.security_deposit}
                Service Fees: {self.service_fees}
                Status: {self.status}
                Type: {self.type}
                URL: {self.url}
                Balcony: {self.balcony}
                Cellar: {self.cellar}
                Front Garden: {self.front_garden}
                Terrace: {self.terrace}
                Elevator: {self.elevator}
                Parking: {self.parking}
                Garage: {self.garage}
                Pets: {self.pets}
                Loggie: {self.loggie}
                Public Transport: {self.public_transport}
                """

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
            user_preferences.front_garden is not None
            and self.front_garden != user_preferences.front_garden
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
