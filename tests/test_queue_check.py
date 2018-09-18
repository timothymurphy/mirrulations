import pytest
import requests_mock
import mock
import fakeredis
from queue_check import queue_check
from redis_manager import RedisManager

@mock.patch('redis_manager.reset_lock')
@mock.patch('redis_manager.set_lock')
def emptydatabase(reset, lock):
    r = RedisManager(fakeredis.FakeRedis())
    return r

@mock.patch('redis_manager.reset_lock')
@mock.patch('redis_manager.set_lock')
def make_database(reset, lock):
    r = RedisManager(fakeredis.FakeRedis())
    r.delete_all()
    list = {"A":"a", "B":["b", "c"]}
    list2 = {"D":"d", "E":["e", "f"]}
    list3 = {"G":"g", "H":["h", "i"]}
    r.add_to_queue(list)
    r.add_to_queue(list2)
    r.add_to_progress(list3)
    return r

def test_queue_check_empty():
    r = emptydatabase()
    a,b = queue_check(r)
    assert len(a) == 0
    assert len(b) == 0

def test_queue_check_items_in_queue():
    r = make_database()
    a,b = queue_check(r)
    assert len(a) == 1
    assert len(b) == 2




