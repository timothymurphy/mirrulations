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


@patch('mirrulations_core.__main__.parse_args', return_value=['wrong', False])
def test_wrong_enum(pa):
    with patch('mirrulations_core.__main__.print') as p, \
         patch('mirrulations_core.__main__.exit') as e:
        main()
        assert p.called
        p.assert_called_with('Wrong enum!\nRun with client/server/web!')
        assert e.called
