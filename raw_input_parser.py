from __future__ import print_function

import os.path
import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Set sheet id as enviroment variable.
INTERFACE_ID = os.environ.get('INTERFACE')

# Only modify if scopes are modified on API dashboard
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def get_secure_connection() -> Credentials:
    creds = None
    # Built on first time setup, used in place of login.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    return creds

def get_ids(target_sheet) -> list:
    """Get sheet ids of each player interface."""
    creds = get_secure_connection()

    try:
        service = build('sheets', 'v4', credentials=creds)

        meta = service.spreadsheets().get(spreadsheetId=target_sheet).execute()
        sheets = meta.get('sheets','')

        return [x.get("properties",{})["title"] for x in sheets if x.get("properties",{})["title"] not in ["Unit Library","Item Library"]]
    except HttpError as error:
        # TODO(developer) - Handle errors from drive API.
        print(f'An Http error occurred: {error}')

def get_unit_lib(target_sheet) -> list:
    creds = get_secure_connection()

    try:
        service = build('sheets', 'v4', credentials=creds)
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=target_sheet,range=f"Unit Library!A:F").execute()

        parsed = parse_results(result.get('values', []),"admin")

        return dict(zip([x["Name"] for x in parsed],parsed))

    except HttpError as error:
        # TODO(developer) - Handle errors from drive API.
        print(f'An Http error occurred: {error}')

def get_info(ownerID_list,target_sheet) -> list:
    """Retrieve and process rows from each player interface."""
    creds = get_secure_connection()

    try:
        # Build connection to the service
        # This is the main interface
        service = build('sheets', 'v4', credentials=creds)
        sheet = service.spreadsheets()

        out_list = list()

        for ownerID in ownerID_list:
            result = sheet.values().get(spreadsheetId=target_sheet,range=f"{ownerID}!A:K").execute()

            values = result.get('values', [])

            out_list += parse_results(values,ownerID)

        return out_list

    except HttpError as error:
        # TODO(developer) - Handle errors from drive API.
        print(f'An error occurred: {error}')


def parse_results(results,owner):
    out = list()
    for row in results[1:]:
        cur = dict(zip(results[0],row))
        cur["Owner"] = owner
        out.append(cur)
    return out


if __name__ == "__main__":
    # print(get_info(get_ids(INTERFACE_ID),INTERFACE_ID))
    print(get_unit_lib(INTERFACE_ID))
