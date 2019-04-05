from mock import patch

from mirrulations_server.__main__ import main


@patch('mirrulations_server.__main__.os.path.exists', return_value=True)
def test_main_no_config_setup(ospe):
    with patch('mirrulations_server.__main__.parse_args', return_value={'config': False}) as pa, \
         patch('mirrulations_server.__main__.os.system') as redis, \
         patch('mirrulations_server.__main__.run') as endpoints, \
         patch('mirrulations_server.__main__.monolith') as dwg, \
         patch('mirrulations_server.__main__.expire') as expire:
        main()
        assert pa.called
        assert redis.called
        assert endpoints.called
        assert dwg.called
        assert expire.called


@patch('mirrulations_server.__main__.os.path.exists', return_value=False)
def test_main_with_config_setup(ospe):
    with patch('mirrulations_server.__main__.parse_args', return_value={'config': False}) as pa, \
         patch('mirrulations_server.__main__.server_config_setup') as scs, \
         patch('mirrulations_server.__main__.os.system') as redis, \
         patch('mirrulations_server.__main__.run') as endpoints, \
         patch('mirrulations_server.__main__.monolith') as dwg, \
         patch('mirrulations_server.__main__.expire') as expire:
        main()
        assert pa.called
        assert scs.called
        assert redis.called
        assert endpoints.called
        assert dwg.called
        assert expire.called
