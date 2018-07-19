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
                self.add_to_queue(item)
            else:
                pass


    def delete_all(self):
        """
        Delete everything from the database
        """
        self.r.flushall()

    def get_sepcific_job_from_queue(self, job_id):
        """
           Selects a job from the queue by its id
           :param job_id: the id for the job in question
           :param Redis_Manager: database manager
           :param queue: the queue containing jobs to be completed
           :return:
           """

        for element in range(self.r.llen('queue')):

            current = (self.r.lindex('queue', element)).decode("utf-8")


            info = json.loads(current)

            if job_id == info['job_id']:
                return current

        return ''

    def does_job_exist_in_queue(self, job_id):
        """
        Verifies that a given job that is to be completed exists
        :param job_id: the id for the job in question
        :param Redis_Manager: database manager
        :param queue: the queue containing jobs to be completed
        :return:
        """

        job = self.get_sepcific_job_from_queue(job_id)
        if job == '':
            return False
        else:
            return True

    def remove_specific_job_from_queue(self, job_id):
        """
        Removes a completed or expired job from the queue
        :param job_id: the id for the job in question
        :param Redis_Manager: database manager
        :param queue: the queue containing jobs to be completed
        :return:
        """
        job = self.get_sepcific_job_from_queue(job_id)
        self.r.lrem('queue', job, 1)

    def does_job_exist_in_progress(self,key):
        """

        :param key:
        :param Redis_Manager:
        :param queue:
        :return:
        """
        job = self.get_specific_job_from_progress(key)
        if job == '':
            return False
        else:
            return True

    def get_specific_job_from_progress(self, key):
        """

        :param key:
        :param Redis_Manager:
        :param queue:
        :return:
        """
        job = self.r.hget('progress', key)

        if job is None:
            return ''
        else:
            data = job.decode("utf-8")
            return data

    def get_keys_from_progress(self, job_id):
        key_list = self.r.hgetall('progress')
        for key in key_list:
            json_info = self.get_specific_job_from_progress(key)
            info = json.loads(json_info)
            if info["job_id"] == job_id:
                return key.decode("utf-8")
        return ''

    def remove_job_from_progress(self, key):
        self.r.hdel('progress', key)

    # Combined Functions
    def renew_job(self, job_id):
        """
        Takes an expired job and adds it back into the job queue
        :param job_id: the id for the job in question
        :param Redis_Manager: database manager
        :return:
        """

        key = self.get_keys_from_progress(job_id)
        job = self.get_specific_job_from_progress(key)
        self.add_to_queue(job)
        self.remove_job_from_progress(key)


def reset_lock(database):
    redis_lock.reset_all(database)

def set_lock(database):
    redis_lock.Lock(database, "lock72")

def get_curr_time():
    return float(time.time())
