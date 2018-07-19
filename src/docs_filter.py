import random
import json
import redis
from redis_manager import RedisManager
r = RedisManager(redis.Redis())

"""
This program does the validation of data for the documents jobs and then creates document jobs using that data
"""


# Validation Functions
def work_file_length_checker(json_data):
    """
    Checks the length of each workfile and the attachment count of each workfile
    :param json_data: the json containing the work files
    :return: True if there are 1000 or less document ids and 1000 or less attachments per workfile
             False if either the ids or attachments are over 1000
    """
    file_count = 0
    attachment_count = 0
    for workfile in json_data["data"]:
        for line in workfile:
            file_count += 1
            attachment_count += line["count"]
        if file_count > 1000 or attachment_count > 1000:
            return False
        else:
            file_count = 0
            attachment_count = 0
    return True


# Assimilation Functions
def add_document_job(json_data):
    """
    Creates a job for each workfile and then adds each to the "queue"
    :param json_data: the json data containing all the workfiles
    :param Redis_Manager: database manager
    :return:
    """
    for workfile in json_data["data"]:
        job_id = str(random.randint(0,1000000000))
        job = create_document_job(workfile, job_id)
        r.add_to_queue(job)


def create_document_job(workfile, job_id):
    """
    Creates a job for the server to provide to clients
    :param workfile: The list of ids for the clients to retrieve
    :param job_id: The id for the job
    :return: A dictionary in the form of a json
    """
    dict = {"job_id": job_id, "job_type": "document", "data": workfile, "version": "1.0"}
    return json.dumps(dict)


# Final Function
def process_docs(json_data, Redis_Manager):
    """
    Main documents function, called by the server to compile list of document jobs and add them to the "queue"
    :param json_data: the json data for the jobs
    :param Redis_Manager: database manager
    :return:
    """

    if r.does_job_exist_in_progress(json_data["job_id"]) is False:
        pass

    else:
        if work_file_length_checker(json_data) and json_data["job_type"] == "documents":
            add_document_job(json_data, Redis_Manager)
            key = r.get_keys_from_progress(json_data["job_id"])
            r.remove_job_from_progress(key)

        else:
            r.renew_job(json_data["job_id"])



