import json


def add_job(job, Redis_Manager, queue):
    Redis_Manager.rpush(queue, job)


def job_exists(job_id, Redis_Manager, queue):
    """
    Returns whether or not a job_id is in the "In progress" queue
    :param job_id:
    :return:
    """

    job = get_job(job_id, Redis_Manager, queue)
    if job == '':
        return False
    else:
        return True


def get_job(job_id, Redis_Manager, queue):

    for element in range(Redis_Manager.llen(queue)):

        current = (Redis_Manager.lindex(queue, element)).decode("utf-8")

        info = json.loads(current)

        if job_id == info['job_id']:
            return current

    return ''


def remove_job(job_id, Redis_Manager, queue):
    job = get_job(job_id, Redis_Manager, queue)
    Redis_Manager.lrem(queue, 1, job)


def renew_job(job_id, Redis_Manager):
    """
    Put the job with the matching id into the "queue" and then remove the job_id from "progress"
    :param job_id:
    :return:
    """
    job = get_job(job_id, Redis_Manager, 'progress')
    job_id = json.loads(job)
    job_id = job_id['job_id']
    add_job(job, Redis_Manager, 'queue')
    remove_job(job_id, Redis_Manager, 'progress')