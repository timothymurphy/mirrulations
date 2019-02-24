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

app = gui("Mirrulations")

app.go()