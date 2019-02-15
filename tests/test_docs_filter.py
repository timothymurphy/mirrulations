import pytest
import json
import mock
import mirrulations.docs_filter as dsf
import fakeredis
import redis
from mirrulations.redis_manager import RedisManager
from ast import literal_eval
import os

PATH = 'tests/test_files/'

r = RedisManager(redis.Redis())


def generate_json_data(file_name):
    file = open(file_name, 'r')
    test_data = json.load(file)
    return test_data


@mock.patch('mirrulations.redis_manager.reset_lock')
@mock.patch('mirrulations.redis_manager.set_lock')
def make_database(reset, lock):
    r = RedisManager(fakeredis.FakeRedis())
    r.delete_all()
    return r


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


# Local Files Check Tests
# CURRENTLY SERVER ONLY TEST
# def test_file_exists_local():
#     home = os.getenv("HOME")
#     path = home + "/regulations_data/AHRQ_FRDOC/AHRQ_FRDOC_0001/AHRQ_FRDOC_0001-0036/doc.AHRQ_FRDOC_0001-0036.json"
#     count = 0
#     count, verdict = dsf.local_files_check(path, count)
#     assert count == 0
#     assert verdict is True


def test_file_doesnt_exists_local():
    home = os.getenv("HOME")
    path = home + "/regulations_data/AHRQ_FRDOC/AHRQ_FRDOC_0001/AHRQ_FRDOC_0001-0037/doc.AHRQ_FRDOC_0001-0037.json"
    verdict = dsf.local_files_check(path)
    assert verdict is False


# Queue Files Check Tests
def test_files_exists_redis_queue():
    r = make_database()
    r.delete_all()
    data = generate_json_data(PATH + "queue_jobs.json")
    for x in data["data"]:
        for line in x:
            r.add_to_queue(line)
    queue, progress = r.get_all_keys()
    verdict = dsf.redis_queue_check("AHRQ_FRDOC_0001-0036", queue)
    assert verdict is True


def test_files_does_not_exists_redis_queue():
    r = make_database()
    r.delete_all()
    data = generate_json_data(PATH + "queue_jobs.json")
    for x in data["data"]:
        for line in x:
            r.add_to_queue(line)
    queue, progress = r.get_all_keys()
    verdict = dsf.redis_queue_check("AHRQ_FRDOC_0001-0039", queue)
    assert verdict is False


# Progress Files Check Tests
def test_files_exists_redis_progress():
    r = make_database()
    r.delete_all()
    data = generate_json_data(PATH + "queue_jobs.json")
    for x in data["data"]:
        for line in x:
            r.add_to_progress(line)
    queue, progress = r.get_all_keys()
    #verdict = dsf.redis_progress_check("AHRQ_FRDOC_0001-0036", progress)
    for key in progress:
        print(r.get_specific_job_from_progress_no_lock(key))
   # assert verdict is True


# Full Files Check Tests
# CURRENTLY SERVER ONLY TEST
# def test_check_document_exists_part_1():
#     test_data = generate_json_data(PATH + "1_workfile_2_documents.json")
#     test_data = dsf.check_document_exists(test_data)
#     assert test_data["data"] == [[{"id": "AHRQ_FRDOC_0001-0037", "count": 1}]]


# Validation Tests
@mock.patch("mirrulations.docs_filter.RedisManager")
def test_file_checker_500_lines(redis):
    test_data = generate_json_data(PATH + '500_lines.json')
    assert dsf.workfile_length_checker(test_data) is True
    assert test_data["type"] == "docs"


@mock.patch("mirrulations.docs_filter.RedisManager")
def test_file_checker_1000_lines(redis):
    test_data = generate_json_data(PATH + '1000_lines.json')
    assert dsf.workfile_length_checker(test_data) is True
    assert test_data["type"] == "docs"


@mock.patch("mirrulations.docs_filter.RedisManager")
def test_file_checker_2_workfiles(redis):
    test_data = generate_json_data(PATH + '2_workfiles.json')
    assert dsf.workfile_length_checker(test_data) is True
    assert test_data["type"] == "docs"


@mock.patch("mirrulations.docs_filter.RedisManager")
def test_file_checker_1001_lines(redis):
    test_data = generate_json_data(PATH + '1001_lines.json')
    assert dsf.workfile_length_checker(test_data) is False
    assert test_data["type"] == "docs"


@mock.patch("mirrulations.docs_filter.RedisManager")
def test_file_checker_too_many_attachments(redis):
    test_data = generate_json_data(PATH + 'too_many_attachments.json')
    assert dsf.workfile_length_checker(test_data) is False
    assert test_data["type"] == "docs"


# Assimilation Tests
@mock.patch("mirrulations.docs_filter.RedisManager")
def test_create_job(redis):
    test_data = generate_json_data(PATH + '500_lines.json')
    job_id = "1"
    job = json.loads(dsf.create_document_job(test_data["data"], job_id))
    assert job["job_id"] == "1"
    assert job["type"] == "doc"
