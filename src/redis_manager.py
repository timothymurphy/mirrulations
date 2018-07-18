import redis
from ast import literal_eval
import redis_lock
import json
import time



class RedisManager:


    def __init__(self, database):
        """
        Initialize the database and create the lock
        """
        self.r = database
        reset_lock(self.r)
        self.lock = set_lock(self.r)


    def get_work(self):
        with self.lock:
            work = literal_eval(self.r.lpop("queue").decode("utf-8"))
            self.add_to_progress(work)
            return work

    def get_singe_queue_item(self):
        with self.lock:
            return self.r.lpop("queue")

    def add_to_queue(self, work):
        with self.lock:
            self.r.lpush("queue", work)

    def add_to_progress(self, work):
        with self.lock:
            self.r.hset("progress", get_curr_time(), work)

    def get_all_items_in_queue(self):
        with self.lock:
            return self.r.lrange("queue", 0, -1)

    def get_all_items_in_progress(self):
        with self.lock:
            return self.r.hgetall("progress")


    def move_between_queues(self, move_from, move_to):
        with self.lock:
            pass

    def find_expired(self):
        for item in self.r.hgetall('progress'):
            if (float(time.time()) - float(item.decode('utf-8')) > 21600):
                self.r.hdel('progress',item)
            else:
                pass


    def delete_all(self):
        """
        Delete everything from the database
        """
        self.r.flushall()

def reset_lock(database):
    redis_lock.reset_all(database)

def set_lock(database):
    redis_lock.Lock(database, "lock72")

def get_curr_time():
    return float(time.time())
