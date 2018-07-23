import random
import json
import redis
import string
import logging
from redis_manager import RedisManager

FORMAT = '%(asctime)-15s %(clientip)s %(user)-8s %(message)s'
logging.basicConfig(filename='example.log', format=FORMAT)
d = { 'clientip': '192.168.0.1', 'user': 'FILTERS'}
logger = logging.getLogger('tcpserver')

r = RedisManager(redis.Redis())

"""
This program does the validation of data for the docs jobs and then creates doc jobs using that data
"""


# Validation Functions
def work_file_length_checker(json_data):
    """
    Checks the length of each workfile and the attachment count of each workfile
    :param json_data: the json containing the work files
    :return: True if there are 1000 or less document ids and 1000 or less attachments per workfile
             False if either the ids or attachments are over 1000
    """

    logger.warning('Function Successful: % s',
                   'work_file_length_checker: work_file_length_checker successfully called from process_docs', extra=d)

    file_count = 0
    attachment_count = 0
    for workfile in json_data["data"]:
        for line in workfile:
            file_count += 1
            attachment_count += line["count"]

        fc = file_count > 1000
        ac = attachment_count > 1000
        if fc or ac:

            logger.warning('Variable Failure: %s',
                           'work_file_length_checker: Something went wrong in work_file_length_checker', extra=d)
            if fc is False:
                logger.warning('Variable Failure: %s',
                               'work_file_length_checker: fc is False', extra=d)
            else:
                logger.warning('Variable Success: %s',
                               'work_file_length_checker: fc is True', extra=d)
            if ac is False:
                logger.warning('Variable Failure: %s',
                               'work_file_length_checker: ac is False', extra=d)
            else:
                logger.warning('Variable Success: %s',
                               'work_file_length_checker: ac is True', extra=d)

            logger.warning('Returning: %s',
                           'work_file_length_checker: returning False', extra=d)
            return False
        else:
            logger.warning('Variable Success: %s',
                           'work_file_length_checker: fc and ac are True', extra=d)
            file_count = 0
            attachment_count = 0
    logger.warning('Returning: %s',
                   'work_file_length_checker: returning True', extra=d)
    return True


# Assimilation Functions
def add_document_job(json_data):
    """
    Creates a job for each workfile and then adds each to the "queue"
    :param json_data: the json data containing all the workfiles
    :return:
    """
    logger.warning('Function Successful: % s',
                   'add_document_job: add_document_job successfully called from process_docs', extra=d)
    for workfile in json_data["data"]:
        random_id = ''.join(random.choices(string.ascii_letters + string.digits, k=16))

        logger.warning('Calling Function: % s',
                       'add_document_job: add_document_job calling create_document_job', extra=d)
        job = create_document_job(workfile, random_id)
        logger.warning('Function Successful: % s',
                       'add_document_job: successfully add_document_job called create_document_job', extra=d)

        logger.warning('Calling Function: % s',
                       'add_document_job: add_document_job calling add_to_queue', extra=d)
        r.add_to_queue(job)
        logger.warning('Function Successful: % s',
                       'add_document_job: successfully add_document_job called add_to_queue', extra=d)


def create_document_job(workfile, job_id):
    """
    Creates a job for the server to provide to clients
    :param workfile: The list of ids for the clients to retrieve
    :param job_id: The id for the job
    :return: A dictionary in the form of a json
    """
    logger.warning('Function Successful: % s',
                   'create_document_job: create_document_job successfully called from add_document_job', extra=d)
    dict = {"job_id": job_id, "job_type": "doc", "data": workfile, "version": "1.0"}
    logger.warning('Returning: %s',
                   'create_document_job: returning a json dictionary', extra=d)
    return json.dumps(dict)


# Final Function
def process_docs(json_data):
    """
    Main documents function, called by the server to compile list of document jobs and add them to the "queue" queue
    :param json_data: the json data for the jobs
    :return:
    """
    logger.warning('Function Successful: % s',
                   'process_docs: process_docs successfully called from return_docs', extra=d)

    if r.does_job_exist_in_progress(json_data["job_id"]) is False:

        logger.warning('Variable Failure: %s',
                       'process_docs: job_id does not exist in progress queue', extra=d)

    else:

        logger.warning('Variable Success: %s',
                       'process_docs: job does exist in progress queue', extra=d)

        logger.warning('Calling Function: % s',
                       'process_docs: process_docs calling work_file_length_checker', extra=d)
        wklc = work_file_length_checker(json_data)
        logger.warning('Function Successful: % s',
                       'process_docs: process_docs successfully called work_file_length_checker', extra=d)

        job_type = json_data["job_type"] == "docs"

        if wklc and job_type:

            logger.warning('Calling Function: % s',
                           'process_docs: process_docs calling add_document_job', extra=d)
            add_document_job(json_data)
            logger.warning('Function Successful: % s',
                           'process_docs: process_docs successfully called add_document_job', extra=d)

            logger.warning('Calling Function: % s',
                           'process_docs: process_docs calling get_keys_from_progress', extra=d)
            key = r.get_keys_from_progress(json_data["job_id"])
            logger.warning('Function Successful: % s',
                           'process_docs: process_docs successfully called get_keys_from_progress', extra=d)

            logger.warning('Calling Function: % s',
                           'process_docs: process_docs calling remove_job_from_progress', extra=d)
            r.remove_job_from_progress(key)
            logger.warning('Function Successful: % s',
                           'process_docs: process_docs successfully called remove_job_from_progress', extra=d)

        else:
            logger.warning('Variable Failure: %s',
                           'process_docs: Something went wrong in validation', extra=d)
            if wklc is False:
                logger.warning('Variable Failure: %s',
                               'process_docs: work_file_length_checker is False', extra=d)
            else:
                logger.warning('Variable Success: %s',
                               'process_docs: work_file_length_checker is True', extra=d)
            if job_type is False:
                logger.warning('Variable Failure: %s',
                               'process_docs: job_type is not docs', extra=d)
            else:
                logger.warning('Variable Success: %s',
                               'process_docs: job_type is docs', extra=d)

            logger.warning('Calling Function: % s',
                           'process_docs: process_docs calling renew_job', extra=d)
            r.renew_job(json_data["job_id"])
            logger.warning('Function Successful: % s',
                           'process_docs: process_docs successfully called renew_job', extra=d)
