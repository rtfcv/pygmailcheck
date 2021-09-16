from __future__ import print_function
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import pandas as pd
import time
import sys
import pyNotify

###############
# TODO
##############
# allow termination by listening to socket or something

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


def main():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None

    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.

    # Later create multiple files for token                      ##############
    # create add_user switch
    # create
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    # user = 'example'
    # if os.path.exists(+'example/token.json'):
    #     creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # service = {}
    # users = ['one', 'two']

    # for user in users:
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json',
                SCOPES
            )
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    # Later create multiple files for token                      ##############

    # instanciate stuffs
    service = build('gmail', 'v1', credentials=creds)

    notify = pyNotify.PyNotify()

    oldDF = None
    newDF = None

    # MAIN LOOP
    while True:
        try:
            results = service.users().messages().list(userId='me').execute()
        except BaseException as e:
            print(e)
            service = build('gmail', 'v1', credentials=creds)
            results = service.users().messages().list(userId='me').execute()

        mesgs = results.get('messages', [])
        newDF = pd.DataFrame(mesgs).set_index('id', drop=True)

        if oldDF is None:
            oldDF = newDF
        newMail = newDF[~newDF.isin(oldDF)].dropna()

        for _id in newMail.index:
            txt = service.users().messages().get(userId='me', id=_id).execute()

            # Use try-except to avoid any Errors
            try:
                # Get value of 'payload' from dictionary 'txt'
                payload = txt['payload']
                headers = payload['headers']
            except BaseException as e:
                print(e)
                continue

            try:
                # Look for Subject and Sender Email in the headers
                for d in headers:
                    if d['name'] == 'Subject':
                        subject = d['value']
                    if d['name'] == 'From':
                        sender = d['value']

                # Printing the subject, sender's email and message
                print(f'Subject: {subject}')
                print(f'From: {sender}')
                print('\n')

                notify.notify('gmail', sender, subject)

            except BaseException as e:
                print(e)
                pass

        oldDF = newDF

        # repeat the above process for multiple users

        try:
            time.sleep(300)
        except KeyboardInterrupt:
            print('Ctrl-C Exiting')
            sys.exit(0)


if __name__ == '__main__':
    main()
