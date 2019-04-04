from mock import patch

from mirrulations_web.__main__ import main


def test_main_no_config_setup():
    main(False)
    assert True


def test_main_with_config_setup():
    with patch('mirrulations_web.__main__.web_config_setup') as wcs:
        main(True)
        assert wcs.called
