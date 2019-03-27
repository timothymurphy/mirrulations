import argparse


def main():

    parser = argparse.ArgumentParser(prog='mirrulations')
    parser.add_argument('enum', help='client, server, web')
    parser.add_argument('-c', '--config', action='store_true', help='force config setup')
    args = vars(parser.parse_args())

    enum = args['enum']
    do_config_setup = args['config']

    if enum == 'client':
        from mirrulations_client.__main__ import main
        from mirrulations_core.config import client_config_setup as config_setup
    elif enum == 'server':
        from mirrulations_server.__main__ import main
        from mirrulations_core.config import server_config_setup as config_setup
    elif enum == 'web':
        from mirrulations_web.__main__ import main
        from mirrulations_core.config import web_config_setup as config_setup
    else:
        print('Invalid command!\n'
              'Choose from client, server, or web!')
        exit(1)

    if do_config_setup:
        config_setup()
    else:
        from mirrulations_core.config import check_config
        if not check_config(enum.upper()):
            print('Config is not set up correctly!\n'
                  'Run with --config tag!')
            exit(2)

    main()


if __name__ == '__main__':
    main()
