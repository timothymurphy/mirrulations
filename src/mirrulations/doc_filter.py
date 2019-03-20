import os
import os.path
import tempfile
import json
import shutil
import re
import zipfile
import logging
import mirrulations_core.documents_core as dc

FORMAT = '%(asctime)-15s %(clientip)s %(user)-8s %(message)s'
logging.basicConfig(filename='doc_filter.log', format=FORMAT)
d = { 'clientip': '192.168.0.1', 'user': 'FILTERS'}
logger = logging.getLogger('tcpserver')

"""
This program does the validation of data from the doc jobs and then saves that data locally
"""


def process_doc(redis_server, json_data, compressed_file):
    """
    Main document function, called by the server to check and save document files returned from the client
    """
    logger.debug('FILTER JOB_ID: %s', 'process_doc: ' + str(json_data["job_id"]), extra=d)
    if redis_server.does_job_exist_in_progress(json_data["job_id"]) is False:
        logger.debug('Variable Failure: %s', 'process_doc: job_id does not exist in progress queue', extra=d)

    else:

        temp_directory = tempfile.mkdtemp()
        temp_directory_path = str(temp_directory + '/')

        # Unzip the zipfile and then remove the tar file and create a list of all the files in the directory
        file_list, temp_directory_path = get_file_list(compressed_file, temp_directory_path, json_data['client_id'])

        for file in file_list:
            JobNeedsRenew = check_if_document_needs_renew(file, json_data, temp_directory_path)
            if JobNeedsRenew is True:
                logger.debug('Calling Function: % s', 'process_doc: process_doc calling renew_job', extra=d)
                redis_server.renew_job(json_data)
                logger.debug('Function Successful: % s', 'process_doc: process_doc successfully called renew_job',
                             extra=d)

        else:
            save_all_files_locally(file_list, temp_directory_path)
            logger.debug('Calling Function: % s', 'process_doc: process_doc calling remove_job_from_progress', extra=d)
            remove_job_from_progress(redis_server, json_data)
            logger.debug('Function Successful: % s', 'process_doc: process_doc successfully called '
                                                     'remove_job_from_progress', extra=d)


def get_file_list(compressed_file, compressed_file_path, client_id):
    """
    Get the list of files to be processed from a compressed file
    :param compressed_file: file containing file list to be uncompressed
    :param compressed_file_path: location of the file in string form
    :param client_id: the id of the client that did the job
    :return: The list of file names in the compressed file
    """

    client_path = os.getenv("HOME") + '/client-logs/' + str(client_id) + '/'

    logger.debug('Function Successful: % s', 'get_file_list: get_file_list successfully called from process_doc',
                 extra=d)
    logger.debug('Calling Function: % s', 'get_file_list: get_file_list calling ZipFile', extra=d)

    files = zipfile.ZipFile(compressed_file, "r")

    logger.debug('Function Successful: % s', 'get_file_list: get_file_list successfully called ZipFile', extra=d)
    logger.debug('Calling Function: % s', 'get_file_list: get_file_list calling extractall', extra=d)

    files.extractall(compressed_file_path)

    logger.debug('Function Successful: % s', 'get_file_list: get_file_list successfully called extractall', extra=d)
    logger.debug('Calling Function: % s', 'get_file_list: get_file_list calling listdir', extra=d)

    file_list = os.listdir(compressed_file_path)

    logger.debug('Function Successful: % s', 'get_file_list: get_file_list successfully called listdir', extra=d)

    final_list = []
    logger.debug('Loop: %s', 'get_file_list: loop through the files', extra=d)
    for file in file_list:
        if file.startswith("doc."):
            final_list.append(file)
        elif file.endswith(".log"):
            if not os.path.exists(client_path):
                os.makedirs(client_path)
                shutil.copy(compressed_file_path + file, client_path)
            else:
                shutil.copy(compressed_file_path + file, client_path)

    logger.debug('Loop successful: %s', 'get_file_list: successfully looped through the files', extra=d)
    logger.debug('Returning: %s', 'get_file_list: returning list of files', extra=d)

    return final_list, compressed_file_path


