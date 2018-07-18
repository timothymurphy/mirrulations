import random
import json
import shared_filter_functions as sff

"""
This program does the validation and assimilation of data for the documents jobs
"""


# Validation Functions
def file_length_checker(json_data):
    """
    Checks the length of the file returned
    :param json_data: path of the file to be checked
    :return:
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
def documents_job(json_data, Redis_Manager):
    """
    Processes documents file and add ids to each document within
    :param json_data: the json data for the jobs
    :param Redis_Manager: database manager
    :return:
    """
    for workfile in json_data["data"]:
        job_id = str(random.randint(0,1000000000))
        job = create_job(workfile, job_id)
        sff.add_job(job, Redis_Manager, "queued")


def create_job(workfile, job_id):
    """
    Creates a job for the server to provide to clients
    :param workfile: the job to be created and eventually completed
    :param job_id: the id for the job
    :return:
    """
    dict = {"job_id": job_id, "job_type": "documents", "data": workfile, "version": "1.0"}
    return json.dumps(dict)


# Final Function
def process_docs(tup, Redis_Manager):
    """
    Main docs function, called by the server to compile list of document jobs
    :param json_data: the json data for the jobs
    :param Redis_Manager: database manager
    :return:
    """

    json_data = tup[0]

    if sff.job_exists(json_data["job_id"], Redis_Manager, "progress") is False:
        pass

    else:
        if file_length_checker(json_data) and json_data["job_type"] == "documents":
            documents_job(json_data, Redis_Manager)
            key = sff.get_key_hash(json_data["job_id"], Redis_Manager, "progress")
            sff.remove_job_progress(key, Redis_Manager, "progress")

        else:
            sff.renew_job(json_data, Redis_Manager)



