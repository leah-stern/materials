from project_db import db, app, Project, addProject, Display
from flask import render_template, request, redirect
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from oauth2client.service_account import ServiceAccountCredentials
import gspread
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

@app.route('/', methods=['GET', 'POST'])
def home():
	# create database
	db.drop_all()
	db.create_all()

	# create form for adding new project to database
	form = addProject(request.form)

	# validate form
	if request.form:
		newProject = Project(
			name=request.form.get("Name"),
			# sheet_URL=request.form.get("URL")
		)

		# add and commit new chemical
		db.session.add(newProject)
		db.session.commit()

		open_sheet(newProject.name)
		# create_sheet(newProject.name)

	# get all projects to display in table format
	all_projects = Display(Project.query.all())
	all_projects.border = True

	# render the form and all projects
	return render_template("project_home.html", form=form, table=all_projects)

def open_sheet(name):
	# set up Google Drive API
	scope = ['https://spreadsheets.google.com/feeds',
			 'https://www.googleapis.com/auth/drive']
	creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
	client = gspread.authorize(creds)
	# service = build('drive', 'v2', credentials=creds)

	print(name)
	sheet = client.open("Test Sheet").sheet1
	print('opened!')


# Creates a new spreadsheet based on the name of the project
#TODO: folder location depends on what Nakul wants. I think it would be best if all projects
# are in the same folder, maybe create a folder for each project or just a spreadsheet would
# do? not sure if there are more files that go with the spreadsheet
def create_sheet(name):
	# set up Google Drive API
	scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive.file']
	creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
	client = gspread.authorize(creds)
	service = build('drive', 'v2', http=creds.authorize(Http()))

	# get "Chemical inventory" folder ID
	folder_id = '1hYOjsp-AzDL-ycPeKAzkW1QNRNFXsG0e'

	# set spreadsheet properties
	spreadsheet = {
		'properties': {
	    	'title': name,
	    	'parents':[{"id":"1hYOjsp-AzDL-ycPeKAzkW1QNRNFXsG0e"}]
		}
	}

	file_metadata = {
	    'name': 'Invoices',
	    'mimeType': 'application/vnd.google-apps.folder'
	}
	file = service.files().insert(body=file_metadata,
	                                    fields='id').execute()
	print(file.get('id'))

	file = service.files().insert(body=spreadsheet, fields='id, parents').execute()
	file_id = file.get('id')

	# file = service.files().get(fileId=file_id, fields='parents').execute()
	# prev = file.get('parents')
	# file = service.files().update(addParents=folder_id, fileId=file_id, fields='id, parents').execute()
	# folder = service.files().getParents().execute()
	# prev = ",".join(file.get('parents'))
	# file = service.files().update
	# file_id = file.get('parents')
	# print(file_id)
	# folder = service.files().get(fileI)


	# set up Google Sheets API
	# scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
	# creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
	# client = gspread.authorize(creds)
	# service = build('sheets', 'v4', credentials=creds)

	# # get "Chemical inventory" folder ID
	# folder_id = '1CzxahrxiVCyH4mB1ZRcHMDte_QFSp5XB'

	# # set spreadsheet properties
	# spreadsheet = {
	# 	'properties': {
	#     	'title': name
	# 	}
	# }

	# # create blank spreadsheet
	# spreadsheet = service.spreadsheets().create(body=spreadsheet, fields='spreadsheetId').execute()
	# sheet_id = spreadsheet.get('spreadsheetId')
	# print(sheet_id)

	# # get previous folder location and move to Chemical inventory folder
	# file = service.spreadsheets().getParents().execute()
	# prev = ",".join(file.get('parents'))
	# file = service.spreadsheets().update(spreadsheetId=sheet_id, addParents=folder_id, fields='id, parents').execute()


if __name__ == '__main__':
    app.run()



