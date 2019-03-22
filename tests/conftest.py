import configparser
import random
import string
import os

CONFIG_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), '../.config/config.ini')
MOVED_CONFIG_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), '../.config/moved_config.ini')


def pytest_addoption(parser):
    parser.addoption('--makeconfig', action='store', default=True)


def pytest_sessionstart(session):
    if session.config.getoption('makeconfig'):

        if os.path.exists(CONFIG_PATH):
            os.rename(CONFIG_PATH, MOVED_CONFIG_PATH)

        cfg = configparser.ConfigParser()
        cfg['CLIENT'] = {'API_KEY': ''.join(random.choices(string.ascii_letters + string.digits, k=40)),
                         'CLIENT_ID': ''.join(random.choices(string.ascii_letters + string.digits, k=16)),
                         'SERVER_ADDRESS': '0.0.0.0:0'}
        cfg['SERVER'] = {'API_KEY': ''.join(random.choices(string.ascii_letters + string.digits, k=40))}
        cfg['WEB'] = {}

        with open(CONFIG_PATH, 'w') as file:
            cfg.write(file)
            file.close()


def pytest_sessionfinish(session):
    if session.config.getoption('makeconfig'):
        os.remove(CONFIG_PATH)
        if os.path.exists(MOVED_CONFIG_PATH):
            os.rename(MOVED_CONFIG_PATH, CONFIG_PATH)
