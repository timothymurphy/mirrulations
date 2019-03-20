import json
import mirrulations.docs_filter as dsf
import os

PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), "../../tests/test_files/mirrulations_files/")
REGULATIONS_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), "../../tests/test_files/regulations-data/")


def generate_json_data(file_name):
    file = open(file_name, 'r')
    test_data = json.load(file)
    return test_data


# Empty Workfile Tests
def test_remove_empty_lists():
    test_data = generate_json_data(PATH + 'multiple_empty_workfiles.json')
    dsf.remove_empty_lists(test_data)
    assert test_data["data"] == []


def test_remove_empty_lists_save_others():
    test_data = generate_json_data(PATH + 'some_empty_workfiles.json')
    dsf.remove_empty_lists(test_data)
    assert test_data["data"] == [
        [{"id": "AHRQ_FRDOC_0001-0037", "count": 1}],
        [{"id": "AHRQ_FRDOC_0001-0038", "count": 1}]
    ]


def test_file_exists_local():
    path = REGULATIONS_PATH + "AHRQ_FRDOC/AHRQ_FRDOC_0001/AHRQ_FRDOC_0001-0036/doc.AHRQ_FRDOC_0001-0036.json"
    count = 0
    count, verdict = dsf.check_if_file_exists_locally(path, count)
    assert count == 0
    assert verdict is True


def test_file_doesnt_exists_local():
    path = REGULATIONS_PATH + "AHRQ_FRDOC/AHRQ_FRDOC_0001/AHRQ_FRDOC_0001-0037/doc.AHRQ_FRDOC_0001-0037.json"
    count = 0
    count, verdict = dsf.check_if_file_exists_locally(path, count)
    assert count == 1
    assert verdict is False


def test_check_document_exists_part_1():
    test_data = generate_json_data(PATH + '1_workfile_2_documents.json')
    test_data = dsf.check_document_exists(test_data, REGULATIONS_PATH)
    assert test_data['data'] == [[{'id': 'AHRQ_FRDOC_0001-0037', 'count': 1}]]


# Validation Tests
def test_file_checker_500_lines():
    test_data = generate_json_data(PATH + '500_lines.json')
    assert dsf.check_workfile_length(test_data) is True
    assert test_data["type"] == "docs"


def test_file_checker_1000_lines():
    test_data = generate_json_data(PATH + '1000_lines.json')
    assert dsf.check_workfile_length(test_data) is True
    assert test_data["type"] == "docs"


def test_file_checker_2_workfiles():
    test_data = generate_json_data(PATH + '2_workfiles.json')
    assert dsf.check_workfile_length(test_data) is True
    assert test_data["type"] == "docs"


def test_file_checker_1001_lines():
    test_data = generate_json_data(PATH + '1001_lines.json')
    assert dsf.check_workfile_length(test_data) is False
    assert test_data["type"] == "docs"


def test_file_checker_too_many_attachments():
    test_data = generate_json_data(PATH + 'too_many_attachments.json')
    assert dsf.check_workfile_length(test_data) is False
    assert test_data["type"] == "docs"


# Assimilation Tests
def test_create_job():
    test_data = generate_json_data(PATH + '500_lines.json')
    job_id = '1'
    job = json.loads(dsf.create_document_job(test_data['data'], job_id))
    assert job['job_id'] == '1'
    assert job['type'] == 'doc'
