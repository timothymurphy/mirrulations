"""This is the document filter used to process all document jobs"""
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
D = {'clientip': '192.168.0.1', 'user': 'FILTERS'}
LOGGER = logging.getLogger('tcpserver')

"""
This program does the validation of data from the doc jobs and then saves that data locally
"""


def process_doc(redis_server, json_data, compressed_file):
    """
    Main document function, called by the server to check and
    save document files returned from the client
    """
    LOGGER.debug('FILTER JOB_ID: %s', 'process_doc: ' + str(json_data['job_id']), extra=D)
    if redis_server.does_job_exist_in_progress(json_data['job_id']) is False:
        LOGGER.debug('Variable Failure: %s', 'process_doc: '
                     'job_id does not exist in progress queue', extra=D)
    else:
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
                LOGGER.debug('Calling Function: % s', 'process_doc: '
                             'process_doc calling renew_job', extra=D)
                redis_server.renew_job(json_data)
                LOGGER.debug('Function Successful: % s', 'process_doc: '
                             'process_doc successfully called renew_job',
                             extra=D)
                break_check = True
                break
        if break_check is True:
            pass
        else:
            save_all_files_locally(file_list, temp_directory_path)
            LOGGER.debug('Calling Function: % s', 'process_doc: '
                         'process_doc calling remove_job_from_progress', extra=D)
            remove_job_from_progress(redis_server, json_data)
            LOGGER.debug('Function Successful: % s', 'process_doc: '
                         'process_doc successfully called remove_job_from_progress', extra=D)


def get_file_list(compressed_file, compressed_file_path, client_id):
    """
    Get the list of files to be processed from a compressed file
    :param compressed_file: file containing file list to be uncompressed
    :param compressed_file_path: location of the file in string form
    :param client_id: the id of the client that did the job
    :return: The list of file names in the compressed file
    """

    client_path = os.getenv("HOME") + '/client-logs/' + str(client_id) + '/'

    LOGGER.debug('Function Successful: % s', 'get_file_list: '
                 'get_file_list successfully called from process_doc', extra=D)
    LOGGER.debug('Calling Function: % s', 'get_file_list: '
                 'get_file_list calling ZipFile', extra=D)

    files = zipfile.ZipFile(compressed_file, 'r')

    LOGGER.debug('Function Successful: % s', 'get_file_list: '
                 'get_file_list successfully called ZipFile', extra=D)
    LOGGER.debug('Calling Function: % s', 'get_file_list: '
                 'get_file_list calling extractall', extra=D)

    files.extractall(compressed_file_path)

    LOGGER.debug('Function Successful: % s', 'get_file_list: '
                 'get_file_list successfully called extractall', extra=D)
    LOGGER.debug('Calling Function: % s', 'get_file_list: '
                 'get_file_list calling listdir', extra=D)

    file_list = os.listdir(compressed_file_path)

    LOGGER.debug('Function Successful: % s', 'get_file_list: '
                 'get_file_list successfully called listdir', extra=D)

    final_list = []
    LOGGER.debug('Loop: %s', 'get_file_list: loop through the files', extra=D)
    for file in file_list:
        if file.startswith('doc.'):
            final_list.append(file)
        elif file.endswith('.log'):
            if not os.path.exists(client_path):
                os.makedirs(client_path)
                shutil.copy(compressed_file_path + file, client_path)
            else:
                shutil.copy(compressed_file_path + file, client_path)

    LOGGER.debug('Loop successful: %s', 'get_file_list: '
                 'successfully looped through the files', extra=D)
    LOGGER.debug('Returning: %s', 'get_file_list: returning list of files', extra=D)

    return final_list, compressed_file_path


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
            LOGGER.debug('Variable Success: %s', 'process_doc: '
                         'file_starts_with_doc, file_begin_with_doc_letter, '
                         'file_end_is_doc_num, and file_job_type_is_doc are True', extra=D)
            return False
        LOGGER.debug('Variable Failure: %s', 'process_doc: '
                     'document_id_matches_json_id is False', extra=D)
        return True

    checks_names = ['file_begin_with_doc_letter', 'file_end_is_doc_num',
                    'file_starts_with_doc', 'file_job_type_is_doc']
    checks_values = [file_begin_with_doc_letter, file_end_is_doc_num,
                     file_starts_with_doc, file_job_type_is_doc]
    dc.write_multiple_checks_into_logger(checks_names, checks_values,
                                         'check_if_document_needs_renew')
    if file_combined_check:
        return False
    return True


def get_document_id(file_name):
    """
    :param file_name:
    :return:
    """
    LOGGER.debug('Function Successful: % s', 'get_document_id: '
                 'get_document_id successfully called from get_doc_attributes', extra=D)
    LOGGER.info('Retrieving document ID...')
    document_id = file_name.split('.')[1]
    LOGGER.debug('Returning: %s', 'get_document_id: returning document_id', extra=D)
    LOGGER.info('Document ID successfully retrieved')

    return document_id


def document_id_beginning_is_letter(document_id):
    """
    :param document_id:
    :return:
    """
    LOGGER.debug('Function Successful: % s', 'document_id_beginning_is_letter: '
                 'document_id_beginning_is_letter successfully called from process_doc', extra=D)
    LOGGER.info('Ensuring that document ID begins with a letter...')

    letter = document_id[0]
    result = letter.isalpha()
    result_name = ['result']
    result_value = [result]
    dc.write_multiple_checks_into_logger(result_name,
                                         result_value,
                                         'document_id_beginning_is_letter')

    return result


