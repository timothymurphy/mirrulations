import pytest
import fakeredis
import redis
import mock
from redis_manager import RedisManager
from ast import literal_eval
import time

@mock.patch('redis_manager.reset_lock')
@mock.patch('redis_manager.set_lock')
def make_databse(reset, lock):
    r = RedisManager(fakeredis.FakeRedis())
    r.delete_all()
    list = ["a", ["b", "c"]]
    list2 = ["d", ["e", "f"]]
    list3 = ["g", ["h", "i"]]
    r.add_to_queue(list)
    r.add_to_queue(list2)
    r.add_to_queue(list3)
    return r


def ignore_test_iterate():
    r = make_databse()
    for item in r.get_all_items_in_queue():
        item  = literal_eval(item.decode('utf-8'))
        if int(time.time()) - item[2] > 21600:
            print(int(time.time()) - item[2])
            print("Expired!")
        else:
            print(int(time.time()) - item[2])
            print("Still Good!")

def test_get_single_queue_item():
    r = make_databse()
    item = literal_eval(r.get_singe_queue_item().decode('utf-8'))
    assert item == ["g", ["h", "i"]]

def test_get_all_item_in_queue():
    r = make_databse()
    items = r.get_all_items_in_queue()
    assert len(items) == 3

def test_get_all_item_in_progress():
    r = make_databse()
    list4 = ["l", ["m", "n"]]
    r.add_to_progress(list4)
    assert len(r.get_all_items_in_progress()) == 1

def test_get_work():
    r = make_databse()
    assert len(r.get_all_items_in_queue()) == 3
    assert len(r.get_all_items_in_progress()) == 0
    work = r.get_work()
    assert work == ["g", ["h", "i"]]
    assert len(r.get_all_items_in_queue()) == 2
    assert len(r.get_all_items_in_progress()) == 1

def test_add_to_queue():
    r = make_databse()
    list4 = ["j", ["k", "l"]]
    assert len(r.get_all_items_in_queue()) == 3
    r.add_to_queue(list4)
    assert len(r.get_all_items_in_queue()) == 4

def test_delete_all():
    r = make_databse()
    r.delete_all()
    assert len(r.get_all_items_in_queue()) == 0
    assert len(r.get_all_items_in_progress()) == 0

@mock.patch('redis_manager.get_curr_time', return_value=1531911498)
def test_find_expired(time):#time):
    r = make_databse()
    r.delete_all()
    t3 = (["g", ["h", "i"]])
    r.add_to_progress(t3)
    assert len(r.get_all_items_in_progress()) == 1
    r.find_expired()
    assert len(r.get_all_items_in_progress()) == 0

def test_find_no_expired():
    r = make_databse()
    r.delete_all()
    t3 = (["g", ["h", "i"]])
    t2 = (["j", ["k", "l"]])
    r.add_to_progress(t3)
    r.add_to_progress(t2)
    assert len(r.get_all_items_in_progress()) == 2
    r.find_expired()
    assert len(r.get_all_items_in_progress()) == 2












