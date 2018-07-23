#!/usr/bin/env python
import os, os.path, tempfile, json, shutil, re, zipfile
import redis
import logging
from redis_manager import RedisManager

FORMAT = '%(asctime)-15s %(clientip)s %(user)-8s %(message)s'
logging.basicConfig(filename='example.log', format=FORMAT)
d = { 'clientip': '192.168.0.1', 'user': 'FILTERS'}
logger = logging.getLogger('tcpserver')

r = RedisManager(redis.Redis())

"""
This program does the validation of data for the doc jobs and then saves that data locally
"""


# General Functions
def get_document_id(file_name):
    """
    Extract the document id from the file name
    :param file_name: name of the file that the id will be extracted from
    :return id: the string of the document id from the file name
    """
    logger.warning('Function Successful: % s',
                   'get_document_id: get_document_id successfully called from get_doc_attributes', extra=d)
    doc,id,ending = file_name.split(".")
    logger.warning('Returning: %s',
                   'get_document_id: returning document_id', extra=d)
    return id


def get_file_name(path):
    """
    Extracts the name of the file from the given path
    :param path: location of the file in which the name will be extracted from
    :return: file_name: The file name from the path
    """
    logger.warning('Function Successful: % s',
                   'get_file_name: get_file_name successfully called from local_save', extra=d)
    split_path = path.split("/")
    file_name = split_path[len(split_path) - 1]
    logger.warning('Returning: %s',
                   'get_file_name: returning the file name', extra=d)
    return file_name


def get_doc_attributes(file_name):
    """
    Get the organization(s), the docket_id and the document_id from a file name
    :param file_name: name of the file to extract attributes of the document name
    :return: orgs: The organizations(s),
             docket_id: the docket_id,
             document_id: the document_id
    """
    document_id = get_document_id(file_name)

    if "_" in document_id:
        split_name = re.split("[-_]", document_id)
        org = split_name[0] + "_" + split_name[1]
        docket_id = org + "_" + split_name[2]
        document_id = docket_id + "-" + split_name[3]
        return org, docket_id, document_id

    else:
        split_name = re.split("[-]", document_id)
        length = len(split_name)
        count = 0
        for x in range(length):
            if split_name[x].isdigit():
                break
            else:
                count += 1

        org_list = split_name[:count]
        org_list.sort()
        org = add_hyphens(org_list)
        docket_id = add_hyphens(split_name[:len(split_name) - 1])
        document_id = add_hyphens(split_name[:len(split_name)])

        return org,docket_id,document_id


def add_hyphens(list):
    """
    Adds hyphens between the list of strings passed
    :param list: the list to be hyphenated
    :return: A string of the list with hyphens in-between
    """
    hyphened_string = ""
    for x in range(len(list)):

        if x == 0:
            if len(list) == 1:
                hyphened_string = list[x]
            else:
                hyphened_string = list[x] + "-"

        elif x == len(list) - 1:
            hyphened_string = hyphened_string + list[x]

        else:
            hyphened_string = hyphened_string + list[x] + "-"

    return hyphened_string


# Validation Functions
def ending_is_number(document_id):
    """
    Ensure that the document id ends in a number
    :param document_id: the document id being checked
    :return:
    """
    list = re.split("-", document_id)
    number = list[-1]
    return number.isdigit()


def id_matches(path, doc_id):
    """
    Ensures that the ids of the documents match correctly
    :param path: the file that is being looked at
    :param doc_id: the document id to check
    :return:
    """
    f = open(path, "r")
    j = json.load(f)

    document_id = j["documentId"]["value"]

    return document_id == doc_id


def beginning_is_letter(document_id):
    """
    Ensures that the beginning of the document id begins with a letter
    :param document_id: the document id being checked
    :return:
    """
    letter = document_id[0]
    return letter.isalpha()


# Saving Functions
def local_save(cur_path, destination):
    """
    Save the file located at the current path to the destination location
    :param cur_path: location of the file to be saved
    :param destination: location that the file should be saved
    :return:
    """
    file_name = get_file_name(cur_path)
    org, docket_id, document_id = get_doc_attributes(file_name)
    destination_path = destination + org + "/" + docket_id + "/" + document_id + "/"
    create_new_dir(destination_path)
    shutil.copy(cur_path, destination_path + '/' + file_name)


def create_new_dir(path):
    """
    If the path does not exist, create the directory
    :param path: the path to the directory to be created
    :return:
    """
    if not os.path.exists(path):
        os.makedirs(path)


def get_file_list(compressed_file, PATHstr):
    """
    Get the list of files to be processed from a compressed file
    :param compressed_file: file containing file list to be uncompressed
    :param PATHstr: location of the file in string form
    :return: The list of file names in the compressed file
    """
    files = zipfile.ZipFile(compressed_file, "r")
    files.extractall(PATHstr)

    # Create a list of all the files in the directory
    file_list = os.listdir(PATHstr)

    final_list = []
    for file in file_list:
        if file.startswith("doc."):
            final_list.append(file)

    return final_list


# Final Function
def process_doc(json_data, compressed_file):
    """
    Main document function, called by the server to check and save document files returned from the client
    :param json_data: json data of the job
    :param compressed_file: compressed file of document data
    :return:
    """

    if r.does_job_exist_in_progress(json_data["job_id"]) is False:
        pass

    else:

        PATH = tempfile.mkdtemp()
        PATHstr = str(PATH)

        # Unzip the zipfile and then remove the tar file and create a list of all the files in the directory
        file_list = get_file_list(compressed_file, PATHstr)

        renew = False
        for file in file_list:
            org, docket_id, document_id = get_doc_attributes(file)

            fsw = file.startswith("doc.")
            bil = beginning_is_letter(document_id)
            ein = ending_is_number(document_id)
            few = file.endswith(".json")
            job_type = json_data["job_type"] == "doc"

            if fsw and bil and ein and few and job_type:
                if id_matches(file, document_id):
                    pass
                else:
                    renew = True
                    break

            elif fsw and bil and ein and job_type:
                    pass
            else:
                renew = True
                break

        if renew is True:
            r.renew_job(json_data)

        else:
            for file in file_list:
                local_save(PATHstr + "/" + file, "~/regulations-data/")
            key = r.get_keys_from_progress(json_data["job_id"])
            r.remove_job_from_progress(key)
