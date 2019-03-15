import argparse
import os

CONFIG_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), '../../config.json')


def main():

    parser = argparse.ArgumentParser(prog='mirrulations')
    parser.add_argument('-s', '--server', action='store_true', help='run as server')
    parser.add_argument('-c', '--config_setup', action='store_true', help='force config setup')
    parser.add_argument('-t', '--terminal', action='store_true', help='run without gui')
    args = vars(parser.parse_args())

    is_server = args['server']
    do_config_setup = args['config_setup'] or not os.path.exists(CONFIG_PATH)
    use_terminal = args['terminal']

    if do_config_setup:
        import mirrulations_core.config_setup as cs
        if use_terminal:
            cs.terminal_server_setup(CONFIG_PATH) if is_server else cs.terminal_client_setup(CONFIG_PATH)
        else:
            cs.gui_server_setup(CONFIG_PATH) if is_server else cs.gui_client_setup(CONFIG_PATH)

    if is_server:
        from threading import Thread
        from mirrulations.docs_work_gen import monolith
        from mirrulations.endpoints import run
        Thread(target=run).start()
        Thread(target=monolith).start()
    else:
        from mirrulations.client import do_work
        do_work()


if __name__ == '__main__':
    main()
