import mirrulations_core.dummy_config_setup as dummy_config_setup


def pytest_addoption(parser):
    parser.addoption('--makeconfig', action='store', default=False)


def pytest_sessionstart(session):
    print('HERE 2')
    if not dummy_config_setup.if_config_exists():
        setattr(session.config, '_makeconfig', True)
        dummy_config_setup.setup_dummy_config_for_tests()
        print('HERE 2.5')


def pytest_sessionfinish(session, exitstatus):
    print('HERE 3')
    if getattr(session.config, '_makeconfig', False):
        dummy_config_setup.remove_config_if_dummy()
        print('HERE 3.5')
