from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, IntegerField, BooleanField, SubmitField, SelectMultipleField, DateField
from wtforms.validators import DataRequired, Optional
from disposition import Disposition
from property_type import PropertyType
from furnished import Furnished
from property_status import PropertyStatus


class UserPreferencesForm(FlaskForm):
    location = SelectField('Location', validators=[DataRequired()], choices=["Praha", "Brno", "Ostrava"])
    estate_type = SelectField('Estate Type', validators=[DataRequired()], choices=["Apartment", "House"])
    listing_type = SelectField('Listing Type', validators=[DataRequired()], choices=["Sale", "Rent"])
    points_of_interest = StringField('Points of Interest', validators=[Optional()])
    disposition = SelectMultipleField('Disposition', choices=[(d.value) for d in Disposition], validators=[Optional()])
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
    type = SelectMultipleField('Property Type', choices=[(d.value) for d in PropertyType], validators=[Optional()])
    furnished = SelectMultipleField('Furnished', choices=[(d.value) for d in Furnished], validators=[Optional()])
    status = SelectMultipleField('Property Status', choices=[(d.value) for d in PropertyStatus], validators=[Optional()])
    floor = IntegerField('Floor', validators=[Optional()])
    description = StringField('Description', validators=[Optional()])
    submit = SubmitField('Submit')
    weight_area = IntegerField('Area Weight', validators=[Optional()])
    weight_rent = IntegerField('Rent Weight', validators=[Optional()])
    weight_disposition = IntegerField('Disposition Weight', validators=[Optional()])
    weight_garden = IntegerField('Garden Weight', validators=[Optional()])
    weight_balcony = IntegerField('Balcony Weight', validators=[Optional()])
    weight_cellar = IntegerField('Cellar Weight', validators=[Optional()])
    weight_loggie = IntegerField('Loggie Weight', validators=[Optional()])
    weight_elevator = IntegerField('Elevator Weight', validators=[Optional()])
    weight_terrace = IntegerField('Terrace Weight', validators=[Optional()])
    weight_garage = IntegerField('Garage Weight', validators=[Optional()])
    weight_parking = IntegerField('Parking Weight', validators=[Optional()])
    weight_poi_distance = IntegerField('POI Distance Weight', validators=[Optional()])
    min_score = IntegerField('Minimum Score', validators=[Optional()])
