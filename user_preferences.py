from listing import Disposition, OwnershipType, PropertyMaterial, PropertyState, Furnished


class UserPreferences:
    def __init__(
        self,
        dispositions=None,
        weight_area=None,
        weight_rent=None,
        weight_location=None,
        min_area=None,
        max_area=None,
        min_price=None,
        max_price=None,
        ownership_type=None,
        state=None,
        property_material=None,
        furnished=None,
        balcony=None,
        terrace=None,
        loggia=None,
        cellar=None,
        garden=None,
    ) -> None:
        self.dispositions: list[Disposition] | None = dispositions
        self.weight_area: float | None = weight_area
        self.weight_rent: float | None = weight_rent
        self.weight_location: float | None = weight_location
        self.min_area: int | None = min_area
        self.max_area: int | None = max_area
        self.min_price: int | None = min_price
        self.max_price: int | None = max_price
        self.ownership_type: list[OwnershipType] | None = ownership_type
        self.state: list[PropertyState] | None = state
        self.property_material: list[PropertyMaterial] | None = property_material
        self.furnished: Furnished | None = furnished
        self.balcony: bool | None = balcony
        self.terrace: bool | None = terrace
        self.loggia: bool | None = loggia
        self.cellar: bool | None = cellar
        self.garden: bool | None = garden

