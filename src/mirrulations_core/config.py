import json
import os
import random
import requests
import string

from mirrulations_core.mirrulations_logging import logger

CONFIG_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), '../../.config/config.json')

connection_error_string = 'Unable to connect!\n' \
                          'We weren\'t able to connect to regulations.gov.\n' \
                          'Please try again later.'
invalid_key_error_string = 'Invalid API key!\n' \
                           'Your API key is invalid.\n' \
                           'Please visit\n' \
                           'https://regulationsgov.github.io/developers/\n' \
                           'for an API key.'
successful_login_string = 'Success!\n' \
                          'You are successfully logged in.'


def read_value(value):
    """
    Reads a file from the configuration JSON file.
    :param value: Value to be read from the JSON
    :return: Value read from the JSON
    """
    try:
        contents = json.loads(open(CONFIG_PATH, "r").read())
        result = contents[value]
    except FileNotFoundError:
        logger.error('File Not Found Error')
        return None
    except IOError:
        logger.error('Input/Output Error')
        return None
    except json.JSONDecodeError:
        logger.error('JSON Decode Error')
        return None
    except KeyError:
        logger.error('Key Error')
        return None
    else:
        return result


def verify_api_key(api_key):
    try:
        r = requests.get('https://api.data.gov/regulations/v3/documents.json?api_key='
                         + api_key)
    except requests.ConnectionError:
        print(connection_error_string)
        exit()
    else:
        if r.status_code == 403:
            print(invalid_key_error_string)
            exit()
        elif r.status_code > 299 and r.status_code != 429:
            print(connection_error_string)
            exit()
        print(successful_login_string)


def client_config_setup():

    api_key = input('API Key:\n')
    verify_api_key(api_key)

    client_id = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    ip = input('IP:\n')
    port = input('Port:\n')

    with open(CONFIG_PATH, 'wt') as file:
        file.write(json.dumps({
            'api_key': api_key,
            'client_id': client_id,
            'ip': ip,
            'port': port
        }, indent=4))
        file.close()


def server_config_setup():

    api_key = input('API Key:\n')
    verify_api_key(api_key)

    with open(CONFIG_PATH, 'wt') as file:
        file.write(json.dumps({
            'api_key': api_key,
        }, indent=4))
        file.close()


def web_config_setup():
    pass
