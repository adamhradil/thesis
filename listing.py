import scrapy  # pylint: disable=import-error


class Listing:
    """
    Represents a listing object.

    Attributes:
        id: The ID of the listing.
        address: The address of the listing.
        area: The area of the listing in square meters.
        available_from: The date when the listing is available from.
        description: The description of the listing.
        disposition: The disposition of the listing (e.g., number of rooms).
        floor: The floor number of the property.
        furnished: Indicates if the listing is furnished or not.
        price: The price of the listing.
        security_deposit: The security deposit required for the listing.
        service_fees: The service fees for the listing.
        status: The status of the listing.
        type: The type of the listing.
        url: The URL of the listing.
        balcony: Indicates if the listing has a balcony or not.
        cellar: Indicates if the listing has a cellar or not.
        garden: Indicates if the listing has a garden or not.
        terrace: Indicates if the listing has a terrace or not.
        elevator: Indicates if the listing has an elevator or not.
        parking: Indicates if the listing has parking or not.
        garage: Indicates if the listing has a garage or not.
        loggie: Indicates if the listing has a loggie or not.
        ownership: The ownership type of the listing.
        gps_lat: The latitude coordinate of the listing's location.
        gps_lon: The longitude coordinate of the listing's location.
        created: The date when the listing was created.
        updated: The date when the listing was last updated.
        last_seen: The date when the listing was last seen.
    """

    def __init__(self, data=None):
        """
        Initialize a Listing object.

        Args:
            data (dict): A dictionary containing the data for the listing.
        """
        self.id = self._value_factory("id", data)
        self.address = self._value_factory("address", data)
        self.area = self._value_factory("area", data)
        self.available_from = self._value_factory("available_from", data)
        self.description = self._value_factory("description", data)
        self.disposition = self._value_factory("disposition", data)
        self.floor = self._value_factory("floor", data)
        self.furnished = self._value_factory("furnished", data)
        self.price = self._value_factory("price", data)
        self.security_deposit = self._value_factory("security_deposit", data)
        self.service_fees = self._value_factory("service_fees", data)
        self.status = self._value_factory("status", data)
        self.type = self._value_factory("type", data)
        self.url = self._value_factory("url", data)
        self.balcony = self._value_factory("balcony", data)
        self.cellar = self._value_factory("cellar", data)
        self.garden = self._value_factory("garden", data)
        self.terrace = self._value_factory("terrace", data)
        self.elevator = self._value_factory("elevator", data)
        self.parking = self._value_factory("parking", data)
        self.garage = self._value_factory("garage", data)
        self.loggie = self._value_factory("loggie", data)
        self.ownership = self._value_factory("ownership", data)
        self.gps_lat = self._value_factory("gps_lat", data)
        self.gps_lon = self._value_factory("gps_lon", data)
        self.created = self._value_factory("created", data)
        self.updated = self._value_factory("updated", data)
        self.last_seen = self._value_factory("last_seen", data)

    def __eq__(self, other):
        """
        Check if the current Listing object is equal to another object.

        Args:
            other: The object to compare with.

        Returns:
            True if the objects are equal, False otherwise.
        """
        if isinstance(other, Listing):
            excluded_attributes = ["last_seen", "updated", "created"]
            return all(
                getattr(self, attr) == getattr(other, attr)
                for attr in [
                    attr
                    for attr in dir(self)
                    if not callable(getattr(self, attr)) and not attr.startswith("__")
                ]
                if attr not in excluded_attributes
            )
        return False

    def __str__(self):
        """
        Returns a string representation of the object.

        Returns:
            str: A string representation of the object.
        """
        return str(self.__dict__)

    def _value_factory(self, attribute: str, data: dict | scrapy.Item | tuple | None):
        """
        Returns the value of the specified attribute from the given data.

        Args:
            attribute: The name of the attribute to retrieve.
            data (dict | scrapy.Item | tuple | None): The data from which to retrieve the attribute value.

        Returns:
            The value of the specified attribute from the given data,
            or None if the data is None or the attribute is not found.
        """
        if data is None:
            return None
        if isinstance(data, (scrapy.Item, dict)):
            return data.get(attribute, "")
        return None
