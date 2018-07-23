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
            item_from_queue = self.r.lpop("queue")

            if item_from_queue is None:
                work = {"type":"none"}
            else:
                work = literal_eval(item_from_queue.decode('utf-8'))
            self.r.hset("progress", get_curr_time(), work)
            return work

    def add_to_queue(self, work):
        """
        Adds work to the queue
        :param work: the word to be added to the queue
        :return:
        """
        with self.lock:
            self.r.rpush("queue", work)

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

    def get_all_items_in_queue_no_lock(self):
        """
        Returns all the items currently in the queue
        :return: the list of items in the queue
        """
        return self.r.lrange("queue", 0, -1)

    def get_all_items_in_progress(self):
        """
        Returns all the items currently in progress
        :return: the list of items currently in progress
        """
        with self.lock:
            return self.r.hgetall("progress")

    def get_all_items_in_progress_no_lock(self):
        """
        Returns all the items currently in progress
        :return: the list of items currently in progress
        """

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
                    self.r.rpush("queue", item)
                else:
                    pass


    def delete_all(self):
        """
        Delete everything from the database
        """
        self.r.flushall()

    def get_specific_job_from_queue(self, job_id):
        """
           Gets a job from the "queue" queue using its job_id
           :param job_id: the id for the job in question
           :return: returns the job of the given job_id or '' if the job does not exist
           """
        with self.lock:
            for element in range(self.r.llen('queue')):

                current = (self.r.lindex('queue', element)).decode("utf-8")

                info = json.loads(current)

                if job_id == info['job_id']:
                    return current

            return ''

    def get_specific_job_from_queue_no_lock(self, job_id):
        """
           Gets a job from the "queue" queue using its job_id
           :param job_id: the id for the job in question
           :return: returns the job of the given job_id or '' if the job does not exist
           """

        for element in range(self.r.llen('queue')):

            current = (self.r.lindex('queue', element)).decode("utf-8")

            info = json.loads(current)

            if job_id == info['job_id']:
                return current

        return ''

    def does_job_exist_in_queue(self, job_id):
        """
        Verifies that a given job is in the "queue" queue exists
        :param job_id: the id for the job in question
        :return: True if the job is in the "queue", False if it is not in the "queue"
        """
        with self.lock:
            job = self.get_specific_job_from_queue_no_lock(job_id)
            if job == '':
                return False
            else:
                return True

    def remove_specific_job_from_queue(self, job_id):
        """
        Removes a job from the "queue" queue
        :param job_id: the id for the job in question
        """
        with self.lock:
            job = self.get_specific_job_from_queue_no_lock(job_id)
            self.r.lrem('queue', job, 1)

    def does_job_exist_in_progress(self, job_id):
        """
        Verifies that a given job is in the "progress" queue exists
        :param job_id: the key of the job
        :return: True if the job is in progress, False if it is not in progress
        """
        with self.lock:
            key = self.get_keys_from_progress_no_lock(job_id)
            job = self.get_specific_job_from_progress_no_lock(key)
            if job == '':
                return False
            else:
                return True

    def get_specific_job_from_progress(self, key):
        """
        Get a specific job that is in the "progress" queue
        :param key: the key of the job requested
        :return: '' if the job does not exist, otherwise returns the data for the job
        """
        with self.lock:
            job = self.r.hget('progress', key)

            if job is not None:
                data = job.decode("utf-8")
                return data
            return ''

    def get_specific_job_from_progress_no_lock(self, key):
        """
        Get a specific job that is in the "progress" queue
        :param key: the key of the job requested
        :return: '' if the job does not exist, otherwise returns the data for the job
        """
        job = self.r.hget('progress', key)

        if job is not None:
            data = job.decode("utf-8")
            return data
        return ''

    def get_keys_from_progress(self, job_id):
        """
        Get the key of a job that is the "progress" queue
        :param job_id: the id of the job you want to get the key for
        :return: '' if the job does not exist, or the key if the job does exist
        """
        with self.lock:
            key_list = self.r.hgetall('progress')
            for key in key_list:
                json_info = self.get_specific_job_from_progress_no_lock(key)
                info = json.loads(json_info)
                if info["job_id"] == job_id:
                    return key.decode("utf-8")
            return ''

    def get_keys_from_progress_no_lock(self, job_id):
        """
        Get the key of a job that is the "progress" queue
        :param job_id: the id of the job you want to get the key for
        :return: '' if the job does not exist, or the key if the job does exist
        """

        key_list = self.r.hgetall('progress')
        for key in key_list:
            json_info = self.get_specific_job_from_progress_no_lock(key)
            info = json.loads(json_info)
            if info["job_id"] == job_id:
                return key.decode("utf-8")
        return ''

    def remove_job_from_progress(self, key):
        """
        Removes a job from the "progress" queue
        :param key: the key of the job that is to be removed
        :return: 
        """
        with self.lock:
            self.r.hdel('progress', key)

    # Combined Functions
    def renew_job(self, job_id):
        """
        Takes an expired job from the "progress" queue and adds it back into the "queue" queue. It then deletes
        the expired job from the "progress" queue
        :param job_id: the id for the job in question
        :return:
        """
        with self.lock:
            key = self.get_keys_from_progress_no_lock(job_id)
            job = self.get_specific_job_from_progress_no_lock(key)
            self.r.rpush("queue", job)
            self.r.hdel('progress', key)


# Used to reset the locks
def reset_lock(database):
    redis_lock.reset_all(database)


# Sets the lock for the database
def set_lock(database):
    return redis_lock.Lock(database, "lock72")


# Returns the current time
def get_curr_time():
    return float(time.time())
