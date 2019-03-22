from mirrulations_client.document_processor import *
import pytest
import requests_mock
import os
import mirrulations_core.config as config

key = config.read_value('CLIENT', 'API_KEY')


@pytest.fixture
def mock_req():
    with requests_mock.Mocker() as m:
        yield m


@pytest.fixture()
def workfile_tempdir():
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield tmpdirname


# def test_collect_extra_documents(mock_req, workfile_tempdir):
#     generic_url = get_document_url('DOCUMENT')
#     document_id = 'OSHA-H117-2006-0947-0647'
#     document_url = get_document_url(document_id, attachment_number=1, content_type='pdf')
#
#     mock_req.get(generic_url, status_code=200, text='{"fileFormats":["' + document_url + '"]}')
#     mock_req.get(document_url)
#     result = get_extra_documents(api_call(generic_url), workfile_tempdir, document_id)
#
#     assert result == 1
#
#
# def test_collect_attachments(mock_req, workfile_tempdir):
#     generic_url = get_document_url('DOCUMENT')
#     document_id = 'FDA-2015-N-0540-0004'
#     document_url_msw12 = get_document_url(document_id, attachment_number=1, content_type='msw12')
#     document_url_pdf = get_document_url(document_id, attachment_number=1, content_type='pdf')
#
#     mock_req.get(generic_url,
#                  status_code=200,
#                  text='{"attachments":[{"fileFormats":["' + document_url_msw12 + '","' + document_url_pdf + '"]}]}')
#     mock_req.get(document_url_msw12, status_code=200, text='Document!')
#     mock_req.get(document_url_pdf, status_code=200, text='Document!')
#
#     result = get_extra_documents(api_call(generic_url), workfile_tempdir, document_id)
#
#     assert result == 1


def test_save_document(workfile_tempdir):
    result = "This is another test"
    document_id = "0000-0000-0067"
    save_document(workfile_tempdir, result, document_id)
    with open(workfile_tempdir + "/doc." + document_id + ".json", 'r') as f:
        assert f.readline().strip() == '"This is another test"'


# def test_download_document(workfile_tempdir, mock_req):
#     document_id = 'FDA-2015-N-0540-0004'
#     document_type = 'msw12'
#     document_url = get_document_url('FDA-2015-N-0540-0004', attachment_number=1, content_type=document_type)
#     mock_req.get(document_url, status_code=200, reason='')
#     result = api_call(document_url)
#     download_document(workfile_tempdir, document_id, result, document_type)
#     assert os.path.exists(workfile_tempdir + '/doc.' + document_id + '.doc')







