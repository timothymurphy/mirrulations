"""This is the documents filter used to process all documents jobs"""
import random
import json
import string
import logging
import os
import zipfile
import tempfile
import shutil
import mirrulations_core.documents_core as dc

FORMAT = '%(asctime)-15s %(clientip)s %(user)-8s %(message)s'
logging.basicConfig(filename='docs_filter.log', format=FORMAT)
D = {'clientip': '192.168.0.1', 'user': 'FILTERS'}
LOGGER = logging.getLogger('tcpserver')

"""
This program does the validation of data from
the docs jobs and then creates doc jobs using that data
"""
VERSION = 'v1.3'


def process_docs(redis_server, json_data, compressed_file):
    """
    Main documents function, called by the server to compile list of
    document jobs and add them to the "queue" queue
    :param json_data: the json data for the jobs
    :param compressed_file: the zipfile containing the client's log
    :return:
    """
    LOGGER.debug('Function Successful: % s',
                 'process_docs: process_docs successfully called from return_docs', extra=D)
    LOGGER.info('Processing Jobs...')

    if redis_server.does_job_exist_in_progress(json_data["job_id"]) is False:
        LOGGER.debug('Variable Failure: %s', 'process_docs: '
                     'job_id does not exist in progress queue', extra=D)

    else:
        save_client_log(json_data['client_id'], compressed_file)

        LOGGER.debug('Variable Success: %s', 'process_docs: '
                     'job does exist in progress queue', extra=D)
        LOGGER.debug('Calling Function: % s', 'process_docs: '
                     'process_docs calling check_workfile_length', extra=D)
        workfile_length_passed = check_workfile_length(json_data)
        LOGGER.debug('Function Successful: % s',
                     'process_docs: process_docs successfully called check_workfile_length',
                     extra=D)
        file_type_is_docs = json_data['type'] == 'docs'

        if workfile_length_passed and file_type_is_docs:

            LOGGER.debug('Calling Function: % s', 'process_docs: '
                         'process_docs calling check_document_exists', extra=D)
            json_data = check_document_exists(json_data)
            LOGGER.debug('Calling Function: % s', 'process_docs: '
                         'process_docs calling add_document_job_to_queue', extra=D)
            add_document_job_to_queue(redis_server, json_data)
            LOGGER.debug('Function Successful: % s', 'process_docs: '
                         'process_docs successfully called add_document_job_to_queue', extra=D)
            LOGGER.debug('Calling Function: % s', 'process_docs: '
                         'process_docs calling get_keys_from_progress', extra=D)
            key = redis_server.get_keys_from_progress(json_data['job_id'])
            LOGGER.debug('Function Successful: % s', 'process_docs: '
                         'process_docs successfully called get_keys_from_progress', extra=D)
            LOGGER.debug('Calling Function: % s', 'process_docs: '
                         'process_docs calling remove_job_from_progress', extra=D)
            redis_server.remove_job_from_progress(key)
            LOGGER.debug('Function Successful: % s', 'process_docs: '
                         'process_docs successfully called remove_job_from_progress', extra=D)

        else:
            LOGGER.debug('Variable Failure: %s', 'process_docs: '
                         'Something went wrong in validation', extra=D)

            checks_name = ['workfile_length_passed', 'file_type_is_docs']
            checks_values = [workfile_length_passed, file_type_is_docs]
            dc.write_multiple_checks_into_logger(checks_name, checks_values, 'process_docs')

            LOGGER.debug('Calling Function: % s', 'process_docs: '
                         'process_docs calling renew_job', extra=D)
            redis_server.renew_job(json_data['job_id'])
            LOGGER.debug('Function Successful: % s', 'process_docs: '
                         'process_docs successfully called renew_job', extra=D)
            LOGGER.info('Jobs successfully processed')


def save_client_log(client_id, compressed_file):
    """

    :param client_id:
    :param compressed_file:
    :return:
    """
    client_path = os.getenv('HOME') + '/client-logs/' + str(client_id) + '/'

    LOGGER.debug('Function Successful: % s', 'get_file_list: '
                 'get_file_list successfully called from process_doc',
                 extra=D)
    LOGGER.info('Saving client log...')
    LOGGER.debug('Calling Function: % s', 'get_file_list: '
                 'get_file_list calling ZipFile', extra=D)

    files = zipfile.ZipFile(compressed_file, "r")
    LOGGER.debug('Function Successful: % s', 'get_file_list: '
                 'get_file_list successfully called ZipFile', extra=D)

    temp_directory = tempfile.mkdtemp()
    temp_directory_path = str(temp_directory + '/')

    LOGGER.debug('Calling Function: % s', 'get_file_list: '
                 'get_file_list calling extractall', extra=D)
    files.extractall(temp_directory_path)
    LOGGER.debug('Function Successful: % s', 'get_file_list: '
                 'get_file_list successfully called extractall', extra=D)

    # Create a list of all the files in the directory
    LOGGER.debug('Calling Function: % s', 'get_file_list: get_file_list calling listdir', extra=D)
    file_list = os.listdir(temp_directory_path)
    LOGGER.debug('Function Successful: % s', 'get_file_list: '
                 'get_file_list successfully called listdir', extra=D)

    LOGGER.debug('Loop: %s', 'get_file_list: loop through the files in the file list', extra=D)
    for file in file_list:
        if file.endswith('.log'):
            if not os.path.exists(client_path):
                os.makedirs(client_path)
                shutil.copy(temp_directory_path + file, client_path)
            else:
                shutil.copy(temp_directory_path + file, client_path)
    LOGGER.debug('Loop Successful: %s', 'get_file_list: loop successful', extra=D)
    LOGGER.info('Log successfully saved')


