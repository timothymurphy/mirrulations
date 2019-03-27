from flask import Flask
import os

HOME_REGULATION_PATH = os.getenv('HOME') + '/regulations-data/'

FLASK_APP = Flask(__name__)
