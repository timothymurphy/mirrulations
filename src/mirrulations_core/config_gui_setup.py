import requests
import random
import string
import json
import os
from appJar import gui

''' 
 This program will prompt the user for their regulations.gov API Key, as well as the IP and port
 of the work server they want to connect to. It will set up the config.json file, store the user's
 API Key, and generate a random ClientID.
'''


def connection_error():
    app.errorBox('Unable to connect!',
                 'We weren\'t able to connect to regulations.gov.\n'
                 'Please try again later.')


def invalid_key_error():
    app.errorBox('Invalid API key!',
                 'Your API key is invalid.\n'
                 'Please visit\n'
                 'https://regulationsgov.github.io/developers/\n'
                 'for an API key.')


def successful_login(ip, port, key, client_id):
    with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), '../../config.json'), 'wt') as file:
        file.write(json.dumps({
            'ip': ip,
            'port': port,
            'key': key,
            'client_id': client_id
        }, indent=4))
        file.close()

    app.infoBox('Success!',
                 'You are successfully logged in!')
    app.stop()


def press():

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
            successful_login(ip, port, key, client_id)


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
    app.addButton('Cancel', app.stop, column=5, row=2, colspan=3)
