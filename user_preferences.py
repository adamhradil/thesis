from datetime import date
import pandas as pd  # type: ignore
from geopy import Point  # type: ignore
from disposition import Disposition
from property_status import PropertyStatus
from property_type import PropertyType
from furnished import Furnished
from geopy.distance import distance  # type: ignore
from geopy.geocoders import Nominatim  # type: ignore
from geopy.point import Point  # type: ignore
import numpy as np  # type: ignore


class UserPreferences:
    def __init__(self) -> None:
        self.location: None | str = None  # later region, city, district, street
        self.points_of_interest: None | list[Point] = None

        self.disposition: None | list[Disposition] = None

        self.min_area: None | int = None
        self.max_area: None | int = None

        self.min_price: None | int = None
        self.max_price: None | int = None

        self.available_from: None | date = None

        self.balcony: None | bool = None
        self.cellar: None | bool = None
        self.elevator: None | bool = None
        self.garage: None | bool = None
        self.garden: None | bool = None
        self.loggie: None | bool = None
        self.parking: None | bool = None
        self.terrace: None | bool = None

        self.type: None | list[PropertyType] = None
        self.furnished: None | list[Furnished] = None
        self.status: None | list[PropertyStatus] = None

        self.floor: None | int = None  # 2. and higher?

        self.description: None | str = None  # description contains a word?

    def filter_listings(self, df: pd.DataFrame) -> pd.DataFrame:
        if self.disposition:
            df = df[df["disposition"].isin([d.value for d in self.disposition])]
        if self.type:
            df = df[df["type"].isin([d.value for d in self.type])]
        if self.furnished:
            df = df[df["furnished"].isin([d.value for d in self.furnished])]
        if self.status:
            df = df[df["status"].isin([d.value for d in self.status])]

        if self.min_area:
            df = df[df["area"] >= self.min_area]
        if self.max_area:
            df = df[df["area"] <= self.max_area]
        if self.min_price:
            df = df[df["rent"] >= self.min_price]
        if self.max_price:
            df = df[df["rent"] <= self.max_price]
        if self.available_from:
            df = df[df["available_from"] >= self.available_from]

        if self.balcony is not None:
            if self.balcony is True:
                df = df[df["balcony"] == 1]
            else:
                df = df[df["balcony"] != 1]
        if self.cellar is not None:
            if self.cellar is True:
                df = df[df["cellar"] == 1]
            else:
                df = df[df["cellar"] != 1]
        if self.loggie is not None:
            if self.loggie is True:
                df = df[df["loggie"] == 1]
            else:
                df = df[df["loggie"] != 1]
        if self.elevator is not None:
            if self.elevator is True:
                df = df[df["elevator"] == 1]
            else:
                df = df[df["elevator"] != 1]
        if self.terrace is not None:
            if self.terrace is True:
                df = df[df["terrace"] == 1]
            else:
                df = df[df["terrace"] != 1]
        if self.garage is not None:
            if self.garage is True:
                df = df[df["garage"] == 1]
            else:
                df = df[df["garage"] != 1]
        if self.parking is not None:
            if self.parking is True:
                df = df[df["parking"] == 1]
            else:
                df = df[df["parking"] != 1]

        if self.garden is not None:
            if self.garden is True:
                df = df[df["garden"].isnull() == False]
            else:
                df = df[df["garden"].isnull() == True]

        if self.description:
            df = df[df["description"].str.contains(self.description, case=False, na=False)]

        if self.location:
            df = df[df["address"].str.contains(self.location, case=False, na=False)]

        return df

    def get_point(self, address) -> None | Point:
        geolocator = Nominatim(user_agent="distance_calculator")
        location = geolocator.geocode(address)
        if location:
            return Point(location.latitude, location.longitude)  # type: ignore
        else:
            return None

    def calculate_score(self, df: pd.DataFrame) -> pd.DataFrame:
        # %% [markdown]
        # ## POI Distance

        # %%
        poi = "NTK Praha"
        poi_point = self.get_point(poi)

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
            "floor",
            "furnished",
            'gps_lat',
            'gps_lon'
        ]
        ordinal = [
            "balcony",
            "cellar",
            "elevator",
            "garage",
            "loggie",
            "parking",
            "terrace",
        ]
        interval = ["available_from", "created", "last_seen", "updated"]
        ratio = ["area", "rent", "poi_distance", "garden"]

        # %%
        for col in ordinal + ratio:
            print(
                f"{df[col].sort_values().value_counts(bins=5 if col not in ordinal else None)}\n"
            )

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
        # for col in ordinal + ratio:
        #     print(col)
        #     max_val = df[col].max()
        #     min_val = df[col].min()
        #     denominator = max_val - min_val
        #     if denominator == 0:
        #         denominator = 1e-10  # Add a small epsilon value to avoid division by zero
        #     df[col] = (df[col] - min_val) / denominator

        #     print(df[col].value_counts(bins=10, sort=False))

        # # %% [markdown]
        # # # Calculate score

        # # %%
        # # sum values of all ordinal and ratio columns
        # df["sum"] = df[ordinal + ratio].sum(axis=1)
        # # normalize the sum
        # df["sum"] = (df["sum"] - df["sum"].min()) / (df["sum"].max() - df["sum"].min())

        # # %%
        # print(ordinal + ratio)
        # sort df by sum
        pd.set_option("display.max_columns", None)
        df.sort_values(by="poi_distance", ascending=False)
        print(df.columns)

        return df
