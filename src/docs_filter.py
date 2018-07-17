import json
import redis
import re

import redis_manager as fr


"""
This program does the validation and assimilation of data for the documents jobs
"""


# Validation Functions
def file_length_checker(file_name):
    """
    Checks the length of the file returned
    :param file_name: path of the file to be checked
    :return:
    """
    result = open(file_name, "r")
    file_count = 0
    attachment_count = 0
    info = json.load(result)
    for workfile in info["data"]:
        for line in workfile:
            file_count += 1
            attachment_count += line["count"]
        if file_count > 1000 or attachment_count > 1000:
            return False
        else:
            file_count = 0
            attachment_count = 0
    return True


def documents_checker(path):
    """
    Checks the names of the files returned from the documents jobs
    :param path: location of the results files from the job
    :return:
    """

    result = open(path, "r")
    info = json.load(result)
    job_id = info["job_id"]
    job_type = info["job_type"] == "documents"

    return job_exists(job_id) and job_type


def job_exists(job_id):
    """
    Returns whether or not a job_id is in the "In progress" queue TODO
    :param job_id:
    :return:
    """

    list = fr.get(fr, "progress")

    return job_id in list


def renew_job(job_id):
    """
    TODO
    :param job_id:
    :return:
    """
    pass


# Assimilation Functions
def documents_job(path):
    """
    TODO
    This reads the file given at path
    Makes a list of all document ids
    Builds a job from the document ids
    :param path: location of the file which contains the document ids
    :return:
    """
    result = open(path, "r")
    info = json.load(result)
    for workfile in info["data"]:
        fr.rpush(fr, "queued", workfile)


# Final Function
def process_docs(data):

    if file_length_checker(data) and documents_checker(data):
        documents_job(data)

    else:
        result = open(data, "r")
        info = json.load(result)
        job_id = info["job_id"]
        renew_job(job_id)



