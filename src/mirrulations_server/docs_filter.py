import json
import os
import random
import shutil
import string
import tempfile
import zipfile

import mirrulations_core.documents_core as dc
from mirrulations_core.mirrulations_logging import logger

"""
This program does the validation of data from the docs jobs and then creates doc jobs using that data
"""
VERSION = 'v1.3'


# Validation Function
def work_file_length_checker(json_data):
    """
        Checks the file count and attachment count of each work file
        :param json_data: the json containing the work files
        :return: True if there are 1000 or less document ids and 1000 or less attachments per work file
                 False if either the ids or attachments are over 1000
        """
    file_count = 0
    attachment_count = 0
    for work_file in json_data["data"]:
        for line in work_file:
            file_count += 1
            attachment_count += line["count"]

        fc = file_count > 1000
        ac = attachment_count > 1000
        if fc or ac:
            return False
        else:
            file_count = 0
            attachment_count = 0
    logger.warning('Workfile length check completed')
    return True


def check_document_exists(json_data):
    """
    Checks to see if a document was already downloaded or already in one of the queues.
    If the document has already been downloaded it will be removed from its work_file.
    If a work_file were to become empty it will be removed to prevent empty doc jobs from existing.
    :param json_data: the json containing the work files
    :return:
    """
    logger.warning('Function Successful: % s',
                   'work_file_length_checker: work_file_length_checker successfully called from process_docs')

    home = os.getenv("HOME")
    path = home + "/regulations_data/"
    for work_file in json_data["data"]:
        count = 0
        for line in work_file:
            document = line["id"]
            alpha_doc_org, docket_id, document_id = dc.get_doc_attributes("doc." + document + ".json")
            full_path = path + alpha_doc_org + "/" + docket_id + "/" + document_id + "/" + "doc." + document + ".json"

            count, local_verdict = local_files_check(full_path, count)

            if local_verdict:  # and redis_verdict:
                work_file.pop(count)

    json_data = remove_empty_lists(json_data)
    return json_data


def local_files_check(full_path, count):
    """
    Checks to see if the document exists.
    If the document does not, then the counter is increased
    If the document does exist, the workfile will remove the document
    :param full_path: The path to the document.json
    :param count: The current count of the workfile
    :return: Returns the count and True if the file does exist, else it will return False
    """
    if os.path.isfile(full_path):
        return count, True
    else:
        count += 1
        return count, False


def remove_empty_lists(json_data):
    """
    Removes any empty workfiles from the data field in the json data
    :param json_data: The json data being looked over
    :return: Returns the empty free json data
    """
    json_data["data"] = [workfile for workfile in json_data["data"] if workfile != []]
    return json_data


# Saving and Adding Functions
def add_document_job(redis_server, json_data):
    """
    Creates a job for each work file and then adds each job to the "queue"
    :param json_data: the json data containing all the work files
    :return:
    """
    logger.warning('Adding document job to the queue...')

    for work_file in json_data["data"]:
        random_id = ''.join(random.choices(string.ascii_letters + string.digits, k=16))

        job = create_document_job(work_file, random_id)
        redis_server.add_to_queue(job)
        logger.warning('Document job successfully added to queue')


def create_document_job(work_file, job_id):
    """
    Creates a job for the server to provide to clients
    :param work_file: The list of ids for the clients to retrieve
    :param job_id: The id for the job
    :return: A json in the form of a dictionary
    """
    logger.warning('Creating document job...')

    return json.dumps({"job_id": job_id, "type": "doc", "data": work_file, "version": VERSION})


def save_client_log(client_id, compressed_file):
    """
    Save the client log to the home directory of the server
    :param client_id: the id of the client that did the job
    :param compressed_file: the compressed file containing the client log
    :return:
    """
    home = os.getenv("HOME")
    client_path = home + '/client-logs/' + str(client_id) + '/'

    files = zipfile.ZipFile(compressed_file, "r")
    path = tempfile.mkdtemp()
    path_string = str(path + "/")
    files.extractall(path_string)

    # Create a list of all the files in the directory
    file_list = os.listdir(path_string)

    for file in file_list:
        if file.endswith(".log"):
            if not os.path.exists(client_path):
                os.makedirs(client_path)
                shutil.copy(path_string + file, client_path)
            else:
                shutil.copy(path_string + file, client_path)


# Final Function
def process_docs(redis_server, json_data, compressed_file):
    """
    Main documents function, called by the server to compile list of document jobs and add them to the "queue" queue
    :param json_data: the json data for the jobs
    :param compressed_file: the zipfile containing the client's log
    :return:
    """
    if redis_server.does_job_exist_in_progress(json_data["job_id"]):
        save_client_log(json_data['client_id'], compressed_file)
        wklc = work_file_length_checker(json_data)
        job_type = json_data["type"] == "docs"
        if wklc and job_type:
            json_data = check_document_exists(json_data)
            add_document_job(redis_server, json_data)
            key = redis_server.get_keys_from_progress(json_data["job_id"])
            redis_server.remove_job_from_progress(key)
        else:
            redis_server.renew_job(json_data["job_id"])
