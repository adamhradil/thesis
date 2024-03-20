# pylint: disable=missing-module-docstring, missing-function-docstring, missing-class-docstring, unused-argument

import datetime
import json
import time
import sys

from scrapy import signals  # type: ignore
from scrapy.crawler import CrawlerProcess  # type: ignore
from scrapy.exporters import JsonItemExporter  # type: ignore

from database_wrapper import DatabaseWrapper

from bezrealitky_scraper.bezrealitky.spiders.search_flats import SearchFlatsSpider
from sreality_scraper.sreality.spiders.sreality_spider import SrealitySpider

from listing import Listing
from user_preferences import UserPreferences
from disposition import Disposition
from listings_clearner import clean_listing_database, get_point

# from sreality_scraper.sreality.spiders.sreality_spider import SrealitySpider

items = []


def get_point(address) -> None | Point:
    geolocator = Nominatim(user_agent="distance_calculator")
    location = geolocator.geocode(address)
    if location:
        return Point(location.latitude, location.longitude)  # type: ignore
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
    for advert in listings:
        if "balk" in advert.description.lower():
            l1.append(advert)
        if advert.balcony:
            l2.append(advert)
        if "balk" in advert.description.lower() and advert.balcony:
            l3.append(advert)
        if "balk" in advert.description.lower() and not advert.balcony:
            l4.append(advert)

    print(f"{len(l1)} listings contain balk in description")
    print(f"{len(l2)} listings contain contain balk in the table")
    print(f"{len(l3)} listings contain contain balk in description and in table")
    print(f"{len(l4)} listings contain contain balk in description and not in table")
    return


def item_scraped(item):
    print(item["url"])
    items.append(item)


if __name__ == "__main__":

    CRAWL = True
    # FILE = "bezrealitky_items.json"
    # FILE = "sreality_items.json"
    FILE = "all_items.json"
    POI = "NTK Praha"
    start = 0.0
    end = 0.0

    crawl_time = datetime.datetime.now()

    if CRAWL:
        process = CrawlerProcess(
            settings={
                "LOG_LEVEL": "INFO",
                "DEFAULT_REQUEST_HEADERS": {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36",
                },
            }
        )

        start = time.time()

        crawler = process.create_crawler(SearchFlatsSpider)
        crawler.signals.connect(item_scraped, signal=signals.item_scraped)
        crawler2 = process.create_crawler(SrealitySpider)
        crawler2.signals.connect(item_scraped, signal=signals.item_scraped)
        process.crawl(crawler)
        process.crawl(crawler2)
        process.start()

        with open(file=FILE, mode="wb") as f:
            exporter = JsonItemExporter(f)
            exporter.start_exporting()
            for i in items:
                exporter.export_item(i)
            exporter.finish_exporting()

        end = time.time()
    else:
        with open(FILE, "r", encoding="utf-8") as f:
            items = json.load(f)

    listings = []
    for i in items:
        listings.append(Listing(i))

    poi_point = get_point(POI)
    if poi_point is None:
        print("Could not find the point of interest")
        sys.exit(1)
    print(repr(tuple(poi_point)))

    preferences = UserPreferences()
    preferences.location = "Praha"
    preferences.points_of_interest = [poi_point]
    preferences.disposition = [Disposition.ONE_PLUS_KK]
    preferences.min_area = 50
    preferences.max_area = 100
    preferences.max_price = 30000

    balcony_filter(listings)

    listings = clean_listings(listings=listings)

    db = DatabaseWrapper("listings.db")
    db.create_table()
    for listing in listings:
        found_listing = db.get_listing(listing.id)
        if found_listing:
            if (
                found_listing != listing
                and datetime.datetime.strptime(
                    found_listing.updated, "%Y-%m-%d %H:%M:%S.%f"
                )
                < crawl_time
            ):
                print(f"listing {listing.id} has changed:", end=" ")
                for attr, value in listing.__dict__.items():
                    if (
                        found_listing.__dict__[attr] != value
                        and attr != "updated"
                        and attr != "last_seen"
                        and attr != "created"
                        and attr != "description"
                    ):
                        print(
                            f"{attr} has changed from {found_listing.__dict__[attr]} to {value}"
                        )
                print("")
                db.update_listing(
                    listing,
                    created=found_listing.created,
                    date_updated=crawl_time,
                    last_seen=crawl_time,
                )
            else:
                db.update_listing(
                    listing,
                    created=found_listing.created,
                    date_updated=found_listing.updated,
                    last_seen=crawl_time,
                )
            continue
        db.insert_listing(listing=listing, date_created=crawl_time)
        print(f"found a new listing: {listing.id}")
    df = db.get_df()
    db.close_conn()


    df = clean_listing_database(DB_FILE)
