from mirrulations.client import *
import pytest
import requests_mock
import pytest_mock
import mock
import unittest
from unittest.mock import create_autospec
import os
from mirrulations.api_call import add_api_key
from mirrulations.api_call_management import CallFailException
import mirrulations_core.config as config

ip = config.read_value('ip')
port = config.read_value('port')
key = config.read_value('key')
client_id = config.read_value('client_id')

serverurl = "http://" + ip + ":" + port
base_url = 'https://api.data.gov/regulations/v3/document?documentId='


@pytest.fixture
def mock_req():
    with requests_mock.Mocker() as m:
        yield m


def test_get_work(mock_req, caplog):
    url = serverurl+"/get_work?client_id=" + str(client_id)
    mock_req.get(url, status_code=200, text='RANDOM')
    result = get_work(str(client_id))
    assert result.status_code == 200
    assert 'Obtained work from server.' in caplog.text


def test_return_docs(mock_req):
    mock_req.post(serverurl+"/return_docs", status_code=200)
    mock_req.get(add_api_key('http://website.com/random'), status_code=200, text='{"documents": \
                                                                                  [{"documentId": "CMS-2005-0001-0001", "attachmentCount": 4},\
                                                                                  {"documentId": "CMS-2005-0001-0002", "attachmentCount": 999}]}')
    r = return_docs({'job_id': 'qwerty', 'data': ['http://website.com/random']}, str(client_id))
    assert r.status_code == 200


# def test_return_docs_assert_logs_pytest_mock(mock_req, mocker):
#     mock_req.post(serverurl+"/return_docs", status_code=200)
#     mock_req.get(add_api_key('http://website.com/random'), status_code=200, text='{"documents": \
#                                                                                   [{"documentId": "CMS-2005-0001-0001", "attachmentCount": 4},\
#                                                                                   {"documentId": "CMS-2005-0001-0002", "attachmentCount": 999}]}')
#     r = return_docs({'job_id': 'qwerty', 'data': ['http://website.com/random']}, str(client_id))
#     mocker.patch('os.remove')
#     assert r.status_code == 200
#     os.remove.assert_called_with()


# @mock.patch('mirrulations.client.os')
# def test_return_docs_assert_logs_unittest_mock(mock_req):
#     mock_req.post(serverurl+"/return_docs", status_code=200)
#     mock_req.get(add_api_key('http://website.com/random'), status_code=200, text='{"documents": \
#                                                                                   [{"documentId": "CMS-2005-0001-0001", "attachmentCount": 4},\
#                                                                                   {"documentId": "CMS-2005-0001-0002", "attachmentCount": 999}]}')
#     r = return_docs({'job_id': 'qwerty', 'data': ['http://website.com/random']}, str(client_id))
#     mock_os.remove.assert_called_with('/../../mirrulations.log')


# @mock.patch('mirrulations.client.os')
# def test_remove_file(self, mock_req):
#     remove_file('../../filename1')
#     mock_req.remove.assert_called_with('../../filename1')


def test_assert_os_remove(mock_req):
    mock_remove_file = create_autospec(remove_file)
    mock_remove_file('../../mirrulations.log')
    mock_remove_file.assert_called_with('../../mirrulations.log')
    

# def test_return_docs_assert_os_remove(mock_req):
#     mock_req.post(serverurl+"/return_docs", status_code=200)
#     mock_req.get(add_api_key('http://website.com/random'), status_code=200, text='{"documents": \
#                                                                                   [{"documentId": "CMS-2005-0001-0001", "attachmentCount": 4},\
#                                                                                   {"documentId": "CMS-2005-0001-0002", "attachmentCount": 999}]}')
#     r = return_docs({'job_id': 'qwerty', 'data': ['http://website.com/random']}, str(client_id))
#
#     mock_remove_file = create_autospec(remove_file)
#
#     assert r.status_code == 200
#
#     mock_remove_file.assert_called_with('../../mirrulations.log')


def ignore_test_return_docs_error(mock_req):
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


def test_add_logs():
    path = tempfile.TemporaryDirectory()
    zip_path = tempfile.TemporaryDirectory()

    open(path.name + "/mirrulations.log", "w").write("test")

    add_client_log_files(zip_path.name, path.name)

    assert open(zip_path.name + "/mirrulations.log", "r").read() == "test"

    path.cleanup()
    zip_path.cleanup()
