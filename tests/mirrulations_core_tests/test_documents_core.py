import pytest
import mirrulations_core.documents_core as dc


def test_get_doc_attributes():
    org, docket, document = dc.get_doc_attributes('mesd-2018-234234-0001')
    assert org == "mesd"
    assert docket == "mesd-2018-234234"
    assert document == "mesd-2018-234234-0001"


def test_get_doc_attributes_multiple_agencies():
    org, docket, document = dc.get_doc_attributes('mesd-abcd-2018-234234-0001')
    assert org == "abcd-mesd"
    assert docket == "mesd-abcd-2018-234234"
    assert document == "mesd-abcd-2018-234234-0001"


def test_get_doc_attributes_special():
    org, docket, document = dc.get_doc_attributes('AHRQ_FRDOC_0001-0001')
    assert org == "AHRQ_FRDOC"
    assert docket == "AHRQ_FRDOC_0001"
    assert document == "AHRQ_FRDOC_0001-0001"


def test_get_doc_attributes_other_special():
    org, docket, document = dc.get_doc_attributes('FDA-2018-N-0073-0002')
    assert org == "FDA"
    assert docket == "FDA-2018-N-0073"
    assert document == "FDA-2018-N-0073-0002"
