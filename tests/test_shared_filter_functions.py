import pytest
import fakeredis
import json
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


def test_job_exists():
    r = setUp()
    sff.add_job(generate_data('1', 'docs', [], 'v1'), r, "progress")
    assert sff.job_exists('1', r, "progress") is True
    r.flushall()


def test_job_does_not_exists():
    r = setUp()
    sff.add_job(generate_data('2', 'docs', [], 'v1'), r, "progress")
    assert sff.job_exists('1', r, "progress") is False
    r.flushall()


def test_add_job():
    r = setUp()
    sff.add_job(generate_data('52', 'doc', [], 'v1'), r, 'queue')
    assert sff.job_exists('52', r, 'queue') is True
    r.flushall()


def test_add_multiple_jobs():
    r = setUp()
    sff.add_job(generate_data('52', 'docs', [], 'v1'), r, "queue")
    sff.add_job(generate_data('30', 'docs', [], 'v1'), r, "queue")
    sff.add_job(generate_data('97', 'docs', [], 'v1'), r, "progress")
    sff.add_job(generate_data('18', 'docs', [], 'v1'), r, "progress")
    assert sff.job_exists('52', r, 'queue') is True
    assert sff.job_exists('30', r, 'queue') is True
    assert sff.job_exists('97', r, 'progress') is True
    assert sff.job_exists('18', r, 'progress') is True
    r.flushall()


def test_remove_job():
    r = setUp()
    sff.add_job(generate_data('2', 'docs', [], 'v1'), r, "progress")
    sff.remove_job('2', r, "progress")
    assert sff.job_exists('2', r, "progress") is False
    r.flushall()


def test_remove_multiple_jobs():
    r = setUp()
    sff.add_job(generate_data('52', 'docs', [], 'v1'), r, "queue")
    sff.add_job(generate_data('30', 'docs', [], 'v1'), r, "queue")
    sff.add_job(generate_data('97', 'docs', [], 'v1'), r, "progress")
    sff.add_job(generate_data('18', 'docs', [], 'v1'), r, "progress")
    sff.remove_job('52', r, 'queue')
    sff.remove_job('30', r, 'queue')
    sff.remove_job('97', r, 'progress')
    sff.remove_job('18', r, 'progress')
    assert sff.job_exists('52', r, 'queue') is False
    assert sff.job_exists('30', r, 'queue') is False
    assert sff.job_exists('97', r, 'progress') is False
    assert sff.job_exists('18', r, 'progress') is False
    r.flushall()


def test_remove_non_existant_job():
    r = setUp()
    sff.remove_job('2', r, "progress")
    assert sff.job_exists('2', r, "progress") is False
    r.flushall()


def test_get_job_attributes():
    r = setUp()
    sff.add_job(generate_data('1', 'doc', [], 'v1'), r, 'queue')
    job = sff.get_job('1', r, 'queue')
    job = json.loads(job)
    assert job['job_id'] == '1'
    assert job["job_type"] == "doc"
    assert job["data"] == []
    assert job["version"] == 'v1'


def test_renew_job():
    r = setUp()
    sff.add_job(generate_data('10', 'docs', [], 'v1'), r, "queue")
    sff.add_job(generate_data('2', 'docs', [], 'v1'), r, "progress")
    sff.renew_job('2', r)
    assert sff.job_exists('2', r, "progress") is False
    assert sff.job_exists('2', r, "queue") is True
    assert sff.job_exists('10', r, "queue") is True
    r.flushall()
