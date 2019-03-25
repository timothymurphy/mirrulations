from mirrulations_client.documents_processor import *
import pytest
import requests_mock
import mirrulations_core.config as config
from mirrulations_core.api_call_manager import APICallManager

API_KEY = config.read_value('CLIENT', 'API_KEY')
CLIENT_ID = config.read_value('CLIENT', 'CLIENT_ID')
DOCS_URL = 'https://www.website.com/regulations/v3/documents.json?api_key=' + API_KEY

version = 'v1.3'


@pytest.fixture
def mock_req():
    with requests_mock.Mocker() as m:
        yield m


def test_documents_processor_basic():
    docs_info_list = []
    docs = documents_processor(APICallManager(API_KEY), docs_info_list, 'JobID', CLIENT_ID)
    assert docs == {'client_id': CLIENT_ID,
                    "type": "docs",
                    'data': [],
                    'job_id': 'JobID',
                    'version': version}


def test_make_docs_complex():
    test = make_docs([{"documentId": "QWERTYUIOP0", "attachmentCount": 998},
                      {"documentId": "QWERTYUIOP1", "attachmentCount": 9},
                      {"documentId": "QWERTYUIOP2", "attachmentCount": 8},
                      {"documentId": "QWERTYUIOP3", "attachmentCount": 7},
                      {"documentId": "QWERTYUIOP4", "attachmentCount": 6},
                      {"documentId": "QWERTYUIOP5", "attachmentCount": 5},
                      {"documentId": "QWERTYUIOP6", "attachmentCount": 4}])
    assert test == [[{"id": "QWERTYUIOP0", "count": 999}],
                    [{"id": "QWERTYUIOP1", "count": 10},
                     {"id": "QWERTYUIOP2", "count": 9},
                     {"id": "QWERTYUIOP3", "count": 8},
                     {"id": "QWERTYUIOP4", "count": 7},
                     {"id": "QWERTYUIOP5", "count": 6},
                     {"id": "QWERTYUIOP6", "count": 5}]]


def test_documents_processor_empty():
    docs_info_list = []
    docs = documents_processor(APICallManager(API_KEY), docs_info_list, 'JobID', CLIENT_ID)
    assert docs == {'client_id': CLIENT_ID,
                    'type': 'docs',
                    'data': [],
                    'job_id': 'JobID',
                    'version': version}


# def test_make_docs():
#
#     test = make_docs([{"documentId":"QWERTYUIOP1", "attachmentCount":9},
#                       {"documentId":"QWERTYUIOP2", "attachmentCount":8},
#                       {"documentId":"QWERTYUIOP3", "attachmentCount":7},
#                       {"documentId":"QWERTYUIOP4", "attachmentCount":6},
#                       {"documentId":"QWERTYUIOP5", "attachmentCount":5},
#                       {"documentId":"QWERTYUIOP6", "attachmentCount":4}])
#     assert test == [[{"id":"QWERTYUIOP1", "count":10},
#                      {"id":"QWERTYUIOP2", "count":9},
#                      {"id":"QWERTYUIOP3", "count":8},
#                      {"id":"QWERTYUIOP4", "count":7},
#                      {"id":"QWERTYUIOP5", "count":6},
#                      {"id":"QWERTYUIOP6", "count":5}]]
#
#
# def test_documents_processor(mock_req):
#     mock_req.get('https://thing',
#                  status_code=200,
#                  text='{"documents":[{"documentId": "CMS-2005-0001-0001", "attachmentCount": 4},\
#                                      {"documentId": "CMS-2005-0001-0002", "attachmentCount": 999}]}')
#     mock_req.get(fake_url,
#                  status_code=200,
#                  text='{"documents":[{"documentId": "CMS-2005-0001-0003", "attachmentCount": 88},\
#                                      {"documentId": "CMS-2005-0001-0004", "attachmentCount": 666}]}')
#     docs = documents_processor(APICallManager(key), ['https://thing', fake_url], 'Job ID', client_id)
#     assert docs == ({'job_id': 'Job ID',
#                      'type': 'docs',
#                      'data': [[{'id': 'CMS-2005-0001-0001', 'count': 5}],
#                               [{'id': 'CMS-2005-0001-0002', 'count': 1000}],
#                               [{'id': 'CMS-2005-0001-0003', 'count': 89}, {'id': 'CMS-2005-0001-0004', 'count': 667}]],
#                      'version': version,
#                      'client_id': str(client_id)})
#
#
# def test_valid_results():
#     result = process_results('{"documents":[{"documentId": "CMS-2005-0001-0001", "attachmentCount": 4},'
#                              '{"documentId": "CMS-2005-0001-0002", "attachmentCount": 999}]}')
#     assert result
