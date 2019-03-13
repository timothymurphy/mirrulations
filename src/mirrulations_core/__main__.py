import os
import sys

CONFIG_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), '../../config.json')


def main():

    args = sys.argv[1:]

    is_server = '--server' in args or '-s' in args
    setup_config = '--config' in args or '-c' in args or not os.path.exists(CONFIG_PATH)
    use_terminal = '--terminal' in args or '-t' in args

    if setup_config:
        import mirrulations_core.config_setup as config_setup
        if use_terminal:
            if is_server:
                config_setup.terminal_server_setup(CONFIG_PATH)
            else:
                config_setup.terminal_client_setup(CONFIG_PATH)
        else:
            if is_server:
                config_setup.gui_server_setup(CONFIG_PATH)
            else:
                config_setup.gui_client_setup(CONFIG_PATH)

    if is_server:
        import mirrulations.docs_work_gen as server
        server.monolith()
    else:
        import mirrulations.client as client
        client.do_work()


if __name__ == '__main__':
    main()
