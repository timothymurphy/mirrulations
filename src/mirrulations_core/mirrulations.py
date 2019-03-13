import os
import sys
import mirrulations.client as client
import mirrulations.docs_work_gen as server
import mirrulations_core.config_setup as config_setup

CONFIG_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), '../config.json')


def main():
    args = sys.argv[1:]

    is_server = '--server' in args or '-s' in args
    setup_config = '--config' in args or '-c' in args or not os.path.exists(CONFIG_PATH)
    use_terminal = '--terminal' in args or '-t' in args

    if setup_config:
        getattr(config_setup, 'terminal_' if use_terminal else 'gui_' + 'server_' if is_server else 'client_' + 'setup')

    if is_server:
        server.monolith()
    else:
        client.do_work()


if __name__ == '__main__':
    main()
