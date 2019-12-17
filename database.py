from flask import Flask
from flask_table import Table, Col
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
# from flask_script import Manager
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, BooleanField, IntegerField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, Optional
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
import os
from flask_cors import CORS

# set up sqlalchemy app & database
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
app.config['SECRET_KEY'] = '41e2419b1b446d6eb75f46ee078cbf54'
app.config['CORS_HEADERS'] = 'Content-Type'
os.environ['DATABASE_URL'] = 'postgresql://postgres:postgres@postgres/postgres'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
db = SQLAlchemy(app)
migrate = Migrate(app, db) 
# manager = Manager(app)

# manager.add_command('db', MigrateCommand)

# association table to handle many-to-many relationship between chemicals and formulations
association = db.Table('association',
	db.Column('formulation_id', db.Integer, db.ForeignKey('formulation.formula_id'), primary_key=True),
	db.Column('chemical_id', db.Integer, db.ForeignKey('chemical.id'), primary_key=True)
)

#TODO: what about the pdfs?? need a way to upload files
#TODO: and the structure PNG! should that be generated automatically or uploaded?
#TODO: click GHS hazard icons for each chemical
class Chemical(db.Model):
	id = db.Column(db.Integer, primary_key=True) # TODO: this should be the CAS number!!
	formulas= db.relationship('Formulation', secondary=association, lazy='dynamic')
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

	def __repr__(self):
		return self.name

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
	project_lead = db.Column(db.String(200), nullable=True)
	goal = db.Column(db.String(200), nullable=True)
	date_started = db.Column(db.String(200), nullable=True) #TODO: datetime format
	sheet_ID = db.Column(db.String(200), nullable=True)
	formulations = db.relationship('Formulation', backref='id', lazy='dynamic')

	def __repr__(self):
		return self.name

	# business_unit = db.Column(db.String(200), nullable=True)
	# other_members = db.Column(db.String(200), nullable=True) #TODO: this should be a list
	# product_contact = db.Column(db.String(200), nullable=True)
	# prior_data = db.Column(db.String(200), nullable=True) #TODO: what is this?
	# notable_formulations = db.Column(db.String(200), nullable=True) #TODO: what is this?

class Formulation(db.Model):
	formula_id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(200), nullable=False)
	project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
	chemicals = db.relationship('Chemical', secondary='association', lazy='dynamic')
	# chemical_amounts = db.relationship('Amounts', backref='formula_id', lazy='dynamic')
	results = db.relationship('Results', uselist=False, backref='formula_id')

	def __repr__(self):
		return self.name

# class Amounts(db.Model):
# 	id = db.Column(db.Integer, primary_key=True)
# 	chemical_id = db.Column(db.Integer, nullable=False)
# 	value = db.Column(db.Integer, nullable=True)
# 	formulation = db.Column(db.Integer, db.ForeignKey('formulation.formula_id'), nullable=False)
# 	# TODO: add weight in grams

class Results(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	thoughts = db.Column(db.String(200), nullable=True)
	A_MA = db.Column(db.String(200), nullable=True)
	composition_notes = db.Column(db.String(200), nullable=True)
	filler_vol_percent = db.Column(db.Integer, nullable=True)
	filler_weight_percent = db.Column(db.Integer, nullable=True)
	formulation = db.Column(db.Integer, db.ForeignKey('formulation.formula_id'), nullable=False)
	# dp = db.Column(db.Integer, nullable=True)
	# ec = db.Column(db.Integer, nullable=True)
	# UTS = db.Column(db.Integer, nullable=True)
	# tensile_modulus = db.Column(db.Integer, nullable=True)
	# strain_at_break = db.Column(db.Integer, nullable=True)
	# FS = db.Column(db.Integer, nullable=True)
	# flexural_modulus = db.Column(db.Integer, nullable=True)
	# flex_strain_at_break = db.Column(db.Integer, nullable=True)
	# viscosity_25C = db.Column(db.Integer, nullable=True)
	# viscosity_35C = db.Column(db.Integer, nullable=True)
	# tg = db.Column(db.Integer, nullable=True)
	# HDT = db.Column(db.Integer, nullable=True)

# Form for adding new projects to the database
class addProject(FlaskForm):
	id = db.Column(db.Integer, primary_key=True)
	name = StringField('')

# Table for displaying all projects in database
class displayFormulas(Table):
	id = Col('id', show=False)
	name = Col('Name')
	project_lead = Col('Project Lead')

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

def chemical_query(): return Chemical.query

class refineSearchForm(FlaskForm):
	id = db.Column(db.Integer, primary_key=True)
	ingredient = QuerySelectField(query_factory = chemical_query, allow_blank=True)
	volume_filler = IntegerField('% volume of filler ', validators = [Optional()])


# if __name__ == '__main__':
# 	manager.run()

