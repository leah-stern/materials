from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive',
      'https://www.googleapis.com/auth/spreadsheets']

def create_sheet():
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
        'name': 'Test Sheet',
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
    create_sheet()