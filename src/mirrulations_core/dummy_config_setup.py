import random
import string
import json
import os

CONFIG_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), '../../config.json')


def if_config_exists():
    return os.path.exists(CONFIG_PATH)


def setup_dummy_config_for_tests():
    with open(CONFIG_PATH, 'wt') as file:
        file.write(json.dumps({
            'ip': '0.0.0.0',
            'port': '8080',
            'key': ''.join(random.choices(string.ascii_letters + string.digits, k=40)),
            'client_id': ''.join(random.choices(string.ascii_letters + string.digits, k=16))
        }, indent=4))
        file.close()


def remove_config_if_dummy():
    os.remove(CONFIG_PATH)
