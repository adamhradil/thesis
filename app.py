# TODO: vvv
# pylint: disable=missing-module-docstring, missing-function-docstring, missing-class-docstring, unused-argument

import json
from enum import Enum

from scrapy import signals
from scrapy.crawler import CrawlerProcess
from scrapy.exporters import JsonItemExporter

from geopy.geocoders import Nominatim
from geopy.distance import geodesic

from bezrealitky_scraper.bezrealitky.spiders.search_flats import SearchFlatsSpider

# from sreality_scraper.sreality.spiders.sreality_spider import SrealitySpider


class Listing:
    def __init__(self, data: dict):
        self.address = data.get("address", "")
        self.area = data.get("area", "")
        self.available_from = data.get("available_from", "")
        self.description = data.get("description", "")
        self.disposition = data.get("disposition", "")
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
                URL: {self.url}"""

    def calculate_score(self, user_preferences):
        pass


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
        garden=None,
    ) -> None:
        self.dispositions: list[Disposition] = dispositions
        self.weight_area: float = weight_area
        self.weight_rent: float = weight_rent
        self.weight_location: float = weight_location
        self.min_area: int = min_area
        self.max_area: int = max_area
        self.min_price: int = min_price
        self.max_price: int = max_price
        self.ownership_type: list[OwnershipType] = ownership_type
        self.state: list[PropertyState] = state
        self.property_material: list[PropertyMaterial] = property_material
        self.furnished: Furnished = furnished
        self.balcony: bool = balcony
        self.terrace: bool = terrace
        self.loggia: bool = loggia
        self.cellar: bool = cellar
        self.garden: bool = garden


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


def get_coordinates(address):
    geolocator = Nominatim(user_agent="distance_calculator")
    location = geolocator.geocode(address)
    if location:
        return (location.latitude, location.longitude)
    else:
        return None


def calculate_distance(address1, address2):
    coord1 = get_coordinates(address1)
    coord2 = get_coordinates(address2)

    if coord1 and coord2:
        return geodesic(coord1, coord2).kilometers
    else:
        return None


def item_scraped(item):
    items.append(item)


if __name__ == "__main__":

    items = []

    CRAWL = False
    FILE = "bezrealitky_items.json"
    POI = "NTK Praha"

    if CRAWL:
        process = CrawlerProcess()
        # crawler = process.create_crawler(SrealitySpider)
        # crawler.signals.connect(item_scraped, signal=signals.item_scraped)
        crawler2 = process.create_crawler(SearchFlatsSpider)
        crawler2.signals.connect(item_scraped, signal=signals.item_scraped)
        # process.crawl(crawler)
        process.crawl(crawler2)
        process.start()

        with open(file=FILE, mode="wb") as f:
            exporter = JsonItemExporter(f)
            exporter.start_exporting()
            for i in items:
                exporter.export_item(i)
            exporter.finish_exporting()
    else:
        with open(FILE, "r", encoding="utf-8") as f:
            items = json.load(f)

    dist = calculate_distance(POI, items[0]["address"])

    print("test")
