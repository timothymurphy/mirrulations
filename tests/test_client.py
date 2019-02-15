from mirrulations.client import *
import pytest
import requests_mock
from mirrulations.api_call import add_api_key
from mirrulations.api_call_management import CallFailException
import mirrulations.config as config


serverurl = "http://" + config.read_value("ip") + ":" + config.read_value("port")
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
    url = serverurl+"/get_work?client_id=" + str(client_id)
    mock_req.get(url, status_code=200, text='RANDOM')
    result = get_work(str(client_id))
    assert result.status_code == 200



def test_return_docs(mock_req):
    mock_req.post(serverurl+"/return_docs", status_code=200)
    mock_req.get(add_api_key('http://website.com/random'), status_code=200, text='{"documents": \
                                                                                  [{"documentId": "CMS-2005-0001-0001", "attachmentCount": 4},\
                                                                                  {"documentId": "CMS-2005-0001-0002", "attachmentCount": 999}]}')
    r = return_docs({'job_id': 'qwerty', 'data': ['http://website.com/random']}, str(client_id))
    assert r.status_code == 200


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

    open(path.name + "/client.log", "w").write("test")
    open(path.name + "/documents_processor.log", "w").write("test")
    open(path.name + "/document_processor.log", "w").write("test")
    open(path.name + "/api_call.log", "w").write("test")
    open(path.name + "/api_call_management.log", "w").write("test")

    add_client_log_files(zip_path.name, path.name)

    assert open(zip_path.name + "/client.log", "r").read() == "test"
    assert open(zip_path.name + "/documents_processor.log", "r").read() == "test"
    assert open(zip_path.name + "/document_processor.log", "r").read() == "test"
    assert open(zip_path.name + "/api_call.log", "r").read() == "test"
    assert open(zip_path.name + "/api_call_management.log", "r").read() == "test"

    path.cleanup()
    zip_path.cleanup()

