from datetime import date
import numpy as np  # type: ignore
import pandas as pd  # type: ignore pylint: disable=import-error
from geopy import Point  # type: ignore pylint: disable=import-error
from geopy.distance import distance  # type: ignore pylint: disable=import-error
from disposition import Disposition
from property_status import PropertyStatus
from property_type import PropertyType
from furnished import Furnished


SCORING_COLUMNS = [
    "area",
    "price",
    "disposition",
    "garden",
    "balcony",
    "cellar",
    "loggie",
    "elevator",
    "terrace",
    "garage",
    "parking",
    "poi_distance",
]


class UserPreferences:
    def __init__(self) -> None:
        self.estate_type: None | str = None
        self.listing_type: None | str = None
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

        self.weight_area: None | float = 1
        self.weight_price: None | float = 1
        self.weight_disposition: None | float = 1
        self.weight_garden: None | float = 1
        self.weight_balcony: None | float = 1
        self.weight_cellar: None | float = 1
        self.weight_loggie: None | float = 1
        self.weight_elevator: None | float = 1
        self.weight_terrace: None | float = 1
        self.weight_garage: None | float = 1
        self.weight_parking: None | float = 1
        self.weight_poi_distance: None | float = 1

    # initialize class from json
    @classmethod
    def from_dict(cls, data):
        user_preferences = UserPreferences()
        for key, value in data.items():
            if value is None:
                continue
            if key == "disposition":
                user_preferences.disposition = [Disposition(d) for d in value]
            elif key == "type":
                user_preferences.type = [PropertyType(t) for t in value]
            elif key == "furnished":
                user_preferences.furnished = [Furnished(f) for f in value]
            elif key == "status":
                user_preferences.status = [PropertyStatus(s) for s in value]
            elif key == "available_from":
                user_preferences.available_from = date.fromisoformat(value)
            elif key == "points_of_interest":
                user_preferences.points_of_interest = [
                    Point(latitude=point[0], longitude=point[1]) for point in value
                ]
            else:
                setattr(user_preferences, key, value)
        return user_preferences

    # make class serializable to json
    def to_dict(self):
        return {
            "location": self.location,
            "estate_type": self.estate_type,
            "listing_type": self.listing_type,
            "points_of_interest": (
                [(point.latitude, point.longitude) for point in self.points_of_interest]
                if self.points_of_interest
                else None
            ),
            "disposition": (
                [d.value for d in self.disposition] if self.disposition else None
            ),
            "min_area": self.min_area,
            "max_area": self.max_area,
            "min_price": self.min_price,
            "max_price": self.max_price,
            "available_from": (
                self.available_from.isoformat() if self.available_from else None
            ),
            "balcony": self.balcony,
            "cellar": self.cellar,
            "elevator": self.elevator,
            "garage": self.garage,
            "garden": self.garden,
            "loggie": self.loggie,
            "parking": self.parking,
            "terrace": self.terrace,
            "type": [t.value for t in self.type] if self.type else None,
            "furnished": [f.value for f in self.furnished] if self.furnished else None,
            "status": [s.value for s in self.status] if self.status else None,
            "floor": self.floor,
            "description": self.description,
            "weight_area": self.weight_area,
            "weight_price": self.weight_price,
            "weight_disposition": self.weight_disposition,
            "weight_garden": self.weight_garden,
            "weight_balcony": self.weight_balcony,
            "weight_cellar": self.weight_cellar,
            "weight_loggie": self.weight_loggie,
            "weight_elevator": self.weight_elevator,
            "weight_terrace": self.weight_terrace,
            "weight_garage": self.weight_garage,
            "weight_parking": self.weight_parking,
            "weight_poi_distance": self.weight_poi_distance,
        }

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
            df = df[df["price"] >= self.min_price]
        if self.max_price:
            df = df[df["price"] <= self.max_price]
        if self.floor:
            df = df[df["floor"] >= self.floor]
        if self.available_from:
            df = df[df["available_from"] >= self.available_from]
       
       
        for attr in "balcony","cellar","loggie","elevator","terrace","garage","parking":
            col = getattr(self, attr)
            if col is not None and col is True:
                df = df[df[attr] == 1]

        if self.garden is not None:
            if self.garden is True:
                df = df[df["garden"] > 0]
            else:
                df = df[df["garden"] <= 0]

        if self.description:
            df = df[
                df["description"].str.contains(self.description, case=False, na=False)
            ]

        if self.location:
            df = df[df["address"].str.contains(self.location, case=False, na=False)]

        return df

    def calculate_score(self, df: pd.DataFrame) -> pd.DataFrame:
        if self.points_of_interest is not None and len(self.points_of_interest) > 0:
            # https://stackoverflow.com/questions/37885798/how-to-calculate-the-midpoint-of-several-geolocations-in-python
            x = 0.0
            y = 0.0
            z = 0.0

            for point in self.points_of_interest:
                if point is None:
                    continue
                latitude = np.radians(point.latitude)
                longitude = np.radians(point.longitude)

                x += np.cos(latitude) * np.cos(longitude)
                y += np.cos(latitude) * np.sin(longitude)
                z += np.sin(latitude)

            total = len(self.points_of_interest)

            x = x / total
            y = y / total
            z = z / total

            central_longitude = np.degrees(np.arctan2(y, x))
            central_square_root = np.sqrt(x * x + y * y)
            central_latitude = np.degrees(np.arctan2(z, central_square_root))

            # print(f"{central_latitude}, {central_longitude}")

            for i, row in df.iterrows():
                df.loc[i, "poi_distance"] = int(
                    distance(  # type: ignore
                        (central_latitude, central_longitude),
                        (row.gps_lat, row.gps_lon),
                    ).m
                )
            df.poi_distance = df.poi_distance.astype(int)
        else:
            df["poi_distance"] = 0

        disposition_mapping = {
            "1+1": 1,
            "1+kk": 2,
            "2+1": 3,
            "2+kk": 4,
            "3+1": 5,
            "3+kk": 6,
            "4+1": 7,
            "4+kk": 8,
            "5+kk": 9,
            "5+1": 10,
            "6-a-více": 11,
            "other": np.nan,
        }
        df.disposition = df.disposition.map(disposition_mapping)

        scoring_weights = {
            "normalized_area": self.weight_area,
            "normalized_price": self.weight_price,
            "normalized_disposition": self.weight_disposition,
            "normalized_garden": self.weight_garden,
            "normalized_balcony": self.weight_balcony,
            "normalized_cellar": self.weight_cellar,
            "normalized_loggie": self.weight_loggie,
            "normalized_elevator": self.weight_elevator,
            "normalized_terrace": self.weight_terrace,
            "normalized_garage": self.weight_garage,
            "normalized_parking": self.weight_parking,
            "normalized_poi_distance": self.weight_poi_distance,
        }

        # Normalize columns
        for col in SCORING_COLUMNS:
            max_val = df[col].max()
            min_val = df[col].min()
            denominator = max_val - min_val
            if denominator == 0:
                denominator = (
                    1e-10  # Add a small epsilon value to avoid division by zero
                )
            if col in ("poi_distance", "price"):
                df["normalized_" + col] = (max_val - df[col]) / denominator
            else:
                df["normalized_" + col] = (df[col] - min_val) / denominator

        scoring_columns = ["normalized_" + col for col in SCORING_COLUMNS]
        # Calculate score
        df["score"] = (df[scoring_columns] * pd.Series(scoring_weights)).sum(axis=1)
        # normalize score
        # df["score"] = (df["score"] - df["score"].min()) / (df["score"].max() - df["score"].min())
        df.disposition = df.disposition.map(
            {v: k for k, v in disposition_mapping.items()}
        )

        return df
