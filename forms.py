from flask_wtf import FlaskForm  # pylint: disable=import-error
from wtforms import (  # pylint: disable=import-error
    SelectField,
    StringField,
    IntegerField,
    BooleanField,
    SubmitField,
    SelectMultipleField,
)
from wtforms.validators import DataRequired, Optional  # pylint: disable=import-error
from disposition import Disposition
from property_type import PropertyType
from furnished import Furnished
from property_status import PropertyStatus


class UserPreferencesForm(FlaskForm):
    """
    Form for user preferences.

    This form allows users to specify their preferences for property search.

    Attributes:
        location (SelectField): The location of the property.
        estate_type (SelectField): The type of the property (e.g., apartment, house).
        listing_type (SelectField): The type of the listing (e.g., sale, rental).
        points_of_interest (StringField): Points of interest near the property.
        disposition (SelectMultipleField): The layout of the property.
        min_area (IntegerField): The minimum area of the property.
        max_area (IntegerField): The maximum area of the property.
        min_price (IntegerField): The minimum price of the property.
        max_price (IntegerField): The maximum price of the property.
        balcony (BooleanField): Indicates if the property has a balcony.
        cellar (BooleanField): Indicates if the property has a cellar.
        elevator (BooleanField): Indicates if the property has an elevator.
        garage (BooleanField): Indicates if the property has a garage.
        garden (BooleanField): Indicates if the property has a garden.
        loggie (BooleanField): Indicates if the property has a loggia.
        parking (BooleanField): Indicates if parking is available.
        terrace (BooleanField): Indicates if the property has a terrace.
        type (SelectMultipleField): The material of the property.
        furnished (SelectMultipleField): The level of furnishing of the property.
        status (SelectMultipleField): The status of the property.
        floor (IntegerField): The floor of the property.
        description (StringField): Description of the property.
        submit (SubmitField): Submit button for the form.
    """

    location = SelectField(
        "Město", validators=[DataRequired()], choices=["Praha", "Brno", "Ostrava"]
    )
    estate_type = SelectField(
        "Typ nemovitosti", validators=[DataRequired()], choices=["byt", "dům"]
    )
    listing_type = SelectField(
        "Typ inzerátu", validators=[DataRequired()], choices=["prodej", "pronájem"]
    )
    points_of_interest = StringField("Body zájmu")
    disposition = SelectMultipleField(
        "Dispozice",
        choices=[(disposition.value) for disposition in Disposition],
        validators=[Optional()],
    )
    min_area = IntegerField("Minimální rozloha")
    max_area = IntegerField("Maximální rozloha")
    min_price = IntegerField("Minimální cena")
    max_price = IntegerField("Maximální cena")
    balcony = BooleanField("Balkon")
    cellar = BooleanField("Sklep")
    elevator = BooleanField("Výtah")
    garage = BooleanField("Garáž")
    garden = BooleanField("Zahrada")
    loggie = BooleanField("Lodžie")
    parking = BooleanField("Parkování")
    terrace = BooleanField("Terasa")
    type = SelectMultipleField(
        "Materiál",
        choices=[(type.value) for type in PropertyType],
        validators=[Optional()],
    )
    furnished = SelectMultipleField(
        "Vybavenost",
        choices=[(furnished.value) for furnished in Furnished],
        validators=[Optional()],
    )
    status = SelectMultipleField(
        "Stav",
        choices=[(status.value) for status in PropertyStatus],
        validators=[Optional()],
    )
    floor = IntegerField("Patro")
    description = StringField("Popis")
    submit = SubmitField("Uložit")
