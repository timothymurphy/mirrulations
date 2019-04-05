import argparse
import os

from mirrulations_core.config import web_config_setup

CONFIG_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                           '../../.config/config.json')


def parse_args():
    parser = argparse.ArgumentParser(prog='mirrulations_web')
    parser.add_argument('-c', '--config',
                        action='store_true',
                        help='force config setup')
    return vars(parser.parse_args())


def main():
    args = parse_args()
    if args['config'] or not os.path.exists(CONFIG_PATH):
        web_config_setup()
