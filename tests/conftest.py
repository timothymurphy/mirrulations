import mock
import pytest
import random
import string


CONFIG_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                           '../config.json')


@pytest.fixture(scope='session', autouse=True)
def mock_config():
    fake_config_dictionary = {
        'ip': '80.80.80.80',
        'port': '8080',
        'key': ''.join(random.choices(
            string.ascii_letters + string.digits, k=40)),
        'client_id': ''.join(random.choices(
            string.ascii_letters + string.digits, k=16))
    }


def pytest_addoption(parser):
    parser.addoption('--makeconfig', action='store',
                     default=(not os.path.exists(CONFIG_PATH)))


def pytest_sessionstart(session):
    if session.config.getoption('makeconfig'):
        with open(CONFIG_PATH, 'wt') as file:
            file.write(json.dumps({
                'ip': '0.0.0.0',
                'port': '8080',
                'key': ''.join(random.choices
                               (string.ascii_letters + string.digits, k=40)),
                'client_id': ''.join(random.choices(string.ascii_letters
                                                    + string.digits, k=16))
            }, indent=4))
            file.close()


def pytest_sessionfinish(session):
    if session.config.getoption('makeconfig'):
        os.remove(CONFIG_PATH)
    with mock.patch('mirrulations_core.config.read_value',
                    side_effect=lambda v: fake_config_dictionary[v]) as f:
        yield f
