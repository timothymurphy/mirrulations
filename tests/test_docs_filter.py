import pytest
import json
import mock
import docs_filter as dsf

PATH = 'test_files/'


def generate_json_data(file_name):
    file = open(file_name, 'r')
    test_data = json.load(file)
    return test_data


# Validation Tests
@mock.patch("docs_filter.RedisManager")
def test_file_checker_500_lines(redis):
    test_data = generate_json_data(PATH + '500_lines.json')
    assert dsf.work_file_length_checker(test_data) is True
    assert test_data["job_type"] == "documents"


@mock.patch("docs_filter.RedisManager")
def test_file_checker_1000_lines(redis):
    test_data = generate_json_data(PATH + '1000_lines.json')
    assert dsf.work_file_length_checker(test_data) is True
    assert test_data["job_type"] == "documents"


@mock.patch("docs_filter.RedisManager")
def test_file_checker_2_workfiles(redis):
    test_data = generate_json_data(PATH + '2_workfiles.json')
    assert dsf.work_file_length_checker(test_data) is True
    assert test_data["job_type"] == "documents"


@mock.patch("docs_filter.RedisManager")
def test_file_checker_1001_lines(redis):
    test_data = generate_json_data(PATH + '1001_lines.json')
    assert dsf.work_file_length_checker(test_data) is False
    assert test_data["job_type"] == "documents"


@mock.patch("docs_filter.RedisManager")
def test_file_checker_too_many_attachments(redis):
    test_data = generate_json_data(PATH + 'too_many_attachments.json')
    assert dsf.work_file_length_checker(test_data) is False
    assert test_data["job_type"] == "documents"


# Assimilation Tests
@mock.patch("docs_filter.RedisManager")
def test_create_job(redis):
    test_data = generate_json_data(PATH + '500_lines.json')
    job_id = "1"
    job = json.loads(dsf.create_document_job(test_data["data"], job_id))
    assert job["job_id"] == "1"
    assert job["job_type"] == "document"
