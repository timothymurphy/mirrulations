import json

# General Functions
def add_job(job, Redis_Manager, queue):
    """
    Adds a job to the queue of jobs for server to provide to clients
    :param job: the job to be added
    :param Redis_Manager: database manager
    :param queue: the queue containing jobs to be completed
    :return:
    """
    Redis_Manager.rpush(queue, job)


def get_job(job_id, Redis_Manager, queue):
    """
    Selects a job from the queue by its id
    :param job_id: the id for the job in question
    :param Redis_Manager: database manager
    :param queue: the queue containing jobs to be completed
    :return:
    """

    for element in range(Redis_Manager.llen(queue)):

        current = (Redis_Manager.lindex(queue, element)).decode("utf-8")

        info = json.loads(current)

        if job_id == info['job_id']:
            return current

    return ''


# Queue Functions
def job_exists(job_id, Redis_Manager, queue):
    """
    Verifies that a given job that is to be completed exists
    :param job_id: the id for the job in question
    :param Redis_Manager: database manager
    :param queue: the queue containing jobs to be completed
    :return:
    """

    job = get_job(job_id, Redis_Manager, queue)
    if job == '':
        return False
    else:
        return True


def remove_job_queue(job_id, Redis_Manager, queue):
    """
    Removes a completed or expired job from the queue
    :param job_id: the id for the job in question
    :param Redis_Manager: database manager
    :param queue: the queue containing jobs to be completed
    :return:
    """
    job = get_job(job_id, Redis_Manager, queue)
    Redis_Manager.lrem(queue, 1, job)


# Progress Functions
def add_job_progress(job, Redis_Manager, queue, time):
    """
    TODO
    :param job:
    :param Redis_Manager:
    :param queue:
    :param time:
    :return:
    """
    Redis_Manager.hset(queue, time, job)


def job_exists_progress(key, Redis_Manager, queue):
    """

    :param key:
    :param Redis_Manager:
    :param queue:
    :return:
    """
    job = get_job_progress(key, Redis_Manager, queue)
    if job == '':
        return False
    else:
        return True


def get_job_progress(key, Redis_Manager, queue):
    """

    :param key:
    :param Redis_Manager:
    :param queue:
    :return:
    """
    job = Redis_Manager.hget(queue, key)

    if job is None:
        return ''
    else:
        data = job.decode("utf-8")
        return data


def get_key(job_id, Redis_Manager, queue):
    key_list = Redis_Manager.hgetall(queue)
    for key in key_list:
        x = get_job_progress(key, Redis_Manager, queue)
        info = json.loads(x)
        if info["job_id"] == job_id:
            return key.decode("utf-8")
    return ''


def remove_job_progress(key, Redis_Manager, queue):
    Redis_Manager.hdel(queue, key)

# Combined Functions
def renew_job(job_id, Redis_Manager):
    """
    Takes an expired job and adds it back into the job queue
    :param job_id: the id for the job in question
    :param Redis_Manager: database manager
    :return:
    """
    progress = "progress"
    queue = "queue"

    key = get_key(job_id, Redis_Manager, progress)
    job = get_job_progress(key, Redis_Manager, progress)
    job_id = json.loads(job)
    job_id = job_id['job_id']
    add_job(job, Redis_Manager, 'queue')
    remove_job_progress(key, Redis_Manager, 'progress')