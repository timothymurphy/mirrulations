"""This is the document filter used to process all document jobs"""
import os
import os.path
import tempfile
import json
import shutil
import re
import zipfile
from mirrulations.mirrulations_logging import logger
import mirrulations_core.documents_core as dc

"""
This program does the validation of data from the doc jobs and then saves that data locally
"""


def process_doc(redis_server, json_data, compressed_file):
    """
    Main document function, called by the server to check and
    save document files returned from the client
    """
    if redis_server.does_job_exist_in_progress(json_data['job_id']):

        temp_directory = tempfile.mkdtemp()
        temp_directory_path = str(temp_directory + '/')

        # Unzip the zipfile and then remove the tar file
        # and create a list of all the files in the directory
        file_list, temp_directory_path = get_file_list(compressed_file,
                                                       temp_directory_path,
                                                       json_data['client_id'])
        break_check = False
        for file in file_list:
            job_needs_renew = check_if_document_needs_renew(file, json_data, temp_directory_path)
            if job_needs_renew is True:
                redis_server.renew_job(json_data)
                break_check = True
                break
        if break_check is False:
            save_all_files_locally(file_list, temp_directory_path)
            remove_job_from_progress(redis_server, json_data)


def get_file_list(compressed_file, compressed_file_path, client_id):
    """
    Get the list of files to be processed from a compressed file
    :param compressed_file: file containing file list to be uncompressed
    :param compressed_file_path: location of the file in string form
    :param client_id: the id of the client that did the job
    :return: The list of file names in the compressed file
    """
    client_path = os.getenv("HOME") + '/client-logs/' + str(client_id) + '/'
    files = zipfile.ZipFile(compressed_file, 'r')
    files.extractall(compressed_file_path)

    file_list = os.listdir(compressed_file_path)

    final_list = []
    for file in file_list:
        if file.startswith('doc.'):
            final_list.append(file)
        elif file.endswith('.log'):
            if not os.path.exists(client_path):
                os.makedirs(client_path)
                shutil.copy(compressed_file_path + file, client_path)
            else:
                shutil.copy(compressed_file_path + file, client_path)


def ending_is_number(document_id):
    """
    Ensure that the document id ends in a number
    :param document_id: the document id being checked
    :return: True if the number is a digit, else it will return False
    """
    list = re.split("-", document_id)
    number = list[-1]
    return number.isdigit()


def check_if_document_needs_renew(file, json_data, path):
    """
    Checks to see if a document conforms to our naming conventions
    """
    file_name = get_document_id(file)
    document_id = dc.get_doc_attributes(file_name)[2]

    file_starts_with_doc = file.startswith('doc.')
    file_begin_with_doc_letter = document_id_beginning_is_letter(document_id)
    file_end_is_doc_num = document_id_ending_is_number(document_id)
    file_ends_with_json = file.endswith('.json')
    file_job_type_is_doc = json_data['type'] == 'doc'

    file_combined_check = file_starts_with_doc and file_begin_with_doc_letter and \
                          file_end_is_doc_num and file_job_type_is_doc
    file_combined_check_and_json = file_combined_check and file_ends_with_json

    if file_combined_check_and_json:
        if document_id_matches_json_id(path + file, document_id):
            return False
        return True

    if file_combined_check:
        return False
    return True


def get_document_id(file_name):
    """
    :param file_name:
    :return:
    """
    document_id = file_name.split('.')[1]
    return document_id


def document_id_beginning_is_letter(document_id):
    """
    :param document_id:
    :return:
    """
    letter = document_id[0]

    result = letter.isalpha()
    if result is True:
        return True
    else:
        logger.warning('Document ID does not begin with a letter')
        return False


def document_id_ending_is_number(document_id):
    """
    :param document_id:
    :return:
    """
    doc_list = re.split('-', document_id)
    number = doc_list[-1]
    return number.isdigit()


def document_id_matches_json_id(path, doc_id):
    """
    :param path:
    :param doc_id:
    :return:
    """
    file = open(path, 'r')

    if not os.path.exists(path):
        os.makedirs(path)

    j = json.load(file)

    document_id = j['documentId']['value']
    result = document_id == doc_id

    return result


def get_file_list(compressed_file, PATHstr, client_id):
    """
    Get the list of files to be processed from a compressed file
    :param compressed_file: file containing file list to be uncompressed
    :param PATHstr: location of the file in string form
    :param client_id: the id of the client that did the job
    :return: The list of file names in the compressed file
    """
    home = os.getenv("HOME")
    client_path = home + '/client-logs/' + str(client_id) + '/'
    files = zipfile.ZipFile(compressed_file, "r")
    files.extractall(PATHstr)
    # Create a list of all the files in the directory
    file_list = os.listdir(PATHstr)

    final_list = []
    for file in file_list:
        if file.startswith("doc."):
            final_list.append(file)
        elif file.endswith(".log"):
            if not os.path.exists(client_path):
                os.makedirs(client_path)
                shutil.copy(PATHstr + file, client_path)
            else:
                shutil.copy(PATHstr + file, client_path)

    return final_list, PATHstr


def save_all_files_locally(file_list, path):
    """
    :param file_list:
    :param path:
    :return:
    """
    for file in file_list:
        reg_data_path = os.getenv('HOME') + '/regulations-data/'
        file_path = path + file
        save_single_file_locally(file_path, reg_data_path)


def save_single_file_locally(current_path, destination):
    """
    :param current_path:
    :param destination:
    :return:
    """
    file_name = get_file_name(current_path)
    doc_id = get_document_id(file_name)
    org, docket_id, document_id = dc.get_doc_attributes(doc_id)
    destination_path = destination + org + "/" + docket_id + "/" + document_id + "/"
    create_new_directory_for_path(destination_path)
    shutil.copy(current_path, destination_path + '/' + file_name)


def check_single_document(file, json_data, path):
    """
    Checks to see if a document conforms to our naming conventions
    :param file:
    :param json_data:
    :param path:
    :return:
    """
    org, docket_id, document_id = dc.get_doc_attributes(file)
    ifFileStartsWithDoc = file.startswith("doc.")
    ifBeginWithDocLetter = document_id_beginning_is_letter(document_id)
    ifEndIsDocNum = ending_is_number(document_id)
    ifFileEndsWithJson = file.endswith(".json")
    job_type = json_data["type"] == "doc"
    ifDocumentsChecks = ifFileStartsWithDoc and ifBeginWithDocLetter and ifEndIsDocNum and job_type
    ifDocumentsChecksAndJson = ifDocumentsChecks and ifFileEndsWithJson

    if ifDocumentsChecksAndJson:
        return True

def get_file_name(file_path):
    """
    :param file_path:
    :return:
    """
    split_path = file_path.split('/')
    file_name = split_path[len(split_path) - 1]
    return file_name


def create_new_directory_for_path(path):
    """
    :param path:
    :return:
    """
    if not os.path.exists(path):
        os.makedirs(path)


def remove_job_from_progress(redis_server, json_data):
    """
    :param redis_server:
    :param json_data:
    :return:
    """
    key = redis_server.get_keys_from_progress(json_data['job_id'])
    redis_server.remove_job_from_progress(key)
