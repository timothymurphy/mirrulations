import pytest
import requests_mock
from mock import *
from mirrulations_core.api_call_management import *


@pytest.fixture
def mock_req():
    with requests_mock.Mocker() as m:
        yield m


def set_time():
    mock_time = Mock()
    mock_time.return_value = None
    return mock_time


def test_happy_path(mock_req):
    mock_req.get(get_documents_url(), status_code=200, text='{}')
    assert send_call(get_documents_url()).text == '{}'


def test_exception_thrown(mock_req):
    mock_req.get(get_documents_url(),status_code=300)
    with pytest.raises(TemporaryException):
        send_call(get_documents_url())


def test_api_count_zero(mock_req):
        mock_req.get(get_documents_url(), status_code=429)
        with pytest.raises(ApiCountZeroException):
            send_call(get_documents_url())


def test_api_permanent_exception(mock_req):
        mock_req.get(get_documents_url(), status_code=404)
        with pytest.raises(PermanentException):
            send_call(get_documents_url())


def test_invalid_key_gives_permanent_exception(mock_req):
        mock_req.get(get_documents_url(), status_code=403)
        with pytest.raises(PermanentException):
            send_call(get_documents_url())


def test_generic_500_failure(mock_req):
    mock_req.get(get_documents_url(), status_code=500)
    with pytest.raises(PermanentException):
        send_call(get_documents_url())


def test_success(mock_req):
    mock_req.get(get_documents_url(), status_code=200, text='{}')
    assert api_call(get_documents_url()).text == '{}'


@patch('time.sleep', set_time())
def test_retry_calls_failure(mock_req):
    mock_req.get(get_documents_url(), status_code=304)
    with pytest.raises(CallFailException):
        api_call(get_documents_url())


def test_callfailexception(mock_req):
    mock_req.get(get_documents_url(), status_code=403)
    with pytest.raises(CallFailException):
        api_call(get_documents_url())


@patch('time.sleep', set_time())
def test_user_out_of_api_calls_sleeps(mock_req):
    mock_req.register_uri('GET',
                          get_documents_url(),
                          [{'text': 'resp1', 'status_code': 429},{'text': '{}', 'status_code': 200}])
    assert api_call(get_documents_url()).text == '{}'



