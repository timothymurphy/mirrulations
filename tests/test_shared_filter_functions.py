import pytest
import fakeredis
import json
import time
import shared_filter_functions as sff


def generate_data(job_id, type, data, version):
    dict = {}

    dict["job_id"] = job_id
    dict["job_type"] = type
    dict["data"] = data
    dict["version"] = version

    json_data = json.dumps(dict)

    return json_data


def setUp():
    # Setup fake redis for testing.
    return fakeredis.FakeStrictRedis()


# QUEUE Tests
def test_job_exists():
    r = setUp()
    job = generate_data('1', 'docs', [], 'v1')
    sff.add_job(job, r, "queue")
    assert sff.job_exists('1', r, "queue") is True
    r.flushall()


def test_job_does_not_exists():
    r = setUp()
    job = generate_data('2', 'docs', [], 'v1')
    sff.add_job(job, r, "queue")
    assert sff.job_exists('1', r, "queue") is False
    r.flushall()


def test_add_job():
    r = setUp()
    job = generate_data('52', 'doc', [], 'v1')
    sff.add_job(job, r, 'queue')
    assert sff.job_exists('52', r, 'queue') is True
    r.flushall()


def test_add_multiple_jobs():
    r = setUp()
    job1 = (generate_data('52', 'docs', [], 'v1'))
    job2 = (generate_data('30', 'docs', [], 'v1'))
    job3 = (generate_data('97', 'docs', [], 'v1'))
    job4 = (generate_data('18', 'docs', [], 'v1'))
    sff.add_job(job1, r, "queue")
    sff.add_job(job2, r, "queue")
    sff.add_job(job3, r, "queue")
    sff.add_job(job4, r, "queue")
    assert sff.job_exists('52', r, 'queue') is True
    assert sff.job_exists('30', r, 'queue') is True
    assert sff.job_exists('97', r, 'queue') is True
    assert sff.job_exists('18', r, 'queue') is True
    r.flushall()


def test_remove_job():
    r = setUp()
    job = (generate_data('2', 'docs', [], 'v1'))
    sff.add_job(job, r, "queue")
    sff.remove_job_queue('2', r, "queue")
    assert sff.job_exists('2', r, "queue") is False
    r.flushall()


def test_remove_multiple_jobs():
    r = setUp()

    job1 = (generate_data('52', 'docs', [], 'v1'))
    job2 = (generate_data('30', 'docs', [], 'v1'))
    job3 = (generate_data('97', 'docs', [], 'v1'))
    job4 = (generate_data('18', 'docs', [], 'v1'))

    sff.add_job(job1, r, "queue")
    sff.add_job(job2, r, "queue")
    sff.add_job(job3, r, "queue")
    sff.add_job(job4, r, "queue")

    sff.remove_job_queue('52', r, 'queue')
    sff.remove_job_queue('30', r, 'queue')
    sff.remove_job_queue('97', r, 'queue')
    sff.remove_job_queue('18', r, 'queue')

    assert sff.job_exists('52', r, 'queue') is False
    assert sff.job_exists('30', r, 'queue') is False
    assert sff.job_exists('97', r, 'queue') is False
    assert sff.job_exists('18', r, 'queue') is False
    r.flushall()


def test_remove_non_existant_job():
    r = setUp()
    sff.remove_job_queue('2', r, "queue")
    assert sff.job_exists('2', r, "queue") is False
    r.flushall()


def test_get_job_attributes():
    r = setUp()
    job1 = (generate_data('1', 'doc', [], 'v1'))
    sff.add_job(job1, r, 'queue')
    job = sff.get_job('1', r, 'queue')
    job = json.loads(job)
    assert job['job_id'] == '1'
    assert job["job_type"] == "doc"
    assert job["data"] == []
    assert job["version"] == 'v1'
    r.flushall()


# PROGRESS Tests
def test_add_job_progress():
    r = setUp()
    job = (generate_data('10', 'docs', [], 'v1'))
    current_time = time.time()
    sff.add_job_progress(job, r, 'progress', current_time)
    assert r.hexists('progress', current_time)
    r.flushall()


def test_get_job_progress():
    r = setUp()
    job = (generate_data('10', 'docs', [], 'v1'))
    current_time = time.time()
    sff.add_job_progress(job, r, 'progress', current_time)
    job = sff.get_job_progress(current_time, r, "progress")
    info = json.loads(job)
    assert info['job_id'] == '10'
    r.flushall()


def test_job_exists_progress():
    r = setUp()
    job = (generate_data('10', 'docs', [], 'v1'))
    current_time = time.time()
    sff.add_job_progress(job, r, 'progress', current_time)
    assert sff.job_exists_progress(current_time, r, 'progress')
    r.flushall()


def test_get_key():
    r = setUp()
    job = (generate_data('10', 'docs', [], 'v1'))
    current_time = str(time.time())
    sff.add_job_progress(job, r, 'progress', current_time)
    key = sff.get_key_hash('10', r, "progress")
    assert key == current_time
    r.flushall()


def test_get_key_multiple_jobs():
    r = setUp()
    job1 = (generate_data('10', 'docs', [], 'v1'))
    job2 = (generate_data('11', 'docs', [], 'v1'))
    job3 = (generate_data('12', 'docs', [], 'v1'))
    time1 = str(time.time())
    time2 = str(time.time())
    time3 = str(time.time())
    sff.add_job_progress(job1, r, 'progress', time1)
    sff.add_job_progress(job2, r, 'progress', time2)
    sff.add_job_progress(job3, r, 'progress', time3)
    key = sff.get_key_hash('12', r, "progress")
    assert key == time3
    r.flushall()


def test_remove_job_progress():
    r = setUp()
    job = (generate_data('10', 'docs', [], 'v1'))
    current_time = str(time.time())
    sff.add_job_progress(job, r, 'progress', current_time)
    sff.remove_job_progress(current_time, r, "progress")
    assert sff.job_exists_progress(current_time, r, "progress") is False
    r.flushall()


# Combination Tests
def test_renew_job():
    r = setUp()

    job1 = (generate_data('10', 'docs', [], 'v1'))
    job2 = (generate_data('2', 'docs', [], 'v1'))
    current_time = str(time.time())

    sff.add_job(job1, r, "queue")
    sff.add_job_progress(job2, r, "progress", current_time)
    sff.renew_job('2', r)

    assert sff.job_exists_progress(current_time, r, "progress") is False
    assert sff.job_exists('2', r, "queue") is True
    assert sff.job_exists('10', r, "queue") is True
    r.flushall()
