from __future__ import print_function
import pickle
import os.path
import flask
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from google.oauth2 import id_token
from google.auth.transport import requests
from httplib2 import Http
from database import db, app, Chemical, addChemical, displayChemicals, searchForm, Project, addProject, displayFormulas, Formulation, Results
from flask import render_template, request, redirect
import os
from sqlalchemy import func
from flask import jsonify
from flask_cors import cross_origin

# import oauth2client
# from oauth2client import file, client, tools
# from google_auth_oauthlib.flow import InstalledAppFlow
# from google.auth.transport.requests import Request
# from wtforms.ext.sqlalchemy.fields import QuerySelectField
# import gspread

# Scopes for Google Drive and Google Sheets APIs
SCOPES = ['https://www.googleapis.com/auth/drive',
      'https://www.googleapis.com/auth/spreadsheets']

CLIENT_SECRETS_FILE = "client_secret.json"

API_SERVICE_NAME = 'drive'
API_VERSION = 'v3'

@app.route('/', methods=['GET', 'POST'])
def home():
    # create database
    db.create_all()

    return render_template("home.html")

@app.route('/chemicals', methods=['GET', 'POST'])
def chemical_inventory():
    # form for adding new chemicals to database
    form = addChemical(request.form)

    # form for searching chemicals in database
    search = searchForm(request.form)

    # get all names for autofill search
    tags = jsonify([chemical.name for chemical in Chemical.query.all()])

    if request.method == 'POST':
        if request.form['button'] == 'Add':
            created = create_chemical(form)
            print(created, flush=True)
        else: 
            selection = search.data['search']
            if selection != '':
                results = Chemical.query.filter(Chemical.name.ilike('%' + str(selection) + '%'))
                return render_template("chemical_db.html", form=form, allTags=tags, searchForm=search, chemicals=results)

    # # get all chemicals to display in table format, order by name
    all_chemicals = Chemical.query.order_by(Chemical.name).all()

    # render the form and all chemicals
    return render_template("chemical_db.html", form=form, allTags=tags, searchForm=search, chemicals=all_chemicals)

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

# TODO: only one details page, select chemical or proj details based on query parameter
@app.route('/chemical_details', methods=['GET', 'POST'])
def chemical_details():
    # get chemical id from query parameter
    chemical_id = request.args.get('id', default = -1, type=int)

    # get chemical with the current chemical ID
    currentChemical = Chemical.query.filter(Chemical.id==chemical_id).first()

    return render_template("chemical_details.html", selected=currentChemical)

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

    # form for searching projects in database
    search = searchForm(request.form)

    # validate form
    if request.method == 'POST':
        if request.form['button'] == 'Add':
            newProject = Project(
                name=request.form.get("Name"),
                project_lead=request.form.get("Project Lead"),
                goal=request.form.get("Goal"),
                date_started=request.form.get("Date Started"),
                formulations = {}
            )

            newProject.formulations.chemicals = {}

            populate_formulations(newProject)

            # add and commit new chemical
            db.session.add(newProject)
            db.session.commit()

            # create_sheet(newProject.name)

        else:
            selection = search.data['search']
            if selection != '':
                results = Project.query.join(Formulation, Project.formulations)\
                                .filter( (Project.name.ilike('%' + str(selection) + '%')) |\
                                (Formulation.name.ilike('%' + str(selection) + '%')))

                return render_template("formulation_db.html", form=form, projects=results, searchForm=search)

    # get all projects to display in table format
    all_projects = Project.query.order_by(Project.name).all()

    # render the form and all projects
    return render_template("formulation_db.html", form=form, projects=all_projects, searchForm=search)

# TODO: loop through spreadsheet data once i get that working
def populate_formulations(project):
    # TODO: remove, this is just for testing, read from sheet to create
    # could appending all this be a function defined within the formulation class?
    everybody = Chemical.query.all()
    one = Chemical.query.first()

    sample_results_1 = Results(
        thoughts = 'just a thought',
        A_MA = 'A/MA',
        composition_notes = 'none',
        filler_vol_percent = 23,
        filler_weight_percent = 31
    )

    sample_results_2 = Results(
        thoughts = 'another thought',
        A_MA = 'A',
        composition_notes = 'none',
        filler_vol_percent = 27,
        filler_weight_percent = 30
    )

    newFormula1 = Formulation(name='H30f0')
    for chemical in everybody:
        newFormula1.chemicals.append(chemical)
    # newFormula1.results.append(sample_results_1)
    project.formulations.append(newFormula1)

    newFormula2 = Formulation(name='HFm006_f55')
    newFormula2.chemicals.append(one)
    # newFormula2.results.append(sample_results_2)
    project.formulations.append(newFormula2)

