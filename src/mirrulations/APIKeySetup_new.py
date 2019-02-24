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


def login_window():

    app.startSubWindow('Login', title='Login Window')

    app.addLabel('IPv4 Address:', column=0, row=0)
    app.addEntry('IP1', column=1, row=0)
    app.addLabel('.', column=2, row=0)
    app.addEntry('IP1', column=3, row=0)
    app.addLabel('.', column=4, row=0)
    app.addEntry('IP1', column=5, row=0)
    app.addLabel('.', column=6, row=0)
    app.addEntry('IP1', column=7, row=0)
    app.addLabel(':', column=8, row=0)
    app.addLabelEntry('Port', column=9, row=0, label='Port')
    app.addLabel('API Key:', column=0, row=1)
    app.addEntry('API Key', column=1, row=1)


app = gui('Mirrulations')

app.go()
