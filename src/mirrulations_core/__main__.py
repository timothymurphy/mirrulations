import argparse
from configparser import ConfigParser
import os
import random
import requests
import string

CONFIG_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), '../../.config/config.ini')

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


def config_setup(is_server):

    if is_server:
        ip = port = 'N/A'
    else:
        ip = input('IP:\n')
        port = input('Port:\n')

    key = input('API Key:\n')
    client_id = ''.join(random.choices(string.ascii_letters + string.digits, k=16))

    try:
        r = requests.get('https://api.data.gov/regulations/v3/documents.json?api_key=' + key)
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

        config = ConfigParser()
        config['CONFIG'] = {'ip': ip,
                            'port': port,
                            'key': key,
                            'client id': client_id}

        with open(CONFIG_PATH, 'wt') as file:
            config.write(file)
            file.close()
            print(successful_login_string)


def main():

    parser = argparse.ArgumentParser(prog='mirrulations')
    parser.add_argument('-s', '--server', action='store_true', help='run as server')
    parser.add_argument('-c', '--config', action='store_true', help='force config setup')
    args = vars(parser.parse_args())

    is_server = args['server']
    do_config_setup = args['config'] or not os.path.exists(CONFIG_PATH)

    if do_config_setup:
        config_setup(is_server)

    if is_server:
        from threading import Thread

        def run_redis():
            os.system('redis-server')

        def run_server():
            from mirrulations_server.endpoints import run
            run()

        def run_work():
            from mirrulations_server.docs_work_gen import monolith
            from mirrulations_server.expire import expire
            monolith()
            expire()

        Thread(target=run_redis).start()
        Thread(target=run_server).start()
        Thread(target=run_work).start()
    else:
        from mirrulations_client.client import do_work
        do_work()


if __name__ == '__main__':
    main()
