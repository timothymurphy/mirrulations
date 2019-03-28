from ast import literal_eval
import fakeredis
import mock
import os
import pytest
import requests_mock

from mirrulations_core import VERSION
from mirrulations_server.redis_manager import reset_lock, set_lock

from mirrulations_server.flask_manager import *

PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), '../test_files/mirrulations_files/filename.txt')



@pytest.fixture
def mock_req():
    with requests_mock.Mocker() as m:
        yield m


@pytest.fixture
def client():
    FLASK_APP.config['TESTING'] = True
    client = FLASK_APP.test_client()
    yield client


def make_json():
    return {'job_id': 1,
            'client_id': 2,
            'data': [[{'id': 1, 'attachment_count': 1}], [{'id': 2, 'attachment_count': 2}]],
            'version': VERSION}


def mock_init(self):
    self.r = fakeredis.FakeRedis()
    reset_lock(self.r)
    self.lock = set_lock(self.r)


def make_database():
    with mock.patch.object(RedisManager, '__init__', mock_init):
        r = RedisManager()
        r.r.flushall()
        test_list = json.dumps(['a', ['b', 'c']])
        r.r.lpush('queue', test_list)
        return r.r


def test_general():
    return True


def test_default_path(client):
    result = client.get('/')
    assert result.status_code == 200


def test_non_existent_endpoint(client):
    result = client.get('/not_existent')
    assert result.status_code == 404


def test_get_work_success(client):
    with mock.patch.object(RedisManager, '__init__', mock_init):
        result = client.get('/get_work', query_string={'client_id': '1'})
        assert result.status_code == 200


def test_get_work_throws_exception_if_no_client_id(client):
    result = client.get('/get_work')
    assert result.status_code == 400


def test_get_work_wrong_parameter(client):
    result = client.get('/get_work', query_string={'clientid': '1'})
    assert result.status_code == 400


def test_get_queue_item(client):
    r = make_database()
    lst = literal_eval(r.lpop('queue').decode('utf-8'))
    assert lst == ['a', ['b', 'c']]


def test_return_docs_call_success(client):
    with mock.patch.object(RedisManager, '__init__', mock_init):
        result = client.post('/return_docs', data={'file': open(PATH, 'rb'), 'json': json.dumps(make_json())})
        assert result.status_code == 200


def test_return_docs_no_parameter(client):
    result = client.post('/return_docs')
    assert result.status_code == 400


def test_return_doc_call_success(client):
    with mock.patch.object(RedisManager, '__init__', mock_init):
        result = client.post('/return_doc', data={'file': open(PATH, 'rb'), 'json': json.dumps(make_json())})
        assert result.status_code == 200


def test_return_doc_no_file_parameter(client):
    result = client.post('/return_doc', data=dict(json_info=json.dumps(make_json())))
    assert result.status_code == 400


def test_return_doc_no_json_parameter(client):
    result = client.post('/return_doc', data=dict(file=open(PATH, 'rb')))
    assert result.status_code == 400
