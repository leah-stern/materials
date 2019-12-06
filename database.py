from flask import Flask
from flask_table import Table, Col
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, BooleanField
from wtforms.validators import DataRequired
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
import os

# set up sqlalchemy app & database
app = Flask(__name__)
app.config['SECRET_KEY'] = '41e2419b1b446d6eb75f46ee078cbf54'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
db = SQLAlchemy(app)

#TODO: what about the pdfs?? need a way to upload files
#TODO: and the structure PNG! should that be generated automatically or uploaded?
#TODO: click GHS hazard icons for each chemical
class Chemical(db.Model):
	id = db.Column(db.Integer, primary_key=True) # TODO: this should be the CAS number!!
	name = db.Column(db.String(200), nullable=True)
	alternate_name = db.Column(db.String(200), nullable=True)
	vendor = db.Column(db.String(200), nullable=True)
	CAS = db.Column(db.Integer, nullable=True)
	description = db.Column(db.String(200), nullable=True)

	# safety information
	hazard_note = db.Column(db.String(200), nullable=True)
	GHS_flammable = db.Column(db.Boolean, nullable=True)
	GHS_explosive = db.Column(db.Boolean, nullable=True)
	GHS_health_hazard = db.Column(db.Boolean, nullable=True)
	GHS_oxidizing = db.Column(db.Boolean, nullable=True)
	GHS_gas = db.Column(db.Boolean, nullable=True)
	GHS_irritant = db.Column(db.Boolean, nullable=True)
	GHS_environment = db.Column(db.Boolean, nullable=True)
	GHS_corrosive = db.Column(db.Boolean, nullable=True)
	GHS_toxic = db.Column(db.Boolean, nullable=True)

	# location
	building_location = db.Column(db.String(200), nullable=True)
	room_location = db.Column(db.String(200), nullable=True)
	cabinet_location = db.Column(db.String(200), nullable=True)
	shelf_location = db.Column(db.String(200), nullable=True)

	# lot_number = db.Column(db.String(200), nullable=True)
	# disposal_note = db.Column(db.String(200), nullable=True)
	# owner = db.Column(db.String(200), nullable=True)
	# contact_info = db.Column(db.String(200), nullable=True)
	# serial_num = db.Column(db.String(200), nullable=True)
	# catalog_num = db.Column(db.Integer, nullable=True)
	# amount = db.Column(db.Integer, nullable=True) #TODO: string for units?
	# unit_price = db.Column(db.Integer, nullable=True)
	# unit_size = db.Column(db.Integer, nullable=True)
	# chemical_URL = db.Column(db.String(200), nullable=True)
	# product_type = db.Column(db.String(200), nullable=True)
	# chemical_type = db.Column(db.String(200), nullable=True)
	# DOM = db.Column(db.String(200), nullable=True)
	# signal_word = db.Column(db.String(200), nullable=True)
	# source = db.Column(db.String(200), nullable=True)
	# technical_details = db.Column(db.String(200), nullable=True)
	# expiration_date = db.Column(db.String(200), nullable=True)
	# auto_reminder = db.Column(db.String(200), nullable=True)
	# bought_from = db.Column(db.String(200), nullable=True)
	# vendor_URL = db.Column(db.String(200), nullable=True)
	#TODO: history? date inventoried, changes

class Project(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(200), nullable=False)
	# sheet_URL = db.Column(db.String(200), nullable=True)
	# date_started = db.Column(db.String(200), nullable=True) #TODO: what format? how can we force the format?
	# business_unit = db.Column(db.String(200), nullable=True)
	# lead_experimenter = db.Column(db.String(200), nullable=True)
	# lead_PM = db.Column(db.String(200), nullable=True)
	# other_members = db.Column(db.String(200), nullable=True) #TODO: this should be a list
	# product_contact = db.Column(db.String(200), nullable=True)
	# goal = db.Column(db.String(200), nullable=True)
	# prior_data = db.Column(db.String(200), nullable=True) #TODO: what is this?
	# notable_formulations = db.Column(db.String(200), nullable=True) #TODO: what is this?

# Form for adding new projects to the database
class addProject(FlaskForm):
	id = db.Column(db.Integer, primary_key=True)
	name = StringField('')
	# url = StringField('')

# Table for displaying all projects in database
class displayFormulas(Table):
	id = Col('id', show=False)
	name = Col('Name')
	# url = Col('sheet_URL')

# Table for displaying all chemicals in database
class displayChemicals(Table):
	id = Col('id', show=False)
	name = Col('Name')
	vendor = Col('Vendor')
	CAS = Col('CAS Number')
	room_location = Col('Room')

# Form for adding new chemicals to the database
class addChemical(FlaskForm):
	id = db.Column(db.Integer, primary_key=True)
	name = StringField('')
	alternate_name = StringField('')
	vendor = StringField('')
	description = StringField('')

class searchForm(FlaskForm):
	id = db.Column(db.Integer, primary_key=True)
	search = StringField('')

