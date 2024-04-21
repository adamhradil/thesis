# pylint: disable=missing-module-docstring, missing-function-docstring, missing-class-docstring, unused-argument

import datetime
import json
import time
import sys
import os

from scrapy.crawler import CrawlerProcess  # type: ignore pylint: disable=import-error
from scrapy.exporters import JsonItemExporter  # type: ignore pylint: disable=import-error
from geopy.geocoders import Nominatim  # type: ignore pylint: disable=import-error
from geopy import Point  # type: ignore pylint: disable=import-error
import pandas as pd  # type: ignore pylint: disable=import-error
from discord_webhook import DiscordWebhook, DiscordEmbed  # pylint: disable=import-error
from flask import Flask, render_template, flash, redirect, request, url_for  # pylint: disable=import-error
from dotenv import load_dotenv

from forms import UserPreferencesForm

from bezrealitky_scraper.bezrealitky.spiders.search_flats import SearchFlatsSpider
from sreality_scraper.sreality.spiders.sreality_spider import SrealitySpider

from database_wrapper import DatabaseWrapper
from furnished import Furnished
from property_status import PropertyStatus
from property_type import PropertyType
from listing import Listing
from user_preferences import UserPreferences, SCORING_COLUMNS
from disposition import Disposition
from listings_cleaner import clean_listing_database


CRAWL = False
USER_DATA_DIR = "userdata"
if not os.path.exists(USER_DATA_DIR):
    os.makedirs(USER_DATA_DIR)
LAST_CRAWL_FILE = USER_DATA_DIR + "/" + "last_crawl.txt"
SCRAPER_OUTPUT_FILE = USER_DATA_DIR + "/" + "scraped_listings.json"
PREFERENCES_FILE = USER_DATA_DIR + "/" + "preferences.json"
POI = "NTK Praha"
DB_FILE = USER_DATA_DIR + "/" + "listings.db"
items = []
load_dotenv()
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
if WEBHOOK_URL == "" or WEBHOOK_URL is None:
    print("Webhook URL not found in .env file")
    sys.exit(1)

app = Flask(__name__)
SECRET_KEY = os.urandom(32)
app.config["SECRET_KEY"] = SECRET_KEY


@app.route("/", methods=["GET", "POST"])
def index():
    user_preferences = load_preferences()
    if not os.path.exists(PREFERENCES_FILE):
        flash("fill out the preferences before viewing the listings")
        return redirect(url_for("preferences"))
    if not os.path.exists(DB_FILE):
        flash("No listings found, please run the scraper with --crawl option")
        return redirect(url_for("preferences"))
    if request.method == "POST":
        print(request.form)

        for column in SCORING_COLUMNS:
            button = column + "_button"
            weight = "weight_" + column
            if button in request.form.keys():
                weight_value = getattr(user_preferences, weight)
                if request.form[button] == "+":
                    if weight_value < 10:
                        setattr(user_preferences, weight, weight_value + 1)
                elif request.form[button] == "-":
                    if weight_value > 0:
                        setattr(user_preferences, weight, weight_value - 1)

        save_preferences(user_preferences)

    df = analyze_listings(DB_FILE, user_preferences)
    return render_template(
        "index.html",
        preferences=user_preferences,
        sorting_columns=SCORING_COLUMNS,
        listings_df=format_result(df),
    )


@app.route("/preferences", methods=["GET", "POST"])
def preferences():
    if request.method == "GET":
        form = UserPreferencesForm(request.form)
        user_preferences = load_preferences()
        # loop through all fields of preferences
        for key, value in user_preferences.to_dict().items():
            if value is None:
                continue
            if key == "available_from":
                continue
            if key == "points_of_interest":
                getattr(form, key).data = (
                    f"{';'.join([str(x[0])+','+str(x[1]) for x in value])}"
                )
                continue
            if "weight_" in key:
                continue
            getattr(form, key).data = value
    # if submit is pushed
    if request.method == "POST":
        form = UserPreferencesForm(request.form)
        user_preferences = load_preferences()
        for key, value in form.data.items():
            if value is None or value == "":
                continue
            if key in ("csrf_token", "submit"):
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
                user_preferences.points_of_interest = [
                    Point(value) for value in value.split(";")
                ]
                continue
            setattr(user_preferences, key, value)
        save_preferences(user_preferences)
    return render_template("preferences.html", title="Set Preferences", form=form)


