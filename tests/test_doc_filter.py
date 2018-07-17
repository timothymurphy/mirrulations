import pytest
import requests_mock
import tempfile
import os
import fakeredis
import doc_filter as df


PATH = 'test_files/'


def setUp():
    # Setup fake redis for testing.
    return fakeredis.FakeStrictRedis()

@pytest.fixture
def mock_req():
    with requests_mock.Mocker() as m:
        yield m


@pytest.fixture()
def workfile_tempdir():
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield tmpdirname


@pytest.fixture()
def savefile_tempdir():
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield tmpdirname


# General Tests
def test_get_document_id():
    assert df.get_document_id('doc.mesd-2018-234234-0001.json') == "mesd-2018-234234-0001"


def test_get_document_id_special():
    assert df.get_document_id('doc.AHRQ_FRDOC_0001-0036.json') == "AHRQ_FRDOC_0001-0036"


def test_get_document_id_other_special():
    assert df.get_document_id('doc.FDA-2018-N-0073-0002.json') == "FDA-2018-N-0073-0002"


def test_get_file_name():
    assert df.get_file_name(PATH + 'doc.mesd-2018-234234-0001.json') == "doc.mesd-2018-234234-0001.json"


def test_get_doc_attributes():
    org, docket, document = df.get_doc_attributes('doc.mesd-2018-234234-0001.json')
    assert org == "mesd"
    assert docket == "mesd-2018-234234"
    assert document == "mesd-2018-234234-0001"


def test_get_doc_attributes_multiple_agencies():
    org, docket, document = df.get_doc_attributes('doc.mesd-abcd-2018-234234-0001.json')
    assert org == "abcd-mesd"
    assert docket == "mesd-abcd-2018-234234"
    assert document == "mesd-abcd-2018-234234-0001"


def test_get_doc_attributes_special():
    org, docket, document = df.get_doc_attributes('doc.AHRQ_FRDOC_0001-0001.json')
    assert org == "AHRQ_FRDOC"
    assert docket == "AHRQ_FRDOC_0001"
    assert document == "AHRQ_FRDOC_0001-0001"


def test_get_doc_attributes_other_special():
    org, docket, document = df.get_doc_attributes('doc.FDA-2018-N-0073-0002.json')
    assert org == "FDA"
    assert docket == "FDA-2018-N-0073"
    assert document == "FDA-2018-N-0073-0002"


# Validation Tests
def test_is_document_ending_a_number():
    assert df.ending_is_number("FDA-2018-N-0073-0002") is True


def test_is_document_ending_a_number_special():
    assert df.ending_is_number("AHRQ_FRDOC_0001-0036") is True


def test_is_document_ending_a_word():
    assert df.ending_is_number("FDA-2018-N-0073-Abcd") is False


def test_is_document_ending_a_word_special():
    assert df.ending_is_number("AHRQ_FRDOC_0001-WXyz") is False


def test_id_matches_good():
    assert df.id_matches(PATH + "doc.FMCSA-1997-2350-21654.json", "FMCSA-1997-2350-21654") is True


def test_id_matches_bad():
    assert df.id_matches(PATH + "doc.FMCSA-1997-2350-21653.json", "FMCSA-1997-2350-21653") is False


# Assimilation Tests
def test_local_save(workfile_tempdir, savefile_tempdir):
    filename = "doc.FMCSA-1997-2350-21654.json"
    path = workfile_tempdir + '/' + filename
    with open(path, 'w') as f:
        f.write("Stuff was written here")
    org, docket_id, document_id = df.get_doc_attributes(filename)
    df.local_save(path, savefile_tempdir + '/')
    assert os.path.exists(savefile_tempdir + '/' + org + '/' + docket_id + '/' + document_id + '/' + filename)
