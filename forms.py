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
