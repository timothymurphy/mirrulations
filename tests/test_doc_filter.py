import pytest
import requests_mock
import tempfile
import os
import fakeredis
import mirrulations.doc_filter as df


PATH = 'tests/test_files/'


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
    org, docket, document = df.get_doc_attributes('mesd-2018-234234-0001')
    assert org == "mesd"
    assert docket == "mesd-2018-234234"
    assert document == "mesd-2018-234234-0001"


def test_get_doc_attributes_multiple_agencies():
    org, docket, document = df.get_doc_attributes('mesd-abcd-2018-234234-0001')
    assert org == "abcd-mesd"
    assert docket == "mesd-abcd-2018-234234"
    assert document == "mesd-abcd-2018-234234-0001"


def test_get_doc_attributes_special():
    org, docket, document = df.get_doc_attributes('AHRQ_FRDOC_0001-0001')
    assert org == "AHRQ_FRDOC"
    assert docket == "AHRQ_FRDOC_0001"
    assert document == "AHRQ_FRDOC_0001-0001"


def test_get_doc_attributes_other_special():
    org, docket, document = df.get_doc_attributes('FDA-2018-N-0073-0002')
    assert org == "FDA"
    assert docket == "FDA-2018-N-0073"
    assert document == "FDA-2018-N-0073-0002"


def test_bad_input():
    orgs, dockID, docID = df.get_doc_attributes('zgdfgsadg')
    assert orgs == ""
    assert dockID == ""
    assert docID == ""


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


def test_is_document_beginning_good():
    assert df.beginning_is_letter("AHRQ_FRDOC_0001-0036") is True


def test_is_document_beginning_bad():
    assert df.beginning_is_letter("9147_FRDOC_0001-0036") is False


# Saving Tests
def test_get_file_list(workfile_tempdir, savefile_tempdir):
    compressed_file = PATH + "Archive.zip"
    PATHstr = savefile_tempdir
    file_list = df.get_file_list(compressed_file, PATHstr + "/", '123')
    assert len(file_list[0]) == 4


def test_get_file_list_and_work(workfile_tempdir, savefile_tempdir):
    compressed_file = PATH + "Archive.zip"
    PATHstr = savefile_tempdir
    file_list = df.get_file_list(compressed_file, PATHstr + "/", '123')

    condition = True
    for file in file_list[0]:
        doc_id = df.get_document_id(file)
        org, docket_id, document_id = df.get_doc_attributes(doc_id)

        if file.startswith("doc.") and df.ending_is_number(document_id) and df.beginning_is_letter(document_id):
            pass
        else:
            condition = False
            break

    assert condition is True


def test_get_file_list_and_bad_work(savefile_tempdir):
    compressed_file = PATH + "Bad_Archive.zip"
    PATHstr = savefile_tempdir
    file_list = df.get_file_list(compressed_file, PATHstr + "/", '123')

    condition = True
    for file in file_list[0]:
        org, docket_id, document_id = df.get_doc_attributes(file)

        if file.startswith("doc.") and df.ending_is_number(document_id) and df.beginning_is_letter(document_id):
            pass
        else:
            condition = False

    assert condition is False


def test_get_file_list_and_more_bad_work(savefile_tempdir):
    compressed_file = PATH + "Bad_Middle_Archive.zip"
    PATHstr = savefile_tempdir
    file_list = df.get_file_list(compressed_file, PATHstr + "/", '123')

    condition = True
    for file in file_list[0]:
        org, docket_id, document_id = df.get_doc_attributes(file)

        if file.startswith("doc.") and df.ending_is_number(document_id) and df.beginning_is_letter(document_id):
            pass
        else:
            condition = False

    assert condition is False


def test_get_file_list_and_bad_number_work(savefile_tempdir):
    compressed_file = PATH + "Bad_Number_Archive.zip"
    PATHstr = savefile_tempdir
    file_list = df.get_file_list(compressed_file, PATHstr + "/", '123')

    condition = True
    for file in file_list[0]:
        org, docket_id, document_id = df.get_doc_attributes(file)

        if file.startswith("doc.") and df.ending_is_number(document_id) and df.beginning_is_letter(document_id):
            pass
        else:
            condition = False

    assert condition is False


def test_local_save(workfile_tempdir, savefile_tempdir):
    filename = "doc.FMCSA-1997-2350-21654.json"
    path = workfile_tempdir + '/' + filename
    with open(path, 'w') as f:
        f.write("Stuff was written here")
    org, docket_id, document_id = df.get_doc_attributes(filename)
    df.local_save(path, savefile_tempdir + '/')
    assert os.path.exists(savefile_tempdir + '/' + org + '/' + docket_id + '/' + document_id + '/' + filename)
