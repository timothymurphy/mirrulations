import requests
import random
import string
import json
from appJar import gui

connection_error_title = 'Unable to connect!'
connection_error_description = 'We weren\'t able to connect to regulations.gov.\n' \
                               'Please try again later.'

invalid_key_error_title = 'Invalid API key!'
invalid_key_error_description = 'Your API key is invalid.\n' \
                                'Please visit\n' \
                                'https://regulationsgov.github.io/developers/\n' \
                                'for an API key.'

successful_login_title = 'Success!'
successful_login_description = 'You are successfully logged in!'


def gui_client_setup(config_path):

    def press():

        def connection_error():
            app.errorBox(connection_error_title, connection_error_description)
            app.stop()
            exit()

        def invalid_key_error():
            app.errorBox(invalid_key_error_title, invalid_key_error_description)
            app.stop()
            exit()

        def successful_login():
            with open(config_path, 'wt') as file:
                file.write(json.dumps({
                    'ip': ip,
                    'port': port,
                    'key': key,
                    'client_id': client_id
                }, indent=4))
                file.close()
            app.infoBox(successful_login_title, successful_login_description)
            app.stop()

        ip = app.getEntry('IP1') + '.' + app.getEntry('IP2') + '.' + app.getEntry('IP3') + '.' + app.getEntry('IP4')
        port = app.getEntry('Port')
        key = app.getEntry('API Key')
        client_id = ''.join(random.choices(string.ascii_letters + string.digits, k=16))

        try:
            r = requests.get('https://api.data.gov/regulations/v3/documents.json?api_key=' + key)
        except requests.ConnectionError:
            connection_error()
        else:
            if r.status_code == 403:
                invalid_key_error()
            elif r.status_code > 299 and r.status_code != 429:
                connection_error()
            else:
                successful_login()

    def cancel():
        app.stop()
        exit()

    with gui('Mirrulations Login') as app:

        app.setSize('750x100')
        app.setFont(size=20, family='Gill Sans')
        app.resizable = False

        app.addLabel('IPv4 Address', text='Server IPv4 Address:', column=0, row=0)
        app.setLabelWidth('IPv4 Address', 20)

        app.addEntry('IP1', column=1, row=0)
        app.setEntryWidth('IP1', 12)

        app.addLabel('stop1', text='.', column=2, row=0)
        app.setLabelWidth('stop1', 4)

        app.addEntry('IP2', column=3, row=0)
        app.setEntryWidth('IP2', 12)

        app.addLabel('stop2', text='.', column=4, row=0)
        app.setLabelWidth('stop2', 4)

        app.addEntry('IP3', column=5, row=0)
        app.setEntryWidth('IP3', 12)

        app.addLabel('stop3', text='.', column=6, row=0)
        app.setLabelWidth('stop3', 4)

        app.addEntry('IP4', column=7, row=0)
        app.setEntryWidth('IP4', 12)

        app.addLabel('colon', text=':', column=8, row=0)
        app.setLabelWidth('colon', 4)

        app.addEntry('Port', column=9, row=0)
        app.setEntryWidth('Port', 16)
        app.setEntryDefault('Port', 'Port')

        app.addLabel('API Key:', column=0, row=1)
        app.addEntry('API Key', column=1, row=1, colspan=9)

        app.addButton('Submit', press, column=1, row=2, colspan=3)
        app.addButton('Cancel', cancel, column=5, row=2, colspan=3)


def gui_server_setup(config_path):

    def press():

        def connection_error():
            app.errorBox(connection_error_title, connection_error_description)
            app.stop()
            exit()

        def invalid_key_error():
            app.errorBox(invalid_key_error_title, invalid_key_error_description)
            app.stop()
            exit()

        def successful_login():
            with open(config_path, 'wt') as file:
                file.write(json.dumps({
                    'key': key,
                    'client_id': client_id
                }, indent=4))
                file.close()
            app.infoBox(successful_login_title, successful_login_description)
            app.stop()

        key = app.getEntry('API Key')
        client_id = ''.join(random.choices(string.ascii_letters + string.digits, k=16))

        try:
            r = requests.get('https://api.data.gov/regulations/v3/documents.json?api_key=' + key)
        except requests.ConnectionError:
            connection_error()
        else:
            if r.status_code == 403:
                invalid_key_error()
            elif r.status_code > 299 and r.status_code != 429:
                connection_error()
            else:
                successful_login()

    def cancel():
        app.stop()
        exit()

    with gui('Mirrulations Login') as app:

        app.setSize('750x60')
        app.setFont(size=20, family='Gill Sans')
        app.resizable = False

        app.addLabel('API Key:', column=0, row=0)
        app.addEntry('API Key', column=1, row=0, colspan=9)

        app.addButton('Submit', press, column=1, row=1, colspan=3)
        app.addButton('Cancel', cancel, column=5, row=1, colspan=3)


def terminal_client_setup(config_path):

    def connection_error():
        print(connection_error_title + '\n' + connection_error_description)
        exit()

    def invalid_key_error():
        print(invalid_key_error_title + '\n' + invalid_key_error_description)
        exit()

    def successful_login():
        with open(config_path, 'wt') as file:
            file.write(json.dumps({
                'ip': ip,
                'port': port,
                'key': key,
                'client_id': client_id
            }, indent=4))
            file.close()
        print(successful_login_title + '\n' + successful_login_description)

    ip = input('IP:\n')
    port = input('Port:\n')
    key = input('API Key:\n')
    client_id = ''.join(random.choices(string.ascii_letters + string.digits, k=16))

    try:
        r = requests.get('https://api.data.gov/regulations/v3/documents.json?api_key=' + key)
    except requests.ConnectionError:
        connection_error()
    else:
        if r.status_code == 403:
            invalid_key_error()
        elif r.status_code > 299 and r.status_code != 429:
            connection_error()
        else:
            successful_login()


def terminal_server_setup(config_path):

    def connection_error():
        print(connection_error_title + '\n' + connection_error_description)
        exit()

    def invalid_key_error():
        print(invalid_key_error_title + '\n' + invalid_key_error_description)
        exit()

    def successful_login():
        with open(config_path, 'wt') as file:
            file.write(json.dumps({
                'key': key,
                'client_id': client_id
            }, indent=4))
            file.close()
        print(successful_login_title + '\n' + successful_login_description)

    key = input('API Key:\n')
    client_id = ''.join(random.choices(string.ascii_letters + string.digits, k=16))

    try:
        r = requests.get('https://api.data.gov/regulations/v3/documents.json?api_key=' + key)
    except requests.ConnectionError:
        connection_error()
    else:
        if r.status_code == 403:
            invalid_key_error()
        elif r.status_code > 299 and r.status_code != 429:
            connection_error()
        else:
            successful_login()
