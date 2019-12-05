from chemical_db import db, app, Chemical, addChemical, displayChemicals, searchForm, Project, addProject, displayFormulas
from flask import render_template, request, redirect
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from oauth2client.service_account import ServiceAccountCredentials
import gspread
import test_drive
import logging

@app.route('/', methods=['GET', 'POST'])
def home():
    # create database
    # db.drop_all()
    db.create_all(bind='formulations')
    return render_template("home.html")

@app.route('/chemicals', methods=['GET', 'POST'])
def chemical_inventory():
    # form for adding new chemicals to database
    form = addChemical(request.form)

    # form for searching chemicals in database
    search = searchForm(request.form)

    if request.method == 'POST':
        if request.form['button'] == 'Add':
            create_chemical(form)
        else: 
            return search_chemical(search)

    # get all names for autofill search
    tags = [chemical.name for chemical in Chemical.query.all()]

    # get all chemicals to display in table format, order by name
    all_chemicals = displayChemicals(Chemical.query.order_by(Chemical.name).all())
    all_chemicals.border = True

    # test_drive.create_sheet(Chemical.query.order_by(Chemical.name).all())

    # render the form and all chemicals
    return render_template("chemical_db.html", form=form, table=all_chemicals, allTags=tags, searchForm=search)

# Create a new chemical based on form entries and add it to the database
def create_chemical(form):
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
def search_chemical(form):
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

@app.route('/formulations', methods=['GET', 'POST'])
def formulation_database():
    # create form for adding new project to database
    form = addProject(request.form)
    logging.info("here")

    # validate form
    if request.method == 'POST':
        newProject = Project(
            name=request.form.get("Name")
        )

        print("NEW PROJECT ALERT: ", newProject.name)
        # add and commit new chemical
        db.session.add(newProject)
        db.session.commit()

        create_sheet(newProject.name)
        print('created')

    # get all projects to display in table format
    all_projects = displayFormulas(Project.query.all())
    all_projects.border = True

    # render the form and all projects
    return render_template("project_home.html", form=form, table=all_projects)

def create_sheet(projectName):
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('drive', 'v3', credentials=creds)
    sheets = build('sheets', 'v4', credentials=creds)

    body = {
        'mimeType': 'application/vnd.google-apps.spreadsheet',
        'name': projectName,
    }

    file = service.files().create(body=body).execute()
    sheet_id = file.get('id')

    # print(list)

    data = {'requests': [
        {'setDataValidation': {
        'range': {
            'startRowIndex': 0,
            'endRowIndex': 1,
            'startColumnIndex': 0,
            'endColumnIndex': 1
        },
        'rule': {
            'condition': {
                'type': 'ONE_OF_LIST',
                    'values': [
                        {'userEnteredValue': 'one'},
                        {'userEnteredValue': 'two'},
                        {'userEnteredValue': 'three'},
                    ]
            },
            'strict': True
        }}}]}

    update = sheets.spreadsheets().batchUpdate(spreadsheetId=sheet_id, body=data).execute()

if __name__ == '__main__':
    app.run(host='0.0.0.0')