from flask import Flask
from flask_table import Table, Col
from flask_sqlalchemy import SQLAlchemy
from wtforms import Form, StringField, SelectField
from sqlalchemy.orm import relationship

# set up sqlalchemy app & database
app = Flask(__name__)
app.config['SECRET_KEY'] = '41e2419b1b446d6eb75f46ee078cbf54'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)

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
class addProject(Form):
	id = db.Column(db.Integer, primary_key=True)
	name = StringField('')
	# url = StringField('')

# Table for displaying all projects in database
class Display(Table):
	id = Col('id', show=False)
	name = Col('Name')
	# url = Col('sheet_URL')
