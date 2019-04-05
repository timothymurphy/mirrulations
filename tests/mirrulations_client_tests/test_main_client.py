from mock import patch

from mirrulations_client.__main__ import main


@patch('mirrulations_client.__main__.os.path.exists', return_value=True)
def test_main_no_config_setup(ospe):
    with patch('mirrulations_client.__main__.parse_args',
               return_value={'config': False}) as pa, \
         patch('mirrulations_client.__main__.do_work') as dw:
        main()
        assert pa.called
        assert dw.called


@patch('mirrulations_client.__main__.os.path.exists', return_value=False)
def test_main_with_config_setup(ospe):
    with patch('mirrulations_client.__main__.parse_args',
               return_value={'config': True}) as pa, \
         patch('mirrulations_client.__main__.client_config_setup') as ccs, \
         patch('mirrulations_client.__main__.do_work') as dw:
        main()
        assert pa.called
        assert ccs.called
        assert dw.called
