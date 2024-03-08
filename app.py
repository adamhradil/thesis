# TODO: vvv
# pylint: disable=missing-module-docstring, missing-function-docstring, missing-class-docstring, unused-argument

import json
import sys

from scrapy import signals
from scrapy.crawler import CrawlerProcess
from scrapy.exporters import JsonItemExporter

from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from database_wrapper import DatabaseWrapper

from bezrealitky_scraper.bezrealitky.spiders.search_flats import SearchFlatsSpider
from listing import Disposition, UserPreferences, Listing

# from sreality_scraper.sreality.spiders.sreality_spider import SrealitySpider

items = []


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


def clean_listings(listings):
    cleaned_listings = []
    seen_listings = set()

    for listing in listings:
        # Remove duplicates
        if str(listing) in seen_listings:
            continue
        seen_listings.add(str(listing))

        # Handle missing values
        for attr, value in listing.__dict__.items():
            if value == "":
                listing.__dict__[attr] = None  # or some default value

        # Validate data types
        # This is just an example for the 'area' attribute
        if listing.area is not None:
            try:
                listing.area = int(listing.area)
            except ValueError:
                continue  # skip this listing

        # Normalize text
        if listing.description is not None:
            listing.description = listing.description.lower().strip()

        cleaned_listings.append(listing)

    return cleaned_listings


def balcony_filter(listings: list[Listing]):
    l1 = []
    l2 = []
    l3 = []
    l4 = []
    for listing in listings:
        if "balk" in listing.description.lower():
            l1.append(listing)
        if listing.balcony:
            l2.append(listing)
        if "balk" in listing.description.lower() and listing.balcony:
            l3.append(listing)
        if "balk" in listing.description.lower() and not listing.balcony:
            l4.append(listing)

    print(f"{len(l1)} listings contain balk in description")
    print(f"{len(l2)} listings contain contain balk in the table")
    print(f"{len(l3)} listings contain contain balk in description and in table")
    print(f"{len(l4)} listings contain contain balk in description and not in table")
    return


def item_scraped(item):
    print(item['url'])
    items.append(item)


if __name__ == "__main__":

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

    balcony_filter(listings)

    listings = clean_listings(listings=listings)

    db = DatabaseWrapper('listings.db')
    db.create_table()
    for listing in listings:
        if db.get_listing(listing.id):
            continue
        db.insert_listing(listing)
        print(f"found a new listing: {listing.id}")
    db.close_conn()

    sys.exit(0)
