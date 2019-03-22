import configparser
import os
import random
import string

from mirrulations_core.api_call_management import verify_key

CONFIG_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), "../../.config/config.ini")


def check_config(section):

    if os.path.exists(CONFIG_PATH):
        return False

    with configparser.ConfigParser() as cfg:
        cfg.read(CONFIG_PATH)
        for key in cfg[section]:
            if cfg[section][key] is None:
                return False
        return True


def make_config_if_missing():

    if not os.path.exists(CONFIG_PATH):
        with configparser.ConfigParser() as cfg:
            cfg['CLIENT'] = {'API_KEY': None,
                             'CLIENT_ID': None,
                             'SERVER_ADDRESS': None}
            cfg['SERVER'] = {'API_KEY': None}
            cfg['WEB'] = {}
            with open(CONFIG_PATH, 'w') as file:
                file.write(cfg)
                file.close()


def client_config_setup():

    make_config_if_missing()

    api_key = input('API Key:\n')
    verify_key(api_key)
    client_id = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    server_ip = input('Server IP:\n')
    server_port = input('Server Port:\n')

    with configparser.ConfigParser() as cfg:
        cfg.read(CONFIG_PATH)
        cfg['CLIENT'] = {'API_KEY': api_key,
                         'CLIENT_ID': client_id,
                         'SERVER_ADDRESS': server_ip + ':' + server_port}
        with open(CONFIG_PATH, 'w') as file:
            file.write(cfg)
            file.close()


def server_config_setup():

    make_config_if_missing()

    api_key = input('API Key:\n')
    verify_key(api_key)

    with configparser.ConfigParser() as cfg:
        cfg.read(CONFIG_PATH)
        cfg['SERVER'] = {'API_KEY': api_key}
        with open(CONFIG_PATH, 'w') as file:
            file.write(cfg)
            file.close()


def web_config_setup():

    make_config_if_missing()

    return None


def read_value(section, value):

    with configparser.ConfigParser() as cfg:
        cfg.read(CONFIG_PATH)
        return cfg[section][value]
