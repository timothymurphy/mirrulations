import random
import string
import json
import os

CONFIG_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), '../../config.json')


def pytest_addoption(parser):
    parser.addoption('--makeconfig', action='store', default=False)


def pytest_sessionstart(session):
    if not os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'wt') as file:
            file.write(json.dumps({
                'ip': '0.0.0.0',
                'port': '8080',
                'key': ''.join(random.choices(string.ascii_letters + string.digits, k=40)),
                'client_id': ''.join(random.choices(string.ascii_letters + string.digits, k=16))
            }, indent=4))
            file.close()
        setattr(session.config, '_makeconfig', True)


def pytest_sessionfinish(session, exitstatus):
    if getattr(session.config, '_makeconfig', False):
        os.remove(CONFIG_PATH)
