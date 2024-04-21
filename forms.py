from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, IntegerField, BooleanField, SubmitField, SelectMultipleField, DateField
from wtforms.validators import DataRequired, Optional
from disposition import Disposition
from property_type import PropertyType
from furnished import Furnished
from property_status import PropertyStatus


class UserPreferencesForm(FlaskForm):
    location = SelectField('Location', validators=[DataRequired()], choices=["Praha", "Brno", "Ostrava"])
    estate_type = SelectField('Estate Type', validators=[DataRequired()], choices=["apartment", "house"])
    listing_type = SelectField('Listing Type', validators=[DataRequired()], choices=["sale", "price"])
    points_of_interest = StringField('Points of Interest', validators=[Optional()])
    disposition = SelectMultipleField('Disposition', choices=[(disposition.value) for disposition in Disposition], validators=[Optional()])
    min_area = IntegerField('Minimum Area', validators=[Optional()])
    max_area = IntegerField('Maximum Area', validators=[Optional()])
    min_price = IntegerField('Minimum Price', validators=[Optional()])
    max_price = IntegerField('Maximum Price', validators=[Optional()])
    available_from = DateField('Available From', format='%Y-%m-%d', validators=[Optional()])
    balcony = BooleanField('Balcony', validators=[Optional()])
    cellar = BooleanField('Cellar', validators=[Optional()])
    elevator = BooleanField('Elevator', validators=[Optional()])
    garage = BooleanField('Garage', validators=[Optional()])
    garden = BooleanField('Garden', validators=[Optional()])
    loggie = BooleanField('Loggie', validators=[Optional()])
    parking = BooleanField('Parking', validators=[Optional()])
    terrace = BooleanField('Terrace', validators=[Optional()])
    type = SelectMultipleField('Property Type', choices=[(type.value) for type in PropertyType], validators=[Optional()])
    furnished = SelectMultipleField('Furnished', choices=[(furnished.value) for furnished in Furnished], validators=[Optional()])
    status = SelectMultipleField('Property Status', choices=[(status.value) for status in PropertyStatus], validators=[Optional()])
    floor = IntegerField('Floor', validators=[Optional()])
    description = StringField('Description', validators=[Optional()])
    submit = SubmitField('Submit')
    min_score = IntegerField('Minimum Score', validators=[Optional()])
