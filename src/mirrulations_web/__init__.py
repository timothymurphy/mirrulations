from flask import Flask
import os

PATH = os.getenv('HOME') + '/regulations-data/'

FLASK_APP = Flask(__name__)
