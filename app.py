# TODO: vvv
# pylint: disable=missing-module-docstring, missing-function-docstring, missing-class-docstring, unused-argument

import json
from enum import Enum
import sys

from scrapy import signals
from scrapy.crawler import CrawlerProcess
from scrapy.exporters import JsonItemExporter

from geopy.geocoders import Nominatim
from geopy.distance import geodesic

from bezrealitky_scraper.bezrealitky.spiders.search_flats import SearchFlatsSpider

# from sreality_scraper.sreality.spiders.sreality_spider import SrealitySpider



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
    print(item['url'])
    items.append(item)


if __name__ == "__main__":

    items = []

    CRAWL = False
    FILE = "bezrealitky_items.json"
    POI = "NTK Praha"

    if CRAWL:
        process = CrawlerProcess(settings={"LOG_LEVEL": "INFO"})

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

    listings = []
    for i in items:
        listings.append(Listing(i))

    dist = calculate_distance(POI, items[0]["address"])

    preferences = UserPreferences(
        dispositions=[
            Disposition.TWO_PLUS_ONE,
            Disposition.THREE_PLUS_KK,
            Disposition.THREE_PLUS_ONE,
        ],
        weight_area=0.5,
        weight_rent=0.4,
        weight_location=0.1,
        min_area=50,
        max_price=30000,
        balcony=True,
    )

    sys.exit(0)
