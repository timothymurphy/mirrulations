import argparse
import os

CONFIG_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), '../../.config/config.json')


def main():

    parser = argparse.ArgumentParser(prog='mirrulations')
    parser.add_argument('enum', help='client/server/web')
    parser.add_argument('-c', '--config', action='store_true', help='force config setup')
    args = vars(parser.parse_args())

    enum = args['enum']
    do_config_setup = args['config'] or not os.path.exists(CONFIG_PATH)

    if enum == 'client':
        from mirrulations_client.__main__ import main
    elif enum == 'server':
        from mirrulations_server.__main__ import main
    elif enum == 'web':
        from mirrulations_web.__main__ import main
    else:
        print('Wrong enum!\nRun with client/server/web!')
        exit()

    main(do_config_setup)


if __name__ == '__main__':
    main()
