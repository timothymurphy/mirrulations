import os

CONFIG_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), '../../config.json')


def client():

    from mirrulations.client import do_work
    do_work()


def client_setup_config():

    from mirrulations_core.config_setup import gui_client_setup
    gui_client_setup(CONFIG_PATH)


def client_setup_config_terminal():

    from mirrulations_core.config_setup import terminal_client_setup
    terminal_client_setup(CONFIG_PATH)


def server():

    from mirrulations.docs_work_gen import monolith
    monolith()


def server_setup_config():

    from mirrulations_core.config_setup import gui_server_setup
    gui_server_setup(CONFIG_PATH)


def server_setup_config_terminal():

    from mirrulations_core.config_setup import terminal_server_setup
    terminal_server_setup(CONFIG_PATH)


if __name__ == '__main__':
    client()
