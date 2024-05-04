import scrapy  # pylint: disable=import-error
from user_preferences import UserPreferences


class Listing:
    def __init__(self, data=None):
        self.id = self._value_factory("id", data)
        self.address = self._value_factory("address", data)
        self.area = self._value_factory("area", data)
        self.available_from = self._value_factory("available_from", data)
        self.description = self._value_factory("description", data)
        self.disposition = self._value_factory("disposition", data)
        self.floor = self._value_factory("floor", data)
        self.furnished = self._value_factory("furnished", data)
        self.price = self._value_factory("price", data)
        self.security_deposit = self._value_factory("security_deposit", data)
        self.service_fees = self._value_factory("service_fees", data)
        self.status = self._value_factory("status", data)
        self.type = self._value_factory("type", data)
        self.url = self._value_factory("url", data)
        self.balcony = self._value_factory("balcony", data)
        self.cellar = self._value_factory("cellar", data)
        self.garden = self._value_factory("garden", data)
        self.terrace = self._value_factory("terrace", data)
        self.elevator = self._value_factory("elevator", data)
        self.parking = self._value_factory("parking", data)
        self.garage = self._value_factory("garage", data)
        # self.pets = self._value_factory("pets", data)
        self.loggie = self._value_factory("loggie", data)
        self.ownership = self._value_factory("ownership", data)
        # self.public_transport = self._value_factory("public_transport", data)
        self.gps_lat = self._value_factory("gps_lat", data)
        self.gps_lon = self._value_factory("gps_lon", data)
        self.created = self._value_factory("created", data)
        self.updated = self._value_factory("updated", data)
        self.last_seen = self._value_factory("last_seen", data)

    def __eq__(self, other):
        if isinstance(other, Listing):
            excluded_attributes = ["last_seen", "updated", "created"]
            return all(
                getattr(self, attr) == getattr(other, attr)
                for attr in [
                    attr
                    for attr in dir(self)
                    if not callable(getattr(self, attr)) and not attr.startswith("__")
                ]
                if attr not in excluded_attributes
            )
        return False

    def __str__(self):
        return str(self.__dict__)

    def _value_factory(self, attribute: str, data: dict | scrapy.Item | tuple | None):
        if data is None:
            return None
        if isinstance(data, (scrapy.Item, dict)):
            return data.get(attribute, "")
        return None

    def calculate_score(self, user_preferences: UserPreferences):
        pass
