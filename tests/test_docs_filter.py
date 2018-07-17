import pytest
import requests_mock
import tempfile
import os
import re

import docs_filter as dsf

PATH = 'test_files/'

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


# Validation Tests
def test_file_checker_500_lines():
    assert dsf.file_length_checker(PATH + '500_lines.json') is True


def test_file_checker_1000_lines():
    assert dsf.file_length_checker(PATH + '1000_lines.json') is True


def test_file_checker_2_workfiles():
    assert dsf.file_length_checker(PATH + '2_workfiles.json') is True


def test_file_checker_1001_lines():
    assert dsf.file_length_checker(PATH + '1001_lines.json') is False


def test_file_checker_too_many_attachments():
    assert dsf.file_length_checker(PATH + 'too_many_attachments.json') is False


def dtest_documents_checker_is_documents():
    assert dsf.documents_checker(PATH + '500_lines.json') is True


# Assimilation Tests


