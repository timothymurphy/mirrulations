import requests
import os
import random
import string
import json
from appJar import gui
from pathlib import Path

''' 
 This program will prompt the user for their regulations.gov API Key, as well as the IP and port
 of the work server they want to connect to. It will set up the config.json file, store the user's
 API Key, and generate a random ClientID.
'''


def press(button):

    if button == 'Cancel':
        app.stop()

    ip = app.getEntry('IP1') + '.' + app.getEntry('IP2') + '.' + app.getEntry('IP3') + '.' + app.getEntry('IP4')
    port = app.getEntry('Port')
    key = app.getEntry('API Key')
    user = ''.join(random.choices(string.ascii_letters + string.digits, k=16))

    if True:
        app.errorBox("Unable to connect!",
                     "We weren't able to connect to regulations.gov.\n"
                     "Please try again later.")
    elif True:
        app.errorBox("Invalid API key!",
                     "Your API key is invalid.\n"
                     "Please visit\n"
                     "https://regulationsgov.github.io/developers/\n"
                     "for an API key.")
    else:
        with open("config.json", "w") as file:
            file.write(json.dumps({
                "ip": ip,
                "port": port,
                "key": key,
                "user": user
            }, indent=4))
            file.close()
            app.stop()


with gui('Mirrulations Login') as app:

    app.setSize('700x100')
    app.setFont(size=20, family="Gill Sans")
    app.resizable = False

    app.addLabel('IPv4 Address', text='IPv4 Address:', column=0, row=0)
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
    app.addButton('Cancel', press, column=5, row=2, colspan=3)

    app.go()
