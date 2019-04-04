# import argparse
# import os
#
# from mirrulations_client.__main__ import main as client_main
# from mirrulations_server.__main__ import main as server_main
# from mirrulations_web.__main__ import main as web_main
#
# CONFIG_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)),
#                                            '../../.config/config.json')
#
#
# def main():
#
#     parser = argparse.ArgumentParser(prog='mirrulations')
#     parser.add_argument('enum', help='client/server/web')
#     parser.add_argument('-c', '--config',
#                         action='store_true', help='force config setup')
#     args = vars(parser.parse_args())
#
#     enum = args['enum']
#     do_config_setup = args['config'] or not os.path.exists(CONFIG_PATH)
#
#     if enum == 'client':
#         client_main(do_config_setup)
#     elif enum == 'server':
#         server_main(do_config_setup)
#     elif enum == 'web':
#         web_main(do_config_setup)
#     else:
#         print('Wrong enum!\nRun with client/server/web!')
#         exit()
#
#
# if __name__ == '__main__':
#     main()

from mock import patch

from mirrulations_core.__main__ import main


@patch('mirrulations_core.__main__.parse_args', return_value=['client', False])
def test_client_main_no_config_setup(pa):
    with patch('mirrulations_core.__main__.client_main') as cm:
        main()
        assert cm.called
        cm.assert_called_with(False)


@patch('mirrulations_core.__main__.parse_args', return_value=['client', True])
def test_client_main_with_config_setup(pa):
    with patch('mirrulations_core.__main__.client_main') as cm:
        main()
        assert cm.called
        cm.assert_called_with(True)


@patch('mirrulations_core.__main__.parse_args', return_value=['server', False])
def test_client_main_no_config_setup(pa):
    with patch('mirrulations_core.__main__.server_main') as sm:
        main()
        assert sm.called
        sm.assert_called_with(False)


@patch('mirrulations_core.__main__.parse_args', return_value=['server', True])
def test_client_main_with_config_setup(pa):
    with patch('mirrulations_core.__main__.server_main') as sm:
        main()
        assert sm.called
        sm.assert_called_with(True)


@patch('mirrulations_core.__main__.parse_args', return_value=['web', False])
def test_client_main_no_config_setup(pa):
    with patch('mirrulations_core.__main__.web_main') as wm:
        main()
        assert wm.called
        wm.assert_called_with(False)


@patch('mirrulations_core.__main__.parse_args', return_value=['web', True])
def test_client_main_with_config_setup(pa):
    with patch('mirrulations_core.__main__.web_main') as wm:
        main()
        assert wm.called
        wm.assert_called_with(True)


@patch('mirrulations_core.__main__.parse_args', return_value=['wrong_enum', False])
def test_wrong_enum(pa):
    with patch('mirrulations_core.__main__.print') as p, \
         patch('mirrulations_core.__main__.exit') as e:
        main()
        assert p.called
        p.assert_called_with('Wrong enum!\nRun with client/server/web!')
        assert e.called
