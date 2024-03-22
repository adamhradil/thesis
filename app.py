# pylint: disable=missing-module-docstring, missing-function-docstring, missing-class-docstring, unused-argument

import datetime
import json
import time
import sys
import os

from scrapy import signals  # type: ignore
from scrapy.crawler import CrawlerProcess  # type: ignore
from scrapy.exporters import JsonItemExporter  # type: ignore
from geopy.geocoders import Nominatim  # type: ignore
from geopy import Point  # type: ignore
import pandas as pd  # type: ignore
from tabulate import tabulate  # type: ignore
from discord_webhook import DiscordWebhook, DiscordEmbed


from bezrealitky_scraper.bezrealitky.spiders.search_flats import SearchFlatsSpider
from sreality_scraper.sreality.spiders.sreality_spider import SrealitySpider

from database_wrapper import DatabaseWrapper
from furnished import Furnished
from property_status import PropertyStatus
from property_type import PropertyType
from listing import Listing
from user_preferences import UserPreferences
from disposition import Disposition
from listings_clearner import clean_listing_database
from dotenv import load_dotenv


items = []
load_dotenv()
webhook_url = os.getenv("WEBHOOK_URL")
if webhook_url == "" or webhook_url is None:
    print("Webhook URL not found in .env file")
    sys.exit(1)

def prepare_output(df: pd.DataFrame):
    df = df.sort_values(by="sum", ascending=False, inplace=False)
    df["rent"] = df["rent"].apply(lambda x: str(int(x)) + " Kč")
    df["area"] = df["area"].apply(lambda x: str(int(x)) + " m2")
    df["sum"] = df["sum"].apply(lambda x: str(int(round(x, 2) * 100)) + "/100")
    listings_to_send = df.head(5)
    print(
        tabulate(
            listings_to_send[["sum", "address", "rent", "disposition", "area", "url"]],
            tablefmt="grid",
            headers=["id", "sum", "address", "rent", "disposition", "area", "url"],
        )
    )
    return df.head(5)


def send_listings(df: pd.DataFrame):

    df = prepare_output(df)
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
    for l in df.to_dict(orient="records"):
        embed.add_embed_field(
            name=f"{l['sum']} - {l['address']}",
            value=f"{l['rent']}\n{l['disposition']} - {l['area']}\n{l['url']}",
            inline=False,
        )

    webhook.add_embed(embed)
    response = webhook.execute()
    if response.status_code != 200:
        print("Error sending the message to discord")


def get_point(address) -> None | Point:
    geolocator = Nominatim(user_agent="distance_calculator")
    location = geolocator.geocode(address)
    if location:
        return Point(location.latitude, location.longitude)  # type: ignore
    else:
        return None


def item_scraped(item):
    print(item["url"])
    items.append(item)


def update_db(db_file: str, last_crawl_time: datetime.datetime):
    print("updating the listing database")
    start = time.time()
    db = DatabaseWrapper(db_file)
    db.create_table()
    if listings is None:
        print("no listings found")
        return
    for listing in listings:
        found_listing = db.get_listing(listing.id)
        if found_listing:
            if (
                found_listing != listing
                and found_listing.updated
                and datetime.datetime.strptime(
                    found_listing.updated, "%Y-%m-%d %H:%M:%S.%f"
                )
                < last_crawl_time
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
                    date_updated=last_crawl_time,
                    last_seen=last_crawl_time,
                )
            else:
                db.update_listing(
                    listing,
                    created=found_listing.created,
                    date_updated=found_listing.updated,
                    last_seen=last_crawl_time,
                )
            continue
        db.insert_listing(listing=listing, date_created=last_crawl_time)
        print(f"found a new listing: {listing.id}")
    db.close_conn()
    end = time.time()
    print(f"updating db took {end - start}s")


def get_res(db_file: str, user_preferences: UserPreferences, user_weights: dict):

    df = clean_listing_database(db_file)

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
    df = user_preferences.filter_listings(df)
    df = user_preferences.calculate_score(df, user_weights)
    send_listings(df)


def crawl_lisings(json_output: str):
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

    start = time.time()

    crawler = process.create_crawler(SearchFlatsSpider)
    crawler.signals.connect(item_scraped, signal=signals.item_scraped)
    crawler2 = process.create_crawler(SrealitySpider)
    crawler2.signals.connect(item_scraped, signal=signals.item_scraped)
    process.crawl(crawler)
    process.crawl(crawler2)
    process.start()

    with open(file=json_output, mode="wb") as output_file:
        exporter = JsonItemExporter(output_file)
        exporter.start_exporting()
        for item in items:
            exporter.export_item(item)
        exporter.finish_exporting()

    end = time.time()

    if start != 0.0 and end != 0.0:
        print(f"crawling finished in {end - start}s")


if __name__ == "__main__":

    CRAWL = True
    SCRAPER_OUTPUT_FILE = "all_items.json"
    POI = "NTK Praha"
    DB_FILE = "listings.db"

    crawl_time = datetime.datetime.now()

    if CRAWL:
        crawl_lisings(SCRAPER_OUTPUT_FILE)
    else:
        with open(SCRAPER_OUTPUT_FILE, "r", encoding="utf-8") as f:
            items = json.load(f)

    listings = []
    for i in items:
        listings.append(Listing(i))

    update_db(DB_FILE, crawl_time)

    poi_point = get_point(POI)
    poi_point_2 = get_point("GRAM Praha")
    if poi_point is None or poi_point_2 is None:
        print("Could not find the point of interest")
        sys.exit(1)

    preferences = UserPreferences()
    # preferences.location = "Praha"
    # preferences.points_of_interest = [poi_point, poi_point_2]
    # preferences.disposition = [
    #     Disposition.TWO_PLUS_KK,
    #     Disposition.TWO_PLUS_ONE,
    #     Disposition.THREE_PLUS_KK,
    #     Disposition.THREE_PLUS_ONE,
    #     Disposition.FOUR_PLUS_KK,
    #     Disposition.FOUR_PLUS_ONE,
    # ]
    # preferences.min_area = 50
    preferences.max_area = 80
    # preferences.min_price = 25000
    preferences.max_price = 30000
    # preferences.balcony = True
    # preferences.terrace = True

    # preferences.floor = 3

    scoring_weights = {
        "normalized_area": 3,
        "normalized_rent": 3,
        "normalized_disposition": 0,
        "normalized_garden": 0,
        "normalized_balcony": 1.5,
        "normalized_cellar": 0,
        "normalized_loggie": 0,
        "normalized_elevator": 0,
        "normalized_terrace": 1.5,
        "normalized_garage": 0,
        "normalized_parking": 0,
        "normalized_poi_distance": 3,
    }

    get_res(DB_FILE, preferences, scoring_weights)