@app.route('/project_details', methods=['GET', 'POST'])
def project_details():
    # get project id from query parameter
    project_id = request.args.get('id', default = -1, type=int)

    # get project with the current project ID
    currentProject = Project.query.filter(Project.id==project_id).first()

    # pass the current project to the project_details page
    return render_template("project_details.html", selected=currentProject)

@app.route('/authenticate', methods=['GET', 'POST'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def authenticate():
    print("here!", flush=True)
    # get token id from POST
    token_id = request.args.get('idtoken', default = -1, type=int)

    print(token_id, flush=True)

    return render_template("home.html")

    # if 'credentials' not in flask.session:
    #     return flask.redirect('authorize')

    # # Load credentials from the session.
    # credentials = google.oauth2.credentials.Credentials(**flask.session['credentials'])
    # print("Credentials: ", credentials)

    # drive = googleapiclient.discovery.build(API_SERVICE_NAME, API_VERSION, credentials=credentials)

    # files = drive.files().list().execute()

    # # Save credentials back to session in case access token was refreshed.
    # # ACTION ITEM: In a production app, you likely want to save these
    # #              credentials in a persistent database instead.
    # flask.session['credentials'] = credentials_to_dict(credentials)

    # return flask.redirect(flask.url_for('home'))

@app.route('/authorize')
def authorize():
    # Use the client_secret.json file to identify the application requesting
    # authorization. The client ID (from that file) and access scopes are required.
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)

    # Indicate where the API server will redirect the user after the user completes
    # the authorization flow. The redirect URI is required. The value must exactly
    # match one of the authorized redirect URIs for the OAuth 2.0 client, which you
    # configured in the API Console. If this value doesn't match an authorized URI,
    # you will get a 'redirect_uri_mismatch' error.
    flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

    # Generate URL for request to Google's OAuth 2.0 server.
    # Use kwargs to set optional request parameters.
    authorization_url, state = flow.authorization_url(
        # Enable offline access so that you can refresh an access token without
        # re-prompting the user for permission. Recommended for web server apps.
        access_type='offline',
        # Enable incremental authorization. Recommended as a best practice.
        include_granted_scopes='true')

    flask.session['state'] = state

    return flask.redirect(authorization_url)

@app.route('/oauth2callback')
def oauth2callback():
  # Specify the state when creating the flow in the callback so that it can
  # verified in the authorization server response.
  state = flask.session['state']

  flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
  flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

  # Use the authorization server's response to fetch the OAuth 2.0 tokens.
  authorization_response = flask.request.url
  print("Auth response: ", authorization_response)
  flow.fetch_token(authorization_response=authorization_response)

  # Store credentials in the session.
  # ACTION ITEM: In a production app, you likely want to save these
  #              credentials in a persistent database instead.
  credentials = flow.credentials
  flask.session['credentials'] = credentials_to_dict(credentials)

  return flask.redirect(flask.url_for('authenticate'))

def credentials_to_dict(credentials):
  return {'token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'token_uri': credentials.token_uri,
          'client_id': credentials.client_id,
          'client_secret': credentials.client_secret,
          'scopes': credentials.scopes}

def create_sheet(projectName):
    creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', SCOPES)

    service = build('drive', 'v4', credentials=creds, http=creds.authorize(Http()))
    sheets = build('sheets', 'v4', credentials=creds)

    body = {
        'mimeType': 'application/vnd.google-apps.spreadsheet',
        'name': projectName,
        'supportsAllDrives': True,
        'driveId': '0ADcJ0eHZoAh4Uk9PVA',
    }

    file = service.files().create(body=body).execute()
    sheet_id = file.get('id')

    # # print(list)

    # data = {'requests': [
    #     {'setDataValidation': {
    #     'range': {
    #         'startRowIndex': 0,
    #         'endRowIndex': 1,
    #         'startColumnIndex': 0,
    #         'endColumnIndex': 1
    #     },
    #     'rule': {
    #         'condition': {
    #             'type': 'ONE_OF_LIST',
    #                 'values': [
    #                     {'userEnteredValue': 'one'},
    #                     {'userEnteredValue': 'two'},
    #                     {'userEnteredValue': 'three'},
    #                 ]
    #         },
    #         'strict': True
    #     }}}]}

    # update = sheets.spreadsheets().batchUpdate(spreadsheetId=sheet_id, body=data).execute()

if __name__ == '__main__':
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    app.run(host='0.0.0.0')