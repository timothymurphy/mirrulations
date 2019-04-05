import argparse
import os

from mirrulations_core.config import client_config_setup

from mirrulations_client.client import do_work

CONFIG_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                           '../../.config/config.json')


def parse_args():
    parser = argparse.ArgumentParser(prog='mirrulations_client')
    parser.add_argument('-c', '--config',
                        action='store_true',
                        help='force config setup')
    return vars(parser.parse_args())


def main():
    args = parse_args()
    if args['config'] or not os.path.exists(CONFIG_PATH):
        client_config_setup()

    do_work()
