from datetime import date
from disposition import Disposition
from property_status import PropertyStatus
from property_type import PropertyType
from furnished import Furnished
from geopy import Point
import pandas as pd
from disposition import Disposition


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

        if self.available_from:
            df = df[df["available_from"] >= self.available_from]

        if self.location:
            df = df[df["address"].str.contains(self.location, case=False, na=False)]


        return df
