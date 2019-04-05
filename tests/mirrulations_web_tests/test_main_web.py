from mock import patch

from mirrulations_web.__main__ import main


@patch('mirrulations_web.__main__.os.path.exists', return_value=False)
def test_main_no_config_setup(ospe):
    with patch('mirrulations_web.__main__.parse_args', return_value={'config': False}) as pa:
        main()
        assert pa.called


@patch('mirrulations_web.__main__.os.path.exists', return_value=False)
def test_main_with_config_setup(ospe):
    with patch('mirrulations_web.__main__.parse_args', return_value={'config': False}) as pa, \
         patch('mirrulations_web.__main__.web_config_setup') as wcs:
        main()
        assert pa.called
        assert wcs.called
