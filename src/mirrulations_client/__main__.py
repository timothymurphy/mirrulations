from mirrulations_core.config import client_config_setup

from mirrulations_client.client import do_work


def main(do_config_setup):

    if do_config_setup:
        client_config_setup()

    do_work()
