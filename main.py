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

import inspect
import json
from pprint import pprint

###############
# TODO
##############
# allow termination by listening to socket or something

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


def load_credentials():
    """Returns Dictionary of credential objects
    key: user ID(internal)
    value: credential obj
    """
    users = ['1', '2', '3']
    creds = {}

    # how to convert json to dict
    # credict = json.loads(creds['one'].to_json())
    # pprint(credict)
    # creds['one'] = Credentials.from_authorized_user_info(credict)

    for user in users:
        # The file token.json stores the user's access and refresh tokens,
        # and is created automatically when the authorization flow completes
        # for the first time.
        creds[user] = None

        token_fname = user+'token.json'

        # create add_user switch
        if os.path.exists(token_fname):
            creds[user] = Credentials\
                .from_authorized_user_file(token_fname, SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds[user] or not creds[user].valid:
            if creds[user] and\
                    creds[user].expired and creds[user].refresh_token:
                creds[user].refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json',
                    SCOPES
                )
                creds[user] = flow.run_local_server(port=0, open_browser=False)

            # Save the credentials for the next run
            with open(token_fname, 'w') as token:
                token.write(creds[user].to_json())

    return creds


def main():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """

    creds = load_credentials()
    users = list(creds.keys())

    # instanciate stuffs
    service = {}
    for user in users:
        service[user] = build('gmail', 'v1', credentials=creds[user])

    notify = pyNotify.PyNotify()

    oldDF = {}
    newDF = {}

    # MAIN LOOP
    while True:
        for user in users:
            try:
                results = service[user].users()\
                    .messages().list(userId='me').execute()
            except BaseException as e:
                print(e)
                service = build('gmail', 'v1', credentials=creds[user])
                results = service[user].users()\
                    .messages().list(userId='me').execute()

            # email address of user
            addr = service[user].users()\
                .getProfile(userId='me').execute()['emailAddress']

            mesgs = results.get('messages', [])
            newDF[user] = pd.DataFrame(mesgs).set_index('id', drop=True)

            # define newMail: mails not present in oldDF but is in newDF
            if not (user in oldDF.keys()):
                oldDF[user] = newDF[user]
            newMail = newDF[user][~newDF[user].isin(oldDF[user])].dropna()

            for _id in newMail.index:
                txt = service[user].users()\
                    .messages().get(userId='me', id=_id).execute()

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
                    print(f'User {user}: {addr}')
                    print(f'Subject: {subject}')
                    print(f'From: {sender}')
                    print('\n')

                    notify.notify('gmail', addr, sender + '\n' + subject)

                except BaseException as e:
                    print(e)
                    pass

            oldDF[user] = newDF[user]

            # repeat the above process for multiple users

        try:
            time.sleep(300)
        except KeyboardInterrupt:
            print('Ctrl-C Exiting')
            sys.exit(0)


if __name__ == '__main__':
    main()
