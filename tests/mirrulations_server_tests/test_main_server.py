from mock import patch

from mirrulations_server.__main__ import main


def test_main_no_config_setup():
    with patch('mirrulations_server.__main__.os.system') as redis, \
         patch('mirrulations_server.__main__.run') as endpoints, \
         patch('mirrulations_server.__main__.monolith') as dwg, \
         patch('mirrulations_server.__main__.expire') as expire:
        main(False)
        assert redis.called
        assert endpoints.called
        assert dwg.called
        assert expire.called


def test_main_with_config_setup():
    with patch('mirrulations_server.__main__.server_config_setup') as scs, \
         patch('mirrulations_server.__main__.os.system') as redis, \
         patch('mirrulations_server.__main__.run') as endpoints, \
         patch('mirrulations_server.__main__.monolith') as dwg, \
         patch('mirrulations_server.__main__.expire') as expire:
        main(True)
        assert scs.called
        assert redis.called
        assert endpoints.called
        assert dwg.called
        assert expire.called