def document_id_ending_is_number(document_id):
    """
    :param document_id:
    :return:
    """
    LOGGER.debug('Function Successful: % s', 'document_id_ending_is_number: '
                 'document_id_ending_is_number successfully called from process_doc', extra=D)
    LOGGER.info('Ensuring document ID ends in a number...')
    LOGGER.debug('Calling Function: % s', 'document_id_ending_is_number: '
                 'document_id_ending_is_number calling split', extra=D)

    doc_list = re.split('-', document_id)

    LOGGER.debug('Function Successful: % s', 'document_id_ending_is_number: '
                 'document_id_ending_is_number successfully called split', extra=D)
    number = doc_list[-1]

    LOGGER.debug('Returning: %s', 'document_id_ending_is_number: returning the number', extra=D)
    LOGGER.info('The ending of the document ID is, in fact, a number')

    return number.isdigit()


def document_id_matches_json_id(path, doc_id):
    """
    :param path:
    :param doc_id:
    :return:
    """
    LOGGER.debug('Function Successful: % s', 'document_id_matches_json_id: '
                 'document_id_matches_json_id successfully called from process_doc', extra=D)
    LOGGER.info('Ensuring that the document IDs match...')
    LOGGER.debug('Calling Function: % s', 'document_id_matches_json_id: '
                 'document_id_matches_json_id calling open', extra=D)

    file = open(path, 'r')

    LOGGER.debug('Function Successful: % s', 'document_id_matches_json_id: '
                 'document_id_matches_json_id successfully called open', extra=D)
    LOGGER.debug('Calling Function: % s', 'document_id_matches_json_id: '
                 'document_id_matches_json_id calling load', extra=D)

    j = json.load(file)

    LOGGER.debug('Function Successful: % s', 'document_id_matches_json_id: '
                 'document_id_matches_json_id successfully called load', extra=D)
    document_id = j['documentId']['value']
    result = document_id == doc_id

    result_name = ['result']
    result_value = [result]
    dc.write_multiple_checks_into_logger(result_name, result_value, 'document_id_matches_json_id')

    return result


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
    LOGGER.debug('Function Successful: % s', 'save_single_file_locally: '
                 'save_single_file_locally successfully called from process_doc', extra=D)
    LOGGER.debug('Calling Function: % s', 'save_single_file_locally: '
                 'save_single_file_locally calling get_file_name', extra=D)

    file_name = get_file_name(current_path)

    LOGGER.debug('Function Successful: % s', 'save_single_file_locally: '
                 'save_single_file_locally successfully called get_file_name', extra=D)
    LOGGER.debug('Calling Function: % s', 'save_single_file_locally: '
                 'save_single_file_locally calling get_doc_attributes', extra=D)
    doc_id = get_document_id(file_name)
    org, docket_id, document_id = dc.get_doc_attributes(doc_id)

    LOGGER.debug('Function Successful: % s', 'save_single_file_locally: '
                 'save_single_file_locally successfully called get_doc_attributes', extra=D)

    destination_path = destination + org + '/' + docket_id + '/' + document_id + '/'

    LOGGER.debug('Calling Function: % s', 'save_single_file_locally: '
                 'save_single_file_locally calling create_new_directory_for_path', extra=D)
    create_new_directory_for_path(destination_path)

    LOGGER.debug('Function Successful: % s', 'save_single_file_locally: '
                 'save_single_file_locally successfully called '
                 'create_new_directory_for_path', extra=D)
    LOGGER.debug('Calling Function: % s', 'save_single_file_locally: '
                 'save_single_file_locally calling copy', extra=D)

    shutil.copy(current_path, destination_path + '/' + file_name)

    LOGGER.debug('Function Successful: % s', 'save_single_file_locally: '
                 'save_single_file_locally successfully called copy', extra=D)


def get_file_name(file_path):
    """
    :param file_path:
    :return:
    """
    LOGGER.debug('Function Successful: % s', 'get_file_name: '
                 'get_file_name successfully called from local_save', extra=D)
    LOGGER.info('Extracting file name...')

    split_path = file_path.split('/')
    file_name = split_path[len(split_path) - 1]

    LOGGER.debug('Returning: %s', 'get_file_name: returning the file name', extra=D)
    LOGGER.info('File name extracted')

    return file_name


def create_new_directory_for_path(path):
    """
    :param path:
    :return:
    """
    LOGGER.debug('Function Successful: % s', 'create_new_directory_for_path: '
                 'create_new_directory_for_path successfully '
                 'called from save_single_file_locally', extra=D)
    if not os.path.exists(path):
        LOGGER.debug('Calling Function: % s', 'create_new_directory_for_path: '
                     'create_new_directory_for_path calling makedirs', extra=D)
        os.makedirs(path)
        LOGGER.debug('Function Successful: % s', 'create_new_directory_for_path: '
                     'create_new_directory_for_path successfully called makedirs', extra=D)


def remove_job_from_progress(redis_server, json_data):
    """
    :param redis_server:
    :param json_data:
    :return:
    """
    key = redis_server.get_keys_from_progress(json_data['job_id'])
    redis_server.remove_job_from_progress(key)
