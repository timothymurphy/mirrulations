import os
from mirrulations import dir_search as ds

PATH = os.getenv("HOME")+"/regulations_data/"
TEMPATH = os.getenv("HOME")+"/mirrulations/tests/test_files/regulations-data/"


def test_search_document():
    "This test requires the regulations-data directory structure on the testing machine"
    full_path = ds.search_for_document("AHRQ_FRDOC_0001-0036")
    assert full_path == PATH + "AHRQ_FRDOC/AHRQ_FRDOC_0001/AHRQ_FRDOC_0001-0036"


def test_search_document_test_directory_good_document():
    full_path = ds.search_for_document_test_directory("CMS-2019-0006-10896", TEMPATH)
    assert full_path == TEMPATH + "CMS/CMS-2019-0006/CMS-2019-0006-10896"


def test_search_document_test_directory_good_document_special_case():
    full_path = ds.search_for_document_test_directory("AHRQ_FRDOC_0001-0036", TEMPATH)
    assert full_path == TEMPATH + "AHRQ_FRDOC/AHRQ_FRDOC_0001/AHRQ_FRDOC_0001-0036"


def test_search_document_test_directory_good_document_orgs_out_of_order():
    full_path = ds.search_for_document_test_directory("USC-RULES-CV-2018-0003-1139", TEMPATH)
    assert full_path == TEMPATH + "CV-RULES-USC/USC-RULES-CV-2018-0003/USC-RULES-CV-2018-0003-1139"


def test_search_document_test_directory_bad_document():
    full_path = ds.search_for_document_test_directory("CMS-2019-0006-10898", TEMPATH)
    assert full_path == ""


def test_search_document_test_directory_bad_document_special_case():
    full_path = ds.search_for_document_test_directory("AHRQ_FRDOC_0001-0037", TEMPATH)
    assert full_path == ""


def test_search_document_test_directory_bad_document_orgs_out_of_order():
    full_path = ds.search_for_document_test_directory("USC-RULES-CV-2018-0003-1130", TEMPATH)
    assert full_path == ""