def load_preferences() -> UserPreferences:
    if not os.path.exists(PREFERENCES_FILE):
        p = UserPreferences()
        # default values for empty preferences
        p.listing_type = "rent"
        p.estate_type = "apartment"
        p.location = "Praha"
        save_preferences(p)
        return p

    with open(PREFERENCES_FILE, "r", encoding="utf-8") as f:
        user_preferences = json.load(f)

    return UserPreferences.from_dict(data=user_preferences)


def save_preferences(user_preferences: UserPreferences) -> None:
    with open(PREFERENCES_FILE, "w", encoding="utf-8") as f:
        f.write(json.dumps(user_preferences.to_dict()))


def crawl_regularly(crawl=True):
    # while True:
    print("starting crawling")
    global items  # pylint: disable=global-statement
    if crawl:
        run_spiders(SCRAPER_OUTPUT_FILE)
    else:
        with open(SCRAPER_OUTPUT_FILE, "r", encoding="utf-8") as f:
            items = json.load(f)

    listings = []
    for item in items:
        listings.append(Listing(item))

    with open(LAST_CRAWL_FILE, "r", encoding="utf-8") as f:
        last_crawl_time = datetime.datetime.fromisoformat(f.read())

    update_listing_database(DB_FILE, listings, last_crawl_time)

    user_preferences = load_preferences()

    df = analyze_listings(DB_FILE, user_preferences)

    notify_user(df, last_crawl_time)


def format_result(df: pd.DataFrame):
    if df.empty:
        return df
    df = df.sort_values(by="score", ascending=False, inplace=False)
    df.price = df.price.apply(lambda x: str(int(x)) + " Kč" if x > 0 else "")
    df.area = df.area.apply(lambda x: str(int(x)) + " m2" if x > 0 else "")
    df.poi_distance = df.poi_distance.apply(
        lambda x: str(int(x)) + " m" if x >= 0 else ""
    )
    df.garden = df.garden.apply(lambda x: str(int(x)) + " m2" if x > 0 else "Ne")
    df.score = df.score.apply(lambda x: round(x, 2) if x > 0 else 0)
    for col in [
        "balcony",
        "cellar",
        "loggie",
        "elevator",
        "terrace",
        "garage",
        "parking",
    ]:
        df[col] = df[col].apply(lambda x: "Ano" if x else "Ne")
    df = df.head(30)
    return df


def notify_user(df: pd.DataFrame, last_crawl_time: datetime.datetime):
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

    embed = DiscordEmbed(title="Nové inzeráty nalezeny", description="", color="03b2f8")
    embed.set_timestamp()
    # Set `inline=False` for the embed field to occupy the whole line
    # discord message length should be limited
    df = df[df["updated"] == last_crawl_time]
    df = format_result(df)
    df = df.head(5)
    for record in df.to_dict(orient="records"):
        embed.add_embed_field(
            name=f"{record['score']} - {record['address']}",
            value=f"{record['price']}\n{record['disposition']} - {record['area']}\n{record['url']}",
            inline=False,
        )

    webhook.add_embed(embed)
    if not df.empty:
        response = webhook.execute()
        if response.status_code != 200:
            print("Error sending the message to discord")


def get_point(address) -> None | Point:
    geolocator = Nominatim(user_agent="distance_calculator")
    location = geolocator.geocode(address)
    if location:
        return Point(location.latitude, location.longitude)  # type: ignore
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
            "price",
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

    return df


# pipeline to fill the items list
class ItemCollectorPipeline():
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
            "ITEM_PIPELINES": {"__main__.ItemCollectorPipeline": 100},
        }
    )

    start = time.time()
    p = load_preferences()
    spider_settings = {}
    spider_settings["listing_type"] = p.listing_type
    spider_settings["estate_type"] = p.estate_type
    spider_settings["location"] = p.location

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
        f"{datetime.datetime.now().isoformat()}: scraped items saved to {output_file}"
    )

    end = time.time()

    if start != 0.0 and end != 0.0:
        print(f"crawling finished in {end - start}s")

    # writing the last crawl time to a file
    with open(LAST_CRAWL_FILE, "w", encoding="utf-8") as f:
        f.write(datetime.datetime.now().isoformat())


if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) > 0 and args[0] == "--crawl":
        crawl_regularly()
    else:
        app.run(debug=True, host="0.0.0.0")
