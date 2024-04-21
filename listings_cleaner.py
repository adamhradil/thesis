# %% [markdown]
# # Data Loading

# %%
import sys
import unidecode
import pandas as pd  # type: ignore
import numpy as np
from database_wrapper import DatabaseWrapper
from sreality_scraper.sreality.spiders.sreality_spider import SrealityUrlBuilder


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
    # df.drop(columns=["public_transport"], inplace=True)
    # drop security_deposit column
    df.drop(columns=["security_deposit"], inplace=True)

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
    df.area = df.area.apply(lambda x: int(unidecode.unidecode(x).replace(" ", "")) if isinstance(x, str) else x)

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
    ).dt.date

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
    ).dt.date

    # %% [markdown]
    # ## Balcony

    # %%
    df.balcony.unique()

    # %%
    # if there's a mention of balk in the field, then balcony is most likely present
    df.balcony = df.balcony.apply(
        lambda x: 1 if isinstance(x, str) and "balk" in x.lower() else x
    )
    df.balcony = df.balcony.fillna(0)

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
    df.cellar = df.cellar.fillna(0)

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
    df.elevator = df.elevator.fillna(0)

    # %%
    df.elevator.unique()

    # %% [markdown]
    # ## Floor

    # %%
    df.floor.unique()

    # %%
    df.loc[:, "floor"] = df.floor.replace(". podlaží.*", "", regex=True).replace(
        " z celkem.*", "", regex=True
    ).replace(" včetně.*", "", regex=True).replace(" underground.*", "", regex=True)
    df.floor.unique()

    # %%
    df.floor = df.floor.apply(lambda x: 0 if x == "přízemí" else x)
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
    df.garden = df.garden.fillna(0)

    # %% [markdown]
    # ## Furnished

    # %%
    df.furnished.unique()

    # %%
    df.furnished = df.furnished.apply(
        lambda x: (
            str(x).replace("2", "Nevybaveno").replace("3", "Částečně").replace("1", "Vybaveno")
            if isinstance(x, int)
            else x
        )
    ).replace("0", np.nan)

    # %%
    df.furnished.unique()

    # %% [markdown]
    # ## Garage

    # %%
    df.garage.unique()

    # %%
    df.garage = df.garage.apply(lambda x: 1 if isinstance(x, str) and "Garáž" in x else x)
    df.garage = df.garage.fillna(0)
    df.garage.unique()

    # %% [markdown]
    # ## Loggie

    # %%
    df.loggie.unique()

    # %%
    df.loggie = df.loggie.apply(
        lambda x: 1 if isinstance(x, str) and "Lodžie" in x else x
    ).astype(float)
    df.loggie = df.loggie.fillna(0)
    df.loggie.unique()

    # %% [markdown]
    # ## Parking

    # %%
    df.parking.unique()

    # %%
    df.parking = df.parking.apply(
        lambda x: 1 if isinstance(x, str) and "Parkování" in x else x
    ).astype(float)
    df.parking = df.parking.fillna(0)
    df.parking.unique()

    # %% [markdown]
    # ## price

    # %%
    df.price.unique()

    # %%
    df.loc[:, "price"] = df.price.apply(
        lambda x: (
            int(x.replace(" ", "").replace("Kč", "").replace("€", ""))
            if isinstance(x, str)
            else x
        )
    ).astype(float)

    df.price.sort_values().unique()

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
            if isinstance(x, int)
            else x
        )
    ).apply(lambda x: x.replace("Obecní", "Ostatní") if isinstance(x, str) else x)

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
    df.terrace = df.terrace.fillna(0)
    df.loc[:, "terrace"].unique()

    # %% [markdown]
    # ## Type

    # %%
    # 'type'
    df.type.unique()
    df.loc[:, "type"] = df["type"].apply(
        lambda x: SrealityUrlBuilder.map_building_type(x) if isinstance(x, int) else x
    )
    df.loc[:, "type"] = df["type"].apply(
        lambda x: (
            x.replace("cihlova", "Cihla")
            .replace("panelova", "Panel")
            .replace("ostatni", "Ostatní")
            .replace("Smíšená", "Ostatní")
            .replace("Skeletová", "Ostatní")
            .replace("Nízkoenergetická", "Ostatní")
            .replace("Montovaná", "Ostatní")
            .replace("Dřevostavba", "Ostatní")
            .replace("Kamenná", "Ostatní")
            if isinstance(x, str)
            else x
        )
    )
    df.type.unique()

    # %% [markdown]
    # ## Floor

    # %%
    df.floor = df.floor.apply(lambda x: int(x) if isinstance(x, str) else x)

    df = df.infer_objects(copy=False).fillna(np.nan)
    return df