def check_if_document_needs_renew(file, json_data, path):
    """
    Checks to see if a document conforms to our naming conventions
    """
    file_name = get_document_id(file)
    org, docket_id, document_id = dc.get_doc_attributes(file_name)

    FileStartsWithDoc = file.startswith('doc.')
    FileBeginWithDocLetter = document_id_beginning_is_letter(document_id)
    FileEndIsDocNum = document_id_ending_is_number(document_id)
    FileEndsWithJson = file.endswith('.json')
    FileJobTypeIsDoc = json_data['type'] == 'doc'

    FileCombinedCheck = FileStartsWithDoc and FileBeginWithDocLetter and FileEndIsDocNum and FileJobTypeIsDoc
    FileCombinedCheckAndJson = FileCombinedCheck and FileEndsWithJson

    if FileCombinedCheckAndJson:
        if document_id_matches_json_id(path + file, document_id):
            logger.debug('Variable Success: %s', 'process_doc: FileStartsWithDoc, FileBeginWithDocLetter, '
                                                 'FileEndIsDocNum, and FileJobTypeIsDoc are True', extra=d)
            return False
        else:
            logger.debug('Variable Failure: %s', 'process_doc: document_id_matches_json_id is False', extra=d)
            return True

    checks_names = ['FileBeginWithDocLetter', 'FileEndIsDocNum', 'FileStartsWithDoc', 'FileJobTypeIsDoc']
    checks_values = [FileBeginWithDocLetter, FileEndIsDocNum, FileStartsWithDoc, FileJobTypeIsDoc]
    dc.write_multiple_checks_into_logger(checks_names, checks_values, 'check_if_document_needs_renew')

    if FileCombinedCheck:
        return False
    else:
        return True


def get_document_id(file_name):

    logger.debug('Function Successful: % s', 'get_document_id: get_document_id successfully called from '
                                             'get_doc_attributes', extra=d)
    logger.info('Retrieving document ID...')

    doc, document_id, ending = file_name.split('.')

    logger.debug('Returning: %s', 'get_document_id: returning document_id', extra=d)
    logger.info('Document ID successfully retrieved')

    return document_id


def document_id_beginning_is_letter(document_id):

    logger.debug('Function Successful: % s', 'document_id_beginning_is_letter: document_id_beginning_is_letter '
                                             'successfully called from process_doc', extra=d)
    logger.info('Ensuring that document ID begins with a letter...')

    letter = document_id[0]
    result = letter.isalpha()
    result_name = ['result']
    result_value = [result]
    dc.write_multiple_checks_into_logger(result_name, result_value, 'document_id_beginning_is_letter')

    return result


def document_id_ending_is_number(document_id):

    logger.debug('Function Successful: % s', 'document_id_ending_is_number: document_id_ending_is_number successfully '
                                             'called from process_doc', extra=d)
    logger.info('Ensuring document ID ends in a number...')
    logger.debug('Calling Function: % s', 'document_id_ending_is_number: document_id_ending_is_number calling split',
                 extra=d)

    doc_list = re.split('-', document_id)

    logger.debug('Function Successful: % s', 'document_id_ending_is_number: document_id_ending_is_number successfully '
                                             'called split', extra=d)
    number = doc_list[-1]

    logger.debug('Returning: %s', 'document_id_ending_is_number: returning the number', extra=d)
    logger.info('The ending of the document ID is, in fact, a number')

    return number.isdigit()


