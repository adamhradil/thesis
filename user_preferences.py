from datetime import date
import numpy as np  # type: ignore
import pandas as pd  # type: ignore
from geopy import Point  # type: ignore
from geopy.distance import distance  # type: ignore
from disposition import Disposition
from property_status import PropertyStatus
from property_type import PropertyType
from furnished import Furnished


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

        self.weight_area: None | float = None
        self.weight_rent: None | float = None
        self.weight_disposition: None | float = None
        self.weight_garden: None | float = None
        self.weight_balcony: None | float = None
        self.weight_cellar: None | float = None
        self.weight_loggie: None | float = None
        self.weight_elevator: None | float = None
        self.weight_terrace: None | float = None
        self.weight_garage: None | float = None
        self.weight_parking: None | float = None
        self.weight_poi_distance: None | float = None

        self.min_score: None | int = 1

    def validate_weights(self):
        # each attribute containing weight_ in the name must be larger than 0
        
        for weight in scoring_weights.values():
            if weight is not None and weight <= 0:
                raise ValueError("Each weight must be larger than 0")

    # initialize class from json
    def from_dict(cls, data):
        user_preferences = cls()
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
                user_preferences.points_of_interest = [Point(latitude=point[0], longitude=point[1]) for point in value]
            else:
                setattr(user_preferences, key, value)
        return user_preferences

    # make class serializable to json
    def to_dict(self):
        return {
            "location": self.location,
            "estate_type": self.estate_type,
            "listing_type": self.listing_type,
            "points_of_interest": [(point.latitude, point.longitude) for point in self.points_of_interest] if self.points_of_interest else None,
            "disposition": [d.value for d in self.disposition] if self.disposition else None,
            "min_area": self.min_area,
            "max_area": self.max_area,
            "min_price": self.min_price,
            "max_price": self.max_price,
            "available_from": self.available_from.isoformat() if self.available_from else None,
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
            "weight_rent": self.weight_rent,
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
            "min_score": self.min_score,
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
            df = df[df["rent"] >= self.min_price]
        if self.max_price:
            df = df[df["rent"] <= self.max_price]
        if self.floor:
            df = df[df["floor"] >= self.floor]
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
                df.loc[i, "poi_distance"] = int(distance(  # type: ignore
                    (central_latitude, central_longitude), (row.gps_lat, row.gps_lon)
                ).m)
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

        scoring_columns = [
            "area",
            "rent",
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

        scoring_weights = {
            "normalized_area": self.weight_area,
            "normalized_rent": self.weight_rent,
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
        # if sum(weights for weights in scoring_weights.values() if weights is not None) != len(scoring_weights):
        #     raise ValueError("Sum of weights must be equal to it's length")


        # Normalize columns
        for col in scoring_columns:
            max_val = df[col].max()
            min_val = df[col].min()
            denominator = max_val - min_val
            if denominator == 0:
                denominator = (
                    1e-10  # Add a small epsilon value to avoid division by zero
                )
            if col == "poi_distance" or col == "rent":
                df["normalized_" + col] = (max_val - df[col]) / denominator
            else:
                df["normalized_" + col] = (df[col] - min_val) / denominator

        scoring_columns = ["normalized_" + col for col in scoring_columns]
        # Calculate score
        df["sum"] = (df[scoring_columns] * pd.Series(scoring_weights)).sum(axis=1)
        # normalize sum
        # df["sum"] = (df["sum"] - df["sum"].min()) / (df["sum"].max() - df["sum"].min())
        df.disposition = df.disposition.map({v: k for k, v in disposition_mapping.items()})

        if self.min_score:
            df = df[df["sum"] >= self.min_score/100]

        return df
