from datetime import datetime
from disposition import Disposition
from property_type import PropertyType
from furnished import Furnished
from geopy import Point


class UserPreferences:
    def __init__(self) -> None:
        self.location: None | str = None  # later region, city, district, street
        self.points_of_interest: None | list[Point] = None

        self.disposition: None | list[Disposition] = None

        self.min_area: None | int = None
        self.max_area: None | int = None

        self.min_price: None | int = None
        self.max_price: None | int = None

        self.available_from: None | datetime = None

        self.balcony: None | bool = None
        self.cellar: None | bool = None
        self.elevator: None | bool = None
        self.garage: None | bool = None
        self.garden: None | bool = None
        self.loggie: None | bool = None
        self.parking: None | bool = None
        self.terrace: None | bool = None

        self.type: None | PropertyType = None
        self.furnished: None | Furnished = None
        self.status: None | str = None

        self.floor: None | int = None  # 2. and higher?

        self.description: None | str = None  # description contains a word?