def check_workfile_length(json_data):
    """
        Checks the file count and attachment count of each work file
        :param json_data: the json containing the work files
        :return: True if there are 1000 or less document ids and 1000
                 or less attachments per work file False if either
                 the ids or attachments are over 1000
        """
    LOGGER.debug('Function Successful: % s', 'check_workfile_length: '
                 'check_workfile_length successfully called from process_docs', extra=D)
    LOGGER.info('Workfile length being checked...')

    file_count = 0
    attachment_count = 0
    for work_file in json_data['data']:
        for line in work_file:
            file_count += 1
            attachment_count += line["count"]

        is_file_count_too_big = file_count > 1000
        is_attachment_count_too_big = attachment_count > 1000
        if is_file_count_too_big or is_attachment_count_too_big:

            LOGGER.debug('Variable Failure: %s', 'check_workfile_length: Something went wrong in '
                                                 'work_file_length_checker', extra=D)

            checks_names = ['is_file_count_too_big', 'is_attachment_count_too_big']
            checks_values = [is_file_count_too_big, is_attachment_count_too_big]
            dc.write_multiple_checks_into_logger(checks_names, checks_values,
                                                 'check_workfile_length')

            LOGGER.debug('Returning: %s', 'check_workfile_length: returning False', extra=D)
            return False

        LOGGER.debug('Variable Success: %s', 'check_workfile_length: is_file_count_too_big and '
                                             'is_attachment_count_too_big are True', extra=D)
        file_count = 0
        attachment_count = 0

    LOGGER.debug('Returning: %s', 'check_workfile_length: returning True', extra=D)
    LOGGER.warning('Workfile length check completed')

    return True


def check_document_exists(json_data, path=os.getenv('HOME') + '/regulations_data/'):
    """
    Checks to see if a document was already downloaded or already in one of the queues.
    If the document has already been downloaded it will be removed from its workfile.
    If a workfile were to become empty it will be removed to prevent empty doc jobs from existing.
    """
    LOGGER.warning('Function Successful: % s', 'check_workfile_length: '
                   'check_workfile_length successfully called from process_docs', extra=D)
    for workfile in json_data['data']:
        count = 0
        for line in workfile:
            document = line['id']
            alpha_doc_org, docket_id, document_id = dc.get_doc_attributes(document)
            full_path = path + alpha_doc_org + '/' + docket_id + '/' + \
                        document_id + '/' + 'doc.' + document + '.json'

            count, local_verdict = check_if_file_exists_locally(full_path, count)

            if local_verdict:
                workfile.pop(count)

    json_data = remove_empty_lists(json_data)
    return json_data


def check_if_file_exists_locally(full_path, count):
    """
    Checks to see if the document exists.
    If the document does not, then the counter is increased
    :param count: The current count of the workfile
    :return: Returns the count and True if the file does exist, else it will return False
    """
    if os.path.isfile(full_path):
        return count, True
    count += 1
    return count, False


def remove_empty_lists(json_data):
    """

    :param json_data:
    :return:
    """
    json_data['data'] = [workfile for workfile in json_data['data'] if workfile != []]
    return json_data


def add_document_job_to_queue(redis_server, json_data):
    """
    Creates a job for each work file and then adds each job to the "queue"
    :param json_data: the json data containing all the work files
    :return:
    """
    LOGGER.debug('Function Successful: % s', 'add_document_job_to_queue: '
                 'add_document_job_to_queue successfully called from process_docs', extra=D)
    LOGGER.warning('Adding document job to the queue...')

    for work_file in json_data["data"]:
        random_id = ''.join(random.choices(string.ascii_letters + string.digits, k=16))

        LOGGER.debug('Calling Function: % s', 'add_document_job_to_queue: '
                     'add_document_job_to_queue calling create_document_job', extra=D)
        job = create_document_job(work_file, random_id)
        LOGGER.debug('Function Successful: % s', 'add_document_job_to_queue: '
                     'successfully add_document_job_to_queue called create_document_job', extra=D)
        LOGGER.debug('Calling Function: % s', 'add_document_job_to_queue: '
                     'add_document_job_to_queue calling add_to_queue', extra=D)
        redis_server.add_to_queue(job)
        LOGGER.debug('Function Successful: % s', 'add_document_job_to_queue: successfully '
                     'add_document_job_to_queue called add_to_queue', extra=D)
        LOGGER.warning('Document job successfully added to queue')


def create_document_job(work_file, job_id):
    """
    Creates a job for the server to provide to clients
    :param work_file: The list of ids for the clients to retrieve
    :param job_id: The id for the job
    :return: A json in the form of a dictionary
    """
    LOGGER.debug('Function Successful: % s', 'create_document_job: create_document_job '
                 'successfully called from add_document_job_to_queue', extra=D)
    LOGGER.warning('Creating document job...')

    dictionary = {'job_id': job_id, 'type': 'doc', 'data': work_file, 'VERSION': VERSION}

    LOGGER.debug('Returning: %s', 'create_document_job: returning a json dictionary', extra=D)
    LOGGER.info('Document job created...')

    return json.dumps(dictionary)