def document_id_matches_json_id(path, doc_id):

    logger.debug('Function Successful: % s', 'document_id_matches_json_id: document_id_matches_json_id successfully '
                                             'called from process_doc', extra=d)
    logger.info('Ensuring that the document IDs match...')
    logger.debug('Calling Function: % s', 'document_id_matches_json_id: document_id_matches_json_id calling open',
                 extra=d)

    f = open(path, 'r')

    logger.debug('Function Successful: % s', 'document_id_matches_json_id: document_id_matches_json_id successfully '
                                             'called open', extra=d)
    logger.debug('Calling Function: % s', 'document_id_matches_json_id: document_id_matches_json_id calling load',
                 extra=d)

    j = json.load(f)

    logger.debug('Function Successful: % s', 'document_id_matches_json_id: document_id_matches_json_id successfully '
                                             'called load', extra=d)

    document_id = j['documentId']['value']
    result = document_id == doc_id

    result_name = ['result']
    result_value = [result]
    dc.write_multiple_checks_into_logger(result_name, result_value, 'document_id_matches_json_id')

    return result


def save_all_files_locally(file_list, path):

    for file in file_list:
        reg_data_path = os.getenv('HOME') + '/regulations-data/'
        file_path = path + file
        save_single_file_locally(file_path, reg_data_path)


def save_single_file_locally(current_path, destination):

    logger.debug('Function Successful: % s', 'save_single_file_locally: save_single_file_locally successfully called '
                                             'from process_doc', extra=d)
    logger.debug('Calling Function: % s', 'save_single_file_locally: save_single_file_locally calling get_file_name',
                 extra=d)

    file_name = get_file_name(current_path)

    logger.debug('Function Successful: % s', 'save_single_file_locally: save_single_file_locally successfully called '
                                             'get_file_name', extra=d)
    logger.debug('Calling Function: % s', 'save_single_file_locally: save_single_file_locally calling '
                                          'get_doc_attributes', extra=d)
    doc_id = get_document_id(file_name)
    org, docket_id, document_id = dc.get_doc_attributes(doc_id)

    logger.debug('Function Successful: % s', 'save_single_file_locally: save_single_file_locally successfully called '
                                             'get_doc_attributes', extra=d)

    destination_path = destination + org + '/' + docket_id + '/' + document_id + '/'

    logger.debug('Calling Function: % s', 'save_single_file_locally: save_single_file_locally calling '
                                          'create_new_directory_for_path', extra=d)
    create_new_directory_for_path(destination_path)

    logger.debug('Function Successful: % s', 'save_single_file_locally: save_single_file_locally successfully '
                                             'called create_new_directory_for_path', extra=d)
    logger.debug('Calling Function: % s', 'save_single_file_locally: save_single_file_locally calling copy', extra=d)

    shutil.copy(current_path, destination_path + '/' + file_name)

    logger.debug('Function Successful: % s', 'save_single_file_locally: save_single_file_locally successfully called '
                                             'copy', extra=d)


def get_file_name(file_path):

    logger.debug('Function Successful: % s', 'get_file_name: get_file_name successfully called from local_save',
                 extra=d)
    logger.info('Extracting file name...')

    split_path = file_path.split('/')
    file_name = split_path[len(split_path) - 1]

    logger.debug('Returning: %s', 'get_file_name: returning the file name', extra=d)
    logger.info('File name extracted')

    return file_name


def create_new_directory_for_path(path):

    logger.debug('Function Successful: % s', 'create_new_directory_for_path: create_new_directory_for_path '
                                             'successfully called from save_single_file_locally', extra=d)
    if not os.path.exists(path):
        logger.debug('Calling Function: % s', 'create_new_directory_for_path: create_new_directory_for_path calling '
                                              'makedirs', extra=d)
        os.makedirs(path)
        logger.debug('Function Successful: % s', 'create_new_directory_for_path: create_new_directory_for_path '
                                                 'successfully called makedirs', extra=d)


def remove_job_from_progress(redis_server, json_data):

    key = redis_server.get_keys_from_progress(json_data['job_id'])
    redis_server.remove_job_from_progress(key)
