from mirrulations_client.client_manager import *
import pytest
import requests_mock

SERVER_URL = 'https://' + SERVER_ADDRESS
FAKE_URL = 'https://website.com/random?api_key=' + API_KEY


@pytest.fixture
def mock_req():
    with requests_mock.Mocker() as m:
        yield m


def test_get_work(mock_req):
    mock_req.get(SERVER_URL + "/get_work?client_id=" + str(CLIENT_ID), status_code=200, text='RANDOM')
    result = get_work()
    assert result.status_code == 200


def test_return_doc(mock_req):
    doc_id = 'OSHA-H117-2006-0947-0647'
    doc_url = api_manager.make_api_call_url('document', '&documentId=OSHA-H117-2006-0947-0647')
    mock_req.post(SERVER_URL + "/return_doc", status_code=200)
    mock_req.get(doc_url, status_code=200, text='{"id": "' + doc_id + '", "count": 4}')
    r = return_doc({'job_id': 'qwerty', 'data': [{'id': doc_id, 'count': 4}]})
    assert r.status_code == 200


def test_return_docs(mock_req):
    mock_req.post(SERVER_URL + "/return_docs", status_code=200)
    docs_po = 0
    docs_rpp = 2
    docs_url = api_manager.make_api_call_url('documents', '&po=' + str(docs_po) + '&rpp=' + str(docs_rpp))
    doc_id_a = 'CMS-2005-0001-0001'
    doc_ac_a = 4
    doc_id_b = 'CMS-2005-0001-0002'
    doc_ac_b = 999
    mock_req.get(docs_url, status_code=200, text='{"documents": [{"documentId": "' + doc_id_a + '", "attachmentCount": '
                                                 + str(doc_ac_a) + '},{"documentId": "' + doc_id_b
                                                 + '", "attachmentCount": ' + str(doc_ac_b) + '}]}')
    r = return_docs({'job_id': 'qwerty', 'data': [[0, 2]]})  # 'http://website.com/random']})
    assert r.status_code == 200
