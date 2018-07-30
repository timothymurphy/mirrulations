from ast import literal_eval
import redis_lock
import json
import time
import logging

FORMAT = '%(asctime)-15s %(clientip)s %(user)-8s %(message)s'
logging.basicConfig(filename='redis_log.log', format=FORMAT)
d = {'clientip': '192.168.0.1', 'user': 'REDIS'}
logger = logging.getLogger('tcpserver')


class RedisManager:

    def __init__(self, database):
        """
        Initialize the database and create the lock
        """
        logger.warning('REDIS Setup Successful: %s', '__init___: redis setup', extra=d)
        logger.warning('Assign Variable: %s', '__init__: assign the redis database', extra=d)
        self.r = database
        logger.warning('Variable Success: %s', '__init__: redis database successfully assigned', extra=d)
        logger.warning('Calling Function: %s', '__init__: init attempting to reset locks', extra=d)
        reset_lock(self.r)
        logger.warning('Function Successful: %s', '__init__: init reset the locks', extra=d)
        logger.warning('Assign Variable: %s', '__init__: attempting assign the lock', extra=d)
        logger.warning('Calling Function: %s', '__init__: attempting to set a lock', extra=d)
        self.lock = set_lock(self.r)


    def get_work(self):
        """
        Gets a single job from the queue
        :return: returns the work to be done from the queue
        """
        logger.warning('Call Successful: %s', 'get_work: get_work call successful', extra=d)
        logger.warning('Locking: %s', 'get_work: attempting to retrieve lock', extra=d)
        with self.lock:
            logger.warning('Locking: %s', 'get_work: lock retrieved successful', extra=d)
            logger.warning('Assign Variable: %s', 'get_work: attempting to pop item from queue', extra=d)
            item_from_queue = self.r.lpop("queue")
            logger.warning('Variable Success: %s', 'get_work: item_from_queue retrieved an item', extra=d)

            if item_from_queue is None:
                logger.warning('Assign Variable: %s', 'get_work: assign work to have a type of none', extra=d)
                work = {"type":"none"}
                logger.warning('Variable Success: %s', 'get_work: type none assigned to work', extra=d)
            else:
                logger.warning('Assign Variable: %s', 'get_work: assign work to the item retrieved from the queue', extra=d)
                work = literal_eval(item_from_queue.decode('utf-8'))
                logger.warning('Variable Success: %s', 'get_work: work assigned to item_from_queue', extra=d)
                logger.warning('Queue Add Attempt: %s', 'get_work: attempting to add the work gotten to the progress queue', extra=d)
                self.r.hset("progress", get_curr_time(), work)
                logger.warning('Queue Add Success: %s', 'get_work: work added to the progress queue', extra=d)
            logger.warning("Returning: %s", 'get_work: returning the work to do', extra=d)
            return work

    def add_to_queue(self, work):
        """
        Adds work to the queue
        :param work: the word to be added to the queue
        :return:
        """
        logger.warning('Call Successful: %s', 'add_to_queue: add_to_queue call successful', extra=d)
        logger.warning('Locking: %s', 'add_to_queue: attempting to retrieve lock', extra=d)
        with self.lock:
            logger.warning('Locking: %s', 'add_to_queue: lock retrieved successful', extra=d)
            logger.warning('Queue Add Attempt: %s', 'add_to_queue: attempting to push item to queue', extra=d)
            self.r.rpush("queue", work)


    def add_to_progress(self, work):
        """
        Adds work to progress queue
        :param work: the work that is in progress
        :return:
        """
        logger.warning('Call Successful: %s', 'add_to_progress: add_to_progress call successful', extra=d)
        logger.warning('Locking: %s', 'add_to_progress: attempting to retrieve lock', extra=d)
        with self.lock:
            logger.warning('Locking: %s', 'add_to_progress: lock retrieved successful', extra=d)
            logger.warning('Queue Add Attempt: %s', 'add_to_progress: attempting to add item to progress queue', extra=d)
            self.r.hset("progress", get_curr_time(), work)

    def get_all_items_in_queue(self):
        """
        Returns all the items currently in the queue
        :return: the list of items in the queue
        """
        logger.warning('Call Successful: %s', 'get_all_items_in_queue: get_all_items_in_queue call successful', extra=d)
        logger.warning('Locking: %s', 'get_all_items_in_queue: attempting to retrieve lock', extra=d)
        with self.lock:
            logger.warning('Locking: %s', 'get_all_items_in_queue: lock retrieved successful', extra=d)
            logger.warning("Returning: %s", 'get_all_items_in_queue: returning the list of all items in queue', extra=d)
            return self.r.lrange("queue", 0, -1)

    def get_all_items_in_queue_no_lock(self):
        """
        Returns all the items currently in the queue
        :return: the list of items in the queue
        """
        logger.warning('Call Successful: %s', 'get_all_items_in_queue_no_lock: get_all_items_in_queue call successful', extra=d)
        logger.warning("Returning: %s", 'get_all_items_in_queue_no_lock: returning the list of all items in queue', extra=d)
        return self.r.lrange("queue", 0, -1)

    def get_all_items_in_progress(self):
        """
        Returns all the items currently in progress
        :return: the list of items currently in progress
        """
        logger.warning('Call Successful: %s', 'get_all_items_in_progress: get_all_items_in_progress call successful', extra=d)
        logger.warning('Locking: %s', 'get_all_items_in_progress: attempting to retrieve lock', extra=d)
        with self.lock:
            logger.warning('Locking: %s', 'get_all_items_in_progress: lock retrieved successful', extra=d)
            logger.warning("Returning: %s", 'get_all_items_in_progress: returning the list of all items in progress', extra=d)
            return self.r.hgetall("progress")

    def get_all_items_in_progress_no_lock(self):
        """
        Returns all the items currently in progress
        :return: the list of items currently in progress
        """
        logger.warning('Call Successful: %s', 'get_all_items_in_progress_no_lock: get_all_items_in_progress_no_lock call successful', extra=d)
        logger.warning("Returning: %s", 'get_all_items_in_progress_no_lock: returning the list of all items in progress',extra=d)
        return self.r.hgetall("progress")

    def find_expired(self):
        """
        Searches through the work in progress, checks which works have been in progress for over 6 hours,
        and moves those that have been in progress for over 6 hours back to the queue
        :return:
        """
        logger.warning('Call Successful: %s','find_expired: find_expired call successful', extra=d)
        logger.warning('Locking: %s', 'find_expired: attempting to retrieve lock', extra=d)
        with self.lock:
            logger.warning('Locking: %s', 'find_expired: lock retrieved successful', extra=d)
            for item in self.r.hgetall('progress'):
                if (float(time.time()) - float(item.decode('utf-8')) > 21600):
                    logger.warning('Queue Remove Attempt: %s', 'find_expired: attmept to remove expired item from progress', extra=d)
                    self.r.hdel('progress',item)
                    logger.warning('Queue Remove Success: %s', 'find_expired: item removed from progress', extra=d)
                    logger.warning('Queue Add Attempt: %s', 'find_expired: attempt to add item to queue', extra=d)
                    self.r.rpush("queue", item)



    def delete_all(self):
        """
        Delete everything from the database
        """
        logger.warning('Call Successful: %s', 'delete_all: delete_all call successful', extra=d)
        logger.warning('Flushall Attempt: %s', 'delete_all: attempting to flush all items from queue', extra=d)
        self.r.flushall()

    def get_specific_job_from_queue(self, job_id):
        """
           Gets a job from the "queue" queue using its job_id
           :param job_id: the id for the job in question
           :return: returns the job of the given job_id or '' if the job does not exist
           """
        logger.warning('Call Successful: %s', 'get_specific_job_from_queue: get_specific_job_from_queue call successful', extra=d)
        logger.warning('Locking: %s', 'get_specific_job_from_queue: attempting to retrieve lock', extra=d)
        with self.lock:
            logger.warning('Locking: %s', 'get_specific_job_from_queue: lock retrieved successful', extra=d)
            for element in range(self.r.llen('queue')):
                logger.warning('Assign Variable: %s', 'get_specific_job_from_queue: get a certain item from queue', extra=d)
                current = (self.r.lindex('queue', element)).decode("utf-8")
                logger.warning('Variable Success: %s', 'get_specific_job_from_queue: item retrieved', extra=d)

                logger.warning('Assign Variable: %s', 'get_specific_job_from_queue: load the json information', extra=d)
                info = json.loads(current)
                logger.warning('Variable Success: %s', 'get_specific_job_from_queue: json successfully loaded', extra=d)

                if job_id == info['job_id']:
                    logger.warning("Returning: %s", 'get_specific_job_from_queue: returning json information as a string', extra=d)
                    return current

            logger.warning("Returning: %s", 'get_specific_job_from_queue: returning nothing if the item wasnt found', extra=d)
            return '{"job_id":"null", "type":"none"}'

    def get_specific_job_from_queue_no_lock(self, job_id):
        """
           Gets a job from the "queue" queue using its job_id
           :param job_id: the id for the job in question
           :return: returns the job of the given job_id or '' if the job does not exist
           """

        for element in range(self.r.llen('queue')):

            logger.warning('Assign Variable: %s', 'get_specific_job_from_queue_no_lock: get a certain item from queue', extra=d)
            current = (self.r.lindex('queue', element)).decode("utf-8")
            logger.warning('Variable Success: %s', 'get_specific_job_from_queue_no_lock: item retrieved', extra=d)

            logger.warning('Assign Variable: %s', 'get_specific_job_from_queue_no_lock: load the json information', extra=d)
            info = json.loads(current)
            logger.warning('Variable Success: %s', 'get_specific_job_from_queue_no_lock: json successfully loaded', extra=d)

            if job_id == info['job_id']:
                logger.warning("Returning: %s", 'get_specific_job_from_queue_no_lock: returning json information as a string',extra=d)
                return current
        logger.warning("Returning: %s", 'get_specific_job_from_queue_no_lock: returning nothing if the item wasnt found', extra=d)
        return '{"job_id":"null", "type":"none"}'

    def does_job_exist_in_queue(self, job_id):
        """
        Verifies that a given job is in the "queue" queue exists
        :param job_id: the id for the job in question
        :return: True if the job is in the "queue", False if it is not in the "queue"
        """
        logger.warning('Call Successful: %s', 'does_job_exist_in_queue: call successful',extra=d)
        logger.warning('Locking: %s', 'does_job_exist_in_queue: attempting to retrieve lock', extra=d)
        with self.lock:
            logger.warning('Locking: %s', 'does_job_exist_in_queue: lock retrieved successful', extra=d)

            logger.warning('Assign Variable: %s', 'does_job_exist_in_queue: assign job a specific item from queue', extra=d)
            job = self.get_specific_job_from_queue_no_lock(job_id)
            logger.warning('Variable Success: %s', 'does_job_exist_in_queue: job assignment successful',extra=d)
            if job == '':
                logger.warning("Returning: %s", 'does_job_exist_in_queues: returning False if the job does not exists', extra=d)
                return False
            else:
                logger.warning("Returning: %s", 'does_job_exist_in_queue: returning True if the job exists', extra=d)
                return True

    def remove_specific_job_from_queue(self, job_id):
        """
        Removes a job from the "queue" queue
        :param job_id: the id for the job in question
        """
        logger.warning('Call Successful: %s', 'remove_specific_job_from_queue: call successful', extra=d)
        logger.warning('Locking: %s', 'remove_specific_job_from_queue: attempting to retrieve lock', extra=d)
        with self.lock:
            logger.warning('Locking: %s', 'remove_specific_job_from_queue: lock retrieved successful', extra=d)

            logger.warning('Assign Variable: %s', 'remove_specific_job_from_queue: assign job a specific item from queue',extra=d)
            job = self.get_specific_job_from_queue_no_lock(job_id)
            logger.warning('Variable Success: %s', 'remove_specific_job_from_queue: job assignment successful', extra=d)

            logger.warning('Queue Remove Attempt: %s', 'remove_specific_job_from_queue: attmept to remove item from queue',extra=d)
            self.r.lrem('queue', job, 1)

    def does_job_exist_in_progress(self, job_id):
        """
        Verifies that a given job is in the "progress" queue exists
        :param job_id: the key of the job
        :return: True if the job is in progress, False if it is not in progress
        """
        logger.warning('Call Successful: %s', 'does_job_exist_in_progress: call successful', extra=d)
        logger.warning('Locking: %s', 'does_job_exist_in_progress: attempting to retrieve lock', extra=d)
        with self.lock:
            logger.warning('Locking: %s', 'does_job_exist_in_progress: lock retrieved successful', extra=d)
            logger.warning('Assign Variable: %s', 'does_job_exist_in_progress: get the key of a job', extra=d)
            key = self.get_keys_from_progress_no_lock(job_id)
            logger.warning('Variable Success: %s', 'does_job_exist_in_progress: key has been received', extra=d)
            if float(key) > -1:
                logger.warning('Assign Variable: %s', 'does_job_exist_in_progress: attempt to get the job from the key', extra=d)
                job = self.get_specific_job_from_progress_no_lock(key)
                logger.warning('Variable Success: %s', 'does_job_exist_in_progress: job has been received from the key', extra=d)
                if job == '{"job_id":"null", "type":"none"}':
                    logger.warning("Returning: %s", 'does_job_exist_in_progress: returning False if the job does not exist', extra=d)
                    return False
                else:
                    logger.warning("Returning: %s",'does_job_exist_in_progress: returning True if the job exists', extra=d)
                    return True
        logger.warning("Returning: %s", 'does_job_exist_in_progress: returning False if the job does not exist',extra=d)
        return False

    def get_specific_job_from_progress(self, key):
        """
        Get a specific job that is in the "progress" queue
        :param key: the key of the job requested
        :return: '' if the job does not exist, otherwise returns the data for the job
        """
        logger.warning('Call Successful: %s', 'get_specific_job_from_progress: call successful', extra=d)
        logger.warning('Locking: %s', 'get_specific_job_from_progress: attempting to retrieve lock', extra=d)
        with self.lock:
            logger.warning('Locking: %s', 'get_specific_job_from_progress: lock retrieved successful', extra=d)
            logger.warning('Assign Variable: %s', 'get_specific_job_from_progress: attempt to get the job from the hash', extra=d)
            job = self.r.hget('progress', key)
            logger.warning('Variable Success %s', 'get_specific_job_from_progress: job was received from the hash', extra=d)

            if job is not None:
                logger.warning('Variable Assign: %s', 'get_specific_job_from_progress: attempt to decode the job', extra=d)
                data = job.decode("utf-8")
                logger.warning('Variable Success: %s', 'get_specific_job_from_progress: job was successfully decoded', extra=d)
                logger.warning("Returning: %s",'get_specific_job_from_progress: return the decoded job', extra=d)
                return data
            logger.warning("Returning: %s", 'get_specific_job_from_progress: returning nothing if the item wasnt found', extra=d)
            return '{"job_id":"null", "type":"none"}'

    def get_specific_job_from_progress_no_lock(self, key):
        """
        Get a specific job that is in the "progress" queue
        :param key: the key of the job requested
        :return: '' if the job does not exist, otherwise returns the data for the job
        """
        logger.warning('Call Successful: %s', 'get_specific_job_from_progress_no_lock: call successful', extra=d)
        logger.warning('Assign Variable: %s', 'get_specific_job_from_progress_no_lock: attempt to get the job from the hash',extra=d)
        job = self.r.hget('progress', key)
        logger.warning('Variable Success %s', 'get_specific_job_from_progress_no_lock: job was received from the hash', extra=d)

        if job is not None:
            logger.warning('Variable Assign: %s', 'get_specific_job_from_progress_no_lock: attempt to decode the job', extra=d)
            data = job.decode("utf-8")
            logger.warning('Variable Success: %s', 'get_specific_job_from_progress_no_lock: job was successfully decoded', extra=d)
            logger.warning("Returning: %s", 'get_specific_job_from_progress_no_lock: return the decoded job', extra=d)
            return data
        logger.warning("Returning: %s", 'get_specific_job_from_progress_no_lock: returning nothing if the item wasnt found',extra=d)
        return '{"job_id":"null", "type":"none"}'

    def get_keys_from_progress(self, job_id):
        """
        Get the key of a job that is the "progress" queue
        :param job_id: the id of the job you want to get the key for
        :return: '' if the job does not exist, or the key if the job does exist
        """
        logger.warning('Call Successful: %s', 'get_keys_from_progress: call successful', extra=d)
        logger.warning('Locking: %s', 'get_keys_from_progress: attempting to retrieve lock', extra=d)
        with self.lock:
            logger.warning('Locking: %s', 'get_keys_from_progress: lock retrieved successful', extra=d)
            logger.warning('Assign Variable: %s', 'get_keys_from_progress: get the list of keys from the progress hash', extra=d)
            key_list = self.r.hgetall('progress')
            logger.warning('Variable Success: %s', 'get_keys_from_progress: list of keys successfully received', extra=d)
            for key in key_list:
                logger.warning('Assign Variable: %s', 'get_keys_from_progress: attempt to get the json using the key', extra=d)
                json_info = self.get_specific_job_from_progress_no_lock(key)
                logger.warning('Variable Success: %s', 'get_keys_from_progress: json was received using the key', extra=d)
                logger.warning('Assign Variable: %s', 'get_keys_from_progress: load the json into a string', extra=d)
                info = literal_eval(json_info)

                logger.warning('Variable Success: %s', 'get_keys_from_progress: successfully loaded the json', extra=d)
                if info["job_id"] == job_id:
                    logger.warning('Returning: %s', 'get_keys_from_progress: return the decoded key', extra=d)
                    return key.decode("utf-8")
            logger.warning("Returning: %s",'get_keys_from_progress: returning nothing if the item wasnt found',extra=d)
            return -1

    def get_keys_from_progress_no_lock(self, job_id):
        """
        Get the key of a job that is the "progress" queue
        :param job_id: the id of the job you want to get the key for
        :return: '' if the job does not exist, or the key if the job does exist
        """
        logger.warning('Call Successful: %s', 'get_keys_from_progress_no_lock: call successful', extra=d)
        logger.warning('Assign Variable: %s', 'get_keys_from_progress_no_lock: get the list of keys from the progress hash',extra=d)
        key_list = self.r.hgetall('progress')
        logger.warning('Variable Success: %s', 'get_keys_from_progress_no_lock: list of keys successfully received', extra=d)
        for key in key_list:
            logger.warning('Assign Variable: %s', 'get_keys_from_progress_no_lock: attempt to get the json using the key',extra=d)
            json_info = self.get_specific_job_from_progress_no_lock(key)
            logger.warning('Variable Success: %s', 'get_keys_from_progress_no_lock: json was received using the key', extra=d)
            logger.warning('Assign Variable: %s', 'get_keys_from_progress_no_lock: load the json into a string', extra=d)
            logger.warning('TestPrintedJson: %s', json_info, extra=d)
            logger.warning('JsonType: %s', type(json_info), extra=d)
            info = literal_eval(json_info)
            logger.warning('Variable Success: %s', 'get_keys_from_progress_no_lock: successfully loaded the json', extra=d)
            if info["job_id"] == job_id:
                logger.warning('Returning: %s', 'get_keys_from_progress_no_lock: return the decoded key', extra=d)
                return key.decode("utf-8")
        logger.warning("Returning: %s", 'get_keys_from_progress_no_lock: returning nothing if the item wasnt found', extra=d)
        return -1

    def remove_job_from_progress(self, key):
        """
        Removes a job from the "progress" queue
        :param key: the key of the job that is to be removed
        :return: 
        """
        logger.warning('Call Successful: %s', 'remove_job_from_progress: call successful', extra=d)
        logger.warning('Locking: %s', 'remove_job_from_progress: attempting to retrieve lock', extra=d)
        with self.lock:
            logger.warning('Locking: %s', 'remove_job_from_progress: lock retrieved successful', extra=d)
            logger.warning('Queue Remove Attempt: %s', 'remove_job_from_progress: attempting to remove job from progress', extra=d)
            self.r.hdel('progress', key)

    # Combined Functions
    def renew_job(self, job_id):
        """
        Takes an expired job from the "progress" queue and adds it back into the "queue" queue. It then deletes
        the expired job from the "progress" queue
        :param job_id: the id for the job in question
        :return:
        """
        logger.warning('Call Successful: %s', 'renew_job: call successful', extra=d)
        logger.warning('Locking: %s', 'renew_job: attempting to retrieve lock', extra=d)
        with self.lock:
            logger.warning('Locking: %s', 'renew_job: lock retrieved successful', extra=d)
            logger.warning('Assign Variable: %s', 'renew_job: attempt to get the key from the job_id', extra=d)
            key = self.get_keys_from_progress_no_lock(job_id)
            if float(key) > -1:
                logger.warning('Variable Success: %s', 'renew_job: received the key', extra=d)
                logger.warning('Assign Variable: %s', 'renew_job: attempt to get a job using the key', extra=d)
                job = self.get_specific_job_from_progress_no_lock(key)
                logger.warning('Variable Success: %s', 'renew_job: successfully got the job', extra=d)
                logger.warning('Queue Add Attempt: %s', 'renew_job: attempting to add job back to queue', extra=d)
                self.r.rpush("queue", job)
                logger.warning('Queue Add Success: %s', 'renew_job: added the job back to the queue', extra=d)
                logger.warning('Queue Remove Attempt: %s', 'renew_job: remove a job from progress', extra=d)
                self.r.hdel('progress', key)


# Used to reset the locks
def reset_lock(database):
    logger.warning('Call Successful: %s', 'reset_lock: call successful', extra=d)
    logger.warning('Locking: %s', 'reset_lock: all locks have been reset', extra=d)
    redis_lock.reset_all(database)


# Sets the lock for the database
def set_lock(database):
    logger.warning('Call Successful: %s', 'set_lock: call successful', extra=d)
    logger.warning('Locking: %s', 'set_lock: lock has been sent', extra=d)
    logger.warning('Returning: %s', 'set_lock: return the set lock', extra=d)
    return redis_lock.Lock(database, "lock72")


# Returns the current time
def get_curr_time():
    logger.warning('Call Successful: %s', 'get_curr_time: call successful', extra=d)
    return float(time.time())
