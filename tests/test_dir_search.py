import pytest
import os
import dir_search as ds

PATH = os.getenv("HOME")+"/regulations_data/"


def test_search_document():
    full_path = ds.search_for_document("AHRQ_FRDOC_0001-0036")
    assert full_path == PATH + "AHRQ_FRDOC/AHRQ_FRDOC_0001/AHRQ_FRDOC_0001-0036"


def dtest_search_document_temp():
    PATHstr = "/test_files/regulations-data/"
    full_path = ds.search_for_document_temp("AHRQ_FRDOC_0001-0036", PATHstr)
    assert full_path == PATHstr
