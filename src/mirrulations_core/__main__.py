import argparse
import os

from mirrulations_client.__main__ import main as client_main
from mirrulations_server.__main__ import main as server_main
from mirrulations_web.__main__ import main as web_main

CONFIG_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                           '../../.config/config.json')


def parse_args():
    parser = argparse.ArgumentParser(prog='mirrulations')
    parser.add_argument('enum', help='client/server/web')
    parser.add_argument('-c', '--config',
                        action='store_true',
                        help='force config setup')
    args = vars(parser.parse_args())
    enum = args['enum']
    do_config_setup = args['config'] or os.path.exists(CONFIG_PATH)
    return enum, do_config_setup


def main():
    enum, do_config_setup = parse_args()

    if enum == 'client':
        client_main(do_config_setup)
    elif enum == 'server':
        server_main(do_config_setup)
    elif enum == 'web':
        web_main(do_config_setup)
    else:
        print('Wrong enum!\nRun with client/server/web!')
        exit()


if __name__ == '__main__':
    main()
