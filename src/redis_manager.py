import redis
import threading
from ast import literal_eval



class RedisManager:


    def __init__(self, command):
        """
        Initialize the database
        """
        self.r = redis.Redis()
        self.lock = threading.RLock()

    def get_work(self):
        with self.lock:
            work = literal_eval(self.r.lpop("queued").decode("utf-8"))
            self.r.lpush("progress", work)
            return work

    def get(self, name):
        """

        :param name:
        :return:
        """
        return self.r.get(name)

    def delete_all(self):
        """
        Delete everything from the database
        """
        self.r.flushall()

