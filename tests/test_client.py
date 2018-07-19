from client import *
import pytest
import requests_mock
from api_call import add_api_key
from api_call_management import CallFailException

server_url = "http://127.0.0.1:5000"
base_url = 'https://api.data.gov/regulations/v3/document?documentId='

home = os.getenv("HOME")
with open(home + '/.env/regulationskey.txt') as f:
    key = f.readline().strip()
    client_id = f.readline().strip()

@pytest.fixture
def mock_req():
    with requests_mock.Mocker() as m:
        yield m


def test_get_work(mock_req):
    url = "http://127.0.0.1:5000/get_work?client_id=" + str(client_id)
    mock_req.get(url, status_code=200, text='RANDOM')
    result = get_work(str(client_id))
    assert result.status_code == 200


def test_get_work(mock_req):
    url = "http://127.0.0.1:5000/get_work?client_id=" + str(client_id)
    mock_req.get(url, status_code=400, text='Error')
    with pytest.raises(CallFailException):
        assert get_work(str(client_id))


def test_return_docs(mock_req):
    mock_req.post(serverurl+"/return_docs", status_code=200)
    mock_req.get(add_api_key('http://website.com/random'), status_code=200, text='{"documents": \
                                                                                  [{"documentId": "CMS-2005-0001-0001", "attachmentCount": 4},\
                                                                                  {"documentId": "CMS-2005-0001-0002", "attachmentCount": 999}]}')
    r = return_docs({'job_id': 'qwerty', 'data': ['http://website.com/random']}, str(client_id))
    assert r.status_code == 200


def test_return_docs_error(mock_req):

    mock_req.get(add_api_key('http://website.com/random'), status_code=400, text='{"documents": \
                                                                                  [{"documentId": "CMS-2005-0001-0001", "attachmentCount": 4},\
                                                                                  {"documentId": "CMS-2005-0001-0002", "attachmentCount": 999}]}')
    with pytest.raises(CallFailException):
        r = return_docs({'job_id': 'qwerty', 'data': ['http://website.com/random']}, str(client_id))


def test_return_doc(mock_req):
    mock_req.post(serverurl + "/return_doc", status_code=200)
    mock_req.get(add_api_key('https://api.data.gov/regulations/v3/document?documentId=website-com'),
                 status_code=200, text='{ "something": '
                                       '["https://api.data.gov/regulations/v3/download?'
                                       'documentId=OSHA-H117-2006-0947-0647&'
                                       'attachmentNumber=1&contentType=pdf"] }')
    r = return_doc({'job_id': 'qwerty', 'data': [{'id':'website-com', 'count':4}]}, str(client_id))
    assert r.status_code == 200


def test_return_doc_error(mock_req):

    mock_req.get(add_api_key('https://api.data.gov/regulations/v3/document?documentId=website-com'), status_code=400, text='{ "something": '
                                                                    '["https://api.data.gov/regulations/v3/download?'
                                                                    'documentId=OSHA-H117-2006-0947-0647&'
                                                                    'attachmentNumber=1&contentType=pdf"] }')
    with pytest.raises(CallFailException):
        r = return_doc({'job_id': 'qwerty', 'data': [{'id':'website-com', 'count':4}]}, str(client_id))


