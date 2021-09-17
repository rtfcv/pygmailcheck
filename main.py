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

# config dict
# top level keys represent a user
#
auth = None
config_dir = ''
auth_path = ''


def load_config():
    global auth
    global config_dir
    global auth_path

    __platform__ = sys.platform
    if __platform__ == 'win32':
        HOME = os.environ.get('HOMEPATH')
        config_dir = os.path.join(HOME, r'AppData\Roaming\pyGmailCheck')
        auth_path = os.path.join(config_dir, 'userdata.json')

    elif __platform__ == 'linux':
        HOME = os.environ.get('HOME')
        config_dir = os.path.join(HOME, '.config/pyGmailCheck')
        auth_path = os.path.join(config_dir, 'userdata.json')

    else:
        print(f'Platform {__platform__} not supported')

    # try to load config
    try:
        with open(auth_path, mode='r') as file:
            auth = json.load(file)
    except FileNotFoundError:
        auth = {}


def save_config():
    # global config
    # global config_dir
    # global config_path
    if not os.path.exists(config_dir):
        os.makedirs(config_dir, exist_ok=True)

    with open(auth_path, mode='w') as file:
        json.dump(auth, file, indent=2)


def load_credentials():
    """Returns Dictionary of credential objects
    key: user ID(internal)
    value: credential obj
    """
    global auth
    load_config()

    users = list(auth.keys())
    creds = {}

    if len(users) == 0:
        users = [1, 2, 3]
        for user in users:
            auth[user] = {}

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
        if 'token' in auth[user].keys():
            creds[user] = Credentials\
                .from_authorized_user_info(auth[user]['token'], SCOPES)

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
            auth[user]['token'] = json.loads(creds[user].to_json())

    save_config()
    return creds


def main():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    global auth

    creds = load_credentials()
    users = list(creds.keys())

    # instanciate stuffs
    service = {}
    for user in users:
        service[user] = build('gmail', 'v1', credentials=creds[user])

    # TODO:
    # temporary measure
    # remove this and put similar procedure
    load_config()
    for user in users:
        addr = service[user].users()\
            .getProfile(userId='me').execute()['emailAddress']
        auth[user]['email'] = addr
    save_config()

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
                    # send notification
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
