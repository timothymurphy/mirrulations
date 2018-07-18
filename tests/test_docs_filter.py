import pytest
import json
import fakeredis

import docs_filter as dsf
import shared_filter_functions as sff

PATH = 'test_files/'


def generate_json_data(file_name):
    file = open(file_name, 'r')
    test_data = json.load(file)
    return test_data


def setUp():
    # Setup fake redis for testing.
    return fakeredis.FakeStrictRedis()


# Validation Tests
def test_file_checker_500_lines():
    test_data = generate_json_data(PATH + '500_lines.json')
    assert dsf.file_length_checker(test_data) is True
    assert test_data["job_type"] == "documents"


def test_file_checker_1000_lines():
    test_data = generate_json_data(PATH + '1000_lines.json')
    assert dsf.file_length_checker(test_data) is True
    assert test_data["job_type"] == "documents"


def test_file_checker_2_workfiles():
    test_data = generate_json_data(PATH + '2_workfiles.json')
    assert dsf.file_length_checker(test_data) is True
    assert test_data["job_type"] == "documents"


def test_file_checker_1001_lines():
    test_data = generate_json_data(PATH + '1001_lines.json')
    assert dsf.file_length_checker(test_data) is False
    assert test_data["job_type"] == "documents"


def test_file_checker_too_many_attachments():
    test_data = generate_json_data(PATH + 'too_many_attachments.json')
    assert dsf.file_length_checker(test_data) is False
    assert test_data["job_type"] == "documents"


# Assimilation Tests
def test_create_job():
    r = setUp()
    test_data = generate_json_data(PATH + '500_lines.json')
    job_id = "1"
    job = dsf.create_job(test_data["data"], job_id)
    sff.add_job(job, r, "queue")
    assert sff.job_exists('1', r, "queue")



