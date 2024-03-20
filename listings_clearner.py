# %% [markdown]
# # Data Loading

# %%
import sys
import unidecode
import pandas as pd  # type: ignore
import numpy as np
from geopy.distance import distance  # type: ignore
from geopy.geocoders import Nominatim  # type: ignore
from geopy.point import Point  # type: ignore
from database_wrapper import DatabaseWrapper
from sreality_scraper.sreality.spiders.sreality_spider import SrealityUrlBuilder


def get_point(address) -> None | Point:
    geolocator = Nominatim(user_agent="distance_calculator")
    location = geolocator.geocode(address)
    if location:
        return Point(location.latitude, location.longitude)  # type: ignore
    else:
        return None


def clean_listing_database(filename: str = "listings.db") -> pd.DataFrame:
    # get the data from the database
    db = DatabaseWrapper(filename)
    df = db.get_df()
    db.close_conn()
    if df is None:
        print("No data to process")
        sys.exit(1)

    # %% [markdown]
    # # Data Cleaning

    # %%
    # set id column as index
    df.set_index("id", inplace=True)

    # %%
    # drop public_transport column, it's not useful for now
    df.drop(columns=["public_transport"], inplace=True)
    # drop security_deposit column
    df.drop(columns=["security_deposit"], inplace=True)

    df.drop(columns=["pets"], inplace=True)
    df.drop(columns=["service_fees"], inplace=True)

    # %% [markdown]
    # ## Dispositions

    # %%
    # print unique disposition values
    df.disposition.unique()

    # %%
    # map integers (sreality disposition ids) to strings
    df.disposition = df.disposition.apply(
        lambda x: SrealityUrlBuilder.map_category_sub_cb(x) if isinstance(x, int) else x
    )
    df.disposition.unique()

    # %%
    # unify disposition values
    df.disposition = (
        df.disposition.replace("Garsoniéra", "1+kk")
        .replace("Ostatní", "other")
        .replace("atypicky", "other")
        .replace("pokoj", "other")
        .replace("6+kk", "6-a-více")
        .replace("6+1", "6-a-více")
        .replace("7+kk", "6-a-více")
        .replace("7+1", "6-a-více")
    )
    df.disposition.unique()

    # %% [markdown]
    # ## Area

    # %%
    df.area = df.area.apply(lambda x: int(x) if isinstance(x, str) and x.isnumeric() else x)

    # %% [markdown]
    # ## Available from

    # %%
    df.available_from.unique()

    # %%
    # trim whitespaces
    df.available_from = df.available_from.str.replace(" ", "")

    # %%
    # replace "Ihned" with last updated date
    ihned_rows = df["available_from"] == "Ihned"
    df.loc[df["available_from"] == "Ihned", "available_from"] = pd.to_datetime(
        df.loc[df["available_from"] == "Ihned", "updated"],
        format="%Y-%m-%d %H:%M:%S.%f",
        errors="coerce",
    )

    # %%
    # try parsing the date for all non empty fields
    invalid_indices = pd.to_datetime(df.available_from, errors="coerce").isnull()

    # %%
    invalid_indices = invalid_indices | ihned_rows
    df.loc[~invalid_indices, "available_from"].unique()

    # %%
    df.loc[~invalid_indices, "available_from"] = pd.to_datetime(
        df.loc[~invalid_indices, "available_from"],
        format="%d.%m.%Y",
        errors="coerce",
    )

    # %% [markdown]
    # ## Balcony

    # %%
    df.balcony.unique()

    # %%
    # if there's a mention of balk in the field, then balcony is most likely present
    df.balcony = df.balcony.apply(
        lambda x: 1 if isinstance(x, str) and "balk" in x.lower() else x
    )

    # %%
    df.balcony.unique()

    # %% [markdown]
    # ## Cellar

    # %%
    df.cellar.unique()

    # %%
    df.cellar = df.cellar.apply(
        lambda x: 1 if isinstance(x, str) and "sklep" in x.lower() else x
    )

    # %%
    df.cellar.unique()

    # %% [markdown]
    # ## Balcony

    # %%
    df.balcony.unique()

    # %% [markdown]
    # ## Elevator

    # %%
    df.elevator.unique()

    # %%
    df.elevator = df.elevator.apply(
        lambda x: 1 if isinstance(x, str) and "výtah" in x.lower() else x
    ).apply(lambda x: 0 if x == 2 else x)

    # %%
    df.elevator.unique()

    # %% [markdown]
    # ## Floor

    # %%
    df.floor.unique()

    # %%
    df.loc[:, "floor"] = df.floor.replace(". podlaží.*", "", regex=True).replace(
        " z celkem.*", "", regex=True
    )
    df.floor.unique()

    # %%
    df.floor = df.floor.apply(lambda x: 0 if x == "přízemí" else x).apply(
        lambda x: np.nan if x is None else int(x)
    )
    df.floor.unique()

    # %% [markdown]
    # ## Garden

    # %%
    df.garden.unique()

    # %%
    # TODO: remove unidecode and move it to Listings class
    df.garden = df.garden.apply(
        lambda x: (
            unidecode.unidecode(x)
            .replace("Predzahradka ", "")
            .replace(" m2", "")
            .replace(" ", "")
            .replace(",", ".")
            if isinstance(x, str)
            else x
        )
    ).astype(float)

    # %% [markdown]
    # ## Furnished

    # %%
    df.furnished.unique()

    # %%
    df.furnished = df.furnished.apply(
        lambda x: (
            x.replace("Nevybaveno", "2").replace("Částečně", "3").replace("Vybaveno", "1")
            if isinstance(x, str)
            else x
        )
    ).apply(lambda x: np.nan if x is None else int(x))

    # %%
    df.furnished.unique()

    # %% [markdown]
    # ## Garage

    # %%
    df.garage.unique()

    # %%
    df.garage = df.garage.apply(lambda x: 1 if isinstance(x, str) and "Garáž" in x else x)
    df.garage.unique()

    # %% [markdown]
    # ## Loggie

    # %%
    df.loggie.unique()

    # %%
    df.loggie = df.loggie.apply(
        lambda x: 1 if isinstance(x, str) and "Lodžie" in x else x
    ).astype(float)
    df.loggie.unique()

    # %% [markdown]
    # ## Parking

    # %%
    df.parking.unique()

    # %%
    df.parking = df.parking.apply(
        lambda x: 1 if isinstance(x, str) and "Parkování" in x else x
    ).astype(float)
    df.parking.unique()

    # %% [markdown]
    # ## Rent

    # %%
    df.rent.unique()

    # %%
    df.loc[:, "rent"] = df.rent.apply(
        lambda x: (
            int(x.replace(" ", "").replace("Kč", "").replace("€", ""))
            if isinstance(x, str)
            else x
        )
    ).astype(float)

    df.rent.sort_values().unique()

    # %% [markdown]
    # ## Status

    # %%
    # 'status'

    # unique values for status
    df.status.unique()

    # %%
    # ## Ownership

    # %%
    df.ownership.unique()

    # %%
    df.ownership = df.ownership.apply(
        lambda x: (
            str(x)
            .replace("1", "Osobní")
            .replace("2", "Družstevní")
            .replace("3", "Ostatní")
            .replace("Obecní", "Ostatní")
            if isinstance(x, int)
            else x
        )
    ).apply(lambda x: np.nan if x is None else x)

    # %%
    df.ownership.unique()

    # %% [markdown]
    # ## Terrace

    # %%
    df.terrace.unique()

    # %%
    # 'terrace',
    df.loc[:, "terrace"] = df["terrace"].apply(
        lambda x: 1 if isinstance(x, str) and "Terasa" in x else x
    )
    df.loc[:, "terrace"].unique()

    # %% [markdown]
    # ## Type

    # %%
    # 'type'
    df.type.unique()
    df.loc[:, "type"] = df["type"].apply(
        lambda x: (
            x.replace("Cihla", "cihlova")
            .replace("Panel", "panelova")
            .replace("Smíšená", "ostatni")
            .replace("Skeletová", "ostatni")
            .replace("Nízkoenergetická", "ostatni")
            .replace("Montovaná", "ostatni")
            .replace("Dřevostavba", "ostatni")
            .replace("Kamenná", "ostatni")
            .replace("Ostatní", "ostatni")
            if isinstance(x, str)
            else x
        )
    )
    df.loc[:, "type"] = df["type"].apply(
        lambda x: SrealityUrlBuilder.map_building_type(x) if isinstance(x, int) else x
    )
    df.type.unique()

    # %% [markdown]
    # ## Floor

    # %%
    df.floor = df.floor.apply(lambda x: int(x) if isinstance(x, str) else x)

    # %% [markdown]
    # ## POI Distance

    # %%
    poi = "NTK Praha"
    poi_point = get_point(poi)

    # %%
    points_of_interest = [poi_point]

    # https://stackoverflow.com/questions/37885798/how-to-calculate-the-midpoint-of-several-geolocations-in-python
    x = 0.0
    y = 0.0
    z = 0.0

    for point in points_of_interest:
        if point is None:
            continue
        latitude = np.radians(point.latitude)
        longitude = np.radians(point.longitude)

        x += np.cos(latitude) * np.cos(longitude)
        y += np.cos(latitude) * np.sin(longitude)
        z += np.sin(latitude)

    total = len(points_of_interest)

    x = x / total
    y = y / total
    z = z / total

    central_longitude = np.degrees(np.arctan2(y, x))
    central_square_root = np.sqrt(x * x + y * y)
    central_latitude = np.degrees(np.arctan2(z, central_square_root))

    print(f"{central_latitude}, {central_longitude}")

    for i, row in df.iterrows():
        df.loc[i, "poi_distance"] = distance(  # type: ignore
            (central_latitude, central_longitude), (row.gps_lat, row.gps_lon)
        ).m

    # %%
    nominal = [
        "address",
        "description",
        "disposition",
        "ownership",
        "status",
        "type",
        "url",
    ]
    ordinal = [
        "floor",
        "furnished",
        "balcony",
        "cellar",
        "elevator",
        "garage",
        "loggie",
        "parking",
        "terrace",
    ]
    interval = ["available_from", "created", "last_seen", "updated"]
    ratio = ["area", "rent", "poi_distance", "garden"]  # 'gps_lat', 'gps_lon' not included

    # %%
    for col in ordinal + ratio:
        print(
            f"{df[col].sort_values().value_counts(bins=5 if col not in ordinal else None)}\n"
        )

    # %%
    df.fillna(value=np.nan, inplace=True)

    # %%
    # mapping = {
    #     "1+1": 1,
    #     "1+kk": 2,
    #     "2+1": 3,
    #     "2+kk": 4,
    #     "3+1": 5,
    #     "3+kk": 6,
    #     "4+1": 7,
    #     "4+kk": 8,
    #     "5+kk": 9,
    #     "5+1": 10,
    #     "6-a-více": 11,
    #     "other": 12,
    # }
    # df.disposition = df.disposition.map(mapping)

    # status_mapping = {
    #     "Projekt": 1,
    #     "Ve výstavbě": 2,
    #     "Novostavba": 3,
    #     "Velmi dobrý": 4,
    #     "Dobrý": 5,
    #     "V rekonstrukci": 6,
    #     "Po rekonstrukci": 7,
    #     "Před rekonstrukcí": 8,
    # }
    # df.status = df.status.map(status_mapping)

    # type_mapping = {
    #     "cihlova": 1,
    #     "panelova": 2,
    #     "ostatni": 3,
    # }
    # df.type = df.type.map(type_mapping)

    # %% [markdown]
    # # Normalize columns

    # %%
    for col in ordinal + ratio:
        print(col)
        max_val = df[col].max()
        min_val = df[col].min()
        denominator = max_val - min_val
        if denominator == 0:
            denominator = 1e-10  # Add a small epsilon value to avoid division by zero
        df[col] = (df[col] - min_val) / denominator

        print(df[col].value_counts(bins=10, sort=False))

    # %% [markdown]
    # # Calculate score

    # %%
    # sum values of all ordinal and ratio columns
    df["sum"] = df[ordinal + ratio].sum(axis=1)
    # normalize the sum
    df["sum"] = (df["sum"] - df["sum"].min()) / (df["sum"].max() - df["sum"].min())

    # %%
    print(ordinal + ratio)
    # sort df by sum
    pd.set_option("display.max_columns", None)
    df.sort_values(by="poi_distance", ascending=False)
    return df
