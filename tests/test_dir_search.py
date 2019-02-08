import pytest
import os
import dir_search as ds


PATH = os.getenv("HOME")+"/regulations_data/"


def test_get_document_id_attributes():
    orgs,dockID,docID = ds.get_document_id_attributes('mesd-2018-234234-0001')
    assert orgs == "mesd"
    assert dockID == 'mesd-2018-234234'
    assert docID == 'mesd-2018-234234-0001'


def test_get_document_id_attributes_special():
    orgs,dockID,docID = ds.get_document_id_attributes('AHRQ_FRDOC_0001-0036')
    assert orgs == "AHRQ_FRDOC"
    assert dockID == 'AHRQ_FRDOC_0001'
    assert docID == 'AHRQ_FRDOC_0001-0036'


def test_bad_input():
    orgs, dockID, docID = ds.get_document_id_attributes('zgdfgsadg')
    assert orgs == ""
    assert dockID == ""
    assert docID == ""


def test_search_document(savefile_tempdir):
    full_path = ds.search_for_document("AHRQ_FRDOC_0001-0036")
    assert full_path == PATH + "AHRQ_FRDOC/AHRQ_FRDOC_0001/AHRQ_FRDOC_0001-0036"


def test_search_document_temp():
    PATHstr = savefile_tempdir + "/"
    orgs, dock_id, doc_id = ds.get_document_id_attributes("AHRQ_FRDOC_0001-0036")

    path = PATHstr + orgs + "/" + dock_id + "/" + doc_id
    os.makedirs(path)
    open(os.path.join(path + "/doc.AHRQ_FRDOC_0001-0036.json"))

    full_path = ds.search_for_document_temp("AHRQ_FRDOC_0001-0036", PATHstr)
    assert full_path == path
