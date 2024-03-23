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
from flask import Flask, render_template, flash, redirect, request, url_for, session
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
SCRAPER_OUTPUT_FILE = "all_items.json"
POI = "NTK Praha"
DB_FILE = "listings.db"
items = []
load_dotenv()
webhook_url = os.getenv("WEBHOOK_URL")
if webhook_url == "" or webhook_url is None:
    print("Webhook URL not found in .env file")
    sys.exit(1)

app = Flask(__name__)
SECRET_KEY = os.urandom(32)
app.config["SECRET_KEY"] = SECRET_KEY


@app.route("/")
def index():

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

    # if session['preferences'] is none, then redirect to preferences page
    if session.get("preferences") is None:
        return redirect(url_for("preferences"))

    preferences = UserPreferences.from_dict(
        UserPreferences, data=session["preferences"]
    )
    print(preferences.to_dict())

    df = get_listings(preferences, scoring_weights)
    return render_template(
        "index.html", utc_dt=datetime.datetime.utcnow(), listings_df=format_result(df)
    )


@app.route("/preferences", methods=["GET", "POST"])
def preferences():
    poi = get_point(POI)
    form = UserPreferencesForm(
        request.form, location="Praha", points_of_interest=f"{poi[0]},{poi[1]}"
    )
    if form.validate_on_submit():
        flash("Preferences set successfully")
        preferences = UserPreferences()
        for key, value in form.data.items():
            if value is None or value == "" or value is False:
                continue
            if key == "csrf_token" or key == "submit":
                continue
            if key == "disposition":
                preferences.disposition = [Disposition(x) for x in value]
                continue
            if key == "type":
                preferences.type = [PropertyType(x) for x in value]
                continue
            if key == "furnished":
                preferences.furnished = [Furnished(x) for x in value]
                continue
            if key == "status":
                preferences.status = [PropertyStatus(x) for x in value]
                continue
            if key == "points_of_interest":
                preferences.points_of_interest = [Point(value)]
            setattr(preferences, key, value)
        session["preferences"] = preferences.to_dict()
        # fill the form with default values
        return redirect(url_for("index"))
    return render_template("preferences.html", title="Set Preferences", form=form)


def get_listings(preferences, scoring_weights):
    crawl_time = datetime.datetime.now()

    if CRAWL:
        run_spiders(SCRAPER_OUTPUT_FILE)
    else:
        with open(SCRAPER_OUTPUT_FILE, "r", encoding="utf-8") as f:
            items = json.load(f)

    listings = []
    for i in items:
        listings.append(Listing(i))

    # update_listing_database(DB_FILE, listings, crawl_time)
    df = analyze_listings(DB_FILE, preferences, scoring_weights)
    return df


def format_result(df: pd.DataFrame):
    df = df.sort_values(by="sum", ascending=False, inplace=False)
    df["rent"] = df["rent"].apply(lambda x: str(int(x)) + " Kč" if x > 0 else "")
    df["area"] = df["area"].apply(lambda x: str(int(x)) + " m2" if x > 0 else "")
    df["sum"] = df["sum"].apply(
        lambda x: str(int(round(x, 2) * 100)) + "/100" if x > 0 else ""
    )
    listings_to_send = df.head(5)
    print(
        tabulate(
            listings_to_send[["sum", "address", "rent", "disposition", "area", "url"]],
            tablefmt="grid",
            headers=["id", "sum", "address", "rent", "disposition", "area", "url"],
        )
    )
    return df


def notify_user(df: pd.DataFrame):
    df = format_result(df)
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


def analyze_listings(
    db_file: str, user_preferences: UserPreferences, user_weights: dict
):
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
    # send_listings(df)
    return df


def run_spiders(json_output: str):
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
    app.run(debug=True)
