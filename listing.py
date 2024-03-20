from enum import Enum
import scrapy
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
        self.rent = self._value_factory("rent", data)
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
        self.pets = self._value_factory("pets", data)
        self.loggie = self._value_factory("loggie", data)
        self.public_transport = self._value_factory("public_transport", data)
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
                for attr in [attr for attr in dir(self) if not callable(getattr(self, attr)) and not attr.startswith("__")]
                if attr not in excluded_attributes
            )
        return False

    def __str__(self):
        return str(self.__dict__)

    def _value_factory(self, attribute: str, data: dict | scrapy.Item | tuple | None):
        if data is None:
            return None
        if isinstance(data, scrapy.Item) or isinstance(data, dict):
            return data.get(attribute, "")

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


