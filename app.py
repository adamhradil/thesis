# pylint: disable=missing-module-docstring, missing-function-docstring, missing-class-docstring, unused-argument

import datetime
import json
import time
import sys
import os

from scrapy.crawler import CrawlerProcess  # type: ignore
from scrapy.exporters import JsonItemExporter  # type: ignore
from geopy.geocoders import Nominatim  # type: ignore
from geopy import Point  # type: ignore
import pandas as pd  # type: ignore
from tabulate import tabulate  # type: ignore
from discord_webhook import DiscordWebhook, DiscordEmbed
from flask import Flask, render_template, flash, redirect, request, url_for
from dotenv import load_dotenv

from forms import UserPreferencesForm

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


CRAWL = False
LAST_CRAWL_FILE = "last_crawl.txt"
SCRAPER_OUTPUT_FILE = "scraped_listings.json"
POI = "NTK Praha"
DB_FILE = "listings.db"
items = []
load_dotenv()
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
if WEBHOOK_URL == "" or WEBHOOK_URL is None:
    print("Webhook URL not found in .env file")
    sys.exit(1)

app = Flask(__name__)
SECRET_KEY = os.urandom(32)
app.config["SECRET_KEY"] = SECRET_KEY


@app.route("/")
def index():
    user_preferences = load_preferences()
    df = analyze_listings(DB_FILE, user_preferences)
    return render_template(
        "index.html", utc_dt=datetime.datetime.utcnow(), listings_df=format_result(df)
    )


@app.route("/preferences", methods=["GET", "POST"])
def preferences():
    if request.method == "GET":        
        form = UserPreferencesForm(request.form)
        user_preferences = load_preferences()
        # loop through all fields of preferences
        for key, value in user_preferences.to_dict().items():
            if key == 'available_from':
                continue
            getattr(form, key).data = value
    # if submit is pushed
    if request.method == "POST":
        form = UserPreferencesForm(request.form)
        user_preferences = load_preferences()
        for key, value in form.data.items():
            if value is None or value == "":
                continue
            if key == "csrf_token" or key == "submit":
                continue
            if key == "disposition":
                user_preferences.disposition = [Disposition(x) for x in value]
                continue
            if key == "type":
                user_preferences.type = [PropertyType(x) for x in value]
                continue
            if key == "furnished":
                user_preferences.furnished = [Furnished(x) for x in value]
                continue
            if key == "status":
                user_preferences.status = [PropertyStatus(x) for x in value]
                continue
            if key == "points_of_interest":
                user_preferences.points_of_interest = [Point(value)]
                continue
            setattr(user_preferences, key, value)
        save_preferences(user_preferences)
    return render_template("preferences.html", title="Set Preferences", form=form)


def load_preferences() -> UserPreferences:
    if not os.path.exists("preferences.json"):
        return UserPreferences()

    with open("preferences.json", "r", encoding="utf-8") as f:
        user_preferences = json.load(f)

    return UserPreferences.from_dict(UserPreferences, data=user_preferences)


def save_preferences(user_preferences: UserPreferences) -> None:
    with open("preferences.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(user_preferences.to_dict()))


def crawl_regularly(crawl=True):
    global items
    if crawl:
        run_spiders(SCRAPER_OUTPUT_FILE)
    else:
        with open(SCRAPER_OUTPUT_FILE, "r", encoding='utf-8') as f:
            items = json.load(f)

    listings = []
    for item in items:
        listings.append(Listing(item))

    with open(LAST_CRAWL_FILE, "r", encoding="utf-8") as f:
        last_crawl_time = datetime.datetime.fromisoformat(f.read())

    update_listing_database(DB_FILE, listings, last_crawl_time)

    user_preferences = load_preferences()

    analyze_listings(DB_FILE, user_preferences)


def format_result(df: pd.DataFrame):
    df = df.sort_values(by="sum", ascending=False, inplace=False)
    df["rent"] = df["rent"].apply(lambda x: str(int(x)) + " Kč" if x > 0 else "")
    df["area"] = df["area"].apply(lambda x: str(int(x)) + " m2" if x > 0 else "")
    df["sum"] = df["sum"].apply(
        lambda x: str(int(round(x, 2) * 100)) + "/100" if x > 0 else ""
    )
    print(
        tabulate(
            df[["sum", "address", "rent", "disposition", "area", "url"]],
            tablefmt="grid",
            headers=["id", "sum", "address", "rent", "disposition", "area", "url"],
        )
    )
    return df


def notify_user(df: pd.DataFrame):
    with open(LAST_CRAWL_FILE, "r", encoding="utf-8") as f:
        last_crawl_time = datetime.datetime.fromisoformat(f.read())

    df = df[df["updated"] == str(last_crawl_time)]

    if df.empty:
        print("No new listings found")
        return
    df = format_result(df)
    if WEBHOOK_URL is None:
        print("Webhook URL not found in .env file")
        return
    webhook = DiscordWebhook(url=WEBHOOK_URL, username="Real Estate")

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
    # discord message length should be limited
    df = df.head(10)
    for record in df.to_dict(orient="records"):
        embed.add_embed_field(
            name=f"{record['sum']} - {record['address']}",
            value=f"{record['rent']}\n{record['disposition']} - {record['area']}\n{record['url']}",
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


def update_listing_database(
    db_file: str, listings: list[Listing], last_crawl_time: datetime.datetime
):
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


def analyze_listings(db_file: str, user_preferences: UserPreferences):
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
    if df.empty:
        print("No listings found after filtering")
        return df
    df = user_preferences.calculate_score(df)

    notify_user(df)
    return df


# pipeline to fill the items list
class ItemCollectorPipeline(object):
    def __init__(self):
        self.ids_seen = set()

    def process_item(self, item, spider):
        print(item["url"])
        items.append(item)


def run_spiders(json_output: str):
    process = CrawlerProcess(
        settings={
            "LOG_LEVEL": "INFO",
            "DEFAULT_REQUEST_HEADERS": {
                "User-Agent": """Mozilla/5.0 (Windows NT 10.0; Win64; x64)
                    AppleWebKit/537.36 (KHTML, like Gecko)
                    Chrome/60.0.3112.113 Safari/537.36""",
            },
            "ITEM_PIPELINES": { "__main__.ItemCollectorPipeline": 100 }
        }
    )

    start = time.time()
    preferences = load_preferences()
    spider_settings = {}
    spider_settings['listing_type'] = preferences.listing_type
    spider_settings['estate_type'] = preferences.estate_type
    spider_settings['location'] = preferences.location

    crawler = process.create_crawler(SearchFlatsSpider)
    crawler2 = process.create_crawler(SrealitySpider)
    
    process.crawl(crawler, spider_settings)
    process.crawl(crawler2, spider_settings)
    process.start()

    with open(file=json_output, mode="wb") as output_file:
        exporter = JsonItemExporter(output_file)
        exporter.start_exporting()
        for item in items:
            exporter.export_item(item)
        exporter.finish_exporting()
    print(
        f"{datetime.datetime.utcnow().isoformat()}: scraped items saved to {output_file}"
    )

    end = time.time()

    if start != 0.0 and end != 0.0:
        print(f"crawling finished in {end - start}s")

    # writing the last crawl time to a file
    with open(LAST_CRAWL_FILE, "w", encoding="utf-8") as f:
        f.write(datetime.datetime.utcnow().isoformat())


if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) > 0 and args[0] == "--crawl":
        crawl_regularly()
    else:
        app.run(debug=True)
