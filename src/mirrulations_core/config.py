import configparser
import os
import random
import requests
import string

from mirrulations_core import CONFIG_PATH


def check_config(section):

    if not os.path.exists(CONFIG_PATH):
        return False

    cfg = configparser.ConfigParser()
    cfg.read(CONFIG_PATH)
    for key in cfg[section]:
        if cfg[section][key] is '':
            return False
    return True


def make_config_if_missing():

    if not os.path.exists(CONFIG_PATH):
        cfg = configparser.ConfigParser()
        cfg['CLIENT'] = {'API_KEY': '',
                         'CLIENT_ID': '',
                         'SERVER_ADDRESS': ''}
        cfg['SERVER'] = {'API_KEY': ''}
        cfg['WEB'] = {}
        with open(CONFIG_PATH, 'w') as file:
            cfg.write(file)
            file.close()


def verify_key(key_input):

    try:
        with requests.get('http://api.data.gov/regulations/v3/documents.json?api_key=' + key_input) as r:
            if r.status_code == 403:
                print('Unable to connect!\n'
                      'We weren\'t able to connect to regulations.gov.\n'
                      'Please try again later.')
                exit(3)
            elif r.status_code > 299 and r.status_code != 429:
                print('Invalid API key!\n'
                      'Your API key is invalid.\n'
                      'Please visit\n'
                      'https://regulationsgov.github.io/developers/\n'
                      'for an API key.')
                exit(4)
            else:
                print('Success!\n'
                      'You are successfully logged in.')
                return None
    except requests.ConnectionError:
        print('Unable to connect!\n'
              'We weren\'t able to connect to regulations.gov.\n'
              'Please try again later.')
        exit(5)


def client_config_setup():

    make_config_if_missing()

    api_key = input('API Key:\n')
    verify_key(api_key)
    client_id = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    server_ip = input('Server IP:\n')
    server_port = input('Server Port:\n')

    cfg = configparser.ConfigParser()
    cfg.read(CONFIG_PATH)
    cfg['CLIENT'] = {'API_KEY': api_key,
                     'CLIENT_ID': client_id,
                     'SERVER_ADDRESS': server_ip + ':' + server_port}
    with open(CONFIG_PATH, 'w') as file:
        cfg.write(file)
        file.close()


def server_config_setup():

    make_config_if_missing()

    api_key = input('API Key:\n')
    verify_key(api_key)

    cfg = configparser.ConfigParser()
    cfg.read(CONFIG_PATH)
    cfg['SERVER'] = {'API_KEY': api_key}
    with open(CONFIG_PATH, 'w') as file:
        cfg.write(file)
        file.close()


def web_config_setup():

    make_config_if_missing()

    return None


def read_value(section, value):

    cfg = configparser.ConfigParser()
    cfg.read(CONFIG_PATH)
    return cfg[section][value]
