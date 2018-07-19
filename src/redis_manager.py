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
        """
        Gets a single job from the queue
        :return: returns the work to be done from the queue
        """
        with self.lock:
            work = literal_eval(self.r.lpop("queue").decode("utf-8"))
            self.add_to_progress(work)
            return work

    def add_to_queue(self, work):
        """
        Adds work to the queue
        :param work: the word to be added to the queue
        :return:
        """
        with self.lock:
            self.r.lpush("queue", work)

    def add_to_progress(self, work):
        """
        Adds work to progress queue
        :param work: the work that is in progress
        :return:
        """
        with self.lock:
            self.r.hset("progress", get_curr_time(), work)

    def get_all_items_in_queue(self):
        """
        Returns all the items currently in the queue
        :return: the list of items in the queue
        """
        with self.lock:
            return self.r.lrange("queue", 0, -1)

    def get_all_items_in_progress(self):
        """
        Returns all the items currently in progress
        :return: the list of items currently in progress
        """
        with self.lock:
            return self.r.hgetall("progress")

    def find_expired(self):
        """
        Searches through the work in progress, checks which works have been in progress for over 6 hours,
        and moves those that have been in progress for over 6 hours back to the queue
        :return:
        """
        with self.lock:
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

    def get_specific_job_from_queue(self, job_id):
        """
           Gets a job from the queue from its job_id
           :param job_id: the id for the job in question
           :return: returns the job with the given job_id
           """
        with self.lock:
            for element in range(self.r.llen('queue')):

                current = (self.r.lindex('queue', element)).decode("utf-8")


                info = json.loads(current)

                if job_id == info['job_id']:
                    return current

            return ''

    def does_job_exist_in_queue(self, job_id):
        """
        Verifies that a given job that is in the queue exists
        :param job_id: the id for the job in question
        :return: true if the job is in the queue, false if it is not in the queue
        """
        with self.lock:
            job = self.get_specific_job_from_queue(job_id)
            if job == '':
                return False
            else:
                return True

    def remove_specific_job_from_queue(self, job_id):
        """
        Removes a completed or expired job from the queue
        :param job_id: the id for the job in question
        """
        with self.lock:
            job = self.get_specific_job_from_queue(job_id)
            self.r.lrem('queue', job, 1)

    def does_job_exist_in_progress(self,key):
        """
        Verifies that a given job that is in progress exists
        :param key: the key of the job
        :return: true if the job is in progress, false if it is not in progress
        """
        with self.lock:
            job = self.get_specific_job_from_progress(key)
            if job == '':
                return False
            else:
                return True

    def get_specific_job_from_progress(self, key):
        """
        Get a specific job that is in progress
        :param key: the key of the job requested
        :return: nothing if the job does not exist, otherwise returns the data for the job
        """
        with self.lock:
            job = self.r.hget('progress', key)

            if job is None:
                return ''
            else:
                data = job.decode("utf-8")
                return data

    def get_keys_from_progress(self, job_id):
        """
        Get the key of a job that is in progress
        :param job_id: the id of the job you want the key from
        :return: nothing if the job does not exist, or the key if it does exist
        """
        with self.lock:
            key_list = self.r.hgetall('progress')
            for key in key_list:
                json_info = self.get_specific_job_from_progress(key)
                info = json.loads(json_info)
                if info["job_id"] == job_id:
                    return key.decode("utf-8")
            return ''

    def remove_job_from_progress(self, key):
        """
        Removes a job from being in progress
        :param key: the key of the job that is to be removed
        :return: 
        """
        with self.lock:
            self.r.hdel('progress', key)

    # Combined Functions
    def renew_job(self, job_id):
        """
        Takes an expired job and adds it back into the job queue
        :param job_id: the id for the job in question
        :return:
        """
        with self.lock:
            key = self.get_keys_from_progress(job_id)
            job = self.get_specific_job_from_progress(key)
            self.add_to_queue(job)
            self.remove_job_from_progress(key)


# Used to reset the locks
def reset_lock(database):
    redis_lock.reset_all(database)


# Sets the lock for the database
def set_lock(database):
    return redis_lock.Lock(database, "lock72")


# Returns the current time
def get_curr_time():
    return float(time.time())
