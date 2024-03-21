# pylint: disable=missing-module-docstring, missing-function-docstring, missing-class-docstring, unused-argument

import datetime
import json
import time
import sys

from scrapy import signals  # type: ignore
from scrapy.crawler import CrawlerProcess  # type: ignore
from scrapy.exporters import JsonItemExporter  # type: ignore
from geopy.geocoders import Nominatim  # type: ignore
from geopy import Point  # type: ignore
import pandas as pd

from discord_webhook import DiscordWebhook, DiscordEmbed

from database_wrapper import DatabaseWrapper

from bezrealitky_scraper.bezrealitky.spiders.search_flats import SearchFlatsSpider
from furnished import Furnished
from property_status import PropertyStatus
from property_type import PropertyType
from sreality_scraper.sreality.spiders.sreality_spider import SrealitySpider

from listing import Listing
from user_preferences import UserPreferences
from disposition import Disposition
from listings_clearner import clean_listing_database


# from sreality_scraper.sreality.spiders.sreality_spider import SrealitySpider

items = []


def send_listings(df: pd.DataFrame):
    df.sort_values(by="sum", ascending=False, inplace=True)
    listings_to_send = df.loc[df['sum'] >= 0.62].head(5).to_dict(orient='records')

    webhook = DiscordWebhook(url=webhook_url, username="Real Estate")

    embed = DiscordEmbed(
        title="Embed Title", description="Your Embed Description", color="03b2f8"
    )
    embed.set_author(
        name="Author Name",
        url="https://github.com/lovvskillz",
        icon_url="https://avatars0.githubusercontent.com/u/14542790",
    )
    embed.set_footer(text="Embed Footer Text")
    embed.set_timestamp()
    # Set `inline=False` for the embed field to occupy the whole line
    for l in listings_to_send:
        embed.add_embed_field(name=f"{int(round(l['sum'], 2)*100)}/100 - {l['address']}", value=f"{int(l['rent'])} Kč\n{int(l['area'])} m2\n{l['url']}", inline=False)


    webhook.add_embed(embed)
    response = webhook.execute()


def get_point(address) -> None | Point:
    geolocator = Nominatim(user_agent="distance_calculator")
    location = geolocator.geocode(address)
    if location:
        return Point(location.latitude, location.longitude)  # type: ignore
    else:
        return None


def balcony_filter(listings_list: list[Listing]):
    l1 = []
    l2 = []
    l3 = []
    l4 = []
    for advert in listings_list:
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
    DB_FILE = "listings.db"
    START = 0.0
    END = 0.0

    crawl_time = datetime.datetime.now()

    if CRAWL:
        process = CrawlerProcess(
            settings={
                "LOG_LEVEL": "INFO",
                "DEFAULT_REQUEST_HEADERS": {
                    "User-Agent": """Mozilla/5.0 (Windows NT 10.0; Win64; x64)
                        AppleWebKit/537.36 (KHTML, like Gecko)
                        Chrome/60.0.3112.113 Safari/537.36""",
                },
            }
        )

        START = time.time()

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

        END = time.time()
    else:
        with open(FILE, "r", encoding="utf-8") as f:
            items = json.load(f)

    listings = []
    for i in items:
        listings.append(Listing(i))

    poi_point = get_point(POI)
    poi_point_2 = get_point("GRAM Praha")
    if poi_point is None or poi_point_2 is None:
        print("Could not find the point of interest")
        sys.exit(1)

    # balcony_filter(listings)

    db = DatabaseWrapper(DB_FILE)
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

    if START != 0.0 and END != 0.0:
        print(f"crawling finished in {END - START}s")

    preferences = UserPreferences()
    # preferences.location = "Praha"
    # preferences.points_of_interest = [poi_point, poi_point_2]
    # preferences.disposition = [Disposition.TWO_PLUS_KK, Disposition.TWO_PLUS_ONE, Disposition.THREE_PLUS_KK, Disposition.THREE_PLUS_ONE, Disposition.FOUR_PLUS_KK, Disposition.FOUR_PLUS_ONE]
    # preferences.min_area = 50
    # preferences.max_area = 100
    # preferences.min_price = 25000
    # preferences.max_price = 30000
    # preferences.balcony = True
    # preferences.terrace = True

    # preferences.floor = 3

    scoring_weights = {
        "normalized_area": 0.9,
        "normalized_rent": 0.9,
        "normalized_disposition": 0.9,
        "normalized_garden": 0.9,
        "normalized_balcony": 0.9,
        "normalized_cellar": 0.9,
        "normalized_loggie": 0.9,
        "normalized_elevator": 0.9,
        "normalized_terrace": 0.9,
        "normalized_garage": 0.9,
        "normalized_parking": 0.9,
        "normalized_poi_distance": 2.1,
    }

    df = clean_listing_database(DB_FILE)

    df = df[
        [
            "address",
            "area",
            "rent",
            "disposition",
            "floor",
            "furnished",
            "garden",
            "type",
            "status",
            "ownership",
            "balcony",
            "cellar",
            "loggie",
            "elevator",
            "terrace",
            "garage",
            "parking",
            "gps_lat",
            "gps_lon",
            "url",
            "description",
            "available_from",
            "created",
            "updated",
            "last_seen",
        ]
    ]
    df = preferences.filter_listings(df)
    df = preferences.calculate_score(df, scoring_weights)
    send_listings(df)
