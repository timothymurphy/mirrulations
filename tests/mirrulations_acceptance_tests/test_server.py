import pytest
from mirrulations_server.endpoints import app
from mirrulations_server.redis_manager import RedisManager
import json

@pytest.fixture
def client():
    app.config['TESTING'] = True
    yield app.test_client()


def test_root_gives_empty_json(client):
    result = client.get('/')
    assert b'{}' == result.data


def test_when_one_job_in_db_then_job_returned_by_get_work(client):
    rm = RedisManager()
    rm.add_to_queue(json.dumps({'job_id': "1234",'type': "docs",'data': ["Url1"],'version': "0.5"}))

    result = client.get('/get_work?client_id=asdf')

    assert b'{"job_id": "1234", "type": "docs", "data": ["Url1"], "version": "0.5"}' == result.data
    assert rm.does_job_exist_in_progress('1234')


