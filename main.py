from chemical_db import db, app, Chemical, addChemical, Display, searchForm
from flask import render_template, request, redirect
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from oauth2client.service_account import ServiceAccountCredentials
import gspread

# @app.route('/', methods=['GET', 'POST'])
# def home():
# 	if request.method == 'POST':
# 		if request.form['redirec']

@app.route('/', methods=['GET', 'POST'])
def home():
	# create database
	# db.drop_all()
	db.create_all()

	# form for adding new chemicals to database
	form = addChemical(request.form)

	# form for searching chemicals in database
	search = searchForm(request.form)

	if request.method == 'POST':
		if request.form['button'] == 'Add':
			createChemical(form)
		else: 
			return searchChemicals(search)

	# get all names for autofill search
	tags = [chemical.name for chemical in Chemical.query.all()]

	# get all chemicals to display in table format, order by name
	all_chemicals = Display(Chemical.query.order_by(Chemical.name).all())
	all_chemicals.border = True

	# render the form and all chemicals
	return render_template("chemical_db.html", form=form, table=all_chemicals, allTags=tags, searchForm=search)

# Create a new chemical based on form entries and add it to the database
def createChemical(form):
	# validate form
	if request.form:
		# create new chemical from form data
		newChemical = Chemical(
			name = request.form.get("Name"),
			alternate_name = request.form.get("Alternate"),
			vendor = request.form.get("Vendor"),
			CAS = request.form.get("CAS"),
			description = request.form.get("Description"),
			hazard_note = request.form.get("Hazard Note"),
			GHS_flammable = False,
			GHS_explosive = False,
			GHS_health_hazard = False,
			GHS_oxidizing = False,
			GHS_gas = False,
			GHS_irritant = False,
			GHS_environment = False,
			GHS_corrosive = False,
			GHS_toxic = False,
			building_location = request.form.get("Building"),
			room_location = request.form.get("Room"),
			cabinet_location = request.form.get("Cabinet"),
			shelf_location = request.form.get("Shelf")
		)

		# assign GHS hazards based on checked boxes
		assign_GHS_values(form, newChemical)

		# add and commit new chemical
		db.session.add(newChemical)
		db.session.commit()

# Search chemicals by name
def searchChemicals(form):
	selection = form.data['search']
	print(selection)

	results = Chemical.query.filter(Chemical.name==str(selection))

	result_table = Display(results)
	result_table.border = True

	return render_template('results.html', table=result_table)

# TODO: this could be a lot more elegant, a loop or switch statement would probably be better
def assign_GHS_values(form, newChemical):
	if request.form.get("Flammable"):
		newChemical.GHS_flammable=True

	if request.form.get("Explosive"):
		newChemical.GHS_explosive=True

	if request.form.get("Health Hazard"):
		newChemical.GHS_health_hazard=True

	if request.form.get("Oxidizing"):
		newChemical.GHS_oxidizing=True

	if request.form.get("Compressed Gas"):
		newChemical.GHS_gas=True

	if request.form.get("Irritant"):
		newChemical.GHS_irritant=True

	if request.form.get("Environment"):
		newChemical.GHS_environment=True

	if request.form.get("Corrosive"):
		newChemical.GHS_corrosive=True

	if request.form.get("Toxic"):
		newChemical.GHS_toxic=True


if __name__ == '__main__':
	app.run(host='0.0.0.0')