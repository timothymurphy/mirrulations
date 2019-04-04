from mock import patch

from mirrulations_client.__main__ import main


def test_main_no_config_setup():
    with patch('mirrulations_client.__main__.do_work') as dw:
        main(False)
        assert dw.called


def test_main_with_config_setup():
    with patch('mirrulations_client.__main__.client_config_setup') as ccs, \
         patch('mirrulations_client.__main__.do_work') as dw:
        main(True)
        assert ccs.called
        assert dw.called
