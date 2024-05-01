from flask_wtf import FlaskForm  # pylint: disable=import-error
from wtforms import (
    SelectField,
    StringField,
    IntegerField,
    BooleanField,
    SubmitField,
    SelectMultipleField,
)
from wtforms.validators import DataRequired, Optional
from disposition import Disposition
from property_type import PropertyType
from furnished import Furnished
from property_status import PropertyStatus


class UserPreferencesForm(FlaskForm):
    location = SelectField(
        "Location", validators=[DataRequired()], choices=["Praha", "Brno", "Ostrava"]
    )
    estate_type = SelectField(
        "Estate Type", validators=[DataRequired()], choices=["apartment", "house"]
    )
    listing_type = SelectField(
        "Listing Type", validators=[DataRequired()], choices=["sale", "price"]
    )
    points_of_interest = StringField("Points of Interest")
    disposition = SelectMultipleField(
        "Disposition",
        choices=[(disposition.value) for disposition in Disposition],
        validators=[Optional()],
    )
    min_area = IntegerField("Minimum Area")
    max_area = IntegerField("Maximum Area")
    min_price = IntegerField("Minimum Price")
    max_price = IntegerField("Maximum Price")
    balcony = BooleanField("Balcony")
    cellar = BooleanField("Cellar")
    elevator = BooleanField("Elevator")
    garage = BooleanField("Garage")
    garden = BooleanField("Garden")
    loggie = BooleanField("Loggie")
    parking = BooleanField("Parking")
    terrace = BooleanField("Terrace")
    type = SelectMultipleField(
        "Property Type",
        choices=[(type.value) for type in PropertyType],
        validators=[Optional()],
    )
    furnished = SelectMultipleField(
        "Furnished",
        choices=[(furnished.value) for furnished in Furnished],
        validators=[Optional()],
    )
    status = SelectMultipleField(
        "Property Status",
        choices=[(status.value) for status in PropertyStatus],
        validators=[Optional()],
    )
    floor = IntegerField("Floor")
    description = StringField("Description")
    submit = SubmitField("Submit")
