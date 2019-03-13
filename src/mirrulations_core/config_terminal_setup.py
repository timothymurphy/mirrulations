import requests
import random
import string
import json
import os

''' 
 This program will prompt the user for their regulations.gov API Key, as well as the IP and port
 of the work server they want to connect to. It will set up the config.json file, store the user's
 API Key, and generate a random ClientID.
'''


def connection_error():
    print('Unable to connect!\n'
          'We weren\'t able to connect to regulations.gov.\n'
          'Please try again later.')


def invalid_key_error():
    print('Invalid API key!\n'
          'Your API key is invalid.\n'
          'Please visit\n'
          'https://regulationsgov.github.io/developers/\n'
          'for an API key.')


def successful_login(ip, port, key, client_id):
    with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), '../../config.json'), 'wt') as file:
        file.write(json.dumps({
            'ip': ip,
            'port': port,
            'key': key,
            'client_id': client_id
        }, indent=4))
        file.close()

    print('Success!\n'
          'You are successfully logged in!')


def main():

    ip = input('IP:\n')
    port = input('Port:')
    key = input('API Key')
    client_id = ''.join(random.choices(string.ascii_letters + string.digits, k=16))

    try:
        r = requests.get('https://api.data.gov/regulations/v3/documents.json?api_key=' + key)
    except requests.ConnectionError:
        connection_error()
    else:
        if r.status_code == 403:
            invalid_key_error()
        elif r.status_code > 299 and r.status_code != 429:
            connection_error()
        else:
            successful_login(ip, port, key, client_id)

    exit()


main()
